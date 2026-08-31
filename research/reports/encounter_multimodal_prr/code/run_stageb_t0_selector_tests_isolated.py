"""Run the non-promotable Stage-B T0 package tests behind the exact loader.

Invoke this runner only as ``python -I -S``.  It authenticates the frozen
synthetic attestation and loader before executing either, loads the selector,
then executes the three attested test sources directly from verified bytes.
It never imports or opens any scientific object, producer, result, or manifest.
"""

from __future__ import annotations

import builtins
import hashlib
import json
import os
import stat
import sys
import unittest
from pathlib import Path
from types import ModuleType

AUTHORIZATION_NONE = "AUTHORIZED-SCIENTIFIC-COMMAND: NONE"
EXPECTED_ATTESTATION_SHA256 = "a7978c22d7ee39111d042edc918c1149f4a985d995fb24491cc6dcb2497e5c80"
EXPECTED_LOADER_SHA256 = "9a3cd379f4a19c5b0cf6317d9e3bfbfd39bf6914714de7fb014754a4d0ca4cad"
EXPECTED_TEST_COUNT = 54
MAX_FILE_BYTES = 8 * 1024 * 1024
BOOTSTRAP_COMPILE = builtins.compile
BOOTSTRAP_EXEC = builtins.exec
BOOTSTRAP_IMPORT = builtins.__import__


class BootstrapError(RuntimeError):
    """The isolated synthetic-test trust boundary failed."""


def _read_exact_regular(path: Path, role: str) -> bytes:
    path = Path(os.path.abspath(path))
    if not path.is_absolute() or not hasattr(os, "O_NOFOLLOW"):
        raise BootstrapError(f"{role} path/runtime is not fail-closed")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = os.lstat(current)
        except OSError as exc:
            raise BootstrapError(f"{role} path is unavailable") from exc
        if stat.S_ISLNK(info.st_mode):
            raise BootstrapError(f"{role} path contains a symbolic link")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as exc:
        raise BootstrapError(f"cannot open {role}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_FILE_BYTES:
            raise BootstrapError(f"{role} is not a bounded regular file")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                raise BootstrapError(f"short {role} read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise BootstrapError(f"{role} grew during read")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    def identity(item: os.stat_result) -> tuple[int, int, int, int, int, int]:
        return (
            item.st_dev,
            item.st_ino,
            item.st_mode,
            item.st_size,
            item.st_mtime_ns,
            item.st_ctime_ns,
        )

    lexical = os.lstat(path)
    if identity(before) != identity(after) or (lexical.st_dev, lexical.st_ino) != (
        before.st_dev,
        before.st_ino,
    ):
        raise BootstrapError(f"{role} changed during descriptor read")
    return b"".join(chunks)


def _execute_verified_module(name: str, path: Path, source: bytes) -> ModuleType:
    if (
        builtins.compile is not BOOTSTRAP_COMPILE
        or builtins.exec is not BOOTSTRAP_EXEC
        or builtins.__import__ is not BOOTSTRAP_IMPORT
    ):
        raise BootstrapError("bootstrap builtins identity drift before captured-byte execution")
    if name in sys.modules:
        raise BootstrapError(f"module name occupied before exact execution: {name}")
    module = ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    module.__loader__ = None
    sys.modules[name] = module
    try:
        BOOTSTRAP_EXEC(
            BOOTSTRAP_COMPILE(source, str(path), "exec", dont_inherit=True),
            module.__dict__,
        )
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def main() -> int:
    if sys.flags.isolated != 1 or sys.flags.no_site != 1 or "" in sys.path:
        raise BootstrapError("runner requires python -I -S")
    code_dir = Path(os.path.abspath(Path(__file__).parent))
    attestation_path = code_dir / "positive_b_stage_b_t0_synthetic_test_attestation_v2.json"
    attestation_bytes = _read_exact_regular(attestation_path, "synthetic attestation")
    if hashlib.sha256(attestation_bytes).hexdigest() != EXPECTED_ATTESTATION_SHA256:
        raise BootstrapError("synthetic attestation SHA-256 mismatch")
    try:
        record = json.loads(attestation_bytes.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError("synthetic attestation is not ASCII JSON") from exc
    if (
        json.dumps(record, sort_keys=True, indent=2).encode("ascii") + b"\n" != attestation_bytes
        or record.get("authorization") != AUTHORIZATION_NONE
        or record.get("status") != "NON-PROMOTABLE-SYNTHETIC-TEST"
    ):
        raise BootstrapError("synthetic attestation canonical/status drift")

    loader_path = code_dir / "positive_b_stage_b_t0_verified_loader.py"
    loader_bytes = _read_exact_regular(loader_path, "verified loader")
    if hashlib.sha256(loader_bytes).hexdigest() != EXPECTED_LOADER_SHA256 or record["files"][
        "loader"
    ] != {
        "path": "code/positive_b_stage_b_t0_verified_loader.py",
        "sha256": EXPECTED_LOADER_SHA256,
    }:
        raise BootstrapError("loader bytes are not bound to the attestation")
    loader = _execute_verified_module(
        "_round81_exact_stageb_t0_loader",
        loader_path,
        loader_bytes,
    )
    selector = loader.load_frozen_selector(
        attestation_path,
        EXPECTED_ATTESTATION_SHA256,
    )
    sys.modules["positive_b_stage_b_t0_verified_loader"] = loader
    sys.modules["positive_b_stage_b_t1_selector_v5"] = selector

    loaded_tests: list[ModuleType] = []
    for name, role, filename in (
        (
            "test_positive_b_stage_b_t1_selector_v5",
            "primary_tests",
            "test_positive_b_stage_b_t1_selector_v5.py",
        ),
        (
            "test_stageb_t0_selector_round78",
            "exploit_tests",
            "test_stageb_t0_selector_round78.py",
        ),
        (
            "test_stageb_t0_selector_round94",
            "race_regression_tests",
            "test_stageb_t0_selector_round94.py",
        ),
    ):
        path = code_dir / filename
        source = _read_exact_regular(path, role)
        entry = record["files"][role]
        if entry != {
            "path": f"code/{filename}",
            "sha256": hashlib.sha256(source).hexdigest(),
        }:
            raise BootstrapError(f"{role} bytes are not bound to the attestation")
        loaded_tests.append(_execute_verified_module(name, path, source))

    suite = unittest.TestSuite()
    test_loader = unittest.defaultTestLoader
    for module in loaded_tests:
        suite.addTests(test_loader.loadTestsFromModule(module))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun != EXPECTED_TEST_COUNT:
        raise BootstrapError(
            f"test-count closure drift: {result.testsRun} != {EXPECTED_TEST_COUNT}"
        )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
