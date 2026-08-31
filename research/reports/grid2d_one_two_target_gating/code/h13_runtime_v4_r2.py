#!/usr/bin/env python3
"""H13 environment-isolated runtime over the immutable H11 transaction layer."""
from __future__ import annotations

import argparse
import base64
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

H12_SHA = "bcc487d9910dd6cb5732f26ca18caecd20b7a24844083fd61b89c361fdae0e0a"
H11_SHA = "dec7cf087c9cb5ab86cc84afbd6b9da59774c76a5bdc030b09155e0745e356ca"
H10_SHA = "d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf"
H9_SHA = "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA = "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
H13_MAN = "notes/isambard_ai_v4_r2_h13_payload.sha256"
H12_MAN = "notes/isambard_ai_v4_r2_h12_payload.sha256"
H11_RUNTIME = "code/h11_runtime_v4_r2.py"
OLD_ROOT = "/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"
HEX = re.compile(r"[0-9a-f]{64}")
SAFE_ABS = re.compile(r"/[A-Za-z0-9._/@+-]+")
# H13's three allowed phases use absolute host executables and a pinned
# container.  They intentionally do not require a login-shell module function.
MODULE_PHASES: frozenset[str] = frozenset()
MODULE_INIT_AUTHORITIES = {
    "/opt/cray/pe/lmod/8.7.55/init/bash":
        "74affab7cadc42647a5b1a01219d23ce289d9debd74cd9fc5694d99c722e4dc2",
}
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

PINNED_PYTHON_LAUNCHER = r'''from __future__ import annotations
import hashlib
import importlib.abc
import importlib.util
import os
import re
import stat
import sys
from pathlib import Path

HEX = re.compile(r"[0-9a-f]{64}")
MODULE = re.compile(r"code/([A-Za-z_][A-Za-z0-9_]*)[.]py")
MANIFEST = "notes/isambard_ai_v4_r2_h13_payload.sha256"
DIR_FLAGS = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW


def req(value, message):
    if not value:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(name):
    req(isinstance(name, str) and name not in ("", "."), "unsafe bound source")
    req("\x00" not in name and "\n" not in name and "\r" not in name, "bound source control byte")
    path = Path(name)
    req(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name, "unsafe bound source")
    return path


def main():
    req(
        sys.flags.isolated
        and sys.flags.ignore_environment
        and sys.flags.no_user_site
        and sys.flags.dont_write_bytecode
        and getattr(sys.flags, "safe_path", sys.flags.isolated),
        "pinned launcher requires -I -B -E -s",
    )
    req(len(sys.argv) >= 3 and HEX.fullmatch(sys.argv[1]) is not None, "pinned launcher arguments")
    anchor, entry, user_args = sys.argv[1], sys.argv[2], sys.argv[3:]
    root_fd = os.open(".", DIR_FLAGS)
    try:
        root_info = os.fstat(root_fd)
        req(
            stat.S_ISDIR(root_info.st_mode)
            and stat.S_IMODE(root_info.st_mode) == 0o700,
            "pinned launcher root",
        )
        root_path = (
            Path(f"/proc/self/fd/{root_fd}")
            if Path("/proc/self/fd").exists()
            else Path.cwd()
        )

        def read_once(name, expected):
            relative = safe(name)
            directory_fd = os.dup(root_fd)
            try:
                for part in relative.parts[:-1]:
                    child_fd = os.open(part, DIR_FLAGS, dir_fd=directory_fd)
                    os.close(directory_fd)
                    directory_fd = child_fd
                descriptor = os.open(
                    relative.parts[-1],
                    os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=directory_fd,
                )
                try:
                    before = os.fstat(descriptor)
                    req(
                        stat.S_ISREG(before.st_mode)
                        and before.st_nlink == 1
                        and stat.S_IMODE(before.st_mode) == 0o400,
                        f"unsafe bound source {name}",
                    )
                    chunks = []
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
                        f"bound source changed {name}",
                    )
                    raw = b"".join(chunks)
                    req(
                        len(raw) == before.st_size and digest(raw) == expected,
                        f"bound source hash drift {name}",
                    )
                    return raw
                finally:
                    os.close(descriptor)
            finally:
                os.close(directory_fd)

        manifest = read_once(MANIFEST, anchor)
        req(manifest.endswith(b"\n") and b"\r" not in manifest, "bound manifest bytes")
        rows = {}
        for line in manifest.decode().splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)", line)
            req(match is not None, "bound manifest syntax")
            expected, name = match.groups()
            safe(name)
            req(name not in rows, "duplicate bound manifest member")
            rows[name] = expected
        safe(entry)
        req(entry in rows and MODULE.fullmatch(entry) is not None, "entry outside bound Python members")
        module_rows = {}
        for name, expected in rows.items():
            match = MODULE.fullmatch(name)
            if match is not None:
                req(match.group(1) not in module_rows, "duplicate bound Python module")
                module_rows[match.group(1)] = (name, expected)

        class BoundLoader(importlib.abc.Loader):
            def __init__(self, fullname, name, expected):
                self.fullname = fullname
                self.name = name
                self.expected = expected

            def create_module(self, spec):
                return None

            def exec_module(self, module):
                raw = read_once(self.name, self.expected)
                filename = str(root_path / self.name)
                module.__file__ = filename
                module.__cached__ = None
                module.__package__ = ""
                exec(compile(raw, filename, "exec"), module.__dict__)

        class BoundFinder(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                del target
                if path is not None or "." in fullname or fullname not in module_rows:
                    return None
                name, expected = module_rows[fullname]
                return importlib.util.spec_from_loader(
                    fullname,
                    BoundLoader(fullname, name, expected),
                    origin=str(root_path / name),
                )

        sys.meta_path.insert(0, BoundFinder())
        raw = read_once(entry, rows[entry])
        filename = str(root_path / entry)
        namespace = {
            "__name__": "__main__",
            "__file__": filename,
            "__package__": None,
            "__cached__": None,
            "__builtins__": __builtins__,
        }
        sys.argv = [filename, *user_args]
        exec(compile(raw, filename, "exec"), namespace)
        return 0
    finally:
        os.close(root_fd)


raise SystemExit(main())
'''


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


