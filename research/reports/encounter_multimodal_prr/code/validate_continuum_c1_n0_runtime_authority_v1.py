"""Validate a static C1/n=0 runtime byte-pin inventory.

All file images are immutable bytes supplied by the caller.  This validator
never opens or executes a serialized pathname and consequently makes no
pathname-TOCTOU or hostile-writer claim.  Mach-O parsing is implemented
separately from the builder; that is not formal independence evidence.  It
validates the selected arm64 slice before reconstructing the pinned
dependency-edge inventory.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import struct
from collections import Counter
from typing import Any, NoReturn

SCHEMA = "encounter_continuum_c1_n0_runtime_byte_pin_inventory_v1"
STATUS = (
    "STATIC_RUNTIME_BYTE_PIN_INVENTORY_ONLY_NO_PROBE_NO_RUNTIME_CLOSURE_"
    "NO_CANDIDATE_EXECUTION_NO_SCIENCE"
)
OPERATION_MODEL_SCHEMA = "encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate"
OPERATION_MODEL_PATH = (
    "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json"
)
OPERATION_MODEL_SHA256 = "ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b"
PROCESS_CONTRACT_SECTION_SHA256 = "47ae856b647fa7be1119f68f684e36e253730bf2a87345ff634979d2893d4833"

MAX_AUTHORITY_BYTES = 262_144
MAX_OPERATION_MODEL_BYTES = 1_048_576
MAX_RUNTIME_FILE_BYTES = 33_554_432
MAX_TOTAL_AUTHENTICATED_BYTES = 100_663_296
MAX_PATH_CHARS = 2_048
MAX_TEXT_CHARS = 4_096
MAX_JSON_DEPTH = 64
MAX_JSON_CONTAINER_ITEMS = 8_192
MAX_JSON_INTEGER_BITS = 64
MAX_FAT_ARCHES = 16
MAX_LOAD_COMMANDS = 4_096
MAX_LOAD_COMMAND_BYTES = 16_777_216

CPU_TYPE_ARM64 = 0x0100000C
CPU_SUBTYPE_ARM64_ALL = 0
MH_EXECUTE = 0x2
MH_DYLIB = 0x6
MH_BUNDLE = 0x8

LC_LOAD_DYLIB = 0xC
LC_ID_DYLIB = 0xD
LC_LOAD_DYLINKER = 0xE
LC_LOAD_WEAK_DYLIB = 0x80000018
LC_REEXPORT_DYLIB = 0x8000001F
LC_LAZY_LOAD_DYLIB = 0x20
LC_LOAD_UPWARD_DYLIB = 0x80000023
LC_RPATH = 0x8000001C
LC_DYLD_ENVIRONMENT = 0x27

EDGE_COMMANDS = {
    LC_LOAD_DYLIB: "LC_LOAD_DYLIB",
    LC_LOAD_DYLINKER: "LC_LOAD_DYLINKER",
}
PROHIBITED_COMMANDS = {
    LC_RPATH: "LC_RPATH",
    LC_DYLD_ENVIRONMENT: "LC_DYLD_ENVIRONMENT",
    0x6: "LC_LOADFVMLIB",
    0x10: "LC_PREBOUND_DYLIB",
    LC_LOAD_WEAK_DYLIB: "LC_LOAD_WEAK_DYLIB",
    LC_REEXPORT_DYLIB: "LC_REEXPORT_DYLIB",
    LC_LAZY_LOAD_DYLIB: "LC_LAZY_LOAD_DYLIB",
    LC_LOAD_UPWARD_DYLIB: "LC_LOAD_UPWARD_DYLIB",
}

AUTHORITY_ROOT = (
    "/Users/ae23069/.local-build/valley-k-small/runtime-authorities/"
    "encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1"
)
PYTHON_PATH = AUTHORITY_ROOT + "/bin/python3.12"
GMPY2_WRAPPER_PATH = AUTHORITY_ROOT + "/site-packages/gmpy2/__init__.py"
GMPY2_EXTENSION_PATH = AUTHORITY_ROOT + "/site-packages/gmpy2/gmpy2.cpython-312-darwin.so"
NUMERICAL_LIBRARY_ROOT = AUTHORITY_ROOT + "/site-packages/gmpy2.libs"
GMP_PATH = NUMERICAL_LIBRARY_ROOT + "/libgmp.10.dylib"
MPFR_PATH = NUMERICAL_LIBRARY_ROOT + "/libmpfr.6.dylib"
MPC_PATH = NUMERICAL_LIBRARY_ROOT + "/libmpc.3.dylib"
EXPECTED_FILE_SHA256 = {
    PYTHON_PATH: "31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805",
    GMPY2_WRAPPER_PATH: ("3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2"),
    GMPY2_EXTENSION_PATH: ("9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b"),
    GMP_PATH: "22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049",
    MPFR_PATH: "d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed",
    MPC_PATH: "d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c",
}
PYTHON_FRAMEWORK_PATH = (
    "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/Python"
)
HOST_BOUNDARY_EDGES = (
    {"boundary_kind": "python_runtime", "path": PYTHON_FRAMEWORK_PATH},
    {"boundary_kind": "apple_system", "path": "/usr/lib/dyld"},
    {"boundary_kind": "apple_system", "path": "/usr/lib/libSystem.B.dylib"},
)
DECLARED_UNOBSERVED_RUNTIME_EXPECTATIONS = {
    "darwin_release": "25.5.0",
    "future_observation_requirement": (
        "FUTURE_AUTHENTICATED_RUNTIME_PROBE_REQUIRED_BEFORE_RUNTIME_CLOSURE"
    ),
    "gmp_version": "GMP 6.3.0",
    "gmpy2_version": "2.2.1",
    "machine": "arm64",
    "macos_build": "25F84",
    "mpc_version": "MPC 1.3.1",
    "mpfr_version": "MPFR 4.2.1",
    "python_full_version": (
        "3.12.13 (main, Mar  3 2026, 12:39:30) [Clang 17.0.0 (clang-1700.6.3.2)]"
    ),
    "python_soabi": "cpython-312-darwin",
    "status": "DECLARED_EXPECTATIONS_NOT_OBSERVED_BY_THIS_STATIC_INVENTORY",
}

IMAGE_IDS = (
    "gmp",
    "gmpy2_extension",
    "mpc",
    "mpfr",
    "python_executable",
)
NUMERICAL_IMAGE_IDS = frozenset({"gmp", "gmpy2_extension", "mpc", "mpfr"})
EXPECTED_FILE_TYPES = {
    "gmp": MH_DYLIB,
    "gmpy2_extension": MH_BUNDLE,
    "mpc": MH_DYLIB,
    "mpfr": MH_DYLIB,
    "python_executable": MH_EXECUTE,
}
IMAGE_PATHS = {
    "gmp": GMP_PATH,
    "gmpy2_extension": GMPY2_EXTENSION_PATH,
    "mpc": MPC_PATH,
    "mpfr": MPFR_PATH,
    "python_executable": PYTHON_PATH,
}
LIBRARY_COMPONENTS = ("gmp", "mpc", "mpfr")
LIBRARY_PATHS = {"gmp": GMP_PATH, "mpc": MPC_PATH, "mpfr": MPFR_PATH}
EXPECTED_COMMAND_SEQUENCES = {
    "python_executable": (
        0x19,
        0x19,
        0x19,
        0x19,
        0x19,
        0x80000034,
        0x80000033,
        0x2,
        0xB,
        LC_LOAD_DYLINKER,
        0x1B,
        0x32,
        0x2A,
        0x80000028,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        0x26,
        0x29,
        0x1D,
    ),
    "gmpy2_extension": (
        0x19,
        0x19,
        0x19,
        0x19,
        0x80000022,
        0x2,
        0xB,
        0x1B,
        0x32,
        0x2A,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        0x26,
        0x29,
        0x1D,
    ),
    "gmp": (
        0x19,
        0x19,
        0x19,
        0x19,
        LC_ID_DYLIB,
        0x80000022,
        0x2,
        0xB,
        0x1B,
        0x32,
        0x2A,
        LC_LOAD_DYLIB,
        0x26,
        0x29,
        0x1D,
    ),
    "mpfr": (
        0x19,
        0x19,
        0x19,
        0x19,
        LC_ID_DYLIB,
        0x80000022,
        0x2,
        0xB,
        0x1B,
        0x32,
        0x2A,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        0x26,
        0x29,
        0x1D,
    ),
    "mpc": (
        0x19,
        0x19,
        0x19,
        0x19,
        LC_ID_DYLIB,
        0x80000022,
        0x2,
        0xB,
        0x1B,
        0x32,
        0x2A,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        LC_LOAD_DYLIB,
        0x26,
        0x29,
        0x1D,
    ),
}
KNOWN_NON_EDGE_COMMANDS = frozenset(
    command for sequence in EXPECTED_COMMAND_SEQUENCES.values() for command in sequence
) - frozenset({LC_ID_DYLIB, LC_LOAD_DYLIB, LC_LOAD_DYLINKER})
EXPECTED_EDGE_INVENTORY = {
    "python_executable": (
        (9, "LC_LOAD_DYLINKER", "/usr/lib/dyld", "explicit_host_boundary", None),
        (
            14,
            "LC_LOAD_DYLIB",
            PYTHON_FRAMEWORK_PATH,
            "explicit_host_boundary",
            None,
        ),
        (
            15,
            "LC_LOAD_DYLIB",
            "/usr/lib/libSystem.B.dylib",
            "explicit_host_boundary",
            None,
        ),
    ),
    "gmpy2_extension": (
        (
            10,
            "LC_LOAD_DYLIB",
            "@loader_path/../gmpy2.libs/libmpc.3.dylib",
            "pinned_numerical",
            "mpc",
        ),
        (
            11,
            "LC_LOAD_DYLIB",
            "@loader_path/../gmpy2.libs/libmpfr.6.dylib",
            "pinned_numerical",
            "mpfr",
        ),
        (
            12,
            "LC_LOAD_DYLIB",
            "@loader_path/../gmpy2.libs/libgmp.10.dylib",
            "pinned_numerical",
            "gmp",
        ),
        (
            13,
            "LC_LOAD_DYLIB",
            "/usr/lib/libSystem.B.dylib",
            "explicit_host_boundary",
            None,
        ),
    ),
    "gmp": (
        (
            11,
            "LC_LOAD_DYLIB",
            "/usr/lib/libSystem.B.dylib",
            "explicit_host_boundary",
            None,
        ),
    ),
    "mpfr": (
        (
            11,
            "LC_LOAD_DYLIB",
            "@loader_path/libgmp.10.dylib",
            "pinned_numerical",
            "gmp",
        ),
        (
            12,
            "LC_LOAD_DYLIB",
            "/usr/lib/libSystem.B.dylib",
            "explicit_host_boundary",
            None,
        ),
    ),
    "mpc": (
        (
            11,
            "LC_LOAD_DYLIB",
            "@loader_path/libmpfr.6.dylib",
            "pinned_numerical",
            "mpfr",
        ),
        (
            12,
            "LC_LOAD_DYLIB",
            "@loader_path/libgmp.10.dylib",
            "pinned_numerical",
            "gmp",
        ),
        (
            13,
            "LC_LOAD_DYLIB",
            "/usr/lib/libSystem.B.dylib",
            "explicit_host_boundary",
            None,
        ),
    ),
}


class RuntimeAuthorityValidationFailure(RuntimeError):
    """Fail-closed rejection of malformed or unauthenticated authority bytes."""


def _fail(detail: str) -> NoReturn:
    raise RuntimeAuthorityValidationFailure(detail)


def _canonical_json_bytes(value: object) -> bytes:
    try:
        raw = (
            json.dumps(
                value,
                ensure_ascii=True,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError, MemoryError) as exc:
        _fail(f"canonical JSON encoding failed: {type(exc).__name__}")
    return raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ascii_text(value: object, label: str, *, maximum: int = MAX_TEXT_CHARS) -> str:
    if type(value) is not str or not value or len(value) > maximum:
        _fail(f"{label}: bounded nonempty string required")
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        _fail(f"{label}: ASCII required")
    if value != value.strip() or any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        _fail(f"{label}: canonical printable ASCII required")
    return value


def _absolute_path(value: object, label: str) -> str:
    path = _ascii_text(value, label, maximum=MAX_PATH_CHARS)
    if not path.startswith("/") or path == "/" or "//" in path:
        _fail(f"{label}: canonical absolute POSIX path required")
    pure = pathlib.PurePosixPath(path)
    if str(pure) != path or any(part in {"", ".", ".."} for part in pure.parts[1:]):
        _fail(f"{label}: canonical absolute POSIX path required")
    return path


def _within_root(path: str, root: str) -> bool:
    return path.startswith(root + "/")


def _strict_json(raw: bytes, *, maximum_bytes: int, label: str) -> Any:
    if type(raw) is not bytes or not raw or len(raw) > maximum_bytes:
        _fail(f"{label}: bounded immutable bytes required")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        _fail(f"{label}: ASCII JSON required")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                _fail(f"{label}: duplicate JSON key")
            value[key] = item
        return value

    def parse_int(token: str) -> int:
        value = int(token)
        if value.bit_length() > MAX_JSON_INTEGER_BITS:
            _fail(f"{label}: integer exceeds bit cap")
        return value

    try:
        value = json.loads(
            text,
            object_pairs_hook=pairs_hook,
            parse_int=parse_int,
            parse_constant=lambda _token: _fail(f"{label}: nonfinite number forbidden"),
        )
    except RuntimeAuthorityValidationFailure:
        raise
    except (ValueError, UnicodeError, RecursionError, MemoryError) as exc:
        _fail(f"{label}: invalid JSON ({type(exc).__name__})")
    stack: list[tuple[object, int]] = [(value, 1)]
    while stack:
        item, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            _fail(f"{label}: JSON depth cap exceeded")
        if type(item) is dict:
            if len(item) > MAX_JSON_CONTAINER_ITEMS:
                _fail(f"{label}: object item cap exceeded")
            for key, child in item.items():
                _ascii_text(key, f"{label} key")
                stack.append((child, depth + 1))
        elif type(item) is list:
            if len(item) > MAX_JSON_CONTAINER_ITEMS:
                _fail(f"{label}: array item cap exceeded")
            stack.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            _ascii_text(item, f"{label} string")
        elif type(item) is int:
            if item.bit_length() > MAX_JSON_INTEGER_BITS:
                _fail(f"{label}: integer exceeds bit cap")
        elif type(item) not in {bool, type(None)}:
            _fail(f"{label}: unsupported JSON scalar")
    return value


def _validate_operation_model(raw: bytes) -> None:
    model = _strict_json(
        raw,
        maximum_bytes=MAX_OPERATION_MODEL_BYTES,
        label="operation model",
    )
    if _canonical_json_bytes(model) != raw:
        _fail("operation model: noncanonical JSON")
    if type(model) is not dict or model.get("schema") != OPERATION_MODEL_SCHEMA:
        _fail("operation model: wrong schema")
    if _sha256(raw) != OPERATION_MODEL_SHA256:
        _fail("operation model: wrong frozen SHA-256")
    process = model.get("process_contract")
    if type(process) is not dict:
        _fail("operation model: process_contract object required")
    if _sha256(_canonical_json_bytes(process)) != PROCESS_CONTRACT_SECTION_SHA256:
        _fail("operation model: wrong process-contract section SHA-256")


def _lc_string(
    command: bytes,
    endian: str,
    offset_field: int,
    minimum_offset: int,
    label: str,
) -> str:
    if len(command) < offset_field + 4:
        _fail(f"{label}: truncated string-offset field")
    (offset,) = struct.unpack_from(endian + "I", command, offset_field)
    if offset < minimum_offset or offset >= len(command):
        _fail(f"{label}: invalid string offset")
    end = command.find(b"\0", offset)
    if end < 0 or any(command[end + 1 :]):
        _fail(f"{label}: invalid terminated string or padding")
    try:
        text = command[offset:end].decode("ascii")
    except UnicodeDecodeError:
        _fail(f"{label}: non-ASCII string")
    return _ascii_text(text, label, maximum=MAX_PATH_CHARS)


def _arm64_slice(raw: bytes, label: str) -> tuple[bytes, dict[str, Any]]:
    if type(raw) is not bytes or len(raw) < 4 or len(raw) > MAX_RUNTIME_FILE_BYTES:
        _fail(f"{label}: invalid Mach-O byte size")
    if raw[:4] == b"\xcf\xfa\xed\xfe":
        if len(raw) < 32:
            _fail(f"{label}: truncated Mach-O header")
        cputype, cpusubtype = struct.unpack_from("<ii", raw, 4)
        if (cputype, cpusubtype) != (CPU_TYPE_ARM64, CPU_SUBTYPE_ARM64_ALL):
            _fail(f"{label}: exact arm64-all architecture required")
        return raw, {
            "container": "thin",
            "cpusubtype": CPU_SUBTYPE_ARM64_ALL,
            "cputype": CPU_TYPE_ARM64,
            "endianness": "little",
            "offset": 0,
            "size": len(raw),
        }
    if raw[:4] in {
        b"\xfe\xed\xfa\xcf",
        b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xce",
    }:
        _fail(f"{label}: little-endian 64-bit Mach-O required")
    fat_magics = {
        b"\xca\xfe\xba\xbe": (">", False),
        b"\xbe\xba\xfe\xca": ("<", False),
        b"\xca\xfe\xba\xbf": (">", True),
        b"\xbf\xba\xfe\xca": ("<", True),
    }
    if raw[:4] not in fat_magics or len(raw) < 8:
        _fail(f"{label}: Mach-O magic required")
    endian, fat64 = fat_magics[raw[:4]]
    (count,) = struct.unpack_from(endian + "I", raw, 4)
    if not 1 <= count <= MAX_FAT_ARCHES:
        _fail(f"{label}: invalid fat architecture count")
    width = 32 if fat64 else 20
    table_end = 8 + count * width
    if table_end > len(raw):
        _fail(f"{label}: truncated fat architecture table")
    entries: list[tuple[int, int, int, int]] = []
    for index in range(count):
        cursor = 8 + index * width
        cputype, cpusubtype = struct.unpack_from(endian + "ii", raw, cursor)
        if fat64:
            offset, size, align, reserved = struct.unpack_from(endian + "QQII", raw, cursor + 8)
            if reserved != 0:
                _fail(f"{label}: nonzero fat64 reserved field")
        else:
            offset, size, align = struct.unpack_from(endian + "III", raw, cursor + 8)
        if (
            align > 31
            or offset < table_end
            or size < 32
            or offset + size > len(raw)
            or offset % (1 << align)
        ):
            _fail(f"{label}: invalid fat slice bounds/alignment")
        entries.append((cputype, cpusubtype, offset, size))
    intervals = sorted((offset, offset + size) for _, _, offset, size in entries)
    if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
        _fail(f"{label}: overlapping fat slices")
    matches = [entry for entry in entries if entry[0] == CPU_TYPE_ARM64]
    if len(matches) != 1:
        _fail(f"{label}: exactly one arm64 fat slice required")
    cputype, cpusubtype, offset, size = matches[0]
    if cpusubtype != CPU_SUBTYPE_ARM64_ALL:
        _fail(f"{label}: fat arm64 subtype must be ARM64_ALL")
    selected = raw[offset : offset + size]
    if selected[:4] != b"\xcf\xfa\xed\xfe" or len(selected) < 32:
        _fail(f"{label}: selected slice must be little-endian arm64 Mach-O")
    header_cpu, header_subtype = struct.unpack_from("<ii", selected, 4)
    if (header_cpu, header_subtype) != (cputype, cpusubtype):
        _fail(f"{label}: fat and thin architecture metadata disagree")
    return selected, {
        "container": "fat64" if fat64 else "fat32",
        "cpusubtype": CPU_SUBTYPE_ARM64_ALL,
        "cputype": CPU_TYPE_ARM64,
        "endianness": "little",
        "offset": offset,
        "size": size,
    }


def _parse_macho(raw: bytes, image_id: str) -> dict[str, Any]:
    if image_id not in IMAGE_IDS:
        _fail("Mach-O parser: known image_id required")
    selected, slice_info = _arm64_slice(raw, image_id)
    (
        _magic,
        cputype,
        cpusubtype,
        filetype,
        ncmds,
        sizeofcmds,
        _flags,
        reserved,
    ) = struct.unpack_from("<IiiIIIII", selected, 0)
    if (cputype, cpusubtype) != (CPU_TYPE_ARM64, CPU_SUBTYPE_ARM64_ALL):
        _fail(f"{image_id}: exact arm64-all header required")
    if reserved != 0:
        _fail(f"{image_id}: mach_header_64 reserved field must be zero")
    if ncmds > MAX_LOAD_COMMANDS or sizeofcmds > MAX_LOAD_COMMAND_BYTES:
        _fail(f"{image_id}: load-command cap exceeded")
    end = 32 + sizeofcmds
    if end > len(selected):
        _fail(f"{image_id}: truncated load-command region")
    cursor = 32
    command_ids: list[int] = []
    edges: list[dict[str, Any]] = []
    dylib_id: dict[str, Any] | None = None
    for index in range(ncmds):
        if cursor + 8 > end:
            _fail(f"{image_id}: truncated load-command header")
        command_id, command_size = struct.unpack_from("<II", selected, cursor)
        if command_size < 8 or command_size % 8 or cursor + command_size > end:
            _fail(f"{image_id}: invalid load-command size")
        command_ids.append(command_id)
        command = selected[cursor : cursor + command_size]
        if command_id in PROHIBITED_COMMANDS:
            _fail(f"{image_id}: {PROHIBITED_COMMANDS[command_id]} forbidden")
        if command_id == LC_ID_DYLIB:
            if dylib_id is not None or command_size < 24:
                _fail(f"{image_id}: invalid duplicate LC_ID_DYLIB")
            name = _lc_string(command, "<", 8, 24, f"{image_id} LC_ID_DYLIB")
            _, _, _, _, current, compatibility = struct.unpack_from("<IIIIII", command, 0)
            dylib_id = {
                "command_index": index,
                "compatibility_version": compatibility,
                "current_version": current,
                "install_name": name,
            }
        elif command_id in EDGE_COMMANDS:
            minimum = 12 if command_id == LC_LOAD_DYLINKER else 24
            if command_size < minimum:
                _fail(f"{image_id}: truncated dependency command")
            edges.append(
                {
                    "command": EDGE_COMMANDS[command_id],
                    "command_index": index,
                    "load_path": _lc_string(command, "<", 8, minimum, f"{image_id} dependency"),
                }
            )
        elif command_id not in KNOWN_NON_EDGE_COMMANDS:
            _fail(f"{image_id}: unknown load command 0x{command_id:08x}")
        cursor += command_size
    if cursor != end:
        _fail(f"{image_id}: load-command size/count mismatch")
    if tuple(command_ids) != EXPECTED_COMMAND_SEQUENCES[image_id]:
        _fail(f"{image_id}: load-command sequence differs from pinned baseline")
    return {
        "dylib_id": dylib_id,
        "edges": edges,
        "filetype": filetype,
        "load_command_ids": command_ids,
        "slice": slice_info,
    }


def _resolve_loader(source_path: str, edge_path: str, root: str) -> str:
    suffix = edge_path.removeprefix("@loader_path")
    if not suffix.startswith("/") or suffix.endswith("/") or "//" in suffix:
        _fail("Mach-O edge: malformed @loader_path")
    parts = list(pathlib.PurePosixPath(source_path).parent.parts)
    for part in suffix.split("/")[1:]:
        if not part:
            continue
        if part == ".":
            _fail("Mach-O edge: noncanonical @loader_path")
        if part == "..":
            if len(parts) <= 1:
                _fail("Mach-O edge: @loader_path escapes filesystem root")
            parts.pop()
        else:
            parts.append(part)
    resolved = str(pathlib.PurePosixPath(*parts))
    if not _within_root(resolved, root):
        _fail("Mach-O edge: @loader_path escapes authority root")
    return resolved


def _classify(
    image_id: str,
    parsed_edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[str]]:
    source_path = IMAGE_PATHS[image_id]
    numerical_by_path = {
        path: target for target, path in IMAGE_PATHS.items() if target in NUMERICAL_IMAGE_IDS
    }
    boundaries = {item["path"]: item["boundary_kind"] for item in HOST_BOUNDARY_EDGES}
    result: list[dict[str, Any]] = []
    used: set[str] = set()
    numerical_targets: Counter[str] = Counter()
    seen_load_paths: set[str] = set()
    for edge in parsed_edges:
        load_path = edge["load_path"]
        if load_path in seen_load_paths:
            _fail(f"{image_id}: duplicate Mach-O edge")
        seen_load_paths.add(load_path)
        if load_path.startswith(("@rpath", "@executable_path")):
            _fail(f"{image_id}: rpath/executable-path edge forbidden")
        if load_path.startswith("@loader_path"):
            resolved = _resolve_loader(source_path, load_path, AUTHORITY_ROOT)
        elif load_path.startswith("/"):
            resolved = _absolute_path(load_path, f"{image_id} edge")
        else:
            _fail(f"{image_id}: private relative edge forbidden")
        target = numerical_by_path.get(resolved)
        if target is not None:
            if edge["command"] != "LC_LOAD_DYLIB":
                _fail(f"{image_id}: numerical edge must be ordinary LC_LOAD_DYLIB")
            numerical_targets[target] += 1
            result.append(
                {
                    **edge,
                    "classification": "pinned_numerical",
                    "target_image_id": target,
                }
            )
            continue
        if _within_root(resolved, AUTHORITY_ROOT):
            _fail(f"{image_id}: unpinned edge inside authority root")
        kind = boundaries.get(load_path)
        if kind is None:
            _fail(f"{image_id}: unclassified Mach-O edge")
        if _within_root(load_path, AUTHORITY_ROOT):
            _fail(f"{image_id}: host boundary must be outside authority root")
        if edge["command"] == "LC_LOAD_DYLINKER":
            if image_id != "python_executable" or load_path != "/usr/lib/dyld":
                _fail(f"{image_id}: LC_LOAD_DYLINKER placement invalid")
        elif edge["command"] != "LC_LOAD_DYLIB":
            _fail(f"{image_id}: host dylib edge must be ordinary LC_LOAD_DYLIB")
        used.add(load_path)
        result.append(
            {
                **edge,
                "classification": "explicit_host_boundary",
                "target_image_id": None,
            }
        )
    expected = EXPECTED_EDGE_INVENTORY[image_id]
    expected_counter = Counter(
        target
        for _, _, _, classification, target in expected
        if classification == "pinned_numerical"
    )
    if numerical_targets != expected_counter:
        _fail(f"{image_id}: numerical dependency multiplicity differs")
    actual = tuple(
        (
            edge["command_index"],
            edge["command"],
            edge["load_path"],
            edge["classification"],
            edge["target_image_id"],
        )
        for edge in result
    )
    if actual != expected:
        _fail(f"{image_id}: edge inventory differs from pinned baseline")
    return result, used


def _snapshot_files(authenticated_files: object) -> dict[str, bytes]:
    if type(authenticated_files) is not dict:
        _fail("authenticated_files: plain dict required")
    snapshot = dict(authenticated_files)
    expected_paths = {OPERATION_MODEL_PATH, GMPY2_WRAPPER_PATH, *IMAGE_PATHS.values()}
    if set(snapshot) != expected_paths or any(
        type(path) is not str or type(raw) is not bytes for path, raw in snapshot.items()
    ):
        _fail("authenticated_files: exact path-to-immutable-bytes dict required")
    if sum(len(raw) for raw in snapshot.values()) > MAX_TOTAL_AUTHENTICATED_BYTES:
        _fail("authenticated_files: total byte cap exceeded")
    if not 1 <= len(snapshot[GMPY2_WRAPPER_PATH]) <= MAX_RUNTIME_FILE_BYTES:
        _fail("gmpy2 wrapper: byte cap violated")
    return snapshot


def _expected_document(
    operation_binding: dict[str, str],
    images: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "authority_root": AUTHORITY_ROOT,
        "claim_boundary": {
            "authority_root_materialized": False,
            "candidate_execution_performed": False,
            "complete_runtime_closure_claimed": False,
            "host_runtime_bytes_complete": False,
            "import_resolution_observed": False,
            "operation_model_runtime_closure_substitution_allowed": False,
            "path_identity_observed": False,
            "pathname_toctou_closure_claimed": False,
            "runtime_probe_performed": False,
            "runtime_metadata_observed": False,
            "scientific_claim_made": False,
            "trust_boundary": (
                "CALLER_AUTHENTICATED_IMMUTABLE_BYTES_ONLY_NO_PATHNAME_OR_CONCURRENT_WRITER_CLAIM"
            ),
        },
        "declared_unobserved_runtime_expectations": (DECLARED_UNOBSERVED_RUNTIME_EXPECTATIONS),
        "gmpy2": {
            "extension": {
                "import_name": "gmpy2.gmpy2",
                "path": GMPY2_EXTENSION_PATH,
                "sha256": EXPECTED_FILE_SHA256[GMPY2_EXTENSION_PATH],
            },
            "wrapper": {
                "import_name": "gmpy2",
                "path": GMPY2_WRAPPER_PATH,
                "sha256": EXPECTED_FILE_SHA256[GMPY2_WRAPPER_PATH],
            },
        },
        "host_boundary_edges": [dict(item) for item in HOST_BOUNDARY_EDGES],
        "macho_images": images,
        "numerical_libraries": [
            {
                "component": component,
                "path": LIBRARY_PATHS[component],
                "sha256": EXPECTED_FILE_SHA256[LIBRARY_PATHS[component]],
            }
            for component in LIBRARY_COMPONENTS
        ],
        "operation_model": operation_binding,
        "python": {
            "path": PYTHON_PATH,
            "sha256": EXPECTED_FILE_SHA256[PYTHON_PATH],
        },
        "schema": SCHEMA,
        "status": STATUS,
    }


def validate_runtime_authority(
    authority_bytes: bytes,
    authenticated_files: object,
) -> dict[str, Any]:
    """Validate exact static inventory bytes and return the parsed document."""

    snapshot = _snapshot_files(authenticated_files)
    document = _strict_json(
        authority_bytes,
        maximum_bytes=MAX_AUTHORITY_BYTES,
        label="runtime byte-pin inventory",
    )
    if _canonical_json_bytes(document) != authority_bytes:
        _fail("runtime byte-pin inventory: noncanonical JSON")
    _validate_operation_model(snapshot[OPERATION_MODEL_PATH])
    operation_binding = {
        "path": OPERATION_MODEL_PATH,
        "process_contract_section_sha256": PROCESS_CONTRACT_SECTION_SHA256,
        "schema": OPERATION_MODEL_SCHEMA,
        "sha256": OPERATION_MODEL_SHA256,
    }
    for path, expected_sha in EXPECTED_FILE_SHA256.items():
        if _sha256(snapshot[path]) != expected_sha:
            _fail(f"{path}: byte SHA-256 differs from pinned baseline")
    expected_images: list[dict[str, Any]] = []
    used_boundaries: set[str] = set()
    for image_id in IMAGE_IDS:
        path = IMAGE_PATHS[image_id]
        raw = snapshot[path]
        parsed = _parse_macho(raw, image_id)
        if parsed["filetype"] != EXPECTED_FILE_TYPES[image_id]:
            _fail(f"{image_id}: unexpected Mach-O filetype")
        if image_id in {"gmp", "mpc", "mpfr"} and parsed["dylib_id"] is None:
            _fail(f"{image_id}: LC_ID_DYLIB required")
        if image_id in {"gmpy2_extension", "python_executable"} and (
            parsed["dylib_id"] is not None
        ):
            _fail(f"{image_id}: LC_ID_DYLIB forbidden")
        edges, used = _classify(image_id, parsed["edges"])
        used_boundaries.update(used)
        expected_images.append(
            {
                "dylib_id": parsed["dylib_id"],
                "edges": edges,
                "filetype": parsed["filetype"],
                "image_id": image_id,
                "load_command_ids": parsed["load_command_ids"],
                "path": path,
                "sha256": EXPECTED_FILE_SHA256[path],
                "slice": parsed["slice"],
            }
        )
    if used_boundaries != {item["path"] for item in HOST_BOUNDARY_EDGES}:
        _fail("host_boundary_edges: unused or missing exact edge")
    expected_document = _expected_document(operation_binding, expected_images)
    if document != expected_document:
        _fail("runtime byte-pin inventory differs from exact static oracle")
    return document


__all__ = [
    "OPERATION_MODEL_PATH",
    "RuntimeAuthorityValidationFailure",
    "SCHEMA",
    "validate_runtime_authority",
]
