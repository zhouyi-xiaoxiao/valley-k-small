#!/usr/bin/env python3
"""Build and verify the append-only closed-world v4-r2 H7 payload."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import tempfile
from pathlib import Path

import build_isambard_ai_v4_r2_h6_payload as h6

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELATIVE = "notes/isambard_ai_v4_r2_h7_payload.sha256"
OUT = ROOT / MANIFEST_RELATIVE
H6_PAYLOAD_SHA256 = (
    "79a61ac2d24e2ff62e50cbf18fd191007eb535652bcb859dc173ebe0376a7d3b"
)
V3_PACK_RELATIVE = "artifacts/data/disorder_field_pack_v3.npz"
V3_PACK_SHA256 = (
    "d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420"
)
H7_MEMBERS = (
    "notes/isambard_ai_v4_r2_h6_payload.sha256",
    V3_PACK_RELATIVE,
    "notes/isambard_ai_v4_r2_h7_closed_world_packaging_amendment.md",
    "code/build_isambard_ai_v4_r2_h7_payload.py",
    "code/test_isambard_ai_gating_v4_r2_h7.py",
)
MEMBERS = h6.MEMBERS + H7_MEMBERS
HEX64 = re.compile(r"[0-9a-f]{64}")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_regular(path: Path, *, mode600: bool) -> os.stat_result:
    metadata = path.lstat()
    req(stat.S_ISREG(metadata.st_mode) and not path.is_symlink(),
        f"non-regular or symlinked H7 member: {path}")
    req(metadata.st_nlink == 1, f"H7 member link-count drift: {path}")
    if mode600:
        req(stat.S_IMODE(metadata.st_mode) == 0o600,
            f"H7 member mode drift: {path}")
    return metadata


def validate_member_names() -> None:
    req(len(MEMBERS) == 118 and len(MEMBERS) == len(set(MEMBERS)),
        "H7 payload member count/uniqueness drift")
    req(tuple(MEMBERS[:len(h6.MEMBERS)]) == tuple(h6.MEMBERS),
        "H7 is not an append-only extension of H6")
    for relative in MEMBERS:
        path = Path(relative)
        req(not path.is_absolute() and ".." not in path.parts
            and path.as_posix() == relative,
            f"unsafe H7 relative member: {relative}")


def lines() -> list[str]:
    validate_member_names()
    req(h6.verify() == H6_PAYLOAD_SHA256,
        "frozen H6 payload manifest/member drift")
    req(sha(ROOT / V3_PACK_RELATIVE) == V3_PACK_SHA256,
        "frozen v3 field-pack drift")
    result: list[str] = []
    for relative in MEMBERS:
        path = ROOT / relative
        safe_regular(path, mode600=False)
        result.append(f"{sha(path)}  {relative}")
    return result


def parse_manifest(path: Path, *, mode600: bool) -> list[tuple[str, str]]:
    safe_regular(path, mode600=mode600)
    raw = path.read_bytes()
    req(raw.endswith(b"\n") and b"\r" not in raw,
        "H7 manifest newline/canonical-byte drift")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("H7 manifest is not UTF-8") from error
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)", line)
        req(match is not None, "H7 manifest row-shape drift")
        digest, relative = match.groups()
        rows.append((digest, relative))
    req([relative for _, relative in rows] == list(MEMBERS),
        "H7 manifest ordered inventory drift")
    req(len({relative for _, relative in rows}) == len(rows),
        "H7 manifest duplicate member")
    return rows


def verify() -> str:
    if OUT.read_text(encoding="utf-8").splitlines() != lines():
        raise ValueError("H7 payload drift")
    safe_regular(OUT, mode600=True)
    parse_manifest(OUT, mode600=True)
    return sha(OUT)


def expected_directories() -> set[str]:
    result: set[str] = set()
    for relative in (*MEMBERS, MANIFEST_RELATIVE):
        parent = Path(relative).parent
        while parent != Path("."):
            result.add(parent.as_posix())
            parent = parent.parent
    return result


def _closed_world_inventory(root: Path) -> tuple[set[str], set[str]]:
    root_metadata = root.lstat()
    req(stat.S_ISDIR(root_metadata.st_mode) and not root.is_symlink(),
        "H7 closed-world root missing/symlinked")
    req(stat.S_IMODE(root_metadata.st_mode) == 0o700,
        "H7 closed-world root mode drift")
    members: set[str] = set()
    observed_directories: set[str] = set()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directories:
            directory = current_path / name
            metadata = directory.lstat()
            req(stat.S_ISDIR(metadata.st_mode) and not directory.is_symlink(),
                f"H7 unsafe directory: {directory}")
            req(stat.S_IMODE(metadata.st_mode) == 0o700,
                f"H7 directory mode drift: {directory}")
            relative_directory = directory.relative_to(root).as_posix()
            req(relative_directory not in observed_directories,
                "H7 duplicate directory inventory")
            observed_directories.add(relative_directory)
        for name in filenames:
            path = current_path / name
            safe_regular(path, mode600=True)
            relative = path.relative_to(root).as_posix()
            req(relative not in members, "H7 duplicate file inventory")
            members.add(relative)
    return members, observed_directories


def verify_closed_world(root: Path, expected_manifest_sha256: str) -> dict:
    validate_member_names()
    req(HEX64.fullmatch(expected_manifest_sha256) is not None,
        "H7 external manifest anchor is not lowercase hex64")
    root = root.absolute()
    actual, actual_directories = _closed_world_inventory(root)
    expected = set(MEMBERS) | {MANIFEST_RELATIVE}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    req(not missing and not extra,
        f"H7 closed-world inventory drift missing={missing} extra={extra}")
    missing_directories = sorted(expected_directories() - actual_directories)
    extra_directories = sorted(actual_directories - expected_directories())
    req(not missing_directories and not extra_directories,
        "H7 closed-world directory inventory drift "
        f"missing={missing_directories} extra={extra_directories}")
    manifest = root / MANIFEST_RELATIVE
    req(sha(manifest) == expected_manifest_sha256,
        "H7 external manifest anchor drift")
    rows = parse_manifest(manifest, mode600=True)
    for digest, relative in rows:
        path = root / relative
        safe_regular(path, mode600=True)
        req(sha(path) == digest, f"H7 member byte drift: {relative}")
    req(sha(root / "notes/isambard_ai_v4_r2_h6_payload.sha256")
        == H6_PAYLOAD_SHA256, "H7 frozen H6 anchor drift")
    req(sha(root / V3_PACK_RELATIVE) == V3_PACK_SHA256,
        "H7 frozen v3 field-pack anchor drift")
    return {
        "status": "PASS_H7_CLOSED_WORLD_PACKAGE",
        "manifest_sha256": expected_manifest_sha256,
        "manifest_members": len(MEMBERS),
        "total_files": len(actual),
        "all_files_mode": "0600",
        "all_file_link_counts": 1,
        "authorizes_slurm_submission": False,
    }


def build() -> str:
    if OUT.exists() or OUT.is_symlink():
        raise FileExistsError("H7 payload is append-only")
    data = ("\n".join(lines()) + "\n").encode()
    descriptor, name = tempfile.mkstemp(
        prefix=".v4-r2-h7-payload.", dir=OUT.parent)
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--verify-closed-world", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args()
    if args.verify_closed_world:
        req(args.root is not None and args.manifest_sha256 is not None,
            "closed-world verification needs root and external manifest SHA")
        print(verify_closed_world(args.root, args.manifest_sha256))
        return 0
    req(args.root is None and args.manifest_sha256 is None,
        "root/manifest SHA are closed-world-only options")
    print(verify() if args.verify else build())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
