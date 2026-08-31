"""Semantic and file-boundary mutations for method registry v3."""

from __future__ import annotations

import copy
import errno
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
VALIDATOR = REPORT / "code/validate_continuum_c1_c2_n0_method_parameter_registry_v3_candidate.py"
BUILDER = REPORT / "code/build_continuum_c1_c2_n0_method_parameter_registry_v3_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
DOMAIN = "encounter-outward-method-parameters-v3"
Mutation = Callable[[dict[str, Any]], None]


def load_module(path: Path, name: str) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        specification.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def digest(parameters: dict[str, Any]) -> str:
    return hashlib.sha256(DOMAIN.encode("ascii") + b"\0" + canonical(parameters)).hexdigest()


def source() -> dict[str, Any]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return subprocess.run(
        [sys.executable, "-I", "-B", str(VALIDATOR), "--artifact", str(path)],
        cwd=REPORT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def mutate_file(tmp_path: Path, mutate: Mutation) -> Path:
    value = copy.deepcopy(source())
    mutate(value)
    path = tmp_path / "registry.json"
    path.write_bytes(canonical(value))
    return path


def coherently_change_record(index: int) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        record = value["parameters"][index]
        record["parameters"]["uncommitted_extra_parameter"] = index
        record["method_parameter_sha256"] = digest(record["parameters"])

    return mutate


@pytest.mark.parametrize("index", range(10))
def test_rejects_coherently_redigested_change_to_every_record(
    tmp_path: Path,
    index: int,
) -> None:
    result = run_validator(mutate_file(tmp_path, coherently_change_record(index)))
    assert result.returncode != 0, result.stdout
    assert "method parameter record semantic drift" in result.stderr


ATTACKS: list[tuple[str, Mutation]] = [
    (
        "raw_precision",
        lambda value: (
            value["parameters"][2]["parameters"].__setitem__("precision_bits", 7),
            value["parameters"][2].__setitem__(
                "method_parameter_sha256",
                digest(value["parameters"][2]["parameters"]),
            ),
        ),
    ),
    (
        "sentinel_relation",
        lambda value: value["parameters"][1]["parameters"].__setitem__(
            "containment_relation",
            "overlap_only",
        ),
    ),
    (
        "reorder",
        lambda value: value["parameters"].__setitem__(
            slice(0, 2),
            list(reversed(value["parameters"][:2])),
        ),
    ),
    (
        "count",
        lambda value: value.__setitem__("parameter_count", 9),
    ),
    (
        "claim",
        lambda value: value["claim_boundary"].__setitem__("complete_C1", True),
    ),
    (
        "outcome_key",
        lambda value: value["parameters"][0]["parameters"].__setitem__(
            "expected_result_sha256",
            "0" * 64,
        ),
    ),
    (
        "status",
        lambda value: value.__setitem__(
            "status",
            "EXTERNALLY_COMMITTED",
        ),
    ),
]


@pytest.mark.parametrize(
    ("name", "mutate"),
    ATTACKS,
    ids=[name for name, _ in ATTACKS],
)
def test_rejects_registry_mutations(
    tmp_path: Path,
    name: str,
    mutate: Mutation,
) -> None:
    assert name
    result = run_validator(mutate_file(tmp_path, mutate))
    assert result.returncode != 0, result.stdout
    assert "ERROR MethodParameterRegistryV3CandidateValidation:" in result.stderr


def test_rejects_duplicate_key(tmp_path: Path) -> None:
    attacked = ARTIFACT.read_bytes().replace(
        b'{\n  "claim_boundary": {',
        b'{\n  "schema": "duplicate",\n  "claim_boundary": {',
        1,
    )
    path = tmp_path / "duplicate.json"
    path.write_bytes(attacked)
    result = run_validator(path)
    assert result.returncode != 0
    assert "strict JSON decoding failed" in result.stderr


def test_deep_json_fails_without_traceback(tmp_path: Path) -> None:
    path = tmp_path / "deep.json"
    path.write_bytes(b'{"x":' + b"[" * 5000 + b"0" + b"]" * 5000 + b"}\n")
    result = run_validator(path)
    assert result.returncode != 0
    assert "ERROR MethodParameterRegistryV3CandidateValidation:" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_symlink_hardlink_and_fifo(tmp_path: Path) -> None:
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(ARTIFACT)
    assert run_validator(symlink).returncode != 0

    clone = tmp_path / "clone.json"
    clone.write_bytes(ARTIFACT.read_bytes())
    hardlink = tmp_path / "hardlink.json"
    os.link(clone, hardlink)
    assert run_validator(hardlink).returncode != 0

    fifo = tmp_path / "registry.fifo"
    os.mkfifo(fifo)
    assert run_validator(fifo).returncode != 0


@pytest.mark.parametrize(
    ("module_path", "function_name"),
    [
        (BUILDER, "read_regular"),
        (VALIDATOR, "snapshot"),
    ],
)
def test_component_anchored_read_rejects_parent_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_path: Path,
    function_name: str,
) -> None:
    module = load_module(module_path, f"registry_parent_{function_name}")
    live = tmp_path / "live"
    live.mkdir()
    source_path = live / "registry.json"
    source_path.write_bytes(b"ORIGINAL")
    displaced = tmp_path / "displaced"
    alternate = tmp_path / "alternate"
    alternate.mkdir()
    (alternate / "registry.json").write_bytes(b"REDIRECTED")
    real_read = module.os.read
    swapped = False

    def swap_then_read(descriptor: int, count: int) -> bytes:
        nonlocal swapped
        if not swapped:
            live.rename(displaced)
            live.symlink_to(alternate, target_is_directory=True)
            swapped = True
        return real_read(descriptor, count)

    monkeypatch.setattr(module.os, "read", swap_then_read)
    with pytest.raises((OSError, ValueError, RuntimeError)):
        getattr(module, function_name)(source_path)


def test_failed_partial_publication_leaves_no_final_or_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_partial_publication")
    output = tmp_path / "registry.json"
    real_write = module.os.write
    calls = 0

    def short_then_fail(descriptor: int, payload: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_write(descriptor, payload[:7])
        raise OSError(errno.ENOSPC, "injected no space")

    monkeypatch.setattr(module.os, "write", short_then_fail)
    with pytest.raises(OSError):
        module.publish_no_replace(output, b"x" * 100)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))
