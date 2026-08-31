#!/usr/bin/env python3
"""Build and independently validate the exact H4 host/SIF runtime receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

HOST_MODULE = "cray-python/3.11.7"
HOST_VERSION = "3.11.7"
CONTAINER_VERSION = "3.12.11"
CONTAINER_IMPLEMENTATION = "CPython"
CONTAINER_PATH = Path(
    "/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
)
CONTAINER_SHA256 = "aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4"
SCHEMA = "grid2d-one-two-target-gating-v4-r2-h4-runtime-v1"
STATUS = "PASS_PINNED_HOST_AND_SIF_PYTHON"
TOP_KEYS = {
    "schema", "status", "phase", "slurm_job_id", "host_python",
    "container_python", "container",
}
HOST_KEYS = {
    "module", "version", "executable", "loaded_modules_exact_contains_pin",
}
CONTAINER_PYTHON_KEYS = {"version", "implementation", "executable"}
CONTAINER_KEYS = {"path", "sha256"}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_json(path: Path) -> dict[str, Any]:
    stat = path.lstat()
    req(path.is_file() and not path.is_symlink() and stat.st_nlink == 1
        and stat.st_mode & 0o777 == 0o600,
        f"unsafe H4 runtime receipt: {path}")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            req(key not in result, f"duplicate H4 runtime key: {key}")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite H4 runtime token: {token}")),
    )
    req(isinstance(value, dict), "H4 runtime root is not an object")
    return value


def validate(value: Mapping[str, Any], *, phase: str, job_id: str) -> dict[str, Any]:
    """Fail closed on every runtime field, not merely status/phase/job."""
    req(set(value) == TOP_KEYS and value["schema"] == SCHEMA
        and value["status"] == STATUS and value["phase"] == phase
        and value["slurm_job_id"] == job_id,
        "H4 runtime envelope drift")
    req(re.fullmatch(r"[a-z0-9_]+", phase) is not None and job_id.isdecimal(),
        "H4 runtime phase/job is not canonical")
    host = value["host_python"]
    req(isinstance(host, dict) and set(host) == HOST_KEYS
        and host["module"] == HOST_MODULE and host["version"] == HOST_VERSION
        and host["loaded_modules_exact_contains_pin"] is True,
        "H4 host Python module/version binding drift")
    host_executable = Path(host["executable"])
    req(host_executable.is_absolute()
        and "python" in host_executable.name.lower(),
        "H4 host Python executable binding drift")
    container_python = value["container_python"]
    req(isinstance(container_python, dict)
        and set(container_python) == CONTAINER_PYTHON_KEYS
        and container_python["version"] == CONTAINER_VERSION
        and container_python["implementation"] == CONTAINER_IMPLEMENTATION,
        "H4 SIF Python identity drift")
    container_executable = Path(container_python["executable"])
    req(container_executable.is_absolute()
        and "python" in container_executable.name.lower(),
        "H4 SIF Python executable drift")
    container = value["container"]
    req(isinstance(container, dict) and set(container) == CONTAINER_KEYS
        and container == {
            "path": str(CONTAINER_PATH), "sha256": CONTAINER_SHA256,
        }, "H4 SIF path/SHA binding drift")
    return dict(value)


def validate_path(path: Path, *, phase: str, job_id: str) -> dict[str, Any]:
    return validate(strict_json(path), phase=phase, job_id=job_id)


def binding(path: Path, *, phase: str, job_id: str) -> dict[str, Any]:
    value = validate_path(path, phase=phase, job_id=job_id)
    return {"path": str(path), "sha256": sha(path), "receipt": value}


def build(*, phase: str, job_id: str, host_executable: str,
          host_version: str, loaded_modules: str, container: Path) -> dict[str, Any]:
    req(container == CONTAINER_PATH and sha(container) == CONTAINER_SHA256,
        "H4 SIF path/SHA drift")
    modules = [item for item in loaded_modules.split(":") if item]
    req(host_version == HOST_VERSION and HOST_MODULE in modules,
        "H4 host runtime is not pinned cray-python/3.11.7")
    payload = {
        "schema": SCHEMA, "status": STATUS, "phase": phase,
        "slurm_job_id": job_id,
        "host_python": {
            "module": HOST_MODULE, "version": host_version,
            "executable": host_executable,
            "loaded_modules_exact_contains_pin": True,
        },
        "container_python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "container": {"path": str(container), "sha256": CONTAINER_SHA256},
    }
    return validate(payload, phase=phase, job_id=job_id)


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(not path.exists(), "H4 runtime receipt already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".runtime-h4.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--host-python-executable", required=True)
    parser.add_argument("--host-python-version", required=True)
    parser.add_argument("--loaded-modules", required=True)
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build(
            phase=args.phase, job_id=args.job_id,
            host_executable=args.host_python_executable,
            host_version=args.host_python_version,
            loaded_modules=args.loaded_modules, container=args.container,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": sha(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
