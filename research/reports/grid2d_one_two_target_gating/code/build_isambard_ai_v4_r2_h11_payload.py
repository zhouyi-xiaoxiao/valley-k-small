#!/usr/bin/env python3
"""Build append-only H11 payload over immutable H10; detached controller is excluded."""
import hashlib
import os
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h10_payload as h10

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h11_payload.sha256"
H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
NEW = (
    "notes/isambard_ai_v4_r2_h10_payload.sha256",
    "notes/isambard_ai_v4_r2_h11_recovery_authority_amendment.md",
    "code/h11_runtime_v4_r2.py",
    "code/build_isambard_ai_v4_r2_h11_payload.py",
    "code/test_isambard_ai_gating_v4_r2_h11.py",
)
MEMBERS = h10.MEMBERS + NEW


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def lines():
    if (
        h10.verify() != H10_SHA
        or tuple(MEMBERS[: len(h10.MEMBERS)]) != tuple(h10.MEMBERS)
        or len(MEMBERS) != len(set(MEMBERS))
    ):
        raise ValueError("frozen H10 append-only drift")
    return [f"{sha(ROOT / name)}  {name}" for name in MEMBERS]


def candidate_bytes():
    return ("\n".join(lines()) + "\n").encode()


def candidate_sha():
    return hashlib.sha256(candidate_bytes()).hexdigest()


def verify():
    if OUT.read_bytes() != candidate_bytes():
        raise ValueError("H11 payload drift")
    return sha(OUT)


def build():
    if OUT.exists() or OUT.is_symlink():
        raise FileExistsError("H11 append-only")
    descriptor, name = tempfile.mkstemp(prefix=".h11-manifest.", dir=OUT.parent)
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