def read_beneath_once(
    root: Path,
    name: str,
    *,
    expected_sha256: str | None = None,
    mode: int = 0o600,
) -> bytes:
    relative = safe_rel(name)
    directory_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(root, directory_flags)
    try:
        for part in relative.parts[:-1]:
            child_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        descriptor = os.open(
            relative.parts[-1],
            os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=directory_fd,
        )
        try:
            before = os.fstat(descriptor)
            req(
                stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == mode,
                f"unsafe package member {name}",
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
                f"package member changed during single-FD read {name}",
            )
            raw = b"".join(chunks)
            req(len(raw) == before.st_size, f"package member short read {name}")
            if expected_sha256 is not None:
                req(sha_bytes(raw) == expected_sha256, f"package member drift {name}")
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory_fd)


def strict_manifest(root: Path, anchor: str, file_mode: int = 0o600) -> dict[str, str]:
    req(HEX.fullmatch(anchor) is not None, "H13 anchor shape")
    root = trusted_abs(root)
    req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode) == 0o700, "package root mode")
    raw = read_beneath_once(
        root, H13_MAN, expected_sha256=anchor, mode=file_mode
    )
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
    req(actual == set(rows) | {H13_MAN}, "closed H13 package inventory")
    for name, digest in rows.items():
        read_beneath_once(root, name, expected_sha256=digest, mode=file_mode)
    read_beneath_once(root, H12_MAN, expected_sha256=H12_SHA, mode=file_mode)
    read_beneath_once(
        root,
        "notes/isambard_ai_v4_r2_h11_payload.sha256",
        expected_sha256=H11_SHA,
        mode=file_mode,
    )
    read_beneath_once(
        root,
        "notes/isambard_ai_v4_r2_h10_payload.sha256",
        expected_sha256=H10_SHA,
        mode=file_mode,
    )
    read_beneath_once(
        root,
        "notes/isambard_ai_v4_r2_h9_payload.sha256",
        expected_sha256=H9_SHA,
        mode=file_mode,
    )
    read_beneath_once(
        root,
        "notes/isambard_ai_v4_r2_h8_payload.sha256",
        expected_sha256=H8_SHA,
        mode=file_mode,
    )
    read_beneath_once(
        root,
        "notes/isambard_ai_v4_r2_h7_payload.sha256",
        expected_sha256=H7_SHA,
        mode=file_mode,
    )
    return rows


