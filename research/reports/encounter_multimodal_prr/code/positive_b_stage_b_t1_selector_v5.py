"""Unique frozen Stage-B-v5 T0 saved-object selector implementation.

This module is a library only.  It has no command-line entry point, opens no
Stage-A/Stage-B object, and imports no scientific producer.  Callers supply a
canonical-JSON byte payload.  Every decision is made from exact binary64
leaves using :class:`fractions.Fraction` and the pinned MPFR runtime required
by the frozen v5 design.

The public high-level entry point is :func:`select_saved_controls_bytes`.
Supplying data does not authorize science: the only accepted authorization
literal, copied into every output, is ``AUTHORIZED-SCIENTIFIC-COMMAND: NONE``.
"""

# ruff: noqa: E402, I001 -- the verified entry gate intentionally precedes imports
from __future__ import annotations

import os
import sys


class Hold(ValueError):
    """A normative T0/T1 condition failed and processing must stop."""


def _expected_trust_contract() -> dict[str, str]:
    return {
        "bootstrap_trust_base": ("CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES"),
        "native_image_execution": ("PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT"),
        "protection_claim": "DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY",
        "runtime_tree_concurrency": ("NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS"),
        "schema": "positive-b-stage-b-t0-execution-trust-contract-v1",
        "wrapper_execution": "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
    }


def _guard_runtime_identity(stage: str) -> None:
    """Invoke the loader-captured builtins/import-machinery identity guard."""

    guard = globals().get("_T0_RUNTIME_IDENTITY_GUARD")
    if guard is None:
        raise Hold("T0 source requires the runtime identity guard")
    guard(stage)


def _require_preimport_verified_entry() -> dict[str, object]:
    """HOLD before gmpy2 import unless the isolated exact loader injected trust."""

    context = globals().get("_T0_VERIFIED_ENTRY_CONTEXT")
    if not isinstance(context, dict) or set(context) != {
        "external_attestation_schema",
        "external_attestation_sha256",
        "external_attestation_status",
        "mode",
        "production_eligible",
        "trust_contract",
    }:
        raise Hold("T0 source requires the isolated verified loader before runtime import")
    digest = context["external_attestation_sha256"]
    synthetic = (
        context["external_attestation_schema"]
        == "positive-b-stage-b-t0-synthetic-test-attestation-v2"
        and context["external_attestation_status"] == "NON-PROMOTABLE-SYNTHETIC-TEST"
        and context["mode"] == "VERIFIED-ISOLATED-SYNTHETIC-TEST"
        and context["production_eligible"] is False
    )
    production = (
        context["external_attestation_schema"] == "positive-b-stage-b-t0-external-attestation-v2"
        and context["external_attestation_status"] == "INDEPENDENT-ATTACK-PASS"
        and context["mode"] == "VERIFIED-ISOLATED"
        and context["production_eligible"] is True
    )
    if (
        not (synthetic or production)
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
        or context["trust_contract"] != _expected_trust_contract()
        or sys.flags.isolated != 1
        or sys.flags.no_site != 1
    ):
        raise Hold("T0 pre-import entry context is not isolated and canonical")
    injected = sorted(
        name
        for name, value in os.environ.items()
        if value and (name.startswith("DYLD_") or name in {"LD_LIBRARY_PATH", "LD_PRELOAD"})
    )
    if injected:
        raise Hold(f"native-loader injection environment is forbidden: {injected}")
    _guard_runtime_identity("selector pre-import entry")
    copied = dict(context)
    copied["trust_contract"] = dict(context["trust_contract"])
    return copied


PREIMPORT_ENTRY_ATTESTATION = _require_preimport_verified_entry()

# Everything below this line is imported only after the isolated loader's
# injected entry context has passed.  This prevents ordinary module search or
# a forged critical-stdlib preload from executing before the source HOLD.
import ctypes
import hashlib
import importlib.machinery
import json
import math
import platform
import re
import stat
import struct
import sysconfig
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

try:
    import gmpy2
except ImportError:  # pragma: no cover - exercised through fail-closed runtime tests
    gmpy2 = None


CRITICAL_STDLIB_MODULES: Final = {
    "_ctypes": sys.modules.get("_ctypes"),
    "ctypes": ctypes,
    "ctypes._endian": sys.modules.get("ctypes._endian"),
    "platform": platform,
    "sysconfig": sysconfig,
}

_guard_runtime_identity("selector after runtime imports")


REPORT_ROOT: Final = Path(os.path.abspath(Path(__file__).parent.parent))
IMPLEMENTATION_NAME: Final = "positive_b_stage_b_t1_selector_v5.py"
DESIGN_V5_RELATIVE: Final = Path("notes/positive_b_stage_b_validation_design_v5.md")
DESIGN_V4_RELATIVE: Final = Path("notes/positive_b_stage_b_validation_design_v4.md")
ROUND73_RELATIVE: Final = Path("audits/round_73_stageb_v5_independent_attack.md")
RUNTIME_LOCK_RELATIVE: Final = Path("code/positive_b_stage_b_t0_runtime_lock_v2.json")

DESIGN_V5_SHA256: Final = "136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd"
DESIGN_V4_SHA256: Final = "e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691"
ROUND73_SHA256: Final = "36c0f502b90cb98e8cdeedd5a1621b0ffa1e3bcc5bc49b5490d1eccde9e7dcf8"
RUNTIME_LOCK_SHA256: Final = "7321fb3ce442276f4b2ff1b7c6f58c844926fba63bcca2270e10e53fb5f44ecf"

AUTHORIZATION_NONE: Final = "AUTHORIZED-SCIENTIFIC-COMMAND: NONE"
INPUT_SCHEMA: Final = "positive-b-stage-b-t0-selector-input-v1"
OUTPUT_SCHEMA: Final = "positive-b-stage-b-t0-selector-output-v3"
ROLE_RADIUS_SCHEMA: Final = "positive-b-stage-b-t0-role-radii-v3"
ROLE_RADIUS_INPUT_SCHEMA: Final = "positive-b-stage-b-t0-role-radii-input-v1"

TARGET: Final = float.fromhex("0x1.8000000000000p-1")
THETA_BOUND: Final = float.fromhex("0x1.3333333333333p-3")
TIME_SCALE: Final = float.fromhex("0x1.1400000000000p+5")
RHO_CAP: Final = float.fromhex("0x1.0000000000000p-7")
ODD_FLOOR: Final = float.fromhex("0x1.ad7f29abcaf48p-25")
MIN_SUBNORMAL: Final = float.fromhex("0x0.0000000000001p-1022")
EXP_TINY_CUTOFF: Final = -1000.0

TARGET_HEX: Final = TARGET.hex()
UINT64_MAX: Final = (1 << 64) - 1
MAX_SNAPSHOT_BYTES: Final = 8 * 1024 * 1024
BRANCH_ID_RE: Final = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")

