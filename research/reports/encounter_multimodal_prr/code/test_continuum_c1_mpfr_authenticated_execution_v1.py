#!/usr/bin/env python3
"""Adversarial gates for the Round-171 authenticated MPFR execution chain."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
CODE = REPORT / "code"
PYTHON = Path("/Users/ae23069/.local-build/valley-k-small/.venv/bin/python")
LAUNCHER = CODE / "run_continuum_c1_mpfr_authenticated_v1.py"
LAUNCHER_SHA256 = "f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4"
AUTHORITY = CODE / "continuum_c1_mpfr_execution_authority_v1.json"
AUTHORITY_SHA256 = "1697b0e1ebd9c1dcc38d827a62d07c2e75b397e25e5e7e0f88bad4d9edac32ab"
BOOTSTRAP = """\
import hashlib, os, stat, sys, types
path = os.path.abspath(sys.argv[1])
expected = sys.argv[2]
fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
try:
    before = os.fstat(fd)
    chunks = []
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    after = os.fstat(fd)
finally:
    os.close(fd)
payload = b"".join(chunks)
identity = lambda value: (
    value.st_dev,
    value.st_ino,
    value.st_mode,
    value.st_size,
    value.st_mtime_ns,
    value.st_ctime_ns,
)
assert stat.S_ISREG(before.st_mode) and identity(before) == identity(after)
lexical = os.lstat(path)
assert (lexical.st_dev, lexical.st_ino) == (before.st_dev, before.st_ino)
actual = hashlib.sha256(payload).hexdigest()
assert actual == expected, (actual, expected)
module = types.ModuleType("_operator_pinned_continuum_c1_launcher")
module.__name__ = "__main__"
module.__file__ = path
module.__package__ = ""
module.__loader__ = None
module.__spec__ = None
module.__dict__["_OUTER_AUTHENTICATED_LAUNCHER_BYTES"] = payload
module.__dict__["_OUTER_AUTHENTICATED_LAUNCHER_SHA256"] = actual
sys.argv = [path, *sys.argv[3:]]
exec(compile(payload, path, "exec", dont_inherit=True), module.__dict__)
"""
FORBIDDEN_ENVIRONMENT = {
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONPATH",
    "PYTHONSTARTUP",
}
SCIENCE_ENTRY_PATHS = {
    "raw_flux_builder": CODE / "build_continuum_c1_fixed_row_raw_flux_source_v1.py",
    "raw_flux_validator": CODE / "validate_continuum_c1_fixed_row_raw_flux_source_v1.py",
    "stationary_builder": CODE / "build_continuum_c1_stationary_integral_source_v1.py",
    "stationary_validator": CODE / "validate_continuum_c1_stationary_integral_source_v1.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for name in tuple(environment):
        if name in FORBIDDEN_ENVIRONMENT or name.startswith("DYLD_"):
            environment.pop(name)
    return environment


def _run_launcher(
    target: str,
    *,
    artifact_probe: Path | None = None,
    cwd: Path = REPORT,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(PYTHON),
        "-I",
        "-S",
        "-c",
        BOOTSTRAP,
        str(LAUNCHER),
        LAUNCHER_SHA256,
        "--target",
        target,
    ]
    if artifact_probe is not None:
        command.extend(("--artifact-probe", str(artifact_probe)))
    return subprocess.run(
        command,
        cwd=cwd,
        env=_clean_environment() if environment is None else environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=120,
        check=False,
    )


def _load_launcher_module() -> ModuleType:
    name = "_round171_launcher_adversarial_test"
    spec = importlib.util.spec_from_file_location(name, LAUNCHER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("ascii")


def test_live_launcher_authority_and_all_receipts_are_exactly_current() -> None:
    assert PYTHON.is_file()
    assert _sha256(LAUNCHER) == LAUNCHER_SHA256
    assert _sha256(AUTHORITY) == AUTHORITY_SHA256
    authority = json.loads(AUTHORITY.read_text(encoding="ascii"))
    assert set(authority["targets"]) == set(SCIENCE_ENTRY_PATHS)

    for target_key, target in authority["targets"].items():
        assert _sha256(REPORT / target["source_path"]) == target["source_sha256"]
        assert _sha256(REPORT / target["artifact_path"]) == target["artifact_sha256"]
        receipt_path = REPORT / target["receipt_path"]
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes)
        assert receipt_bytes == _canonical(receipt)
        assert receipt["authority"] == {
            "path": "code/continuum_c1_mpfr_execution_authority_v1.json",
            "sha256": AUTHORITY_SHA256,
        }
        assert receipt["launcher"]["sha256"] == LAUNCHER_SHA256
        assert receipt["target"]["key"] == target_key
        assert receipt["target"]["source_sha256"] == target["source_sha256"]
        assert receipt["artifact"]["sha256"] == target["artifact_sha256"]
        assert receipt["artifact"]["builder_self_pin"] == {
            "path": authority["targets"][target["artifact_builder_target"]]["source_path"],
            "sha256": authority["targets"][target["artifact_builder_target"]]["source_sha256"],
        }
        assert receipt["execution"]["ambient_mpfr_precision_bits"] == 53
        assert receipt["execution"]["ambient_mpfr_rounding"] == "RoundToNearest"
        assert receipt["runtime_attestation"]["runtime"]["loaded_native_images"] == [
            "gmpy2.cpython-312-darwin.so",
            "libgmp.10.dylib",
            "libmpc.3.dylib",
            "libmpfr.6.dylib",
        ]
        assert all(value is False for value in receipt["claim_boundary"].values())


@pytest.mark.parametrize(
    ("target", "source"),
    sorted(SCIENCE_ENTRY_PATHS.items()),
)
def test_direct_scientific_entry_holds_before_fake_gmpy2_executes(
    tmp_path: Path,
    target: str,
    source: Path,
) -> None:
    fake_root = tmp_path / target
    fake_package = fake_root / "gmpy2"
    fake_package.mkdir(parents=True)
    sentinel = fake_root / "fake-gmpy2-executed"
    (fake_package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
        encoding="utf-8",
    )
    environment = _clean_environment()
    environment["PYTHONPATH"] = str(fake_root)
    result = subprocess.run(
        [str(PYTHON), "-I", "-S", str(source)],
        cwd=fake_root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0, result.stdout
    assert (
        "authenticated MPFR launcher context required before imports" in result.stdout
        or "HOLD_AUTHENTICATED_RUNTIME" in result.stdout
    )
    assert not sentinel.exists()


def test_fake_pythonpath_wrapper_is_rejected_before_sentinel_execution(
    tmp_path: Path,
) -> None:
    fake_package = tmp_path / "gmpy2"
    fake_package.mkdir()
    sentinel = tmp_path / "fake-wrapper-executed"
    (fake_package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
        encoding="utf-8",
    )
    environment = _clean_environment()
    environment["PYTHONPATH"] = str(tmp_path)
    result = _run_launcher(
        "stationary_builder",
        cwd=tmp_path,
        environment=environment,
    )
    assert result.returncode == 1, result.stdout
    assert "forbidden Python/native loader environment" in result.stdout
    assert "PYTHONPATH" in result.stdout
    assert not sentinel.exists()


def test_hostile_cwd_is_excluded_and_53_bit_ambient_context_is_recorded(
    tmp_path: Path,
) -> None:
    sentinel = tmp_path / "hostile-cwd-gmpy2-executed"
    (tmp_path / "gmpy2.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
        encoding="utf-8",
    )
    result = _run_launcher("stationary_builder", cwd=tmp_path)
    assert result.returncode == 0, result.stdout
    assert not sentinel.exists()
    authority = json.loads(AUTHORITY.read_text(encoding="ascii"))
    receipt = json.loads(
        (REPORT / authority["targets"]["stationary_builder"]["receipt_path"]).read_text(
            encoding="ascii"
        )
    )
    assert receipt["execution"]["cwd_excluded_from_sys_path"] is True
    assert receipt["execution"]["ambient_mpfr_precision_bits"] == 53
    assert receipt["execution"]["ambient_mpfr_rounding"] == "RoundToNearest"
    assert (
        receipt["artifact"]["sha256"]
        == authority["targets"]["stationary_builder"]["artifact_sha256"]
    )


@pytest.mark.parametrize("role", ("target source", "artifact probe"))
def test_descriptor_snapshot_detects_target_and_artifact_path_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    role: str,
) -> None:
    launcher = _load_launcher_module()
    path = tmp_path / "victim.bin"
    replacement = tmp_path / "replacement.bin"
    path.write_bytes(b"A" * 131_072)
    replacement.write_bytes(b"B" * 131_072)
    original_read = launcher.os.read
    attacked = False

    def replacing_read(descriptor: int, count: int) -> bytes:
        nonlocal attacked
        chunk = original_read(descriptor, count)
        if not attacked:
            attacked = True
            os.replace(replacement, path)
        return chunk

    monkeypatch.setattr(launcher.os, "read", replacing_read)
    with pytest.raises(
        launcher.AuthenticatedExecutionError,
        match="changed during read|path was replaced",
    ):
        launcher._stable_snapshot(path, role, 1_000_000)
    assert attacked
    assert path.read_bytes() == b"B" * 131_072


def test_symlink_and_strict_type_authority_mutations_fail_closed(
    tmp_path: Path,
) -> None:
    launcher = _load_launcher_module()
    regular = tmp_path / "regular.bin"
    regular.write_bytes(b"x")
    symlink = tmp_path / "symlink.bin"
    symlink.symlink_to(regular)
    with pytest.raises(
        launcher.AuthenticatedExecutionError,
        match="symbolic link",
    ):
        launcher._stable_snapshot(symlink, "symlink probe", 100)

    authority = json.loads(AUTHORITY.read_text(encoding="ascii"))
    mutation = copy.deepcopy(authority)
    mutation["claim_boundary"]["complete_C1"] = 0
    with pytest.raises(
        launcher.AuthenticatedExecutionError,
        match="claim boundary",
    ):
        launcher._validate_authority(mutation)


def test_validator_artifact_probe_rejects_builder_self_pin_mutation(
    tmp_path: Path,
) -> None:
    authority = json.loads(AUTHORITY.read_text(encoding="ascii"))
    artifact_path = REPORT / authority["targets"]["stationary_validator"]["artifact_path"]
    mutation = json.loads(artifact_path.read_text(encoding="ascii"))
    mutation["source_pins"]["builder_source"]["sha256"] = "0" * 64
    probe = tmp_path / "self-pin-mutation.json"
    probe.write_bytes(_canonical(mutation))
    result = _run_launcher(
        "stationary_validator",
        artifact_probe=probe,
        cwd=tmp_path,
    )
    assert result.returncode != 0, result.stdout
    assert "HOLD_PROBE" in result.stdout


def test_wrong_operator_launcher_digest_never_executes_launcher() -> None:
    result = subprocess.run(
        [
            str(PYTHON),
            "-I",
            "-S",
            "-c",
            BOOTSTRAP,
            str(LAUNCHER),
            "0" * 64,
            "--target",
            "stationary_builder",
        ],
        cwd=REPORT,
        env=_clean_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0
    assert "AssertionError" in result.stdout
