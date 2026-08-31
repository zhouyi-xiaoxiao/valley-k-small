#!/usr/bin/env python3
"""Independent post-result auditor for the allocation-cusp v6 freeze.

This module deliberately does not import the producer.  It validates the
frozen provenance/result/evidence contracts and algebraically reconstructs the
reported score, physical-law, branch-orientation, and PASS implications.  It
does not recompute matrix exponentials or independently solve a cusp.
"""

from __future__ import annotations

import csv
import ctypes
import functools
import hashlib
import importlib.metadata
import io
import json
import math
import os
import platform
import re
import stat
import subprocess
import sys
import sysconfig
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "positive_b_allocation_cusp_discovery_manifest.json"
DISCOVERY_RUNNER = HERE.with_name("positive_b_allocation_cusp_discovery.py")
RESULT = DATA / "positive_b_allocation_cusp_discovery_result.json"
EVIDENCE = DATA / "positive_b_allocation_cusp_discovery_reproducibility.json"
OUTPUT = DATA / "positive_b_allocation_cusp_discovery_independent_audit.json"
EXPECTED_FIVE_PATH_ABSENCE = [
    "artifacts/data/positive_b_allocation_cusp_discovery_result.json",
    "artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json",
    "artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json",
    "artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json",
    "artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json",
]
EXPECTED_PROMOTION_STAGING_ABSENCE = [
    "artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging",
    "artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging",
]

EXPECTED_MANIFEST_SHA256 = "2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948"
SCHEMA_VERSION = 6
STAGE = "result_blind_fixed_B_allocation_cusp_two_mesh_discovery_v6"
PASS_STATUS = "PASS_DISCOVERY_LOW_MESH_ONLY"
HOLD_STATUS = "HOLD_DISCOVERY"
DISCOVERY_MESHES = (65, 97)
SYSTEM_NATIVE_PREFIXES = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)
NATIVE_IMAGE_PHASES = (
    "bootstrap_pre_third_party",
    "runner_post_import",
    "post_manifest_validation",
    "full_stack_post_import",
)
NATIVE_IMAGE_PROBE = r"""\
import csv
import ctypes
import hashlib
import importlib
import io
import json
import os
import runpy
import stat
import subprocess
import sys

runner, site_packages = sys.argv[1:]
code_directory = os.path.dirname(runner)
system_prefixes = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)

def loaded_non_system_images():
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows = {}
    count = int(dyld._dyld_image_count())
    for index in range(count):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise SystemExit("dyld returned a non-absolute image path")
        resolved = os.path.realpath(lexical)
        if lexical.startswith(system_prefixes) or resolved.startswith(system_prefixes):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise SystemExit("dyld returned multiple lexical names for one loaded image")
    return [rows[key] for key in sorted(rows)]

def main_executable_image():
    dyld = ctypes.CDLL(None)
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    encoded = dyld._dyld_get_image_name(0)
    if not encoded:
        raise SystemExit("dyld did not expose the main executable image")
    lexical = os.fsdecode(encoded)
    return {"lexical_path": lexical, "resolved_path": os.path.realpath(lexical)}

bootstrap = loaded_non_system_images()
sys.path.append(site_packages)
import argparse
import functools
import math
import platform
import re
import sysconfig
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import LinearOperator, expm_multiply
runner_import = loaded_non_system_images()
platform.mac_ver()
post_manifest_validation = loaded_non_system_images()
sys.path.insert(0, code_directory)
for local_name in (
    "continuum_g1_smoke",
    "continuum_observable_four_patch",
    "continuum_weak_budget_design",
    "continuum_broad_patch_b0_bridge",
):
    importlib.import_module(local_name)
full_stack = loaded_non_system_images()
print(
    json.dumps(
        {
            "main_executable_image": main_executable_image(),
            "phase_images": {
                "bootstrap_pre_third_party": bootstrap,
                "runner_post_import": runner_import,
                "post_manifest_validation": post_manifest_validation,
                "full_stack_post_import": full_stack,
            },
        },
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
)
"""
EXPECTED_EVIDENCE_TIMING = "FROZEN_BEFORE_ANY_ALLOCATION_CUSP_MESH_65_OR_97_RUN"
EXPECTED_LIMITATIONS = [
    "meshes 65 and 97 are two same-family discovery meshes; mesh 97 is not held out",
    "same finite-volume solver family and one fixed box",
    "no held-out parity, box, continuum, or independent-solver evidence",
    "retained-window modes are not a global exact-count theorem",
    "PASS_DISCOVERY_LOW_MESH_ONLY is not a manuscript confirmation or publication pass",
]
CONTROL_GATE_NAMES = {
    "alternating_topology",
    "endpoint_signs",
    "peak_ratio",
    "valley_ratio",
    "curvature",
    "root_residual",
    "event_masses",
    "positive_density_and_survival",
    "survival_monotone",
    "sampled_state_nonnegative",
    "sampled_survival_monotone",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "event_partition_closure",
    "final_state_nonnegative",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
}
SCAN_PHYSICAL_GATE_NAMES = {
    "positive_density_and_survival",
    "state_nonnegative",
    "sampled_survival_monotone",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
    "all_bracketed_roots_physical",
}
BRANCH_GATE_NAMES = {
    "minimum_nodes",
    "required_reach",
    "comparison_nodes_present",
    "comparison_nodes_distinct",
    "comparison_nodes_on_signed_side",
    "comparison_offset_mismatch",
    "fold_residuals",
    "third_derivative",
    "fold_rank",
    "physical_law",
    "comparison_scan_physical_law",
    "remote_pair_retained",
    "stable_remote_pair_identity",
    "remote_pair_lineage",
}
RESULT_KEYS = {
    "schema_version",
    "stage",
    "status",
    "evidence_timing",
    "claim_scope",
    "manifest_sha256",
    "small_explicit_csr_preflight",
    "discovery_mesh_rows",
    "bounded_phase_discovery",
    "all_discovery_gates_passed",
    "required_claim_flags",
    "forbidden_claims",
    "pin_snapshots",
    "lexical_pin_snapshots",
    "pinned_file_hashes",
    "software",
    "limitations",
}
MESH_ROW_KEYS = {
    "mesh",
    "status",
    "reason",
    "model_diagnostics",
    "homotopy",
    "cusp",
    "cusp_diagnostics",
    "stationary_scan",
    "remote_pair",
    "branches",
    "all_mesh_discovery_gates_passed",
}