# The T0 MPFR vehicle is intentionally platform-byte-pinned.  Algebraic
# operations never depend on compiler floating-point contraction; they are
# exact Fractions.  The extension is used only for outward sqrt enclosures,
# with exact rational square/midpoint checks deciding equality and ties.
GMPY2_VERSION: Final = "2.2.1"
MPFR_VERSION: Final = "MPFR 4.2.1"
GMP_VERSION: Final = "GMP 6.3.0"
MPC_VERSION: Final = "MPC 1.3.1"
GMPY2_PACKAGE_INIT_NAME: Final = "__init__.py"
GMPY2_PACKAGE_INIT_SHA256: Final = (
    "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2"
)
GMPY2_EXTENSION_NAME: Final = "gmpy2.cpython-312-darwin.so"
GMPY2_EXTENSION_SHA256: Final = "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b"
GMPY2_PACKAGE_FILE_HASHES: Final = (
    ("__init__.pxd", "de9ed5a04d31e6b5b1381d783bca4210e0a547a037dd543ed66cb068d78e7e53"),
    ("__init__.py", GMPY2_PACKAGE_INIT_SHA256),
    (
        "__pycache__/__init__.cpython-312.pyc",
        "54d8fdae082333ac0e23fd407c9682998158ee614b767b491289a6de13dade94",
    ),
    ("gmp.h", "c8ec93de51c0c3a329af7702ca8f98469bc7eb90225d4405711eea1a6555e76b"),
    (GMPY2_EXTENSION_NAME, GMPY2_EXTENSION_SHA256),
    ("gmpy2.h", "c15fa409c1f49bb7ff1c4481459c72c0379a0bb35a62491debc13c86734c54a5"),
    ("gmpy2.pxd", "f36a87076d4fd08e64f11bc915fcefb66a3e17248b8c09f670f07702395eb8e2"),
    ("mpc.h", "bca641f4c59f5303d3212650cc00fec0ee2659a220067535dee9029761e83849"),
    ("mpfr.h", "0f1bf63d924c33f3f73d3fc68b049d9f01523a021f89fa4d8910e35122151e33"),
)
GMPY2_BUNDLED_LIBRARY_HASHES: Final = (
    (
        "libgmp.10.dylib",
        "22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049",
    ),
    (
        "libmpc.3.dylib",
        "d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c",
    ),
    (
        "libmpfr.6.dylib",
        "d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed",
    ),
)
GMPY2_NATIVE_EXPORTS: Final = (
    "RoundDown",
    "RoundUp",
    "context",
    "exp",
    "get_context",
    "is_finite",
    "log",
    "mp_version",
    "mpc_version",
    "mpfr",
    "mpfr_version",
    "mpq",
    "sqrt",
    "version",
)
PYTHON_ABI: Final = (3, 12)
HOST_SYSTEM: Final = "Darwin"
HOST_MACHINE: Final = "arm64"
PYTHON_COMPILER: Final = "clang"
PYTHON_CFLAGS: Final = (
    "-fno-strict-overflow -Wsign-compare -Wunreachable-code -fno-common "
    "-dynamic -DNDEBUG -g -O3 -Wall"
)
MPFR_EMAX: Final = 1_073_741_823
MPFR_EMIN: Final = -1_073_741_823

Interval = tuple[float, float]
VectorInterval = tuple[Interval, ...]
Theta = tuple[float, float]
Point = tuple[float, float, float]


@dataclass(frozen=True)
class Frame:
    """The exact RN oriented frame and local scale for one saved branch."""

    tangent: Theta
    normal: Theta
    ell: float
    previous: Point
    base: Point
    following: Point
    comparison_rank: tuple[float, float, int]
    acceptance_index: int


@dataclass(frozen=True)
class CandidateMeasure:
    """A validated joined candidate and its RN chart coordinates."""

    index: int
    theta_hex: tuple[str, str]
    weights_hex: tuple[str, str, str, str]
    count: int
    topology: str
    s: float
    q: float
    radius: float


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], role: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise Hold(f"{role} schema mismatch; missing={missing}, extra={extra}")


