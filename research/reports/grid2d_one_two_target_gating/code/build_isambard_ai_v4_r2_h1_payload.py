#!/usr/bin/env python3
"""Build or verify the append-only v4-r2-h1 authority payload."""
from __future__ import annotations
import argparse
import hashlib
import os
import tempfile
from pathlib import Path
import build_isambard_ai_v4_r2_payload as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h1_payload.sha256"
BASE_PAYLOAD_SHA = "c6c77f62d05fb17c25160723f87324654041c2de484c3f4e12b2bf92bb8af404"
H1_MEMBERS = (
    "notes/isambard_ai_v4_r2_payload.sha256",
    "notes/isambard_ai_v4_r2_h1_authority_amendment.md",
    "code/analyze_gpu_gating_v4_r2_combined_h1.py",
    "code/build_isambard_ai_v4_r2_h1_payload.py",
    "code/independent_replay_gpu_gating_v4_r2_h1.py",
    "code/submit_isambard_ai_gating_v4_r2_h1.py",
    "code/test_isambard_ai_gating_v4_r2_h1.py",
    "code/verify_v3_release_for_v4_r2_h1.py",
    "code/isambard_ai_gating_v4_r2_combined_h1.sbatch",
    "code/isambard_ai_gating_v4_r2_fullnode_h1.sbatch",
    "code/isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch",
    "code/isambard_ai_gating_v4_r2_reduce_h1.sbatch",
    "code/isambard_ai_gating_v4_r2_replay_h1.sbatch",
)
MEMBERS = base.MEMBERS + H1_MEMBERS


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines() -> list[str]:
    if sha(ROOT / "notes/isambard_ai_v4_r2_payload.sha256") != BASE_PAYLOAD_SHA:
        raise ValueError("frozen base r2 payload manifest drift")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate h1 payload member")
    result = []
    for relative in MEMBERS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing/symlinked h1 payload member: {relative}")
        result.append(f"{sha(path)}  {relative}")
    return result


def verify() -> str:
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("h1 payload drift")
    return sha(OUT)


def build() -> str:
    if OUT.exists():
        raise FileExistsError("h1 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v4-r2-h1-payload.", dir=OUT.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, OUT)
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
