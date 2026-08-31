"""Materialize the one frozen C1/n=0 static runtime root.

The public API has no path, source, layout, or syscall parameters.  It accepts
only the already-frozen static-inventory bytes and publishes only the literal
root named below.  The publication parent is a deliberate precondition: this
component never creates it and never falls back to a different root.

This component performs no import, runtime probe, candidate execution, or
scientific computation.  Its receipt attests only to this invocation's
materialization steps and the independently reopened static byte tree.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import secrets
import stat
import sys
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

RENAME_EXCL: Final = 0x00000004
RENAME_NOFOLLOW_ANY: Final = 0x00000010
RENAME_FLAGS: Final = RENAME_EXCL | RENAME_NOFOLLOW_ANY
ACL_TYPE_EXTENDED: Final = 0x00000100
XATTR_SHOWCOMPRESSION: Final = 0x00000020
ALLOWED_OS_MANAGED_XATTRS: Final = (b"com.apple.provenance",)
MAX_INVENTORY_BYTES: Final = 32_768
MAX_RECEIPT_BYTES: Final = 131_072
MAX_JSON_INTEGER_BITS: Final = 64
MAX_JSON_INTEGER_CHARS: Final = 20
READ_CHUNK: Final = 1 << 20


@dataclass(frozen=True)
class _SourceSpec:
    source_path: str
    relative_path: str
    byte_length: int
    sha256: str
    destination_mode: int


@dataclass(frozen=True)
class _Config:
    authority_root: str
    publication_parent: str
    lock_name: str
    expected_uid: int
    expected_gid: int
    sources: tuple[_SourceSpec, ...]
    inventory_schema: str = INVENTORY_SCHEMA
    inventory_byte_length: int = INVENTORY_BYTE_LENGTH
    inventory_sha256: str = INVENTORY_SHA256
    deterministic_stage_name: str | None = None


PUBLIC_SOURCES: Final = (
    _SourceSpec(
        (
            "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/"
            "Python.framework/Versions/3.12/bin/python3.12"
        ),
        "bin/python3.12",
        52_448,
        "31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805",
        0o555,
    ),
    _SourceSpec(
        (
            "/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/"
            "site-packages/gmpy2/__init__.py"
        ),
        "site-packages/gmpy2/__init__.py",
        412,
        "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2",
        0o444,
    ),
    _SourceSpec(
        (
            "/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/"
            "site-packages/gmpy2/gmpy2.cpython-312-darwin.so"
        ),
        "site-packages/gmpy2/gmpy2.cpython-312-darwin.so",
        573_056,
        "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b",
        0o444,
    ),
    _SourceSpec(
        (
            "/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/"
            "site-packages/gmpy2.libs/libgmp.10.dylib"
        ),
        "site-packages/gmpy2.libs/libgmp.10.dylib",
        468_768,
        "22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049",
        0o444,
    ),
    _SourceSpec(
        (
            "/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/"
            "site-packages/gmpy2.libs/libmpfr.6.dylib"
        ),
        "site-packages/gmpy2.libs/libmpfr.6.dylib",
        469_360,
        "d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed",
        0o444,
    ),
    _SourceSpec(
        (
            "/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/"
            "site-packages/gmpy2.libs/libmpc.3.dylib"
        ),
        "site-packages/gmpy2.libs/libmpc.3.dylib",
        152_112,
        "d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c",
        0o444,
    ),
)
PUBLIC_CONFIG: Final = _Config(
    authority_root=AUTHORITY_ROOT,
    publication_parent=PUBLICATION_PARENT,
    lock_name=LOCK_NAME,
    expected_uid=EXPECTED_UID,
    expected_gid=EXPECTED_GID,
    sources=PUBLIC_SOURCES,
)


class SealedRuntimeRootMaterializationFailure(RuntimeError):
    """Fail-closed materialization failure."""


def _fail(message: str) -> NoReturn:
    raise SealedRuntimeRootMaterializationFailure(message)


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
        _fail("static inventory integer exceeds the fixed cap")
    value = int(raw, 10)
    if value.bit_length() > MAX_JSON_INTEGER_BITS:
        _fail("static inventory integer exceeds the fixed cap")
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


class _SystemCalls:
    """Small private syscall seam used only by bounded tmp tests."""

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

    def write(self, fd: int, raw: memoryview) -> int:
        return os.write(fd, raw)

    def mkdir(self, path: str, mode: int, *, dir_fd: int) -> None:
        os.mkdir(path, mode, dir_fd=dir_fd)

    def listdir(self, fd: int) -> list[str]:
        return os.listdir(fd)

    def fchmod(self, fd: int, mode: int) -> None:
        os.fchmod(fd, mode)

    def chmod(self, path: str, mode: int, *, dir_fd: int) -> None:
        os.chmod(path, mode, dir_fd=dir_fd, follow_symlinks=False)

    def fsync(self, fd: int) -> None:
        os.fsync(fd)

    def unlink(self, path: str, *, dir_fd: int) -> None:
        os.unlink(path, dir_fd=dir_fd)

    def rmdir(self, path: str, *, dir_fd: int) -> None:
        os.rmdir(path, dir_fd=dir_fd)

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
            _fail("flistxattr changed during inspection")
        names = tuple(item for item in buffer.raw[:actual].split(b"\0") if item)
        return names

    def clear_xattrs(self, fd: int) -> None:
        names = self.list_xattrs(fd)
        if not names:
            return
        libc = self._libc()
        if not hasattr(libc, "fremovexattr"):
            _fail("fremovexattr unavailable")
        function = libc.fremovexattr
        function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        function.restype = ctypes.c_int
        for name in names:
            ctypes.set_errno(0)
            if function(fd, ctypes.c_char_p(name), 0) != 0:
                number = ctypes.get_errno()
                raise OSError(number, os.strerror(number))

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

    def clear_extended_acl(self, fd: int) -> None:
        libc = self._libc()
        if not hasattr(libc, "acl_delete_fd_np"):
            _fail("acl_delete_fd_np unavailable")
        function = libc.acl_delete_fd_np
        function.argtypes = [ctypes.c_int, ctypes.c_int]
        function.restype = ctypes.c_int
        ctypes.set_errno(0)
        result = function(fd, ACL_TYPE_EXTENDED)
        if result != 0 and ctypes.get_errno() not in {0, errno.ENOENT}:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number))

    def clear_flags(self, fd: int) -> None:
        libc = self._libc()
        if not hasattr(libc, "fchflags"):
            _fail("fchflags unavailable")
        function = libc.fchflags
        function.argtypes = [ctypes.c_int, ctypes.c_uint]
        function.restype = ctypes.c_int
        ctypes.set_errno(0)
        if function(fd, 0) != 0:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number))

    def rename_exclusive(
        self,
        parent_fd: int,
        source: str,
        destination: str,
    ) -> None:
        libc = self._libc()
        if not hasattr(libc, "renameatx_np"):
            _fail("Darwin renameatx_np unavailable; no rename fallback is permitted")
        function = libc.renameatx_np
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        function.restype = ctypes.c_int
        ctypes.set_errno(0)
        result = function(
            parent_fd,
            ctypes.c_char_p(os.fsencode(source)),
            parent_fd,
            ctypes.c_char_p(os.fsencode(destination)),
            RENAME_FLAGS,
        )
        if result != 0:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number), destination)


def _directory_open_flags() -> int:
    return os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _file_read_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _open_absolute_directory(calls: _SystemCalls, path: Path) -> int:
    if not path.is_absolute() or path == Path("/"):
        if path == Path("/"):
            return calls.open("/", _directory_open_flags())
        _fail("directory anchor must be absolute")
    current = calls.open("/", _directory_open_flags())
    try:
        for part in path.parts[1:]:
            child = calls.open(part, _directory_open_flags(), dir_fd=current)
            calls.close(current)
            current = child
        value = calls.fstat(current)
        if not stat.S_ISDIR(value.st_mode):
            _fail("absolute directory walk ended at a non-directory")
        return current
    except BaseException:
        calls.close(current)
        raise


def _open_relative_directory(
    calls: _SystemCalls,
    root_fd: int,
    parts: tuple[str, ...],
) -> int:
    current = calls.dup(root_fd)
    try:
        for part in parts:
            child = calls.open(part, _directory_open_flags(), dir_fd=current)
            calls.close(current)
            current = child
        return current
    except BaseException:
        calls.close(current)
        raise


def _require_path_anchor(
    calls: _SystemCalls,
    path: Path,
    anchor_fd: int,
    identity: tuple[int, int],
    phase: str,
) -> None:
    if _object_identity(calls.fstat(anchor_fd)) != identity:
        _fail(f"descriptor identity changed {phase}")
    current_fd = _open_absolute_directory(calls, path)
    try:
        if _object_identity(calls.fstat(current_fd)) != identity:
            _fail(f"path anchor was rebound {phase}")
    finally:
        calls.close(current_fd)
    if _object_identity(calls.fstat(anchor_fd)) != identity:
        _fail(f"descriptor identity changed {phase}")


def _require_parent_security(
    calls: _SystemCalls,
    parent_fd: int,
    config: _Config,
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
        _fail(f"publication parent security metadata mismatch {phase}")
    if calls.has_extended_acl(parent_fd):
        _fail(f"publication parent extended ACL is present {phase}")


def _decode_inventory(raw: bytes, config: _Config) -> dict[str, Any]:
    if type(raw) is not bytes:
        _fail("static inventory must be immutable bytes")
    if len(raw) > MAX_INVENTORY_BYTES or len(raw) != config.inventory_byte_length:
        _fail("static inventory byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != config.inventory_sha256:
        _fail("static inventory SHA-256 mismatch")

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
    if value.get("schema") != config.inventory_schema:
        _fail("static inventory schema mismatch")
    if config.inventory_schema == INVENTORY_SCHEMA:
        _require_inventory_matches_config(value, config)
    return value


def _require_inventory_matches_config(value: dict[str, Any], config: _Config) -> None:
    """Join the authenticated production inventory to the configured tree."""

    if value.get("authority_root") != config.authority_root:
        _fail("static inventory authority root does not match the configured tree")
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
        f"{config.authority_root}/{spec.relative_path}": spec.sha256 for spec in config.sources
    }
    if observed != expected:
        _fail("static inventory path/hash map does not match the configured tree")


def _validate_config(config: _Config) -> None:
    root = Path(config.authority_root)
    parent = Path(config.publication_parent)
    if not root.is_absolute() or root.parent != parent or root.name in {"", ".", ".."}:
        _fail("private configuration has an unsafe authority root")
    if type(config.lock_name) is not str or "/" in config.lock_name or not config.lock_name:
        _fail("private configuration has an unsafe lock name")
    if len(config.sources) != EXPECTED_FILE_COUNT:
        _fail("private configuration file count mismatch")
    relatives = [_safe_relative(item.relative_path).as_posix() for item in config.sources]
    if len(set(relatives)) != len(relatives):
        _fail("private configuration has duplicate destination paths")
    if sum(item.byte_length for item in config.sources) != EXPECTED_TOTAL_FILE_BYTES:
        _fail("private configuration total byte length mismatch")
    for item in config.sources:
        if not Path(item.source_path).is_absolute():
            _fail("private configuration source path is not absolute")
        if item.byte_length < 0 or item.destination_mode not in {0o444, 0o555}:
            _fail("private configuration file metadata mismatch")
        if (
            len(item.sha256) != 64
            or item.sha256.lower() != item.sha256
            or any(character not in "0123456789abcdef" for character in item.sha256)
        ):
            _fail("private configuration SHA-256 is malformed")


def _read_source(calls: _SystemCalls, spec: _SourceSpec) -> bytes:
    path = Path(spec.source_path)
    parent_fd = _open_absolute_directory(calls, path.parent)
    parent_identity = _object_identity(calls.fstat(parent_fd))
    fd = -1
    try:
        fd = calls.open(path.name, _file_read_flags(), dir_fd=parent_fd)
        before = calls.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            _fail(f"{spec.source_path}: source is not a single-link regular file")
        calls.event("after_source_open", spec=spec, fd=fd)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = calls.read(fd, min(READ_CHUNK, spec.byte_length + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > spec.byte_length:
                _fail(f"{spec.source_path}: source exceeds frozen byte length")
        after = calls.fstat(fd)
        if _stable_identity(before) != _stable_identity(after):
            _fail(f"{spec.source_path}: source changed while read")
        path_after = calls.stat(path.name, dir_fd=parent_fd)
        if not stat.S_ISREG(path_after.st_mode) or _stable_identity(before) != _stable_identity(
            path_after
        ):
            _fail(f"{spec.source_path}: source pathname changed while read")
        _require_path_anchor(
            calls,
            path.parent,
            parent_fd,
            parent_identity,
            "during source read",
        )
        raw = b"".join(chunks)
        if len(raw) != spec.byte_length:
            _fail(f"{spec.source_path}: source byte length mismatch")
        if hashlib.sha256(raw).hexdigest() != spec.sha256:
            _fail(f"{spec.source_path}: source SHA-256 mismatch")
        return raw
    except OSError as error:
        _fail(f"{spec.source_path}: secure source read failed: {error}")
    finally:
        if fd >= 0:
            calls.close(fd)
        calls.close(parent_fd)


def _prepare_owned_fd(calls: _SystemCalls, fd: int) -> None:
    calls.clear_xattrs(fd)
    if calls.has_extended_acl(fd):
        calls.clear_extended_acl(fd)
        if calls.has_extended_acl(fd):
            _fail("extended ACL deletion did not take effect")
    calls.clear_flags(fd)


def _mkdir_chain(
    calls: _SystemCalls,
    root_fd: int,
    parts: tuple[str, ...],
    owned_identities: set[tuple[int, int]],
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None],
) -> None:
    current = calls.dup(root_fd)
    try:
        for part in parts:
            parent_identity = _object_identity(calls.fstat(current))
            binding = (*parent_identity, part)
            try:
                calls.mkdir(part, 0o700, dir_fd=current)
                owned_bindings[binding] = None
                created = calls.stat(part, dir_fd=current)
                if not stat.S_ISDIR(created.st_mode):
                    _fail("new staging path is not a directory")
                created_identity = _object_identity(created)
                owned_bindings[binding] = created_identity
                owned_identities.add(created_identity)
                calls.chmod(part, 0o700, dir_fd=current)
                child = calls.open(part, _directory_open_flags(), dir_fd=current)
                try:
                    if _object_identity(calls.fstat(child)) != created_identity:
                        _fail("new staging directory identity changed before preparation")
                    _prepare_owned_fd(calls, child)
                finally:
                    calls.close(child)
            except FileExistsError:
                pass
            child = calls.open(part, _directory_open_flags(), dir_fd=current)
            value = calls.fstat(child)
            if not stat.S_ISDIR(value.st_mode) or stat.S_IMODE(value.st_mode) != 0o700:
                calls.close(child)
                _fail("staging directory type or mode mismatch")
            if _object_identity(value) not in owned_identities:
                calls.close(child)
                _fail("unowned object appeared inside the hidden stage")
            calls.close(current)
            current = child
    finally:
        calls.close(current)


def _write_staged_file(
    calls: _SystemCalls,
    root_fd: int,
    spec: _SourceSpec,
    raw: bytes,
    owned_identities: set[tuple[int, int]],
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None],
) -> None:
    relative = _safe_relative(spec.relative_path)
    _mkdir_chain(
        calls,
        root_fd,
        relative.parts[:-1],
        owned_identities,
        owned_bindings,
    )
    parent_fd = _open_relative_directory(calls, root_fd, relative.parts[:-1])
    fd = -1
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        binding = (*_object_identity(calls.fstat(parent_fd)), relative.name)
        fd = calls.open(relative.name, flags, 0o600, dir_fd=parent_fd)
        owned_bindings[binding] = None
        created = calls.fstat(fd)
        if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
            _fail("new staged file is not a single-link regular file")
        created_identity = _object_identity(created)
        owned_bindings[binding] = created_identity
        owned_identities.add(created_identity)
        _prepare_owned_fd(calls, fd)
        view = memoryview(raw)
        while view:
            written = calls.write(fd, view)
            if written <= 0 or written > len(view):
                _fail("staged-file write made invalid progress")
            view = view[written:]
        calls.fsync(fd)
        calls.fchmod(fd, spec.destination_mode)
        calls.fsync(fd)
    finally:
        if fd >= 0:
            calls.close(fd)
        calls.close(parent_fd)


def _seal_directories(
    calls: _SystemCalls,
    root_fd: int,
    directories: set[PurePosixPath],
) -> None:
    for relative in sorted(
        directories,
        key=lambda item: (-len(item.parts), item.as_posix()),
    ):
        fd = _open_relative_directory(calls, root_fd, relative.parts)
        try:
            calls.fchmod(fd, 0o555)
            calls.fsync(fd)
        finally:
            calls.close(fd)
    calls.fchmod(root_fd, 0o555)
    calls.fsync(root_fd)


def _expected_tree(config: _Config) -> dict[str, tuple[str, int, _SourceSpec | None]]:
    result: dict[str, tuple[str, int, _SourceSpec | None]] = {".": ("directory", 0o555, None)}
    for spec in config.sources:
        relative = _safe_relative(spec.relative_path)
        result[relative.as_posix()] = ("file", spec.destination_mode, spec)
        parent = relative.parent
        while parent != PurePosixPath("."):
            result.setdefault(parent.as_posix(), ("directory", 0o555, None))
            parent = parent.parent
    if sum(kind == "directory" for kind, _, _ in result.values()) != EXPECTED_DIRECTORY_COUNT:
        _fail("frozen directory count mismatch")
    return result


def _expected_nlink(
    expected: dict[str, tuple[str, int, _SourceSpec | None]],
    path: str,
) -> int:
    if expected[path][0] == "file":
        return 1
    prefix = "" if path == "." else path + "/"
    depth = 0 if path == "." else len(PurePosixPath(path).parts)
    children = 0
    for candidate in expected:
        if candidate == "." or not candidate.startswith(prefix):
            continue
        if len(PurePosixPath(candidate).parts) == depth + 1:
            children += 1
    return 2 + children


def _assert_security(
    calls: _SystemCalls,
    fd: int,
    relative: str,
    value: os.stat_result,
    config: _Config,
    expected_mode: int,
    expected_nlink: int,
) -> tuple[os.stat_result, tuple[str, ...]]:
    value = calls.adapt_stat(relative, value)
    if (
        value.st_uid != config.expected_uid
        or value.st_gid != config.expected_gid
        or stat.S_IMODE(value.st_mode) != expected_mode
        or value.st_nlink != expected_nlink
    ):
        _fail(f"{relative}: frozen metadata mismatch")
    if getattr(value, "st_flags", 0) != 0:
        _fail(f"{relative}: BSD flags are not zero")
    xattrs = calls.list_xattrs(fd)
    if len(xattrs) != len(set(xattrs)) or any(
        name not in ALLOWED_OS_MANAGED_XATTRS for name in xattrs
    ):
        _fail(f"{relative}: unexpected extended attribute is present")
    if calls.has_extended_acl(fd):
        _fail(f"{relative}: extended ACL is present")
    return value, tuple(sorted(name.decode("ascii") for name in xattrs))


def _read_file_for_ack(
    calls: _SystemCalls,
    parent_fd: int,
    name: str,
    relative: str,
    spec: _SourceSpec,
    config: _Config,
) -> tuple[dict[str, Any], tuple[int, int]]:
    before_path = calls.stat(name, dir_fd=parent_fd)
    fd = calls.open(name, _file_read_flags(), dir_fd=parent_fd)
    try:
        before = calls.fstat(fd)
        if (
            not stat.S_ISREG(before_path.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or _object_identity(before_path) != _object_identity(before)
        ):
            _fail(f"{relative}: acknowledgement file identity mismatch")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = calls.read(fd, min(READ_CHUNK, spec.byte_length + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > spec.byte_length:
                _fail(f"{relative}: acknowledgement file exceeds frozen size")
        after = calls.fstat(fd)
        if _stable_identity(before) != _stable_identity(after):
            _fail(f"{relative}: acknowledgement file changed while read")
        current = calls.stat(name, dir_fd=parent_fd)
        if _stable_identity(before) != _stable_identity(current):
            _fail(f"{relative}: acknowledgement pathname changed while read")
        checked, xattrs = _assert_security(
            calls,
            fd,
            relative,
            after,
            config,
            spec.destination_mode,
            1,
        )
        security_after = calls.fstat(fd)
        security_path = calls.stat(name, dir_fd=parent_fd)
        if _stable_identity(before) != _stable_identity(security_after) or _stable_identity(
            before
        ) != _stable_identity(security_path):
            _fail(f"{relative}: file changed during security inspection")
        raw = b"".join(chunks)
        if len(raw) != spec.byte_length or hashlib.sha256(raw).hexdigest() != spec.sha256:
            _fail(f"{relative}: acknowledgement bytes mismatch")
        return (
            {
                "ctime_ns": checked.st_ctime_ns,
                "dev": checked.st_dev,
                "gid": checked.st_gid,
                "ino": checked.st_ino,
                "mode": f"{stat.S_IMODE(checked.st_mode):04o}",
                "mtime_ns": checked.st_mtime_ns,
                "nlink": checked.st_nlink,
                "path": relative,
                "sha256": spec.sha256,
                "size": spec.byte_length,
                "type": "file",
                "uid": checked.st_uid,
                "xattrs": list(xattrs),
            },
            _object_identity(checked),
        )
    finally:
        calls.close(fd)


def _scan_tree(
    calls: _SystemCalls,
    parent_fd: int,
    root_name: str,
    owned_identity: tuple[int, int],
    config: _Config,
) -> tuple[os.stat_result, list[dict[str, Any]]]:
    root_path_value = calls.stat(root_name, dir_fd=parent_fd)
    root_fd = calls.open(root_name, _directory_open_flags(), dir_fd=parent_fd)
    expected = _expected_tree(config)
    entries: list[dict[str, Any]] = []
    try:
        root_before = calls.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_path_value.st_mode)
            or not stat.S_ISDIR(root_before.st_mode)
            or _object_identity(root_path_value) != _object_identity(root_before)
            or _object_identity(root_before) != owned_identity
        ):
            _fail("published root identity mismatch")

        def visit(
            directory_fd: int,
            relative: str,
            containing_fd: int | None,
            containing_name: str | None,
        ) -> None:
            kind, mode, _ = expected[relative]
            if kind != "directory":
                _fail("internal expected-tree mismatch")
            directory_before = calls.fstat(directory_fd)
            if not stat.S_ISDIR(directory_before.st_mode):
                _fail(f"{relative}: expected a directory")
            checked, xattrs = _assert_security(
                calls,
                directory_fd,
                relative,
                directory_before,
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
                _fail(f"{relative}: exact tree membership mismatch")
            for name in expected_children:
                child_relative = name if relative == "." else f"{relative}/{name}"
                child_kind, _, child_spec = expected[child_relative]
                if child_kind == "directory":
                    child_path = calls.stat(name, dir_fd=directory_fd)
                    child_fd = calls.open(name, _directory_open_flags(), dir_fd=directory_fd)
                    try:
                        if not stat.S_ISDIR(child_path.st_mode) or _object_identity(
                            child_path
                        ) != _object_identity(calls.fstat(child_fd)):
                            _fail(f"{child_relative}: directory identity mismatch")
                        calls.event(
                            "after_ack_directory_open",
                            relative=child_relative,
                            containing_fd=directory_fd,
                            entry_name=name,
                            child_fd=child_fd,
                        )
                        visit(child_fd, child_relative, directory_fd, name)
                    finally:
                        calls.close(child_fd)
                else:
                    if child_spec is None:
                        _fail("internal file specification missing")
                    entry, _ = _read_file_for_ack(
                        calls,
                        directory_fd,
                        name,
                        child_relative,
                        child_spec,
                        config,
                    )
                    entries.append(entry)
            directory_after = calls.fstat(directory_fd)
            if _stable_identity(directory_before) != _stable_identity(directory_after):
                _fail(f"{relative}: directory changed during acknowledgement")
            if containing_fd is not None and containing_name is not None:
                path_after = calls.stat(containing_name, dir_fd=containing_fd)
                if not stat.S_ISDIR(path_after.st_mode) or _stable_identity(
                    directory_before
                ) != _stable_identity(path_after):
                    _fail(f"{relative}: directory pathname changed during acknowledgement")

        visit(root_fd, ".", None, None)
        root_after = calls.fstat(root_fd)
        if _stable_identity(root_before) != _stable_identity(root_after):
            _fail("published root changed during acknowledgement")
        calls.event(
            "before_ack_root_final_path_check",
            parent_fd=parent_fd,
            root_name=root_name,
            root_fd=root_fd,
        )
        final_path = calls.stat(root_name, dir_fd=parent_fd)
        if _stable_identity(final_path) != _stable_identity(root_before):
            _fail("published root pathname or metadata changed during acknowledgement")
        if len(entries) != EXPECTED_DIRECTORY_COUNT + EXPECTED_FILE_COUNT:
            _fail("acknowledgement entry count mismatch")
        if sum(item.get("size", 0) for item in entries) != EXPECTED_TOTAL_FILE_BYTES:
            _fail("acknowledgement total byte length mismatch")
        return root_after, sorted(entries, key=lambda item: item["path"])
    finally:
        calls.close(root_fd)


def _confirm_root_snapshot(
    calls: _SystemCalls,
    parent_fd: int,
    root_name: str,
    expected_value: os.stat_result,
    config: _Config,
) -> None:
    path_value = calls.stat(root_name, dir_fd=parent_fd)
    fd = calls.open(root_name, _directory_open_flags(), dir_fd=parent_fd)
    try:
        before = calls.fstat(fd)
        if (
            not stat.S_ISDIR(path_value.st_mode)
            or _stable_identity(path_value) != _stable_identity(expected_value)
            or _stable_identity(before) != _stable_identity(expected_value)
        ):
            _fail("published root changed after acknowledgement")
        _assert_security(
            calls,
            fd,
            ".",
            before,
            config,
            0o555,
            _expected_nlink(_expected_tree(config), "."),
        )
        after = calls.fstat(fd)
        final_path = calls.stat(root_name, dir_fd=parent_fd)
        if _stable_identity(after) != _stable_identity(expected_value) or _stable_identity(
            final_path
        ) != _stable_identity(expected_value):
            _fail("published root changed during final confirmation")
    finally:
        calls.close(fd)


def _clear_owned_directory(
    calls: _SystemCalls,
    directory_fd: int,
    owned_identities: set[tuple[int, int]],
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None],
) -> None:
    value = calls.fstat(directory_fd)
    if not stat.S_ISDIR(value.st_mode):
        _fail("owned rollback object is not a directory")
    calls.fchmod(directory_fd, 0o700)
    directory_identity = _object_identity(calls.fstat(directory_fd))
    missing = object()
    for name in sorted(calls.listdir(directory_fd)):
        try:
            before = calls.stat(name, dir_fd=directory_fd)
        except FileNotFoundError:
            continue
        identity = _object_identity(before)
        binding = (*directory_identity, name)
        bound_identity = owned_bindings.get(binding, missing)
        if identity not in owned_identities and not (
            bound_identity is None or bound_identity == identity
        ):
            continue
        if bound_identity is None:
            owned_bindings[binding] = identity
            owned_identities.add(identity)
        if stat.S_ISDIR(before.st_mode):
            try:
                child_fd = calls.open(name, _directory_open_flags(), dir_fd=directory_fd)
            except PermissionError:
                calls.chmod(name, 0o700, dir_fd=directory_fd)
                child_fd = calls.open(name, _directory_open_flags(), dir_fd=directory_fd)
            except FileNotFoundError:
                continue
            try:
                if _object_identity(calls.fstat(child_fd)) != _object_identity(before):
                    continue
                _clear_owned_directory(
                    calls,
                    child_fd,
                    owned_identities,
                    owned_bindings,
                )
            finally:
                calls.close(child_fd)
            try:
                current = calls.stat(name, dir_fd=directory_fd)
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(current.st_mode) and _object_identity(current) == _object_identity(
                before
            ):
                try:
                    calls.rmdir(name, dir_fd=directory_fd)
                except OSError as error:
                    if error.errno not in {errno.ENOTEMPTY, errno.EEXIST}:
                        raise
        else:
            try:
                current = calls.stat(name, dir_fd=directory_fd)
            except FileNotFoundError:
                continue
            if (
                before.st_nlink == 1
                and current.st_nlink == 1
                and _object_identity(current) == _object_identity(before)
            ):
                calls.unlink(name, dir_fd=directory_fd)
    calls.fsync(directory_fd)


def _remove_owned_directory_at_name(
    calls: _SystemCalls,
    parent_fd: int,
    name: str,
    owned_identity: tuple[int, int],
    owned_identities: set[tuple[int, int]],
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None],
) -> bool:
    try:
        before = calls.stat(name, dir_fd=parent_fd)
    except FileNotFoundError:
        return False
    if not stat.S_ISDIR(before.st_mode) or _object_identity(before) != owned_identity:
        return False
    try:
        fd = calls.open(name, _directory_open_flags(), dir_fd=parent_fd)
    except PermissionError:
        calls.chmod(name, 0o700, dir_fd=parent_fd)
        fd = calls.open(name, _directory_open_flags(), dir_fd=parent_fd)
    except FileNotFoundError:
        return False
    try:
        if _object_identity(calls.fstat(fd)) != owned_identity:
            return False
        _clear_owned_directory(calls, fd, owned_identities, owned_bindings)
    finally:
        calls.close(fd)
    try:
        current = calls.stat(name, dir_fd=parent_fd)
    except FileNotFoundError:
        return False
    if stat.S_ISDIR(current.st_mode) and _object_identity(current) == owned_identity:
        try:
            calls.rmdir(name, dir_fd=parent_fd)
        except OSError as error:
            if error.errno in {errno.ENOTEMPTY, errno.EEXIST}:
                return False
            raise
        calls.fsync(parent_fd)
        return True
    return False


def _rollback_owned_directory(
    calls: _SystemCalls,
    parent_fd: int,
    parent_identity: tuple[int, int],
    owned_identity: tuple[int, int],
    owned_identities: set[tuple[int, int]],
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None],
) -> None:
    if _object_identity(calls.fstat(parent_fd)) != parent_identity:
        _fail("publication parent changed before rollback")
    for _ in range(3):
        matches: list[str] = []
        for name in sorted(calls.listdir(parent_fd)):
            try:
                value = calls.stat(name, dir_fd=parent_fd)
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(value.st_mode) and _object_identity(value) == owned_identity:
                matches.append(name)
        if not matches:
            break
        for name in matches:
            _remove_owned_directory_at_name(
                calls,
                parent_fd,
                name,
                owned_identity,
                owned_identities,
                owned_bindings,
            )
    for name in calls.listdir(parent_fd):
        try:
            value = calls.stat(name, dir_fd=parent_fd)
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(value.st_mode) and _object_identity(value) == owned_identity:
            _fail("owned publication rollback incomplete")


def _remove_owned_lock(
    calls: _SystemCalls,
    parent_fd: int,
    lock_name: str,
    lock_identity: tuple[int, int] | None,
    *,
    require_path_identity: bool,
) -> bool:
    if lock_identity is None:
        return True
    matches: list[tuple[str, os.stat_result]] = []
    for name in sorted(calls.listdir(parent_fd)):
        try:
            value = calls.stat(name, dir_fd=parent_fd)
        except FileNotFoundError:
            continue
        if _object_identity(value) == lock_identity:
            matches.append((name, value))
    path_was_owned = any(name == lock_name for name, _ in matches)
    if len(matches) > 1 or any(value.st_nlink != 1 for _, value in matches):
        return False
    if matches:
        calls.unlink(matches[0][0], dir_fd=parent_fd)
    calls.fsync(parent_fd)
    for name in calls.listdir(parent_fd):
        try:
            value = calls.stat(name, dir_fd=parent_fd)
        except FileNotFoundError:
            continue
        if _object_identity(value) == lock_identity:
            return False
    try:
        calls.stat(lock_name, dir_fd=parent_fd)
    except FileNotFoundError:
        fixed_name_absent = True
    else:
        fixed_name_absent = False
    if require_path_identity:
        return path_was_owned and fixed_name_absent
    return True


def _publication_attestation(config: _Config) -> dict[str, Any]:
    return {
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
        "source_same_fd_read_hash_with_pre_post_fstat": True,
        "stage_is_hidden_and_same_parent": True,
    }


def _receipt(
    config: _Config,
    root_value: os.stat_result,
    entries: list[dict[str, Any]],
) -> bytes:
    document = {
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
            "schema": MATERIALIZER_SCHEMA,
            **_publication_attestation(config),
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
    raw = canonical_json_bytes(document)
    if len(raw) > MAX_RECEIPT_BYTES:
        _fail("receipt exceeds byte cap")
    return raw


def _materialize_with_config(
    static_inventory_bytes: bytes,
    config: _Config,
    calls: _SystemCalls,
) -> bytes:
    """Private tmp-test seam; production callers must use the public API."""

    _validate_config(config)
    _decode_inventory(static_inventory_bytes, config)
    root = Path(config.authority_root)
    parent_path = Path(config.publication_parent)
    try:
        parent_fd = _open_absolute_directory(calls, parent_path)
    except OSError as error:
        _fail(
            "fixed publication parent must preexist as a no-symlink directory; "
            f"it was not created: {error}"
        )
    parent_identity = _object_identity(calls.fstat(parent_fd))
    try:
        _require_parent_security(calls, parent_fd, config, "before lock acquisition")
    except BaseException:
        calls.close(parent_fd)
        raise

    lock_fd = -1
    lock_identity: tuple[int, int] | None = None
    owned_fd = -1
    owned_identity: tuple[int, int] | None = None
    owned_identities: set[tuple[int, int]] = set()
    owned_bindings: dict[tuple[int, int, str], tuple[int, int] | None] = {}
    stage_name = config.deterministic_stage_name or (
        f".{root.name}.stage-{os.getpid()}-{secrets.token_hex(16)}"
    )
    if "/" in stage_name or not stage_name.startswith(".") or stage_name in {".", ".."}:
        calls.close(parent_fd)
        _fail("unsafe hidden stage name")
    stage_binding = (*parent_identity, stage_name)

    def rollback_created_stage() -> None:
        nonlocal owned_identity
        if owned_identity is None and stage_binding in owned_bindings:
            try:
                recovered = calls.stat(stage_name, dir_fd=parent_fd)
            except FileNotFoundError:
                return
            if not stat.S_ISDIR(recovered.st_mode):
                _fail("created hidden stage was replaced before rollback")
            recovered_identity = _object_identity(recovered)
            recorded = owned_bindings[stage_binding]
            if recorded is not None and recorded != recovered_identity:
                _fail("created hidden stage identity changed before rollback")
            owned_identity = recovered_identity
            owned_bindings[stage_binding] = recovered_identity
            owned_identities.add(recovered_identity)
        if owned_identity is not None:
            _rollback_owned_directory(
                calls,
                parent_fd,
                parent_identity,
                owned_identity,
                owned_identities,
                owned_bindings,
            )

    try:
        lock_flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        lock_fd = calls.open(config.lock_name, lock_flags, 0o600, dir_fd=parent_fd)
        lock_identity = _object_identity(calls.fstat(lock_fd))
        _prepare_owned_fd(calls, lock_fd)
        calls.fsync(lock_fd)
        calls.event("after_lock", parent_fd=parent_fd, lock_name=config.lock_name)
        try:
            calls.stat(root.name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        else:
            _fail("fixed authority root already exists")
        try:
            calls.stat(stage_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        else:
            _fail("hidden stage already exists")

        source_bytes = [(spec, _read_source(calls, spec)) for spec in config.sources]
        calls.mkdir(stage_name, 0o700, dir_fd=parent_fd)
        owned_bindings[stage_binding] = None
        stage_value = calls.stat(stage_name, dir_fd=parent_fd)
        if not stat.S_ISDIR(stage_value.st_mode):
            _fail("new hidden stage is not a directory")
        owned_identity = _object_identity(stage_value)
        owned_bindings[stage_binding] = owned_identity
        owned_identities.add(owned_identity)
        calls.chmod(stage_name, 0o700, dir_fd=parent_fd)
        owned_fd = calls.open(stage_name, _directory_open_flags(), dir_fd=parent_fd)
        if _object_identity(calls.fstat(owned_fd)) != owned_identity:
            _fail("hidden stage identity changed before preparation")
        _prepare_owned_fd(calls, owned_fd)
        calls.event("after_stage", parent_fd=parent_fd, stage_name=stage_name)
        directories: set[PurePosixPath] = set()
        for spec, raw in source_bytes:
            _write_staged_file(
                calls,
                owned_fd,
                spec,
                raw,
                owned_identities,
                owned_bindings,
            )
            parent = _safe_relative(spec.relative_path).parent
            while parent != PurePosixPath("."):
                directories.add(parent)
                parent = parent.parent
        _seal_directories(calls, owned_fd, directories)
        calls.event(
            "before_publish",
            parent_fd=parent_fd,
            stage_name=stage_name,
            root_name=root.name,
        )
        _require_path_anchor(
            calls,
            parent_path,
            parent_fd,
            parent_identity,
            "before publication",
        )
        _require_parent_security(calls, parent_fd, config, "before publication")
        calls.rename_exclusive(parent_fd, stage_name, root.name)
        calls.fsync(parent_fd)
        calls.event(
            "after_publish",
            parent_fd=parent_fd,
            stage_name=stage_name,
            root_name=root.name,
            owned_identity=owned_identity,
        )
        _require_path_anchor(
            calls,
            parent_path,
            parent_fd,
            parent_identity,
            "after publication",
        )
        _require_parent_security(calls, parent_fd, config, "after publication")
        calls.event("before_ack", parent_fd=parent_fd, root_name=root.name)
        root_value, entries = _scan_tree(
            calls,
            parent_fd,
            root.name,
            owned_identity,
            config,
        )
        calls.event("after_ack", parent_fd=parent_fd, root_name=root.name)
        _confirm_root_snapshot(calls, parent_fd, root.name, root_value, config)
        _require_path_anchor(
            calls,
            parent_path,
            parent_fd,
            parent_identity,
            "after acknowledgement",
        )
        _require_parent_security(calls, parent_fd, config, "after acknowledgement")
        receipt = _receipt(config, root_value, entries)
        calls.event(
            "before_success_lock_removal",
            parent_fd=parent_fd,
            lock_name=config.lock_name,
        )
        if not _remove_owned_lock(
            calls,
            parent_fd,
            config.lock_name,
            lock_identity,
            require_path_identity=True,
        ):
            _fail("invocation lock pathname was replaced before successful cleanup")
        lock_identity = None
        return receipt
    except FileExistsError as error:
        rollback_created_stage()
        _fail(f"exclusive publication object appeared concurrently: {error}")
    except OSError as error:
        rollback_created_stage()
        _fail(f"sealed runtime root publication failed closed: {error}")
    except BaseException:
        rollback_created_stage()
        raise
    finally:
        if lock_identity is None and lock_fd >= 0:
            try:
                lock_value = calls.fstat(lock_fd)
            except OSError:
                pass
            else:
                if stat.S_ISREG(lock_value.st_mode) and lock_value.st_nlink == 1:
                    lock_identity = _object_identity(lock_value)
        if owned_fd >= 0:
            calls.close(owned_fd)
        if lock_fd >= 0:
            calls.close(lock_fd)
        _remove_owned_lock(
            calls,
            parent_fd,
            config.lock_name,
            lock_identity,
            require_path_identity=False,
        )
        calls.close(parent_fd)


def materialize_sealed_runtime_root_v1(static_inventory_bytes: bytes) -> bytes:
    """Publish only the frozen production root and return its canonical receipt."""

    return _materialize_with_config(static_inventory_bytes, PUBLIC_CONFIG, _SystemCalls())


def main() -> int:
    """There is deliberately no executable materialization CLI."""

    print(
        "HOLD_C1_N0_SEALED_RUNTIME_ROOT_V1: "
        "no CLI; call the fixed public API with authenticated inventory bytes",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUTHORITY_ROOT",
    "INVENTORY_BYTE_LENGTH",
    "INVENTORY_SCHEMA",
    "INVENTORY_SHA256",
    "RECEIPT_SCHEMA",
    "SealedRuntimeRootMaterializationFailure",
    "materialize_sealed_runtime_root_v1",
]
