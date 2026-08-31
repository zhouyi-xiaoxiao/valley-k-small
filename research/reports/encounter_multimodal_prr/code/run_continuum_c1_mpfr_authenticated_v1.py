"""Authenticated MPFR launcher for the frozen Round-171 fixed-row sources.

This file is a payload, not a pathname-trusted script.  It must be read once,
SHA-256 checked against an operator-frozen digest, and executed from those
captured bytes under ``python -I -S``.  A direct pathname execution fails
before any gmpy2 code is loaded.

The launcher reuses the independently accepted Round-95 descriptor-snapshot
loader to authenticate the exact gmpy2 wrapper, native extension, bundled
GMP/MPFR/MPC libraries, and runtime lock.  It then compiles and executes the
selected scientific target from a descriptor snapshot.  Native images remain
path-loaded under the explicit no-hostile-same-UID-writer contract carried by
the authority; this is defense in depth, not cryptographic immutability.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Final

AUTHORITY_RELATIVE: Final = Path("code/continuum_c1_mpfr_execution_authority_v1.json")
# Patched only after all target bytes and the canonical authority are frozen.
AUTHORITY_SHA256: Final = "1697b0e1ebd9c1dcc38d827a62d07c2e75b397e25e5e7e0f88bad4d9edac32ab"
AUTHORITY_SCHEMA: Final = "encounter_continuum_c1_mpfr_execution_authority_v1"
AUTHORITY_STATUS: Final = "AUTHORITY_FIXED_12_ROW_EXECUTION_ONLY_NO_REFINEMENT_NO_C1_C2"
AUTHORIZATION: Final = "FIXED-ROW-SOURCE-EXECUTION-ONLY-NO-SCIENTIFIC-PROMOTION"
CONTEXT_SCHEMA: Final = "encounter_continuum_c1_authenticated_target_context_v1"
RECEIPT_SCHEMA: Final = "encounter_continuum_c1_mpfr_authenticated_outer_receipt_v1"
RECEIPT_STATUS: Final = "PASS_AUTHENTICATED_FIXED_ROW_SOURCE_EXECUTION_ONLY_NO_SCIENTIFIC_PROMOTION"
MAX_SOURCE_BYTES: Final = 2_000_000
MAX_ARTIFACT_BYTES: Final = 16_000_000
EXPECTED_AUTHORITY_KEYS: Final = {
    "authorization",
    "claim_boundary",
    "runtime",
    "schema",
    "status",
    "targets",
    "trust_contract",
}
EXPECTED_TARGET_KEYS: Final = {
    "artifact_builder_target",
    "artifact_path",
    "artifact_sha256",
    "expected_argv",
    "receipt_path",
    "source_path",
    "source_sha256",
    "target_kind",
}
EXPECTED_CONTEXT_KEYS: Final = {
    "authority_sha256",
    "gmpy2_module",
    "launcher_sha256",
    "runtime_attestation",
    "schema",
    "target_key",
    "target_source_path",
    "target_source_sha256",
}
REQUIRED_FALSE_CLAIMS: Final = {
    "backend_independence_claimed",
    "complete_C1",
    "complete_C2",
    "release_eligible",
}


class AuthenticatedExecutionError(RuntimeError):
    """A frozen source or execution-boundary check failed closed."""


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 48:
        raise AuthenticatedExecutionError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise AuthenticatedExecutionError("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise AuthenticatedExecutionError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise AuthenticatedExecutionError("invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise AuthenticatedExecutionError(f"forbidden JSON type: {type(value).__name__}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise AuthenticatedExecutionError("duplicate or invalid JSON object key")
        result[key] = value
    return result


def _canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _parse_canonical_json(payload: bytes, role: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(
                AuthenticatedExecutionError(f"forbidden JSON constant: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuthenticatedExecutionError(f"{role} is not canonical ASCII JSON") from error
    if type(value) is not dict or _canonical_bytes(value) != payload:
        raise AuthenticatedExecutionError(f"{role} canonical-byte drift")
    return value


def _safe_relative(value: object, role: str) -> Path:
    if type(value) is not str:
        raise AuthenticatedExecutionError(f"{role} path is not a string")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or not pure.parts
        or "." in pure.parts
        or ".." in pure.parts
        or value != pure.as_posix()
    ):
        raise AuthenticatedExecutionError(f"{role} path is not safe report-relative")
    return Path(*pure.parts)


def _canonical_nonsymlink_path(path: Path, role: str) -> Path:
    if type(path) is not Path:
        path = Path(path)
    lexical = Path(os.path.abspath(path))
    if path != lexical or not path.is_absolute():
        raise AuthenticatedExecutionError(f"{role} path is not canonical absolute")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = os.lstat(current)
        except OSError as error:
            raise AuthenticatedExecutionError(f"{role} path is unavailable") from error
        if stat.S_ISLNK(info.st_mode):
            raise AuthenticatedExecutionError(f"{role} path contains a symbolic link")
    return lexical


def _stable_snapshot(path: Path, role: str, cap: int) -> bytes:
    path = _canonical_nonsymlink_path(path, role)
    if not hasattr(os, "O_NOFOLLOW"):
        raise AuthenticatedExecutionError("O_NOFOLLOW is unavailable")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as error:
        raise AuthenticatedExecutionError(f"cannot open {role}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size <= 0 or before.st_size > cap:
            raise AuthenticatedExecutionError(f"{role} is not a bounded regular file")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                raise AuthenticatedExecutionError(f"short read for {role}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AuthenticatedExecutionError(f"{role} grew during read")
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
        raise AuthenticatedExecutionError(f"{role} changed during read")
    lexical_after = os.lstat(path)
    if (lexical_after.st_dev, lexical_after.st_ino) != (before.st_dev, before.st_ino):
        raise AuthenticatedExecutionError(f"{role} path was replaced during read")
    return b"".join(chunks)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_digest(path: Path, expected: object, role: str, cap: int) -> bytes:
    if not _is_sha256(expected):
        raise AuthenticatedExecutionError(f"{role} SHA-256 is not canonical")
    payload = _stable_snapshot(path, role, cap)
    if _sha256(payload) != expected:
        raise AuthenticatedExecutionError(f"{role} SHA-256 mismatch")
    return payload


def _report_root() -> Path:
    launcher = Path(__file__)
    if not launcher.is_absolute():
        raise AuthenticatedExecutionError("launcher __file__ is not absolute")
    launcher = _canonical_nonsymlink_path(
        Path(os.path.abspath(launcher)),
        "authenticated launcher",
    )
    if launcher.parent.name != "code":
        raise AuthenticatedExecutionError("launcher is not in the report code directory")
    return launcher.parents[1]


def _validate_authority(authority: dict[str, Any]) -> None:
    if set(authority) != EXPECTED_AUTHORITY_KEYS:
        raise AuthenticatedExecutionError("authority top-level schema drift")
    if authority["schema"] != AUTHORITY_SCHEMA:
        raise AuthenticatedExecutionError("authority schema drift")
    if authority["status"] != AUTHORITY_STATUS:
        raise AuthenticatedExecutionError("authority status drift")
    if authority["authorization"] != AUTHORIZATION:
        raise AuthenticatedExecutionError("authority authorization drift")
    claims = authority["claim_boundary"]
    if (
        type(claims) is not dict
        or not REQUIRED_FALSE_CLAIMS.issubset(claims)
        or any(type(value) is not bool or value for value in claims.values())
    ):
        raise AuthenticatedExecutionError("authority claim boundary is not exact-false")
    runtime = authority["runtime"]
    if (
        type(runtime) is not dict
        or set(runtime)
        != {
            "external_attestation",
            "requirements_lock",
            "runtime_lock",
            "runtime_site_root",
            "verified_loader",
            "versions",
        }
        or type(runtime["runtime_site_root"]) is not str
        or type(runtime["versions"]) is not dict
    ):
        raise AuthenticatedExecutionError("authority runtime schema drift")
    for role in (
        "external_attestation",
        "requirements_lock",
        "runtime_lock",
        "verified_loader",
    ):
        entry = runtime[role]
        if (
            type(entry) is not dict
            or set(entry) != {"path", "sha256"}
            or not _is_sha256(entry["sha256"])
        ):
            raise AuthenticatedExecutionError(f"authority runtime entry drift for {role}")
        _safe_relative(entry["path"], f"runtime {role}")
    targets = authority["targets"]
    if type(targets) is not dict or not targets:
        raise AuthenticatedExecutionError("authority has no targets")
    for key, entry in targets.items():
        if type(key) is not str or type(entry) is not dict or set(entry) != EXPECTED_TARGET_KEYS:
            raise AuthenticatedExecutionError(f"authority target schema drift for {key!r}")
        for path_role in (
            "artifact_path",
            "receipt_path",
            "source_path",
        ):
            _safe_relative(entry[path_role], f"target {key} {path_role}")
        if (
            not _is_sha256(entry["artifact_sha256"])
            or not _is_sha256(entry["source_sha256"])
            or type(entry["artifact_builder_target"]) is not str
            or entry["artifact_builder_target"] not in targets
            or type(entry["target_kind"]) is not str
            or entry["target_kind"] not in {"builder_check", "independent_validator"}
            or type(entry["expected_argv"]) is not list
            or any(type(item) is not str for item in entry["expected_argv"])
        ):
            raise AuthenticatedExecutionError(f"authority target value drift for {key}")
    trust = authority["trust_contract"]
    if (
        type(trust) is not dict
        or trust.get("schema") != "encounter_continuum_c1_mpfr_execution_trust_contract_v1"
        or trust.get("target_execution") != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
        or trust.get("gmpy2_wrapper_execution") != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
        or trust.get("native_image_execution")
        != "PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT"
        or trust.get("runtime_tree_concurrency")
        != "NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-TARGET-EXECUTION"
        or trust.get("protection_claim") != "DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY"
    ):
        raise AuthenticatedExecutionError("authority trust-contract drift")


def _load_authority(report: Path) -> tuple[dict[str, Any], Path]:
    authority_path = report / AUTHORITY_RELATIVE
    payload = _require_digest(
        authority_path,
        AUTHORITY_SHA256,
        "MPFR execution authority",
        100_000,
    )
    authority = _parse_canonical_json(payload, "MPFR execution authority")
    _validate_authority(authority)
    return authority, authority_path


def _verify_isolated_entry() -> tuple[bytes, str]:
    if (
        sys.flags.isolated != 1
        or sys.flags.no_site != 1
        or not sys.flags.safe_path
        or "" in sys.path
    ):
        raise AuthenticatedExecutionError("launcher requires python -I -S safe-path isolation")
    forbidden_environment = sorted(
        name
        for name, value in os.environ.items()
        if value
        and (
            name
            in {
                "LD_LIBRARY_PATH",
                "LD_PRELOAD",
                "PYTHONHOME",
                "PYTHONINSPECT",
                "PYTHONPATH",
                "PYTHONSTARTUP",
            }
            or name.startswith("DYLD_")
        )
    )
    if forbidden_environment:
        raise AuthenticatedExecutionError(
            f"forbidden Python/native loader environment: {forbidden_environment}"
        )
    cwd = Path(os.path.realpath(os.getcwd()))
    for entry in sys.path:
        if not os.path.isabs(entry) or Path(os.path.realpath(entry)) == cwd:
            raise AuthenticatedExecutionError("cwd or a relative entry is present in sys.path")
    if any(name == "gmpy2" or name.startswith("gmpy2.") for name in sys.modules):
        raise AuthenticatedExecutionError("gmpy2 was loaded before authenticated entry")

    injected_bytes = globals().get("_OUTER_AUTHENTICATED_LAUNCHER_BYTES")
    injected_sha256 = globals().get("_OUTER_AUTHENTICATED_LAUNCHER_SHA256")
    if type(injected_bytes) is not bytes or not _is_sha256(injected_sha256):
        raise AuthenticatedExecutionError(
            "operator-authenticated launcher snapshot injection is missing"
        )
    if _sha256(injected_bytes) != injected_sha256:
        raise AuthenticatedExecutionError("injected launcher snapshot SHA-256 mismatch")
    current = _stable_snapshot(
        Path(os.path.abspath(__file__)),
        "launcher path postcheck",
        MAX_SOURCE_BYTES,
    )
    if _sha256(current) != injected_sha256 or current != injected_bytes:
        raise AuthenticatedExecutionError(
            "executed launcher snapshot differs from its current frozen path"
        )
    return injected_bytes, injected_sha256


def _load_verified_loader(
    report: Path,
    authority: dict[str, Any],
) -> tuple[ModuleType, bytes]:
    entry = authority["runtime"]["verified_loader"]
    path = report / _safe_relative(entry["path"], "verified loader")
    payload = _require_digest(
        path,
        entry["sha256"],
        "verified Round-95 loader",
        MAX_SOURCE_BYTES,
    )
    module_name = "_encounter_round171_authenticated_mpfr_loader"
    if module_name in sys.modules:
        raise AuthenticatedExecutionError("private verified-loader module name is occupied")
    module = ModuleType(module_name)
    module.__file__ = str(path)
    module.__package__ = ""
    module.__loader__ = None
    module.__spec__ = None
    module.__dict__["__builtins__"] = (
        dict(__builtins__) if type(__builtins__) is dict else (dict(__builtins__.__dict__))
    )
    sys.modules[module_name] = module
    try:
        code = compile(payload, str(path), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    post = _require_digest(
        path,
        entry["sha256"],
        "verified Round-95 loader postcheck",
        MAX_SOURCE_BYTES,
    )
    if post != payload:
        raise AuthenticatedExecutionError("verified loader path changed after execution")
    return module, payload


def _load_authenticated_runtime(
    report: Path,
    authority: dict[str, Any],
) -> tuple[Any, ModuleType, dict[str, Any]]:
    runtime = authority["runtime"]
    for role in ("external_attestation", "requirements_lock", "runtime_lock"):
        entry = runtime[role]
        _require_digest(
            report / _safe_relative(entry["path"], role),
            entry["sha256"],
            role,
            MAX_SOURCE_BYTES,
        )
    loader, _loader_bytes = _load_verified_loader(report, authority)
    guard = loader._RuntimeIdentityGuard()
    external = runtime["external_attestation"]
    external_path = report / _safe_relative(external["path"], "external attestation")
    selector_sha256, runtime_root, entry_context = loader._consume_external_attestation(
        external_path,
        external["sha256"],
    )
    expected_runtime_root = Path(runtime["runtime_site_root"])
    expected_runtime_root = _canonical_nonsymlink_path(
        expected_runtime_root,
        "authority runtime-site root",
    )
    if runtime_root != expected_runtime_root:
        raise AuthenticatedExecutionError("runtime-site root differs from authority")

    selector_path = Path(os.path.abspath(Path(loader.__file__).parent / loader.IMPLEMENTATION_NAME))
    selector_source = loader._read_exact_source(selector_path)
    if _sha256(selector_source) != selector_sha256:
        raise AuthenticatedExecutionError("Round-95 selector snapshot digest drift")
    runtime_snapshot = loader._verify_runtime_tree(runtime_root)
    loader._load_verified_gmpy2(runtime_snapshot, guard)
    selector = loader._execute_frozen_selector(
        entry_context=entry_context,
        expected_sha256=selector_sha256,
        guard=guard,
        source=selector_source,
        source_path=selector_path,
    )
    attestation = selector.verify_t0_package_runtime(require_isolated=True)
    observed_versions = {
        "gmp": attestation["runtime"]["gmp"],
        "gmpy2": attestation["runtime"]["gmpy2"],
        "mpc": attestation["runtime"]["mpc"],
        "mpfr": attestation["runtime"]["mpfr"],
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
        "system": (f"{selector.platform.system()} {selector.platform.machine()}"),
    }
    if observed_versions != runtime["versions"]:
        raise AuthenticatedExecutionError("authenticated runtime version mapping drift")
    return guard, selector, attestation


def _artifact_snapshot(
    path: Path,
    expected_sha256: str | None,
    role: str,
) -> tuple[bytes, str, dict[str, Any]]:
    payload = _stable_snapshot(path, role, MAX_ARTIFACT_BYTES)
    digest = _sha256(payload)
    if expected_sha256 is not None and digest != expected_sha256:
        raise AuthenticatedExecutionError(f"{role} SHA-256 mismatch")
    artifact = _parse_canonical_json(payload, role)
    return payload, digest, artifact


def _check_artifact_boundary(
    artifact: dict[str, Any],
    authority: dict[str, Any],
    target: dict[str, Any],
) -> dict[str, str]:
    claims = artifact.get("claim_boundary")
    if (
        type(claims) is not dict
        or not REQUIRED_FALSE_CLAIMS.issubset(claims)
        or any(type(value) is not bool or value for value in claims.values())
    ):
        raise AuthenticatedExecutionError("artifact claim boundary is not exact-false")
    pins = artifact.get("source_pins")
    if type(pins) is not dict or type(pins.get("builder_source")) is not dict:
        raise AuthenticatedExecutionError("artifact builder self-pin is missing")
    self_pin = pins["builder_source"]
    if type(self_pin) is not dict or set(self_pin) != {"path", "sha256"}:
        raise AuthenticatedExecutionError("artifact builder self-pin schema drift")
    builder_target_key = target["artifact_builder_target"]
    builder_target = authority["targets"][builder_target_key]
    expected = {
        "path": builder_target["source_path"],
        "sha256": builder_target["source_sha256"],
    }
    if self_pin != expected:
        raise AuthenticatedExecutionError(
            "artifact builder self-pin differs from captured authority snapshot"
        )
    return expected


def _target_context(
    *,
    authority_sha256: str,
    launcher_sha256: str,
    runtime_attestation: dict[str, Any],
    target_key: str,
    target: dict[str, Any],
) -> dict[str, Any]:
    context = {
        "authority_sha256": authority_sha256,
        "gmpy2_module": sys.modules.get("gmpy2"),
        "launcher_sha256": launcher_sha256,
        "runtime_attestation": runtime_attestation,
        "schema": CONTEXT_SCHEMA,
        "target_key": target_key,
        "target_source_path": target["source_path"],
        "target_source_sha256": target["source_sha256"],
    }
    if (
        set(context) != EXPECTED_CONTEXT_KEYS
        or context["gmpy2_module"] is None
        or sys.modules.get("gmpy2") is not context["gmpy2_module"]
    ):
        raise AuthenticatedExecutionError("authenticated target context construction failed")
    return context


def _execute_target_snapshot(
    *,
    argv: list[str],
    context: dict[str, Any],
    guard: Any,
    source: bytes,
    source_path: Path,
) -> tuple[int, str, str]:
    module_name = f"_encounter_round171_target_{context['target_source_sha256'][:16]}"
    if module_name in sys.modules:
        raise AuthenticatedExecutionError("private target module name is occupied")
    module = ModuleType(module_name)
    module.__name__ = "__main__"
    module.__file__ = str(source_path)
    module.__package__ = ""
    module.__loader__ = None
    module.__spec__ = None
    module.__dict__["__builtins__"] = dict(guard.wrapper_builtins)
    module.__dict__["_CONTINUUM_C1_AUTHENTICATED_EXECUTION_CONTEXT"] = context
    sys.modules[module_name] = module
    output = io.StringIO()
    errors = io.StringIO()
    previous_argv = sys.argv
    sys.argv = [str(source_path), *argv]
    exit_code = 0
    try:
        guard.check("before Round-171 target compile")
        source_code = guard.compile(
            source,
            str(source_path),
            "exec",
            dont_inherit=True,
        )
        guard.check("before Round-171 target execution")
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            try:
                guard.exec(source_code, module.__dict__)
            except SystemExit as error:
                code = error.code
                if code is None:
                    exit_code = 0
                elif type(code) is int:
                    exit_code = code
                else:
                    errors.write(str(code) + "\n")
                    exit_code = 1
        guard.check("after Round-171 target execution")
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    finally:
        sys.argv = previous_argv
    return exit_code, output.getvalue(), errors.getvalue()


def _write_receipt(path: Path, payload: bytes) -> str:
    parent = _canonical_nonsymlink_path(path.parent, "receipt parent")
    if path != parent / path.name:
        raise AuthenticatedExecutionError("receipt path escaped its canonical parent")
    if path.exists() or path.is_symlink():
        _canonical_nonsymlink_path(path, "existing receipt")
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode):
            raise AuthenticatedExecutionError("existing receipt is not a regular file")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    observed = _stable_snapshot(path, "written outer receipt", 1_000_000)
    if observed != payload:
        raise AuthenticatedExecutionError("written outer receipt byte drift")
    return _sha256(payload)


def _canonical_execution(
    *,
    artifact_probe: str | None,
    authority: dict[str, Any],
    launcher_sha256: str,
    regenerate_builder: bool,
    report: Path,
    target_key: str,
) -> tuple[int, str | None]:
    targets = authority["targets"]
    if target_key not in targets:
        raise AuthenticatedExecutionError("unknown authority target")
    target = targets[target_key]
    source_path = report / _safe_relative(target["source_path"], "target source")
    source = _require_digest(
        source_path,
        target["source_sha256"],
        f"target source {target_key}",
        MAX_SOURCE_BYTES,
    )
    artifact_path = report / _safe_relative(target["artifact_path"], "target artifact")
    probe_path: Path | None = None
    if artifact_probe is None:
        artifact_before, artifact_sha_before, parsed_before = _artifact_snapshot(
            artifact_path,
            target["artifact_sha256"],
            "canonical target artifact before execution",
        )
        if regenerate_builder:
            if target["target_kind"] != "builder_check":
                raise AuthenticatedExecutionError("regeneration is builder-only")
            target_argv = []
        else:
            _check_artifact_boundary(parsed_before, authority, target)
            target_argv = list(target["expected_argv"])
    else:
        if regenerate_builder:
            raise AuthenticatedExecutionError(
                "artifact probe and builder regeneration are mutually exclusive"
            )
        if target["target_kind"] != "independent_validator":
            raise AuthenticatedExecutionError("artifact probes are validator-only")
        probe_path = _canonical_nonsymlink_path(
            Path(artifact_probe),
            "validator artifact probe",
        )
        artifact_before, artifact_sha_before, _parsed_before = _artifact_snapshot(
            probe_path,
            None,
            "validator artifact probe before execution",
        )
        target_argv = ["--artifact", str(probe_path)]

    guard, selector, runtime_attestation = _load_authenticated_runtime(report, authority)
    authenticated_gmpy2 = sys.modules.get("gmpy2")
    if authenticated_gmpy2 is None:
        raise AuthenticatedExecutionError("authenticated gmpy2 disappeared before target")
    ambient_context = authenticated_gmpy2.get_context()
    ambient_context.precision = 53
    ambient_context.round = authenticated_gmpy2.RoundToNearest
    ambient_precision = int(ambient_context.precision)
    if ambient_precision != 53 or ambient_context.round != authenticated_gmpy2.RoundToNearest:
        raise AuthenticatedExecutionError("cannot establish hostile ambient MPFR context")
    ambient_rounding = "RoundToNearest"
    context = _target_context(
        authority_sha256=AUTHORITY_SHA256,
        launcher_sha256=launcher_sha256,
        runtime_attestation=runtime_attestation,
        target_key=target_key,
        target=target,
    )
    exit_code, stdout, stderr = _execute_target_snapshot(
        argv=target_argv,
        context=context,
        guard=guard,
        source=source,
        source_path=source_path,
    )
    guard.check("after target return")
    selector.verify_t0_package_runtime(require_isolated=True)
    source_after = _require_digest(
        source_path,
        target["source_sha256"],
        f"target source {target_key} postcheck",
        MAX_SOURCE_BYTES,
    )
    if source_after != source:
        raise AuthenticatedExecutionError("target source path changed after captured execution")

    observed_artifact_path = probe_path if probe_path is not None else artifact_path
    artifact_after, artifact_sha_after, parsed_after = _artifact_snapshot(
        observed_artifact_path,
        None if probe_path is not None or regenerate_builder else target["artifact_sha256"],
        "target artifact after execution",
    )
    if not regenerate_builder and (
        artifact_after != artifact_before or artifact_sha_after != artifact_sha_before
    ):
        raise AuthenticatedExecutionError("target artifact changed during authenticated execution")

    if probe_path is not None:
        if exit_code == 0 and artifact_sha_after != target["artifact_sha256"]:
            raise AuthenticatedExecutionError("validator accepted a noncanonical artifact probe")
        combined = (stdout + stderr).strip()
        if exit_code != 0:
            print(f"HOLD_PROBE {combined}", file=sys.stderr)
            return exit_code, None
        print(
            "PASS_PROBE "
            + json.dumps(
                {
                    "artifact_sha256": artifact_sha_after,
                    "target": target_key,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0, None

    if exit_code != 0:
        raise AuthenticatedExecutionError(
            f"authenticated target returned {exit_code}: {(stdout + stderr).strip()}"
        )
    self_pin = _check_artifact_boundary(parsed_after, authority, target)
    if regenerate_builder:
        print(
            "PASS_REGENERATED "
            + json.dumps(
                {
                    "artifact_sha256": artifact_sha_after,
                    "builder_self_pin": self_pin,
                    "target": target_key,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0, None
    receipt_path = report / _safe_relative(target["receipt_path"], "outer receipt")
    serializable_context = {key: value for key, value in context.items() if key != "gmpy2_module"}
    receipt = {
        "artifact": {
            "builder_self_pin": self_pin,
            "path": target["artifact_path"],
            "sha256": artifact_sha_after,
        },
        "authority": {
            "path": AUTHORITY_RELATIVE.as_posix(),
            "sha256": AUTHORITY_SHA256,
        },
        "authorization": AUTHORIZATION,
        "claim_boundary": authority["claim_boundary"],
        "execution": {
            "ambient_mpfr_precision_bits": ambient_precision,
            "ambient_mpfr_rounding": ambient_rounding,
            "argv": target_argv,
            "cwd_excluded_from_sys_path": True,
            "isolated": True,
            "no_site": True,
            "safe_path": True,
            "target_exit_code": exit_code,
            "target_stderr": stderr,
            "target_stdout": stdout,
        },
        "launcher": {
            "execution": "OPERATOR-PINNED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
            "path": Path(__file__).relative_to(report).as_posix(),
            "sha256": launcher_sha256,
        },
        "runtime_attestation": runtime_attestation,
        "schema": RECEIPT_SCHEMA,
        "status": RECEIPT_STATUS,
        "target": {
            "authenticated_context": serializable_context,
            "key": target_key,
            "kind": target["target_kind"],
            "source_path": target["source_path"],
            "source_sha256": target["source_sha256"],
        },
        "trust_contract": authority["trust_contract"],
    }
    payload = _canonical_bytes(receipt)
    receipt_sha256 = _write_receipt(receipt_path, payload)
    print(receipt_sha256)
    return 0, receipt_sha256


def main() -> int:
    try:
        _launcher_bytes, launcher_sha256 = _verify_isolated_entry()
        report = _report_root()
        authority, _authority_path = _load_authority(report)
        parser = argparse.ArgumentParser()
        parser.add_argument("--target", required=True)
        parser.add_argument("--artifact-probe")
        parser.add_argument("--regenerate-builder", action="store_true")
        arguments = parser.parse_args()
        return _canonical_execution(
            artifact_probe=arguments.artifact_probe,
            authority=authority,
            launcher_sha256=launcher_sha256,
            regenerate_builder=arguments.regenerate_builder,
            report=report,
            target_key=arguments.target,
        )[0]
    except (AuthenticatedExecutionError, OSError, ValueError) as error:
        print(f"HOLD {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
