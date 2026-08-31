"""Descriptor-snapshot loader for the unique Stage-B-v5 T0 source.

Future T1 code must authenticate an external T0 record and execute this
loader from the already captured loader bytes under ``python -I -S``.  The
Python ``gmpy2`` wrapper is compiled and executed from the descriptor snapshot
verified here; it is never reopened by a pathname-backed source loader.

This is a scientific-integrity boundary, not a same-UID security sandbox.
The invoked CPython/stdlib/import machinery/OS loader and absence of a hostile
same-UID writer for the runtime tree throughout loading and public calls are
explicit external trust assumptions.  Native images remain path-loaded under
that contract.
"""

from __future__ import annotations

import _imp
import builtins
import hashlib
import importlib
import importlib.machinery
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path
from types import ModuleType

IMPLEMENTATION_NAME = "positive_b_stage_b_t1_selector_v5.py"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
AUTHORIZATION_NONE = "AUTHORIZED-SCIENTIFIC-COMMAND: NONE"
PRODUCTION_ATTESTATION_SCHEMA = "positive-b-stage-b-t0-external-attestation-v2"
SYNTHETIC_ATTESTATION_SCHEMA = "positive-b-stage-b-t0-synthetic-test-attestation-v2"
TRUST_CONTRACT_SCHEMA = "positive-b-stage-b-t0-execution-trust-contract-v1"
RUNTIME_LOCK_SHA256 = "7321fb3ce442276f4b2ff1b7c6f58c844926fba63bcca2270e10e53fb5f44ecf"
GMPY2_PACKAGE_INIT_SHA256 = "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2"
GMPY2_EXTENSION_NAME = "gmpy2.cpython-312-darwin.so"
GMPY2_EXTENSION_SHA256 = "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b"
GMPY2_PACKAGE_FILE_HASHES = (
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
GMPY2_LIBRARY_HASHES = (
    ("libgmp.10.dylib", "22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049"),
    ("libmpc.3.dylib", "d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c"),
    ("libmpfr.6.dylib", "d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed"),
)
CRITICAL_STDLIB_MODULE_NAMES = frozenset(
    {"_ctypes", "ctypes", "ctypes._endian", "platform", "sysconfig"}
)
COMMON_ATTESTED_PATHS = {
    "design_v4": "notes/positive_b_stage_b_validation_design_v4.md",
    "design_v5": "notes/positive_b_stage_b_validation_design_v5.md",
    "exploit_tests": "code/test_stageb_t0_selector_round78.py",
    "implementation": "code/positive_b_stage_b_t1_selector_v5.py",
    "loader": "code/positive_b_stage_b_t0_verified_loader.py",
    "primary_tests": "code/test_positive_b_stage_b_t1_selector_v5.py",
    "race_regression_tests": "code/test_stageb_t0_selector_round94.py",
    "protocol_v1_historical": "notes/positive_b_stage_b_t0_selector_protocol_v1.md",
    "protocol_v2_historical": "notes/positive_b_stage_b_t0_selector_protocol_v2.md",
    "protocol_v3": "notes/positive_b_stage_b_t0_selector_protocol_v3.md",
    "requirements_lock": "code/positive_b_stage_b_t0_requirements.lock",
    "round73": "audits/round_73_stageb_v5_independent_attack.md",
    "round75_historical": "audits/round_75_stageb_t0_selector_build.md",
    "round78_historical": "audits/round_78_stageb_t0_selector_independent_attack.md",
    "round81_historical": "audits/round_81_stageb_t0_selector_repair_freeze.md",
    "round93_rejection": "audits/round_93_stageb_t0_selector_independent_attack.md",
    "runtime_lock": "code/positive_b_stage_b_t0_runtime_lock_v2.json",
    "tombstone": "code/positive_b_stage_b_t0_selector.py",
    "v5_bridge": "notes/positive_b_stage_b_t1_selector_protocol_v5.md",
}


def _expected_trust_contract() -> dict[str, str]:
    """Return the exact external execution trust contract carried by records."""

    return {
        "bootstrap_trust_base": ("CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES"),
        "native_image_execution": ("PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT"),
        "protection_claim": "DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY",
        "runtime_tree_concurrency": ("NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS"),
        "schema": TRUST_CONTRACT_SCHEMA,
        "wrapper_execution": "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
    }


class FrozenLoadError(RuntimeError):
    """The exact frozen T0 implementation could not be authenticated."""


def _same_identity_sequence(left: tuple[object, ...], right: list[object]) -> bool:
    return len(left) == len(right) and all(
        expected is observed for expected, observed in zip(left, right, strict=True)
    )


class _RuntimeIdentityGuard:
    """Defense-in-depth guard for the explicitly trusted Python bootstrap."""

    __slots__ = (
        "_builtin_identities",
        "_import_identities",
        "_meta_path",
        "_module_identities",
        "_path",
        "_path_hooks",
        "compile",
        "exec",
        "wrapper_builtins",
    )

    def __init__(self) -> None:
        module_names = (
            "builtins",
            "_imp",
            "importlib",
            "importlib.machinery",
            "importlib.util",
            "_frozen_importlib",
            "_frozen_importlib_external",
        )
        modules = {name: sys.modules.get(name) for name in module_names}
        if any(module is None for module in modules.values()):
            raise FrozenLoadError("critical import machinery is unavailable at guard capture")
        self._module_identities = modules
        self._builtin_identities = {
            "__build_class__": builtins.__build_class__,
            "__import__": builtins.__import__,
            "compile": builtins.compile,
            "exec": builtins.exec,
        }
        self._import_identities = {
            "_imp.create_dynamic": _imp.create_dynamic,
            "_imp.exec_dynamic": _imp.exec_dynamic,
            "ExtensionFileLoader": importlib.machinery.ExtensionFileLoader,
            "ModuleSpec": importlib.machinery.ModuleSpec,
            "SourceFileLoader": importlib.machinery.SourceFileLoader,
            "module_from_spec": importlib.util.module_from_spec,
            "spec_from_file_location": importlib.util.spec_from_file_location,
        }
        self._meta_path = tuple(sys.meta_path)
        self._path_hooks = tuple(sys.path_hooks)
        self._path = tuple(sys.path)
        self.compile = builtins.compile
        self.exec = builtins.exec
        self.wrapper_builtins = dict(builtins.__dict__)
        self.wrapper_builtins.update(self._builtin_identities)
        self.check("capture")

    def check(self, stage: str) -> None:
        for name, expected in self._module_identities.items():
            if sys.modules.get(name) is not expected:
                raise FrozenLoadError(
                    f"runtime identity guard HOLD at {stage}: module drift for {name}"
                )
        for name, expected in self._builtin_identities.items():
            if getattr(builtins, name, None) is not expected:
                raise FrozenLoadError(
                    f"runtime identity guard HOLD at {stage}: builtins.{name} drift"
                )
        observed_import_identities = {
            "_imp.create_dynamic": _imp.create_dynamic,
            "_imp.exec_dynamic": _imp.exec_dynamic,
            "ExtensionFileLoader": importlib.machinery.ExtensionFileLoader,
            "ModuleSpec": importlib.machinery.ModuleSpec,
            "SourceFileLoader": importlib.machinery.SourceFileLoader,
            "module_from_spec": importlib.util.module_from_spec,
            "spec_from_file_location": importlib.util.spec_from_file_location,
        }
        for name, expected in self._import_identities.items():
            if observed_import_identities[name] is not expected:
                raise FrozenLoadError(
                    f"runtime identity guard HOLD at {stage}: import machinery drift for {name}"
                )
        if not _same_identity_sequence(self._meta_path, sys.meta_path):
            raise FrozenLoadError(
                f"runtime identity guard HOLD at {stage}: sys.meta_path identity drift"
            )
        if not _same_identity_sequence(self._path_hooks, sys.path_hooks):
            raise FrozenLoadError(
                f"runtime identity guard HOLD at {stage}: sys.path_hooks identity drift"
            )
        if tuple(sys.path) != self._path:
            raise FrozenLoadError(f"runtime identity guard HOLD at {stage}: sys.path drift")


class _VerifiedRuntimeSnapshot:
    """Descriptor-authenticated Python bytes plus path-loaded native locations."""

    __slots__ = (
        "extension",
        "libraries_root",
        "package_init",
        "package_root",
        "wrapper_bytes",
    )

    def __init__(
        self,
        *,
        extension: Path,
        libraries_root: Path,
        package_init: Path,
        package_root: Path,
        wrapper_bytes: bytes,
    ) -> None:
        self.extension = extension
        self.libraries_root = libraries_root
        self.package_init = package_init
        self.package_root = package_root
        self.wrapper_bytes = wrapper_bytes


def _check_absolute_components(path: Path, role: str) -> Path:
    lexical = Path(os.path.abspath(path))
    if path != lexical or not path.is_absolute():
        raise FrozenLoadError(f"{role} path is not canonical absolute")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = os.lstat(current)
        except OSError as exc:
            raise FrozenLoadError(f"{role} path is unavailable") from exc
        if stat.S_ISLNK(info.st_mode):
            raise FrozenLoadError(f"{role} path contains a symbolic link")
    return lexical


def _read_regular_file(path: Path, role: str) -> bytes:
    path = _check_absolute_components(path, role)
    if not hasattr(os, "O_NOFOLLOW"):
        raise FrozenLoadError("O_NOFOLLOW is unavailable")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as exc:
        raise FrozenLoadError(f"cannot open {role} descriptor") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_SOURCE_BYTES:
            raise FrozenLoadError(f"{role} is not a bounded regular file")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                raise FrozenLoadError(f"short {role} read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise FrozenLoadError(f"{role} grew during read")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    def identity(info: os.stat_result) -> tuple[int, int, int, int, int, int]:
        return (
            info.st_dev,
            info.st_ino,
            info.st_mode,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        )

    if identity(before) != identity(after):
        raise FrozenLoadError(f"{role} changed during read")
    lexical_after = os.lstat(path)
    if (lexical_after.st_dev, lexical_after.st_ino) != (before.st_dev, before.st_ino):
        raise FrozenLoadError(f"{role} path was replaced during read")
    return b"".join(chunks)


def _read_exact_source(path: Path) -> bytes:
    root = Path(os.path.abspath(Path(__file__).parent))
    if path != root / IMPLEMENTATION_NAME:
        raise FrozenLoadError("implementation is not the unique sibling v5 path")
    return _read_regular_file(path, "frozen implementation")


def _is_canonical_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _consume_external_attestation(
    path: Path,
    expected_sha256: str,
) -> tuple[str, Path, dict[str, object]]:
    """Authenticate the external record and every package byte it closes."""

    if not _is_canonical_sha256(expected_sha256):
        raise FrozenLoadError("external attestation SHA-256 is not canonical")
    payload = _read_regular_file(path, "external T0 attestation")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise FrozenLoadError("external T0 attestation SHA-256 mismatch")
    try:
        record = json.loads(payload.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FrozenLoadError("external T0 attestation is not canonical ASCII JSON") from exc
    if (
        not isinstance(record, dict)
        or set(record)
        != {
            "authorization",
            "files",
            "runtime_site_root",
            "schema",
            "status",
            "trust_contract",
        }
        or json.dumps(record, sort_keys=True, indent=2).encode("ascii") + b"\n" != payload
    ):
        raise FrozenLoadError("external T0 attestation schema/canonical-byte drift")
    if record["authorization"] != AUTHORIZATION_NONE:
        raise FrozenLoadError("external T0 attestation authorization drift")
    expected_trust_contract = _expected_trust_contract()
    if record["trust_contract"] != expected_trust_contract:
        raise FrozenLoadError("external T0 attestation trust-contract drift")
    schema = record["schema"]
    if schema == SYNTHETIC_ATTESTATION_SCHEMA:
        if record["status"] != "NON-PROMOTABLE-SYNTHETIC-TEST":
            raise FrozenLoadError("synthetic attestation status drift")
        expected_roles = set(COMMON_ATTESTED_PATHS)
        entry_mode = "VERIFIED-ISOLATED-SYNTHETIC-TEST"
        production_eligible = False
    elif schema == PRODUCTION_ATTESTATION_SCHEMA:
        if record["status"] != "INDEPENDENT-ATTACK-PASS":
            raise FrozenLoadError("production attestation is not independently accepted")
        expected_roles = set(COMMON_ATTESTED_PATHS) | {
            "independent_attack",
            "round94_repair",
        }
        entry_mode = "VERIFIED-ISOLATED"
        production_eligible = True
    else:
        raise FrozenLoadError("external T0 attestation schema drift")

    files = record["files"]
    if not isinstance(files, dict) or set(files) != expected_roles:
        raise FrozenLoadError("external T0 attestation package-role closure drift")
    report_root = Path(os.path.abspath(Path(__file__).parent.parent))
    verified: dict[str, str] = {}
    claimed_paths: dict[str, str] = {}
    for role, raw_entry in files.items():
        if not isinstance(raw_entry, dict) or set(raw_entry) != {"path", "sha256"}:
            raise FrozenLoadError(f"external T0 attestation entry drift for {role}")
        relative_raw = raw_entry["path"]
        digest = raw_entry["sha256"]
        if not isinstance(relative_raw, str) or not _is_canonical_sha256(digest):
            raise FrozenLoadError(f"external T0 attestation value drift for {role}")
        relative = Path(relative_raw)
        if relative.is_absolute() or ".." in relative.parts or relative_raw != relative.as_posix():
            raise FrozenLoadError(f"external T0 attestation path drift for {role}")
        if relative_raw in claimed_paths:
            raise FrozenLoadError(
                f"external T0 attestation path is reused by {claimed_paths[relative_raw]} and {role}"
            )
        claimed_paths[relative_raw] = role
        if role in COMMON_ATTESTED_PATHS and relative_raw != COMMON_ATTESTED_PATHS[role]:
            raise FrozenLoadError(f"external T0 attestation role/path swap for {role}")
        if role == "round94_repair" and relative_raw != (
            "audits/round_94_stageb_t0_selector_race_repair_freeze.md"
        ):
            raise FrozenLoadError("Round-94 repair-record path drift")
        if role == "independent_attack" and (
            len(relative.parts) != 2
            or relative.parts[0] != "audits"
            or not relative.name.startswith("round_")
            or not relative.name.endswith("_stageb_t0_selector_independent_attack.md")
        ):
            raise FrozenLoadError("independent-attack path drift")
        actual = hashlib.sha256(
            _read_regular_file(report_root / relative, f"attested package role {role}")
        ).hexdigest()
        if actual != digest:
            raise FrozenLoadError(f"attested package SHA-256 mismatch for {role}")
        verified[role] = digest

    if verified["runtime_lock"] != RUNTIME_LOCK_SHA256:
        raise FrozenLoadError("runtime-lock digest drift in external attestation")
    runtime_site_root = record["runtime_site_root"]
    if not isinstance(runtime_site_root, str):
        raise FrozenLoadError("runtime-site root is not a string")
    entry_context: dict[str, object] = {
        "external_attestation_schema": schema,
        "external_attestation_sha256": expected_sha256,
        "external_attestation_status": record["status"],
        "mode": entry_mode,
        "production_eligible": production_eligible,
        "trust_contract": expected_trust_contract,
    }
    return verified["implementation"], Path(runtime_site_root), entry_context


def _verify_runtime_tree(runtime_site_root: Path) -> _VerifiedRuntimeSnapshot:
    """Capture the authentic wrapper bytes and verify the path-loaded tree."""

    runtime_site_root = _check_absolute_components(runtime_site_root, "runtime site root")
    if not runtime_site_root.is_dir():
        raise FrozenLoadError("runtime site root is not a directory")
    if any(name == "gmpy2" or name.startswith("gmpy2.") for name in sys.modules):
        raise FrozenLoadError("gmpy2 was imported before runtime-tree attestation")

    package_root = runtime_site_root / "gmpy2"
    package_init = package_root / "__init__.py"
    libraries_root = runtime_site_root / "gmpy2.libs"
    _check_absolute_components(package_root, "gmpy2 package root")
    try:
        actual_package_names = {entry.name for entry in os.scandir(package_root)}
    except OSError as exc:
        raise FrozenLoadError("cannot enumerate gmpy2 package root") from exc
    expected_package_names = {
        Path(relative).parts[0] for relative, _digest in GMPY2_PACKAGE_FILE_HASHES
    }
    if actual_package_names != expected_package_names:
        raise FrozenLoadError("gmpy2 package exact-file closure drift")
    pycache_root = package_root / "__pycache__"
    try:
        actual_pycache_names = {entry.name for entry in os.scandir(pycache_root)}
    except OSError as exc:
        raise FrozenLoadError("cannot enumerate gmpy2 package pycache") from exc
    expected_pycache_names = {
        Path(relative).name
        for relative, _digest in GMPY2_PACKAGE_FILE_HASHES
        if Path(relative).parts[0] == "__pycache__"
    }
    if actual_pycache_names != expected_pycache_names:
        raise FrozenLoadError("gmpy2 package pycache closure drift")
    wrapper_bytes: bytes | None = None
    for relative, expected_sha256 in GMPY2_PACKAGE_FILE_HASHES:
        path = package_root / relative
        payload = _read_regular_file(path, f"gmpy2/{relative}")
        if hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise FrozenLoadError(f"gmpy2/{relative} SHA-256 mismatch")
        if relative == "__init__.py":
            wrapper_bytes = payload

    _check_absolute_components(libraries_root, "gmpy2 bundled-library root")
    try:
        actual_library_names = {entry.name for entry in os.scandir(libraries_root)}
    except OSError as exc:
        raise FrozenLoadError("cannot enumerate gmpy2 bundled-library root") from exc
    expected_library_names = {name for name, _digest in GMPY2_LIBRARY_HASHES}
    if actual_library_names != expected_library_names:
        raise FrozenLoadError("gmpy2 bundled-library closure drift")
    for name, expected_sha256 in GMPY2_LIBRARY_HASHES:
        path = libraries_root / name
        if hashlib.sha256(_read_regular_file(path, name)).hexdigest() != expected_sha256:
            raise FrozenLoadError(f"{name} SHA-256 mismatch")
    if wrapper_bytes is None:
        raise FrozenLoadError("verified gmpy2 wrapper snapshot is missing")
    return _VerifiedRuntimeSnapshot(
        extension=package_root / GMPY2_EXTENSION_NAME,
        libraries_root=libraries_root,
        package_init=package_init,
        package_root=package_root,
        wrapper_bytes=wrapper_bytes,
    )


def _load_verified_gmpy2(
    snapshot: _VerifiedRuntimeSnapshot,
    guard: _RuntimeIdentityGuard,
) -> ModuleType:
    """Load native code by absolute path, then execute only captured wrapper bytes."""

    if any(name == "gmpy2" or name.startswith("gmpy2.") for name in sys.modules):
        raise FrozenLoadError("gmpy2 module name was occupied before captured-wrapper load")
    guard.check("before native extension load")

    package_loader = importlib.machinery.SourceFileLoader(
        "gmpy2",
        str(snapshot.package_init),
    )
    package_spec = importlib.machinery.ModuleSpec(
        "gmpy2",
        package_loader,
        origin=str(snapshot.package_init),
        is_package=True,
    )
    package_spec.submodule_search_locations = [str(snapshot.package_root)]
    package = ModuleType("gmpy2")
    package.__file__ = str(snapshot.package_init)
    package.__package__ = "gmpy2"
    package.__loader__ = package_loader
    package.__spec__ = package_spec
    package.__path__ = [str(snapshot.package_root)]
    package.__dict__["__builtins__"] = dict(guard.wrapper_builtins)
    sys.modules["gmpy2"] = package

    try:
        extension_loader = importlib.machinery.ExtensionFileLoader(
            "gmpy2.gmpy2",
            str(snapshot.extension),
        )
        extension_spec = importlib.util.spec_from_file_location(
            "gmpy2.gmpy2",
            str(snapshot.extension),
            loader=extension_loader,
        )
        if extension_spec is None:
            raise FrozenLoadError("cannot construct exact gmpy2 native-extension spec")
        extension_module = importlib.util.module_from_spec(extension_spec)
        sys.modules["gmpy2.gmpy2"] = extension_module
        package.gmpy2 = extension_module
        extension_loader.exec_module(extension_module)
        guard.check("after native extension load")

        wrapper_code = guard.compile(
            snapshot.wrapper_bytes,
            str(snapshot.package_init),
            "exec",
            dont_inherit=True,
        )
        guard.check("before captured gmpy2 wrapper execution")
        guard.exec(wrapper_code, package.__dict__)
        package.__dict__["__t0_wrapper_execution__"] = "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
        package.__dict__["__t0_wrapper_sha256__"] = GMPY2_PACKAGE_INIT_SHA256
        guard.check("after captured gmpy2 wrapper execution")
    except BaseException:
        for name in tuple(sys.modules):
            if name == "gmpy2" or name.startswith("gmpy2."):
                sys.modules.pop(name, None)
        raise
    if Path(os.path.abspath(package.__file__)) != snapshot.package_init:
        raise FrozenLoadError("gmpy2 package metadata escaped the verified runtime tree")
    return package


def _execute_frozen_selector(
    *,
    entry_context: dict[str, object],
    expected_sha256: str,
    guard: _RuntimeIdentityGuard,
    source: bytes,
    source_path: Path,
) -> ModuleType:
    """Compile and execute captured selector bytes under the runtime guard."""

    module_name = f"_positive_b_stage_b_t0_attested_{expected_sha256[:16]}"
    if module_name in sys.modules:
        raise FrozenLoadError("private attested module name is already occupied")
    module = ModuleType(module_name)
    module.__file__ = str(source_path)
    module.__package__ = ""
    module.__loader__ = None
    module.__dict__["__builtins__"] = dict(guard.wrapper_builtins)
    module.__dict__["_T0_RUNTIME_IDENTITY_GUARD"] = guard.check
    module.__dict__["_T0_VERIFIED_ENTRY_CONTEXT"] = entry_context
    sys.modules[module_name] = module
    try:
        guard.check("before selector source compile")
        source_code = guard.compile(
            source,
            str(source_path),
            "exec",
            dont_inherit=True,
        )
        guard.check("before selector source execution")
        guard.exec(source_code, module.__dict__)
        guard.check("after selector source execution")
        attestation = module.verify_t0_package_runtime(require_isolated=True)
        guard.check("after selector post-load attestation")
        if attestation.get("implementation_sha256") != expected_sha256:
            raise FrozenLoadError("post-load implementation attestation mismatch")
        if attestation.get("entry") != entry_context:
            raise FrozenLoadError("post-load external-attestation binding mismatch")
        if attestation.get("trust_contract") != _expected_trust_contract():
            raise FrozenLoadError("post-load execution trust-contract mismatch")
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def load_frozen_selector(
    external_attestation_path: str | Path,
    expected_external_attestation_sha256: str,
) -> ModuleType:
    """Load exact T0 bytes under the external execution trust contract."""

    if sys.flags.isolated != 1 or sys.flags.no_site != 1 or "" in sys.path:
        raise FrozenLoadError("T0 loader requires python -I -S isolation")
    injected = sorted(
        name
        for name, value in os.environ.items()
        if value and (name.startswith("DYLD_") or name in {"LD_LIBRARY_PATH", "LD_PRELOAD"})
    )
    if injected:
        raise FrozenLoadError(f"native-loader injection environment is forbidden: {injected}")
    preloaded_critical_stdlib = sorted(
        name for name in CRITICAL_STDLIB_MODULE_NAMES if name in sys.modules
    )
    if preloaded_critical_stdlib:
        raise FrozenLoadError(
            "critical selector stdlib module was preloaded before verified entry: "
            f"{preloaded_critical_stdlib}"
        )
    occupied_selector_names = {
        name
        for name in (
            "positive_b_stage_b_t0_selector",
            "positive_b_stage_b_t1_selector_v5",
        )
        if name in sys.modules
    }
    if occupied_selector_names:
        raise FrozenLoadError("selector module name was occupied before verified loading")

    sys.dont_write_bytecode = True
    guard = _RuntimeIdentityGuard()
    expected_sha256, runtime_root, entry_context = _consume_external_attestation(
        Path(external_attestation_path),
        expected_external_attestation_sha256,
    )
    guard.check("after external attestation consumption")
    source_path = Path(os.path.abspath(Path(__file__).parent / IMPLEMENTATION_NAME))
    source = _read_exact_source(source_path)
    actual_sha256 = hashlib.sha256(source).hexdigest()
    if actual_sha256 != expected_sha256:
        raise FrozenLoadError("frozen implementation SHA-256 mismatch")
    guard.check("after selector source snapshot")
    runtime_snapshot = _verify_runtime_tree(runtime_root)
    guard.check("after runtime-tree snapshot")
    try:
        _load_verified_gmpy2(runtime_snapshot, guard)
        return _execute_frozen_selector(
            entry_context=entry_context,
            expected_sha256=expected_sha256,
            guard=guard,
            source=source,
            source_path=source_path,
        )
    except BaseException:
        for name in tuple(sys.modules):
            if name == "gmpy2" or name.startswith("gmpy2."):
                sys.modules.pop(name, None)
        raise


__all__ = ["FrozenLoadError", "load_frozen_selector"]
