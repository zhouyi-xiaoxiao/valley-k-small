"""Tests proving that the rejected v1 probe is an inert HOLD sentinel."""

from __future__ import annotations

import builtins
import importlib
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest
import validate_continuum_c1_n0_runtime_origin_probe_v1 as probe

SCRIPT = Path(probe.__file__).resolve()


class HostilePath:
    """An argument whose every observation would fail the test."""

    def __fspath__(self) -> str:
        raise AssertionError("spec path was converted with os.fspath")

    def __str__(self) -> str:
        raise AssertionError("spec path was converted to text")

    def __getattribute__(self, name: str):
        if name.startswith("__") and name in {
            "__class__",
            "__enter__",
            "__exit__",
            "__fspath__",
            "__str__",
        }:
            return object.__getattribute__(self, name)
        raise AssertionError(f"spec path attribute was observed: {name}")


def _forbid(*args, **kwargs):
    del args, kwargs
    raise AssertionError("forbidden filesystem, import, or process hook was called")


def test_public_api_is_one_exact_failure_without_observing_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(builtins, "open", _forbid)
    monkeypatch.setattr(os, "stat", _forbid)
    monkeypatch.setattr(os, "lstat", _forbid)
    monkeypatch.setattr(os, "readlink", _forbid)
    monkeypatch.setattr(Path, "resolve", _forbid)
    monkeypatch.setattr(Path, "exists", _forbid)
    monkeypatch.setattr(Path, "read_bytes", _forbid)
    monkeypatch.setattr(importlib, "import_module", _forbid)
    monkeypatch.setattr(subprocess, "Popen", _forbid)
    monkeypatch.setattr(subprocess, "run", _forbid)
    monkeypatch.setattr(builtins, "__import__", _forbid)

    with pytest.raises(probe.ProbeFailure) as captured:
        probe.validate_runtime_origin_probe(HostilePath())

    assert str(captured.value) + "\n" == probe.HOLD_LINE
    assert captured.value.args == (probe.HOLD_LINE[:-1],)


@pytest.mark.parametrize(
    "argv",
    [
        None,
        [],
        ["--spec", "/definitely/not/present.json"],
        ["--spec"],
        ["--unknown"],
        ["-h"],
        ["--help"],
        ["--spec", ""],
        ["--spec", "../../malformed/../path"],
    ],
)
def test_direct_main_invocation_matrix_is_exact_hold(
    argv: list[str] | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr(probe.sys, "stdout", stdout)
    monkeypatch.setattr(probe.sys, "stderr", stderr)
    monkeypatch.setattr(builtins, "open", _forbid)
    monkeypatch.setattr(os, "stat", _forbid)
    monkeypatch.setattr(os, "lstat", _forbid)
    monkeypatch.setattr(Path, "resolve", _forbid)
    monkeypatch.setattr(importlib, "import_module", _forbid)
    monkeypatch.setattr(subprocess, "Popen", _forbid)
    monkeypatch.setattr(subprocess, "run", _forbid)
    monkeypatch.setattr(builtins, "__import__", _forbid)

    assert probe.main(argv) == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == probe.HOLD_LINE


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--spec", "/definitely/not/present.json"],
        ["--spec"],
        ["--unknown"],
        ["-h"],
        ["--help"],
        ["--spec", ""],
        ["--spec", "../../malformed/../path"],
    ],
)
def test_process_invocation_matrix_is_exact_hold(arguments: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        env={"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    assert completed.returncode == 2
    assert completed.stdout == b""
    assert completed.stderr == probe.HOLD_LINE.encode("ascii")


def test_rejected_draft_exports_no_pass_or_child_surface() -> None:
    assert probe.STATUS == "REJECTED_DRAFT_ROUND182_NO_RUNTIME_TRUTH"
    assert probe.HOST_RUNTIME_BYTE_COMPLETE is False
    assert probe.EXECUTABLE_VALIDATION_PATH_PRESENT is False
    assert not hasattr(probe, "PASS_STATUS")
    assert not hasattr(probe, "CHILD_PROGRAM")
    assert not hasattr(probe, "_run_child_once")
    assert not hasattr(probe, "subprocess")
    assert not hasattr(probe, "Path")