def captured_member(root: Path, name: str, rows: dict[str, str]) -> bytes:
    req(name in rows, "member outside H13 manifest")
    return read_beneath_once(root, name, expected_sha256=rows[name])


def write_new_beneath(root: Path, name: str, raw: bytes, mode: int) -> None:
    relative = safe_rel(name)
    directory_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(root, directory_flags)
    try:
        root_info = os.fstat(directory_fd)
        req(
            stat.S_ISDIR(root_info.st_mode)
            and stat.S_IMODE(root_info.st_mode) == 0o700,
            "unsafe snapshot root",
        )
        for part in relative.parts[:-1]:
            try:
                child_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            except FileNotFoundError:
                os.mkdir(part, 0o700, dir_fd=directory_fd)
                os.fsync(directory_fd)
                child_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            child_info = os.fstat(child_fd)
            req(
                stat.S_ISDIR(child_info.st_mode)
                and stat.S_IMODE(child_info.st_mode) == 0o700,
                "unsafe snapshot directory",
            )
            os.close(directory_fd)
            directory_fd = child_fd
        descriptor = os.open(
            relative.parts[-1],
            os.O_RDWR
            | os.O_CREAT
            | os.O_EXCL
            | os.O_CLOEXEC
            | os.O_NOFOLLOW,
            mode,
            dir_fd=directory_fd,
        )
        try:
            view = memoryview(raw)
            offset = 0
            while offset < len(view):
                written = os.write(descriptor, view[offset:])
                req(written > 0, "snapshot write stalled")
                offset += written
            os.fchmod(descriptor, mode)
            os.fsync(descriptor)
            info = os.fstat(descriptor)
            req(
                stat.S_ISREG(info.st_mode)
                and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == mode
                and info.st_size == len(raw),
                "unsafe snapshot member",
            )
            os.lseek(descriptor, 0, os.SEEK_SET)
            chunks: list[bytes] = []
            while True:
                block = os.read(descriptor, 1 << 20)
                if not block:
                    break
                chunks.append(block)
            after = os.fstat(descriptor)
            req(
                b"".join(chunks) == raw
                and (
                    info.st_dev,
                    info.st_ino,
                    info.st_mode,
                    info.st_nlink,
                    info.st_size,
                    info.st_mtime_ns,
                    info.st_ctime_ns,
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
                "snapshot single-FD readback drift",
            )
        finally:
            os.close(descriptor)
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def copy_snapshot_hardened(
    package: Path,
    snapshot: Path,
    h13: str,
) -> dict[str, str]:
    rows = strict_manifest(package, h13)
    req(not snapshot.exists() and not snapshot.is_symlink(), "snapshot collision")
    snapshot.mkdir(mode=0o700)
    os.chmod(snapshot, 0o700)
    baseline = {**rows, H13_MAN: h13}
    for name, digest in baseline.items():
        raw = read_beneath_once(
            package,
            name,
            expected_sha256=digest,
            mode=0o600,
        )
        write_new_beneath(snapshot, name, raw, 0o400)
    strict_manifest(snapshot, h13, 0o400)
    strict_manifest(package, h13)
    return baseline


def copy_inputs_hardened(
    run: Path,
    snapshot: Path,
    records: list[dict],
    baseline: dict[str, str],
) -> dict[str, str]:
    imported: dict[str, str] = {}
    for item in records:
        req(
            set(item) == {"path", "sha256"}
            and HEX.fullmatch(item["sha256"]) is not None,
            "input schema",
        )
        name = item["path"]
        safe_rel(name)
        req(
            name.startswith("artifacts/")
            and name not in baseline
            and name not in imported,
            "input collision",
        )
        raw = read_beneath_once(
            run,
            name,
            expected_sha256=item["sha256"],
            mode=0o600,
        )
        write_new_beneath(snapshot, name, raw, 0o400)
        imported[name] = item["sha256"]
    return imported


def load_h11_base(package: Path, rows: dict[str, str]):
    raw = captured_member(package, H11_RUNTIME, rows)
    module = types.ModuleType("h13_pinned_h11_runtime_base")
    module.__file__ = str(package / H11_RUNTIME)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    module.MAN = H13_MAN
    module.H10_MAN = H12_MAN
    module.H10_SHA = H12_SHA
    module.copy_snapshot = copy_snapshot_hardened
    module.copy_inputs = copy_inputs_hardened
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
    for candidate, expected_sha256 in MODULE_INIT_AUTHORITIES.items():
        if Path(candidate).exists():
            authority = secure_system_file(candidate)
            req(
                authority["sha256"] == expected_sha256,
                "root-owned module initialization hash drift",
            )
            return authority
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
        "H13_PACKAGE_ROOT": str(package),
        "H13_RUN_ROOT": str(run),
        "H13_SNAPSHOT_ROOT": str(snapshot),
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
        "h13",
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
    req(set(config) == keys and config["schema"] == "h13-runtime-config-v1", "runtime config schema")
    req(
        (config["h12"], config["h11"], config["h10"], config["h9"], config["h8"], config["h7"])
        == (H12_SHA, H11_SHA, H10_SHA, H9_SHA, H8_SHA, H7_SHA),
        "runtime lineage anchors",
    )
    req(HEX.fullmatch(config["h13"]) is not None, "runtime H13 anchor")
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
    rows = strict_manifest(package, config["h13"])
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
    snapshot = temporary / f"h13-{config['phase']}-{suffix}"
    baseline = base.copy_snapshot(package, snapshot, config["h13"])
    imported = base.copy_inputs(run, snapshot, config["phase_inputs"], baseline)
    before = {**baseline, **imported}
    science = bytes.fromhex(config["science_bytes_hex"])
    req(
        sha_bytes(science) == config["science_sha256"] == baseline.get(config["science_path"]),
        "captured science binding",
    )
    launcher_b64 = base64.b64encode(PINNED_PYTHON_LAUNCHER.encode()).decode()
    launcher_shell = (
        "h13_pinned_source() {\n"
        f"  /usr/bin/printf '%s' '{launcher_b64}' | /usr/bin/base64 -d\n"
        "}\n"
        "readonly -f h13_pinned_source\n"
    )
    body = (
        launcher_shell
        + "\n".join(
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
    shell_argv = ["/bin/bash", "--noprofile", "--norc", "-c", shell_code, "h13-science"]
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
    if initialization is not None:
        req(
            secure_system_file(initialization["path"]) == initialization,
            "module initialization changed during science execution",
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
        "h13": config["h13"],
        "h12": H12_SHA,
        "h11": H11_SHA,
        "h10": H10_SHA,
        "h9": H9_SHA,
        "h8": H8_SHA,
        "h7": H7_SHA,
        "h13_status": "PASS_H13_ENVIRONMENT_ISOLATED_EXECUTION",
        "h12_status": "PASS_H12_POLICY_INHERITED_BY_H13",
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
