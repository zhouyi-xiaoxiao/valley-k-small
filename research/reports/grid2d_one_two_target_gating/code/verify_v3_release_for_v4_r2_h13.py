#!/usr/bin/env python3
"""H13 authority scaffold for frozen v3 primary plus a future audited R5."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import scientific_primary_replay_v4_r2_h3 as primary
import scientific_tail_replay_v4_r2_h2 as science


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
V3_ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
V3_MANIFEST = V3_ROOT / "artifacts/data/gating_v3_production_manifest.json"
V3_RAW = V3_ROOT / "artifacts/outputs/isambard_ai_v3/production-5788353"
V3_REDUCTION_ROOT = V3_ROOT / (
    "artifacts/outputs/isambard_ai_v3/reductions/"
    "production-5788353-reduce-5788358"
)
V3_REDUCTION = V3_REDUCTION_ROOT / "reduction.json"
V3_REDUCTION_CSV = V3_REDUCTION_ROOT / "reduction.csv"
V3_SACCT = V3_REDUCTION_ROOT / "sacct-production-5788353.psv"
V3_ACTIVE_PAYLOAD = V3_ROOT / "notes/isambard_ai_v3_payload.sha256"
V3_SUBMISSION_STATE = V3_ROOT / (
    "artifacts/outputs/isambard_ai_v3/submission/submission_state_v3.json"
)
OUTPUT = PACKAGE_ROOT / "artifacts/releases/v3-release-for-v4-r2-h13.json"

V3_MANIFEST_SHA256 = "419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f"
V3_ACTIVE_PAYLOAD_SHA256 = "9a56344f23afc0f14a269c7e4c10a062e920d5393032a223eccbb9eaa4269dd9"
V3_SUBMISSION_STATE_SHA256 = "bfdab79ad8156de7a79a3d4a475eff6608bb08354847c5036b0dc081c795b947"
V3_REDUCTION_SHA256 = "9576b601e52eeb9d6eae6c99cbb52d241050c9bc0714628d5f3e267ceed99984"
V3_REDUCTION_CSV_SHA256 = "698cc32633d7e24f47eb09555d1c3e0fc3b259b1faa13ce69c8d59d14f9f30eb"
V3_SACCT_SHA256 = "e2723dea5263c912830189abb056ecd2e722db74f678ebb8eb996e118859360c"
V3_INVENTORY_DIGEST = "cfeb3466f8760dcfec2f8edc9babfcf249cc8b054a307059417a1261c2579646"

AUTHORITY_INPUT_SCHEMA = "h13-secondary-authority-cli-v1"
EXPECTED_SECONDARY_RELEASE_SCHEMA = "__SECONDARY_R5_RELEASE_SCHEMA_PENDING__"
EXPECTED_SECONDARY_RELEASE_STATUS = "__SECONDARY_R5_RELEASE_STATUS_PENDING__"
EXPECTED_SECONDARY_AUDIT_SCHEMA = "__SECONDARY_R5_AUDIT_SCHEMA_PENDING__"
EXPECTED_SECONDARY_AUDIT_STATUS = "__SECONDARY_R5_AUDIT_STATUS_PENDING__"
EXPECTED_SECONDARY_PUBLICATION_PREFIX = "__SECONDARY_R5_PUBLICATION_PREFIX_PENDING__"
EXPECTED_SECONDARY_MEMBER_NAMES = ("__SECONDARY_R5_MEMBER_NAMES_PENDING__",)
EXPECTED_SECONDARY_DATA_MEMBER_NAMES = (
    "__SECONDARY_R5_DATA_MEMBER_NAMES_PENDING__",
)
EXPECTED_SECONDARY_RELEASE_MEMBER = "__SECONDARY_R5_RELEASE_MEMBER_PENDING__"
EXPECTED_SECONDARY_AUDIT_MEMBER = "__SECONDARY_R5_AUDIT_MEMBER_PENDING__"
EXPECTED_SECONDARY_RELEASE_KEYS = frozenset({
    "__SECONDARY_R5_RELEASE_KEYS_PENDING__",
})
EXPECTED_SECONDARY_AUDIT_KEYS = frozenset({
    "__SECONDARY_R5_AUDIT_KEYS_PENDING__",
})
EXPECTED_SECONDARY_RELEASE_AUDIT_TRUE_KEYS = (
    "__SECONDARY_R5_RELEASE_AUDIT_TRUE_KEYS_PENDING__",
)
SECONDARY_R5_PAYLOAD_SHA256 = "__SECONDARY_R5_PAYLOAD_SHA256_PENDING__"
SECONDARY_R5_CONTRACT_SHA256 = "__SECONDARY_R5_CONTRACT_SHA256_PENDING__"
SECONDARY_R5_CONTAINER_SHA256 = "__SECONDARY_R5_LIVE_CONTAINER_SHA256_PENDING__"
SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER = (
    "__SECONDARY_R5_INDEPENDENT_GO_AUDIT_MEMBER_PENDING__"
)
SECONDARY_R5_INDEPENDENT_AUDIT_SHA256 = (
    "__SECONDARY_R5_INDEPENDENT_GO_AUDIT_SHA256_PENDING__"
)
SECONDARY_R5_INDEPENDENT_AUDIT_DECISION_MARKER = (
    "__SECONDARY_R5_INDEPENDENT_GO_DECISION_MARKER_PENDING__"
)
REJECTED_SECONDARY_R4_PAYLOAD_SHA256 = (
    "e02ac46aa968ff725f83b08a759b81cfea37197dca710c42544f78ecac0387af"
)
REJECTED_SECONDARY_R4_CONTRACT_SHA256 = (
    "c90ebc92958c1ddb82aa0f54919a32f8e0c3ca64c7ea90dbf7c97dc20da232b4"
)
HEX64 = re.compile(r"[0-9a-f]{64}")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def contract_ready() -> None:
    scalar = (
        EXPECTED_SECONDARY_RELEASE_SCHEMA,
        EXPECTED_SECONDARY_RELEASE_STATUS,
        EXPECTED_SECONDARY_AUDIT_SCHEMA,
        EXPECTED_SECONDARY_AUDIT_STATUS,
        EXPECTED_SECONDARY_PUBLICATION_PREFIX,
        *EXPECTED_SECONDARY_MEMBER_NAMES,
        *EXPECTED_SECONDARY_DATA_MEMBER_NAMES,
        EXPECTED_SECONDARY_RELEASE_MEMBER,
        EXPECTED_SECONDARY_AUDIT_MEMBER,
        *EXPECTED_SECONDARY_RELEASE_KEYS,
        *EXPECTED_SECONDARY_AUDIT_KEYS,
        *EXPECTED_SECONDARY_RELEASE_AUDIT_TRUE_KEYS,
        SECONDARY_R5_PAYLOAD_SHA256,
        SECONDARY_R5_CONTRACT_SHA256,
        SECONDARY_R5_CONTAINER_SHA256,
        SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER,
        SECONDARY_R5_INDEPENDENT_AUDIT_SHA256,
        SECONDARY_R5_INDEPENDENT_AUDIT_DECISION_MARKER,
    )
    req(all("PENDING" not in value and "__" not in value for value in scalar), "secondary R5 contract pending")
    req(
        all(
            HEX64.fullmatch(value) is not None
            for value in (
                SECONDARY_R5_PAYLOAD_SHA256,
                SECONDARY_R5_CONTRACT_SHA256,
                SECONDARY_R5_CONTAINER_SHA256,
                SECONDARY_R5_INDEPENDENT_AUDIT_SHA256,
            )
        ),
        "secondary R5 anchor shape",
    )
    independent = Path(SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER)
    req(
        not independent.is_absolute()
        and ".." not in independent.parts
        and independent.as_posix() == SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER
        and SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER.startswith("notes/"),
        "secondary R5 independent audit member",
    )
    req(
        set(EXPECTED_SECONDARY_DATA_MEMBER_NAMES)
        == set(EXPECTED_SECONDARY_MEMBER_NAMES) - {EXPECTED_SECONDARY_AUDIT_MEMBER}
        and EXPECTED_SECONDARY_RELEASE_MEMBER
        in EXPECTED_SECONDARY_DATA_MEMBER_NAMES,
        "secondary R5 member partition",
    )


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        req(key not in result, f"duplicate JSON key {key}")
        result[key] = value
    return result


def json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON token {token} in {label}")
        ),
    )
    req(isinstance(value, dict), f"{label} root is not an object")
    return value


def read_once(path: Path, expected_sha256: str, mode: int = 0o400) -> bytes:
    req(HEX64.fullmatch(expected_sha256) is not None, "malformed expected SHA-256")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        req(
            stat.S_ISREG(before.st_mode)
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == mode,
            f"unsafe input {path}",
        )
        chunks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1 << 20)
            if not block:
                break
            chunks.append(block)
        after = os.fstat(descriptor)
        req(
            (
                before.st_dev,
                before.st_ino,
                before.st_mode,
                before.st_nlink,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_mode,
                after.st_nlink,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            ),
            f"input changed during single-FD read {path}",
        )
        raw = b"".join(chunks)
        req(len(raw) == before.st_size and sha_bytes(raw) == expected_sha256, f"input hash drift {path}")
        return raw
    finally:
        os.close(descriptor)


def verify_primary() -> dict[str, Any]:
    req(sha(V3_MANIFEST) == V3_MANIFEST_SHA256, "v3 manifest drift")
    req(sha(V3_ACTIVE_PAYLOAD) == V3_ACTIVE_PAYLOAD_SHA256, "v3 active payload drift")
    req(sha(V3_SUBMISSION_STATE) == V3_SUBMISSION_STATE_SHA256, "v3 submission state drift")
    req(sha(V3_REDUCTION) == V3_REDUCTION_SHA256, "v3 reduction JSON drift")
    req(sha(V3_REDUCTION_CSV) == V3_REDUCTION_CSV_SHA256, "v3 reduction CSV drift")
    req(sha(V3_SACCT) == V3_SACCT_SHA256, "v3 sacct receipt drift")
    state = science.strict_json(V3_SUBMISSION_STATE, mode600=True)
    expected_chain = {
        "environment": ("5788353", None),
        "canary_array": ("5788354", "5788353"),
        "canary_reducer": ("5788356", "5788354"),
        "production_array": ("5788357", "5788356"),
        "production_reducer": ("5788358", "5788357"),
    }
    req(
        state.get("schema") == "grid2d-one-two-target-gating-isambard-submission-state-v3"
        and state.get("state_version") == 3,
        "v3 submission state schema",
    )
    for stage, (job, dependency) in expected_chain.items():
        entry = state.get("jobs", {}).get(stage, {})
        req(
            entry.get("job_id") == job
            and entry.get("dependency_afterok") == dependency,
            f"v3 submission chain drift {stage}",
        )
    reduction = science.strict_json(V3_REDUCTION, mode600=True)
    inventory = reduction.get("inventory")
    req(
        isinstance(inventory, list)
        and len(inventory) == 5760
        and reduction.get("audit", {}).get("inventory_digest") == V3_INVENTORY_DIGEST,
        "v3 production inventory drift",
    )
    allocation = science.replay_sacct_bijection(
        V3_SACCT,
        "5788357",
        inventory,
        task_count=480,
        cells_per_allocation=12,
        require_extended=False,
    )
    tail_replay = science.recompute_tail_evidence(
        V3_MANIFEST,
        V3_RAW,
        V3_REDUCTION,
        expected_cells=5760,
        expected_blocks=32,
    )
    primary_replay = primary.replay(
        V3_MANIFEST,
        V3_RAW,
        V3_REDUCTION,
        expected_blocks=32,
        tail_replay=tail_replay,
    )
    req(
        tail_replay.get("status") == "PASS_TAIL_EVIDENCE"
        and primary_replay.get("status") == "PASS_PRIMARY_ROPE_EVIDENCE"
        and primary_replay.get("authorizes_ready_evidence") is True,
        "frozen v3 primary did not authorize",
    )
    return {
        "manifest_sha256": V3_MANIFEST_SHA256,
        "active_payload_manifest_sha256": V3_ACTIVE_PAYLOAD_SHA256,
        "submission_state_sha256": V3_SUBMISSION_STATE_SHA256,
        "reduction_json_sha256": V3_REDUCTION_SHA256,
        "reduction_csv_sha256": V3_REDUCTION_CSV_SHA256,
        "sacct_receipt_sha256": V3_SACCT_SHA256,
        "inventory_digest": V3_INVENTORY_DIGEST,
        "fixed_jobs": {stage: value[0] for stage, value in expected_chain.items()},
        "production_allocation_bijection": allocation,
        "scientific_tail_replay": tail_replay,
        "scientific_primary_replay": primary_replay,
    }


def verify_accounting(
    raw: bytes,
    payload_sha256: str,
    job_id: str,
    publication_name: str,
) -> dict[str, Any]:
    value = json_bytes(raw, "secondary authority accounting")
    req(
        value.get("schema") == "h13-secondary-authority-accounting-v1"
        and value.get("status") == "PASS_EXACT_LIVE_SACCT_TERMINAL_BINDING"
        and value.get("h13") == payload_sha256
        and value.get("job_id") == job_id
        and value.get("publication_name") == publication_name
        and value.get("authorizes_scientific_release") is False,
        "secondary authority accounting identity",
    )
    req(sha_bytes(value["raw_stdout"].encode()) == value["raw_stdout_sha256"], "accounting raw hash")
    row = value.get("row", {})
    req(
        row.get("job_id_raw") == row.get("job_id") == job_id
        and row.get("state") == "COMPLETED"
        and row.get("exit_code") == "0:0"
        and isinstance(row.get("elapsed_raw"), int)
        and row["elapsed_raw"] > 0,
        "secondary authority accounting row",
    )
    return value


def verify_secondary(args: argparse.Namespace) -> dict[str, Any]:
    contract_ready()
    req(
        args.input_contract_schema == AUTHORITY_INPUT_SCHEMA
        and args.secondary_release_schema == EXPECTED_SECONDARY_RELEASE_SCHEMA
        and args.secondary_release_status == EXPECTED_SECONDARY_RELEASE_STATUS
        and args.secondary_audit_schema == EXPECTED_SECONDARY_AUDIT_SCHEMA
        and args.secondary_audit_status == EXPECTED_SECONDARY_AUDIT_STATUS,
        "secondary authority versioned contract",
    )
    req(args.secondary_job_id.isdecimal() and int(args.secondary_job_id) > 0, "secondary job id")
    req(
        args.publication_name
        == f"{EXPECTED_SECONDARY_PUBLICATION_PREFIX}{args.secondary_job_id}",
        "secondary publication/job identity",
    )
    req(
        len(args.secondary_member_name)
        == len(args.secondary_member)
        == len(args.secondary_member_sha256)
        == len(EXPECTED_SECONDARY_MEMBER_NAMES),
        "secondary member count",
    )
    req(tuple(args.secondary_member_name) == EXPECTED_SECONDARY_MEMBER_NAMES, "secondary member order")
    req(
        args.secondary_release_member == EXPECTED_SECONDARY_RELEASE_MEMBER
        and args.secondary_audit_member == EXPECTED_SECONDARY_AUDIT_MEMBER,
        "secondary release/receipt member identity",
    )
    parents = {path.parent for path in args.secondary_member}
    req(
        len(parents) == 1
        and next(iter(parents)).name == args.publication_name
        and tuple(path.name for path in args.secondary_member) == EXPECTED_SECONDARY_MEMBER_NAMES,
        "secondary closed publication layout",
    )
    blobs = {
        name: read_once(path, digest)
        for name, path, digest in zip(
            args.secondary_member_name,
            args.secondary_member,
            args.secondary_member_sha256,
            strict=True,
        )
    }
    release = json_bytes(blobs[args.secondary_release_member], "secondary release")
    audit = json_bytes(
        blobs[args.secondary_audit_member],
        "secondary publication receipt",
    )
    req(
        set(release) == set(EXPECTED_SECONDARY_RELEASE_KEYS)
        and release.get("schema") == EXPECTED_SECONDARY_RELEASE_SCHEMA
        and release.get("status") == EXPECTED_SECONDARY_RELEASE_STATUS,
        "secondary release exact schema/status/keys",
    )
    req(
        set(audit) == set(EXPECTED_SECONDARY_AUDIT_KEYS)
        and audit.get("schema") == EXPECTED_SECONDARY_AUDIT_SCHEMA
        and audit.get("status") == EXPECTED_SECONDARY_AUDIT_STATUS,
        "secondary audit exact schema/status/keys",
    )
    member_hashes = dict(
        zip(args.secondary_member_name, args.secondary_member_sha256, strict=True)
    )
    data_member_hashes = {
        name: member_hashes[name]
        for name in EXPECTED_SECONDARY_DATA_MEMBER_NAMES
    }
    req(
        release.get("publication_name") == args.publication_name
        and release.get("authorizes_v3_secondary_result") is True
        and release.get("authorizes_fullnode_v4") is False,
        "secondary release publication/authority boundary",
    )
    release_audit = release.get("audit", {})
    req(
        isinstance(release_audit, dict)
        and release_audit.get("pass") is True
        and release_audit.get("fail_closed") is True
        and all(
            release_audit.get(key) is True
            for key in EXPECTED_SECONDARY_RELEASE_AUDIT_TRUE_KEYS
        )
        and release_audit.get("contract_sha256") == SECONDARY_R5_CONTRACT_SHA256
        and release_audit.get("payload_manifest_sha256")
        == SECONDARY_R5_PAYLOAD_SHA256
        and release_audit.get("container_sha256")
        == SECONDARY_R5_CONTAINER_SHA256
        and release_audit.get("secondary_slurm_job_id")
        == args.secondary_job_id
        and release_audit.get("member_sha256") == data_member_hashes,
        "secondary release exact R5 audit binding",
    )
    req(
        audit.get("publication_name") == args.publication_name
        and audit.get("secondary_slurm_job_id") == args.secondary_job_id
        and audit.get("member_sha256") == data_member_hashes
        and audit.get("published_inventory")
        == list(EXPECTED_SECONDARY_MEMBER_NAMES)
        and audit.get("contract_sha256") == SECONDARY_R5_CONTRACT_SHA256
        and audit.get("payload_manifest_sha256") == SECONDARY_R5_PAYLOAD_SHA256
        and audit.get("container_sha256") == SECONDARY_R5_CONTAINER_SHA256,
        "secondary publication receipt identity/reverse binding",
    )
    receipt_authority = audit.get("authority", {})
    req(
        isinstance(receipt_authority, dict)
        and receipt_authority.get("authorization_filename")
        == EXPECTED_SECONDARY_RELEASE_MEMBER
        and receipt_authority.get("authorization_sha256")
        == member_hashes[EXPECTED_SECONDARY_RELEASE_MEMBER]
        and receipt_authority.get("core_pair_authoritative") is False
        and receipt_authority.get("published_result_authorized") is True
        and audit.get("raw_count_recomputation_verified") is True
        and audit.get("raw_upstream_inventory_bound") is True
        and audit.get("single_process_directory_fd_retained") is True,
        "secondary publication receipt R5 killing-fixture authority",
    )
    independent_audit_raw = read_once(
        PACKAGE_ROOT / SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER,
        SECONDARY_R5_INDEPENDENT_AUDIT_SHA256,
    )
    req(
        SECONDARY_R5_INDEPENDENT_AUDIT_DECISION_MARKER.encode()
        in independent_audit_raw,
        "secondary independent audit decision marker",
    )
    req(
        release_audit.get("container_sha256") == audit.get("container_sha256"),
        "secondary container reverse binding",
    )
    accounting_raw = read_once(
        args.secondary_accounting, args.secondary_accounting_sha256
    )
    accounting = verify_accounting(
        accounting_raw,
        args.h13_payload_sha256,
        args.secondary_job_id,
        args.publication_name,
    )
    return {
        "schema": EXPECTED_SECONDARY_RELEASE_SCHEMA,
        "status": EXPECTED_SECONDARY_RELEASE_STATUS,
        "audit_schema": EXPECTED_SECONDARY_AUDIT_SCHEMA,
        "audit_status": EXPECTED_SECONDARY_AUDIT_STATUS,
        "job_id": args.secondary_job_id,
        "publication_name": args.publication_name,
        "member_sha256": member_hashes,
        "release_sha256": member_hashes[args.secondary_release_member],
        "audit_sha256": member_hashes[args.secondary_audit_member],
        "r5_payload_manifest_sha256": SECONDARY_R5_PAYLOAD_SHA256,
        "r5_contract_sha256": SECONDARY_R5_CONTRACT_SHA256,
        "r5_container_sha256": SECONDARY_R5_CONTAINER_SHA256,
        "independent_go_audit": {
            "path": SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER,
            "sha256": SECONDARY_R5_INDEPENDENT_AUDIT_SHA256,
            "decision_marker": SECONDARY_R5_INDEPENDENT_AUDIT_DECISION_MARKER,
        },
        "live_accounting_sha256": args.secondary_accounting_sha256,
        "live_accounting": accounting,
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    req(HEX64.fullmatch(args.h13_payload_sha256) is not None, "H13 payload SHA-256")
    secondary = verify_secondary(args)
    frozen_primary = verify_primary()
    return {
        "schema": "grid2d-one-two-target-gating-v3-release-for-v4-r2-h13",
        "status": "PASS_AUTHORIZE_V4_R2_H13_HARDWARE_CANARY",
        "h13": args.h13_payload_sha256,
        "fixed_roots": {
            "v3_primary": str(V3_ROOT),
            "h13_package_snapshot": str(PACKAGE_ROOT),
        },
        "frozen_v3_primary": frozen_primary,
        "secondary_r5_authority": secondary,
        "authority_boundary": {
            "legacy_h1_receipt_required": False,
            "legacy_h1_receipt_forged": False,
            "authorizes_only_h13_canary_then_production": True,
            "authorizes_reducer_or_later": False,
        },
        "authorizes_v4_r2_h13": True,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(path == OUTPUT and not path.exists() and not path.is_symlink(), "H13 release output path")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    raw = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v3-h13-release.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h13-payload-sha256", required=True)
    parser.add_argument("--input-contract-schema", required=True)
    parser.add_argument("--secondary-release-schema", required=True)
    parser.add_argument("--secondary-release-status", required=True)
    parser.add_argument("--secondary-audit-schema", required=True)
    parser.add_argument("--secondary-audit-status", required=True)
    parser.add_argument("--secondary-job-id", required=True)
    parser.add_argument("--publication-name", required=True)
    parser.add_argument("--secondary-accounting", type=Path, required=True)
    parser.add_argument("--secondary-accounting-sha256", required=True)
    parser.add_argument("--secondary-member-name", action="append", default=[])
    parser.add_argument("--secondary-member", type=Path, action="append", default=[])
    parser.add_argument("--secondary-member-sha256", action="append", default=[])
    parser.add_argument("--secondary-release-member", required=True)
    parser.add_argument("--secondary-audit-member", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    req(args.output == OUTPUT, "H13 output is not package-snapshot canonical")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = validate(args)
        commit(args.output, payload)
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": sha(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
