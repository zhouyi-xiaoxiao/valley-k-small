#!/opt/cray/pe/python/3.11.7/bin/python3.11 -I
"""Detached H13 controller with an isolated entrypoint and versioned authority input."""
from __future__ import annotations

import sys

if __name__ == "__main__" and not (
    sys.flags.isolated and sys.flags.ignore_environment and sys.flags.no_user_site
):
    print("FAIL-CLOSED: H13 controller requires the absolute -I isolated shebang", file=sys.stderr)
    raise SystemExit(126)

import argparse
import base64
import contextlib
import fcntl
import hashlib
import json
import os
import pwd
import re
import shlex
import stat
import subprocess
import types
from pathlib import Path

H13_SHA = "__H13_PAYLOAD_SHA_PENDING__"
H12_SHA = "bcc487d9910dd6cb5732f26ca18caecd20b7a24844083fd61b89c361fdae0e0a"
H11_SHA = "dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca"
H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
H9_SHA = "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA = "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
H11_CONTROLLER_SHA = "776ef08bd2c54e22bfb4acc3863da37e9c18c0beb7e101e5824777c490732f2f"
MAN = "notes/isambard_ai_v4_r2_h13_payload.sha256"
H12_MAN = "notes/isambard_ai_v4_r2_h12_payload.sha256"
RUNTIME = "code/h13_runtime_v4_r2.py"
ZERO = "0" * 64
HEX = re.compile(r"[0-9a-f]{64}")
SAFE_ABS = re.compile(r"/[A-Za-z0-9._/@+-]+")
DEFAULT_TOOLS = {
    "sbatch": "/usr/bin/sbatch",
    "squeue": "/usr/bin/squeue",
    "scontrol": "/usr/bin/scontrol",
    "sacct": "/usr/bin/sacct",
}
CONTROL_PYTHON = "/opt/cray/pe/python/3.11.7/bin/python3.11"
CONTROL_PYTHON_SHA256 = "9270f0548999f7c4fa66df1c4fd4ec6a7edfc54ff5b8bd881d89a2cc891f6b94"
DENIED_ENV = {
    "BASH_ENV",
    "ENV",
    "CDPATH",
    "GLOBIGNORE",
    "SHELLOPTS",
    "BASHOPTS",
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONINSPECT",
    "PYTHONBREAKPOINT",
    "LD_PRELOAD",
    "LD_LIBRARY_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
}
AUTHORITY_INPUT_SCHEMA = "h13-secondary-authority-cli-v1"
SECONDARY_RELEASE_SCHEMA = "__SECONDARY_R5_RELEASE_SCHEMA_PENDING__"
SECONDARY_RELEASE_STATUS = "__SECONDARY_R5_RELEASE_STATUS_PENDING__"
SECONDARY_AUDIT_SCHEMA = "__SECONDARY_R5_AUDIT_SCHEMA_PENDING__"
SECONDARY_AUDIT_STATUS = "__SECONDARY_R5_AUDIT_STATUS_PENDING__"
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


def load_h11_controller():
    path = Path(__file__).with_name("h11_pinned_controller_v4_r2.py")
    raw = path.read_bytes()
    req(sha_bytes(raw) == H11_CONTROLLER_SHA, "externally pinned H11 controller drift")
    module = types.ModuleType("h13_pinned_h11_controller_base")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


base = load_h11_controller()
CAMPAIGN_ORDER = ("v3_authority_h13", "canary", "production")
SCIENCE_SCRIPTS = {
    "v3_authority_h13": "code/isambard_ai_gating_v4_r2_v3_authority_h13.sbatch",
    "canary": "code/isambard_ai_gating_v4_r2_gpu_canary_h13.sbatch",
    "production": "code/isambard_ai_gating_v4_r2_fullnode_h13.sbatch",
}
SCRIPTS = {phase: SCIENCE_SCRIPTS[phase] for phase in CAMPAIGN_ORDER}
SELFTEST_PHASES: tuple[str, ...] = ()


