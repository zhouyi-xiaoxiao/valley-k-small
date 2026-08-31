#!/usr/bin/env python3
"""Build or verify the append-only content-addressed v4-r2 H5 payload."""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h4_payload as h4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h5_payload.sha256"
H4_PAYLOAD_SHA256 = "441032dda489ce206b3ddec09925b53184e036248e7b393d2120ea1a5dbd47cf"
H5_MEMBERS = (
    "notes/isambard_ai_v4_r2_h4_payload.sha256",
    "notes/isambard_ai_v4_r2_h5_terminal_authority_amendment.md",
    "notes/isambard_ai_v4_r2_h5_independent_terminal_audit.md",
    "code/build_isambard_ai_v4_r2_h5_payload.py",
    "code/isambard_ai_gating_v4_r2_release_h5.sbatch",
    "code/provision_gpu_gating_v4_r2_h5.py",
    "code/runtime_probe_v4_r2_h5.py",
    "code/submit_isambard_ai_gating_v4_r2_h5.py",
    "code/terminal_audit_gpu_gating_v4_r2_h5.py",
    "code/test_isambard_ai_gating_v4_r2_h5.py",
)
MEMBERS = h4.MEMBERS + H5_MEMBERS


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines() -> list[str]:
    if h4.verify() != H4_PAYLOAD_SHA256:
        raise ValueError("frozen H4 payload manifest/member drift")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate H5 payload member")
    result = []
    for relative in MEMBERS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing/symlinked H5 payload member: {relative}")
        result.append(f"{sha(path)}  {relative}")
    return result


def verify() -> str:
    stat = OUT.lstat()
    if (not OUT.is_file() or OUT.is_symlink() or stat.st_nlink != 1
            or stat.st_mode & 0o777 != 0o600):
        raise ValueError("unsafe H5 payload manifest")
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("H5 payload drift")
    return sha(OUT)


def build() -> str:
    if OUT.exists() or OUT.is_symlink():
        raise FileExistsError("H5 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(
        prefix=".v4-r2-h5-payload.", dir=OUT.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, OUT)
    finally:
        temporary.unlink(missing_ok=True)
    return verify()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    print(verify() if args.verify else build())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
