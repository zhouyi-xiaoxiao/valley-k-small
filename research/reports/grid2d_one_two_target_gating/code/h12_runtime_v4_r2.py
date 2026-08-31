#!/usr/bin/env python3
"""H12 environment-isolated overlay over the immutable H11 transaction runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pwd
import re
import stat
import subprocess
import sys
import types
from pathlib import Path

H11_SHA = "dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca"
H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
H9_SHA = "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA = "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
H12_MAN = "notes/isambard_ai_v4_r2_h12_payload.sha256"
H11_MAN = "notes/isambard_ai_v4_r2_h11_payload.sha256"
H11_RUNTIME = "code/h11_runtime_v4_r2.py"
OLD_ROOT = "/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"
HEX = re.compile(r"[0-9a-f]{64}")
SAFE_ABS = re.compile(r"/[A-Za-z0-9._/@+-]+")
MODULE_PHASES = {
    "v3_authority",
    "canary",
    "production",
    "reducer",
    "replay",
    "combined",
    "release",
    "terminal",
}
MODULE_INIT_CANDIDATES = (
    "/etc/profile.d/modules.sh",
    "/etc/profile.d/lmod.sh",
    "/etc/profile.d/z00_lmod.sh",
    "/usr/share/lmod/lmod/init/bash",
)
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
SAFE_GPU_ENV = {
    "CUDA_VISIBLE_DEVICES",
    "ROCR_VISIBLE_DEVICES",
    "GPU_DEVICE_ORDINAL",
}


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


def strict_manifest(root: Path, anchor: str, file_mode: int = 0o600) -> dict[str, str]:
    req(HEX.fullmatch(anchor) is not None, "H12 anchor shape")
    root = trusted_abs(root)
    req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode) == 0o700, "package root mode")
    manifest = root / H12_MAN
    req(manifest.is_file() and not manifest.is_symlink() and sha(manifest) == anchor, "H12 manifest pin")
    raw = manifest.read_bytes()
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
    req(actual == set(rows) | {H12_MAN}, "closed H12 package inventory")
    for name, digest in rows.items():
        req(sha(root / name) == digest, f"package member drift {name}")
    req(sha(root / H11_MAN) == H11_SHA, "H11 parent drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h10_payload.sha256") == H10_SHA, "H10 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h9_payload.sha256") == H9_SHA, "H9 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h8_payload.sha256") == H8_SHA, "H8 ancestor drift")
    req(sha(root / "notes/isambard_ai_v4_r2_h7_payload.sha256") == H7_SHA, "H7 ancestor drift")
    return rows


def captured_member(root: Path, name: str, rows: dict[str, str]) -> bytes:
    req(name in rows, "member outside H12 manifest")
    path = root / safe_rel(name)
    before = path.lstat()
    raw = path.read_bytes()
    after = path.lstat()
    req(
        stat.S_ISREG(before.st_mode)
        and not path.is_symlink()
        and before.st_nlink == 1
        and before.st_ino == after.st_ino
        and before.st_mtime_ns == after.st_mtime_ns
        and before.st_size == after.st_size
        and sha_bytes(raw) == rows[name],
        "captured member TOCTOU",
    )
    return raw


def load_h11_base(package: Path, rows: dict[str, str]):
    raw = captured_member(package, H11_RUNTIME, rows)
    module = types.ModuleType("h12_pinned_h11_runtime_base")
    module.__file__ = str(package / H11_RUNTIME)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    module.MAN = H12_MAN
    module.H10_MAN = H11_MAN
    module.H10_SHA = H11_SHA
    return module


def secure_system_file(path: Path | str) -> dict:
    original = Path(path)
    req(original.is_absolute() and original.exists(), "system file missing")
    resolved = original.resolve(strict=True)
    info = resolved.stat()
    req(
        stat.S_ISREG(info.st_mode)
        and info.st_uid == 0
        and not (stat.S_IMODE(info.st_mode) & 0o022),
        "system file is not immutable root authority",
    )
    probe = resolved.parent
    while True:
        item = probe.stat()
        req(
            stat.S_ISDIR(item.st_mode)
            and item.st_uid == 0
            and not (stat.S_IMODE(item.st_mode) & 0o022),
            "system file ancestor authority",
        )
        if probe == probe.parent:
            break
        probe = probe.parent
    return {
        "path": str(resolved),
        "sha256": sha(resolved),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
    }


def module_init(phase: str) -> dict | None:
    if phase not in MODULE_PHASES:
        return None
    for candidate in MODULE_INIT_CANDIDATES:
        if Path(candidate).exists():
            return secure_system_file(candidate)
    raise ValueError("root-owned module initialization not found")


def validate_entry_environment(config: dict) -> dict:
    keys = set(os.environ)
    req(not (keys & DENIED_ENV), "denied inherited environment variable")
    req(not any(key.startswith("BASH_FUNC_") for key in keys), "exported shell function")
    req(os.environ.get("PATH") == "/usr/bin:/bin", "wrapper PATH policy")
    req(os.environ.get("LC_ALL") == "C" and os.environ.get("LANG") == "C", "wrapper locale policy")
    interpreter = config["python_interpreter"]
    running = Path(sys.executable).resolve()
    allowed_uids = (
        {0, os.getuid()}
        if config["phase"] in ("selftest_upstream", "selftest_downstream")
        else {0}
    )
    req(
        str(running) == interpreter["path"]
        and sha(running) == interpreter["sha256"]
        and running.stat().st_uid in allowed_uids
        and not (stat.S_IMODE(running.stat().st_mode) & 0o022),
        "runtime interpreter anchor",
    )
    return {
        "entry_environment_keys": sorted(keys),
        "entry_environment_keys_sha256": sha_bytes(
            json.dumps(sorted(keys), separators=(",", ":")).encode()
        ),
        "path": os.environ["PATH"],
        "locale": "C",
        "submission_export": "NIL",
        "python_interpreter": interpreter,
    }


def science_environment(config: dict, package: Path, run: Path, snapshot: Path) -> dict[str, str]:
    account = pwd.getpwuid(os.getuid())
    result = {
        "HOME": account.pw_dir,
        "USER": account.pw_name,
        "LOGNAME": account.pw_name,
        "SHELL": "/bin/bash",
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "H11_PACKAGE_ROOT": str(package),
        "H11_RUN_ROOT": str(run),
        "H11_SNAPSHOT_ROOT": str(snapshot),
        "H12_PACKAGE_ROOT": str(package),
        "H12_RUN_ROOT": str(run),
        "H12_SNAPSHOT_ROOT": str(snapshot),
    }
    for key, value in os.environ.items():
        if key.startswith("SLURM_") or key.startswith("SPANK_") or key in SAFE_GPU_ENV:
            result[key] = value
    test_name = config.get("selftest_output_name")
    if test_name is not None:
        req(
            config["phase"] in ("selftest_upstream", "selftest_downstream")
            and re.fullmatch(r"[A-Za-z0-9._-]+", test_name) is not None,
            "selftest environment value",
        )
        result["H9_TEST_OUTPUT_NAME"] = test_name
    req(not (set(result) & DENIED_ENV), "science environment denylist")
    req(not any(key.startswith("BASH_FUNC_") for key in result), "science exported shell function")
    return result


def execute(config: dict) -> dict:
    keys = {
        "schema",
        "phase",
        "package_root",
        "run_root",
        "h12",
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
        "python_interpreter",
        "environment_policy_sha256",
        "selftest_output_name",
    }
    req(set(config) == keys and config["schema"] == "h12-runtime-config-v1", "runtime config schema")
    req(
        (config["h11"], config["h10"], config["h9"], config["h8"], config["h7"])
        == (H11_SHA, H10_SHA, H9_SHA, H8_SHA, H7_SHA),
        "runtime lineage anchors",
    )
    req(HEX.fullmatch(config["h12"]) is not None, "runtime H12 anchor")
    policy = {
        "submission_export": "NIL",
        "wrapper_path": "/usr/bin:/bin",
        "denied_environment": sorted(DENIED_ENV),
        "deny_exported_shell_functions": True,
        "science_environment": "explicit-slurm-gpu-identity-allowlist",
        "science_shell": "/bin/bash --noprofile --norc",
    }
    req(
        sha_bytes(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode())
        == config["environment_policy_sha256"],
        "environment policy anchor",
    )
    entry_policy = validate_entry_environment(config)
    package = trusted_abs(config["package_root"])
    run = trusted_abs(config["run_root"])
    rows = strict_manifest(package, config["h12"])
    base = load_h11_base(package, rows)
    raw_tmp = os.environ.get("SLURM_TMPDIR", "")
    req(raw_tmp.startswith("/"), "SLURM_TMPDIR")
    temporary = trusted_abs(raw_tmp)
    job = os.environ.get("SLURM_JOB_ID", "")
    array = os.environ.get("SLURM_ARRAY_JOB_ID")
    task_raw = os.environ.get("SLURM_ARRAY_TASK_ID")
    req(job.isdecimal(), "JobIDRaw runtime identity")
    task = int(task_raw) if task_raw is not None else None
    if config["phase"] == "production":
        req(
            array is not None and array.isdecimal() and task is not None and 0 <= task < 480,
            "array runtime identity",
        )
    else:
        req(array is None and task is None, "nonarray runtime identity")
    submitted_script = trusted_abs(os.environ.get("H11_SUBMITTED_SCRIPT_PATH", ""))
    expected_binding = os.environ.get("H11_EXPECTED_BINDING_SHA256", "")
    req(HEX.fullmatch(expected_binding) is not None, "submitted script binding missing")
    actual_script_sha = base.script_binding(submitted_script, expected_binding)
    suffix = f"{array}_{task}" if task is not None else job
    snapshot = temporary / f"h12-{config['phase']}-{suffix}"
    baseline = base.copy_snapshot(package, snapshot, config["h12"])
    imported = base.copy_inputs(run, snapshot, config["phase_inputs"], baseline)
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
    effective_args = base.mapped_args(
        config["phase_args"], run, package, snapshot, imported
    )
    initialization = module_init(config["phase"])
    shell_code = (
        'init="$1"; shift; source "$init"; source /dev/stdin'
        if initialization is not None
        else "source /dev/stdin"
    )
    shell_argv = ["/bin/bash", "--noprofile", "--norc", "-c", shell_code, "h12-science"]
    if initialization is not None:
        shell_argv.append(initialization["path"])
    shell_argv.extend(effective_args)
    clean_environment = science_environment(config, package, run, snapshot)
    completed = subprocess.run(
        shell_argv,
        input=body,
        cwd=snapshot,
        env=clean_environment,
        check=False,
    )
    req(completed.returncode == 0, "science body failed")
    after = base.inventory(snapshot)
    for name, digest in before.items():
        req(
            name in after
            and after[name]["sha256"] == digest
            and after[name]["mode"] == 0o400,
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
        "h12": config["h12"],
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "h12_status": "PASS_H12_ENVIRONMENT_ISOLATED_EXECUTION",
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
        "phase_args_sha256": sha_bytes(
            json.dumps(config["phase_args"], separators=(",", ":")).encode()
        ),
        "effective_phase_args_sha256": sha_bytes(
            json.dumps(effective_args, separators=(",", ":")).encode()
        ),
        "phase_inputs": config["phase_inputs"],
        "outputs": outputs,
        "environment_policy": entry_policy,
        "science_environment_keys": sorted(clean_environment),
        "science_environment_keys_sha256": sha_bytes(
            json.dumps(sorted(clean_environment), separators=(",", ":")).encode()
        ),
        "module_initialization": initialization,
        "terminal_accounting_claimed_at_runtime": False,
        "authorizes_scientific_release": False,
    }
    key = base.receipt_key(config["phase"], array, task, job)
    tx = base.prepare_transaction(run, key, outputs, snapshot, receipt)
    return base.recover_transaction(tx)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    result = execute(json.loads(args.config.read_text()))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError, RuntimeError) as error:
        print(f"FAIL-CLOSED: {error}", file=sys.stderr)
        raise SystemExit(2)