def verify_package(root: Path) -> dict[str, str]:
    req(HEX.fullmatch(H13_SHA) is not None and H13_SHA != ZERO, "H13 pin unset")
    root = trusted_abs(root)
    req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode) == 0o700, "package root mode")
    manifest = root / MAN
    req(manifest.is_file() and not manifest.is_symlink() and sha(manifest) == H13_SHA, "externally pinned H13 drift")
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
    req(actual == set(rows) | {MAN}, "closed H13 package inventory")
    for name, digest in rows.items():
        req(sha(root / name) == digest, f"package member drift {name}")
    req(sha(root / H12_MAN) == H12_SHA, "H12 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h11_payload.sha256") == H11_SHA, "H11 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h10_payload.sha256") == H10_SHA, "H10 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h9_payload.sha256") == H9_SHA, "H9 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h8_payload.sha256") == H8_SHA, "H8 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h7_payload.sha256") == H7_SHA, "H7 ancestor drift")
    return rows


def secure_root_executable(path: Path | str, allow_user_owned: bool = False) -> dict:
    original = Path(path)
    req(original.is_absolute() and original.exists(), "executable missing")
    resolved = original.resolve(strict=True)
    info = resolved.stat()
    allowed_uids = {0, os.getuid()} if allow_user_owned else {0}
    req(
        stat.S_ISREG(info.st_mode)
        and info.st_uid in allowed_uids
        and not (stat.S_IMODE(info.st_mode) & 0o022)
        and os.access(resolved, os.X_OK),
        "executable authority",
    )
    probe = resolved.parent
    while True:
        item = probe.stat()
        req(
            stat.S_ISDIR(item.st_mode)
            and item.st_uid in allowed_uids
            and not (stat.S_IMODE(item.st_mode) & 0o022),
            "executable ancestor authority",
        )
        if probe == probe.parent:
            break
        probe = probe.parent
    return {
        "path": str(resolved),
        "sha256": sha(resolved),
        "device": info.st_dev,
        "inode": info.st_ino,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
    }


def tool_anchors(paths: dict[str, str] | None = None) -> dict[str, dict]:
    chosen = DEFAULT_TOOLS if paths is None else paths
    req(set(chosen) == set(DEFAULT_TOOLS), "scheduler tool set")
    return {name: secure_root_executable(chosen[name]) for name in sorted(chosen)}


def python_anchor(phase: str) -> dict:
    del phase
    authority = secure_root_executable(Path(sys.executable))
    req(
        authority["path"] == CONTROL_PYTHON
        and authority["sha256"] == CONTROL_PYTHON_SHA256,
        "H13 control Python authority",
    )
    return authority


def revalidate_anchor(anchor: dict) -> None:
    path = Path(anchor["path"])
    info = path.stat()
    req(
        stat.S_ISREG(info.st_mode)
        and info.st_dev == anchor["device"]
        and info.st_ino == anchor["inode"]
        and info.st_size == anchor["size"]
        and info.st_mtime_ns == anchor["mtime_ns"]
        and stat.S_IMODE(info.st_mode) == anchor["mode"]
        and info.st_uid == anchor["uid"]
        and sha(path) == anchor["sha256"],
        "scheduler executable changed",
    )


def control_environment() -> dict[str, str]:
    account = pwd.getpwuid(os.getuid())
    return {
        "HOME": account.pw_dir,
        "USER": account.pw_name,
        "LOGNAME": account.pw_name,
        "SHELL": "/bin/bash",
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
    }


class SchedulerSubprocess:
    CalledProcessError = subprocess.CalledProcessError

    def __init__(self, anchors: dict[str, dict]):
        self.anchors = anchors
        self.by_path = {value["path"]: value for value in anchors.values()}

    def run(self, argv, *args, **kwargs):
        req(
            isinstance(argv, list)
            and argv
            and isinstance(argv[0], str)
            and argv[0] in self.by_path,
            "unanchored scheduler executable",
        )
        req("env" not in kwargs, "scheduler environment supplied by caller")
        anchor = self.by_path[argv[0]]
        revalidate_anchor(anchor)
        completed = subprocess.run(argv, *args, env=control_environment(), **kwargs)
        revalidate_anchor(anchor)
        return completed


def environment_policy() -> dict:
    return {
        "submission_export": "NIL",
        "wrapper_path": "/usr/bin:/bin",
        "denied_environment": sorted(DENIED_ENV),
        "deny_exported_shell_functions": True,
        "science_environment": "explicit-slurm-gpu-identity-allowlist",
        "science_shell": "/bin/bash --noprofile --norc",
    }


