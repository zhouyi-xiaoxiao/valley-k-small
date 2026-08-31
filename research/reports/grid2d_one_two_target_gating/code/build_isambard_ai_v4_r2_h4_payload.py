#!/usr/bin/env python3
"""Build or verify the append-only content-addressed v4-r2 H4 payload."""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h3_payload as h3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes/isambard_ai_v4_r2_h4_payload.sha256"
H3_PAYLOAD_SHA256 = "df399e156545935ccaa0d5d5a73b8c3f8f32227f8889ffe55b34662630adf1f2"
H4_MEMBERS = (
    "notes/isambard_ai_v4_r2_h3_payload.sha256",
    "notes/isambard_ai_v4_r2_h4_authority_amendment.md",
    "notes/isambard_ai_v4_r2_h4_independent_repair_audit.md",
    "code/analyze_gpu_gating_v4_r2_combined_h4.py",
    "code/build_isambard_ai_v4_r2_h4_payload.py",
    "code/finalize_gpu_gating_v4_r2_h4.py",
    "code/independent_replay_gpu_gating_v4_r2_h4.py",
    "code/runtime_probe_v4_r2_h4.py",
    "code/submit_isambard_ai_gating_v4_r2_h4.py",
    "code/test_isambard_ai_gating_v4_r2_h4.py",
    "code/verify_gpu_canary_v4_r2_h4.py",
    "code/verify_v3_release_for_v4_r2_h4.py",
    "code/isambard_ai_gating_v4_r2_combined_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_reduce_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_release_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_replay_h4.sbatch",
    "code/isambard_ai_gating_v4_r2_v3_authority_h4.sbatch",
)
MEMBERS = h3.MEMBERS + H4_MEMBERS


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines() -> list[str]:
    if sha(ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256") \
            != H3_PAYLOAD_SHA256:
        raise ValueError("frozen H3 payload manifest drift")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate H4 payload member")
    result = []
    for relative in MEMBERS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing/symlinked H4 payload member: {relative}")
        result.append(f"{sha(path)}  {relative}")
    return result


def verify() -> str:
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("H4 payload drift")
    return sha(OUT)


def build() -> str:
    if OUT.exists():
        raise FileExistsError("H4 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v4-r2-h4-payload.",
                                        dir=OUT.parent)
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
