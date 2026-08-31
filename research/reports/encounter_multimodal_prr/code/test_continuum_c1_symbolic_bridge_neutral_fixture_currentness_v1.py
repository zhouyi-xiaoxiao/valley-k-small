#!/usr/bin/env python3
"""Strict hash-and-size currentness gate for the eight-file neutral C1 fixture.

Passing this gate freezes only the neutral symbolic-bridge fixture.  It does not
materialize a formal production symbolic candidate or an acceptance receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
MANIFEST_RELATIVE = PurePosixPath(
    "artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.json"
)

EXPECTED_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1"
EXPECTED_STATUS = (
    "CURRENTNESS_ONLY_NEUTRAL_FIXTURE_NO_FORMAL_PRODUCTION_CANDIDATE_"
    "OR_ACCEPTANCE_RECEIPT"
)
EXPECTED_CLAIM_KEYS = {
    "acceptance_pass",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "formal_production_candidate_materialized",
    "production_geometry_evidence",
    "production_member_sources_complete",
    "production_pass",
    "release_submission_science_execution",
    "science_pass",
    "symbolic_acceptance_receipt_materialized",
    "symbolic_machine_contract_complete",
}
EXPECTED_ROLE_PATHS = [
    (
        "neutral_source",
        "artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json",
    ),
    (
        "outer_manifest",
        "artifacts/data/continuum_c1_symbolic_bridge_neutral_outer_manifest_v1.json",
    ),
    (
        "operation_model",
        "code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json",
    ),
    (
        "canonical_artifact",
        "artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json",
    ),
    (
        "builder",
        "code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py",
    ),
    (
        "independent_validator",
        "code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py",
    ),
    (
        "static_test",
        "code/test_continuum_c1_symbolic_bridge_neutral_fixture_v1.py",
    ),
    (
        "mutation_test",
        "code/test_continuum_c1_symbolic_bridge_neutral_fixture_mutations_v1.py",
    ),
]
LOWER_HEX = frozenset("0123456789abcdef")
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", None)
O_DIRECTORY = getattr(os, "O_DIRECTORY", None)
if type(O_NOFOLLOW) is not int or type(O_DIRECTORY) is not int:
    raise RuntimeError("currentness gate requires O_NOFOLLOW and O_DIRECTORY")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _safe_relative(value: str) -> PurePosixPath:
    if type(value) is not str or not value or "\x00" in value or "\\" in value:
        raise ValueError("currentness path must be a nonempty POSIX string")
    relative = PurePosixPath(value)
    if relative.is_absolute() or relative.as_posix() != value:
        raise ValueError(f"non-canonical currentness path: {value!r}")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"unsafe currentness path: {value!r}")
    return relative


def _stable_snapshot(metadata: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _require_directory(metadata: os.stat_result, label: str) -> None:
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"currentness parent is not an ordinary directory: {label}")


def _require_single_link_regular(metadata: os.stat_result, label: str) -> None:
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"currentness target is not an ordinary regular file: {label}")
    if metadata.st_nlink != 1:
        raise ValueError(f"currentness target must have exactly one hard link: {label}")


def _read_ordinary_report_file(relative: PurePosixPath) -> tuple[bytes, int]:
    label = relative.as_posix()
    directory_fds: list[int] = []
    parent_chain: list[tuple[int, str, int, tuple[int, int, int, int, int, int, int]]] = []
    target_fd: int | None = None
    try:
        root_named_before = os.stat(REPORT, follow_symlinks=False)
        _require_directory(root_named_before, str(REPORT))
        root_fd = os.open(REPORT, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
        directory_fds.append(root_fd)
        root_opened = os.fstat(root_fd)
        _require_directory(root_opened, str(REPORT))
        root_snapshot = _stable_snapshot(root_opened)
        if _stable_snapshot(root_named_before) != root_snapshot:
            raise ValueError("report root changed before descriptor open")

        for component in relative.parts[:-1]:
            parent_fd = directory_fds[-1]
            named_before = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            _require_directory(named_before, f"{label}:{component}")
            child_fd = os.open(
                component,
                os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW,
                dir_fd=parent_fd,
            )
            directory_fds.append(child_fd)
            opened = os.fstat(child_fd)
            _require_directory(opened, f"{label}:{component}")
            opened_snapshot = _stable_snapshot(opened)
            if _stable_snapshot(named_before) != opened_snapshot:
                raise ValueError(f"currentness parent changed before open: {label}")
            parent_chain.append((parent_fd, component, child_fd, opened_snapshot))

        target_name = relative.parts[-1]
        target_parent_fd = directory_fds[-1]
        target_named_before = os.stat(
            target_name,
            dir_fd=target_parent_fd,
            follow_symlinks=False,
        )
        _require_single_link_regular(target_named_before, label)
        target_fd = os.open(
            target_name,
            os.O_RDONLY | O_NOFOLLOW,
            dir_fd=target_parent_fd,
        )
        target_opened = os.fstat(target_fd)
        _require_single_link_regular(target_opened, label)
        target_snapshot = _stable_snapshot(target_opened)
        if _stable_snapshot(target_named_before) != target_snapshot:
            raise ValueError(f"currentness target changed before open: {label}")

        chunks: list[bytes] = []
        while True:
            chunk = os.read(target_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)

        target_after = os.fstat(target_fd)
        _require_single_link_regular(target_after, label)
        if _stable_snapshot(target_after) != target_snapshot:
            raise ValueError(f"currentness target changed while reading: {label}")
        target_named_after = os.stat(
            target_name,
            dir_fd=target_parent_fd,
            follow_symlinks=False,
        )
        _require_single_link_regular(target_named_after, label)
        if _stable_snapshot(target_named_after) != target_snapshot:
            raise ValueError(f"currentness target name changed while reading: {label}")

        for parent_fd, component, child_fd, expected in reversed(parent_chain):
            child_after = os.fstat(child_fd)
            _require_directory(child_after, f"{label}:{component}")
            if _stable_snapshot(child_after) != expected:
                raise ValueError(f"currentness parent descriptor changed: {label}")
            named_after = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            _require_directory(named_after, f"{label}:{component}")
            if _stable_snapshot(named_after) != expected:
                raise ValueError(f"currentness parent name changed: {label}")

        root_after = os.fstat(root_fd)
        _require_directory(root_after, str(REPORT))
        if _stable_snapshot(root_after) != root_snapshot:
            raise ValueError("report root descriptor changed while reading")
        root_named_after = os.stat(REPORT, follow_symlinks=False)
        _require_directory(root_named_after, str(REPORT))
        if _stable_snapshot(root_named_after) != root_snapshot:
            raise ValueError("report root name changed while reading")

        payload = b"".join(chunks)
        if len(payload) != target_after.st_size:
            raise ValueError(f"short currentness read: {label}")
        return payload, target_after.st_size
    finally:
        if target_fd is not None:
            os.close(target_fd)
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)


def _load_manifest() -> tuple[dict[str, Any], bytes]:
    payload, _ = _read_ordinary_report_file(MANIFEST_RELATIVE)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("currentness manifest is not UTF-8") from error
    value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    if type(value) is not dict:
        raise ValueError("currentness manifest root must be an object")
    canonical = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode(
        "utf-8"
    )
    if payload != canonical:
        raise ValueError("currentness manifest is not canonical sorted JSON")
    return value, payload


def main() -> int:
    value, _ = _load_manifest()
    if set(value) != {"claim_boundary", "files", "schema", "status"}:
        raise ValueError("wrong currentness-manifest shape")
    if type(value["schema"]) is not str or value["schema"] != EXPECTED_SCHEMA:
        raise ValueError("wrong currentness schema")
    if type(value["status"]) is not str or value["status"] != EXPECTED_STATUS:
        raise ValueError("wrong currentness status")

    claims = value["claim_boundary"]
    if type(claims) is not dict or set(claims) != EXPECTED_CLAIM_KEYS:
        raise ValueError("currentness claim-boundary keys changed")
    for key in sorted(EXPECTED_CLAIM_KEYS):
        if type(claims[key]) is not bool or claims[key] is not False:
            raise ValueError(f"currentness claim must remain exact false: {key}")

    files = value["files"]
    if type(files) is not list or len(files) != 8:
        raise ValueError("currentness manifest must contain exactly eight files")
    observed_role_paths: list[tuple[str, str]] = []
    seen_paths: set[str] = set()
    for entry in files:
        if type(entry) is not dict or set(entry) != {"path", "role", "sha256", "size_bytes"}:
            raise ValueError("malformed currentness entry")
        if type(entry["role"]) is not str:
            raise ValueError("currentness role must be a string")
        relative = _safe_relative(entry["path"])
        relative_text = relative.as_posix()
        if relative_text in seen_paths:
            raise ValueError(f"duplicate currentness path: {relative_text}")
        seen_paths.add(relative_text)
        observed_role_paths.append((entry["role"], relative_text))

        expected_hash = entry["sha256"]
        if (
            type(expected_hash) is not str
            or len(expected_hash) != 64
            or any(character not in LOWER_HEX for character in expected_hash)
        ):
            raise ValueError(f"invalid SHA-256 field: {relative_text}")
        expected_size = entry["size_bytes"]
        if type(expected_size) is not int or expected_size < 0:
            raise ValueError(f"invalid exact byte size: {relative_text}")

        payload, observed_size = _read_ordinary_report_file(relative)
        if observed_size != expected_size:
            raise ValueError(f"stale currentness size: {relative_text}")
        observed_hash = hashlib.sha256(payload).hexdigest()
        if observed_hash != expected_hash:
            raise ValueError(f"stale currentness hash: {relative_text}")

    if observed_role_paths != EXPECTED_ROLE_PATHS:
        raise ValueError("currentness roles, paths, or order changed")

    for role, _ in EXPECTED_ROLE_PATHS:
        print(f"PASS current_{role}")
    print("SUMMARY 8/8 PASS")
    print("BOUNDARY formal_production_candidate_materialized=false")
    print("BOUNDARY symbolic_acceptance_receipt_materialized=false")
    print("BOUNDARY production_science_acceptance_complete_flags=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