def authority_contract_ready() -> None:
    values = (
        H13_SHA,
        CONTROL_PYTHON_SHA256,
        SECONDARY_RELEASE_SCHEMA,
        SECONDARY_RELEASE_STATUS,
        SECONDARY_AUDIT_SCHEMA,
        SECONDARY_AUDIT_STATUS,
        SECONDARY_R5_PAYLOAD_SHA256,
        SECONDARY_R5_CONTRACT_SHA256,
        SECONDARY_R5_CONTAINER_SHA256,
        SECONDARY_R5_INDEPENDENT_AUDIT_MEMBER,
        SECONDARY_R5_INDEPENDENT_AUDIT_SHA256,
        SECONDARY_R5_INDEPENDENT_AUDIT_DECISION_MARKER,
    )
    req(all("PENDING" not in value and "__" not in value for value in values), "H13/R5 authority contract pending")


def parse_secondary_accounting(raw: str, job: str) -> dict:
    lines = [line for line in raw.splitlines() if line]
    req(len(lines) == 1, "secondary authority sacct row count")
    parts = lines[0].split("|")
    req(
        len(parts) == 5
        and parts[0] == parts[1] == job
        and parts[2].split("+", 1)[0] == "COMPLETED"
        and parts[3] == "0:0"
        and parts[4].isdecimal()
        and int(parts[4]) > 0,
        "secondary authority sacct terminal binding",
    )
    return {
        "job_id_raw": parts[0],
        "job_id": parts[1],
        "state": "COMPLETED",
        "exit_code": parts[3],
        "elapsed_raw": int(parts[4]),
    }


def secondary_accounting(
    run: Path,
    job: str,
    publication_name: str,
    anchors: dict[str, dict],
) -> tuple[Path, str]:
    req(job.isdecimal() and int(job) > 0, "secondary authority job id")
    req(
        re.fullmatch(r"[A-Za-z0-9._-]+", publication_name) is not None
        and publication_name.endswith(f"-{job}"),
        "secondary authority publication/job identity",
    )
    sacct = anchors["sacct"]["path"]
    argv = [
        sacct,
        "-X",
        "-j",
        job,
        "-n",
        "-P",
        "-o",
        "JobIDRaw,JobID,State,ExitCode,ElapsedRaw",
    ]
    completed = SchedulerSubprocess(anchors).run(argv, capture_output=True, check=True)
    raw = completed.stdout.decode()
    value = {
        "schema": "h13-secondary-authority-accounting-v1",
        "status": "PASS_EXACT_LIVE_SACCT_TERMINAL_BINDING",
        "h13": H13_SHA,
        "job_id": job,
        "publication_name": publication_name,
        "argv": argv,
        "raw_stdout": raw,
        "raw_stdout_sha256": sha_bytes(completed.stdout),
        "row": parse_secondary_accounting(raw, job),
        "scheduler_tool": anchors["sacct"],
        "authorizes_scientific_release": False,
    }
    path = run / "artifacts/h13_external_accounting" / f"secondary-{job}.json"
    if path.exists():
        req(base.json_mode(path) == value, "secondary authority accounting replay drift")
    else:
        base.exclusive(path, value)
    return path, sha(path)