def sha256(path: Path) -> str:
    return sha256_bytes(stable_regular_file_bytes(Path(path))[0])


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require_finite_json(value: Any, location: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"nonfinite number at {location}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            require_finite_json(item, f"{location}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError(f"non-string key at {location}")
            require_finite_json(item, f"{location}.{key}")
        return
    raise TypeError(f"unsupported JSON type at {location}: {type(value).__name__}")


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    require_finite_json(payload)
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def lexical_path_exists(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return False
    return True


def stable_regular_file_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    lexical = Path(path)
    before = os.lstat(lexical)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise RuntimeError(f"audit input is not a lexical regular file: {lexical}")
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise RuntimeError("O_NOFOLLOW is unavailable")
    descriptor = os.open(lexical, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0))
    try:
        opened = os.fstat(descriptor)
        identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
        )
        if (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_size,
            opened.st_mtime_ns,
        ) != identity:
            raise RuntimeError(f"audit lexical/open identity mismatch: {lexical}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = os.lstat(lexical)
    if (
        after_fd.st_dev,
        after_fd.st_ino,
        after_fd.st_mode,
        after_fd.st_size,
        after_fd.st_mtime_ns,
    ) != identity or (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_size,
        after.st_mtime_ns,
    ) != identity:
        raise RuntimeError(f"audit input changed during capture: {lexical}")
    payload = b"".join(chunks)
    if len(payload) != before.st_size:
        raise RuntimeError(f"audit input short read: {lexical}")
    return payload, {
        "path": str(lexical),
        "st_dev": int(after.st_dev),
        "st_ino": int(after.st_ino),
        "st_mode": int(after.st_mode),
        "st_nlink": int(after.st_nlink),
        "st_uid": int(after.st_uid),
        "st_gid": int(after.st_gid),
        "st_size": int(after.st_size),
        "st_mtime_ns": int(after.st_mtime_ns),
        "sha256": sha256_bytes(payload),
    }


def _closure_sha256(rows: Sequence[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for name, file_hash in sorted(rows):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def exact_import_tree_closure(
    root: Path, file_hash_cache: dict[str, str] | None = None
) -> dict[str, Any]:
    base = Path(os.path.abspath(root))
    try:
        base_metadata = os.lstat(base)
    except FileNotFoundError:
        return {
            "present": False,
            "entry_count": 0,
            "regular_file_count": 0,
            "pyc_file_count": 0,
            "symlink_count": 0,
            "closure_sha256": _closure_sha256([]),
        }
    if stat.S_ISLNK(base_metadata.st_mode) or not stat.S_ISDIR(base_metadata.st_mode):
        raise RuntimeError("audit import-tree root is not a lexical directory")
    cache = file_hash_cache if file_hash_cache is not None else {}
    rows: list[tuple[str, str]] = []
    regular_count = 0
    pyc_count = 0
    symlink_count = 0
    for directory, directory_names, file_names in os.walk(base, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            path = directory_path / name
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = path.relative_to(base).as_posix()
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                raise RuntimeError("audit import tree contains a non-directory")
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = directory_path / name
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = path.relative_to(base).as_posix()
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise RuntimeError("audit import tree contains a special file")
            cache_key = str(path)
            file_hash = cache.get(cache_key)
            if file_hash is None:
                payload, _snapshot = stable_regular_file_bytes(path)
                file_hash = sha256_bytes(payload)
                cache[cache_key] = file_hash
            rows.append(
                (
                    path.relative_to(base).as_posix(),
                    f"F:{metadata.st_mode}:{metadata.st_size}:{file_hash}",
                )
            )
            regular_count += 1
            pyc_count += int(name.endswith(".pyc"))
    return {
        "present": True,
        "entry_count": len(rows),
        "regular_file_count": regular_count,
        "pyc_file_count": pyc_count,
        "symlink_count": symlink_count,
        "closure_sha256": _closure_sha256(rows),
    }


def stdlib_tree_closure(root: Path) -> dict[str, Any]:
    closure = exact_import_tree_closure(Path(os.path.realpath(root)))
    if closure["present"] is not True:
        raise RuntimeError("audit Python stdlib root is missing")
    return closure


def _lexical_regular_under(root: Path, path: Path) -> tuple[bytes, dict[str, Any]]:
    base = Path(os.path.abspath(root))
    target = Path(os.path.abspath(os.path.normpath(path)))
    if target == base or not target.is_relative_to(base):
        raise RuntimeError("audit runtime package path escapes the frozen venv")
    current = base
    parts = target.relative_to(base).parts
    for index, part in enumerate(parts):
        current /= part
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError("audit runtime package path contains a symlink")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise RuntimeError("audit runtime package path has the wrong file type")
    return stable_regular_file_bytes(target)


def distribution_record_closure(
    venv_root: Path,
    site_packages: Path,
    record_path: Path,
    file_hash_cache: dict[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(os.path.abspath(venv_root))
    site = Path(os.path.abspath(site_packages))
    record = Path(os.path.abspath(record_path))
    record_bytes, _metadata = _lexical_regular_under(root, record)
    try:
        records = list(csv.reader(io.StringIO(record_bytes.decode("utf-8"), newline="")))
    except (UnicodeDecodeError, csv.Error) as error:
        raise RuntimeError("audit distribution RECORD is malformed") from error
    rows: list[tuple[str, str]] = []
    native_rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    cache = file_hash_cache if file_hash_cache is not None else {}
    for row in records:
        if len(row) != 3 or not row[0]:
            raise RuntimeError("audit distribution RECORD row is malformed")
        path = Path(os.path.abspath(os.path.normpath(site / row[0])))
        if not path.is_relative_to(root):
            raise RuntimeError("audit distribution RECORD path escapes the frozen venv")
        relative = path.relative_to(root).as_posix()
        if relative in seen:
            raise RuntimeError("audit distribution RECORD has a duplicate path")
        seen.add(relative)
        file_hash = cache.get(str(path))
        if file_hash is None:
            payload, _snapshot = _lexical_regular_under(root, path)
            file_hash = sha256_bytes(payload)
            cache[str(path)] = file_hash
        rows.append((relative, file_hash))
        if relative.endswith((".so", ".dylib", ".pyd", ".dll")):
            native_rows.append((relative, file_hash))
    return {
        "record_file_count": len(rows),
        "record_sha256": sha256_bytes(record_bytes),
        "record_closure_sha256": _closure_sha256(rows),
        "native_extension_count": len(native_rows),
        "native_extension_closure_sha256": _closure_sha256(native_rows),
    }


def _is_system_native_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in SYSTEM_NATIVE_PREFIXES)


def repository_site_packages() -> Path:
    return (
        (REPOSITORY / ".venv").resolve()
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    ).resolve()


def loaded_non_system_native_images() -> list[dict[str, str]]:
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows: dict[str, dict[str, str]] = {}
    for index in range(int(dyld._dyld_image_count())):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise RuntimeError("audit dyld returned a non-absolute image path")
        resolved = os.path.realpath(lexical)
        if _is_system_native_path(lexical) or _is_system_native_path(resolved):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise RuntimeError("audit dyld returned multiple lexical names for one loaded image")
    return [rows[key] for key in sorted(rows)]


def isolated_native_image_probe() -> dict[str, Any]:
    site_packages = repository_site_packages()
    environment = {
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    completed = subprocess.run(
        [
            os.path.abspath(sys.executable),
            "-I",
            "-S",
            "-B",
            "-c",
            NATIVE_IMAGE_PROBE,
            str(DISCOVERY_RUNNER),
            str(site_packages),
        ],
        cwd=REPOSITORY,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"audit isolated native-image probe failed: {completed.stderr.strip()}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("audit isolated native-image probe returned malformed JSON") from error
    if type(value) is not dict or set(value) != {"main_executable_image", "phase_images"}:
        raise RuntimeError("audit isolated native-image probe schema changed")
    main = value["main_executable_image"]
    phases = value["phase_images"]
    if (
        type(main) is not dict
        or set(main) != {"lexical_path", "resolved_path"}
        or type(phases) is not dict
        or set(phases) != set(NATIVE_IMAGE_PHASES)
    ):
        raise RuntimeError("audit isolated native-image phase schema changed")
    previous: set[str] = set()
    for phase in NATIVE_IMAGE_PHASES:
        rows = phases[phase]
        if type(rows) is not list or not rows:
            raise RuntimeError("audit isolated native-image phase is empty")
        resolved_order: list[str] = []
        for row in rows:
            if (
                type(row) is not dict
                or set(row) != {"lexical_path", "resolved_path"}
                or type(row["lexical_path"]) is not str
                or type(row["resolved_path"]) is not str
                or not os.path.isabs(row["lexical_path"])
                or not os.path.isabs(row["resolved_path"])
                or os.path.realpath(row["lexical_path"]) != row["resolved_path"]
                or _is_system_native_path(row["lexical_path"])
                or _is_system_native_path(row["resolved_path"])
            ):
                raise RuntimeError("audit isolated native-image phase row is malformed")
            resolved_order.append(row["resolved_path"])
        if resolved_order != sorted(set(resolved_order)):
            raise RuntimeError("audit isolated native-image phase is not uniquely sorted")
        current = set(resolved_order)
        if not previous.issubset(current):
            raise RuntimeError("audit isolated native-image phases are not monotone")
        previous = current
    if main not in phases["bootstrap_pre_third_party"]:
        raise RuntimeError("audit native-image main executable is absent from bootstrap phase")
    return value


def _macho_load_commands(path: Path, otool: Path) -> tuple[str | None, list[str], list[str]]:
    completed = subprocess.run(
        [str(otool), "-l", str(path)],
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"audit otool failed for native image: {path}")
    lines = completed.stdout.splitlines()
    install_names: list[str] = []
    rpaths: list[str] = []
    dependencies: list[str] = []
    load_commands = {
        "LC_LOAD_DYLIB",
        "LC_LOAD_WEAK_DYLIB",
        "LC_REEXPORT_DYLIB",
        "LC_LOAD_UPWARD_DYLIB",
    }
    for index, line in enumerate(lines):
        command = line.strip()
        if command == "cmd LC_ID_DYLIB":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    install_names.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command.removeprefix("cmd ") in load_commands:
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    dependencies.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command == "cmd LC_RPATH":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("path "):
                    rpaths.append(item[5:].split(" (offset ", 1)[0])
                    break
    unique_install_names = sorted(set(install_names))
    if len(unique_install_names) > 1:
        raise RuntimeError(f"audit native image has multiple install names: {path}")
    return (
        unique_install_names[0] if unique_install_names else None,
        list(dict.fromkeys(rpaths)),
        sorted(set(dependencies)),
    )


def _expand_macho_anchor(value: str, loader: Path, executable: Path) -> Path:
    if value == "@loader_path":
        return loader.parent
    if value.startswith("@loader_path/"):
        return loader.parent / value[len("@loader_path/") :]
    if value == "@executable_path":
        return executable.parent
    if value.startswith("@executable_path/"):
        return executable.parent / value[len("@executable_path/") :]
    if os.path.isabs(value):
        return Path(value)
    raise RuntimeError(f"audit unsupported Mach-O path anchor: {value}")


def _resolve_macho_dependency(
    install_name: str,
    loader: Path,
    executable: Path,
    rpaths: Sequence[str],
) -> tuple[str, str, str | None]:
    if _is_system_native_path(install_name):
        return "system_dyld_cache", install_name, None
    if install_name.startswith("@rpath/"):
        suffix = install_name[len("@rpath/") :]
        candidates: list[Path] = []
        for rpath in rpaths:
            base = _expand_macho_anchor(rpath, loader, executable)
            candidate = Path(os.path.abspath(os.path.normpath(base / suffix)))
            if os.path.lexists(candidate):
                candidates.append(candidate)
        if not candidates:
            raise RuntimeError(f"audit unresolved @rpath dependency {install_name} in {loader}")
        lexical = str(candidates[0])
    else:
        lexical = str(
            Path(
                os.path.abspath(
                    os.path.normpath(_expand_macho_anchor(install_name, loader, executable))
                )
            )
        )
    resolved = os.path.realpath(lexical)
    if _is_system_native_path(lexical) or _is_system_native_path(resolved):
        return "system_dyld_cache", lexical, None
    if not os.path.lexists(lexical):
        raise RuntimeError(f"audit non-system native dependency is absent: {lexical}")
    return "non_system", lexical, resolved


def bounded_non_system_native_provenance() -> dict[str, Any]:
    probe = isolated_native_image_probe()
    phases = probe["phase_images"]
    executable = Path(probe["main_executable_image"]["resolved_path"])
    otool = Path("/usr/bin/otool")
    otool_bytes, _otool_metadata = stable_regular_file_bytes(otool)
    aliases: dict[str, set[str]] = {}
    actual_phases: dict[str, set[str]] = {}
    for phase in NATIVE_IMAGE_PHASES:
        actual_phases[phase] = {row["resolved_path"] for row in phases[phase]}
        for row in phases[phase]:
            aliases.setdefault(row["resolved_path"], set()).add(row["lexical_path"])
    pending = sorted(actual_phases["full_stack_post_import"])
    metadata: dict[str, tuple[str | None, list[str], list[dict[str, Any]]]] = {}
    while pending:
        resolved = pending.pop(0)
        if resolved in metadata:
            continue
        path = Path(resolved)
        if not path.is_absolute() or _is_system_native_path(resolved):
            raise RuntimeError("audit non-system native closure contains an invalid root")
        install_name, rpaths, raw_dependencies = _macho_load_commands(path, otool)
        dependency_rows: list[dict[str, Any]] = []
        for raw in raw_dependencies:
            classification, lexical, dependency_resolved = _resolve_macho_dependency(
                raw, path, executable, rpaths
            )
            dependency_rows.append(
                {
                    "install_name": raw,
                    "classification": classification,
                    "lexical_path": lexical,
                    "resolved_path": dependency_resolved,
                }
            )
            if dependency_resolved is not None:
                aliases.setdefault(dependency_resolved, set()).add(lexical)
                if dependency_resolved not in metadata and dependency_resolved not in pending:
                    pending.append(dependency_resolved)
                    pending.sort()
        metadata[resolved] = (
            install_name,
            rpaths,
            sorted(
                dependency_rows,
                key=lambda row: (
                    row["install_name"],
                    row["lexical_path"],
                    row["resolved_path"] or "",
                ),
            ),
        )
    rows: list[dict[str, Any]] = []
    for resolved in sorted(metadata):
        payload, snapshot = stable_regular_file_bytes(Path(resolved))
        install_name, rpaths, dependencies = metadata[resolved]
        lexical_paths = sorted(aliases.get(resolved, {resolved}))
        if any(os.path.realpath(path) != resolved for path in lexical_paths):
            raise RuntimeError("audit native lexical alias does not resolve to its row")
        rows.append(
            {
                "resolved_path": resolved,
                "lexical_paths": lexical_paths,
                "install_name": install_name,
                "size": int(snapshot["st_size"]),
                "sha256": sha256_bytes(payload),
                "rpaths": rpaths,
                "dependencies": dependencies,
                "actual_loaded_phases": [
                    phase for phase in NATIVE_IMAGE_PHASES if resolved in actual_phases[phase]
                ],
            }
        )
    encoded_rows = json.dumps(rows, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    transition_added = [
        row for row in phases["post_manifest_validation"] if row not in phases["runner_post_import"]
    ]
    if len(transition_added) != 1 or not Path(transition_added[0]["resolved_path"]).name.startswith(
        "pyexpat."
    ):
        raise RuntimeError("audit post-manifest-validation phase did not add exactly pyexpat")
    return {
        "contract": "bounded_non_system_macho_closure_v1",
        "threat_boundary": "reproducibility_witness_not_malicious_same_uid_prevention",
        "bootstrap_root_of_trust_includes_hash_primitive": True,
        "probe_induced_images_included": ["ctypes", "_ctypes"],
        "phase_transition_causes": {
            "post_manifest_validation": {
                "operation": "signed_dyld_cache_provenance.platform.mac_ver",
                "added_images": transition_added,
            }
        },
        "system_leaf_prefixes": list(SYSTEM_NATIVE_PREFIXES),
        "main_executable_image": probe["main_executable_image"],
        "phase_images": phases,
        "otool": {"path": str(otool), "sha256": sha256_bytes(otool_bytes)},
        "closure_image_count": len(rows),
        "closure_sha256": sha256_bytes(encoded_rows),
        "images": rows,
    }


def signed_dyld_cache_provenance() -> dict[str, Any]:
    codesign = Path("/usr/bin/codesign")
    codesign_bytes, _metadata = stable_regular_file_bytes(codesign)
    cache_root = Path("/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld")
    prefix = "dyld_shared_cache_arm64e"
    cache_paths = sorted(
        (
            path
            for path in cache_root.iterdir()
            if path.name == prefix
            or re.fullmatch(r"dyld_shared_cache_arm64e\.\d+(?:\..+)?", path.name)
        ),
        key=lambda path: path.name,
    )
    if not cache_paths:
        raise RuntimeError("audit arm64e dyld shared cache is missing")
    environment = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    rows: list[dict[str, Any]] = []
    for path in cache_paths:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise RuntimeError("audit dyld cache is not a lexical regular file")
        verified = subprocess.run(
            [str(codesign), "--verify", "--strict", str(path)],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        described = subprocess.run(
            [str(codesign), "-dvvv", str(path)],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        after = os.lstat(path)
        initial_identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
        )
        final_identity = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_size,
            after.st_mtime_ns,
        )
        hashes = [
            line.split("=", 1)[1]
            for line in (described.stdout + described.stderr).splitlines()
            if line.startswith("CandidateCDHashFull sha256=")
        ]
        if (
            verified.returncode != 0
            or described.returncode != 0
            or initial_identity != final_identity
            or len(hashes) != 1
            or not re.fullmatch(r"[0-9a-f]{64}", hashes[0])
        ):
            raise RuntimeError(f"audit signed dyld cache attestation failed: {path}")
        rows.append(
            {
                "path": str(path),
                "size": int(before.st_size),
                "candidate_cdhash_full_sha256": hashes[0],
            }
        )
    mac_version = platform.mac_ver()
    return {
        "darwin_uname": list(os.uname()),
        "mac_ver": [mac_version[0], list(mac_version[1]), mac_version[2]],
        "machine": platform.machine(),
        "codesign_tool": {"path": str(codesign), "sha256": sha256_bytes(codesign_bytes)},
        "dyld_cache_root": str(cache_root),
        "dyld_cache_code_directories": rows,
    }


def rebuild_runtime_provenance() -> dict[str, Any]:
    venv_root = (REPOSITORY / ".venv").resolve()
    site_packages = (
        venv_root
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    ).resolve()
    stdlib_root = Path(sysconfig.get_path("stdlib")).resolve()
    real_executable = Path(os.path.realpath(sys.executable))
    executable_bytes, _metadata = stable_regular_file_bytes(real_executable)
    base_prefix = Path(sys.base_prefix).resolve()
    framework_files: dict[str, str] = {}
    for path in (
        base_prefix / "Python",
        base_prefix / "Resources" / "Python.app" / "Contents" / "MacOS" / "Python",
    ):
        payload, _snapshot = stable_regular_file_bytes(path)
        framework_files[str(path)] = sha256_bytes(payload)

    scipy_version = importlib.metadata.version("scipy")
    distributions: dict[str, dict[str, Any]] = {}
    for name, version, module_file in (
        ("numpy", np.__version__, np.__file__),
        ("scipy", scipy_version, site_packages / "scipy" / "__init__.py"),
    ):
        file_hash_cache: dict[str, str] = {}
        import_tree_closures = {
            root_name: {
                "path": str(site_packages / root_name),
                **exact_import_tree_closure(site_packages / root_name, file_hash_cache),
            }
            for root_name in (name, f"{name}.libs")
        }
        record_path = site_packages / f"{name}-{version}.dist-info" / "RECORD"
        distributions[name] = {
            "version": version,
            "module_origin": str(Path(module_file).resolve()),
            "record_path": str(record_path),
            **distribution_record_closure(
                venv_root,
                site_packages,
                record_path,
                file_hash_cache,
            ),
            "import_tree_closures": import_tree_closures,
        }

    numpy_configuration = np.show_config(mode="dicts")
    if type(numpy_configuration) is not dict:
        raise RuntimeError("audit NumPy build configuration is not a dictionary")
    provenance = {
        "contract": "bounded_runtime_closure_v2",
        "python": {
            "version": sys.version,
            "cache_tag": sys.implementation.cache_tag,
            "invocation_path": os.path.abspath(sys.executable),
            "real_executable_path": str(real_executable),
            "real_executable_sha256": sha256_bytes(executable_bytes),
            "stdlib_root": str(stdlib_root),
            "stdlib_closure": stdlib_tree_closure(stdlib_root),
            "framework_files": framework_files,
        },
        "venv_root": str(venv_root),
        "site_packages": str(site_packages),
        "distributions": distributions,
        "numpy_build_configuration": numpy_configuration,
        "non_system_native": bounded_non_system_native_provenance(),
        "system_native": signed_dyld_cache_provenance(),
    }
    require_finite_json(provenance)
    return provenance


@functools.lru_cache(maxsize=1)
def current_runtime_provenance() -> dict[str, Any]:
    return rebuild_runtime_provenance()


def parse_json_object_bytes(
    payload: bytes, label: str, *, require_canonical: bool = True
) -> dict[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key in {label}: {key}")
            value[key] = item
        return value

    def reject_constant(value: str) -> Any:
        raise ValueError(f"nonfinite JSON constant in {label}: {value}")

    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    if type(value) is not dict:
        raise ValueError(f"{label} must contain one JSON object")
    require_finite_json(value)
    if require_canonical and canonical_json_bytes(value) != payload:
        raise ValueError(f"{label} is not canonical JSON")
    return value


def exact_json_contract(observed: Any, expected: Any) -> bool:
    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            exact_json_contract(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            exact_json_contract(left, right) for left, right in zip(observed, expected, strict=True)
        )
    return bool(observed == expected)


def load_json(path: Path) -> dict[str, Any]:
    payload, _metadata = stable_regular_file_bytes(Path(path))
    return parse_json_object_bytes(payload, str(path), require_canonical=False)


def close(left: float, right: float, tolerance: float = 5.0e-13) -> bool:
    return abs(float(left) - float(right)) <= tolerance * max(1.0, abs(left), abs(right))


def _nonnegative_float(value: Any) -> bool:
    return type(value) is float and math.isfinite(value) and value >= 0.0


def _bernoulli_scalar(value: float) -> float:
    if abs(value) < 1.0e-5:
        return 1.0 - value / 2.0 + value**2 / 12.0 - value**4 / 720.0 + value**6 / 30240.0
    return value / math.expm1(value)


def _sg_generator_trace(
    cells: int,
    bounds: Sequence[float],
    diffusion: float,
    drift: Callable[[float], float],
) -> float:
    spacing = (float(bounds[1]) - float(bounds[0])) / cells
    rate_scale = diffusion / spacing**2
    total = 0.0
    for index in range(1, cells):
        face = float(bounds[0]) + index * spacing
        peclet = drift(face) * spacing / diffusion
        total -= rate_scale * (_bernoulli_scalar(-peclet) + _bernoulli_scalar(peclet))
    return float(total)


def expected_generator_diagonal_sums(cells: int, manifest: dict[str, Any]) -> tuple[float, float]:
    physical = manifest["physical_parameters"]
    finite_volume = manifest["finite_volume"]
    diffusion = physical["particle_diffusion"]
    stiffness = physical["ou_stiffness"]
    mean = physical["ou_mean"]
    midpoint = _sg_generator_trace(
        cells,
        finite_volume["midpoint_bounds"],
        diffusion / 2.0,
        lambda value: -stiffness * (value - mean),
    )
    parallel = _sg_generator_trace(
        cells,
        finite_volume["relative_parallel_bounds"],
        2.0 * diffusion,
        lambda value: -stiffness * value,
    )
    perpendicular_spacing = physical["transverse_width"] / cells
    perpendicular_rate = 2.0 * diffusion / perpendicular_spacing**2
    perpendicular = -2.0 * cells * perpendicular_rate
    relative = cells * parallel + cells * perpendicular
    return midpoint, float(relative)


CONTROL_KEYS = {
    "status",
    "reason",
    "theta",
    "weights",
    "retained_maximum_count",
    "topology",
    "stationary_scan",
    "roots",
    "all_bracketed_roots",
    "tail_trace",
    "model_diagnostics",
    "peak_minimum_to_maximum_ratio",
    "valley_to_smaller_peak_ratios",
    "event_basin_masses",
    "event_partition_closure_error",
    "final_survival",
    "minimum_final_state_component",
    "score_term_margins",
    "robustness_score",
    "gates",
    "all_gates_passed",
}
ROOT_KEYS = {
    "bracket_index",
    "bracket",
    "time",
    "density_per_budget",
    "scaled_root_residual",
    "scaled_curvature",
    "type",
    "survival",
    "minimum_state_component",
    "differential_mass_balance_error",
    "density_eligible",
    "residual_eligible",
    "curvature_eligible",
    "duplicate_refined_root",
    "eligible",
    "separation_eligible",
    "eligibility_reasons",
}
SAVED_TRACE_KEYS = {
    "time",
    "density",
    "density_per_budget",
    "first_derivative_per_budget",
    "second_derivative_per_budget",
    "survival",
    "minimum_state_component",
    "differential_mass_balance_error",
}
STATE_LAW_KEYS = {
    "density",
    "density_per_budget",
    "survival",
    "minimum_state_component",
    "survival_derivative",
    "survival_density_identity_error",
    "differential_mass_balance_error",
}
SCAN_KEYS = {
    "spacing",
    "time_window",
    "grid_point_count",
    "reference_maximum_density_per_budget",
    "endpoint_first_derivatives_per_budget",
    "endpoint_signs_passed",
    "minimum_sampled_state",
    "minimum_sampled_density",
    "minimum_sampled_survival",
    "maximum_sampled_survival_increase",
    "maximum_sampled_differential_mass_balance_error",
    "full_scan_trace",
    "saved_trace",
    "roots",
    "all_bracketed_roots",
    "topology",
    "physical_law_gates",
}
MODEL_DIAGNOSTIC_KEYS = {
    "mesh",
    "state_count",
    "matrix_free_full_generator",
    "initial_mass",
    "initial_mass_error",
    "installed_budget",
    "physical_installed_budget",
    "physical_installed_budget_absolute_error",
    "minimum_weight",
    "weight_sum_error",
    "minimum_killing_per_budget",
    "maximum_killing_per_budget",
    "midpoint_killing_profile_minimum",
    "midpoint_killing_profile_maximum",
    "midpoint_killing_profile_sum",
    "contact_killing_profile_minimum",
    "contact_killing_profile_maximum",
    "contact_killing_profile_sum",
    "midpoint_generator_diagonal_sum",
    "relative_generator_diagonal_sum",
    "generator_killing_identity_error",
    "analytic_column_operator_trace",
    "factor_diagnostics",
}
FACTOR_DIAGNOSTIC_KEYS = {
    "cells_per_coordinate",
    "state_count_if_full_matrix_formed",
    "spacings",
    "patch_integrals",
    "maximum_patch_quadrature_error_estimate",
    "midpoint_initial_mass",
    "relative_initial_mass",
    "maximum_initial_quadrature_error_estimate",
    "contact_area",
    "contact_area_exact",
    "contact_area_error_estimate",
    "midpoint_generator_row_error",
    "relative_generator_row_error",
}
LAW_GATE_NAMES = {
    "positive_density_and_survival",
    "state_nonnegative",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
}
HOMOTOPY_ROW_KEYS = {
    "budget",
    "status",
    "converged",
    "iterations",
    "reason",
    "point",
    "maximum_scaled_residual",
}
SNAPSHOT_KEYS = {
    "time",
    "budget",
    "theta",
    "weights",
    "density_per_budget",
    "per_budget_time_jets_0_to_4",
    "allocation_time_jets",
}
DERIVATIVE_ROW_KEYS = {
    "allocation_step",
    "relative_time_step",
    "maximum_state_tangent_relative_l1_error",
    "maximum_dimensionless_jacobian_error",
}
DERIVATIVE_AUDIT_KEYS = {
    "rows",
    "state_error_decrease_or_floor",
    "jacobian_error_decrease_or_floor",
    "passed",
}
CUSP_DIAGNOSTIC_BASE_KEYS = {
    "maximum_dimensionless_residual",
    "minimum_weight",
    "scaled_fourth_derivative",
    "projected_singular_values",
    "projected_singular_value_ratio",
    "full_smallest_singular_value",
    "determinant_factorization_relative_residual",
    "maximum_survival_identity_residual",
    "model_diagnostics",
    "state_law_diagnostics",
    "dimensionless_jacobian",
    "derivative_audit",
}
CUSP_GATE_NAMES = {
    "cusp_residual",
    "simplex_margin",
    "quartic_nondegeneracy",
    "projected_rank_floor",
    "projected_rank_ratio",
    "full_jacobian_rank",
    "determinant_factorization",
    "mixed_jet_audit",
    "survival_identities",
    *LAW_GATE_NAMES,
}
FOLD_NODE_KEYS = {
    "acceptance_index",
    "time",
    "theta",
    "weights",
    "normalized_fold_residual",
    "scaled_third_derivative",
    "dimensionless_fold_singular_values",
    "model_diagnostics",
    "state_law_diagnostics",
    "physical_law_gates",
}
COMPARISON_NODE_KEYS = {
    *FOLD_NODE_KEYS,
    "signed_time_offset",
    "target_signed_time_offset",
    "absolute_time_offset_mismatch",
}


def _float_vector(value: Any, length: int) -> bool:
    return (
        type(value) is list and len(value) == length and all(type(item) is float for item in value)
    )


def _float_matrix(value: Any, rows: int, columns: int) -> bool:
    return (
        type(value) is list
        and len(value) == rows
        and all(_float_vector(row, columns) for row in value)
    )


def weights_from_theta(theta: list[float], manifest: dict[str, Any]) -> list[float]:
    reference = manifest["allocation_chart"]["reference_weights"]
    basis = manifest["allocation_chart"]["P"]
    return [
        reference[row] + sum(basis[row][column] * theta[column] for column in range(2))
        for row in range(4)
    ]


def point_in_trust_box(time: float, theta: list[float], manifest: dict[str, Any]) -> bool:
    try:
        solver = manifest["solver"]
        weights = weights_from_theta(theta, manifest)
        return bool(
            type(time) is float
            and _float_vector(theta, 2)
            and solver["time_trust_box"][0] <= time <= solver["time_trust_box"][1]
            and max(abs(value) for value in theta) <= solver["maximum_theta_linf"]
            and min(weights) >= solver["minimum_simplex_weight"]
        )
    except (KeyError, TypeError, ValueError):
        return False


def validate_model_diagnostics(
    value: Any,
    cells: int,
    manifest: dict[str, Any],
    *,
    budget: float | None = None,
    weights: list[float] | None = None,
) -> bool:
    if type(value) is not dict or set(value) != MODEL_DIAGNOSTIC_KEYS:
        return False
    try:
        factors = value["factor_diagnostics"]
        primitive_nonnegative = {
            "initial_mass_error",
            "installed_budget",
            "physical_installed_budget",
            "physical_installed_budget_absolute_error",
            "weight_sum_error",
            "minimum_killing_per_budget",
            "maximum_killing_per_budget",
            "midpoint_killing_profile_minimum",
            "midpoint_killing_profile_maximum",
            "midpoint_killing_profile_sum",
            "contact_killing_profile_minimum",
            "contact_killing_profile_maximum",
            "contact_killing_profile_sum",
            "generator_killing_identity_error",
        }
        midpoint_spacing = factors["spacings"]["midpoint"]
        parallel_spacing = factors["spacings"]["relative_parallel"]
        perpendicular_spacing = factors["spacings"]["relative_perp"]
        midpoint_minimum = value["midpoint_killing_profile_minimum"]
        midpoint_maximum = value["midpoint_killing_profile_maximum"]
        midpoint_sum = value["midpoint_killing_profile_sum"]
        contact_minimum = value["contact_killing_profile_minimum"]
        contact_maximum = value["contact_killing_profile_maximum"]
        contact_sum = value["contact_killing_profile_sum"]
        width = manifest["physical_parameters"]["transverse_width"]
        reconstructed_minimum_killing = midpoint_minimum * contact_minimum / width
        reconstructed_maximum_killing = midpoint_maximum * contact_maximum / width
        reconstructed_killing_sum = midpoint_sum * contact_sum / width
        reconstructed_trace = (
            cells**2 * value["midpoint_generator_diagonal_sum"]
            + cells * value["relative_generator_diagonal_sum"]
            - value["installed_budget"] * reconstructed_killing_sum
        )
        row_error_bound = (
            factors["midpoint_generator_row_error"]
            + factors["relative_generator_row_error"]
            + manifest["factor_gates"]["maximum_error_estimate_undercoverage"]
        )
        expected_midpoint_diagonal, expected_relative_diagonal = expected_generator_diagonal_sums(
            cells, manifest
        )
        return bool(
            type(value["mesh"]) is list
            and len(value["mesh"]) == 3
            and all(type(item) is int and item == cells for item in value["mesh"])
            and type(value["state_count"]) is int
            and value["state_count"] == cells**3
            and value["matrix_free_full_generator"] is True
            and all(
                type(value[key]) is float
                for key in MODEL_DIAGNOSTIC_KEYS
                - {"mesh", "state_count", "matrix_free_full_generator", "factor_diagnostics"}
            )
            and type(factors) is dict
            and set(factors) == FACTOR_DIAGNOSTIC_KEYS
            and type(factors["cells_per_coordinate"]) is int
            and factors["cells_per_coordinate"] == cells
            and type(factors["state_count_if_full_matrix_formed"]) is int
            and factors["state_count_if_full_matrix_formed"] == cells**3
            and type(factors["spacings"]) is dict
            and set(factors["spacings"]) == {"midpoint", "relative_parallel", "relative_perp"}
            and all(type(item) is float for item in factors["spacings"].values())
            and _float_vector(factors["patch_integrals"], 4)
            and all(
                type(factors[key]) is float
                for key in FACTOR_DIAGNOSTIC_KEYS
                - {
                    "cells_per_coordinate",
                    "state_count_if_full_matrix_formed",
                    "spacings",
                    "patch_integrals",
                }
            )
            and factor_diagnostics_pass(value, manifest)
            and all(_nonnegative_float(value[key]) for key in primitive_nonnegative)
            and type(value["initial_mass"]) is float
            and value["initial_mass"] > 0.0
            and type(value["minimum_weight"]) is float
            and type(value["midpoint_generator_diagonal_sum"]) is float
            and value["midpoint_generator_diagonal_sum"] <= 0.0
            and close(value["midpoint_generator_diagonal_sum"], expected_midpoint_diagonal)
            and type(value["relative_generator_diagonal_sum"]) is float
            and value["relative_generator_diagonal_sum"] <= 0.0
            and close(value["relative_generator_diagonal_sum"], expected_relative_diagonal)
            and midpoint_minimum <= midpoint_maximum <= 1.0 / midpoint_spacing + 5.0e-13
            and contact_minimum <= contact_maximum <= 1.0 + 5.0e-13
            and close(midpoint_sum * midpoint_spacing, 1.0)
            and close(
                contact_sum * parallel_spacing * perpendicular_spacing,
                factors["contact_area"],
            )
            and close(value["minimum_killing_per_budget"], reconstructed_minimum_killing)
            and close(value["maximum_killing_per_budget"], reconstructed_maximum_killing)
            and value["minimum_killing_per_budget"] <= value["maximum_killing_per_budget"]
            and close(value["analytic_column_operator_trace"], reconstructed_trace)
            and value["analytic_column_operator_trace"] <= 0.0
            and value["generator_killing_identity_error"] <= row_error_bound
            and close(
                value["physical_installed_budget"],
                value["installed_budget"] * midpoint_sum * midpoint_spacing,
            )
            and close(value["initial_mass_error"], abs(value["initial_mass"] - 1.0))
            and close(
                value["physical_installed_budget_absolute_error"],
                abs(value["physical_installed_budget"] - value["installed_budget"]),
            )
            and (budget is None or close(value["installed_budget"], budget))
            and (
                weights is None
                or (
                    _float_vector(weights, 4)
                    and close(value["minimum_weight"], min(weights))
                    and close(value["weight_sum_error"], abs(sum(weights) - 1.0))
                )
            )
        )
    except (KeyError, TypeError, ValueError):
        return False


def factor_diagnostics_pass(value: Any, manifest: dict[str, Any]) -> bool:
    """Independently reconstruct the frozen finite-volume factor gates."""

    try:
        mesh = value["mesh"]
        factors = value["factor_diagnostics"]
        if (
            type(mesh) is not list
            or len(mesh) != 3
            or not all(type(item) is int for item in mesh)
            or len(set(mesh)) != 1
            or type(factors) is not dict
            or set(factors) != FACTOR_DIAGNOSTIC_KEYS
        ):
            return False
        cells = mesh[0]
        finite_volume = manifest["finite_volume"]
        physical = manifest["physical_parameters"]
        rules = manifest["factor_gates"]
        expected_spacings = {
            "midpoint": (finite_volume["midpoint_bounds"][1] - finite_volume["midpoint_bounds"][0])
            / cells,
            "relative_parallel": (
                finite_volume["relative_parallel_bounds"][1]
                - finite_volume["relative_parallel_bounds"][0]
            )
            / cells,
            "relative_perp": physical["transverse_width"] / cells,
        }
        spacing_error = max(
            abs(factors["spacings"][key] - expected) for key, expected in expected_spacings.items()
        )
        patch_error = max(abs(item - 1.0) for item in factors["patch_integrals"])
        initial_error = max(
            abs(factors["midpoint_initial_mass"] - 1.0),
            abs(factors["relative_initial_mass"] - 1.0),
        )
        expected_contact = math.pi * physical["contact_radius"] ** 2
        contact_exact_error = abs(factors["contact_area_exact"] - expected_contact)
        contact_error = abs(factors["contact_area"] - factors["contact_area_exact"])
        patch_estimate = factors["maximum_patch_quadrature_error_estimate"]
        initial_estimate = factors["maximum_initial_quadrature_error_estimate"]
        contact_estimate = factors["contact_area_error_estimate"]
        row_errors = (
            factors["midpoint_generator_row_error"],
            factors["relative_generator_row_error"],
        )
        mass_tolerance = rules["maximum_mass_or_conservation_error"]
        estimate_tolerance = rules["maximum_quadrature_error_estimate"]
        undercoverage = rules["maximum_error_estimate_undercoverage"]
        return bool(
            spacing_error <= rules["maximum_spacing_reconstruction_error"]
            and patch_error <= mass_tolerance
            and initial_error <= mass_tolerance
            and contact_exact_error <= undercoverage
            and contact_error <= mass_tolerance
            and all(
                type(item) is float and math.isfinite(item) and 0.0 <= item <= estimate_tolerance
                for item in (patch_estimate, initial_estimate, contact_estimate)
            )
            and patch_error <= patch_estimate + undercoverage
            and initial_error <= initial_estimate + undercoverage
            and contact_error <= contact_estimate + undercoverage
            and all(
                type(item) is float
                and math.isfinite(item)
                and 0.0 <= item <= rules["maximum_generator_row_error"]
                for item in row_errors
            )
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_state_law(value: Any, *, budget: float | None = None) -> bool:
    try:
        return bool(
            type(value) is dict
            and set(value) == STATE_LAW_KEYS
            and all(type(value[key]) is float for key in STATE_LAW_KEYS)
            and _nonnegative_float(value["survival_density_identity_error"])
            and _nonnegative_float(value["differential_mass_balance_error"])
            and close(
                value["survival_density_identity_error"],
                value["differential_mass_balance_error"],
            )
            and close(value["survival_derivative"] + value["density"], 0.0)
            and (budget is None or close(value["density"], budget * value["density_per_budget"]))
        )
    except (KeyError, TypeError):
        return False


def reconstruct_law_gates(
    diagnostics: dict[str, Any], rows: list[dict[str, float]], manifest: dict[str, Any]
) -> dict[str, bool]:
    rules = manifest["representative_gates"]
    return {
        "positive_density_and_survival": bool(
            rows
            and min(row["density"] for row in rows) > rules["minimum_density"]
            and min(row["survival"] for row in rows) > rules["minimum_survival"]
        ),
        "state_nonnegative": bool(
            rows
            and min(row["minimum_state_component"] for row in rows)
            >= -rules["maximum_negative_state_tolerance"]
        ),
        "survival_density_identity": bool(
            rows
            and max(row["survival_density_identity_error"] for row in rows)
            <= rules["maximum_survival_identity_error"]
        ),
        "generator_killing_identity": diagnostics["generator_killing_identity_error"]
        <= rules["maximum_generator_killing_identity_error"],
        "differential_mass_balance": bool(
            rows
            and max(row["differential_mass_balance_error"] for row in rows)
            <= rules["maximum_differential_mass_balance_error"]
        ),
        "initial_mass": diagnostics["initial_mass_error"] <= rules["maximum_initial_mass_error"],
        "installed_budget": diagnostics["physical_installed_budget_absolute_error"]
        <= rules["maximum_installed_budget_error"],
        "finite_factor_diagnostics": factor_diagnostics_pass(diagnostics, manifest),
    }


def _root_contract(root: Any, index: int) -> bool:
    try:
        return bool(
            type(root) is dict
            and set(root) == ROOT_KEYS
            and type(root["bracket_index"]) is int
            and root["bracket_index"] == index
            and type(root["bracket"]) is list
            and len(root["bracket"]) == 2
            and all(type(item) is float for item in root["bracket"])
            and root["bracket"][0] <= root["time"] <= root["bracket"][1]
            and all(
                type(root[key]) is float
                for key in {
                    "time",
                    "density_per_budget",
                    "survival",
                    "minimum_state_component",
                    "differential_mass_balance_error",
                }
            )
            and all(
                root[key] is None or type(root[key]) is float
                for key in {"scaled_root_residual", "scaled_curvature"}
            )
            and _nonnegative_float(root["differential_mass_balance_error"])
            and (root["scaled_root_residual"] is None or root["scaled_root_residual"] >= 0.0)
            and root["type"] in {"maximum", "minimum"}
            and type(root["eligibility_reasons"]) is list
            and all(type(item) is str for item in root["eligibility_reasons"])
            and all(
                type(root[key]) is bool
                for key in {
                    "density_eligible",
                    "residual_eligible",
                    "curvature_eligible",
                    "duplicate_refined_root",
                    "eligible",
                    "separation_eligible",
                }
            )
            and root["eligible"]
            == bool(
                root["density_eligible"]
                and root["residual_eligible"]
                and root["curvature_eligible"]
                and not root["duplicate_refined_root"]
                and root["separation_eligible"]
            )
        )
    except (KeyError, TypeError):
        return False


def reconstruct_root_semantics(
    roots: list[dict[str, Any]], reference_density: float, manifest: dict[str, Any]
) -> bool:
    try:
        rules = manifest["root_search"]
        distinct = [
            index
            for index, root in enumerate(roots)
            if not (index > 0 and root["time"] - roots[index - 1]["time"] < 1.0e-8)
        ]
        positions = {root_index: position for position, root_index in enumerate(distinct)}
        for index, root in enumerate(roots):
            density = bool(
                root["density_per_budget"] > 0.0
                and reference_density > 0.0
                and root["density_per_budget"]
                >= rules["relative_density_floor"] * reference_density
            )
            residual = bool(
                root["scaled_root_residual"] is not None
                and root["scaled_root_residual"] >= 0.0
                and root["scaled_root_residual"] <= rules["maximum_scaled_root_residual"]
            )
            curvature = bool(
                root["scaled_curvature"] is not None
                and abs(root["scaled_curvature"]) >= rules["minimum_absolute_scaled_curvature"]
            )
            duplicate = bool(index > 0 and root["time"] - roots[index - 1]["time"] < 1.0e-8)
            if duplicate:
                separation = True
            else:
                position = positions[index]
                left_gap = (
                    root["time"] - roots[distinct[position - 1]]["time"]
                    if position > 0
                    else math.inf
                )
                right_gap = (
                    roots[distinct[position + 1]]["time"] - root["time"]
                    if position + 1 < len(distinct)
                    else math.inf
                )
                separation = bool(min(left_gap, right_gap) >= rules["minimum_root_separation"])
            reasons: list[str] = []
            if not density:
                reasons.append("density_floor_or_positivity")
            if not residual:
                reasons.append("scaled_root_residual")
            if not curvature:
                reasons.append("scaled_curvature")
            if duplicate:
                reasons.append("duplicate_refined_root")
            if not separation:
                reasons.append("minimum_root_separation")
            expected_type = (
                "maximum"
                if root["scaled_curvature"] is not None and root["scaled_curvature"] < 0.0
                else "minimum"
            )
            eligible = bool(density and residual and curvature and not duplicate and separation)
            if (
                root["type"] != expected_type
                or root["density_eligible"] is not density
                or root["residual_eligible"] is not residual
                or root["curvature_eligible"] is not curvature
                or root["duplicate_refined_root"] is not duplicate
                or root["separation_eligible"] is not separation
                or root["eligibility_reasons"] != reasons
                or root["eligible"] is not eligible
            ):
                return False
        return True
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def reconstruct_full_scan_primitives(scan: Any, manifest: dict[str, Any]) -> bool:
    """Independently rebuild the full grid, 70-row projection, and every bracket."""

    try:
        if type(scan) is not dict:
            return False
        spacing = scan["spacing"]
        start, stop = scan["time_window"]
        full = scan["full_scan_trace"]
        saved = scan["saved_trace"]
        roots = scan["all_bracketed_roots"]
        if (
            type(spacing) is not float
            or type(start) is not float
            or type(stop) is not float
            or type(full) is not list
            or type(saved) is not list
            or type(roots) is not list
        ):
            return False
        expected_count = int(round((stop - start) / spacing)) + 1
        if scan["grid_point_count"] != expected_count or len(full) != expected_count:
            return False
        target_budget = manifest["budget_homotopy"]["target_budget"]
        for index, row in enumerate(full):
            if (
                type(row) is not dict
                or set(row) != SAVED_TRACE_KEYS
                or not all(type(row[key]) is float for key in SAVED_TRACE_KEYS)
                or not close(row["time"], start + index * spacing)
                or not close(row["density"], target_budget * row["density_per_budget"])
                or not _nonnegative_float(row["differential_mass_balance_error"])
            ):
                return False
        saved_spacing = manifest["root_search"]["saved_trace_spacing"]
        stride = int(round(saved_spacing / spacing))
        if stride < 1 or not close(stride * spacing, saved_spacing):
            return False
        expected_saved = [
            row for index, row in enumerate(full) if index % stride == 0 or index == len(full) - 1
        ]
        if saved != expected_saved:
            return False
        density_per_budget = [row["density_per_budget"] for row in full]
        survival = [row["survival"] for row in full]
        if (
            not close(scan["reference_maximum_density_per_budget"], max(density_per_budget))
            or not all(
                close(left, right)
                for left, right in zip(
                    scan["endpoint_first_derivatives_per_budget"],
                    [
                        full[0]["first_derivative_per_budget"],
                        full[-1]["first_derivative_per_budget"],
                    ],
                    strict=True,
                )
            )
            or not close(
                scan["minimum_sampled_state"],
                min(row["minimum_state_component"] for row in full),
            )
            or not close(scan["minimum_sampled_density"], min(row["density"] for row in full))
            or not close(scan["minimum_sampled_survival"], min(survival))
            or not close(
                scan["maximum_sampled_survival_increase"],
                max(
                    0.0,
                    max(
                        (right - left for left, right in zip(survival, survival[1:])),
                        default=0.0,
                    ),
                ),
            )
            or not close(
                scan["maximum_sampled_differential_mass_balance_error"],
                max(row["differential_mass_balance_error"] for row in full),
            )
        ):
            return False
        brackets: list[list[float]] = []
        for left_row, right_row in zip(full, full[1:]):
            left = left_row["first_derivative_per_budget"]
            right = right_row["first_derivative_per_budget"]
            if left == 0.0:
                brackets.append([left_row["time"], left_row["time"]])
            elif left * right < 0.0:
                brackets.append([left_row["time"], right_row["time"]])
        if len(roots) != len(brackets):
            return False
        return all(
            root["bracket_index"] == index
            and type(root["bracket"]) is list
            and len(root["bracket"]) == 2
            and all(
                close(observed, expected)
                for observed, expected in zip(root["bracket"], bracket, strict=True)
            )
            for index, (root, bracket) in enumerate(zip(roots, brackets, strict=True))
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def reconstruct_scan(scan: Any, diagnostics: dict[str, Any], manifest: dict[str, Any]) -> bool:
    try:
        if type(scan) is not dict or set(scan) != SCAN_KEYS:
            return False
        full = scan["full_scan_trace"]
        saved = scan["saved_trace"]
        all_roots = scan["all_bracketed_roots"]
        roots = scan["roots"]
        if (
            not reconstruct_full_scan_primitives(scan, manifest)
            or not validate_model_diagnostics(diagnostics, diagnostics["mesh"][0], manifest)
            or type(diagnostics["mesh"]) is not list
            or len(diagnostics["mesh"]) != 3
            or not all(type(item) is int for item in diagnostics["mesh"])
            or len(set(diagnostics["mesh"])) != 1
            or type(scan["spacing"]) is not float
            or scan["spacing"] != manifest["root_search"][f"mesh_{diagnostics['mesh'][0]}_spacing"]
            or scan["time_window"] != manifest["root_search"]["time_window"]
            or type(scan["grid_point_count"]) is not int
            or scan["grid_point_count"]
            != int(round((scan["time_window"][1] - scan["time_window"][0]) / scan["spacing"])) + 1
            or type(scan["reference_maximum_density_per_budget"]) is not float
            or scan["reference_maximum_density_per_budget"] <= 0.0
            or not _float_vector(scan["endpoint_first_derivatives_per_budget"], 2)
            or type(scan["endpoint_signs_passed"]) is not bool
            or scan["endpoint_signs_passed"]
            is not bool(
                scan["endpoint_first_derivatives_per_budget"][0] > 0.0
                and scan["endpoint_first_derivatives_per_budget"][1] < 0.0
            )
            or not all(
                type(scan[key]) is float
                for key in {
                    "minimum_sampled_state",
                    "minimum_sampled_density",
                    "minimum_sampled_survival",
                    "maximum_sampled_survival_increase",
                    "maximum_sampled_differential_mass_balance_error",
                }
            )
            or scan["maximum_sampled_survival_increase"] < 0.0
            or scan["maximum_sampled_differential_mass_balance_error"] < 0.0
            or type(saved) is not list
            or not saved
            or any(
                type(row) is not dict
                or set(row) != SAVED_TRACE_KEYS
                or not all(type(row[key]) is float for key in SAVED_TRACE_KEYS)
                or not close(
                    row["density"],
                    manifest["budget_homotopy"]["target_budget"] * row["density_per_budget"],
                )
                for row in saved
            )
            or saved[0]["time"] != scan["time_window"][0]
            or saved[-1]["time"] != scan["time_window"][1]
            or any(right["time"] <= left["time"] for left, right in zip(saved, saved[1:]))
            or any(
                abs(
                    (row["time"] - scan["time_window"][0])
                    / manifest["root_search"]["saved_trace_spacing"]
                    - round(
                        (row["time"] - scan["time_window"][0])
                        / manifest["root_search"]["saved_trace_spacing"]
                    )
                )
                > 5.0e-13
                for row in saved
            )
            or type(all_roots) is not list
            or any(not _root_contract(root, index) for index, root in enumerate(all_roots))
            or any(right["time"] < left["time"] for left, right in zip(all_roots, all_roots[1:]))
            or roots != [root for root in all_roots if root["eligible"]]
            or not reconstruct_root_semantics(
                all_roots, scan["reference_maximum_density_per_budget"], manifest
            )
            or any(
                root["bracket"][0] < scan["time_window"][0]
                or root["bracket"][1] > scan["time_window"][1]
                or (
                    root["bracket"][0] != root["bracket"][1]
                    and not close(root["bracket"][1] - root["bracket"][0], scan["spacing"])
                )
                or any(
                    abs(
                        (endpoint - scan["time_window"][0]) / scan["spacing"]
                        - round((endpoint - scan["time_window"][0]) / scan["spacing"])
                    )
                    > 5.0e-13
                    for endpoint in root["bracket"]
                )
                for root in all_roots
            )
            or scan["reference_maximum_density_per_budget"] + 5.0e-13
            < max(
                [row["density_per_budget"] for row in saved]
                + [root["density_per_budget"] for root in all_roots]
            )
            or scan["topology"] != [root["type"] for root in roots]
            or type(scan["physical_law_gates"]) is not dict
            or set(scan["physical_law_gates"]) != SCAN_PHYSICAL_GATE_NAMES
            or any(type(value) is not bool for value in scan["physical_law_gates"].values())
        ):
            return False
        rules = manifest["representative_gates"]
        serialized_rows = [
            *full,
            *[
                {
                    "time": root["time"],
                    "density": manifest["budget_homotopy"]["target_budget"]
                    * root["density_per_budget"],
                    "survival": root["survival"],
                    "minimum_state_component": root["minimum_state_component"],
                    "differential_mass_balance_error": root["differential_mass_balance_error"],
                }
                for root in all_roots
            ],
        ]
        ordered = sorted(serialized_rows, key=lambda item: item["time"])
        if (
            any(
                right["survival"] > left["survival"] + rules["maximum_survival_increase"]
                for left, right in zip(ordered, ordered[1:])
            )
            or scan["minimum_sampled_density"]
            > min(row["density"] for row in serialized_rows) + 5.0e-13
            or scan["minimum_sampled_survival"]
            > min(row["survival"] for row in serialized_rows) + 5.0e-13
            or scan["minimum_sampled_state"]
            > min(row["minimum_state_component"] for row in serialized_rows) + 5.0e-13
            or scan["maximum_sampled_differential_mass_balance_error"] + 5.0e-13
            < max(row["differential_mass_balance_error"] for row in serialized_rows)
        ):
            return False
        root_density = [
            manifest["budget_homotopy"]["target_budget"] * row["density_per_budget"]
            for row in all_roots
        ]
        root_survival = [row["survival"] for row in all_roots]
        root_state = [row["minimum_state_component"] for row in all_roots]
        root_mass = [row["differential_mass_balance_error"] for row in all_roots]
        reconstructed = {
            "positive_density_and_survival": bool(
                scan["minimum_sampled_density"] > rules["minimum_density"]
                and scan["minimum_sampled_survival"] > rules["minimum_survival"]
                and min([row["density"] for row in full] + root_density) > rules["minimum_density"]
                and min([row["survival"] for row in full] + root_survival)
                > rules["minimum_survival"]
            ),
            "state_nonnegative": bool(
                scan["minimum_sampled_state"] >= -rules["maximum_negative_state_tolerance"]
                and min([row["minimum_state_component"] for row in full] + root_state)
                >= -rules["maximum_negative_state_tolerance"]
            ),
            "sampled_survival_monotone": scan["maximum_sampled_survival_increase"]
            <= rules["maximum_survival_increase"],
            "survival_density_identity": bool(
                scan["maximum_sampled_differential_mass_balance_error"]
                <= rules["maximum_survival_identity_error"]
                and max([row["differential_mass_balance_error"] for row in full] + root_mass)
                <= rules["maximum_survival_identity_error"]
            ),
            "generator_killing_identity": diagnostics["generator_killing_identity_error"]
            <= rules["maximum_generator_killing_identity_error"],
            "differential_mass_balance": bool(
                scan["maximum_sampled_differential_mass_balance_error"]
                <= rules["maximum_differential_mass_balance_error"]
                and max([row["differential_mass_balance_error"] for row in full] + root_mass)
                <= rules["maximum_differential_mass_balance_error"]
            ),
            "initial_mass": diagnostics["initial_mass_error"]
            <= rules["maximum_initial_mass_error"],
            "installed_budget": diagnostics["physical_installed_budget_absolute_error"]
            <= rules["maximum_installed_budget_error"],
            "finite_factor_diagnostics": factor_diagnostics_pass(diagnostics, manifest),
            "all_bracketed_roots_physical": bool(
                all_roots
                and min(root_density) > rules["minimum_density"]
                and min(root_survival) > rules["minimum_survival"]
                and min(root_state) >= -rules["maximum_negative_state_tolerance"]
                and max(root_mass) <= rules["maximum_differential_mass_balance_error"]
            ),
        }
        return scan["physical_law_gates"] == reconstructed
    except (KeyError, TypeError, ValueError):
        return False


def reconstruct_control(control: dict[str, Any], manifest: dict[str, Any]) -> bool:
    if type(control) is not dict or set(control) != CONTROL_KEYS:
        return False
    if control.get("status") == "HOLD_CONTROL_EVALUATION":
        gates = control.get("gates")
        theta = control.get("theta")
        weights = control.get("weights")
        return (
            type(gates) is dict
            and set(gates) == CONTROL_GATE_NAMES
            and type(control.get("reason")) is str
            and (theta is None or _float_vector(theta, 2))
            and (weights is None or _float_vector(weights, 4))
            and (
                (theta is None and weights is None)
                or (
                    theta is not None
                    and weights is not None
                    and all(
                        close(left, right)
                        for left, right in zip(
                            weights, weights_from_theta(theta, manifest), strict=True
                        )
                    )
                )
            )
            and type(control.get("retained_maximum_count")) is int
            and control.get("retained_maximum_count") == 0
            and control.get("topology") == []
            and control.get("roots") == []
            and control.get("all_bracketed_roots") == []
            and all(value is False for value in gates.values())
            and control.get("all_gates_passed") is False
            and control.get("robustness_score") is None
            and control.get("stationary_scan") is None
            and control.get("model_diagnostics") is None
            and control.get("tail_trace") is None
            and control.get("minimum_final_state_component") is None
            and control.get("peak_minimum_to_maximum_ratio") is None
            and control.get("valley_to_smaller_peak_ratios") is None
            and control.get("event_basin_masses") is None
            and control.get("event_partition_closure_error") is None
            and (
                control.get("final_survival") is None
                or type(control.get("final_survival")) is float
            )
            and control.get("score_term_margins") is None
        )
    try:
        gates = control["gates"]
        if type(gates) is not dict or set(gates) != CONTROL_GATE_NAMES:
            return False
        rules = manifest["representative_gates"]
        roots = control["roots"]
        topology = control["topology"]
        scan = control["stationary_scan"]
        tail = control["tail_trace"]
        diagnostics = control["model_diagnostics"]
        masses = control["event_basin_masses"]
        all_roots = control["all_bracketed_roots"]
        if (
            type(control["retained_maximum_count"]) is not int
            or not validate_model_diagnostics(
                diagnostics,
                diagnostics["mesh"][0],
                manifest,
                budget=manifest["budget_homotopy"]["target_budget"],
                weights=control["weights"],
            )
            or type(control["reason"]) is not str
            or not _float_vector(control["theta"], 2)
            or not _float_vector(control["weights"], 4)
            or any(
                not close(left, right)
                for left, right in zip(
                    control["weights"],
                    weights_from_theta(control["theta"], manifest),
                    strict=True,
                )
            )
            or not reconstruct_scan(scan, diagnostics, manifest)
            or roots != scan["roots"]
            or all_roots != scan["all_bracketed_roots"]
            or topology != scan["topology"]
            or type(tail) is not list
            or len(tail) != len(manifest["representative_gates"]["tail_checkpoints"])
            or any(
                type(row) is not dict
                or set(row) != {"time", *STATE_LAW_KEYS}
                or not all(type(row[key]) is float for key in {"time", *STATE_LAW_KEYS})
                or not validate_state_law(
                    {key: row[key] for key in STATE_LAW_KEYS},
                    budget=manifest["budget_homotopy"]["target_budget"],
                )
                for row in tail
            )
            or [row["time"] for row in tail] != manifest["representative_gates"]["tail_checkpoints"]
        ):
            return False
        maxima = [row for row in roots if row["type"] == "maximum"]
        minima = [row for row in roots if row["type"] == "minimum"]
        alternating = topology in (
            ["maximum"],
            ["maximum", "minimum", "maximum"],
            ["maximum", "minimum", "maximum", "minimum", "maximum"],
        )
        maximum_count = len(maxima) if alternating else 0
        peak_ratio = (
            min(row["density_per_budget"] for row in maxima)
            / max(row["density_per_budget"] for row in maxima)
            if maxima
            else 0.0
        )
        valley_ratios = []
        for index, root in enumerate(roots):
            if root["type"] == "minimum" and 0 < index < len(roots) - 1:
                valley_ratios.append(
                    root["density_per_budget"]
                    / min(
                        roots[index - 1]["density_per_budget"],
                        roots[index + 1]["density_per_budget"],
                    )
                )
        valley_ratio = max(valley_ratios) if valley_ratios else 0.0
        minimum_curvature = min((abs(row["scaled_curvature"]) for row in roots), default=0.0)
        maximum_residual = max((row["scaled_root_residual"] for row in roots), default=None)
        survival_values = [1.0, *(row["survival"] for row in minima), control["final_survival"]]
        reconstructed_masses = [
            left - right for left, right in zip(survival_values, survival_values[1:])
        ]
        if (
            control["retained_maximum_count"] != maximum_count
            or type(control["peak_minimum_to_maximum_ratio"]) is not float
            or control["peak_minimum_to_maximum_ratio"] < 0.0
            or not close(control["peak_minimum_to_maximum_ratio"], peak_ratio)
            or type(control["valley_to_smaller_peak_ratios"]) is not list
            or len(control["valley_to_smaller_peak_ratios"]) != len(valley_ratios)
            or not all(
                _nonnegative_float(value) for value in control["valley_to_smaller_peak_ratios"]
            )
            or any(
                not close(left, right)
                for left, right in zip(
                    control["valley_to_smaller_peak_ratios"],
                    valley_ratios,
                    strict=True,
                )
            )
            or type(control["final_survival"]) is not float
            or control["final_survival"] < 0.0
            or type(control["minimum_final_state_component"]) is not float
            or type(control["event_partition_closure_error"]) is not float
            or control["event_partition_closure_error"] < 0.0
            or type(masses) is not list
            or not all(_nonnegative_float(value) for value in masses)
            or len(masses) != len(maxima)
            or len(reconstructed_masses) != len(maxima)
            or any(value < 0.0 for value in reconstructed_masses)
            or any(
                not close(left, right)
                for left, right in zip(masses, reconstructed_masses, strict=True)
            )
            or not close(control["final_survival"], tail[-1]["survival"])
            or not close(
                control["minimum_final_state_component"], tail[-1]["minimum_state_component"]
            )
        ):
            return False
        trace_rows = [*scan["full_scan_trace"], *tail]
        minimum_density = min(
            scan["minimum_sampled_density"],
            *[row["density"] for row in trace_rows],
            *[0.01 * row["density_per_budget"] for row in all_roots],
        )
        minimum_survival = min(
            scan["minimum_sampled_survival"],
            *[row["survival"] for row in trace_rows],
            *[row["survival"] for row in all_roots],
        )
        maximum_mass_error = max(
            scan["maximum_sampled_differential_mass_balance_error"],
            *[row["differential_mass_balance_error"] for row in trace_rows],
            *[row["differential_mass_balance_error"] for row in all_roots],
        )
        reconstructed = {
            "alternating_topology": alternating,
            "endpoint_signs": scan["endpoint_signs_passed"] is True,
            "peak_ratio": peak_ratio >= rules["minimum_peak_ratio"],
            "valley_ratio": valley_ratio <= rules["maximum_valley_ratio"],
            "curvature": minimum_curvature >= rules["minimum_absolute_scaled_curvature"],
            "root_residual": maximum_residual is not None
            and maximum_residual <= rules["maximum_scaled_root_residual"],
            "event_masses": bool(masses) and min(masses) >= rules["minimum_each_event_basin_mass"],
            "positive_density_and_survival": minimum_density > rules["minimum_density"]
            and minimum_survival > rules["minimum_survival"],
            "survival_monotone": all(
                right <= left + rules["maximum_survival_increase"]
                for left, right in zip(survival_values, survival_values[1:])
            )
            and all(
                right["survival"] <= left["survival"] + rules["maximum_survival_increase"]
                for left, right in zip(tail, tail[1:])
            ),
            "sampled_state_nonnegative": scan["physical_law_gates"]["state_nonnegative"],
            "sampled_survival_monotone": scan["physical_law_gates"]["sampled_survival_monotone"],
            "survival_density_identity": maximum_mass_error
            <= rules["maximum_survival_identity_error"],
            "generator_killing_identity": diagnostics["generator_killing_identity_error"]
            <= rules["maximum_generator_killing_identity_error"],
            "differential_mass_balance": maximum_mass_error
            <= rules["maximum_differential_mass_balance_error"],
            "event_partition_closure": control["event_partition_closure_error"]
            <= rules["maximum_event_partition_closure_error"],
            "final_state_nonnegative": control["minimum_final_state_component"]
            >= -rules["maximum_negative_state_tolerance"],
            "initial_mass": diagnostics["initial_mass_error"]
            <= rules["maximum_initial_mass_error"],
            "installed_budget": diagnostics["physical_installed_budget_absolute_error"]
            <= rules["maximum_installed_budget_error"],
            "finite_factor_diagnostics": True,
        }
        if (
            gates != reconstructed
            or type(control["all_gates_passed"]) is not bool
            or control["all_gates_passed"] is not all(gates.values())
            or control["status"]
            != ("PASS_CONTROL_EVALUATION" if all(gates.values()) else HOLD_STATUS)
        ):
            return False
        margins = {
            "peak_ratio": peak_ratio / rules["minimum_peak_ratio"] - 1.0,
            "valley_ratio": (rules["maximum_valley_ratio"] - valley_ratio)
            / (1.0 - rules["maximum_valley_ratio"]),
            "absolute_scaled_curvature": minimum_curvature
            / rules["minimum_absolute_scaled_curvature"]
            - 1.0,
            "event_basin_mass": min(masses, default=0.0) / rules["minimum_each_event_basin_mass"]
            - 1.0,
        }
        return (
            type(control["score_term_margins"]) is dict
            and set(control["score_term_margins"]) == set(manifest["phase_search"]["score_terms"])
            and all(
                close(control["score_term_margins"][key], value) for key, value in margins.items()
            )
            and close(
                control["robustness_score"],
                min(margins[key] for key in manifest["phase_search"]["score_terms"]),
            )
            and close(
                control["event_partition_closure_error"],
                abs(sum(reconstructed_masses) - (1.0 - control["final_survival"])),
            )
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_homotopy(homotopy: Any, cusp: Any, manifest: dict[str, Any]) -> bool:
    if type(homotopy) is not dict or set(homotopy) != {"status", "rows"}:
        return False
    rows = homotopy["rows"]
    schedule = manifest["budget_homotopy"]["schedule"]
    if type(rows) is not list or not rows or len(rows) > len(schedule):
        return False
    try:
        tolerance = manifest["solver"]["scaled_residual_tolerance"]
        maximum_iterations = manifest["solver"]["maximum_newton_iterations"]
        for index, row in enumerate(rows):
            if (
                type(row) is not dict
                or set(row) != HOMOTOPY_ROW_KEYS
                or type(row["budget"]) is not float
                or not close(row["budget"], schedule[index])
                or type(row["status"]) is not str
                or type(row["converged"]) is not bool
                or type(row["iterations"]) is not int
                or not 0 <= row["iterations"] <= maximum_iterations
                or type(row["reason"]) is not str
                or (row["point"] is not None and not _float_vector(row["point"], 3))
                or (
                    row["maximum_scaled_residual"] is not None
                    and type(row["maximum_scaled_residual"]) is not float
                )
                or (row["point"] is None) != (row["maximum_scaled_residual"] is None)
                or (
                    row["point"] is not None
                    and not point_in_trust_box(row["point"][0], row["point"][1:], manifest)
                )
                or (
                    row["maximum_scaled_residual"] is not None
                    and row["maximum_scaled_residual"] < 0.0
                )
            ):
                return False
            if row["converged"]:
                if (
                    row["status"] != "PASS_CUSP_SOLVE"
                    or row["point"] is None
                    or row["maximum_scaled_residual"] > tolerance
                ):
                    return False
            elif index != len(rows) - 1 or row["status"] != HOLD_STATUS:
                return False
        passed = len(rows) == len(schedule) and all(row["converged"] for row in rows)
        if homotopy["status"] != ("PASS_HOMOTOPY" if passed else HOLD_STATUS):
            return False
        return bool(
            not passed
            or (
                type(cusp) is dict
                and close(rows[-1]["point"][0], cusp["time"])
                and all(
                    close(left, right)
                    for left, right in zip(rows[-1]["point"][1:], cusp["theta"], strict=True)
                )
            )
        )
    except (IndexError, KeyError, TypeError):
        return False


def validate_snapshot(snapshot: Any, manifest: dict[str, Any], *, include_state_law: bool) -> bool:
    keys = set(SNAPSHOT_KEYS)
    if include_state_law:
        keys.add("state_law_diagnostics")
    if type(snapshot) is not dict or set(snapshot) != keys:
        return False
    try:
        if (
            type(snapshot["time"]) is not float
            or type(snapshot["budget"]) is not float
            or not close(snapshot["budget"], manifest["budget_homotopy"]["target_budget"])
            or not _float_vector(snapshot["theta"], 2)
            or not _float_vector(snapshot["weights"], 4)
            or type(snapshot["density_per_budget"]) is not float
            or snapshot["density_per_budget"] <= 0.0
            or not _float_vector(snapshot["per_budget_time_jets_0_to_4"], 5)
            or not _float_matrix(snapshot["allocation_time_jets"], 2, 5)
            or not point_in_trust_box(snapshot["time"], snapshot["theta"], manifest)
            or not close(snapshot["density_per_budget"], snapshot["per_budget_time_jets_0_to_4"][0])
            or any(
                not close(left, right)
                for left, right in zip(
                    snapshot["weights"],
                    weights_from_theta(snapshot["theta"], manifest),
                    strict=True,
                )
            )
        ):
            return False
        if not include_state_law:
            return True
        law = snapshot["state_law_diagnostics"]
        return bool(
            validate_state_law(law, budget=snapshot["budget"])
            and close(law["density_per_budget"], snapshot["density_per_budget"])
        )
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def validate_derivative_audit(derivative: Any, manifest: dict[str, Any]) -> bool:
    if type(derivative) is not dict or set(derivative) != DERIVATIVE_AUDIT_KEYS:
        return False
    rows = derivative["rows"]
    settings = manifest["derivative_audit"]
    if type(rows) is not list or len(rows) != 2:
        return False
    try:
        for index, row in enumerate(rows):
            if (
                type(row) is not dict
                or set(row) != DERIVATIVE_ROW_KEYS
                or not all(type(row[key]) is float for key in DERIVATIVE_ROW_KEYS)
                or row["allocation_step"] != settings["allocation_steps"][index]
                or row["relative_time_step"] != settings["relative_time_steps"][index]
                or row["maximum_state_tangent_relative_l1_error"] < 0.0
                or row["maximum_dimensionless_jacobian_error"] < 0.0
            ):
                return False
        large, small = rows
        state_decreased = small["maximum_state_tangent_relative_l1_error"] <= max(
            settings["roundoff_floor"],
            settings["required_error_reduction_factor"]
            * large["maximum_state_tangent_relative_l1_error"],
        )
        jacobian_decreased = small["maximum_dimensionless_jacobian_error"] <= max(
            settings["roundoff_floor"],
            settings["required_error_reduction_factor"]
            * large["maximum_dimensionless_jacobian_error"],
        )
        passed = bool(
            state_decreased
            and jacobian_decreased
            and small["maximum_state_tangent_relative_l1_error"]
            <= settings["maximum_normalized_disagreement"]
            and small["maximum_dimensionless_jacobian_error"]
            <= settings["maximum_normalized_disagreement"]
        )
        return bool(
            derivative["state_error_decrease_or_floor"] is state_decreased
            and derivative["jacobian_error_decrease_or_floor"] is jacobian_decreased
            and derivative["passed"] is passed
        )
    except (KeyError, TypeError):
        return False


def reconstruct_cusp_diagnostics(
    diagnostics: Any,
    cusp: dict[str, Any],
    mesh_diagnostics: dict[str, Any],
    cells: int,
    manifest: dict[str, Any],
) -> bool:
    expected_keys = CUSP_DIAGNOSTIC_BASE_KEYS | {"gates", "all_gates_passed"}
    if type(diagnostics) is not dict or set(diagnostics) != expected_keys:
        return False
    try:
        scalar_keys = CUSP_DIAGNOSTIC_BASE_KEYS - {
            "model_diagnostics",
            "state_law_diagnostics",
            "dimensionless_jacobian",
            "derivative_audit",
            "projected_singular_values",
        }
        if (
            not all(type(diagnostics[key]) is float for key in scalar_keys)
            or not all(
                _nonnegative_float(diagnostics[key])
                for key in {
                    "maximum_dimensionless_residual",
                    "projected_singular_value_ratio",
                    "full_smallest_singular_value",
                    "determinant_factorization_relative_residual",
                    "maximum_survival_identity_residual",
                }
            )
            or diagnostics["model_diagnostics"] != mesh_diagnostics
            or not validate_model_diagnostics(
                mesh_diagnostics,
                cells,
                manifest,
                budget=cusp["budget"],
                weights=cusp["weights"],
            )
            or not validate_state_law(diagnostics["state_law_diagnostics"], budget=cusp["budget"])
            or not _float_vector(diagnostics["projected_singular_values"], 2)
            or any(value < 0.0 for value in diagnostics["projected_singular_values"])
            or not _float_matrix(diagnostics["dimensionless_jacobian"], 3, 3)
            or not validate_derivative_audit(diagnostics["derivative_audit"], manifest)
            or type(diagnostics["gates"]) is not dict
            or set(diagnostics["gates"]) != CUSP_GATE_NAMES
            or any(type(value) is not bool for value in diagnostics["gates"].values())
            or type(diagnostics["all_gates_passed"]) is not bool
        ):
            return False
        time = cusp["time"]
        jets = np.asarray(cusp["per_budget_time_jets_0_to_4"], dtype=float)
        allocation = np.asarray(cusp["allocation_time_jets"], dtype=float)
        density = jets[0]
        if density <= 0.0:
            return False
        raw = np.asarray(
            (
                (jets[2], allocation[0, 1], allocation[1, 1]),
                (jets[3], allocation[0, 2], allocation[1, 2]),
                (jets[4], allocation[0, 3], allocation[1, 3]),
            )
        )
        row_scale = np.asarray((time / density, time**2 / density, time**3 / density))
        matrix = row_scale[:, None] * raw * np.asarray((time, 1.0, 1.0))[None, :]
        projected = np.linalg.svd(matrix[:2, 1:], compute_uv=False)
        full = np.linalg.svd(matrix, compute_uv=False)
        fourth = float(time**4 * jets[4] / density)
        determinant_left = float(np.linalg.det(matrix))
        determinant_right = float(fourth * np.linalg.det(matrix[:2, 1:]))
        determinant_residual = abs(determinant_left - determinant_right) / max(
            abs(determinant_left), abs(determinant_right), 1.0e-300
        )
        residual = float(
            np.max(
                np.abs(np.asarray((time * jets[1], time**2 * jets[2], time**3 * jets[3])) / density)
            )
        )
        if (
            not np.allclose(matrix, diagnostics["dimensionless_jacobian"], rtol=5e-13, atol=5e-13)
            or not np.allclose(
                projected,
                diagnostics["projected_singular_values"],
                rtol=5e-13,
                atol=5e-13,
            )
            or not close(diagnostics["maximum_dimensionless_residual"], residual)
            or not close(diagnostics["minimum_weight"], min(cusp["weights"]))
            or not close(diagnostics["scaled_fourth_derivative"], fourth)
            or not close(
                diagnostics["projected_singular_value_ratio"],
                projected[-1] / projected[0] if projected[0] > 0.0 else 0.0,
            )
            or not close(diagnostics["full_smallest_singular_value"], full[-1])
            or not close(
                diagnostics["determinant_factorization_relative_residual"],
                determinant_residual,
            )
        ):
            return False
        physical = reconstruct_law_gates(
            mesh_diagnostics, [diagnostics["state_law_diagnostics"]], manifest
        )
        gates_rules = manifest["cusp_gates"]
        gates = {
            "cusp_residual": residual <= gates_rules["maximum_dimensionless_residual"],
            "simplex_margin": diagnostics["minimum_weight"]
            >= gates_rules["minimum_simplex_weight"],
            "quartic_nondegeneracy": abs(fourth)
            >= gates_rules["minimum_absolute_scaled_fourth_derivative"],
            "projected_rank_floor": projected[-1]
            >= gates_rules["minimum_projected_second_singular_value"],
            "projected_rank_ratio": diagnostics["projected_singular_value_ratio"]
            >= gates_rules["minimum_projected_singular_value_ratio"],
            "full_jacobian_rank": full[-1] >= gates_rules["minimum_full_jacobian_singular_value"],
            "determinant_factorization": determinant_residual
            <= gates_rules["maximum_determinant_factorization_relative_residual"],
            "mixed_jet_audit": diagnostics["derivative_audit"]["passed"],
            "survival_identities": diagnostics["maximum_survival_identity_residual"]
            <= gates_rules["maximum_explicit_action_residual"],
            **physical,
        }
        return bool(
            diagnostics["gates"] == gates and diagnostics["all_gates_passed"] is all(gates.values())
        )
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_fold_node(
    node: Any, cells: int, manifest: dict[str, Any], *, comparison: bool = False
) -> bool:
    keys = COMPARISON_NODE_KEYS if comparison else FOLD_NODE_KEYS
    if type(node) is not dict or set(node) != keys:
        return False
    try:
        if (
            type(node["acceptance_index"]) is not int
            or type(node["time"]) is not float
            or not _float_vector(node["theta"], 2)
            or not _float_vector(node["weights"], 4)
            or not point_in_trust_box(node["time"], node["theta"], manifest)
            or any(
                not close(left, right)
                for left, right in zip(
                    node["weights"],
                    weights_from_theta(node["theta"], manifest),
                    strict=True,
                )
            )
            or type(node["normalized_fold_residual"]) is not float
            or node["normalized_fold_residual"] < 0.0
            or type(node["scaled_third_derivative"]) is not float
            or not _float_vector(node["dimensionless_fold_singular_values"], 2)
            or any(value < 0.0 for value in node["dimensionless_fold_singular_values"])
            or not validate_model_diagnostics(
                node["model_diagnostics"],
                cells,
                manifest,
                budget=manifest["budget_homotopy"]["target_budget"],
                weights=node["weights"],
            )
            or not validate_state_law(
                node["state_law_diagnostics"],
                budget=manifest["budget_homotopy"]["target_budget"],
            )
            or type(node["physical_law_gates"]) is not dict
            or set(node["physical_law_gates"]) != LAW_GATE_NAMES
            or node["physical_law_gates"]
            != reconstruct_law_gates(
                node["model_diagnostics"], [node["state_law_diagnostics"]], manifest
            )
        ):
            return False
        return not comparison or (
            all(
                type(node[key]) is float
                for key in {
                    "signed_time_offset",
                    "target_signed_time_offset",
                    "absolute_time_offset_mismatch",
                }
            )
            and node["target_signed_time_offset"] >= 0.0
            and node["absolute_time_offset_mismatch"] >= 0.0
        )
    except (KeyError, TypeError, ValueError):
        return False


LINEAGE_KEYS = {
    "global_root_ordinal",
    "type",
    "side",
    "time",
    "origin_bracket_index",
    "previous_bracket_index",
    "current_bracket_index",
    "predecessor_global_root_ordinal",
    "successor_global_root_ordinal",
    "matched_previous_global_root_ordinal",
    "adjacent_time_drift",
}
REMOTE_KEYS = {
    "remote_pair_present",
    "pair_identity",
    "anchor_pair_identity",
    "pair",
    "root_lineage",
    "lineage_status",
    "lineage_passed",
    "lineage_hold_reasons",
    "maximum_observed_adjacent_drift",
    "candidate_search_bounded_to_frozen_window",
}
REMOTE_PAIR_KEYS = {
    "maximum",
    "minimum",
    "side",
    "pair_type",
    "selected_global_root_indices",
    "origin_bracket_lineage",
    "maximum_global_root_ordinal",
    "minimum_global_root_ordinal",
    "maximum_bracket_index",
    "minimum_bracket_index",
    "eligible_root_count_at_anchor",
}


def reconstruct_remote(remote: Any) -> bool:
    try:
        if type(remote) is not dict or set(remote) != REMOTE_KEYS:
            return False
        lineage = remote["root_lineage"]
        if (
            type(lineage) is not list
            or any(
                type(row) is not dict
                or set(row) != LINEAGE_KEYS
                or type(row["global_root_ordinal"]) is not int
                or row["global_root_ordinal"] != index
                or row["type"] not in {"maximum", "minimum"}
                or row["side"] not in {"negative_time", "positive_time"}
                or type(row["origin_bracket_index"]) is not int
                or type(row["previous_bracket_index"]) is not int
                or type(row["current_bracket_index"]) is not int
                or any(
                    row[key] is not None and type(row[key]) is not int
                    for key in {
                        "predecessor_global_root_ordinal",
                        "successor_global_root_ordinal",
                        "matched_previous_global_root_ordinal",
                    }
                )
                or type(row["adjacent_time_drift"]) is not float
                or row["adjacent_time_drift"] < 0.0
                for index, row in enumerate(lineage)
            )
            or type(remote["lineage_passed"]) is not bool
            or type(remote["remote_pair_present"]) is not bool
            or type(remote["lineage_hold_reasons"]) is not list
            or remote["candidate_search_bounded_to_frozen_window"] is not True
        ):
            return False
        pair = remote["pair"]
        if pair is None:
            return remote["lineage_passed"] is False and remote["remote_pair_present"] is False
        indices = pair["selected_global_root_indices"]
        return bool(
            type(pair) is dict
            and set(pair) == REMOTE_PAIR_KEYS
            and pair["pair_type"] == "maximum_minimum"
            and type(indices) is list
            and len(indices) == 2
            and all(type(item) is int for item in indices)
            and type(pair["origin_bracket_lineage"]) is list
            and all(type(item) is int for item in pair["origin_bracket_lineage"])
            and all(
                type(pair[key]) is int
                for key in {
                    "maximum_global_root_ordinal",
                    "minimum_global_root_ordinal",
                    "maximum_bracket_index",
                    "minimum_bracket_index",
                    "eligible_root_count_at_anchor",
                }
            )
            and indices[1] == indices[0] + 1
            and pair["maximum_global_root_ordinal"] == indices[0]
            and pair["minimum_global_root_ordinal"] == indices[1]
            and pair["maximum"]["type"] == "maximum"
            and pair["minimum"]["type"] == "minimum"
            and remote["lineage_passed"] is remote["remote_pair_present"]
            and remote["pair_identity"] == remote["anchor_pair_identity"]
        )
    except (IndexError, KeyError, TypeError):
        return False


def reconstruct_anchor_remote(
    remote: dict[str, Any], scan: dict[str, Any], cusp_time: float
) -> bool:
    try:
        if not reconstruct_remote(remote) or remote["lineage_status"] != "CUSP_ANCHOR":
            return False
        roots = scan["roots"]
        lineage = remote["root_lineage"]
        if len(roots) != len(lineage):
            return False
        for index, (root, row) in enumerate(zip(roots, lineage, strict=True)):
            side = "positive_time" if root["time"] > cusp_time else "negative_time"
            predecessor = index - 1 if index > 0 else None
            successor = index + 1 if index + 1 < len(roots) else None
            if not (
                row["global_root_ordinal"] == index
                and row["type"] == root["type"]
                and row["side"] == side
                and close(row["time"], root["time"])
                and row["origin_bracket_index"] == root["bracket_index"]
                and row["previous_bracket_index"] == root["bracket_index"]
                and row["current_bracket_index"] == root["bracket_index"]
                and row["predecessor_global_root_ordinal"] == predecessor
                and row["successor_global_root_ordinal"] == successor
                and row["matched_previous_global_root_ordinal"] == index
                and close(row["adjacent_time_drift"], 0.0)
            ):
                return False
        pair = remote["pair"]
        left_index, right_index = pair["selected_global_root_indices"]
        origin = [roots[left_index]["bracket_index"], roots[right_index]["bracket_index"]]
        expected_identity = (
            f"{pair['side']}:maximum_minimum:global_{left_index}_{right_index}:"
            f"origin_brackets_{origin[0]}_{origin[1]}"
        )
        return bool(
            remote["pair_identity"] == expected_identity
            and remote["anchor_pair_identity"] == expected_identity
            and remote["lineage_passed"] is True
            and remote["remote_pair_present"] is True
            and remote["lineage_hold_reasons"] == []
            and remote["maximum_observed_adjacent_drift"] == 0.0
            and pair["origin_bracket_lineage"] == origin
            and pair["eligible_root_count_at_anchor"] == len(roots)
            and pair["maximum"] == roots[left_index]
            and pair["minimum"] == roots[right_index]
            and pair["maximum_bracket_index"] == roots[left_index]["bracket_index"]
            and pair["minimum_bracket_index"] == roots[right_index]["bracket_index"]
        )
    except (IndexError, KeyError, TypeError):
        return False


def expected_comparison_remote(
    scan: dict[str, Any],
    cusp_time: float,
    anchor: dict[str, Any],
    previous: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    roots = list(scan["roots"])
    anchor_lineage = anchor.get("root_lineage")
    previous_lineage = previous.get("root_lineage")
    reasons: list[str] = []
    if type(anchor_lineage) is not list or type(previous_lineage) is not list:
        reasons.append("unmatched_lineage")
        anchor_lineage = []
        previous_lineage = []
    if len(roots) != len(anchor_lineage) or len(roots) != len(previous_lineage):
        reasons.append("eligible_root_birth_or_death")
    lineage = []
    maximum_drift = 0.0
    for index, root in enumerate(roots):
        if index >= len(anchor_lineage) or index >= len(previous_lineage):
            reasons.append("unmatched_root")
            break
        origin = anchor_lineage[index]
        predecessor = previous_lineage[index]
        time = float(root["time"])
        side = "positive_time" if time > cusp_time else "negative_time"
        drift = abs(time - float(predecessor["time"]))
        maximum_drift = max(maximum_drift, drift)
        expected_predecessor = index - 1 if index > 0 else None
        expected_successor = index + 1 if index + 1 < len(roots) else None
        if (
            origin.get("global_root_ordinal") != index
            or predecessor.get("global_root_ordinal") != index
            or root.get("type") != origin.get("type")
            or root.get("type") != predecessor.get("type")
            or side != origin.get("side")
            or predecessor.get("predecessor_global_root_ordinal") != expected_predecessor
            or predecessor.get("successor_global_root_ordinal") != expected_successor
        ):
            reasons.append("root_crossing_type_side_or_order_change")
        if drift > manifest["remote_pair"]["maximum_adjacent_root_time_drift"]:
            reasons.append("excess_adjacent_root_time_drift")
        lineage.append(
            {
                "global_root_ordinal": index,
                "type": root["type"],
                "side": side,
                "time": time,
                "origin_bracket_index": int(origin["origin_bracket_index"]),
                "previous_bracket_index": int(predecessor["current_bracket_index"]),
                "current_bracket_index": int(root["bracket_index"]),
                "predecessor_global_root_ordinal": expected_predecessor,
                "successor_global_root_ordinal": expected_successor,
                "matched_previous_global_root_ordinal": index,
                "adjacent_time_drift": float(drift),
            }
        )
    pair = None
    pair_identity = None
    anchor_pair = anchor.get("pair")
    selected = (
        anchor_pair.get("selected_global_root_indices") if type(anchor_pair) is dict else None
    )
    if (
        type(selected) is not list
        or len(selected) != 2
        or not all(type(value) is int for value in selected)
        or selected[1] != selected[0] + 1
        or selected[0] < 0
        or selected[1] >= len(roots)
    ):
        reasons.append("unmatched_anchor_pair")
    else:
        left_index, right_index = selected
        left = roots[left_index]
        right = roots[right_index]
        left_time = float(left["time"])
        right_time = float(right["time"])
        side = "positive_time" if left_time > cusp_time else "negative_time"
        pair_valid = bool(
            left["type"] == "maximum"
            and right["type"] == "minimum"
            and side == anchor_pair["side"]
            and (left_time - cusp_time) * (right_time - cusp_time) > 0.0
            and abs(left_time - cusp_time) > manifest["remote_pair"]["cusp_exclusion_radius"]
            and abs(right_time - cusp_time) > manifest["remote_pair"]["cusp_exclusion_radius"]
            and right_time - left_time >= manifest["remote_pair"]["minimum_root_separation"]
        )
        if not pair_valid:
            reasons.append("selected_pair_type_side_or_separation_changed")
        else:
            pair_identity = anchor.get("pair_identity")
            pair = {
                "maximum": left,
                "minimum": right,
                "side": side,
                "pair_type": "maximum_minimum",
                "selected_global_root_indices": [left_index, right_index],
                "origin_bracket_lineage": list(anchor_pair["origin_bracket_lineage"]),
                "maximum_global_root_ordinal": left_index,
                "minimum_global_root_ordinal": right_index,
                "maximum_bracket_index": int(left["bracket_index"]),
                "minimum_bracket_index": int(right["bracket_index"]),
                "eligible_root_count_at_anchor": int(anchor_pair["eligible_root_count_at_anchor"]),
            }
    reasons = list(dict.fromkeys(reasons))
    passed = not reasons and pair is not None and len(lineage) == len(roots)
    return {
        "remote_pair_present": passed,
        "pair_identity": pair_identity,
        "anchor_pair_identity": anchor.get("pair_identity"),
        "pair": pair,
        "root_lineage": lineage,
        "lineage_status": "MATCHED_COMPARISON" if passed else "HOLD_LINEAGE",
        "lineage_passed": passed,
        "lineage_hold_reasons": reasons,
        "maximum_observed_adjacent_drift": float(maximum_drift),
        "candidate_search_bounded_to_frozen_window": True,
    }


def reconstruct_branch(
    branch: dict[str, Any],
    sign: int,
    manifest: dict[str, Any],
    anchor: dict[str, Any],
    cusp_time: float,
    cells: int,
) -> bool:
    try:
        rules = manifest["fold_continuation"]
        if (
            type(branch) is not dict
            or set(branch)
            != {
                "status",
                "orientation",
                "nodes",
                "comparison_nodes",
                "comparison_node_remote_pairs",
                "gates",
            }
            or branch["orientation"] != ("positive_time" if sign > 0 else "negative_time")
            or type(branch["gates"]) is not dict
            or set(branch["gates"]) != BRANCH_GATE_NAMES
            or any(type(value) is not bool for value in branch["gates"].values())
            or not reconstruct_remote(anchor)
            or type(branch["nodes"]) is not list
        ):
            return False
        nodes = branch["nodes"]
        if any(
            not validate_fold_node(node, cells, manifest) or node["acceptance_index"] != index
            for index, node in enumerate(nodes)
        ):
            return False
        comparisons = branch["comparison_nodes"]
        remote_rows = branch["comparison_node_remote_pairs"]
        if comparisons is None or remote_rows is None:
            if comparisons is not None or remote_rows is not None:
                return False
            comparisons = []
            remote_rows = []
        elif type(comparisons) is not list or type(remote_rows) is not list:
            return False
        desired_sign = 1.0 if sign > 0 else -1.0
        expected_comparisons = []
        used: set[int] = set()
        for target in rules["comparison_time_offsets"]:
            eligible = [
                node
                for node in nodes
                if desired_sign * (node["time"] - cusp_time) > 0.0
                and node["acceptance_index"] not in used
            ]
            if not eligible:
                expected_comparisons = []
                break
            chosen = min(
                eligible,
                key=lambda node: (
                    abs(desired_sign * (node["time"] - cusp_time) - target),
                    node["normalized_fold_residual"],
                    node["acceptance_index"],
                ),
            )
            expected = dict(chosen)
            expected["signed_time_offset"] = float(desired_sign * (chosen["time"] - cusp_time))
            expected["target_signed_time_offset"] = float(target)
            expected["absolute_time_offset_mismatch"] = float(
                abs(expected["signed_time_offset"] - target)
            )
            expected_comparisons.append(expected)
            used.add(chosen["acceptance_index"])
        if comparisons != expected_comparisons or len(remote_rows) != len(comparisons):
            return False
        previous = anchor
        identities = []
        comparison_scan_valid = len(remote_rows) == 3
        lineage_valid = len(remote_rows) == 3 and anchor["lineage_passed"] is True
        for comparison, remote_row in zip(comparisons, remote_rows, strict=True):
            if (
                not validate_fold_node(comparison, cells, manifest, comparison=True)
                or type(remote_row) is not dict
                or set(remote_row) != {"acceptance_index", "time", "remote_pair", "stationary_scan"}
                or remote_row["acceptance_index"] != comparison["acceptance_index"]
                or remote_row["time"] != comparison["time"]
            ):
                return False
            current = remote_row["remote_pair"]
            if remote_row["stationary_scan"] is None:
                if not (
                    reconstruct_remote(current)
                    and current["remote_pair_present"] is False
                    and current["pair_identity"] is None
                    and current["anchor_pair_identity"] == anchor["pair_identity"]
                    and current["pair"] is None
                    and current["root_lineage"] == []
                    and current["lineage_status"] == "HOLD_LINEAGE"
                    and current["lineage_passed"] is False
                    and current["lineage_hold_reasons"]
                    and current["maximum_observed_adjacent_drift"] == 0.0
                ):
                    return False
                comparison_scan_valid = False
                lineage_valid = False
            else:
                if not reconstruct_scan(
                    remote_row["stationary_scan"], comparison["model_diagnostics"], manifest
                ):
                    return False
                expected_remote = expected_comparison_remote(
                    remote_row["stationary_scan"],
                    comparison["time"],
                    anchor,
                    previous,
                    manifest,
                )
                if current != expected_remote:
                    return False
                comparison_scan_valid = comparison_scan_valid and all(
                    remote_row["stationary_scan"]["physical_law_gates"].values()
                )
                lineage_valid = lineage_valid and current["lineage_passed"]
                previous = current
            identities.append(current["pair_identity"])
        signed_reach = max(
            (desired_sign * (node["time"] - cusp_time) for node in nodes),
            default=-math.inf,
        )
        gates = {
            "minimum_nodes": len(nodes) >= rules["minimum_accepted_noncusp_nodes"],
            "required_reach": signed_reach >= rules["required_absolute_time_reach"],
            "comparison_nodes_present": len(comparisons) == 3,
            "comparison_nodes_distinct": len({row["acceptance_index"] for row in comparisons}) == 3,
            "comparison_nodes_on_signed_side": len(comparisons) == 3
            and all(row["signed_time_offset"] > 0.0 for row in comparisons),
            "comparison_offset_mismatch": len(comparisons) == 3
            and all(
                row["absolute_time_offset_mismatch"]
                <= rules["maximum_comparison_time_offset_mismatch"]
                for row in comparisons
            ),
            "fold_residuals": bool(nodes)
            and max(row["normalized_fold_residual"] for row in nodes)
            <= rules["maximum_normalized_fold_residual"],
            "third_derivative": bool(nodes)
            and all(
                row["scaled_third_derivative"] >= rules["minimum_scaled_third_derivative"]
                for row in nodes
                if abs(row["time"] - cusp_time) >= 0.25
            ),
            "fold_rank": bool(nodes)
            and all(
                row["dimensionless_fold_singular_values"][-1]
                >= rules["minimum_dimensionless_fold_singular_value"]
                for row in nodes
            ),
            "physical_law": bool(nodes)
            and all(all(row["physical_law_gates"].values()) for row in nodes),
            "comparison_scan_physical_law": comparison_scan_valid,
            "remote_pair_retained": len(remote_rows) == 3
            and all(row["remote_pair"]["remote_pair_present"] for row in remote_rows),
            "stable_remote_pair_identity": len(identities) == 3
            and identities[0] is not None
            and len(set(identities)) == 1
            and identities[0] == anchor["pair_identity"],
            "remote_pair_lineage": lineage_valid,
        }
        return bool(
            branch["gates"] == gates
            and branch["status"]
            == ("PASS_BRANCH_DISCOVERY" if all(gates.values()) else "HOLD_BRANCH")
        )
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def reconstruct_phase(
    phase: Any,
    manifest: dict[str, Any],
    expected_cusp_theta: list[float] | None,
) -> tuple[bool, bool]:
    if phase is None:
        return True, False
    phase_keys = {
        "phase_centre_theta",
        "candidate_generation",
        "screened_mesh_65",
        "advanced_mesh_97",
        "representatives",
        "all_three_regions_found",
        "phase_complete",
        "hold_reasons",
        "search_expanded",
    }
    candidate_keys = {
        "candidate_index",
        "radius",
        "direction",
        "theta",
        "weights",
        "eligible_geometry",
    }
    screened_keys = candidate_keys | {"mesh_65", "mesh_65_evaluation_status"}
    advanced_keys = screened_keys | {
        "mesh_97",
        "mesh_97_evaluation_status",
        "worst_score",
        "both_meshes_pass",
    }
    try:
        if type(phase) is not dict or set(phase) != phase_keys:
            return False, False
        generated = phase["candidate_generation"]
        screened = phase["screened_mesh_65"]
        advanced = phase["advanced_mesh_97"]
        search = manifest["phase_search"]
        if (
            not _float_vector(phase["phase_centre_theta"], 2)
            or not _float_vector(expected_cusp_theta, 2)
            or any(
                abs(left - right) > search["centre_formula_absolute_tolerance"]
                for left, right in zip(
                    phase["phase_centre_theta"], expected_cusp_theta, strict=True
                )
            )
            or type(generated) is not list
            or len(generated) != search["candidate_count"]
            or type(screened) is not list
            or len(screened) != len(generated)
            or type(advanced) is not list
            or type(phase["representatives"]) is not dict
            or set(phase["representatives"]) != {"1", "2", "3"}
            or type(phase["hold_reasons"]) is not list
            or not all(type(item) is str for item in phase["hold_reasons"])
            or phase["search_expanded"] is not False
        ):
            return False, False
        reference = manifest["allocation_chart"]["reference_weights"]
        basis = manifest["allocation_chart"]["P"]
        centre = phase["phase_centre_theta"]
        for index, candidate in enumerate(generated):
            if type(candidate) is not dict or set(candidate) != candidate_keys:
                return False, False
            radius = search["radii"][index // len(search["directions"])]
            direction = search["directions"][index % len(search["directions"])]
            if (
                type(candidate["candidate_index"]) is not int
                or candidate["candidate_index"] != index
                or type(candidate["radius"]) is not float
                or candidate["radius"] != radius
                or not _float_vector(candidate["direction"], 2)
                or candidate["direction"] != direction
                or not _float_vector(candidate["theta"], 2)
                or not _float_vector(candidate["weights"], 4)
                or type(candidate["eligible_geometry"]) is not bool
            ):
                return False, False
            expected_theta = [
                centre[coordinate] + radius * direction[coordinate] for coordinate in range(2)
            ]
            if any(
                abs(left - right) > search["centre_formula_absolute_tolerance"]
                for left, right in zip(candidate["theta"], expected_theta, strict=True)
            ):
                return False, False
            weights = [
                reference[row]
                + sum(basis[row][column] * candidate["theta"][column] for column in range(2))
                for row in range(4)
            ]
            if any(
                not close(left, right)
                for left, right in zip(candidate["weights"], weights, strict=True)
            ):
                return False, False
            expected_geometry = bool(
                manifest["solver"]["time_trust_box"][0]
                <= manifest["allocation_chart"]["reference_cusp_time"]
                <= manifest["solver"]["time_trust_box"][1]
                and max(abs(value) for value in candidate["theta"])
                <= manifest["solver"]["maximum_theta_linf"]
                and min(candidate["weights"]) >= manifest["solver"]["minimum_simplex_weight"]
            )
            if candidate["eligible_geometry"] is not expected_geometry:
                return False, False
        for candidate, row in zip(generated, screened, strict=True):
            if type(row) is not dict or set(row) != screened_keys:
                return False, False
            if {key: row[key] for key in candidate_keys} != candidate:
                return False, False
            status = row["mesh_65_evaluation_status"]
            if status == "EVALUATED":
                if not reconstruct_control(row["mesh_65"], manifest):
                    return False, False
            elif status == "NOT_ELIGIBLE_GEOMETRY":
                if row["eligible_geometry"] or row["mesh_65"] is not None:
                    return False, False
            elif status == "HOLD_CONTROL_EVALUATION":
                if row["mesh_65"] is not None and not reconstruct_control(row["mesh_65"], manifest):
                    return False, False
            else:
                return False, False
        missing_65_indices = [
            row["candidate_index"]
            for row in screened
            if row["eligible_geometry"] and row["mesh_65_evaluation_status"] != "EVALUATED"
        ]
        if missing_65_indices:
            valid = bool(
                advanced == []
                and phase["representatives"] == {"1": None, "2": None, "3": None}
                and phase["all_three_regions_found"] is False
                and phase["phase_complete"] is False
                and phase["hold_reasons"]
                == [f"missing_eligible_mesh_65_evaluations:{missing_65_indices}"]
            )
            return valid, False
        expected_bases: list[dict[str, Any]] = []
        for target in search["target_retained_maximum_counts"]:
            eligible = [
                row
                for row in screened
                if row["mesh_65_evaluation_status"] == "EVALUATED"
                and row["mesh_65"] is not None
                and row["mesh_65"]["retained_maximum_count"] == target
                and row["mesh_65"]["gates"]["alternating_topology"]
                and row["mesh_65"]["gates"]["endpoint_signs"]
                and row["mesh_65"]["gates"]["root_residual"]
                and row["mesh_65"]["robustness_score"] is not None
            ]
            eligible.sort(
                key=lambda row: (-row["mesh_65"]["robustness_score"], tuple(row["weights"]))
            )
            expected_bases.extend(eligible[: search["maximum_advanced_per_mode_count"]])
        if len(advanced) != len(expected_bases):
            return False, False
        for base, row in zip(expected_bases, advanced, strict=True):
            if type(row) is not dict or set(row) != advanced_keys:
                return False, False
            if {key: row[key] for key in screened_keys} != base:
                return False, False
            if row["mesh_97_evaluation_status"] == "EVALUATED":
                if not reconstruct_control(row["mesh_97"], manifest):
                    return False, False
                worst = min(row["mesh_65"]["robustness_score"], row["mesh_97"]["robustness_score"])
                target = row["mesh_65"]["retained_maximum_count"]
                both = bool(
                    row["mesh_65"]["all_gates_passed"]
                    and row["mesh_97"]["all_gates_passed"]
                    and row["mesh_97"]["retained_maximum_count"] == target
                )
                if not close(row["worst_score"], worst) or row["both_meshes_pass"] is not both:
                    return False, False
            elif row["mesh_97_evaluation_status"] == "HOLD_CONTROL_EVALUATION":
                if row["worst_score"] is not None or row["both_meshes_pass"] is not False:
                    return False, False
            else:
                return False, False
        missing = any(
            row["eligible_geometry"] and row["mesh_65_evaluation_status"] != "EVALUATED"
            for row in screened
        ) or any(row["mesh_97_evaluation_status"] != "EVALUATED" for row in advanced)
        complete = not missing
        expected_hold_reasons = [
            f"missing_selected_mesh_97_evaluation:{row['candidate_index']}"
            for row in advanced
            if row["mesh_97_evaluation_status"] != "EVALUATED"
        ]
        representatives: dict[str, Any] = {}
        for target in (1, 2, 3):
            passing = [
                row
                for row in advanced
                if row["mesh_65"]["retained_maximum_count"] == target
                and row["both_meshes_pass"] is True
            ]
            passing.sort(key=lambda row: (-row["worst_score"], tuple(row["weights"])))
            representatives[str(target)] = passing[0] if passing else None
        if not complete:
            representatives = {"1": None, "2": None, "3": None}
        found = bool(
            complete and all(representatives[str(target)] is not None for target in (1, 2, 3))
        )
        valid = bool(
            phase["phase_complete"] is complete
            and phase["representatives"] == representatives
            and phase["all_three_regions_found"] is found
            and phase["hold_reasons"] == expected_hold_reasons
        )
        return valid, bool(valid and found)
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False, False


def audit_payload(
    manifest: dict[str, Any],
    result: dict[str, Any],
    evidence: dict[str, Any],
    result_bytes: bytes,
    evidence_bytes: bytes | None = None,
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)
        if not condition:
            errors.append(name)

    try:
        require_finite_json(manifest)
        require_finite_json(result)
        require_finite_json(evidence)
    except (TypeError, ValueError):
        check("finite_native_json", False)
    else:
        check("finite_native_json", True)
    check("canonical_result_bytes", canonical_json_bytes(result) == result_bytes)
    if evidence_bytes is None:
        evidence_bytes = canonical_json_bytes(evidence)
    check("canonical_evidence_bytes", canonical_json_bytes(evidence) == evidence_bytes)
    check(
        "manifest_schema_stage",
        type(manifest.get("schema_version")) is int
        and manifest.get("schema_version") == SCHEMA_VERSION
        and manifest.get("stage") == STAGE
        and sha256(MANIFEST) == EXPECTED_MANIFEST_SHA256,
    )
    try:
        runtime_provenance_valid = exact_json_contract(
            manifest.get("runtime_provenance"), current_runtime_provenance()
        )
    except (KeyError, OSError, RuntimeError, ValueError):
        runtime_provenance_valid = False
    check("manifest_runtime_provenance_rebuilt", runtime_provenance_valid)
    check("result_exact_top_level", type(result) is dict and set(result) == RESULT_KEYS)
    check(
        "result_schema_stage_manifest",
        type(result.get("schema_version")) is int
        and result.get("schema_version") == SCHEMA_VERSION
        and result.get("stage") == STAGE
        and result.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
    )
    check(
        "scope_evidence_timing_limitations_exact",
        result.get("claim_scope") == manifest.get("claim_scope")
        and result.get("evidence_timing") == EXPECTED_EVIDENCE_TIMING
        and result.get("limitations") == EXPECTED_LIMITATIONS,
    )
    pins = manifest.get("pinned_files")
    pinned_hashes = (
        {role: row["sha256"] for role, row in pins.items()}
        if type(pins) is dict
        and all(type(row) is dict and "sha256" in row for row in pins.values())
        else {}
    )
    observed_pins: dict[str, str] = {}
    pins_valid = bool(pins)
    if type(pins) is dict:
        for role, row in pins.items():
            try:
                raw = Path(row["path"])
                current = REPORT
                chain_valid = not raw.is_absolute() and ".." not in raw.parts
                for index, part in enumerate(raw.parts):
                    current = current / part
                    lexical = os.lstat(current)
                    chain_valid = bool(
                        chain_valid
                        and not stat.S_ISLNK(lexical.st_mode)
                        and (
                            stat.S_ISREG(lexical.st_mode)
                            if index == len(raw.parts) - 1
                            else stat.S_ISDIR(lexical.st_mode)
                        )
                    )
                path = current
                valid = (
                    chain_valid
                    and not stat.S_ISLNK(lexical.st_mode)
                    and stat.S_ISREG(lexical.st_mode)
                    and type(row["sha256"]) is str
                    and len(row["sha256"]) == 64
                )
                payload, _metadata = stable_regular_file_bytes(path)
                observed_pins[role] = sha256_bytes(payload)
                pins_valid = pins_valid and valid and observed_pins[role] == row["sha256"]
            except (KeyError, OSError, ValueError):
                pins_valid = False
    check("manifest_pins_rehashed", pins_valid and observed_pins == pinned_hashes)
    snapshots = result.get("pin_snapshots")
    check(
        "result_pin_snapshots",
        type(snapshots) is dict
        and set(snapshots) == {"before_formal", "after_formal"}
        and snapshots.get("before_formal") == pinned_hashes
        and snapshots.get("after_formal") == pinned_hashes
        and result.get("pinned_file_hashes") == pinned_hashes,
    )
    lexical_snapshots = result.get("lexical_pin_snapshots")
    lexical_valid = bool(
        type(lexical_snapshots) is dict
        and set(lexical_snapshots) == {"before_formal", "after_formal"}
        and lexical_snapshots.get("before_formal") == lexical_snapshots.get("after_formal")
    )
    if lexical_valid:
        expected_roles = {"manifest", *pinned_hashes}
        metadata_keys = {
            "path",
            "st_dev",
            "st_ino",
            "st_mode",
            "st_nlink",
            "st_uid",
            "st_gid",
            "st_size",
            "st_mtime_ns",
            "sha256",
        }
        before = lexical_snapshots["before_formal"]
        lexical_valid = bool(type(before) is dict and set(before) == expected_roles)
        if lexical_valid:
            for role, row in before.items():
                lexical_valid = bool(
                    lexical_valid
                    and type(row) is dict
                    and set(row) == metadata_keys
                    and type(row["path"]) is str
                    and type(row["sha256"]) is str
                    and all(type(row[key]) is int for key in metadata_keys - {"path", "sha256"})
                    and (
                        (role == "manifest" and row["sha256"] == EXPECTED_MANIFEST_SHA256)
                        or (role != "manifest" and row["sha256"] == pinned_hashes[role])
                    )
                )
    check("result_lexical_metadata_snapshots", lexical_valid)
    flags = result.get("required_claim_flags")
    passed = result.get("all_discovery_gates_passed")
    check(
        "negative_claim_flags",
        type(flags) is dict
        and set(flags) == set(manifest.get("required_claim_flags", {}))
        and all(
            value is False for key, value in flags.items() if key != "low_mesh_discovery_completed"
        )
        and flags.get("low_mesh_discovery_completed") is passed,
    )
    check(
        "forbidden_claims_exact", result.get("forbidden_claims") == manifest.get("forbidden_claims")
    )

    preflight = result.get("small_explicit_csr_preflight")
    try:
        preflight_valid = (
            type(preflight) is dict
            and set(preflight) == {"mesh", "state_count", "errors", "maximum_error", "passed"}
            and type(preflight.get("mesh")) is list
            and len(preflight["mesh"]) == 3
            and all(type(item) is int and item == 7 for item in preflight["mesh"])
            and type(preflight.get("state_count")) is int
            and preflight.get("state_count") == 343
            and type(preflight.get("errors")) is dict
            and set(preflight["errors"])
            == {"column_action", "row_action", "augmented_column_action", "augmented_row_action"}
            and all(type(value) is float and value >= 0.0 for value in preflight["errors"].values())
            and type(preflight.get("maximum_error")) is float
            and preflight.get("maximum_error") == max(preflight["errors"].values())
            and type(preflight.get("passed")) is bool
            and preflight.get("passed")
            == (preflight.get("maximum_error") <= manifest["preflight"]["maximum_action_residual"])
        )
    except (KeyError, TypeError, ValueError):
        preflight_valid = False
    check("preflight_reconstructed", preflight_valid)
    rows = result.get("discovery_mesh_rows")
    mesh_rows_valid = type(rows) is list and len(rows) == 2
    if mesh_rows_valid:
        for cells, row in zip(DISCOVERY_MESHES, rows, strict=True):
            row_valid = bool(
                type(row) is dict
                and set(row) == MESH_ROW_KEYS
                and type(row.get("mesh")) is list
                and len(row["mesh"]) == 3
                and all(type(item) is int and item == cells for item in row["mesh"])
            )
            if row_valid and row.get("status") in {
                "NOT_RUN_AFTER_HOLD",
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            }:
                row_valid = bool(
                    type(row.get("reason")) is str
                    and row.get("reason")
                    == (
                        "explicit_csr_preflight_held_before_scientific_construction"
                        if row.get("status") == "NOT_RUN_AFTER_PREFLIGHT_HOLD"
                        else "earlier_discovery_mesh_held"
                    )
                    and row.get("all_mesh_discovery_gates_passed") is False
                    and all(
                        row[key] is None
                        for key in (
                            "model_diagnostics",
                            "homotopy",
                            "cusp",
                            "cusp_diagnostics",
                            "stationary_scan",
                            "remote_pair",
                            "branches",
                        )
                    )
                )
            elif row_valid:
                row_valid = validate_homotopy(row.get("homotopy"), row.get("cusp"), manifest)
                if row_valid and row["homotopy"]["status"] == HOLD_STATUS:
                    row_valid = bool(
                        row["status"] == HOLD_STATUS
                        and row["reason"] == "homotopy_failed"
                        and row["model_diagnostics"] is None
                        and row["cusp"] is None
                        and row["cusp_diagnostics"] is None
                        and row["stationary_scan"] is None
                        and row["remote_pair"] is None
                        and row["branches"] is None
                        and row["all_mesh_discovery_gates_passed"] is False
                    )
                elif row_valid and row["cusp_diagnostics"] is None:
                    row_valid = bool(
                        row["status"] == HOLD_STATUS
                        and row["reason"] == "post_homotopy_numerical_evaluation_failed"
                        and row["model_diagnostics"] is None
                        and validate_snapshot(row["cusp"], manifest, include_state_law=False)
                        and row["stationary_scan"] is None
                        and row["remote_pair"] is None
                        and row["branches"] is None
                        and row["all_mesh_discovery_gates_passed"] is False
                    )
                elif row_valid:
                    row_valid = bool(
                        validate_model_diagnostics(row["model_diagnostics"], cells, manifest)
                        and validate_snapshot(row["cusp"], manifest, include_state_law=True)
                        and row["cusp"]["state_law_diagnostics"]
                        == row["cusp_diagnostics"]["state_law_diagnostics"]
                        and reconstruct_cusp_diagnostics(
                            row["cusp_diagnostics"],
                            row["cusp"],
                            row["model_diagnostics"],
                            cells,
                            manifest,
                        )
                        and reconstruct_scan(
                            row["stationary_scan"], row["model_diagnostics"], manifest
                        )
                        and reconstruct_anchor_remote(
                            row["remote_pair"],
                            row["stationary_scan"],
                            row["cusp"]["time"],
                        )
                        and type(row["branches"]) is dict
                        and set(row["branches"]) == {"negative", "positive"}
                        and reconstruct_branch(
                            row["branches"]["negative"],
                            -1,
                            manifest,
                            row["remote_pair"],
                            row["cusp"]["time"],
                            cells,
                        )
                        and reconstruct_branch(
                            row["branches"]["positive"],
                            1,
                            manifest,
                            row["remote_pair"],
                            row["cusp"]["time"],
                            cells,
                        )
                    )
                    if row_valid:
                        reconstructed_mesh_pass = bool(
                            row["cusp_diagnostics"]["all_gates_passed"]
                            and all(row["stationary_scan"]["physical_law_gates"].values())
                            and row["remote_pair"]["remote_pair_present"]
                            and all(
                                branch["status"] == "PASS_BRANCH_DISCOVERY"
                                for branch in row["branches"].values()
                            )
                        )
                        row_valid = bool(
                            row["all_mesh_discovery_gates_passed"] is reconstructed_mesh_pass
                            and row["status"]
                            == ("PASS_MESH_DISCOVERY" if reconstructed_mesh_pass else HOLD_STATUS)
                            and row["reason"]
                            == (
                                "all_mesh_gates_passed"
                                if reconstructed_mesh_pass
                                else "mesh_gate_failed"
                            )
                        )
            mesh_rows_valid = mesh_rows_valid and row_valid
        if mesh_rows_valid and preflight_valid and preflight["passed"] is False:
            mesh_rows_valid = mesh_rows_valid and [row["status"] for row in rows] == [
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            ]
        if mesh_rows_valid and rows[0]["all_mesh_discovery_gates_passed"] is False:
            mesh_rows_valid = mesh_rows_valid and rows[1]["status"] in {
                "NOT_RUN_AFTER_HOLD",
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            }
    check("mesh_rows_and_branch_implications", mesh_rows_valid)

    phase = result.get("bounded_phase_discovery")
    expected_phase_centre = None
    if (
        type(rows) is list
        and len(rows) == 2
        and type(rows[1]) is dict
        and type(rows[1].get("cusp")) is dict
    ):
        expected_phase_centre = rows[1]["cusp"].get("theta")
    phase_valid, phase_pass = reconstruct_phase(phase, manifest, expected_phase_centre)
    check("phase_and_control_algebra", phase_valid)
    reconstructed_pass = bool(
        preflight_valid
        and preflight["passed"]
        and mesh_rows_valid
        and type(rows) is list
        and len(rows) == 2
        and all(row["all_mesh_discovery_gates_passed"] for row in rows)
        and phase_pass
    )
    check(
        "overall_status_reconstructed",
        type(passed) is bool
        and passed == reconstructed_pass
        and result.get("status") == (PASS_STATUS if passed else HOLD_STATUS),
    )

    result_hash = sha256_bytes(result_bytes)
    evidence_keys = {
        "schema_version",
        "stage",
        "manifest_sha256",
        "independent_process_count",
        "execution_order",
        "five_path_absence_before_replicas",
        "promotion_staging_absence_before_replicas",
        "per_replica_launch_boundaries",
        "replica_exit_codes",
        "replica_result_sha256",
        "byte_identical",
        "canonical_result_sha256",
        "result_status",
        "all_discovery_gates_passed",
        "pin_snapshot_before_replicas",
        "pin_snapshot_after_replicas",
        "lexical_snapshot_before_replicas",
        "lexical_snapshot_after_replicas",
    }
    expected_code = 0 if passed else 2
    check(
        "two_process_evidence",
        set(evidence) == evidence_keys
        and type(evidence.get("schema_version")) is int
        and evidence.get("schema_version") == 1
        and evidence.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256
        and type(evidence.get("independent_process_count")) is int
        and evidence.get("independent_process_count") == 2
        and evidence.get("execution_order") == "sequential"
        and evidence.get("five_path_absence_before_replicas") == EXPECTED_FIVE_PATH_ABSENCE
        and evidence.get("promotion_staging_absence_before_replicas")
        == EXPECTED_PROMOTION_STAGING_ABSENCE
        and evidence.get("per_replica_launch_boundaries")
        == [
            {
                "replica_index": 1,
                "allowed_present_science_paths": [],
                "promotion_staging_paths_absent": True,
            },
            {
                "replica_index": 2,
                "allowed_present_science_paths": [EXPECTED_FIVE_PATH_ABSENCE[2]],
                "promotion_staging_paths_absent": True,
            },
        ]
        and type(evidence.get("replica_exit_codes")) is list
        and all(type(item) is int for item in evidence["replica_exit_codes"])
        and evidence.get("replica_exit_codes") == [expected_code, expected_code]
        and evidence.get("replica_result_sha256") == [result_hash, result_hash]
        and evidence.get("byte_identical") is True
        and evidence.get("canonical_result_sha256") == result_hash
        and evidence.get("result_status") == result.get("status")
        and evidence.get("all_discovery_gates_passed") is passed
        and evidence.get("pin_snapshot_before_replicas") == pinned_hashes
        and evidence.get("pin_snapshot_after_replicas") == pinned_hashes
        and evidence.get("lexical_snapshot_before_replicas")
        == evidence.get("lexical_snapshot_after_replicas")
        and type(lexical_snapshots) is dict
        and evidence.get("lexical_snapshot_before_replicas")
        == lexical_snapshots.get("before_formal")
        and type(evidence.get("lexical_snapshot_before_replicas")) is dict,
    )
    integrity = bool(checks and all(checks.values()))
    return {
        "schema_version": 1,
        "stage": "allocation_cusp_v6_independent_postresult_audit",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "canonical_result_sha256": result_hash,
        "scientific_result_status": result.get("status"),
        "scientific_result_passed": passed is True,
        "audit_integrity_passed": integrity,
        "release_status": (
            "PASS_AUDIT_DISCOVERY_LOW_MESH_ONLY"
            if integrity and passed is True
            else ("HOLD_SCIENCE_AUDIT_VALID" if integrity else "HOLD_AUDIT")
        ),
        "checks": checks,
        "failed_checks": errors,
        "algebraically_reconstructed": [
            "complete pin and two-process evidence chain",
            "preflight, mesh, phase, and negative-claim implications",
            "control score formulas and reported physical-law gates",
            "all 691 scan rows, the exact 70-row projection, aggregates, and sign brackets",
            "signed branch reach, comparison uniqueness, mismatch, and pair identity",
        ],
        "producer_reported_not_recomputed": [
            "matrix exponential state trajectories",
            "absence of even-multiplicity roots inside one 0.05 scan interval",
            "cusp and fold Newton solves",
            "finite-volume generator construction",
        ],
        "limitations": [
            "no semigroup recomputation",
            "no independent cusp solver",
            "no held-out, parity, box, continuum, or publication claim",
        ],
    }


def _path_inode(path: Path) -> tuple[int, int] | None:
    try:
        item = os.lstat(path)
    except FileNotFoundError:
        return None
    return int(item.st_dev), int(item.st_ino)


def _unlink_owned_path(path: Path, ownership: tuple[int, int] | None) -> bool:
    """Remove only the exact inode created by this invocation."""

    if ownership is None or _path_inode(path) != ownership:
        return False
    path.unlink()
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return True


def write_append_only(path: Path, payload: bytes) -> tuple[int, int]:
    if lexical_path_exists(path):
        raise RuntimeError("independent audit output is append-only")
    stage = path.with_name(f".{path.name}.staging")
    if lexical_path_exists(stage):
        raise RuntimeError("independent audit staging path already exists")
    output_ownership: tuple[int, int] | None = None
    stage_ownership: tuple[int, int] | None = None
    try:
        descriptor = os.open(
            stage,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        stage_ownership = _path_inode(stage)
        if stage_ownership is None:
            raise RuntimeError("independent audit did not own its staging inode")
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.link(stage, path, follow_symlinks=False)
        output_ownership = _path_inode(path)
        if output_ownership != stage_ownership:
            raise RuntimeError("independent audit output inode is not the staged inode")
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        if stable_regular_file_bytes(path)[0] != payload:
            raise RuntimeError("independent audit post-replace byte drift")
        return output_ownership
    except BaseException:
        _unlink_owned_path(path, output_ownership)
        raise
    finally:
        _unlink_owned_path(stage, stage_ownership)


def _capture_audit_input_snapshot() -> tuple[
    dict[str, bytes], dict[str, dict[str, Any]], dict[str, Any]
]:
    payloads: dict[str, bytes] = {}
    metadata: dict[str, dict[str, Any]] = {}
    manifest_bytes, manifest_metadata = stable_regular_file_bytes(MANIFEST)
    manifest = parse_json_object_bytes(manifest_bytes, "manifest")
    payloads["manifest"] = manifest_bytes
    metadata["manifest"] = manifest_metadata
    pins = manifest.get("pinned_files")
    if type(pins) is not dict:
        raise RuntimeError("manifest pin map is malformed")
    for role in sorted(pins):
        row = pins[role]
        raw = Path(row["path"])
        if raw.is_absolute() or ".." in raw.parts:
            raise RuntimeError(f"pinned path escapes report: {role}")
        current = REPORT
        for index, part in enumerate(raw.parts):
            current = current / part
            item = os.lstat(current)
            if stat.S_ISLNK(item.st_mode):
                raise RuntimeError(f"pinned lexical chain contains symlink: {role}")
            if index < len(raw.parts) - 1 and not stat.S_ISDIR(item.st_mode):
                raise RuntimeError(f"pinned lexical parent is not directory: {role}")
        pin_bytes, pin_metadata = stable_regular_file_bytes(current)
        payloads[f"pin:{role}"] = pin_bytes
        metadata[f"pin:{role}"] = pin_metadata
    for label, path in (("result", RESULT), ("evidence", EVIDENCE)):
        raw, item = stable_regular_file_bytes(path)
        payloads[label] = raw
        metadata[label] = item
    return payloads, metadata, manifest


def main() -> int:
    if lexical_path_exists(OUTPUT):
        raise RuntimeError("independent audit output is append-only")
    hidden_replicas = [REPORT / relative for relative in EXPECTED_FIVE_PATH_ABSENCE[2:4]]
    if any(lexical_path_exists(path) for path in hidden_replicas):
        raise RuntimeError("hidden replica paths must be absent before post-result audit")
    initial_payloads, initial_metadata, manifest = _capture_audit_input_snapshot()
    if sha256_bytes(initial_payloads["manifest"]) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("allocation-cusp v6 manifest hash changed")
    result_bytes = initial_payloads["result"]
    evidence_bytes = initial_payloads["evidence"]
    result = parse_json_object_bytes(result_bytes, "canonical result")
    evidence = parse_json_object_bytes(evidence_bytes, "reproducibility evidence")
    audit = audit_payload(manifest, result, evidence, result_bytes, evidence_bytes)
    output_ownership: tuple[int, int] | None = None
    try:
        output_ownership = write_append_only(OUTPUT, canonical_json_bytes(audit))
        final_payloads, final_metadata, _final_manifest = _capture_audit_input_snapshot()
        if final_payloads != initial_payloads or final_metadata != initial_metadata:
            raise RuntimeError("audit input metadata/bytes changed during audit window")
    except BaseException:
        _unlink_owned_path(OUTPUT, output_ownership)
        raise
    print(audit["release_status"])
    print(OUTPUT)
    return 0 if audit["audit_integrity_passed"] and audit["scientific_result_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
