#!/usr/bin/env python3
"""Build append-only H12 payload over immutable H11; detached controller is excluded."""
import hashlib
import os
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h11_payload as h11

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h12_payload.sha256"
H11_SHA = "dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca"
NEW = (
    "notes/isambard_ai_v4_r2_h11_payload.sha256",
    "notes/isambard_ai_v4_r2_h12_environment_authority_amendment.md",
    "code/h12_runtime_v4_r2.py",
    "code/build_isambard_ai_v4_r2_h12_payload.py",
    "code/test_isambard_ai_gating_v4_r2_h12.py",
)
MEMBERS = h11.MEMBERS + NEW


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def lines():
    if (
        h11.verify() != H11_SHA
        or tuple(MEMBERS[: len(h11.MEMBERS)]) != tuple(h11.MEMBERS)
        or len(MEMBERS) != len(set(MEMBERS))
    ):
        raise ValueError("frozen H11 append-only drift")
    return [f"{sha(ROOT / name)}  {name}" for name in MEMBERS]


def candidate_bytes():
    return ("\n".join(lines()) + "\n").encode()


def candidate_sha():
    return hashlib.sha256(candidate_bytes()).hexdigest()


def verify():
    if OUT.read_bytes() != candidate_bytes():
        raise ValueError("H12 payload drift")
    return sha(OUT)


def build():
    if OUT.exists() or OUT.is_symlink():
        raise FileExistsError("H12 append-only")
    descriptor, name = tempfile.mkstemp(prefix=".h12-manifest.", dir=OUT.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(candidate_bytes())
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, OUT)
    finally:
        temporary.unlink(missing_ok=True)
    return verify()


if __name__ == "__main__":
    print(verify() if OUT.exists() else build())