def render(
    package: Path,
    run: Path,
    phase: str,
    args: list[str],
    inputs: list[dict],
    rows: dict[str, str],
) -> tuple[bytes, str, str]:
    science = base.capture(package, SCIENCE_SCRIPTS[phase], rows)
    runtime = base.capture(package, RUNTIME, rows)
    directives: list[str] = []
    for line in science.decode().splitlines()[1:]:
        if line.startswith("#SBATCH") and not any(
            value in line for value in ("--chdir", "--output", "--error", "--export")
        ):
            directives.append(line)
    interpreter = python_anchor(phase)
    test_name = None
    if phase in ("selftest_upstream", "selftest_downstream"):
        test_name = os.environ.get("H9_TEST_OUTPUT_NAME")
        req(
            isinstance(test_name, str)
            and re.fullmatch(r"[A-Za-z0-9._-]+", test_name) is not None,
            "selftest output name",
        )
    policy = environment_policy()
    config = {
        "schema": "h13-runtime-config-v1",
        "phase": "production" if phase == "production" else phase,
        "package_root": str(package),
        "run_root": str(run),
        "h13": H13_SHA,
        "h12": H12_SHA,
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "science_path": SCIENCE_SCRIPTS[phase],
        "science_sha256": sha_bytes(science),
        "science_bytes_hex": science.hex(),
        "phase_args": args,
        "phase_inputs": inputs,
        "python_interpreter": interpreter,
        "environment_policy_sha256": sha_bytes(
            json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()
        ),
        "selftest_output_name": test_name,
    }
    runtime_b64 = base64.b64encode(runtime).decode()
    config_b64 = base64.b64encode(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).decode()
    python_path = shlex.quote(interpreter["path"])
    lines = [
        "#!/bin/bash",
        *directives,
        "#SBATCH --export=NIL",
        f"#SBATCH --chdir={run}",
        f"#SBATCH --output={run}/logs/%x-%A_%a.out",
        f"#SBATCH --error={run}/logs/%x-%A_%a.err",
        "set -euo pipefail",
        "umask 077",
        "unset BASH_ENV ENV CDPATH GLOBIGNORE PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONBREAKPOINT LD_PRELOAD LD_LIBRARY_PATH DYLD_INSERT_LIBRARIES DYLD_LIBRARY_PATH",
        "export PATH=/usr/bin:/bin LC_ALL=C LANG=C",
        f"export H11_EXPECTED_BINDING_SHA256={ZERO}",
        'export H11_SUBMITTED_SCRIPT_PATH="$0"',
        '[[ -n "${SLURM_TMPDIR:-}" && "${SLURM_TMPDIR#/}" != "$SLURM_TMPDIR" ]] || exit 90',
        'launch="$(/usr/bin/mktemp -d "$SLURM_TMPDIR/h13-launch.XXXXXX")"',
        "trap '/bin/rm -rf -- \"$launch\"' EXIT",
        f'/usr/bin/printf %s {runtime_b64} | /usr/bin/base64 -d > "$launch/runtime.py"',
        f'/usr/bin/printf %s {config_b64} | /usr/bin/base64 -d > "$launch/config.json"',
        '/bin/chmod 400 "$launch/runtime.py" "$launch/config.json"',
        f'{python_path} -I -B -E -s "$launch/runtime.py" --config "$launch/config.json"',
    ]
    template = ("\n".join(lines) + "\n").encode()
    binding = sha_bytes(template)
    final = template.replace(
        f"H11_EXPECTED_BINDING_SHA256={ZERO}".encode(),
        f"H11_EXPECTED_BINDING_SHA256={binding}".encode(),
    )
    req(final != template, "binding insertion")
    return final, binding, sha_bytes(final)


def prepare_intent(
    run: Path,
    phase: str,
    intent_base: dict,
    script: bytes,
) -> tuple[str, dict, Path]:
    intent = canonical_sha(intent_base)
    comment = f"H11:{intent}"
    argv = [
        intent_base["sbatch_executable"],
        "--parsable",
        "--hold",
        "--export=NIL",
        f"--comment={comment}",
        f"--chdir={run}",
    ]
    if intent_base["dependency_afterok"] is not None:
        argv.append(f"--dependency=afterok:{intent_base['dependency_afterok']}")
    value = {**intent_base, "sbatch_argv": argv}
    intent_path, archive = base.intent_paths(run, phase, intent)
    if intent_path.exists():
        req(base.json_mode(intent_path) == value, "existing intent drift")
        req(sha(archive) == intent_base["submitted_script_sha256"], "existing archive drift")
    else:
        if not archive.exists():
            base.exclusive(archive, script)
        else:
            req(sha(archive) == intent_base["submitted_script_sha256"], "intent archive collision")
        base.exclusive(intent_path, value)
    return intent, value, archive


@contextlib.contextmanager
def hardened_base(anchors: dict[str, dict]):
    names = ("verify_package", "render", "prepare_intent", "subprocess", "SCRIPTS", "ORDER")
    previous = {name: getattr(base, name) for name in names}
    base.verify_package = verify_package
    base.render = render
    base.prepare_intent = prepare_intent
    base.subprocess = SchedulerSubprocess(anchors)
    base.SCRIPTS = dict(SCRIPTS)
    base.ORDER = tuple(CAMPAIGN_ORDER)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(base, name, value)


