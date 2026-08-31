#!/usr/bin/env python3
"""H11 job-private runtime and recoverable independent-inode output transaction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
H9_SHA = "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA = "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN = "notes/isambard_ai_v4_r2_h11_payload.sha256"
H10_MAN = "notes/isambard_ai_v4_r2_h10_payload.sha256"
OLD_ROOT = "/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"
HEX = re.compile(r"[0-9a-f]{64}")
SAFE_ABS = re.compile(r"/[A-Za-z0-9._/-]+")


def req(value, message):
    if not value:
        raise ValueError(message)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_rel(name: str) -> Path:
    req(isinstance(name, str) and name not in ("", "."), "unsafe relative path")
    req("\x00" not in name and "\n" not in name and "\r" not in name, "relative path control byte")
    path = Path(name)
    req(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name, "unsafe relative path")
    return path


def trusted_abs(path: Path | str, must_exist: bool = True) -> Path:
    value = Path(path).absolute()
    req(SAFE_ABS.fullmatch(str(value)) is not None, "unsafe absolute path")
    probe = value if value.exists() or value.is_symlink() else value.parent
    if must_exist:
        req(value.exists() and not value.is_symlink(), "missing or symlink path")
    while True:
        req(not probe.is_symlink(), "ancestor symlink")
        if probe == probe.parent:
            break
        probe = probe.parent
    return value


def write_all(fd: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        written = os.write(fd, raw[offset:])
        req(written > 0, "short write")
        offset += written


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def exclusive_bytes(path: Path, raw: bytes, mode: int) -> str:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        write_all(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, mode)
    fsync_dir(path.parent)
    return sha_bytes(raw)


def canonical_json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def exclusive_json(path: Path, value, mode: int = 0o600) -> str:
    return exclusive_bytes(path, canonical_json(value), mode)


def load_json(path: Path, mode: int) -> dict:
    info = path.lstat()
    req(
        stat.S_ISREG(info.st_mode)
        and not path.is_symlink()
        and info.st_nlink == 1
        and stat.S_IMODE(info.st_mode) == mode,
        "unsafe JSON",
    )
    return json.loads(path.read_text())


def ensure_dir_chain(root: Path, target: Path) -> None:
    req(target == root or root in target.parents, "directory escaped run root")
    missing: list[Path] = []
    probe = target
    while probe != root:
        if not probe.exists() and not probe.is_symlink():
            missing.append(probe)
        probe = probe.parent
    for path in reversed(missing):
        path.mkdir(mode=0o700)
        os.chmod(path, 0o700)
    probe = target
    while True:
        info = probe.lstat()
        req(
            stat.S_ISDIR(info.st_mode)
            and not probe.is_symlink()
            and stat.S_IMODE(info.st_mode) == 0o700,
            "unsafe run directory",
        )
        if probe == root:
            break
        probe = probe.parent


def manifest(root: Path, anchor: str, file_mode: int = 0o600) -> dict[str, str]:
    req(HEX.fullmatch(anchor) is not None, "H11 anchor shape")
    root = trusted_abs(root)
    req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode) == 0o700, "package root mode")
    manifest_path = root / MAN
    req(manifest_path.is_file() and not manifest_path.is_symlink() and sha(manifest_path) == anchor, "H11 manifest pin")
    raw = manifest_path.read_bytes()
    req(raw.endswith(b"\n") and b"\r" not in raw, "manifest canonical bytes")
    rows: dict[str, str] = {}
    for line in raw.decode().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)", line)
        req(match is not None, "manifest syntax")
        digest, name = match.groups()
        safe_rel(name)
        req(name not in rows, "duplicate manifest member")
        rows[name] = digest
    actual: set[str] = set()
    for current, directories, files in os.walk(root, followlinks=False):
        for directory in directories:
            path = Path(current) / directory
            info = path.lstat()
            req(
                stat.S_ISDIR(info.st_mode)
                and not path.is_symlink()
                and stat.S_IMODE(info.st_mode) == 0o700,
                "package directory inventory",
            )
        for filename in files:
            path = Path(current) / filename
            info = path.lstat()
            req(
                stat.S_ISREG(info.st_mode)
                and not path.is_symlink()
                and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == file_mode,
                "package file inventory",
            )
            actual.add(path.relative_to(root).as_posix())
    req(actual == set(rows) | {MAN}, "closed package inventory")
    for name, digest in rows.items():
        req(sha(root / name) == digest, f"package member drift {name}")
    req(sha(root / H10_MAN) == H10_SHA, "H10 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h9_payload.sha256") == H9_SHA, "H9 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h8_payload.sha256") == H8_SHA, "H8 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h7_payload.sha256") == H7_SHA, "H7 parent drift")
    return rows


def copy_snapshot(package: Path, snapshot: Path, h11: str) -> dict[str, str]:
    rows = manifest(package, h11)
    req(not snapshot.exists() and not snapshot.is_symlink(), "snapshot collision")
    snapshot.mkdir(mode=0o700)
    baseline = {**rows, MAN: h11}
    for name, digest in baseline.items():
        target = snapshot / safe_rel(name)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(package / name, target)
        os.chmod(target, 0o400)
        req(sha(target) == digest, "snapshot copy digest")
    for current, _, _ in os.walk(snapshot):
        os.chmod(current, 0o700)
    manifest(snapshot, h11, 0o400)
    manifest(package, h11)
    return baseline


def copy_inputs(run: Path, snapshot: Path, records: list[dict], baseline: dict[str, str]) -> dict[str, str]:
    imported: dict[str, str] = {}
    for item in records:
        req(set(item) == {"path", "sha256"} and HEX.fullmatch(item["sha256"]) is not None, "input schema")
        name = item["path"]
        safe_rel(name)
        req(name.startswith("artifacts/") and name not in baseline and name not in imported, "input collision")
        source = run / name
        info = source.lstat()
        req(
            stat.S_ISREG(info.st_mode)
            and not source.is_symlink()
            and info.st_nlink == 1
            and stat.S_IMODE(info.st_mode) == 0o600
            and sha(source) == item["sha256"],
            "input source drift",
        )
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(source, target)
        os.chmod(target, 0o400)
        req(sha(target) == item["sha256"], "copied input drift")
        imported[name] = item["sha256"]
    return imported


def inventory(root: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for current, directories, files in os.walk(root, followlinks=False):
        for directory in directories:
            path = Path(current) / directory
            info = path.lstat()
            req(
                stat.S_ISDIR(info.st_mode)
                and not path.is_symlink()
                and stat.S_IMODE(info.st_mode) == 0o700,
                "runtime directory drift",
            )
        for filename in files:
            path = Path(current) / filename
            info = path.lstat()
            req(
                stat.S_ISREG(info.st_mode)
                and not path.is_symlink()
                and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) in (0o400, 0o600),
                "runtime file drift",
            )
            result[path.relative_to(root).as_posix()] = {
                "sha256": sha(path),
                "mode": stat.S_IMODE(info.st_mode),
            }
    return result


def mapped_args(args: list[str], run: Path, package: Path, snapshot: Path, imported: dict[str, str]) -> list[str]:
    result: list[str] = []
    for value in args:
        req("\x00" not in value and "\n" not in value and "\r" not in value, "argv control byte")
        if value.startswith(str(run) + "/"):
            name = Path(value).relative_to(run).as_posix()
            req(name in imported, "argv run path not content-bound")
            result.append(str(snapshot / name))
        else:
            req(not value.startswith("/") and not value.startswith(str(package) + "/"), "absolute argv snapshot bypass")
            result.append(value)
    return result


def script_binding(path: Path, expected: str) -> str:
    data = path.read_bytes()
    normalized, count = re.subn(
        rb"H11_EXPECTED_BINDING_SHA256=[0-9a-f]{64}",
        b"H11_EXPECTED_BINDING_SHA256=" + b"0" * 64,
        data,
    )
    req(count == 1 and sha_bytes(normalized) == expected, "embedded submitted-script binding")
    return sha_bytes(data)


def receipt_key(phase: str, array: str | None, task: int | None, job: str) -> str:
    return f"{phase}-{array}_{task}" if task is not None else f"{phase}-{job}"


def copy_independent(source: Path, target: Path, digest: str, mode: int) -> None:
    source_info = source.lstat()
    req(stat.S_ISREG(source_info.st_mode) and not source.is_symlink(), "copy source unsafe")
    fd_in = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    fd_out = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        while True:
            block = os.read(fd_in, 1 << 20)
            if not block:
                break
            write_all(fd_out, block)
        os.fsync(fd_out)
    finally:
        os.close(fd_in)
        os.close(fd_out)
    os.chmod(target, mode)
    target_info = target.lstat()
    req(
        target_info.st_ino != source_info.st_ino
        and target_info.st_nlink == 1
        and stat.S_IMODE(target_info.st_mode) == mode
        and sha(target) == digest,
        "independent copy drift",
    )


def transaction_roots(run: Path) -> tuple[Path, Path]:
    transactions = run / "artifacts/h11_transactions"
    claims = run / "artifacts/h11_transaction_claims"
    ensure_dir_chain(run, transactions)
    ensure_dir_chain(run, claims)
    return transactions, claims


def validate_transaction(tx: Path) -> dict:
    plan_path = tx / "plan.json"
    plan = load_json(plan_path, 0o400)
    req(
        plan.get("schema") == "h11-output-transaction-v1"
        and plan.get("status") == "PREPARED_IMMUTABLE_AUTHORITY_FALSE",
        "transaction plan schema",
    )
    key = plan.get("key")
    req(
        tx.name == key or (isinstance(key, str) and tx.name.startswith(f".{key}.prepare-")),
        "transaction key",
    )
    run = trusted_abs(plan["run_root"])
    outputs = plan.get("outputs")
    req(isinstance(outputs, list), "transaction outputs")
    paths: list[str] = []
    for item in outputs:
        req(set(item) == {"path", "sha256"} and HEX.fullmatch(item["sha256"]) is not None, "transaction output schema")
        safe_rel(item["path"])
        req(item["path"].startswith("artifacts/"), "transaction output namespace")
        paths.append(item["path"])
    req(len(paths) == len(set(paths)), "duplicate transaction output")
    staged = tx / "staged"
    req(staged.is_dir() and not staged.is_symlink() and stat.S_IMODE(staged.lstat().st_mode) == 0o700, "staged root")
    actual: set[str] = set()
    for current, directories, files in os.walk(staged, followlinks=False):
        for directory in directories:
            path = Path(current) / directory
            info = path.lstat()
            req(
                stat.S_ISDIR(info.st_mode)
                and not path.is_symlink()
                and stat.S_IMODE(info.st_mode) == 0o700,
                "staged directory",
            )
        for filename in files:
            path = Path(current) / filename
            info = path.lstat()
            req(
                stat.S_ISREG(info.st_mode)
                and not path.is_symlink()
                and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == 0o400,
                "staged file invariant",
            )
            actual.add(path.relative_to(staged).as_posix())
    req(actual == set(paths), "staged closed inventory")
    for item in outputs:
        req(sha(staged / item["path"]) == item["sha256"], "staged digest drift")
    req(plan.get("receipt_path") == f"artifacts/h11_receipts/{key}.json", "receipt path binding")
    req(isinstance(plan.get("receipt"), dict), "transaction receipt")
    req(plan["receipt"].get("outputs") == outputs, "transaction receipt/output binding")
    req(str(run) == plan["run_root"], "transaction run root")
    return plan


def recover_claim(run: Path, claim_path: Path) -> Path:
    claim = load_json(claim_path, 0o400)
    req(
        claim.get("schema") == "h11-transaction-publish-claim-v1"
        and claim.get("status") == "PREPARED_TREE_COMPLETE_AUTHORITY_FALSE",
        "transaction claim schema",
    )
    key = claim.get("key")
    req(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9._-]+", key), "transaction claim key")
    transactions, _ = transaction_roots(run)
    tx = transactions / key
    prepare_name = claim.get("prepare_dir")
    req(
        isinstance(prepare_name, str)
        and "/" not in prepare_name
        and prepare_name.startswith(f".{key}.prepare-"),
        "transaction prepare name",
    )
    prepared = transactions / prepare_name
    if tx.exists():
        req(not prepared.exists(), "published and prepared transaction both exist")
        req(sha(tx / "plan.json") == claim["plan_sha256"], "published transaction claim drift")
        validate_transaction(tx)
        return tx
    req(prepared.is_dir() and not prepared.is_symlink(), "claimed prepared tree missing")
    req(sha(prepared / "plan.json") == claim["plan_sha256"], "prepared transaction claim drift")
    validate_transaction(prepared)
    os.rename(prepared, tx)
    fsync_dir(transactions)
    validate_transaction(tx)
    return tx


def prepare_transaction(run: Path, key: str, outputs: list[dict], snapshot: Path, receipt: dict) -> Path:
    req(re.fullmatch(r"[A-Za-z0-9._-]+", key) is not None, "transaction key shape")
    run = trusted_abs(run)
    transactions, claims = transaction_roots(run)
    tx = transactions / key
    claim_path = claims / f"{key}.json"
    if tx.exists():
        validate_transaction(tx)
        return tx
    if claim_path.exists():
        return recover_claim(run, claim_path)
    paths = [item.get("path") for item in outputs if isinstance(item, dict)]
    req(len(paths) == len(outputs) == len(set(paths)), "transaction output uniqueness")
    prepared = Path(tempfile.mkdtemp(prefix=f".{key}.prepare-", dir=transactions))
    os.chmod(prepared, 0o700)
    staged = prepared / "staged"
    staged.mkdir(mode=0o700)
    for item in outputs:
        req(set(item) == {"path", "sha256"} and HEX.fullmatch(item["sha256"]) is not None, "output schema")
        name = item["path"]
        safe_rel(name)
        req(name.startswith("artifacts/"), "output namespace")
        source = snapshot / name
        req(sha(source) == item["sha256"], "snapshot output drift")
        target = staged / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        copy_independent(source, target, item["sha256"], 0o400)
    for current, _, _ in os.walk(staged, topdown=False):
        os.chmod(current, 0o700)
        fsync_dir(Path(current))
    plan = {
        "schema": "h11-output-transaction-v1",
        "status": "PREPARED_IMMUTABLE_AUTHORITY_FALSE",
        "key": key,
        "run_root": str(run),
        "outputs": outputs,
        "receipt_path": f"artifacts/h11_receipts/{key}.json",
        "receipt": receipt,
        "authorizes_scientific_release": False,
    }
    plan_sha = exclusive_json(prepared / "plan.json", plan, 0o400)
    fsync_dir(prepared)
    if os.environ.get("H11_TEST_CRASH_AFTER_STAGE") == "1":
        raise RuntimeError("H11 injected post-stage pre-claim crash")
    claim = {
        "schema": "h11-transaction-publish-claim-v1",
        "status": "PREPARED_TREE_COMPLETE_AUTHORITY_FALSE",
        "key": key,
        "run_root": str(run),
        "prepare_dir": prepared.name,
        "plan_sha256": plan_sha,
    }
    exclusive_json(claim_path, claim, 0o400)
    if os.environ.get("H11_TEST_CRASH_AFTER_TRANSACTION_CLAIM") == "1":
        raise RuntimeError("H11 injected post-claim pre-publish crash")
    return recover_claim(run, claim_path)


def promotion_path(target: Path, key: str, index: int) -> Path:
    return target.parent / f".h11-promote-{key}-{index:06d}"


def prepare_promotion(staged: Path, promotion: Path, digest: str) -> None:
    if promotion.exists() or promotion.is_symlink():
        info = promotion.lstat()
        if (
            stat.S_ISREG(info.st_mode)
            and not promotion.is_symlink()
            and info.st_nlink == 1
            and stat.S_IMODE(info.st_mode) == 0o600
            and sha(promotion) == digest
        ):
            return
        req(stat.S_ISREG(info.st_mode) and not promotion.is_symlink() and info.st_nlink == 1, "unsafe partial promotion")
        promotion.unlink()
        fsync_dir(promotion.parent)
    copy_independent(staged, promotion, digest, 0o600)


def promote_one(run: Path, tx: Path, key: str, index: int, item: dict, crash_after_link: bool) -> None:
    staged = tx / "staged" / item["path"]
    target = run / safe_rel(item["path"])
    ensure_dir_chain(run, target.parent)
    promotion = promotion_path(target, key, index)
    if target.exists() or target.is_symlink():
        target_info = target.lstat()
        req(stat.S_ISREG(target_info.st_mode) and not target.is_symlink(), "target collision")
        if promotion.exists() or promotion.is_symlink():
            promotion_info = promotion.lstat()
            req(
                stat.S_ISREG(promotion_info.st_mode)
                and not promotion.is_symlink()
                and promotion_info.st_ino == target_info.st_ino
                and promotion_info.st_nlink == 2
                and sha(promotion) == item["sha256"],
                "promotion/target collision",
            )
            promotion.unlink()
            fsync_dir(target.parent)
            target_info = target.lstat()
        req(
            target_info.st_nlink == 1
            and stat.S_IMODE(target_info.st_mode) == 0o600
            and sha(target) == item["sha256"],
            "existing target drift",
        )
        req(target_info.st_ino != staged.lstat().st_ino, "stage-target inode alias")
        return
    prepare_promotion(staged, promotion, item["sha256"])
    os.link(promotion, target, follow_symlinks=False)
    fsync_dir(target.parent)
    if crash_after_link:
        raise RuntimeError("H11 injected post-link pre-unlink crash")
    promotion.unlink()
    fsync_dir(target.parent)
    target_info = target.lstat()
    staged_info = staged.lstat()
    req(
        target_info.st_nlink == 1
        and staged_info.st_nlink == 1
        and target_info.st_ino != staged_info.st_ino
        and stat.S_IMODE(target_info.st_mode) == 0o600
        and stat.S_IMODE(staged_info.st_mode) == 0o400
        and sha(target) == item["sha256"]
        and sha(staged) == item["sha256"],
        "promoted output invariant",
    )


def recover_transaction(
    tx: Path,
    crash_after: int | None = None,
    crash_after_link: int | None = None,
    crash_after_commit: bool = False,
) -> dict:
    tx = trusted_abs(tx)
    plan = validate_transaction(tx)
    run = trusted_abs(plan["run_root"])
    _, claims = transaction_roots(run)
    claim = load_json(claims / f"{tx.name}.json", 0o400)
    req(
        claim.get("schema") == "h11-transaction-publish-claim-v1"
        and claim.get("key") == tx.name
        and claim.get("plan_sha256") == sha(tx / "plan.json"),
        "transaction publish claim replay",
    )
    promoted = 0
    for index, item in enumerate(plan["outputs"]):
        promote_one(run, tx, tx.name, index, item, crash_after_link == index)
        promoted += 1
        if crash_after is not None and promoted >= crash_after:
            raise RuntimeError("H11 injected output promotion crash")
    complete = tx / "complete.json"
    complete_value = {
        "schema": "h11-output-transaction-complete-v1",
        "status": "COMMITTED_NO_OVERWRITE",
        "plan_sha256": sha(tx / "plan.json"),
        "outputs": plan["outputs"],
    }
    if not complete.exists():
        exclusive_json(complete, complete_value, 0o400)
    else:
        req(load_json(complete, 0o400) == complete_value, "transaction complete drift")
    if crash_after_commit or os.environ.get("H11_TEST_CRASH_AFTER_COMMIT") == "1":
        raise RuntimeError("H11 injected post-commit pre-receipt crash")
    receipt_path = run / plan["receipt_path"]
    if not receipt_path.exists():
        exclusive_json(receipt_path, plan["receipt"], 0o600)
    else:
        req(load_json(receipt_path, 0o600) == plan["receipt"], "recovered receipt drift")
    return plan["receipt"]


def recover_all(run: Path) -> dict:
    run = trusted_abs(run)
    transactions, claims = transaction_roots(run)
    published: list[str] = []
    for claim_path in sorted(claims.glob("*.json")):
        published.append(recover_claim(run, claim_path).name)
    recovered: list[str] = []
    ignored_orphans: list[str] = []
    for path in sorted(transactions.iterdir()):
        if path.name.startswith(".") and ".prepare-" in path.name:
            ignored_orphans.append(path.name)
        elif path.is_dir() and not path.is_symlink():
            recover_transaction(path)
            recovered.append(path.name)
        else:
            raise ValueError("unexpected transaction-root entry")
    return {
        "schema": "h11-transaction-recovery-v1",
        "status": "PASS_RECOVERED_PUBLISHED_TRANSACTIONS",
        "published": published,
        "recovered": recovered,
        "ignored_unclaimed_preparation_orphans": ignored_orphans,
    }


def execute(config: dict) -> dict:
    keys = {
        "schema",
        "phase",
        "package_root",
        "run_root",
        "h11",
        "h10",
        "h9",
        "h8",
        "h7",
        "science_path",
        "science_sha256",
        "science_bytes_hex",
        "phase_args",
        "phase_inputs",
    }
    req(set(config) == keys and config["schema"] == "h11-runtime-config-v1", "runtime config schema")
    req(
        (config["h10"], config["h9"], config["h8"], config["h7"])
        == (H10_SHA, H9_SHA, H8_SHA, H7_SHA),
        "runtime parent anchors",
    )
    req(HEX.fullmatch(config["h11"]) is not None, "runtime H11 anchor")
    package = trusted_abs(config["package_root"])
    run = trusted_abs(config["run_root"])
    raw_tmp = os.environ.get("SLURM_TMPDIR", "")
    req(raw_tmp.startswith("/"), "SLURM_TMPDIR")
    temporary = trusted_abs(raw_tmp)
    job = os.environ.get("SLURM_JOB_ID", "")
    array = os.environ.get("SLURM_ARRAY_JOB_ID")
    task_raw = os.environ.get("SLURM_ARRAY_TASK_ID")
    req(job.isdecimal(), "JobIDRaw runtime identity")
    task = int(task_raw) if task_raw is not None else None
    if config["phase"] == "production":
        req(array is not None and array.isdecimal() and task is not None and 0 <= task < 480, "array runtime identity")
    else:
        req(array is None and task is None, "nonarray runtime identity")
    submitted_script = trusted_abs(os.environ.get("H11_SUBMITTED_SCRIPT_PATH", ""))
    expected_binding = os.environ.get("H11_EXPECTED_BINDING_SHA256", "")
    req(HEX.fullmatch(expected_binding) is not None, "submitted script binding missing")
    actual_script_sha = script_binding(submitted_script, expected_binding)
    suffix = f"{array}_{task}" if task is not None else job
    snapshot = temporary / f"h11-{config['phase']}-{suffix}"
    baseline = copy_snapshot(package, snapshot, config["h11"])
    imported = copy_inputs(run, snapshot, config["phase_inputs"], baseline)
    before = {**baseline, **imported}
    science = bytes.fromhex(config["science_bytes_hex"])
    req(
        sha_bytes(science) == config["science_sha256"] == baseline.get(config["science_path"]),
        "captured science binding",
    )
    body = (
        "\n".join(
            line
            for line in science.decode().splitlines()[1:]
            if not line.startswith("#SBATCH")
        ).replace(OLD_ROOT, str(snapshot))
        + "\n"
    ).encode()
    effective_args = mapped_args(config["phase_args"], run, package, snapshot, imported)
    completed = subprocess.run(
        ["bash", "-s", "--", *effective_args],
        input=body,
        cwd=snapshot,
        env={
            **os.environ,
            "H11_PACKAGE_ROOT": str(package),
            "H11_RUN_ROOT": str(run),
            "H11_SNAPSHOT_ROOT": str(snapshot),
        },
        check=False,
    )
    req(completed.returncode == 0, "science body failed")
    after = inventory(snapshot)
    for name, digest in before.items():
        req(
            name in after and after[name]["sha256"] == digest and after[name]["mode"] == 0o400,
            "immutable source/input drift",
        )
    new = sorted(set(after) - set(before))
    req(all(name.startswith("artifacts/") for name in new), "output namespace")
    outputs = [{"path": name, "sha256": after[name]["sha256"]} for name in new]
    runtime_identity = {
        "job_id_raw": job,
        "job_id": f"{array}_{task}" if task is not None else job,
        "array_job_id": array,
        "array_task_id": task,
    }
    receipt = {
        "schema": "h11-runtime-receipt-v1",
        "status": "PASS_H11_RUNTIME_IDENTITY_AND_TRANSACTION_COMMITTED",
        "phase": config["phase"],
        "h11": config["h11"],
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "package_root": str(package),
        "run_root": str(run),
        "runtime_identity": runtime_identity,
        "submitted_script_sha256": actual_script_sha,
        "submitted_script_binding_sha256": expected_binding,
        "science_source": {
            "path": config["science_path"],
            "sha256": config["science_sha256"],
            "derived_body_sha256": sha_bytes(body),
        },
        "phase_args_sha256": sha_bytes(json.dumps(config["phase_args"], separators=(",", ":")).encode()),
        "effective_phase_args_sha256": sha_bytes(json.dumps(effective_args, separators=(",", ":")).encode()),
        "phase_inputs": config["phase_inputs"],
        "outputs": outputs,
        "terminal_accounting_claimed_at_runtime": False,
        "authorizes_scientific_release": False,
    }
    key = receipt_key(config["phase"], array, task, job)
    tx = prepare_transaction(run, key, outputs, snapshot, receipt)
    crash_after_raw = os.environ.get("H11_TEST_CRASH_AFTER_PROMOTE")
    crash_link_raw = os.environ.get("H11_TEST_CRASH_AFTER_LINK")
    return recover_transaction(
        tx,
        int(crash_after_raw) if crash_after_raw else None,
        int(crash_link_raw) if crash_link_raw else None,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--recover-run", type=Path)
    args = parser.parse_args()
    req((args.config is None) != (args.recover_run is None), "choose execute or recover")
    result = execute(json.loads(args.config.read_text())) if args.config else recover_all(args.recover_run)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
