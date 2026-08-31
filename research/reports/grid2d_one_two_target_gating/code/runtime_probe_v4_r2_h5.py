#!/usr/bin/env python3
"""Build and validate the exact H5 release-job runtime receipt."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import runtime_probe_v4_r2_h4 as h4

HOST_MODULE = h4.HOST_MODULE
HOST_VERSION = h4.HOST_VERSION
CONTAINER_VERSION = h4.CONTAINER_VERSION
CONTAINER_IMPLEMENTATION = h4.CONTAINER_IMPLEMENTATION
CONTAINER_PATH = h4.CONTAINER_PATH
CONTAINER_SHA256 = h4.CONTAINER_SHA256
SCHEMA = "grid2d-one-two-target-gating-v4-r2-h5-runtime-v1"
STATUS = h4.STATUS
TOP_KEYS = h4.TOP_KEYS


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    return h4.sha(path)


def strict_json(path: Path) -> dict[str, Any]:
    return h4.strict_json(path)


def validate(value: Mapping[str, Any], *, phase: str, job_id: str) -> dict[str, Any]:
    req(set(value) == TOP_KEYS and value.get("schema") == SCHEMA,
        "H5 runtime exact schema/key drift")
    normalized = dict(value)
    normalized["schema"] = h4.SCHEMA
    h4.validate(normalized, phase=phase, job_id=job_id)
    return dict(value)


def validate_path(path: Path, *, phase: str, job_id: str) -> dict[str, Any]:
    return validate(strict_json(path), phase=phase, job_id=job_id)


def binding(path: Path, *, phase: str, job_id: str) -> dict[str, Any]:
    value = validate_path(path, phase=phase, job_id=job_id)
    return {"path": str(path), "sha256": sha(path), "receipt": value}


def build(*, phase: str, job_id: str, host_executable: str,
          host_version: str, loaded_modules: str, container: Path) -> dict[str, Any]:
    payload = h4.build(
        phase=phase, job_id=job_id, host_executable=host_executable,
        host_version=host_version, loaded_modules=loaded_modules,
        container=container,
    )
    payload["schema"] = SCHEMA
    return validate(payload, phase=phase, job_id=job_id)


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(not path.exists(), "H5 runtime receipt already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".runtime-h5.", dir=path.parent)
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
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": sha(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
