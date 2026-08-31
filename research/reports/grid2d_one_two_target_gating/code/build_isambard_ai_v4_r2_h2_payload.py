#!/usr/bin/env python3
"""Build/verify the append-only v4-r2 H2 authority payload manifest."""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h1_payload as h1

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256"
H1_PAYLOAD_SHA256 = "29949d276b04e6ebecdba3a3e0891a8f0ad6895cf6857822956395bff0eac76e"
H2_MEMBERS = (
    "notes/isambard_ai_v4_r2_h1_payload.sha256",
    "notes/isambard_ai_v4_r2_h2_authority_amendment.md",
    "notes/isambard_ai_v4_r2_h2_pack_heterogeneity_contract.json",
    "code/analyze_gpu_gating_v4_r2_combined_h2.py",
    "code/build_isambard_ai_v4_r2_h2_payload.py",
    "code/finalize_gpu_gating_v4_r2_h2.py",
    "code/independent_replay_gpu_gating_v4_r2_h2.py",
    "code/runtime_probe_v4_r2_h2.py",
    "code/scientific_tail_replay_v4_r2_h2.py",
    "code/submit_isambard_ai_gating_v4_r2_h2.py",
    "code/test_isambard_ai_gating_v4_r2_h2.py",
    "code/verify_gpu_canary_v4_r2_h2.py",
    "code/verify_v3_release_for_v4_r2_h2.py",
    "code/isambard_ai_gating_v4_r2_combined_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_fullnode_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_gpu_canary_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_reduce_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_release_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_replay_h2.sbatch",
    "code/isambard_ai_gating_v4_r2_v3_authority_h2.sbatch",
)
MEMBERS = h1.MEMBERS + H2_MEMBERS


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines() -> list[str]:
    if sha(ROOT / "notes/isambard_ai_v4_r2_h1_payload.sha256") != H1_PAYLOAD_SHA256:
        raise ValueError("frozen H1 payload manifest drift")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate H2 payload member")
    result: list[str] = []
    for relative in MEMBERS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing/symlinked H2 payload member: {relative}")
        result.append(f"{sha(path)}  {relative}")
    return result


def verify() -> str:
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("H2 payload drift")
    return sha(OUT)


def build() -> str:
    if OUT.exists():
        raise FileExistsError("H2 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v4-r2-h2-payload.", dir=OUT.parent)
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
