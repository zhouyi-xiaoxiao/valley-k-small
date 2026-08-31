#!/usr/bin/env python3
"""Write an append-only host/container Python runtime authority receipt."""
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

CONTAINER_SHA256 = "aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4"
VERSION = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION.fullmatch(value)
    req(match is not None, f"invalid Python version: {value}")
    return tuple(map(int, match.groups()))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(phase: str, job_id: str, host_version: str,
          container: Path) -> dict[str, object]:
    req(re.fullmatch(r"[a-z0-9_-]+", phase) is not None,
        "runtime phase is not canonical")
    req(job_id.isdecimal(), "runtime job ID is not decimal")
    host_tuple = parse_version(host_version)
    container_version = platform.python_version()
    container_tuple = parse_version(container_version)
    req(host_tuple >= (3, 10, 0), "host Python is below 3.10")
    req(container_tuple >= (3, 10, 0), "container Python is below 3.10")
    req(sha(container) == CONTAINER_SHA256, "container image SHA drift")
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-h2-runtime-v1",
        "status": "PASS_FIXED_CONTAINER_PYTHON_GE_3_10",
        "phase": phase,
        "slurm_job_id": job_id,
        "host_python": {"version": host_version, "minimum_satisfied": True},
        "container_python": {
            "version": container_version,
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "minimum_satisfied": True,
        },
        "container": {"path": str(container), "sha256": CONTAINER_SHA256},
    }


def commit(path: Path, payload: dict[str, object]) -> None:
    req(not path.exists(), "runtime receipt already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".runtime-h2.", dir=path.parent)
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
    parser.add_argument("--host-python-version", required=True)
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build(args.phase, args.job_id, args.host_python_version,
                        args.container)
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": sha(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