def _require_mapping(value: Any, role: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise Hold(f"{role} must be a JSON object")
    return value


def _require_list(value: Any, role: str) -> list[Any]:
    if not isinstance(value, list):
        raise Hold(f"{role} must be a JSON array")
    return value


def _require_uint64(value: Any, role: str) -> int:
    if type(value) is not int or not 0 <= value <= UINT64_MAX:
        raise Hold(f"{role} must be an unsigned 64-bit integer")
    return value


def _require_branch_id(value: Any, role: str) -> str:
    if not isinstance(value, str) or BRANCH_ID_RE.fullmatch(value) is None:
        raise Hold(f"{role} is not a canonical branch identifier")
    return value


def canonical_float(value: float) -> float:
    """Reject non-binary64 values/nonfinites and canonicalize signed zero."""

    if type(value) is not float or not math.isfinite(value):
        raise Hold("expected a finite binary64 value")
    return 0.0 if value == 0.0 else value


def exact(value: float) -> Fraction:
    """Interpret a finite binary64 leaf as its exact rational value."""

    return Fraction.from_float(canonical_float(value))


def float_hex(value: float) -> str:
    """Return the v5 lowercase, signed-zero-canonical binary64 spelling."""

    return canonical_float(value).hex()


def parse_float_hex(value: Any, role: str) -> float:
    """Parse only the unique canonical ``float.hex`` spelling."""

    if not isinstance(value, str) or value != value.lower():
        raise Hold(f"{role} must be a lowercase canonical float.hex string")
    try:
        parsed = float.fromhex(value)
    except ValueError as exc:
        raise Hold(f"{role} is not a float.hex value") from exc
    parsed = canonical_float(parsed)
    if parsed.hex() != value:
        raise Hold(f"{role} is not the unique canonical float.hex spelling")
    return parsed


def _float_bits(value: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", canonical_float(value)))[0]


def _bits_float(bits: int) -> float:
    return struct.unpack(">d", struct.pack(">Q", bits))[0]


def next_up(value: float) -> float:
    """Return exact binary64 adjacency without a host-libm decision."""

    value = canonical_float(value)
    if value == 0.0:
        return _bits_float(1)
    bits = _float_bits(value)
    candidate = _bits_float(bits + 1 if value > 0.0 else bits - 1)
    if not math.isfinite(candidate):
        raise Hold("nextUp leaves the finite binary64 domain")
    return canonical_float(candidate)


def next_down(value: float) -> float:
    """Return exact binary64 adjacency without a host-libm decision."""

    value = canonical_float(value)
    if value == 0.0:
        return _bits_float((1 << 63) | 1)
    bits = _float_bits(value)
    candidate = _bits_float(bits - 1 if value > 0.0 else bits + 1)
    if not math.isfinite(candidate):
        raise Hold("nextDown leaves the finite binary64 domain")
    return canonical_float(candidate)


def rn_fraction(value: Fraction) -> float:
    """Round an exact rational to binary64, ties to even."""

    try:
        rounded = float(value)
    except (OverflowError, ValueError) as exc:
        raise Hold("RN result is outside finite binary64") from exc
    if not math.isfinite(rounded):
        raise Hold("RN result is nonfinite")
    return canonical_float(rounded)


def down64(value: Fraction) -> float:
    """Greatest finite binary64 no larger than an exact rational."""

    rounded = rn_fraction(value)
    if exact(rounded) > value:
        rounded = next_down(rounded)
    if exact(rounded) > value:
        raise Hold("internal down64 enclosure failure")
    return canonical_float(rounded)


def up64(value: Fraction) -> float:
    """Least finite binary64 no smaller than an exact rational."""

    rounded = rn_fraction(value)
    if exact(rounded) < value:
        rounded = next_up(rounded)
    if exact(rounded) < value:
        raise Hold("internal up64 enclosure failure")
    return canonical_float(rounded)


def rn_add(left: float, right: float) -> float:
    return rn_fraction(exact(left) + exact(right))


def rn_sub(left: float, right: float) -> float:
    return rn_fraction(exact(left) - exact(right))


def rn_mul(left: float, right: float) -> float:
    return rn_fraction(exact(left) * exact(right))


def rn_div(left: float, right: float) -> float:
    denominator = exact(right)
    if denominator == 0:
        raise Hold("division by zero")
    return rn_fraction(exact(left) / denominator)


def _lexical_absolute(path: Path) -> Path:
    if not path.is_absolute():
        raise Hold("snapshot path must be absolute")
    return Path(os.path.abspath(path))


def _check_lexical_components(root: Path, path: Path) -> None:
    root = _lexical_absolute(root)
    path = _lexical_absolute(path)
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise Hold("snapshot escapes its lexical root") from exc
    current = root
    components = (Path("."), *relative.parts)
    for component in components:
        if component != Path("."):
            current /= component
        try:
            info = os.lstat(current)
        except FileNotFoundError as exc:
            raise Hold("snapshot component is missing") from exc
        if stat.S_ISLNK(info.st_mode):
            raise Hold("snapshot component is a symbolic link")


def _stat_identity(info: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read_descriptor(fd: int, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = os.read(fd, min(remaining, 65536))
        if not chunk:
            raise Hold("short descriptor read")
        chunks.append(chunk)
        remaining -= len(chunk)
    if os.read(fd, 1):
        raise Hold("snapshot grew during descriptor read")
    return b"".join(chunks)


def _snapshot_regular_file_bytes(
    root: Path,
    path: Path,
    *,
    max_bytes: int = MAX_SNAPSHOT_BYTES,
) -> bytes:
    """Read one stable non-symlink regular-file descriptor exactly once."""

    root = _lexical_absolute(root)
    path = _lexical_absolute(path)
    _check_lexical_components(root, path)
    if not hasattr(os, "O_NOFOLLOW"):
        raise Hold("O_NOFOLLOW is unavailable")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise Hold("cannot open snapshot descriptor") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise Hold("snapshot descriptor is not a regular file")
        if not 0 <= before.st_size <= max_bytes:
            raise Hold("snapshot exceeds the fixed byte cap")
        payload = _read_descriptor(descriptor, before.st_size)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if _stat_identity(before) != _stat_identity(after):
        raise Hold("snapshot descriptor changed during read")
    _check_lexical_components(root, path)
    lexical_after = os.lstat(path)
    if (lexical_after.st_dev, lexical_after.st_ino) != (before.st_dev, before.st_ino):
        raise Hold("snapshot path was replaced during read")
    return payload


def snapshot_regular_file(
    root: Path,
    path: Path,
    expected_sha256: str,
    *,
    max_bytes: int = MAX_SNAPSHOT_BYTES,
) -> bytes:
    """Read one stable non-symlink descriptor and verify its exact bytes."""

    payload = _snapshot_regular_file_bytes(root, path, max_bytes=max_bytes)
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise Hold("snapshot SHA-256 mismatch")
    return payload


def snapshot_regular_file_digest(
    root: Path,
    path: Path,
    *,
    max_bytes: int = MAX_SNAPSHOT_BYTES,
) -> str:
    """Return the SHA-256 of one stable non-symlink descriptor snapshot."""

    payload = _snapshot_regular_file_bytes(root, path, max_bytes=max_bytes)
    return hashlib.sha256(payload).hexdigest()


def verify_normative_snapshots(root: Path = REPORT_ROOT) -> dict[str, str]:
    """Verify the v5/v4 bytes and their independent Round-73 acceptance."""

    pins = (
        ("stage_b_v5_design", DESIGN_V5_RELATIVE, DESIGN_V5_SHA256),
        ("stage_b_v4_import", DESIGN_V4_RELATIVE, DESIGN_V4_SHA256),
        ("round_73_acceptance", ROUND73_RELATIVE, ROUND73_SHA256),
    )
    verified: dict[str, str] = {}
    for role, relative, digest in pins:
        snapshot_regular_file(root, root / relative, digest)
        verified[role] = digest
    return verified


def _module_origin(module: Any, role: str) -> Path:
    """Return one self-consistent absolute module origin or HOLD."""

    module_file = getattr(module, "__file__", None)
    spec = getattr(module, "__spec__", None)
    spec_origin = getattr(spec, "origin", None)
    if not isinstance(module_file, str) or not isinstance(spec_origin, str):
        raise Hold(f"{role} has no concrete file origin")
    origin = Path(os.path.abspath(module_file))
    if not origin.is_absolute() or os.path.abspath(spec_origin) != str(origin):
        raise Hold(f"{role} file/spec origin mismatch")
    return origin


def _verify_critical_stdlib_trust_base() -> dict[str, Any]:
    """Reject critical-module substitution and disclose the external trust base."""

    _guard_runtime_identity("critical stdlib precheck")
    for name, module in CRITICAL_STDLIB_MODULES.items():
        if module is None or sys.modules.get(name) is not module:
            raise Hold(f"critical stdlib identity drift for {name}")

    stdlib_raw = sysconfig.get_path("stdlib")
    extension_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if not isinstance(stdlib_raw, str) or not isinstance(extension_suffix, str):
        raise Hold("critical stdlib layout is unavailable")
    stdlib_root = Path(os.path.abspath(stdlib_raw))
    expected_origins = {
        "_ctypes": stdlib_root / "lib-dynload" / f"_ctypes{extension_suffix}",
        "ctypes": stdlib_root / "ctypes" / "__init__.py",
        "ctypes._endian": stdlib_root / "ctypes" / "_endian.py",
        "platform": stdlib_root / "platform.py",
        "sysconfig": stdlib_root / "sysconfig.py",
    }
    source_modules = {"ctypes", "ctypes._endian", "platform", "sysconfig"}
    origins: dict[str, str] = {}
    for name, expected in expected_origins.items():
        module = CRITICAL_STDLIB_MODULES[name]
        spec = getattr(module, "__spec__", None)
        expected_loader = (
            importlib.machinery.SourceFileLoader
            if name in source_modules
            else importlib.machinery.ExtensionFileLoader
        )
        if not isinstance(getattr(spec, "loader", None), expected_loader):
            raise Hold(f"critical stdlib loader drift for {name}")
        origin = _module_origin(module, f"critical stdlib {name}")
        if origin != expected:
            raise Hold(f"critical stdlib origin drift for {name}")
        origins[name] = str(origin)

    executable = Path(os.path.abspath(sys.executable))
    executable_realpath = Path(os.path.realpath(executable))
    if not executable.is_absolute() or not executable_realpath.is_file():
        raise Hold("CPython executable trust-base path drift")
    _guard_runtime_identity("critical stdlib postcheck")
    return {
        "critical_module_origins": origins,
        "executable": str(executable),
        "executable_realpath": str(executable_realpath),
        "stdlib_root": str(stdlib_root),
    }


def _loaded_gmpy2_native_images() -> set[Path]:
    """Return dyld's actually loaded gmpy2/GMP/MPFR/MPC image paths."""

    dyld = ctypes.CDLL(None)
    image_count = dyld._dyld_image_count
    image_count.argtypes = []
    image_count.restype = ctypes.c_uint32
    image_name = dyld._dyld_get_image_name
    image_name.argtypes = [ctypes.c_uint32]
    image_name.restype = ctypes.c_char_p
    count = int(image_count())
    if not 0 < count < 100_000:
        raise Hold("dyld returned an invalid loaded-image count")
    selected: set[Path] = set()
    native_name = re.compile(r"(?:gmpy2\..*\.so|lib(?:gmp|mpfr|mpc)(?:\.[0-9]+)*\.dylib)\Z")
    for index in range(count):
        encoded = image_name(index)
        if not encoded:
            continue
        try:
            decoded = encoded.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Hold("dyld returned a non-UTF-8 image path") from exc
        path = Path(os.path.abspath(decoded))
        if native_name.fullmatch(path.name):
            selected.add(path)
    return selected


def verify_mpfr_runtime() -> dict[str, Any]:
    """Check the captured wrapper and path-loaded native runtime under contract."""

    _guard_runtime_identity("MPFR runtime precheck")
    cpython_trust_base = _verify_critical_stdlib_trust_base()
    if gmpy2 is None:
        raise Hold("gmpy2/MPFR runtime is unavailable")
    if sys.modules.get("gmpy2") is not gmpy2:
        raise Hold("gmpy2 sys.modules identity drift")
    if getattr(gmpy2, "__name__", None) != "gmpy2":
        raise Hold("gmpy2 package identity drift")
    if (
        getattr(gmpy2, "__t0_wrapper_execution__", None)
        != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
        or getattr(gmpy2, "__t0_wrapper_sha256__", None) != GMPY2_PACKAGE_INIT_SHA256
    ):
        raise Hold("gmpy2 captured-wrapper execution marker drift")
    package_spec = getattr(gmpy2, "__spec__", None)
    if not isinstance(
        getattr(package_spec, "loader", None),
        importlib.machinery.SourceFileLoader,
    ):
        raise Hold("gmpy2 package is not source-loader backed")

    package_init = _module_origin(gmpy2, "gmpy2 package")
    if package_init.name != GMPY2_PACKAGE_INIT_NAME or package_init.parent.name != "gmpy2":
        raise Hold("gmpy2 package path drift")
    package_root = package_init.parent
    package_paths = tuple(os.path.abspath(item) for item in getattr(gmpy2, "__path__", ()))
    if package_paths != (str(package_root),):
        raise Hold("gmpy2 package search path drift")
    try:
        package_names = {entry.name for entry in os.scandir(package_root)}
    except OSError as exc:
        raise Hold("cannot enumerate gmpy2 package root") from exc
    expected_package_names = {
        Path(relative).parts[0] for relative, _digest in GMPY2_PACKAGE_FILE_HASHES
    }
    if package_names != expected_package_names:
        raise Hold("gmpy2 package exact-file closure drift")
    pycache_root = package_root / "__pycache__"
    try:
        pycache_names = {entry.name for entry in os.scandir(pycache_root)}
    except OSError as exc:
        raise Hold("cannot enumerate gmpy2 package pycache") from exc
    expected_pycache_names = {
        Path(relative).name
        for relative, _digest in GMPY2_PACKAGE_FILE_HASHES
        if Path(relative).parts[0] == "__pycache__"
    }
    if pycache_names != expected_pycache_names:
        raise Hold("gmpy2 package pycache closure drift")
    package_hashes: dict[str, str] = {}
    for relative, digest in GMPY2_PACKAGE_FILE_HASHES:
        snapshot_regular_file(package_root, package_root / relative, digest)
        package_hashes[relative] = digest

    extension_module = sys.modules.get("gmpy2.gmpy2")
    if extension_module is None:
        raise Hold("gmpy2 native extension module is not loaded")
    extension_spec = getattr(extension_module, "__spec__", None)
    if not isinstance(
        getattr(extension_spec, "loader", None),
        importlib.machinery.ExtensionFileLoader,
    ):
        raise Hold("gmpy2 native module is not extension-loader backed")
    extension = _module_origin(extension_module, "gmpy2 native extension")
    if extension.parent != package_root or extension.name != GMPY2_EXTENSION_NAME:
        raise Hold("gmpy2 native extension path drift")
    snapshot_regular_file(package_root, extension, GMPY2_EXTENSION_SHA256)
    for export in GMPY2_NATIVE_EXPORTS:
        if getattr(gmpy2, export, None) is not getattr(extension_module, export, None):
            raise Hold(f"gmpy2 wrapper override detected for {export}")

    libraries_root = package_root.parent / "gmpy2.libs"
    _check_lexical_components(package_root.parent, libraries_root)
    try:
        library_names = {entry.name for entry in os.scandir(libraries_root)}
    except OSError as exc:
        raise Hold("cannot enumerate gmpy2 bundled dynamic libraries") from exc
    expected_library_names = {name for name, _digest in GMPY2_BUNDLED_LIBRARY_HASHES}
    if library_names != expected_library_names:
        raise Hold("gmpy2 bundled dynamic-library closure drift")
    library_hashes: dict[str, str] = {}
    for name, digest in GMPY2_BUNDLED_LIBRARY_HASHES:
        snapshot_regular_file(libraries_root, libraries_root / name, digest)
        library_hashes[name] = digest

    expected_loaded_images = {extension} | {
        libraries_root / name for name, _digest in GMPY2_BUNDLED_LIBRARY_HASHES
    }
    loaded_images = _loaded_gmpy2_native_images()
    if loaded_images != expected_loaded_images:
        raise Hold("loaded gmpy2 native-image closure drift")

    snapshot_regular_file(
        REPORT_ROOT,
        REPORT_ROOT / RUNTIME_LOCK_RELATIVE,
        RUNTIME_LOCK_SHA256,
    )
    if gmpy2.version() != GMPY2_VERSION:
        raise Hold("gmpy2 version drift")
    if gmpy2.mpfr_version() != MPFR_VERSION:
        raise Hold("MPFR version drift")
    if gmpy2.mp_version() != GMP_VERSION or gmpy2.mpc_version() != MPC_VERSION:
        raise Hold("GMP/MPC version drift")
    if sys.version_info[:2] != PYTHON_ABI:
        raise Hold("Python ABI drift")
    if platform.system() != HOST_SYSTEM or platform.machine() != HOST_MACHINE:
        raise Hold("host ABI drift")
    if sysconfig.get_config_var("CC") != PYTHON_COMPILER:
        raise Hold("Python compiler identity drift")
    if sysconfig.get_config_var("PY_CFLAGS") != PYTHON_CFLAGS:
        raise Hold("Python compiler flags drift")

    _guard_runtime_identity("MPFR runtime postcheck")
    return {
        "bundled_libraries_sha256": library_hashes,
        "cpython_trust_base": cpython_trust_base,
        "extension_sha256": GMPY2_EXTENSION_SHA256,
        "gmp": GMP_VERSION,
        "gmpy2": GMPY2_VERSION,
        "loaded_native_images": sorted(path.name for path in loaded_images),
        "mpc": MPC_VERSION,
        "mpfr": MPFR_VERSION,
        "package_files_sha256": package_hashes,
        "package_init_sha256": GMPY2_PACKAGE_INIT_SHA256,
        "python_wrapper_execution": "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
        "python_cflags": PYTHON_CFLAGS,
        "python_compiler": PYTHON_COMPILER,
        "runtime_lock_sha256": RUNTIME_LOCK_SHA256,
    }


def _entry_attestation(*, require_isolated: bool) -> dict[str, object]:
    _guard_runtime_identity("entry attestation")
    context = globals().get("_T0_VERIFIED_ENTRY_CONTEXT")
    if context != PREIMPORT_ENTRY_ATTESTATION:
        raise Hold("T0 verified-entry context schema drift")
    if require_isolated and (sys.flags.isolated != 1 or sys.flags.no_site != 1):
        raise Hold("T0 verified-entry context is not isolated and canonical")
    copied = dict(PREIMPORT_ENTRY_ATTESTATION)
    copied["trust_contract"] = dict(PREIMPORT_ENTRY_ATTESTATION["trust_contract"])
    return copied


def verify_t0_package_runtime(*, require_isolated: bool = False) -> dict[str, Any]:
    """Describe the verified package and its explicit external trust contract."""

    _guard_runtime_identity("package attestation precheck")
    implementation = Path(__file__)
    if not implementation.is_absolute():
        raise Hold("T0 implementation path is not absolute")
    implementation = Path(os.path.abspath(implementation))
    expected = REPORT_ROOT / "code" / IMPLEMENTATION_NAME
    if implementation != expected or implementation.name != IMPLEMENTATION_NAME:
        raise Hold("T0 implementation origin is not the unique frozen v5 path")
    implementation_sha256 = snapshot_regular_file_digest(
        REPORT_ROOT,
        implementation,
    )
    result = {
        "entry": _entry_attestation(require_isolated=require_isolated),
        "implementation_filename": IMPLEMENTATION_NAME,
        "implementation_sha256": implementation_sha256,
        "runtime": verify_mpfr_runtime(),
        "trust_contract": _expected_trust_contract(),
    }
    _guard_runtime_identity("package attestation postcheck")
    return result


# Fail closed before source execution returns. Public byte entry points repeat
# the guard and path checks under the declared no-hostile-writer contract.
STARTUP_ATTESTATION: Final = verify_t0_package_runtime()


def _mpfr_as_fraction(value: Any) -> Fraction:
    if gmpy2 is None or not gmpy2.is_finite(value):
        raise Hold("MPFR produced a nonfinite endpoint")
    numerator, denominator = value.as_integer_ratio()
    return Fraction(int(numerator), int(denominator))


def _mpfr_unary_interval(
    argument: Fraction,
    operation: str,
    precision: int,
) -> tuple[Fraction, Fraction]:
    """Return a directed MPFR enclosure for one monotone unary function."""

    rational = gmpy2.mpq(argument.numerator, argument.denominator)
    context_options = {
        "allow_complex": False,
        "allow_release_gil": False,
        "emax": MPFR_EMAX,
        "emin": MPFR_EMIN,
        "precision": precision,
        "rational_division": False,
        "subnormalize": False,
        "trap_divzero": False,
        "trap_erange": False,
        "trap_inexact": False,
        "trap_invalid": False,
        "trap_overflow": False,
        "trap_underflow": False,
    }
    downward = gmpy2.context(round=gmpy2.RoundDown, **context_options)
    upward = gmpy2.context(round=gmpy2.RoundUp, **context_options)
    function = getattr(gmpy2, operation)
    with gmpy2.context(downward):
        lower = function(gmpy2.mpfr(rational))
    with gmpy2.context(upward):
        upper = function(gmpy2.mpfr(rational))
    lower_exact = _mpfr_as_fraction(lower)
    upper_exact = _mpfr_as_fraction(upper)
    if lower_exact > upper_exact:
        raise Hold("MPFR returned a reversed directed interval")
    return lower_exact, upper_exact


def _validate_sqrt_candidate(argument: Fraction, candidate: float) -> float:
    candidate = canonical_float(candidate)
    candidate_exact = exact(candidate)
    if candidate_exact * candidate_exact == argument:
        return candidate
    if candidate <= 0.0:
        raise Hold("invalid nonpositive MPFR sqrt candidate")
    lower = next_down(candidate)
    upper = next_up(candidate)
    lower_midpoint = (exact(lower) + candidate_exact) / 2
    upper_midpoint = (candidate_exact + exact(upper)) / 2
    lower_boundary = lower_midpoint * lower_midpoint
    upper_boundary = upper_midpoint * upper_midpoint
    if not lower_boundary <= argument <= upper_boundary:
        raise Hold("MPFR sqrt candidate is outside its exact RN cell")
    if argument == lower_boundary:
        return lower if _float_bits(lower) & 1 == 0 else candidate
    if argument == upper_boundary:
        return candidate if _float_bits(candidate) & 1 == 0 else upper
    return candidate


def sqrt_rn(value: float) -> float:
    """Correctly rounded sqrt via MPFR intervals and exact tie checks."""

    verify_mpfr_runtime()
    value = canonical_float(value)
    if value < 0.0:
        raise Hold("sqrt domain error")
    if value == 0.0:
        return 0.0
    argument = exact(value)
    for precision in (128, 256, 512, 1024, 2048, 4096):
        lower_exact, upper_exact = _mpfr_unary_interval(argument, "sqrt", precision)
        if lower_exact * lower_exact > argument or upper_exact * upper_exact < argument:
            raise Hold("MPFR directed sqrt enclosure failure")
        lower_rn = rn_fraction(lower_exact)
        upper_rn = rn_fraction(upper_exact)
        if lower_rn == upper_rn:
            return _validate_sqrt_candidate(argument, lower_rn)
        if lower_rn >= 0.0 and next_up(lower_rn) == upper_rn:
            midpoint = (exact(lower_rn) + exact(upper_rn)) / 2
            comparison = argument - midpoint * midpoint
            if comparison < 0:
                candidate = lower_rn
            elif comparison > 0:
                candidate = upper_rn
            else:
                candidate = lower_rn if _float_bits(lower_rn) & 1 == 0 else upper_rn
            return _validate_sqrt_candidate(argument, candidate)
    raise Hold("MPFR precision escalation did not identify a unique sqrt endpoint")


def sqrt_down64(value: float) -> float:
    """Directed lower binary64 endpoint of the exact square root."""

    value = canonical_float(value)
    if value < 0.0:
        raise Hold("sqrt domain error")
    candidate = sqrt_rn(value)
    return candidate if exact(candidate) ** 2 <= exact(value) else next_down(candidate)


def sqrt_up64(value: float) -> float:
    """Directed upper binary64 endpoint of the exact square root."""

    value = canonical_float(value)
    if value < 0.0:
        raise Hold("sqrt domain error")
    candidate = sqrt_rn(value)
    return candidate if exact(candidate) ** 2 >= exact(value) else next_up(candidate)


def _transcendental_endpoint(value: float, operation: str, mode: str) -> float:
    verify_mpfr_runtime()
    value = canonical_float(value)
    if mode not in ("rn", "down", "up"):
        raise Hold("unsupported endpoint mode")
    if operation == "log":
        if value <= 0.0:
            raise Hold("log domain error")
        if value == 1.0:
            return 0.0
    elif operation == "exp":
        if value == 0.0:
            return 1.0
        if value <= EXP_TINY_CUTOFF:
            # exp(-1000) < 2^-1075: ln(2) < 0.7 follows from the positive
            # Taylor lower sum for exp(0.7), which already exceeds 2, and
            # 1075*0.7 < 1000.  Hence every accepted value in this branch is
            # strictly below the binary64 zero/minsub midpoint.  Positivity
            # then fixes all three directed endpoints without asking MPFR to
            # represent an exponent below its configured range.
            return MIN_SUBNORMAL if mode == "up" else 0.0
    else:  # pragma: no cover - internal programming guard
        raise Hold("unsupported MPFR unary operation")
    argument = exact(value)
    for precision in (128, 256, 512, 1024, 2048, 4096, 8192):
        lower, upper = _mpfr_unary_interval(argument, operation, precision)
        if mode == "rn":
            lower_endpoint = rn_fraction(lower)
            upper_endpoint = rn_fraction(upper)
        elif mode == "down":
            lower_endpoint = down64(lower)
            upper_endpoint = down64(upper)
        elif mode == "up":
            lower_endpoint = up64(lower)
            upper_endpoint = up64(upper)
        if lower_endpoint == upper_endpoint:
            return lower_endpoint
    # V5's algebraic/transcendental separation proves that a non-special
    # binary64 boundary or midpoint cannot be exact here.  Non-separation is
    # therefore an implementation/runtime failure, never a tolerance choice.
    raise Hold(f"MPFR precision escalation did not identify unique {operation}/{mode}")


def log_rn(value: float) -> float:
    """Correctly rounded natural logarithm using the pinned MPFR interval."""

    return _transcendental_endpoint(value, "log", "rn")


def log_down64(value: float) -> float:
    """Directed lower binary64 endpoint of the exact natural logarithm."""

    return _transcendental_endpoint(value, "log", "down")


def log_up64(value: float) -> float:
    """Directed upper binary64 endpoint of the exact natural logarithm."""

    return _transcendental_endpoint(value, "log", "up")


def exp_rn(value: float) -> float:
    """Correctly rounded exponential using the pinned MPFR interval."""

    return _transcendental_endpoint(value, "exp", "rn")


def exp_down64(value: float) -> float:
    """Directed lower binary64 endpoint of the exact exponential."""

    return _transcendental_endpoint(value, "exp", "down")


def exp_up64(value: float) -> float:
    """Directed upper binary64 endpoint of the exact exponential."""

    return _transcendental_endpoint(value, "exp", "up")


def dot2_rn(left: Theta, right: Theta) -> float:
    p0 = rn_mul(left[0], right[0])
    p1 = rn_mul(left[1], right[1])
    return rn_add(p0, p1)


def norm2_rn(vector: Theta) -> float:
    p0 = rn_mul(vector[0], vector[0])
    p1 = rn_mul(vector[1], vector[1])
    square_sum = rn_add(p0, p1)
    return sqrt_rn(square_sum)


def _checked_interval(value: Sequence[float], role: str) -> tuple[Fraction, Fraction]:
    if len(value) != 2:
        raise Hold(f"{role} must have two endpoints")
    lower = exact(value[0])
    upper = exact(value[1])
    if lower > upper:
        raise Hold(f"{role} has reversed endpoints")
    return lower, upper


def dplus(left: Interval, right: Interval) -> float:
    left_lower, left_upper = _checked_interval(left, "left interval")
    right_lower, right_upper = _checked_interval(right, "right interval")
    return up64(
        max(
            abs(left_lower - right_upper),
            abs(left_upper - right_lower),
        )
    )


def dminus(left: Interval, right: Interval) -> float:
    left_lower, left_upper = _checked_interval(left, "left interval")
    right_lower, right_upper = _checked_interval(right, "right interval")
    return down64(
        max(
            Fraction(0),
            left_lower - right_upper,
            right_lower - left_upper,
        )
    )


def odd_gate_scalar(coarse: Interval, middle: Interval, fine: Interval) -> bool:
    """The complete v5 production Boolean for one scalar interval."""

    verify_normative_snapshots()
    verify_t0_package_runtime()
    coarse_plus = dplus(middle, coarse)
    fine_plus = dplus(fine, middle)
    coarse_minus = dminus(middle, coarse)
    return max(coarse_plus, fine_plus) <= ODD_FLOOR or fine_plus < coarse_minus


def odd_gate_vector(
    coarse: VectorInterval,
    middle: VectorInterval,
    fine: VectorInterval,
) -> bool:
    """Coordinatewise outward discrepancies followed by the fixed L-inf gate."""

    verify_normative_snapshots()
    if not coarse or not (len(coarse) == len(middle) == len(fine)):
        raise Hold("vector odd-gate shapes differ or are empty")
    coarse_plus = max(dplus(m, c) for m, c in zip(middle, coarse, strict=True))
    fine_plus = max(dplus(f, m) for f, m in zip(fine, middle, strict=True))
    coarse_minus = max(dminus(m, c) for m, c in zip(middle, coarse, strict=True))
    return max(coarse_plus, fine_plus) <= ODD_FLOOR or fine_plus < coarse_minus


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Hold(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_float(_value: str) -> Any:
    raise Hold("JSON number floats are forbidden; use canonical float.hex strings")


def _reject_json_constant(_value: str) -> Any:
    raise Hold("nonfinite JSON constants are forbidden")


def _validate_json_tree(value: Any) -> None:
    if value is None or isinstance(value, (str, bool)) or type(value) is int:
        return
    if isinstance(value, list):
        for child in value:
            _validate_json_tree(child)
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise Hold("JSON object keys must be strings")
        for child in value.values():
            _validate_json_tree(child)
        return
    raise Hold("unsupported value in canonical JSON tree")


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize the selector's unique no-float canonical JSON dialect."""

    _validate_json_tree(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def parse_canonical_json_bytes(payload: bytes) -> Any:
    """Decode duplicate-free canonical JSON and reject alternate byte spellings."""

    if not isinstance(payload, bytes) or not payload or len(payload) > MAX_SNAPSHOT_BYTES:
        raise Hold("canonical JSON payload is empty, non-bytes, or oversized")
    try:
        decoded = payload.decode("utf-8")
        value = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Hold("invalid UTF-8 canonical JSON") from exc
    if canonical_json_bytes(value) != payload:
        raise Hold("JSON bytes are not in the unique canonical form")
    return value


def _parse_theta(value: Any, role: str) -> tuple[tuple[str, str], Theta]:
    items = _require_list(value, role)
    if len(items) != 2:
        raise Hold(f"{role} must have exactly two coordinates")
    parsed = tuple(parse_float_hex(item, f"{role}[{index}]") for index, item in enumerate(items))
    return (items[0], items[1]), (parsed[0], parsed[1])


def _parse_weights(value: Any, role: str) -> tuple[str, str, str, str]:
    items = _require_list(value, role)
    if len(items) != 4:
        raise Hold(f"{role} must have exactly four weights")
    for index, item in enumerate(items):
        parse_float_hex(item, f"{role}[{index}]")
    return items[0], items[1], items[2], items[3]


def _validate_generation_record(value: Any, role: str) -> dict[str, Any]:
    record = _require_mapping(value, role)
    _require_exact_keys(record, {"index", "theta", "weights"}, role)
    theta_hex, _ = _parse_theta(record["theta"], f"{role}.theta")
    weights_hex = _parse_weights(record["weights"], f"{role}.weights")
    return {
        "index": _require_uint64(record["index"], f"{role}.index"),
        "theta": theta_hex,
        "weights": weights_hex,
    }


def _validate_evaluated_record(value: Any, role: str) -> dict[str, Any]:
    record = _require_mapping(value, role)
    expected = {
        "control_gates_passed",
        "index",
        "retained_maximum_count",
        "saved_topology",
        "status",
        "theta",
        "weights",
    }
    _require_exact_keys(record, expected, role)
    if record["status"] != "EVALUATED" or record["control_gates_passed"] is not True:
        raise Hold(f"{role} is not an evaluated all-gates-pass row")
    topology = record["saved_topology"]
    if not isinstance(topology, str) or not topology or len(topology) > 128:
        raise Hold(f"{role}.saved_topology is not a canonical saved label")
    theta_hex, _ = _parse_theta(record["theta"], f"{role}.theta")
    weights_hex = _parse_weights(record["weights"], f"{role}.weights")
    return {
        "index": _require_uint64(record["index"], f"{role}.index"),
        "theta": theta_hex,
        "weights": weights_hex,
        "topology": topology,
        "count": _require_uint64(
            record["retained_maximum_count"],
            f"{role}.retained_maximum_count",
        ),
    }


def _unique_collection(
    records: list[Any], role: str, *, evaluated: bool
) -> dict[int, dict[str, Any]]:
    if not records:
        raise Hold(f"{role} collection is empty")
    result: dict[int, dict[str, Any]] = {}
    for position, raw in enumerate(records):
        item_role = f"{role}[{position}]"
        record = (
            _validate_evaluated_record(raw, item_role)
            if evaluated
            else _validate_generation_record(raw, item_role)
        )
        if record["index"] in result:
            raise Hold(f"duplicate index within {role}")
        result[record["index"]] = record
    return result


def _join_candidates(payload: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    generated = _unique_collection(
        _require_list(payload["candidate_generation"], "candidate_generation"),
        "candidate_generation",
        evaluated=False,
    )
    mesh65 = _unique_collection(
        _require_list(payload["screened_mesh_65"], "screened_mesh_65"),
        "screened_mesh_65",
        evaluated=True,
    )
    mesh97 = _unique_collection(
        _require_list(payload["advanced_mesh_97"], "advanced_mesh_97"),
        "advanced_mesh_97",
        evaluated=True,
    )
    if not (set(generated) == set(mesh65) == set(mesh97)):
        raise Hold("candidate cross-collection index join is not one-to-one")

    physical_controls: dict[bytes, int] = {}
    joined: dict[int, dict[str, Any]] = {}
    for index in sorted(generated):
        source = generated[index]
        coarse = mesh65[index]
        advanced = mesh97[index]
        identity = (source["theta"], source["weights"])
        for row in (coarse, advanced):
            if (row["theta"], row["weights"]) != identity:
                raise Hold("theta/weights bytes differ across the source join")
        if coarse["topology"] != advanced["topology"]:
            raise Hold("mesh-65 and mesh-97 saved topology bytes differ")
        if coarse["count"] != advanced["count"]:
            raise Hold("mesh-65 and mesh-97 retained counts differ")
        control_bytes = canonical_json_bytes(
            {"theta": list(source["theta"]), "weights": list(source["weights"])}
        )
        if control_bytes in physical_controls:
            raise Hold("two distinct indices have identical physical-control bytes")
        physical_controls[control_bytes] = index
        joined[index] = {
            **source,
            "count": advanced["count"],
            "topology": advanced["topology"],
            "control_sha256": hashlib.sha256(control_bytes).hexdigest(),
        }
    return joined


def _parse_point_node(value: Any, role: str) -> tuple[int, Point]:
    node = _require_mapping(value, role)
    _require_exact_keys(node, {"acceptance_index", "t", "theta"}, role)
    acceptance_index = _require_uint64(node["acceptance_index"], f"{role}.acceptance_index")
    time = parse_float_hex(node["t"], f"{role}.t")
    _, theta = _parse_theta(node["theta"], f"{role}.theta")
    return acceptance_index, (time, theta[0], theta[1])


def _comparison_frame(branch: Mapping[str, Any], role: str) -> Frame:
    records = _require_list(branch["comparison_records"], f"{role}.comparison_records")
    retained: list[tuple[tuple[float, float, int], int]] = []
    seen_acceptance: set[int] = set()
    seen_ranks: set[tuple[float, float, int]] = set()
    for position, raw in enumerate(records):
        item_role = f"{role}.comparison_records[{position}]"
        record = _require_mapping(raw, item_role)
        expected = {
            "acceptance_index",
            "normalized_fold_residual",
            "realized_signed_offset",
            "target_offset",
        }
        _require_exact_keys(record, expected, item_role)
        target_hex = record["target_offset"]
        target = parse_float_hex(target_hex, f"{item_role}.target_offset")
        realized = parse_float_hex(
            record["realized_signed_offset"],
            f"{item_role}.realized_signed_offset",
        )
        residual = parse_float_hex(
            record["normalized_fold_residual"],
            f"{item_role}.normalized_fold_residual",
        )
        acceptance = _require_uint64(
            record["acceptance_index"],
            f"{item_role}.acceptance_index",
        )
        if target_hex != TARGET_HEX or target != TARGET:
            continue
        rank = (abs(rn_sub(realized, TARGET)), abs(residual), acceptance)
        if acceptance in seen_acceptance:
            raise Hold("repeated retained comparison acceptance index")
        if rank in seen_ranks:
            raise Hold("duplicate retained comparison full rank")
        seen_acceptance.add(acceptance)
        seen_ranks.add(rank)
        retained.append((rank, acceptance))
    if not retained:
        raise Hold("no saved comparison record has TARGET bytes")
    retained.sort(key=lambda item: item[0])
    comparison_rank, acceptance_index = retained[0]

    raw_nodes = _require_list(branch["nodes"], f"{role}.nodes")
    if len(raw_nodes) < 3:
        raise Hold("saved node array has fewer than three nodes")
    nodes = [_parse_point_node(raw, f"{role}.nodes[{i}]") for i, raw in enumerate(raw_nodes)]
    node_ids = [item[0] for item in nodes]
    if len(set(node_ids)) != len(node_ids):
        raise Hold("duplicate saved node acceptance index")
    matches = [position for position, item in enumerate(nodes) if item[0] == acceptance_index]
    if len(matches) != 1 or matches[0] in (0, len(nodes) - 1):
        raise Hold("comparison node is missing, duplicated, or lacks both neighbors")
    position = matches[0]
    previous = nodes[position - 1][1]
    base = nodes[position][1]
    following = nodes[position + 1][1]

    sigma = branch["sigma"]
    if type(sigma) is not int or sigma not in (-1, 1):
        raise Hold("branch sigma must be the exact integer -1 or +1")
    c0 = rn_sub(following[1], previous[1])
    c1 = rn_sub(following[2], previous[2])
    dt = rn_sub(following[0], previous[0])
    omega = rn_mul(float(sigma), dt)
    if omega == 0.0:
        raise Hold("omega is zero")
    if omega < 0.0:
        c0 = canonical_float(-c0)
        c1 = canonical_float(-c1)
    c_norm = norm2_rn((c0, c1))
    if c_norm == 0.0:
        raise Hold("central secant norm is zero")
    u0 = rn_div(c0, c_norm)
    u1 = rn_div(c1, c_norm)
    n0 = canonical_float(-u1)
    n1 = u0

    vp0 = rn_sub(base[1], previous[1])
    vp1 = rn_sub(base[2], previous[2])
    vn0 = rn_sub(following[1], base[1])
    vn1 = rn_sub(following[2], base[2])
    ell_previous = norm2_rn((vp0, vp1))
    ell_next = norm2_rn((vn0, vn1))
    ell = min(ell_previous, ell_next)
    if ell <= 0.0:
        raise Hold("local chart scale ell is nonpositive")
    return Frame(
        tangent=(u0, u1),
        normal=(n0, n1),
        ell=ell,
        previous=previous,
        base=base,
        following=following,
        comparison_rank=comparison_rank,
        acceptance_index=acceptance_index,
    )


def _measure_candidate(candidate: Mapping[str, Any], frame: Frame) -> CandidateMeasure | None:
    theta = tuple(parse_float_hex(value, "candidate.theta") for value in candidate["theta"])
    d0 = rn_sub(theta[0], frame.base[1])
    d1 = rn_sub(theta[1], frame.base[2])
    s_value = dot2_rn(frame.normal, (d0, d1))
    q_value = dot2_rn(frame.tangent, (d0, d1))
    radius = norm2_rn((d0, d1))
    two_ell = rn_mul(float.fromhex("0x1.0000000000000p+1"), frame.ell)
    half_ell = rn_div(frame.ell, float.fromhex("0x1.0000000000000p+1"))
    sixteenth_ell = rn_div(frame.ell, float.fromhex("0x1.0000000000000p+4"))
    if not (
        radius > 0.0
        and radius <= two_ell
        and abs(q_value) <= half_ell
        and abs(s_value) >= sixteenth_ell
    ):
        return None
    return CandidateMeasure(
        index=candidate["index"],
        theta_hex=candidate["theta"],
        weights_hex=candidate["weights"],
        count=candidate["count"],
        topology=candidate["topology"],
        s=s_value,
        q=q_value,
        radius=radius,
    )


def _pair_rank(
    left: CandidateMeasure,
    right: CandidateMeasure,
    ell: float,
) -> tuple[tuple[float, float, float, int, int], CandidateMeasure, CandidateMeasure] | None:
    if left.index == right.index:
        raise Hold("candidate pair repeats an index")
    if left.s < 0.0 < right.s:
        minus, plus = left, right
    elif right.s < 0.0 < left.s:
        minus, plus = right, left
    else:
        return None
    if abs(minus.count - plus.count) != 1:
        return None
    k1 = rn_div(max(minus.radius, plus.radius), ell)
    k2 = rn_div(abs(rn_add(minus.s, plus.s)), ell)
    k3n = rn_add(abs(minus.q), abs(plus.q))
    k3 = rn_div(k3n, ell)
    k4 = min(minus.index, plus.index)
    k5 = max(minus.index, plus.index)
    return (k1, k2, k3, k4, k5), minus, plus


def _selected_branch(
    branch: Mapping[str, Any],
    candidates: dict[int, dict[str, Any]],
    role: str,
) -> dict[str, Any]:
    frame = _comparison_frame(branch, role)
    branch_id = branch["branch_id"]
    measured = [
        item
        for candidate in candidates.values()
        if (item := _measure_candidate(candidate, frame)) is not None
    ]
    pair_candidates = [
        pair
        for left, right in combinations(measured, 2)
        if (pair := _pair_rank(left, right, frame.ell)) is not None
    ]
    if not pair_candidates:
        raise Hold(f"{role} has no eligible opposite-side count-changing pair")
    ranks = [item[0] for item in pair_candidates]
    if len(set(ranks)) != len(ranks):
        raise Hold(f"{role} has a duplicate full pair rank")
    pair_candidates.sort(key=lambda item: item[0])
    rank, minus, plus = pair_candidates[0]

    def selected(side: str, candidate: CandidateMeasure) -> dict[str, Any]:
        control_bytes = canonical_json_bytes(
            {"theta": list(candidate.theta_hex), "weights": list(candidate.weights_hex)}
        )
        return {
            "control_sha256": hashlib.sha256(control_bytes).hexdigest(),
            "index": candidate.index,
            "retained_maximum_count": candidate.count,
            "s": float_hex(candidate.s),
            "side": side,
            "theta": list(candidate.theta_hex),
            "topology": candidate.topology,
            "weights": list(candidate.weights_hex),
        }

    return {
        "branch_id": branch_id,
        "comparison_acceptance_index": frame.acceptance_index,
        "comparison_rank": [
            float_hex(frame.comparison_rank[0]),
            float_hex(frame.comparison_rank[1]),
            frame.comparison_rank[2],
        ],
        "count_pair": sorted((minus.count, plus.count)),
        "frame": {
            "ell": float_hex(frame.ell),
            "normal": [float_hex(value) for value in frame.normal],
            "tangent": [float_hex(value) for value in frame.tangent],
        },
        "pair_rank": [float_hex(rank[0]), float_hex(rank[1]), float_hex(rank[2]), rank[3], rank[4]],
        "selected": [selected("minus", minus), selected("plus", plus)],
    }


def _select_saved_controls(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and apply the literal v5 byte-unique two-branch selector."""

    payload = _require_mapping(payload, "selector input")
    expected = {
        "advanced_mesh_97",
        "authorization",
        "candidate_generation",
        "saved_branches",
        "schema",
        "screened_mesh_65",
    }
    _require_exact_keys(payload, expected, "selector input")
    if payload["schema"] != INPUT_SCHEMA:
        raise Hold("selector input schema/version mismatch")
    if payload["authorization"] != AUTHORIZATION_NONE:
        raise Hold("selector input authorization is not the frozen NONE literal")
    raw_branches = _require_list(payload["saved_branches"], "saved_branches")
    if len(raw_branches) != 2:
        raise Hold("exactly two saved branches are required")
    branches: list[Mapping[str, Any]] = []
    branch_ids: set[str] = set()
    for position, raw in enumerate(raw_branches):
        role = f"saved_branches[{position}]"
        branch = _require_mapping(raw, role)
        _require_exact_keys(
            branch,
            {"branch_id", "comparison_records", "nodes", "sigma"},
            role,
        )
        branch_id = _require_branch_id(branch["branch_id"], f"{role}.branch_id")
        if branch_id in branch_ids:
            raise Hold("duplicate saved branch ID")
        branch_ids.add(branch_id)
        branches.append(branch)

    candidates = _join_candidates(payload)
    selected = [
        _selected_branch(branch, candidates, f"saved_branches[{position}]")
        for position, branch in enumerate(branches)
    ]
    selected_indices = [item["index"] for branch in selected for item in branch["selected"]]
    if len(set(selected_indices)) != len(selected_indices):
        raise Hold("cross-branch selected-candidate collision")
    count_pairs = {tuple(branch["count_pair"]) for branch in selected}
    if count_pairs != {(1, 2), (2, 3)}:
        raise Hold("the two unordered count pairs are not exactly {(1,2),(2,3)}")
    return {
        "authorization": AUTHORIZATION_NONE,
        "branches": selected,
        "normative_snapshot": {
            "round_73_sha256": ROUND73_SHA256,
            "stage_b_v4_sha256": DESIGN_V4_SHA256,
            "stage_b_v5_sha256": DESIGN_V5_SHA256,
        },
        "schema": OUTPUT_SCHEMA,
    }


def select_saved_controls_bytes(payload: bytes) -> bytes:
    """Verify frozen bytes and return deterministic canonical selector JSON."""

    _guard_runtime_identity("select_saved_controls_bytes entry")
    verify_normative_snapshots()
    package_runtime = verify_t0_package_runtime()
    decoded = parse_canonical_json_bytes(payload)
    result = _select_saved_controls(decoded)
    result["package_runtime"] = package_runtime
    _guard_runtime_identity("select_saved_controls_bytes before output bytes")
    output = canonical_json_bytes(result)
    _guard_runtime_identity("select_saved_controls_bytes after output bytes")
    return output


def _exact_metric(left: Point, right: Point) -> Fraction:
    return max(
        abs(exact(left[0]) - exact(right[0])) / exact(TIME_SCALE),
        abs(exact(left[1]) - exact(right[1])),
        abs(exact(left[2]) - exact(right[2])),
    )


def _strictly_inside_role_ball(seed: Point, radius: float) -> bool:
    time_delta_hi = up64(exact(TIME_SCALE) * exact(radius))
    time_lower = down64(exact(seed[0]) - exact(time_delta_hi))
    time_upper = up64(exact(seed[0]) + exact(time_delta_hi))
    theta0_lower = down64(exact(seed[1]) - exact(radius))
    theta0_upper = up64(exact(seed[1]) + exact(radius))
    theta1_lower = down64(exact(seed[2]) - exact(radius))
    theta1_upper = up64(exact(seed[2]) + exact(radius))
    return (
        time_lower > 9.0
        and time_upper < 18.0
        and theta0_lower > -THETA_BOUND
        and theta0_upper < THETA_BOUND
        and theta1_lower > -THETA_BOUND
        and theta1_upper < THETA_BOUND
    )


def _compute_role_radii(seeds: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Compute and outward-postcheck the seven v5 saved-field role radii."""

    if not isinstance(seeds, list | tuple) or len(seeds) != 7:
        raise Hold("the role-radius schema requires exactly seven seeds")
    parsed: list[tuple[int, Point]] = []
    for position, raw in enumerate(seeds):
        role = f"role_seeds[{position}]"
        seed = _require_mapping(raw, role)
        _require_exact_keys(seed, {"role_id", "t", "theta"}, role)
        role_id = _require_uint64(seed["role_id"], f"{role}.role_id")
        time = parse_float_hex(seed["t"], f"{role}.t")
        _, theta = _parse_theta(seed["theta"], f"{role}.theta")
        parsed.append((role_id, (time, theta[0], theta[1])))
    role_ids = [item[0] for item in parsed]
    if role_ids != sorted(role_ids) or len(set(role_ids)) != 7:
        raise Hold("role seeds are not in unique ascending role-ID order")

    details: list[dict[str, Any]] = []
    radii: list[float] = []
    for index, (role_id, seed) in enumerate(parsed):
        boundary_components = (
            down64((exact(seed[0]) - exact(9.0)) / exact(TIME_SCALE)),
            down64((exact(18.0) - exact(seed[0])) / exact(TIME_SCALE)),
            down64(exact(THETA_BOUND) - abs(exact(seed[1]))),
            down64(exact(THETA_BOUND) - abs(exact(seed[2]))),
        )
        boundary_lower = min(boundary_components)
        separation_lower = min(
            max(
                down64(abs(exact(seed[0]) - exact(other[1][0])) / exact(TIME_SCALE)),
                down64(abs(exact(seed[1]) - exact(other[1][1]))),
                down64(abs(exact(seed[2]) - exact(other[1][2]))),
            )
            for other_index, other in enumerate(parsed)
            if other_index != index
        )
        radius = down64(
            min(
                exact(RHO_CAP),
                exact(boundary_lower) / 4,
                exact(separation_lower) / 4,
            )
        )
        if min(boundary_lower, separation_lower, radius) <= 0.0:
            raise Hold("HOLD-T1: a saved role radius input is nonpositive")
        radii.append(radius)
        details.append(
            {
                "b_lower": float_hex(boundary_lower),
                "rho": float_hex(radius),
                "role_id": role_id,
                "s_lower": float_hex(separation_lower),
            }
        )

    for (_, seed), radius in zip(parsed, radii, strict=True):
        if not _strictly_inside_role_ball(seed, radius):
            raise Hold("HOLD-T1: a closed role ball is not strictly inside the global box")
    for left_index, (_, left) in enumerate(parsed):
        for right_index in range(left_index + 1, len(parsed)):
            radius_upper = up64(exact(radii[left_index]) + exact(radii[right_index]))
            distance_lower = down64(_exact_metric(left, parsed[right_index][1]))
            if not radius_upper < distance_lower:
                raise Hold("HOLD-T1: saved role balls are not outward-certified disjoint")
    return {
        "authorization": AUTHORIZATION_NONE,
        "roles": details,
        "schema": ROLE_RADIUS_SCHEMA,
    }


def compute_role_radii_bytes(payload: bytes) -> bytes:
    """Verify frozen bytes and return canonical seven-role radius JSON."""

    _guard_runtime_identity("compute_role_radii_bytes entry")
    verify_normative_snapshots()
    package_runtime = verify_t0_package_runtime()
    decoded = _require_mapping(parse_canonical_json_bytes(payload), "role-radius input")
    _require_exact_keys(
        decoded,
        {"authorization", "role_seeds", "schema"},
        "role-radius input",
    )
    if decoded["schema"] != ROLE_RADIUS_INPUT_SCHEMA:
        raise Hold("role-radius input schema/version mismatch")
    if decoded["authorization"] != AUTHORIZATION_NONE:
        raise Hold("role-radius input authorization is not the frozen NONE literal")
    seeds = _require_list(decoded["role_seeds"], "role-radius input.role_seeds")
    result = _compute_role_radii(seeds)
    result["package_runtime"] = package_runtime
    _guard_runtime_identity("compute_role_radii_bytes before output bytes")
    output = canonical_json_bytes(result)
    _guard_runtime_identity("compute_role_radii_bytes after output bytes")
    return output


__all__ = [
    "AUTHORIZATION_NONE",
    "DESIGN_V4_SHA256",
    "DESIGN_V5_SHA256",
    "Hold",
    "INPUT_SCHEMA",
    "MIN_SUBNORMAL",
    "ODD_FLOOR",
    "OUTPUT_SCHEMA",
    "ROUND73_SHA256",
    "ROLE_RADIUS_INPUT_SCHEMA",
    "ROLE_RADIUS_SCHEMA",
    "canonical_json_bytes",
    "compute_role_radii_bytes",
    "dminus",
    "dot2_rn",
    "down64",
    "dplus",
    "exp_down64",
    "exp_rn",
    "exp_up64",
    "float_hex",
    "log_down64",
    "log_rn",
    "log_up64",
    "next_down",
    "next_up",
    "norm2_rn",
    "odd_gate_scalar",
    "odd_gate_vector",
    "parse_canonical_json_bytes",
    "parse_float_hex",
    "rn_add",
    "rn_div",
    "rn_fraction",
    "rn_mul",
    "rn_sub",
    "select_saved_controls_bytes",
    "snapshot_regular_file",
    "snapshot_regular_file_digest",
    "sqrt_down64",
    "sqrt_rn",
    "sqrt_up64",
    "up64",
    "verify_mpfr_runtime",
    "verify_normative_snapshots",
    "verify_t0_package_runtime",
]
