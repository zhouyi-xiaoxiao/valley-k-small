#!/usr/bin/env python3
"""Build or verify the exact append-only v4 payload SHA-256 inventory."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import tempfile
from pathlib import Path

REPORT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPORT_ROOT / "notes/isambard_ai_v4_payload.sha256"
MEMBERS = (
    "artifacts/data/disorder_field_pack_v4.npz",
    "artifacts/data/disorder_field_pack_v4.manifest.json",
    "artifacts/data/gating_v4_production_manifest.json",
    "code/analyze_gpu_gating_v4_combined.py",
    "code/build_gating_campaign_manifest_v4.py",
    "code/generate_disorder_field_pack_v4.py",
    "code/gpu_gating_mc_v3.py",
    "code/gpu_gating_mc_v4.py",
    "code/isambard_ai_gating_v4_combined.sbatch",
    "code/isambard_ai_gating_v4_fullnode.sbatch",
    "code/isambard_ai_gating_v4_reduce.sbatch",
    "code/reduce_gpu_gating_v3.py",
    "code/reduce_gpu_gating_v4.py",
    "code/test_isambard_ai_gating_v4.py",
    "code/validate_gating_campaign_manifest_v4.py",
    "notes/isambard_ai_v4_fullnode_expansion_preregistered_protocol.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_lines(root: Path) -> list[str]:
    lines = []
    for relative in MEMBERS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing or symlinked payload member: {relative}")
        lines.append(f"{sha256(path)}  {relative}")
    return lines


def verify(output: Path, root: Path = REPORT_ROOT) -> str:
    if not output.is_file() or output.is_symlink():
        raise ValueError("payload manifest missing or symlinked")
    lines = output.read_text(encoding="utf-8").splitlines()
    if lines != expected_lines(root):
        raise ValueError("payload manifest exact ordered inventory/hash drift")
    for line in lines:
        if re.fullmatch(r"[0-9a-f]{64}  [A-Za-z0-9_./-]+", line) is None:
            raise ValueError("malformed payload line")
    return sha256(output)


def build(output: Path, root: Path = REPORT_ROOT) -> str:
    if output.exists():
        raise FileExistsError("v4 payload manifest is append-only")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = ("\n".join(expected_lines(root)) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle: handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, output)
    finally: temporary.unlink(missing_ok=True)
    return verify(output, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    digest = verify(args.output.absolute()) if args.verify else build(args.output.absolute())
    print(digest); return 0


if __name__ == "__main__":
    raise SystemExit(main())
