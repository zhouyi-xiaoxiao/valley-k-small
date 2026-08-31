#!/usr/bin/env python3
"""Detached H11 controller for held submission, recovery, accounting, and final replay."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path

H11_SHA = "dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca"
H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
H9_SHA = "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA = "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN = "notes/isambard_ai_v4_r2_h11_payload.sha256"
RUNTIME = "code/h11_runtime_v4_r2.py"
ZERO = "0" * 64
SCRIPTS = {
    "v3_authority": "code/isambard_ai_gating_v4_r2_v3_authority_h4.sbatch",
    "canary": "code/isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
    "production": "code/isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
    "reducer": "code/isambard_ai_gating_v4_r2_reduce_h4.sbatch",
    "replay": "code/isambard_ai_gating_v4_r2_replay_h4.sbatch",
    "combined": "code/isambard_ai_gating_v4_r2_combined_h4.sbatch",
    "release": "code/isambard_ai_gating_v4_r2_release_h5.sbatch",
    "terminal": "code/isambard_ai_gating_v4_r2_terminal_h9.sbatch",
    "selftest_upstream": "code/isambard_ai_gating_v4_r2_selftest_h9.sbatch",
    "selftest_downstream": "code/isambard_ai_gating_v4_r2_selftest_h9.sbatch",
}
ORDER = ("v3_authority", "canary", "production", "reducer", "replay", "combined", "release", "terminal")
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


def canonical_json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def canonical_sha(value) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


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


def exclusive(path: Path, value, mode: int = 0o600) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
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


def json_mode(path: Path, mode: int = 0o600) -> dict:
    info = path.lstat()
    req(
        stat.S_ISREG(info.st_mode)
        and not path.is_symlink()
        and info.st_nlink == 1
        and stat.S_IMODE(info.st_mode) == mode,
        "unsafe JSON receipt",
    )
    return json.loads(path.read_text())


def verify_package(root: Path) -> dict[str, str]:
    req(HEX.fullmatch(H11_SHA) is not None, "H11 pin unset")
    root = trusted_abs(root)
    req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode) == 0o700, "package root mode")
    manifest = root / MAN
    req(manifest.is_file() and not manifest.is_symlink() and sha(manifest) == H11_SHA, "externally pinned H11 drift")
    raw = manifest.read_bytes()
    req(raw.endswith(b"\n") and b"\r" not in raw, "manifest canonical bytes")
    rows: dict[str, str] = {}
    for line in raw.decode().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)", line)
        req(match is not None, "manifest syntax")
        digest, name = match.groups()
        safe_rel(name)
        req(name not in rows, "duplicate member")
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
                and stat.S_IMODE(info.st_mode) == 0o600,
                "package file inventory",
            )
            actual.add(path.relative_to(root).as_posix())
    req(actual == set(rows) | {MAN}, "closed package inventory")
    for name, digest in rows.items():
        req(sha(root / name) == digest, f"package member drift {name}")
    req(sha(root / "notes/isambard_ai_v4_r2_h10_payload.sha256") == H10_SHA, "H10 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h9_payload.sha256") == H9_SHA, "H9 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h8_payload.sha256") == H8_SHA, "H8 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h7_payload.sha256") == H7_SHA, "H7 parent drift")
    return rows


def capture(root: Path, name: str, rows: dict[str, str]) -> bytes:
    req(name in rows, "source outside manifest")
    path = root / name
    before = path.lstat()
    data = path.read_bytes()
    after = path.lstat()
    req(
        stat.S_ISREG(before.st_mode)
        and not path.is_symlink()
        and before.st_nlink == 1
        and before.st_ino == after.st_ino
        and before.st_mtime_ns == after.st_mtime_ns
        and before.st_size == after.st_size
        and sha_bytes(data) == rows[name],
        "captured bytes TOCTOU",
    )
    return data


def phase_inputs(run: Path, values: list[str]) -> list[dict]:
    result: list[dict] = []
    for value in values:
        req("=" in value, "phase input syntax")
        name, digest = value.rsplit("=", 1)
        safe_rel(name)
        req(name.startswith("artifacts/") and HEX.fullmatch(digest) is not None, "phase input shape")
        path = run / name
        info = path.lstat()
        req(
            stat.S_ISREG(info.st_mode)
            and not path.is_symlink()
            and info.st_nlink == 1
            and stat.S_IMODE(info.st_mode) == 0o600
            and sha(path) == digest,
            "phase input drift",
        )
        result.append({"path": name, "sha256": digest})
    req(len(result) == len({item["path"] for item in result}), "duplicate phase input")
    return result


def render(
    package: Path,
    run: Path,
    phase: str,
    args: list[str],
    inputs: list[dict],
    rows: dict[str, str],
) -> tuple[bytes, str, str]:
    science = capture(package, SCRIPTS[phase], rows)
    runtime = capture(package, RUNTIME, rows)
    directives: list[str] = []
    for line in science.decode().splitlines()[1:]:
        if line.startswith("#SBATCH") and not any(value in line for value in ("--chdir", "--output", "--error")):
            directives.append(line)
    config = {
        "schema": "h11-runtime-config-v1",
        "phase": "production" if phase == "production" else phase,
        "package_root": str(package),
        "run_root": str(run),
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "science_path": SCRIPTS[phase],
        "science_sha256": sha_bytes(science),
        "science_bytes_hex": science.hex(),
        "phase_args": args,
        "phase_inputs": inputs,
    }
    runtime_b64 = base64.b64encode(runtime).decode()
    config_b64 = base64.b64encode(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).decode()
    lines = [
        "#!/usr/bin/env bash",
        *directives,
        f"#SBATCH --chdir={run}",
        f"#SBATCH --output={run}/logs/%x-%A_%a.out",
        f"#SBATCH --error={run}/logs/%x-%A_%a.err",
        "set -euo pipefail",
        "umask 077",
        f"export H11_EXPECTED_BINDING_SHA256={ZERO}",
        'export H11_SUBMITTED_SCRIPT_PATH="$0"',
        '[[ -n "${SLURM_TMPDIR:-}" ]] || exit 90',
        'launch="$(mktemp -d "$SLURM_TMPDIR/h11-launch.XXXXXX")"',
        "trap 'rm -rf \"$launch\"' EXIT",
        f'printf %s {runtime_b64} | base64 -d > "$launch/runtime.py"',
        f'printf %s {config_b64} | base64 -d > "$launch/config.json"',
        'chmod 400 "$launch/runtime.py" "$launch/config.json"',
        'python3 "$launch/runtime.py" --config "$launch/config.json"',
    ]
    template = ("\n".join(lines) + "\n").encode()
    binding = sha_bytes(template)
    final = template.replace(
        f"H11_EXPECTED_BINDING_SHA256={ZERO}".encode(),
        f"H11_EXPECTED_BINDING_SHA256={binding}".encode(),
    )
    req(final != template, "binding insertion")
    return final, binding, sha_bytes(final)


def intent_paths(run: Path, phase: str, intent: str) -> tuple[Path, Path]:
    root = run / "artifacts/h11_intents"
    return root / f"{phase}-{intent}.json", root / f"{phase}-{intent}.sbatch"


def dispatch_root(run: Path) -> Path:
    return run / "artifacts/h11_dispatch"


def submission_path(run: Path, phase: str, job: str) -> Path:
    return run / "artifacts/h11_submissions" / f"{phase}-{job}.json"


def release_intent_path(run: Path, phase: str, job: str) -> Path:
    return run / "artifacts/h11_release_intents" / f"{phase}-{job}.json"


def release_path(run: Path, phase: str, job: str) -> Path:
    return run / "artifacts/h11_releases" / f"{phase}-{job}.json"


def accounting_path(run: Path, phase: str, job: str) -> Path:
    return run / "artifacts/h11_accounting" / f"{phase}-{job}.json"


def parse_squeue(raw: str, intent: str) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for line in raw.splitlines():
        if not line:
            continue
        parts = line.split("|")
        req(len(parts) == 4, "squeue row shape")
        job, comment, state, reason = parts
        if comment != f"H11:{intent}":
            continue
        req(job.isdecimal(), "squeue logical parent")
        groups.setdefault(job, []).append(
            {"job_id": job, "comment": comment, "state": state, "reason": reason}
        )
    return groups


def discover(squeue: str, intent: str) -> dict:
    argv = [squeue, "-h", "-o", "%A|%k|%T|%r"]
    completed = subprocess.run(argv, capture_output=True, check=True)
    raw = completed.stdout.decode()
    return {
        "argv": argv,
        "raw_stdout": raw,
        "raw_stdout_sha256": sha_bytes(completed.stdout),
        "groups": parse_squeue(raw, intent),
    }


def show(scontrol: str, job: str) -> dict:
    argv = [scontrol, "show", "job", "-o", job]
    completed = subprocess.run(argv, capture_output=True, check=True)
    raw = completed.stdout.decode()
    return {
        "argv": argv,
        "raw_stdout": raw,
        "raw_stdout_sha256": sha_bytes(completed.stdout),
        "fields": parse_scontrol(raw),
    }


def parse_scontrol(raw: str) -> dict[str, str]:
    lines = [line for line in raw.splitlines() if line]
    req(len(lines) == 1, "scontrol row cardinality")
    fields: dict[str, str] = {}
    for token in lines[0].split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        req(key not in fields, "duplicate scontrol field")
        fields[key] = value
    for key in ("JobId", "JobState", "Reason", "Comment", "WorkDir", "Dependency", "Command", "StdIn"):
        req(key in fields, f"missing scontrol field {key}")
    return fields


def expected_dependency(dependency: str | None) -> str:
    return "(null)" if dependency is None else f"afterok:{dependency}"


def validate_scontrol_common(
    evidence: dict,
    job: str,
    intent: str,
    run: Path,
    dependency: str | None,
) -> dict[str, str]:
    req(
        len(evidence.get("argv", [])) == 5
        and evidence["argv"][1:] == ["show", "job", "-o", job],
        "scontrol argv",
    )
    req(sha_bytes(evidence["raw_stdout"].encode()) == evidence["raw_stdout_sha256"], "scontrol raw SHA")
    fields = parse_scontrol(evidence["raw_stdout"])
    req(fields == evidence["fields"], "scontrol parsed replay")
    req(fields["JobId"] == job, "scontrol exact JobId")
    req(fields["Comment"] == f"H11:{intent}", "scontrol exact Comment")
    req(fields["WorkDir"] == str(run), "scontrol exact WorkDir")
    req(fields["Dependency"] == expected_dependency(dependency), "scontrol exact Dependency")
    req(fields["StdIn"] == "/dev/null", "scontrol exact StdIn")
    req(fields["Command"] == "(null)" or fields["Command"].endswith("/slurm_script"), "scontrol stdin command")
    return fields


def validate_held(
    evidence: dict,
    job: str,
    intent: str,
    run: Path,
    dependency: str | None,
) -> None:
    fields = validate_scontrol_common(evidence, job, intent, run, dependency)
    req(fields["JobState"] == "PENDING" and fields["Reason"] == "JobHeldUser", "job not exactly user-held")


def validate_released(
    evidence: dict,
    job: str,
    intent: str,
    run: Path,
    dependency: str | None,
) -> None:
    fields = validate_scontrol_common(evidence, job, intent, run, dependency)
    req(
        fields["JobState"] in ("PENDING", "RUNNING", "COMPLETED") and fields["Reason"] != "JobHeldUser",
        "job not released",
    )


def intent_base(
    package: Path,
    run: Path,
    phase: str,
    dependency: str | None,
    args: list[str],
    inputs: list[dict],
    rows: dict[str, str],
    exact_script_sha: str,
    binding: str,
    sbatch: str,
) -> dict:
    return {
        "schema": "h11-submission-intent-v1",
        "status": "PREPARED_HELD_SUBMISSION_INTENT_AUTHORITY_FALSE",
        "phase": phase,
        "dependency_afterok": dependency,
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "package_root": str(package),
        "run_root": str(run),
        "science_path": SCRIPTS[phase],
        "science_sha256": rows[SCRIPTS[phase]],
        "submitted_script_sha256": exact_script_sha,
        "submitted_script_binding_sha256": binding,
        "phase_args": args,
        "phase_inputs": inputs,
        "sbatch_executable": sbatch,
        "authorizes_scientific_release": False,
    }


def prepare_intent(
    run: Path,
    phase: str,
    base: dict,
    script: bytes,
) -> tuple[str, dict, Path]:
    intent = canonical_sha(base)
    comment = f"H11:{intent}"
    argv = [
        base["sbatch_executable"],
        "--parsable",
        "--hold",
        f"--comment={comment}",
        f"--chdir={run}",
    ]
    if base["dependency_afterok"] is not None:
        argv.append(f"--dependency=afterok:{base['dependency_afterok']}")
    value = {**base, "sbatch_argv": argv}
    intent_path, archive = intent_paths(run, phase, intent)
    if intent_path.exists():
        req(json_mode(intent_path) == value, "existing intent drift")
        req(sha(archive) == base["submitted_script_sha256"], "existing archive drift")
    else:
        if not archive.exists():
            exclusive(archive, script)
        else:
            req(sha(archive) == base["submitted_script_sha256"], "intent archive collision")
        exclusive(intent_path, value)
    return intent, value, archive


def attempt_paths(run: Path, phase: str, intent: str, number: int) -> tuple[Path, Path]:
    root = dispatch_root(run)
    prefix = f"{phase}-{intent}-attempt-{number:06d}"
    return root / f"{prefix}.json", root / f"{prefix}.response.json"


def next_attempt(run: Path, phase: str, intent: str) -> int:
    root = dispatch_root(run)
    if not root.exists():
        return 1
    pattern = re.compile(re.escape(f"{phase}-{intent}-attempt-") + r"([0-9]{6})\.json")
    values: list[int] = []
    for path in root.iterdir():
        match = pattern.fullmatch(path.name)
        if match:
            values.append(int(match.group(1)))
    return max(values, default=0) + 1


def find_submission(run: Path, phase: str, intent: str) -> tuple[Path, dict] | None:
    root = run / "artifacts/h11_submissions"
    if not root.exists():
        return None
    matches: list[tuple[Path, dict]] = []
    for path in root.glob(f"{phase}-*.json"):
        value = json_mode(path)
        if value.get("intent_sha256") == intent:
            matches.append((path, value))
    req(len(matches) <= 1, "duplicate immutable submission receipts")
    return matches[0] if matches else None


def dispatch_or_discover(
    run: Path,
    phase: str,
    intent: str,
    intent_value: dict,
    script: bytes,
    squeue: str,
) -> tuple[str, dict]:
    evidence = discover(squeue, intent)
    groups = evidence["groups"]
    req(len(groups) <= 1, "duplicate same-comment logical jobs")
    if not groups:
        number = next_attempt(run, phase, intent)
        attempt_path, response_path = attempt_paths(run, phase, intent, number)
        attempt = {
            "schema": "h11-dispatch-attempt-v1",
            "status": "ABOUT_TO_CALL_SBATCH_HELD_AUTHORITY_FALSE",
            "phase": phase,
            "intent_sha256": intent,
            "attempt": number,
            "argv": intent_value["sbatch_argv"],
            "submitted_script_sha256": intent_value["submitted_script_sha256"],
        }
        exclusive(attempt_path, attempt)
        if os.environ.get("H11_TEST_CRASH_AFTER_DISPATCH_BEFORE_SBATCH") == "1":
            raise RuntimeError("H11 injected post-dispatch pre-sbatch crash")
        completed = subprocess.run(intent_value["sbatch_argv"], input=script, capture_output=True, check=True)
        if os.environ.get("H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM") == "1":
            raise RuntimeError("H11 injected post-sbatch pre-claim crash")
        job = completed.stdout.decode().strip().split(";")[0]
        req(job.isdecimal(), "sbatch job id")
        response = {
            "schema": "h11-dispatch-response-v1",
            "status": "SBATCH_RETURNED_HELD_JOB_ID_AUTHORITY_FALSE",
            "phase": phase,
            "intent_sha256": intent,
            "attempt": number,
            "job_id": job,
            "argv": intent_value["sbatch_argv"],
            "raw_stdout": completed.stdout.decode(),
            "raw_stdout_sha256": sha_bytes(completed.stdout),
            "raw_stderr": completed.stderr.decode(),
            "raw_stderr_sha256": sha_bytes(completed.stderr),
        }
        exclusive(response_path, response)
        evidence = discover(squeue, intent)
        groups = evidence["groups"]
        req(len(groups) == 1 and job in groups, "sbatch response/discovery mismatch")
    req(len(groups) == 1, "intent discovery requires exactly one logical job")
    job = next(iter(groups))
    for row in groups[job]:
        req(row["state"] == "PENDING" and row["reason"] == "JobHeldUser", "discovered job not held")
    return job, evidence


def attempt_receipts(run: Path, phase: str, intent: str) -> list[dict]:
    root = dispatch_root(run)
    if not root.exists():
        return []
    pattern = re.compile(
        re.escape(f"{phase}-{intent}-attempt-") + r"([0-9]{6})(?:\.response)?\.json"
    )
    result: list[dict] = []
    for path in sorted(root.iterdir()):
        if pattern.fullmatch(path.name):
            result.append({"path": str(path.relative_to(run)), "sha256": sha(path)})
    return result


def validate_submission_receipt(run: Path, phase: str, job: str, value: dict) -> dict:
    req(
        value.get("schema") == "h11-submission-receipt-v1"
        and value.get("status") == "PASS_EXACT_UNIQUE_HELD_JOB_DURABLE_BEFORE_RELEASE"
        and value.get("phase") == phase
        and value.get("job_id") == job,
        "submission receipt identity",
    )
    req(
        (value.get("h11"), value.get("h10"), value.get("h9"), value.get("h8"), value.get("h7"))
        == (H11_SHA, H10_SHA, H9_SHA, H8_SHA, H7_SHA),
        "submission anchors",
    )
    req(value.get("run_root") == str(run), "submission run root")
    intent = value["intent_sha256"]
    intent_path, archive = intent_paths(run, phase, intent)
    intent_value = json_mode(intent_path)
    base = {key: item for key, item in intent_value.items() if key != "sbatch_argv"}
    req(canonical_sha(base) == intent, "submission intent binding")
    req(value["sbatch_argv"] == intent_value["sbatch_argv"], "submission sbatch argv")
    for key in (
        "dependency_afterok",
        "h11",
        "h10",
        "h9",
        "h8",
        "h7",
        "package_root",
        "run_root",
        "science_path",
        "science_sha256",
        "submitted_script_sha256",
        "submitted_script_binding_sha256",
        "phase_args",
        "phase_inputs",
    ):
        req(value.get(key) == intent_value.get(key), f"submission/intent field {key}")
    req(
        value.get("submitted_script_path") == str(archive.relative_to(run)),
        "submission archive path",
    )
    req(sha(archive) == value["submitted_script_sha256"] == intent_value["submitted_script_sha256"], "submission archive")
    discovery = value["held_squeue_discovery"]
    req(sha_bytes(discovery["raw_stdout"].encode()) == discovery["raw_stdout_sha256"], "submission squeue raw SHA")
    groups = parse_squeue(discovery["raw_stdout"], intent)
    req(set(groups) == {job}, "submission unique squeue replay")
    for row in groups[job]:
        req(row["state"] == "PENDING" and row["reason"] == "JobHeldUser", "submission squeue held replay")
    dispatch = value.get("dispatch_receipts")
    req(isinstance(dispatch, list) and dispatch, "submission dispatch receipts")
    dispatch_paths: list[str] = []
    for item in dispatch:
        req(set(item) == {"path", "sha256"} and HEX.fullmatch(item["sha256"]) is not None, "dispatch receipt schema")
        path = safe_rel(item["path"])
        req(
            item["path"].startswith(f"artifacts/h11_dispatch/{phase}-{intent}-attempt-")
            and sha(run / path) == item["sha256"],
            "dispatch receipt replay",
        )
        dispatch_paths.append(item["path"])
    req(len(dispatch_paths) == len(set(dispatch_paths)), "duplicate dispatch receipt")
    validate_held(value["held_scontrol_readback"], job, intent, run, value["dependency_afterok"])
    req(value.get("authorizes_scientific_release") is False, "submission authority")
    return intent_value


def validate_release_receipt(run: Path, phase: str, job: str, submission: dict, value: dict) -> None:
    req(
        value.get("schema") == "h11-release-receipt-v1"
        and value.get("phase") == phase
        and value.get("job_id") == job
        and value.get("intent_sha256") == submission["intent_sha256"]
        and value.get("submission_receipt_sha256") == sha(submission_path(run, phase, job))
        and value.get("h11") == H11_SHA,
        "release receipt identity",
    )
    req(
        value.get("status")
        in (
            "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT",
            "RECOVERED_ALREADY_RELEASED_AFTER_DURABLE_RELEASE_INTENT",
        ),
        "release receipt status",
    )
    release_intent = json_mode(release_intent_path(run, phase, job))
    req(
        release_intent.get("schema") == "h11-release-intent-v1"
        and release_intent.get("job_id") == job
        and release_intent.get("intent_sha256") == submission["intent_sha256"]
        and release_intent.get("submission_receipt_sha256")
        == value["submission_receipt_sha256"],
        "release intent replay",
    )
    if value["status"] == "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT":
        validate_held(
            value["pre_release_scontrol"],
            job,
            submission["intent_sha256"],
            run,
            submission["dependency_afterok"],
        )
    else:
        validate_released(
            value["pre_release_scontrol"],
            job,
            submission["intent_sha256"],
            run,
            submission["dependency_afterok"],
        )
    validate_released(
        value["post_release_scontrol"],
        job,
        submission["intent_sha256"],
        run,
        submission["dependency_afterok"],
    )
    release_call = value["release_call"]
    req(sha_bytes(release_call["raw_stdout"].encode()) == release_call["raw_stdout_sha256"], "release stdout SHA")
    req(sha_bytes(release_call["raw_stderr"].encode()) == release_call["raw_stderr_sha256"], "release stderr SHA")
    if value["status"] == "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT":
        req(
            len(release_call["argv"]) == 3
            and release_call["argv"][1:] == ["release", job],
            "release argv",
        )
    else:
        req(release_call["argv"] == [], "recovered release argv")
    req(value.get("authorizes_scientific_release") is False, "release authority")


def release_job(
    run: Path,
    phase: str,
    job: str,
    submission: dict,
    squeue: str,
    scontrol: str,
) -> dict:
    release_receipt_path = release_path(run, phase, job)
    if release_receipt_path.exists():
        value = json_mode(release_receipt_path)
        validate_release_receipt(run, phase, job, submission, value)
        return value
    intent = submission["intent_sha256"]
    discovery = discover(squeue, intent)
    req(len(discovery["groups"]) <= 1, "duplicate same-comment jobs before release")
    req(not discovery["groups"] or set(discovery["groups"]) == {job}, "different same-comment job before release")
    release_intent = release_intent_path(run, phase, job)
    intent_value = {
        "schema": "h11-release-intent-v1",
        "status": "ABOUT_TO_RELEASE_DURABLE_SUBMISSION_AUTHORITY_FALSE",
        "phase": phase,
        "job_id": job,
        "intent_sha256": intent,
        "submission_receipt_sha256": sha(submission_path(run, phase, job)),
        "h11": H11_SHA,
    }
    existed = release_intent.exists()
    if existed:
        req(json_mode(release_intent) == intent_value, "release intent drift")
    else:
        exclusive(release_intent, intent_value)
    if os.environ.get("H11_TEST_CRASH_AFTER_RELEASE_INTENT") == "1":
        raise RuntimeError("H11 injected post-release-intent crash")
    pre = show(scontrol, job)
    fields = validate_scontrol_common(pre, job, intent, run, submission["dependency_afterok"])
    if fields["JobState"] == "PENDING" and fields["Reason"] == "JobHeldUser":
        release_argv = [scontrol, "release", job]
        completed = subprocess.run(release_argv, capture_output=True, check=True)
        release_call = {
            "argv": release_argv,
            "raw_stdout": completed.stdout.decode(),
            "raw_stdout_sha256": sha_bytes(completed.stdout),
            "raw_stderr": completed.stderr.decode(),
            "raw_stderr_sha256": sha_bytes(completed.stderr),
        }
        status = "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT"
    else:
        req(existed, "job released before durable release intent")
        validate_released(pre, job, intent, run, submission["dependency_afterok"])
        release_call = {
            "argv": [],
            "raw_stdout": "",
            "raw_stdout_sha256": sha_bytes(b""),
            "raw_stderr": "",
            "raw_stderr_sha256": sha_bytes(b""),
        }
        status = "RECOVERED_ALREADY_RELEASED_AFTER_DURABLE_RELEASE_INTENT"
    if os.environ.get("H11_TEST_CRASH_AFTER_SCONTROL_RELEASE") == "1":
        raise RuntimeError("H11 injected post-scontrol-release crash")
    post = show(scontrol, job)
    validate_released(post, job, intent, run, submission["dependency_afterok"])
    value = {
        "schema": "h11-release-receipt-v1",
        "status": status,
        "phase": phase,
        "job_id": job,
        "intent_sha256": intent,
        "submission_receipt_sha256": sha(submission_path(run, phase, job)),
        "h11": H11_SHA,
        "pre_release_scontrol": pre,
        "release_call": release_call,
        "post_release_scontrol": post,
        "authorizes_scientific_release": False,
    }
    exclusive(release_receipt_path, value)
    return value


def parse_nonarray(raw: str, job: str) -> list[dict]:
    lines = [line for line in raw.splitlines() if line]
    req(len(lines) == 1, "nonarray sacct row count")
    parts = lines[0].split("|")
    req(
        len(parts) == 5
        and parts[0] == job
        and parts[1] == job
        and parts[2] == "COMPLETED"
        and parts[3] == "0:0"
        and parts[4].isdecimal(),
        "nonarray live sacct shape",
    )
    return [
        {
            "job_id_raw": parts[0],
            "job_id": parts[1],
            "state": parts[2],
            "exit_code": parts[3],
            "elapsed_raw": int(parts[4]),
            "array_job_id": None,
            "array_task_id": None,
        }
    ]


def parse_array(raw: str, parent: str) -> list[dict]:
    lines = [line for line in raw.splitlines() if line]
    req(len(lines) == 480, "array live sacct row count")
    rows: dict[int, dict] = {}
    raw_ids: set[str] = set()
    for line in lines:
        parts = line.split("|")
        req(
            len(parts) == 5
            and parts[0].isdecimal()
            and parts[2] == "COMPLETED"
            and parts[3] == "0:0"
            and parts[4].isdecimal(),
            "array live sacct field shape",
        )
        match = re.fullmatch(re.escape(parent) + r"_([0-9]+)", parts[1])
        req(match is not None, "array JobID shape")
        task = int(match.group(1))
        req(task not in rows and parts[0] not in raw_ids, "array duplicate identity")
        raw_ids.add(parts[0])
        rows[task] = {
            "job_id_raw": parts[0],
            "job_id": parts[1],
            "state": parts[2],
            "exit_code": parts[3],
            "elapsed_raw": int(parts[4]),
            "array_job_id": parent,
            "array_task_id": task,
        }
    req(set(rows) == set(range(480)), "array exact task set")
    return [rows[index] for index in range(480)]


def accounting(run: Path, phase: str, job: str, sacct: str = "sacct") -> tuple[dict, Path]:
    fields = "JobIDRaw,JobID,State,ExitCode,ElapsedRaw"
    argv = [sacct, "-X"] + (["--array"] if phase == "production" else []) + [
        "-j",
        job,
        "-n",
        "-P",
        "-o",
        fields,
    ]
    completed = subprocess.run(argv, capture_output=True, check=True)
    raw = completed.stdout.decode()
    rows = parse_array(raw, job) if phase == "production" else parse_nonarray(raw, job)
    value = {
        "schema": "h11-accounting-receipt-v1",
        "status": "PASS_EXACT_LIVE_SACCT_TERMINAL_BINDING",
        "phase": phase,
        "parent_job_id": job,
        "h11": H11_SHA,
        "h10": H10_SHA,
        "argv": argv,
        "raw_stdout": raw,
        "raw_stdout_sha256": sha_bytes(completed.stdout),
        "rows": rows,
        "authorizes_scientific_release": False,
    }
    path = accounting_path(run, phase, job)
    if not path.exists():
        exclusive(path, value)
    else:
        req(json_mode(path) == value, "accounting receipt drift")
    return value, path


def runtime_identity(row: dict) -> dict:
    return {
        "job_id_raw": row["job_id_raw"],
        "job_id": row["job_id"],
        "array_job_id": row["array_job_id"],
        "array_task_id": row["array_task_id"],
    }


def validate_submission(run: Path, phase: str, job: str) -> dict:
    path = submission_path(run, phase, job)
    value = json_mode(path)
    validate_submission_receipt(run, phase, job, value)
    release_receipt = json_mode(release_path(run, phase, job))
    validate_release_receipt(run, phase, job, value, release_receipt)
    return value


def validate_runtime(run: Path, phase: str, job: str, submission: dict, accounting_value: dict) -> list[tuple[Path, dict]]:
    root = run / "artifacts/h11_receipts"
    paths = (
        [root / f"production-{job}_{index}.json" for index in range(480)]
        if phase == "production"
        else [root / f"{phase}-{job}.json"]
    )
    result: list[tuple[Path, dict]] = []
    for index, path in enumerate(paths):
        value = json_mode(path)
        row = accounting_value["rows"][index]
        req(
            value.get("schema") == "h11-runtime-receipt-v1"
            and value.get("status") == "PASS_H11_RUNTIME_IDENTITY_AND_TRANSACTION_COMMITTED"
            and value.get("phase") == phase,
            "runtime receipt schema",
        )
        req(
            (value.get("h11"), value.get("h10"), value.get("h9"), value.get("h8"), value.get("h7"))
            == (H11_SHA, H10_SHA, H9_SHA, H8_SHA, H7_SHA),
            "runtime receipt anchors",
        )
        req(value.get("runtime_identity") == runtime_identity(row), "runtime/accounting identity join")
        req(value.get("terminal_accounting_claimed_at_runtime") is False, "runtime terminal claim")
        req(
            value.get("submitted_script_sha256") == submission["submitted_script_sha256"]
            and value.get("submitted_script_binding_sha256") == submission["submitted_script_binding_sha256"],
            "runtime submitted script binding",
        )
        req(
            value.get("science_source", {}).get("path") == submission["science_path"]
            and value.get("science_source", {}).get("sha256") == submission["science_sha256"],
            "runtime science binding",
        )
        req(
            value.get("phase_inputs") == submission["phase_inputs"]
            and value.get("phase_args_sha256")
            == sha_bytes(json.dumps(submission["phase_args"], separators=(",", ":")).encode()),
            "runtime phase inputs/argv",
        )
        outputs = value.get("outputs")
        req(isinstance(outputs, list), "runtime outputs")
        names: list[str] = []
        for item in outputs:
            req(set(item) == {"path", "sha256"} and HEX.fullmatch(item["sha256"]) is not None, "runtime output schema")
            names.append(item["path"])
            target = run / safe_rel(item["path"])
            info = target.lstat()
            req(
                stat.S_ISREG(info.st_mode)
                and not target.is_symlink()
                and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == 0o600
                and sha(target) == item["sha256"],
                "runtime output drift",
            )
        req(len(names) == len(set(names)), "duplicate runtime output")
        result.append((path, value))
    return result


def prior_gate(run: Path, phase: str, job: str, sacct: str = "sacct") -> dict:
    submission = validate_submission(run, phase, job)
    accounting_value, accounting_receipt = accounting(run, phase, job, sacct)
    runtime_values = validate_runtime(run, phase, job, submission, accounting_value)
    return {
        "submission": submission,
        "accounting": accounting_value,
        "accounting_path": accounting_receipt,
        "runtime": runtime_values,
    }


def submit(
    package: Path,
    run: Path,
    phase: str,
    args: list[str],
    input_values: list[str],
    dependency: str | None = None,
    sbatch: str = "sbatch",
    squeue: str = "squeue",
    scontrol: str = "scontrol",
    sacct: str = "sacct",
) -> dict:
    req(phase in SCRIPTS, "phase")
    package = trusted_abs(package)
    run = trusted_abs(run, False)
    req(package != run and package not in run.parents and run not in package.parents, "roots mixed")
    rows = verify_package(package)
    run.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(run, 0o700)
    (run / "logs").mkdir(exist_ok=True, mode=0o700)
    (run / "artifacts").mkdir(exist_ok=True, mode=0o700)
    os.chmod(run / "logs", 0o700)
    os.chmod(run / "artifacts", 0o700)
    if phase in ORDER and ORDER.index(phase) > 0:
        req(dependency is not None and dependency.isdecimal(), "missing dependency")
        prior_gate(run, ORDER[ORDER.index(phase) - 1], dependency, sacct)
    if phase == "selftest_downstream":
        req(dependency is not None and dependency.isdecimal(), "missing selftest dependency")
        prior_gate(run, "selftest_upstream", dependency, sacct)
    inputs = phase_inputs(run, input_values)
    script, binding, exact_script_sha = render(package, run, phase, args, inputs, rows)
    base = intent_base(
        package,
        run,
        phase,
        dependency,
        args,
        inputs,
        rows,
        exact_script_sha,
        binding,
        sbatch,
    )
    intent, intent_value, _ = prepare_intent(run, phase, base, script)
    if os.environ.get("H11_TEST_CRASH_AFTER_INTENT") == "1":
        raise RuntimeError("H11 injected post-intent pre-dispatch crash")
    existing = find_submission(run, phase, intent)
    if existing:
        path, submission = existing
        req(path == submission_path(run, phase, submission["job_id"]), "submission path")
        validate_submission_receipt(run, phase, submission["job_id"], submission)
        release_receipt = release_job(run, phase, submission["job_id"], submission, squeue, scontrol)
        return {"submission": submission, "release": release_receipt}
    job, discovery = dispatch_or_discover(run, phase, intent, intent_value, script, squeue)
    held = show(scontrol, job)
    validate_held(held, job, intent, run, dependency)
    submission = {
        "schema": "h11-submission-receipt-v1",
        "status": "PASS_EXACT_UNIQUE_HELD_JOB_DURABLE_BEFORE_RELEASE",
        "phase": phase,
        "job_id": job,
        "intent_sha256": intent,
        "dependency_afterok": dependency,
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "package_root": str(package),
        "run_root": str(run),
        "science_path": SCRIPTS[phase],
        "science_sha256": rows[SCRIPTS[phase]],
        "submitted_script_path": str(intent_paths(run, phase, intent)[1].relative_to(run)),
        "submitted_script_sha256": exact_script_sha,
        "submitted_script_binding_sha256": binding,
        "phase_args": args,
        "phase_inputs": inputs,
        "sbatch_argv": intent_value["sbatch_argv"],
        "dispatch_receipts": attempt_receipts(run, phase, intent),
        "held_squeue_discovery": discovery,
        "held_scontrol_readback": held,
        "authorizes_scientific_release": False,
    }
    path = submission_path(run, phase, job)
    exclusive(path, submission)
    if os.environ.get("H11_TEST_CRASH_AFTER_SUBMISSION_RECEIPT") == "1":
        raise RuntimeError("H11 injected post-submission-receipt pre-release crash")
    release_receipt = release_job(run, phase, job, submission, squeue, scontrol)
    return {"submission": submission, "release": release_receipt}


def finalize(run: Path, jobs: dict, sacct: str = "sacct") -> dict:
    run = trusted_abs(run)
    req(set(jobs) == set(ORDER) and len(set(map(str, jobs.values()))) == len(ORDER), "final job set")
    previous: str | None = None
    phases: list[dict] = []
    for phase in ORDER:
        job = str(jobs[phase])
        req(job.isdecimal(), "final job identity")
        gate = prior_gate(run, phase, job, sacct)
        req(gate["submission"]["dependency_afterok"] == previous, "final dependency chain")
        phases.append(
            {
                "phase": phase,
                "job_id": job,
                "submission_sha256": sha(submission_path(run, phase, job)),
                "release_sha256": sha(release_path(run, phase, job)),
                "accounting_path": str(gate["accounting_path"].relative_to(run)),
                "accounting_sha256": sha(gate["accounting_path"]),
                "accounting_raw_stdout_sha256": gate["accounting"]["raw_stdout_sha256"],
                "runtime_receipts": [
                    {"path": str(path.relative_to(run)), "sha256": sha(path)}
                    for path, _ in gate["runtime"]
                ],
            }
        )
        previous = job
    value = {
        "schema": "grid2d-v4-r2-h11-terminal-candidate-v1",
        "status": "PASS_H11_RECOVERED_LIVE_ACCOUNTING_TRANSACTION_NO_AUTHORITY",
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "highest_root_authority": "H11",
        "phases": phases,
        "authorizes_execution": False,
        "authorizes_scientific_release": False,
    }
    output = run / "artifacts/h11_final/terminal-candidate.json"
    exclusive(output, value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--package-root", type=Path, required=True)
    submit_parser.add_argument("--run-root", type=Path, required=True)
    submit_parser.add_argument("--phase", choices=SCRIPTS, required=True)
    submit_parser.add_argument("--dependency")
    submit_parser.add_argument("--phase-input", action="append", default=[])
    submit_parser.add_argument("stage_args", nargs="*")
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--run-root", type=Path, required=True)
    finalize_parser.add_argument("--jobs-json", required=True)
    args = parser.parse_args()
    result = (
        submit(
            args.package_root,
            args.run_root,
            args.phase,
            args.stage_args,
            args.phase_input,
            args.dependency,
        )
        if args.command == "submit"
        else finalize(args.run_root, json.loads(args.jobs_json))
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
