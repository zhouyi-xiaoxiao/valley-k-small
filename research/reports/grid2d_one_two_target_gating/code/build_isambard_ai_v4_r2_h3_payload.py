#!/usr/bin/env python3
"""Build/verify the append-only v4-r2 H3 authority payload."""
from __future__ import annotations
import argparse
import hashlib
import os
import tempfile
from pathlib import Path
import build_isambard_ai_v4_r2_h2_payload as h2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256"
H2_PAYLOAD_SHA256 = "1dd32b6c5a1786b3e1c2d0d587c0e4219ab894b96f132c94c391804f9e970aec"
H3_MEMBERS = (
    "notes/isambard_ai_v4_r2_h2_payload.sha256",
    "notes/isambard_ai_v4_r2_h3_authority_amendment.md",
    "code/analyze_gpu_gating_v4_r2_combined_h3.py",
    "code/build_isambard_ai_v4_r2_h3_payload.py",
    "code/finalize_gpu_gating_v4_r2_h3.py",
    "code/independent_replay_gpu_gating_v4_r2_h3.py",
    "code/runtime_probe_v4_r2_h3.py",
    "code/scientific_primary_replay_v4_r2_h3.py",
    "code/submit_isambard_ai_gating_v4_r2_h3.py",
    "code/test_isambard_ai_gating_v4_r2_h3.py",
    "code/verify_gpu_canary_v4_r2_h3.py",
    "code/verify_v3_release_for_v4_r2_h3.py",
    "code/isambard_ai_gating_v4_r2_combined_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_fullnode_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_gpu_canary_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_reduce_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_release_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_replay_h3.sbatch",
    "code/isambard_ai_gating_v4_r2_v3_authority_h3.sbatch",
)
MEMBERS = h2.MEMBERS + H3_MEMBERS


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines() -> list[str]:
    if sha(ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256") != H2_PAYLOAD_SHA256:
        raise ValueError("frozen H2 payload manifest drift")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate H3 payload member")
    result = []
    for relative in MEMBERS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing/symlinked H3 payload member: {relative}")
        result.append(f"{sha(path)}  {relative}")
    return result


def verify() -> str:
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("H3 payload drift")
    return sha(OUT)


def build() -> str:
    if OUT.exists(): raise FileExistsError("H3 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v4-r2-h3-payload.", dir=OUT.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, OUT)
    finally: temporary.unlink(missing_ok=True)
    return verify()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true"); args = parser.parse_args()
    print(verify() if args.verify else build()); return 0


if __name__ == "__main__": raise SystemExit(main())
