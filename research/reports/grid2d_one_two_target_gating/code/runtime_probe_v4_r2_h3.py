#!/usr/bin/env python3
"""Bind the pinned Cray host Python and pinned SIF Python for every H3 phase."""
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

HOST_MODULE = "cray-python/3.11.7"
HOST_VERSION = "3.11.7"
CONTAINER_VERSION = "3.12.11"
CONTAINER_SHA256 = "aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4"


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(*, phase: str, job_id: str, host_executable: str,
          host_version: str, loaded_modules: str, container: Path) -> dict[str, object]:
    req(re.fullmatch(r"[a-z0-9_-]+", phase) is not None,
        "runtime phase is not canonical")
    req(job_id.isdecimal(), "runtime Slurm job ID is not decimal")
    modules = [item for item in loaded_modules.split(":") if item]
    req(host_version == HOST_VERSION and HOST_MODULE in modules,
        "host runtime is not the pinned cray-python/3.11.7 module")
    req(Path(host_executable).is_absolute()
        and "python" in Path(host_executable).name.lower(),
        "host Python executable is not an absolute Python path")
    container_version = platform.python_version()
    req(container_version == CONTAINER_VERSION,
        "SIF Python version is not the frozen 3.12.11 runtime")
    req(sha(container) == CONTAINER_SHA256, "SIF SHA-256 drift")
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-h3-runtime-v1",
        "status": "PASS_PINNED_HOST_AND_SIF_PYTHON",
        "phase": phase, "slurm_job_id": job_id,
        "host_python": {
            "module": HOST_MODULE, "version": host_version,
            "executable": host_executable,
            "loaded_modules_exact_contains_pin": True,
        },
        "container_python": {
            "version": container_version,
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "container": {"path": str(container), "sha256": CONTAINER_SHA256},
    }


def commit(path: Path, payload: dict[str, object]) -> None:
    req(not path.exists(), "H3 runtime receipt already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".runtime-h3.", dir=path.parent)
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