@contextlib.contextmanager
def controller_lock(run: Path):
    run.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(run, 0o700)
    path = run / ".h13-controller.lock"
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        req(
            stat.S_ISREG(info.st_mode)
            and info.st_nlink == 1
            and stat.S_IMODE(info.st_mode) == 0o600,
            "controller lock inode",
        )
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def envelope_path(run: Path, phase: str, job: str) -> Path:
    return run / "artifacts/h13_envelopes" / f"{phase}-{job}.json"


def validate_envelope(run: Path, phase: str, job: str) -> dict:
    path = envelope_path(run, phase, job)
    value = base.json_mode(path)
    req(
        value.get("schema") == "h13-execution-envelope-v1"
        and value.get("status") == "PASS_H13_ISOLATED_ENVIRONMENT_AND_PINNED_EXECUTABLES"
        and value.get("phase") == phase
        and value.get("job_id") == job
        and value.get("h13") == H13_SHA
        and value.get("h12") == H12_SHA
        and value.get("h11") == H11_SHA,
        "H13 envelope identity",
    )
    req(
        value.get("submission_sha256") == sha(base.submission_path(run, phase, job))
        and value.get("release_sha256") == sha(base.release_path(run, phase, job)),
        "H13 envelope legacy receipt binding",
    )
    submission = base.json_mode(base.submission_path(run, phase, job))
    argv = submission["sbatch_argv"]
    req(
        argv.count("--export=NIL") == 1
        and Path(argv[0]).is_absolute()
        and submission["submitted_script_sha256"] == value["submitted_script_sha256"],
        "H13 envelope submission policy",
    )
    return value


def validate_h13_prior(run: Path, phase: str, job: str) -> None:
    validate_envelope(run, phase, job)
    root = run / "artifacts/h11_receipts"
    paths = (
        [root / f"production-{job}_{index}.json" for index in range(480)]
        if phase == "production"
        else [root / f"{phase}-{job}.json"]
    )
    for path in paths:
        value = base.json_mode(path)
        req(
            value.get("h13") == H13_SHA
            and value.get("h13_status") == "PASS_H13_ENVIRONMENT_ISOLATED_EXECUTION"
            and value.get("h12") == H12_SHA,
            "prior runtime lacks H13 environment authority",
        )


def submit(
    package: Path,
    run: Path,
    phase: str,
    args: list[str],
    input_values: list[str],
    dependency: str | None = None,
) -> dict:
    req(phase in SCRIPTS or phase in SELFTEST_PHASES, "phase")
    package = trusted_abs(package)
    run = trusted_abs(run, False)
    req(package != run and package not in run.parents and run not in package.parents, "roots mixed")
    verify_package(package)
    selected = tool_anchors()
    req(set(selected) == set(DEFAULT_TOOLS), "scheduler anchor set")
    for anchor in selected.values():
        revalidate_anchor(anchor)
    with controller_lock(run):
        authority_contract_ready()
        effective_args = list(args)
        effective_inputs = list(input_values)
        if phase == "v3_authority_h13":
            req(
                len(effective_args) >= 8
                and effective_args[0] == H13_SHA
                and effective_args[1] == AUTHORITY_INPUT_SCHEMA
                and effective_args[2] == SECONDARY_RELEASE_SCHEMA
                and effective_args[3] == SECONDARY_RELEASE_STATUS
                and effective_args[4] == SECONDARY_AUDIT_SCHEMA
                and effective_args[5] == SECONDARY_AUDIT_STATUS,
                "H13 versioned secondary authority CLI contract",
            )
            secondary_job = effective_args[6]
            publication_name = effective_args[7]
            accounting_path, accounting_sha = secondary_accounting(
                run, secondary_job, publication_name, selected
            )
            accounting_relative = accounting_path.relative_to(run).as_posix()
            effective_inputs.append(f"{accounting_relative}={accounting_sha}")
            effective_args = [
                *effective_args[:8],
                str(accounting_path),
                accounting_sha,
                *effective_args[8:],
            ]
        if phase in CAMPAIGN_ORDER and CAMPAIGN_ORDER.index(phase) > 0:
            req(dependency is not None and dependency.isdecimal(), "missing dependency")
            validate_h13_prior(
                run,
                CAMPAIGN_ORDER[CAMPAIGN_ORDER.index(phase) - 1],
                dependency,
            )
        with hardened_base(selected):
            result = base.submit(
                package,
                run,
                phase,
                effective_args,
                effective_inputs,
                dependency,
                selected["sbatch"]["path"],
                selected["squeue"]["path"],
                selected["scontrol"]["path"],
                selected["sacct"]["path"],
            )
        submission = result["submission"]
        job = submission["job_id"]
        req(
            submission["sbatch_argv"].count("--export=NIL") == 1
            and submission["sbatch_argv"][0] == selected["sbatch"]["path"],
            "submission export/tool policy",
        )
        value = {
            "schema": "h13-execution-envelope-v1",
            "status": "PASS_H13_ISOLATED_ENVIRONMENT_AND_PINNED_EXECUTABLES",
            "phase": phase,
            "job_id": job,
            "dependency_afterok": dependency,
            "h13": H13_SHA,
            "h12": H12_SHA,
            "h11": H11_SHA,
            "h10": H10_SHA,
            "h9": H9_SHA,
            "h8": H8_SHA,
            "h7": H7_SHA,
            "submission_sha256": sha(base.submission_path(run, phase, job)),
            "release_sha256": sha(base.release_path(run, phase, job)),
            "submitted_script_sha256": submission["submitted_script_sha256"],
            "submitted_script_binding_sha256": submission["submitted_script_binding_sha256"],
            "scheduler_tools": selected,
            "python_interpreter": python_anchor(phase),
            "environment_policy": environment_policy(),
            "authorizes_scientific_release": False,
        }
        path = envelope_path(run, phase, job)
        if path.exists():
            req(base.json_mode(path) == value, "existing H13 envelope drift")
        else:
            base.exclusive(path, value)
        validate_envelope(run, phase, job)
        return {"h13": value, **result}


def finalize(run: Path, jobs: dict) -> dict:
    run = trusted_abs(run)
    authority_contract_ready()
    req(
        set(jobs) == set(CAMPAIGN_ORDER)
        and len({str(value) for value in jobs.values()}) == len(CAMPAIGN_ORDER),
        "final H13 campaign job set",
    )
    selected = tool_anchors()
    with controller_lock(run):
        previous = None
        phases = []
        with hardened_base(selected):
            for phase in CAMPAIGN_ORDER:
                job = str(jobs[phase])
                req(job.isdecimal(), "final H13 job identity")
                validate_h13_prior(run, phase, job)
                gate = base.prior_gate(run, phase, job, selected["sacct"]["path"])
                req(
                    gate["submission"]["dependency_afterok"] == previous,
                    "final H13 dependency chain",
                )
                phases.append(
                    {
                        "phase": phase,
                        "job_id": job,
                        "h13_envelope_sha256": sha(envelope_path(run, phase, job)),
                        "submission_sha256": sha(
                            base.submission_path(run, phase, job)
                        ),
                        "release_sha256": sha(base.release_path(run, phase, job)),
                        "accounting_sha256": sha(gate["accounting_path"]),
                        "runtime_receipt_count": 480 if phase == "production" else 1,
                    }
                )
                previous = job
        value = {
            "schema": "grid2d-v4-r2-h13-production-campaign-candidate-v1",
            "status": "PASS_H13_960_NHR_CEILING_CAMPAIGN_NO_SCIENTIFIC_AUTHORITY",
            "h13": H13_SHA,
            "h12": H12_SHA,
            "h11": H11_SHA,
            "phases": phases,
            "production_shape": {
                "array": "0-479%240",
                "nodes_per_task": 1,
                "tasks_per_array_element": 4,
                "gpus_per_task": 1,
                "gpus_per_array_element": 4,
                "gpu_lanes_per_array_element": 4,
                "cells_per_array_element": 48,
                "total_cells": 23040,
                "full_node_exclusive_gpu_shape": True,
                "walltime_hours": 2,
                "maximum_node_hours": 960,
            },
            "tail_phases_authorized": False,
            "authorizes_execution": False,
            "authorizes_scientific_release": False,
        }
        output = run / "artifacts/h13_final/production-campaign-candidate.json"
        base.exclusive(output, value)
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
    except (
        ValueError,
        OSError,
        json.JSONDecodeError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"FAIL-CLOSED: {error}", file=sys.stderr)
        raise SystemExit(2)
