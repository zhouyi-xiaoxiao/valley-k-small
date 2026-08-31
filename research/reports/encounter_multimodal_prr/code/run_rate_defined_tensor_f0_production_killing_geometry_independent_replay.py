"""Two-clean-process replay wrapper for the separate-source geometry verifier.

This observer is intentionally narrower than an F0 runner.  It stages the
finite frozen input closure twice, launches the separately coded verifier in
two serialized fresh processes, validates the complete file/stdout wire, and
accepts only byte-identical deterministic semantic receipts.  It never builds
a concrete killing array or promotes an operator, F0, F1, or release claim.

The caller must provide a dedicated current-UID-owned 0700 receipt directory.
That excludes group/other writers, but is not an OS sandbox against a separate
concurrent process running under the same UID; formal replay excludes such a
concurrent writer while the exclusive publication protocol is active.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import secrets
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final, Sequence

try:
    import gmpy2
except Exception:  # pragma: no cover - converted to a source HOLD by _main
    gmpy2 = None


OPERATION_MODEL_SHA256: Final = "53f709139c380e9512740a6fdabcd7570c1822650817915454ddbd7d7395feb0"
OPERATION_MODEL_SCHEMA: Final = "encounter_killing_geometry_independent_operation_model_v2"
EXPECTED_VERIFIER_SHA256: Final = "70942ed70eabd1cca48499d004550670bd12acfe714e4d6ca43308a210f1fb4d"
SNAPSHOT_SCHEMA: Final = "encounter_killing_geometry_input_snapshot_v1"
SNAPSHOT_DOMAIN: Final = b"encounter-killing-geometry-input-snapshot-v1\0"

CHILD_PASS_STATUS: Final = (
    "PASS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_SAME_BACKEND_"
    "CONTAINMENT_CHILD_ONLY_NOT_CLEAN_REPLAY_NOT_CONCRETE_KILLING_"
    "NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
OUTER_PASS_STATUS: Final = (
    "PASS_TWO_REPEAT_CLEAN_PROCESS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_"
    "SAME_BACKEND_CONTAINMENT_ONLY_NOT_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
HOLD_API: Final = "HOLD_KILLING_GEOMETRY_VERIFY_API"
HOLD_SOURCE: Final = "HOLD_KILLING_GEOMETRY_VERIFY_SOURCE"
HOLD_IMPORT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_IMPORT_BOUNDARY"
HOLD_TREE: Final = "HOLD_KILLING_GEOMETRY_VERIFY_TREE"
HOLD_MANIFEST: Final = "HOLD_KILLING_GEOMETRY_VERIFY_MANIFEST"
HOLD_PARTITION: Final = "HOLD_KILLING_GEOMETRY_VERIFY_PARTITION"
HOLD_CONTACT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CONTACT_ORACLE"
HOLD_SUPPORT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_SUPPORT_ORACLE"
HOLD_CONTAINMENT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CONTAINMENT"
HOLD_WIDTH: Final = "HOLD_KILLING_GEOMETRY_VERIFY_WIDTH"
HOLD_NORMALIZATION: Final = "HOLD_KILLING_GEOMETRY_VERIFY_NORMALIZATION"
HOLD_REPEAT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_REPEAT"
HOLD_TIMEOUT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_TIMEOUT"
HOLD_CLEANUP: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CLEANUP"
HOLD_STATUSES: Final = (
    HOLD_API,
    HOLD_SOURCE,
    HOLD_IMPORT,
    HOLD_TREE,
    HOLD_MANIFEST,
    HOLD_PARTITION,
    HOLD_CONTACT,
    HOLD_SUPPORT,
    HOLD_CONTAINMENT,
    HOLD_WIDTH,
    HOLD_NORMALIZATION,
    HOLD_REPEAT,
    HOLD_TIMEOUT,
    HOLD_CLEANUP,
)

CHILD_ACK_SCHEMA: Final = "encounter_killing_geometry_child_ack_v1"
CHILD_UNBOUND_HOLD_ACK_SCHEMA: Final = "encounter_killing_geometry_child_unbound_hold_ack_v1"
CHILD_OBSERVATION_SCHEMA: Final = "encounter_killing_geometry_child_observation_v1"
CHILD_SEMANTIC_SCHEMA: Final = (
    "encounter_killing_geometry_separate_source_child_semantic_receipt_v2"
)
CHILD_SEMANTIC_HOLD_SCHEMA: Final = "encounter_killing_geometry_separate_source_hold_v1"
OUTER_RECEIPT_SCHEMA: Final = "encounter_killing_geometry_two_repeat_outer_receipt_v1"
OUTER_ACK_SCHEMA: Final = "encounter_killing_geometry_outer_ack_v1"
OUTER_HOLD_ACK_SCHEMA: Final = "encounter_killing_geometry_outer_hold_ack_v1"

CHILD_PROCESS_DEADLINE_SECONDS: Final = 1_200
OUTER_DEADLINE_SECONDS: Final = 2_700
OUTER_NONCHILD_RESERVE_SECONDS: Final = 300
TERM_GRACE_SECONDS: Final = 3
KILL_WAIT_SECONDS: Final = 2
PIPE_DRAIN_SECONDS: Final = 2
MAX_CHILD_ACK_BYTES: Final = 4_096
MAX_CHILD_STDERR_BYTES: Final = 4_096
MAX_CHILD_SEMANTIC_BYTES: Final = 2_097_152
MAX_CHILD_OBSERVATION_BYTES: Final = 65_536
MAX_OUTER_RECEIPT_BYTES: Final = 262_144
MAX_TREE_FILES: Final = 256
MAX_TREE_DIRECTORIES: Final = 64
MAX_TREE_BYTES: Final = 67_108_864
MAX_TREE_DEPTH: Final = 3
MAX_FILE_COMPONENT_BYTES: Final = 536_870_912

AUTHORITY_PATH: Final = Path("artifacts/data/physical_killing_geometry_source_v1.json")
CONFIGURATION_PATH: Final = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
PARTITION_ROOT_PATH: Final = Path("artifacts/data/physical_production_initial_stream_v1")
PRODUCER_PATH: Final = Path("code/rate_defined_tensor_f0_production_killing_geometry.py")
PRODUCER_TEST_PATH: Final = Path("code/test_rate_defined_tensor_f0_production_killing_geometry.py")
F0_CORE_PATH: Final = Path("code/rate_defined_tensor_f0.py")
INITIAL_STREAM_PATH: Final = Path("code/rate_defined_tensor_f0_production_initial_stream.py")
DESIGN_PATH: Final = Path("notes/f0_production_killing_geometry_independent_verifier_design.md")
VERIFIER_PATH: Final = Path(
    "code/rate_defined_tensor_f0_production_killing_geometry_independent.py"
)
OPERATION_MODEL_PATH: Final = Path(
    "code/rate_defined_tensor_f0_production_killing_geometry_independent_operation_model_v2.json"
)

COMPONENT_ORDER: Final = (
    "candidate_tree",
    "accepted_partition_tree",
    "authority_bytes",
    "control_free_configuration_bytes",
    "producer_source",
    "producer_test_source",
    "f0_core_source",
    "initial_stream_source",
    "design_bytes",
    "independent_verifier_source",
    "operation_model_bytes",
    "runtime_executable",
    "gmpy2_extension",
)

_SHA_RE: Final = re.compile(r"[0-9a-f]{64}\Z")
_NONCE_RE: Final = re.compile(r"[0-9a-f]{64}\Z")

CHILD_SEMANTIC_KEYS: Final = {
    "candidate",
    "contact_summary",
    "flags",
    "frozen_sources",
    "independent_partition_semantic_sha256s",
    "precision_bits",
    "runtime",
    "schema",
    "status",
    "support_policy_digests",
    "support_summary",
    "verifier_staged_file_sha256_at_receipt",
}
CHILD_OBSERVATION_KEYS: Final = {
    "elapsed_monotonic_ns",
    "launch_nonce",
    "peak_rss_bytes",
    "pgid",
    "pid",
    "ppid",
    "run_index",
    "schema",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "status",
    "verifier_staged_file_sha256_at_observation",
}
CHILD_ACK_KEYS: Final = {
    "launch_nonce",
    "observation_byte_length",
    "observation_sha256",
    "run_index",
    "schema",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "status",
}
OUTER_RECEIPT_KEYS: Final = {
    "child_runs",
    "flags",
    "input_snapshot_sha256",
    "operation_model_sha256",
    "runtime",
    "schema",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "status",
    "verifier_source_sha256",
}
OUTER_CHILD_RUN_KEYS: Final = {
    "cleanup",
    "exit_code",
    "launch_nonce",
    "observation_byte_length",
    "observation_sha256",
    "pgid",
    "pid",
    "run_index",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "snapshot_sha256s",
    "stderr_byte_length",
    "stderr_sha256",
    "stdout_byte_length",
    "stdout_sha256",
}
CLEANUP_KEYS: Final = {
    "direct_child_reaped",
    "parent_pipe_fds_closed",
    "process_group_absent",
    "selector_closed",
    "stage_absent",
    "stderr_eof_observed",
    "stdout_eof_observed",
}
SNAPSHOT_PHASE_KEYS: Final = {
    "origin_pre_copy",
    "stage_post_copy",
    "stage_pre_launch",
    "stage_post_exit",
}

REQUIRED_SEMANTIC_FLAGS: Final = {
    "candidate_width_caps_passed": True,
    "concrete_killing_constructed": False,
    "contact_pi_r_squared_enclosed_all_rows": True,
    "continuum_verified": False,
    "directed_mpfr_contact_oracle": True,
    "f0_core_imported": False,
    "f0_pass": False,
    "f1_authorized": False,
    "full_operator_bound": False,
    "independent_backend": False,
    "independent_simpson_remainder_source": True,
    "initial_stream_imported": False,
    "installed_budget_used": False,
    "killing_geometry_bound": True,
    "largest_state_tensor_allocated": False,
    "partitions_reconstructed_from_control_free_config": True,
    "positive_budget_executed": False,
    "producer_envelopes_contain_independent_oracles": True,
    "producer_module_imported": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "prospective_control_used": False,
    "prr_release_authorized": False,
    "resource_promotion_eligible": False,
    "science_executed": False,
    "separate_source_implementation": True,
    "shared_simpson_remainder_lemma": True,
    "single_physical_operator_bound": False,
    "support_unit_integral_enclosed_all_rows_profiles": True,
    "topology_complete": False,
    "verifier_executed_source_attested": False,
}
ADDITIONAL_SEMANTIC_FLAGS: Final = {
    "flat_tail_bound_active": True,
    "outer_staged_source_pre_post_required": True,
    "paired_same_leaf_precision_sentinel": True,
    "sentinel_independent_2^-68_adaptive": False,
}
OUTER_ONLY_FLAGS: Final = {
    "child_process_groups_cleaned": True,
    "clean_process_repeat_count": 2,
    "distinct_child_pids": True,
    "full_binary_dependency_filesystem_closure": False,
    "os_network_isolation": False,
    "pinned_source_requests_no_network_api": True,
    "semantic_receipt_bytes_identical": True,
    "serialized_child_execution": True,
    "temporary_stages_removed": True,
}


class ReplayHold(Exception):
    """Bounded internal failure carrying only a frozen public HOLD status."""

    def __init__(self, status: str):
        super().__init__(status)
        self.status = status if status in HOLD_STATUSES else HOLD_API


@dataclass(frozen=True)
class ComponentSpec:
    component: str
    kind: str
    origin: Path
    staged: Path | None
    external: bool = False


@dataclass(frozen=True)
class Snapshot:
    body: dict[str, object]
    raw: bytes
    digest: str

    def component(self, name: str) -> dict[str, object]:
        for record in self.body["components"]:  # type: ignore[index]
            if record["component"] == name:
                return record
        raise ReplayHold(HOLD_SOURCE)


@dataclass(frozen=True)
class LinkChain:
    launcher: Path
    final_target: Path
    records: tuple[tuple[str, int, str], ...]


@dataclass
class CaptureResult:
    pid: int
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    issue_status: str | None
    cleanup: dict[str, bool]


@dataclass
class RunResult:
    record: dict[str, object]
    semantic_raw: bytes
    semantic: dict[str, object]


@dataclass(frozen=True)
class ReceiptTarget:
    path: Path
    parent_identity: tuple[int, int, int]


@dataclass
class PublishedReceipt:
    target: ReceiptTarget
    directory_descriptor: int
    file_identity: tuple[int, int, int, int, int, int]
    raw: bytes
    closed: bool = False


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    try:
        encoded = (
            json.dumps(
                value,
                sort_keys=True,
                indent=2,
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise ReplayHold(HOLD_API) from error
    return encoded


def _reject_constant(_: str) -> object:
    raise ValueError("non-finite JSON number")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_float_tree(value: object) -> None:
    if type(value) is float:
        raise ReplayHold(HOLD_REPEAT)
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ReplayHold(HOLD_REPEAT)
            _reject_json_float_tree(item)
    elif type(value) is list:
        for item in value:
            _reject_json_float_tree(item)


def _decode_canonical_object(raw: bytes, *, maximum_bytes: int) -> dict[str, object]:
    if len(raw) > maximum_bytes:
        raise ReplayHold(HOLD_REPEAT)
    try:
        if raw.decode("ascii").encode("ascii") != raw:
            raise ValueError("non-ASCII JSON")
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise ReplayHold(HOLD_REPEAT) from error
    _reject_json_float_tree(value)
    if type(value) is not dict or _canonical_json_bytes(value) != raw:
        raise ReplayHold(HOLD_REPEAT)
    return value


def _exact_keys(value: object, keys: set[str], *, status: str = HOLD_REPEAT) -> dict[str, object]:
    if type(value) is not dict or set(value) != keys:
        raise ReplayHold(status)
    return value


def _exact_nonnegative_int(value: object, *, positive: bool = False) -> int:
    if type(value) is not int or value < (1 if positive else 0):
        raise ReplayHold(HOLD_REPEAT)
    return value


def _exact_sha(value: object) -> str:
    if type(value) is not str or _SHA_RE.fullmatch(value) is None:
        raise ReplayHold(HOLD_REPEAT)
    return value


def _runtime_versions() -> dict[str, str]:
    if gmpy2 is None:
        raise ReplayHold(HOLD_SOURCE)
    values = {
        "gmp": gmpy2.mp_version().removeprefix("GMP "),
        "gmpy2": gmpy2.version(),
        "mpc": gmpy2.mpc_version().removeprefix("MPC "),
        "mpfr": gmpy2.mpfr_version().removeprefix("MPFR "),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    if any(type(item) is not str or not item or not item.isascii() for item in values.values()):
        raise ReplayHold(HOLD_SOURCE)
    return values


def _lstat_chain(path: Path, *, require_executable: bool = True) -> LinkChain:
    if not path.is_absolute():
        raise ReplayHold(HOLD_SOURCE)
    current = Path(os.path.abspath(path))
    records: list[tuple[str, int, str]] = []
    visited: set[str] = set()
    for _ in range(41):
        lexical = os.fspath(current)
        if lexical in visited:
            raise ReplayHold(HOLD_SOURCE)
        visited.add(lexical)
        try:
            metadata = os.lstat(current)
        except OSError as error:
            raise ReplayHold(HOLD_SOURCE) from error
        if stat.S_ISLNK(metadata.st_mode):
            try:
                target = os.readlink(current)
            except OSError as error:
                raise ReplayHold(HOLD_SOURCE) from error
            if not target or not target.isascii():
                raise ReplayHold(HOLD_SOURCE)
            records.append((lexical, stat.S_IFLNK, target))
            next_path = Path(target)
            current = next_path if next_path.is_absolute() else current.parent / next_path
            current = Path(os.path.abspath(current))
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise ReplayHold(HOLD_SOURCE)
        records.append((lexical, stat.S_IFREG, ""))
        try:
            physical_target = current.resolve(strict=True)
            physical_metadata = os.lstat(physical_target)
        except OSError as error:
            raise ReplayHold(HOLD_SOURCE) from error
        if not stat.S_ISREG(physical_metadata.st_mode) or stat.S_ISLNK(physical_metadata.st_mode):
            raise ReplayHold(HOLD_SOURCE)
        records.append((os.fspath(physical_target), stat.S_IFREG, "physical_target"))
        if require_executable and not os.access(physical_target, os.X_OK):
            raise ReplayHold(HOLD_SOURCE)
        return LinkChain(Path(os.path.abspath(path)), physical_target, tuple(records))
    raise ReplayHold(HOLD_SOURCE)


def _gmpy2_link_chain() -> LinkChain:
    extension = None if gmpy2 is None else getattr(gmpy2, "gmpy2", None)
    extension_path = None if extension is None else getattr(extension, "__file__", None)
    if type(extension_path) is not str or not extension_path.endswith(".so"):
        raise ReplayHold(HOLD_SOURCE)
    return _lstat_chain(Path(extension_path), require_executable=False)


def _read_regular_stable(path: Path, *, maximum_bytes: int) -> bytes:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ReplayHold(HOLD_SOURCE)
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
            raise ReplayHold(HOLD_SOURCE)
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | nofollow)
    except ReplayHold:
        raise
    except OSError as error:
        raise ReplayHold(HOLD_SOURCE) from error
    try:
        opened = os.fstat(descriptor)
        identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_size,
            opened.st_mtime_ns,
        )
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != before.st_dev
            or opened.st_ino != before.st_ino
            or opened.st_size < 0
            or opened.st_size > maximum_bytes
        ):
            raise ReplayHold(HOLD_SOURCE)
        chunks: list[bytes] = []
        remaining = opened.st_size
        while remaining:
            chunk = os.read(descriptor, min(1 << 20, remaining))
            if not chunk:
                raise ReplayHold(HOLD_SOURCE)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1) != b"":
            raise ReplayHold(HOLD_SOURCE)
        after_fd = os.fstat(descriptor)
        if (
            after_fd.st_dev,
            after_fd.st_ino,
            after_fd.st_mode,
            after_fd.st_size,
            after_fd.st_mtime_ns,
        ) != identity:
            raise ReplayHold(HOLD_SOURCE)
    finally:
        if not _close_descriptor_confirmed(descriptor):
            raise ReplayHold(HOLD_CLEANUP)
    try:
        after = os.lstat(path)
    except OSError as error:
        raise ReplayHold(HOLD_SOURCE) from error
    if (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns) != identity:
        raise ReplayHold(HOLD_SOURCE)
    return b"".join(chunks)


def _read_published_stable(path: Path, *, maximum_bytes: int) -> bytes:
    def read_once() -> bytes:
        try:
            metadata = os.lstat(path)
        except OSError as error:
            raise ReplayHold(HOLD_REPEAT) from error
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_nlink != 1
            or metadata.st_size < 0
            or metadata.st_size > maximum_bytes
        ):
            raise ReplayHold(HOLD_REPEAT)
        try:
            return _read_regular_stable(path, maximum_bytes=maximum_bytes)
        except ReplayHold as error:
            raise ReplayHold(HOLD_REPEAT) from error

    first = read_once()
    second = read_once()
    if first != second:
        raise ReplayHold(HOLD_REPEAT)
    return first


def _safe_ascii_relative(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ReplayHold(HOLD_TREE) from error
    pure = PurePosixPath(relative.as_posix())
    if (
        pure.is_absolute()
        or not pure.parts
        or any(part in {"", ".", ".."} for part in pure.parts)
        or not pure.as_posix().isascii()
    ):
        raise ReplayHold(HOLD_TREE)
    return pure.as_posix()


def _metadata_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _directory_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    # Directory link counts can change when this process creates the receipt.
    return metadata.st_dev, metadata.st_ino, metadata.st_mode


def _published_file_identity(
    metadata: os.stat_result,
) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
    )


def _directory_signature(
    path: Path,
) -> tuple[
    tuple[int, int, int, int, int, int],
    tuple[tuple[str, tuple[int, int, int, int, int, int]], ...],
]:
    try:
        metadata = os.lstat(path)
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise ReplayHold(HOLD_TREE)
        entries = list(os.scandir(path))
        signature: list[tuple[str, tuple[int, int, int, int, int, int]]] = []
        for entry in entries:
            if not entry.name.isascii() or entry.name in {"", ".", ".."}:
                raise ReplayHold(HOLD_TREE)
            entry_metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(entry_metadata.st_mode):
                raise ReplayHold(HOLD_TREE)
            signature.append((entry.name, _metadata_identity(entry_metadata)))
        signature.sort(key=lambda item: item[0])
        after = os.lstat(path)
    except ReplayHold:
        raise
    except OSError as error:
        raise ReplayHold(HOLD_TREE) from error
    if _metadata_identity(metadata) != _metadata_identity(after):
        raise ReplayHold(HOLD_TREE)
    return _metadata_identity(metadata), tuple(signature)


def _tree_record(
    component: str,
    root: Path,
    *,
    require_single_link: bool = False,
    require_read_only: bool = False,
) -> dict[str, object]:
    try:
        root_meta = os.lstat(root)
    except OSError as error:
        raise ReplayHold(HOLD_TREE) from error
    if not stat.S_ISDIR(root_meta.st_mode) or stat.S_ISLNK(root_meta.st_mode):
        raise ReplayHold(HOLD_TREE)
    if require_read_only and root_meta.st_mode & 0o222:
        raise ReplayHold(HOLD_TREE)
    directories = ["."]
    files: list[dict[str, object]] = []
    total = 0
    root_identity = _metadata_identity(root_meta)
    pending = [(root, root_identity)]
    observed_signatures: dict[
        Path,
        tuple[
            tuple[int, int, int, int, int, int],
            tuple[tuple[str, tuple[int, int, int, int, int, int]], ...],
        ],
    ] = {}
    while pending:
        current, expected_identity = pending.pop()
        current_signature = _directory_signature(current)
        if current_signature[0] != expected_identity:
            raise ReplayHold(HOLD_TREE)
        if require_read_only and current_signature[0][2] & 0o222:
            raise ReplayHold(HOLD_TREE)
        observed_signatures[current] = current_signature
        try:
            entries = list(os.scandir(current))
        except OSError as error:
            raise ReplayHold(HOLD_TREE) from error
        for entry in entries:
            path = Path(entry.path)
            relative = _safe_ascii_relative(path, root)
            depth = len(PurePosixPath(relative).parts)
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as error:
                raise ReplayHold(HOLD_TREE) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise ReplayHold(HOLD_TREE)
            if stat.S_ISDIR(metadata.st_mode):
                if depth > MAX_TREE_DEPTH:
                    raise ReplayHold(HOLD_TREE)
                if require_read_only and metadata.st_mode & 0o222:
                    raise ReplayHold(HOLD_TREE)
                directories.append(relative)
                pending.append((path, _metadata_identity(metadata)))
            elif stat.S_ISREG(metadata.st_mode):
                if depth > MAX_TREE_DEPTH:
                    raise ReplayHold(HOLD_TREE)
                if require_single_link and metadata.st_nlink != 1:
                    raise ReplayHold(HOLD_TREE)
                if require_read_only and metadata.st_mode & 0o222:
                    raise ReplayHold(HOLD_TREE)
                raw = _read_regular_stable(path, maximum_bytes=MAX_TREE_BYTES)
                total += len(raw)
                if total > MAX_TREE_BYTES:
                    raise ReplayHold(HOLD_TREE)
                files.append({"byte_length": len(raw), "path": relative, "sha256": _sha256(raw)})
            else:
                raise ReplayHold(HOLD_TREE)
            if len(directories) > MAX_TREE_DIRECTORIES or len(files) > MAX_TREE_FILES:
                raise ReplayHold(HOLD_TREE)
        if _directory_signature(current) != current_signature:
            raise ReplayHold(HOLD_TREE)
    for path, signature in observed_signatures.items():
        if _directory_signature(path) != signature:
            raise ReplayHold(HOLD_TREE)
    directories.sort()
    files.sort(key=lambda record: record["path"])
    return {
        "component": component,
        "directories": directories,
        "directory_count": len(directories),
        "file_count": len(files),
        "files": files,
        "kind": "tree",
        "total_byte_length": total,
    }


def _file_record(
    component: str,
    path: Path,
    *,
    require_single_link: bool = False,
    require_read_only: bool = False,
) -> dict[str, object]:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise ReplayHold(HOLD_SOURCE) from error
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or (require_single_link and metadata.st_nlink != 1)
        or (require_read_only and metadata.st_mode & 0o222)
    ):
        raise ReplayHold(HOLD_SOURCE)
    raw = _read_regular_stable(path, maximum_bytes=MAX_FILE_COMPONENT_BYTES)
    return {
        "byte_length": len(raw),
        "component": component,
        "kind": "file",
        "sha256": _sha256(raw),
    }


def _component_specs(
    report_root: Path,
    bundle_root: Path,
    stage: Path | None,
    runtime_chain: LinkChain,
    extension_chain: LinkChain,
) -> tuple[ComponentSpec, ...]:
    staged_report = None if stage is None else stage / "inputs" / "report"
    staged_candidate = None if stage is None else stage / "inputs" / "candidate_tree"

    def report_file(name: str, relative: Path) -> ComponentSpec:
        return ComponentSpec(
            name,
            "file",
            report_root / relative,
            None if staged_report is None else staged_report / relative,
        )

    return (
        ComponentSpec("candidate_tree", "tree", bundle_root, staged_candidate),
        ComponentSpec(
            "accepted_partition_tree",
            "tree",
            report_root / PARTITION_ROOT_PATH,
            None if staged_report is None else staged_report / PARTITION_ROOT_PATH,
        ),
        report_file("authority_bytes", AUTHORITY_PATH),
        report_file("control_free_configuration_bytes", CONFIGURATION_PATH),
        report_file("producer_source", PRODUCER_PATH),
        report_file("producer_test_source", PRODUCER_TEST_PATH),
        report_file("f0_core_source", F0_CORE_PATH),
        report_file("initial_stream_source", INITIAL_STREAM_PATH),
        report_file("design_bytes", DESIGN_PATH),
        report_file("independent_verifier_source", VERIFIER_PATH),
        report_file("operation_model_bytes", OPERATION_MODEL_PATH),
        ComponentSpec(
            "runtime_executable",
            "file",
            runtime_chain.final_target,
            runtime_chain.final_target,
            external=True,
        ),
        ComponentSpec(
            "gmpy2_extension",
            "file",
            extension_chain.final_target,
            extension_chain.final_target,
            external=True,
        ),
    )


def _snapshot(
    specs: Sequence[ComponentSpec],
    *,
    staged: bool,
    require_read_only: bool = False,
) -> Snapshot:
    if tuple(spec.component for spec in specs) != COMPONENT_ORDER:
        raise ReplayHold(HOLD_SOURCE)
    records: list[dict[str, object]] = []
    for spec in specs:
        path = spec.origin if not staged or spec.external else spec.staged
        if path is None:
            raise ReplayHold(HOLD_SOURCE)
        staged_component = staged and not spec.external
        record = (
            _tree_record(
                spec.component,
                path,
                require_single_link=staged_component,
                require_read_only=require_read_only and staged_component,
            )
            if spec.kind == "tree"
            else _file_record(
                spec.component,
                path,
                require_single_link=staged_component,
                require_read_only=require_read_only and staged_component,
            )
        )
        records.append(record)
    body = {
        "components": records,
        "runtime_versions": _runtime_versions(),
        "schema": SNAPSHOT_SCHEMA,
    }
    raw = _canonical_json_bytes(body)
    return Snapshot(body, raw, _sha256(SNAPSHOT_DOMAIN + raw))


def _copy_file_bytes(source: Path, destination: Path, *, maximum_bytes: int) -> None:
    raw = _read_regular_stable(source, maximum_bytes=maximum_bytes)
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if not hasattr(os, "O_NOFOLLOW"):
        raise ReplayHold(HOLD_SOURCE)
    flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(destination, flags, 0o600)
    except OSError as error:
        raise ReplayHold(HOLD_SOURCE) from error
    try:
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ReplayHold(HOLD_SOURCE)
            view = view[written:]
        os.fsync(descriptor)
        destination_meta = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    source_meta = os.stat(source, follow_symlinks=False)
    if destination_meta.st_nlink != 1 or (destination_meta.st_dev, destination_meta.st_ino) == (
        source_meta.st_dev,
        source_meta.st_ino,
    ):
        raise ReplayHold(HOLD_SOURCE)


def _copy_tree_bytes(source: Path, destination: Path, record: dict[str, object]) -> None:
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    directories = record["directories"]
    files = record["files"]
    if type(directories) is not list or type(files) is not list:
        raise ReplayHold(HOLD_TREE)
    for relative in directories:
        if relative != ".":
            (destination / relative).mkdir(mode=0o700, parents=True, exist_ok=False)
    for file_record in files:
        relative = file_record["path"]
        _copy_file_bytes(
            source / relative,
            destination / relative,
            maximum_bytes=MAX_TREE_BYTES,
        )


def _copy_staged_components(specs: Sequence[ComponentSpec], origin: Snapshot) -> None:
    by_name = {record["component"]: record for record in origin.body["components"]}
    for spec in specs:
        if spec.external:
            continue
        if spec.staged is None:
            raise ReplayHold(HOLD_SOURCE)
        record = by_name[spec.component]
        if spec.kind == "tree":
            _copy_tree_bytes(spec.origin, spec.staged, record)
        else:
            _copy_file_bytes(spec.origin, spec.staged, maximum_bytes=MAX_FILE_COMPONENT_BYTES)


def _make_inputs_read_only(input_root: Path) -> None:
    for root, directories, files in os.walk(input_root, topdown=False, followlinks=False):
        for name in files:
            path = Path(root) / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise ReplayHold(HOLD_SOURCE)
            os.chmod(path, 0o400, follow_symlinks=False)
        for name in directories:
            path = Path(root) / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise ReplayHold(HOLD_SOURCE)
            os.chmod(path, 0o500, follow_symlinks=False)
    os.chmod(input_root, 0o500, follow_symlinks=False)


def _make_stage_writable(stage: Path) -> None:
    if not os.path.lexists(stage):
        return
    for root, directories, files in os.walk(stage, topdown=False, followlinks=False):
        for name in files:
            try:
                os.chmod(Path(root) / name, 0o600, follow_symlinks=False)
            except OSError:
                pass
        for name in directories:
            try:
                os.chmod(Path(root) / name, 0o700, follow_symlinks=False)
            except OSError:
                pass
    try:
        os.chmod(stage, 0o700, follow_symlinks=False)
    except OSError:
        pass


def _remove_stage(stage: Path) -> bool:
    try:
        _make_stage_writable(stage)
        shutil.rmtree(stage)
    except OSError:
        return False
    return not os.path.lexists(stage)


def _new_stage(input_roots: Sequence[Path], run_index: int) -> Path:
    parent = Path(tempfile.gettempdir()).resolve(strict=True)
    for input_root in input_roots:
        try:
            parent.relative_to(input_root)
        except ValueError:
            pass
        else:
            raise ReplayHold(HOLD_SOURCE)
    stage: Path | None = None
    try:
        stage = Path(tempfile.mkdtemp(prefix=f"encounter-kg-replay-{run_index}-", dir=parent))
        os.chmod(stage, 0o700)
        for relative in (
            Path("home"),
            Path("tmp"),
            Path("inputs"),
            Path("outputs"),
        ):
            path = stage / relative
            path.mkdir(mode=0o700)
            if stat.S_IMODE(os.stat(path).st_mode) != 0o700:
                raise ReplayHold(HOLD_SOURCE)
        return stage
    except BaseException as error:
        if stage is not None and not _remove_stage(stage):
            raise ReplayHold(HOLD_CLEANUP) from error
        if isinstance(error, ReplayHold):
            raise
        raise ReplayHold(HOLD_SOURCE) from error


def _child_environment(stage: Path) -> dict[str, str]:
    environment = {
        "HOME": os.fspath(stage / "home"),
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.fspath(stage / "tmp"),
        "TZ": "UTC",
    }
    if set(environment) != {"HOME", "LANG", "LC_ALL", "TMPDIR", "TZ"} or len(environment) != 5:
        raise ReplayHold(HOLD_API)
    return environment


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _signal_group(pgid: int, action: signal.Signals) -> None:
    try:
        os.killpg(pgid, action)
    except ProcessLookupError:
        pass
    except OSError:
        pass


def _finish_started_process(
    process: subprocess.Popen[bytes],
    selector: selectors.BaseSelector,
    *,
    global_deadline: float,
    issue: str | None,
    buffers: dict[str, bytearray] | None = None,
    eof: dict[str, bool] | None = None,
) -> CaptureResult:
    """Idempotent bounded cleanup for every path after successful Popen."""
    streams = {"stdout": process.stdout, "stderr": process.stderr}
    buffers = buffers or {"stdout": bytearray(), "stderr": bytearray()}
    eof = eof or {"stdout": False, "stderr": False}
    limits = {"stdout": MAX_CHILD_ACK_BYTES, "stderr": MAX_CHILD_STDERR_BYTES}

    def drain_once() -> None:
        nonlocal issue
        for name, stream in streams.items():
            if stream is None or eof[name] or stream.closed:
                continue
            try:
                os.set_blocking(stream.fileno(), False)
                while True:
                    chunk = os.read(stream.fileno(), 65_536)
                    if chunk == b"":
                        eof[name] = True
                        break
                    remaining = limits[name] + 1 - len(buffers[name])
                    if remaining > 0:
                        buffers[name].extend(chunk[:remaining])
                    if len(buffers[name]) > limits[name] and issue is None:
                        issue = HOLD_REPEAT
            except BlockingIOError:
                pass
            except BaseException:
                if issue is None:
                    issue = HOLD_REPEAT

    try:
        for key in list(selector.get_map().values()):
            try:
                selector.unregister(key.fileobj)
            except BaseException:
                pass
    except BaseException:
        issue = HOLD_CLEANUP

    return_code = process.poll()
    direct_reaped = return_code is not None
    group_alive = _group_exists(process.pid)
    if return_code is not None and group_alive and issue is None:
        issue = HOLD_CLEANUP
    if return_code is None or group_alive:
        if issue is None:
            issue = HOLD_CLEANUP
        _signal_group(process.pid, signal.SIGTERM)
        term_deadline = min(time.monotonic() + TERM_GRACE_SECONDS, global_deadline)
        while time.monotonic() < term_deadline and (
            process.poll() is None or _group_exists(process.pid)
        ):
            drain_once()
            time.sleep(min(0.01, max(0.0, term_deadline - time.monotonic())))
        if process.poll() is None or _group_exists(process.pid):
            _signal_group(process.pid, signal.SIGKILL)
            kill_deadline = min(time.monotonic() + KILL_WAIT_SECONDS, global_deadline)
            while time.monotonic() < kill_deadline and (
                process.poll() is None or _group_exists(process.pid)
            ):
                drain_once()
                time.sleep(min(0.01, max(0.0, kill_deadline - time.monotonic())))

    try:
        return_code = process.wait(
            timeout=max(
                0.0,
                min(KILL_WAIT_SECONDS, global_deadline - time.monotonic()),
            )
        )
        direct_reaped = True
    except BaseException:
        return_code = None
        issue = HOLD_CLEANUP

    group_absent = not _group_exists(process.pid)
    if not group_absent:
        _signal_group(process.pid, signal.SIGKILL)
        kill_deadline = min(time.monotonic() + KILL_WAIT_SECONDS, global_deadline)
        while time.monotonic() < kill_deadline and _group_exists(process.pid):
            drain_once()
            time.sleep(min(0.01, max(0.0, kill_deadline - time.monotonic())))
        group_absent = not _group_exists(process.pid)
        if not group_absent:
            issue = HOLD_CLEANUP

    drain_once()
    pipe_deadline = min(time.monotonic() + PIPE_DRAIN_SECONDS, global_deadline)
    while not all(eof.values()) and time.monotonic() < pipe_deadline:
        drain_once()
        time.sleep(min(0.01, max(0.0, pipe_deadline - time.monotonic())))
    if not all(eof.values()):
        issue = HOLD_CLEANUP

    for stream in streams.values():
        if stream is not None:
            try:
                stream.close()
            except BaseException:
                pass
    pipes_closed = all(stream is not None and stream.closed for stream in streams.values())
    try:
        selector_empty = not selector.get_map()
    except BaseException:
        selector_empty = False
    try:
        selector.close()
        selector_closed = selector_empty
    except BaseException:
        selector_closed = False

    cleanup = {
        "direct_child_reaped": direct_reaped,
        "parent_pipe_fds_closed": pipes_closed,
        "process_group_absent": group_absent,
        "selector_closed": selector_closed,
        "stage_absent": False,
        "stderr_eof_observed": eof["stderr"],
        "stdout_eof_observed": eof["stdout"],
    }
    if not all(value for key, value in cleanup.items() if key != "stage_absent"):
        issue = HOLD_CLEANUP
    return CaptureResult(
        process.pid,
        return_code,
        bytes(buffers["stdout"]),
        bytes(buffers["stderr"]),
        issue,
        cleanup,
    )


def _capture_started_process(
    process: subprocess.Popen[bytes],
    selector: selectors.BaseSelector,
    *,
    global_deadline: float,
) -> CaptureResult:
    if process.stdout is None or process.stderr is None:
        raise RuntimeError("missing captured pipe")
    streams = {"stdout": process.stdout, "stderr": process.stderr}
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    eof = {"stdout": False, "stderr": False}
    limits = {"stdout": MAX_CHILD_ACK_BYTES, "stderr": MAX_CHILD_STDERR_BYTES}
    process_deadline = min(
        time.monotonic() + CHILD_PROCESS_DEADLINE_SECONDS,
        global_deadline,
    )

    def read_ready(name: str) -> str | None:
        stream = streams[name]
        while True:
            try:
                chunk = os.read(stream.fileno(), 65_536)
            except BlockingIOError:
                return None
            if chunk == b"":
                eof[name] = True
                try:
                    selector.unregister(stream)
                except BaseException:
                    pass
                return None
            remaining = limits[name] + 1 - len(buffers[name])
            if remaining > 0:
                buffers[name].extend(chunk[:remaining])
            if len(buffers[name]) > limits[name]:
                return HOLD_REPEAT

    try:
        for name, stream in streams.items():
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        issue: str | None = None
        while True:
            for key, _ in selector.select(0.05):
                observed = read_ready(key.data)
                if observed is not None and issue is None:
                    issue = observed
            return_code = process.poll()
            if issue is None and time.monotonic() >= process_deadline:
                issue = HOLD_TIMEOUT
            if issue is not None or return_code is not None:
                break
        return _finish_started_process(
            process,
            selector,
            global_deadline=global_deadline,
            issue=issue,
            buffers=buffers,
            eof=eof,
        )
    except BaseException:
        return _finish_started_process(
            process,
            selector,
            global_deadline=global_deadline,
            issue=HOLD_REPEAT,
            buffers=buffers,
            eof=eof,
        )


def _capture_child(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    global_deadline: float,
) -> CaptureResult:
    if len(environment) != 5 or set(environment) != {
        "HOME",
        "LANG",
        "LC_ALL",
        "TMPDIR",
        "TZ",
    }:
        raise ReplayHold(HOLD_API)
    try:
        selector = selectors.DefaultSelector()
    except BaseException as error:
        raise ReplayHold(HOLD_REPEAT) from error
    try:
        _global_time_check(global_deadline)
    except ReplayHold:
        selector.close()
        raise
    try:
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            close_fds=True,
            start_new_session=True,
            bufsize=0,
        )
    except BaseException as error:
        selector.close()
        raise ReplayHold(HOLD_REPEAT) from error
    try:
        return _capture_started_process(
            process,
            selector,
            global_deadline=global_deadline,
        )
    except BaseException:
        return _finish_started_process(
            process,
            selector,
            global_deadline=global_deadline,
            issue=HOLD_CLEANUP,
        )


def _validate_semantic(
    raw: bytes,
    *,
    snapshot: Snapshot,
    verifier_sha256: str,
) -> dict[str, object]:
    semantic = _decode_canonical_object(raw, maximum_bytes=MAX_CHILD_SEMANTIC_BYTES)
    _exact_keys(semantic, CHILD_SEMANTIC_KEYS)
    if semantic["schema"] != CHILD_SEMANTIC_SCHEMA or semantic["status"] != CHILD_PASS_STATUS:
        raise ReplayHold(HOLD_REPEAT)
    if semantic["runtime"] != snapshot.body["runtime_versions"]:
        raise ReplayHold(HOLD_SOURCE)
    if semantic["verifier_staged_file_sha256_at_receipt"] != verifier_sha256:
        raise ReplayHold(HOLD_SOURCE)
    flags = semantic["flags"]
    if type(flags) is not dict:
        raise ReplayHold(HOLD_REPEAT)
    expected_flags = dict(REQUIRED_SEMANTIC_FLAGS)
    expected_flags.update(ADDITIONAL_SEMANTIC_FLAGS)
    if set(flags) != set(expected_flags):
        raise ReplayHold(HOLD_REPEAT)
    for key, expected in expected_flags.items():
        if flags.get(key) is not expected:
            raise ReplayHold(HOLD_REPEAT)
    for forbidden in (
        "repeat",
        "pid",
        "ppid",
        "pgid",
        "run_index",
        "launch_nonce",
        "peak_rss_bytes",
        "elapsed_monotonic_ns",
        "cleanup",
    ):
        if forbidden in semantic:
            raise ReplayHold(HOLD_REPEAT)
    frozen = semantic["frozen_sources"]
    frozen_keys = {
        "authority_sha256",
        "configuration_sha256",
        "design_sha256",
        "f0_core_sha256",
        "initial_stream_source_sha256",
        "operation_model_sha256",
        "partition_bundle_sha256",
        "partition_tree_sha256",
        "producer_sha256",
        "producer_test_sha256",
    }
    if type(frozen) is not dict or set(frozen) != frozen_keys:
        raise ReplayHold(HOLD_REPEAT)
    component_to_frozen = {
        "authority_bytes": "authority_sha256",
        "control_free_configuration_bytes": "configuration_sha256",
        "producer_source": "producer_sha256",
        "producer_test_source": "producer_test_sha256",
        "f0_core_source": "f0_core_sha256",
        "initial_stream_source": "initial_stream_source_sha256",
        "design_bytes": "design_sha256",
        "operation_model_bytes": "operation_model_sha256",
    }
    for component, key in component_to_frozen.items():
        expected = snapshot.component(component)["sha256"]
        if frozen.get(key) != expected:
            raise ReplayHold(HOLD_SOURCE)
    for value in frozen.values():
        _exact_sha(value)
    candidate = semantic["candidate"]
    candidate_keys = {
        "bundle_sha256",
        "family_relation_sha256",
        "factorization_contract_sha256",
        "partition_reference_graph_sha256",
        "tree_sha256",
    }
    if type(candidate) is not dict or set(candidate) != candidate_keys:
        raise ReplayHold(HOLD_REPEAT)
    for value in candidate.values():
        _exact_sha(value)
    if (
        type(semantic["contact_summary"]) is not dict
        or type(semantic["support_summary"]) is not dict
        or type(semantic["precision_bits"]) is not dict
        or type(semantic["support_policy_digests"]) is not dict
        or type(semantic["independent_partition_semantic_sha256s"]) is not list
    ):
        raise ReplayHold(HOLD_REPEAT)
    if semantic["precision_bits"] != {"primary": 384, "sentinel": 512}:
        raise ReplayHold(HOLD_REPEAT)
    for value in semantic["support_policy_digests"].values():
        _exact_sha(value)
    return semantic


def _validate_observation_and_ack(
    *,
    semantic_raw: bytes,
    observation_raw: bytes,
    stdout_raw: bytes,
    capture: CaptureResult,
    nonce: str,
    run_index: int,
    verifier_sha256: str,
    expected_status: str = CHILD_PASS_STATUS,
) -> tuple[dict[str, object], dict[str, object]]:
    observation = _decode_canonical_object(
        observation_raw, maximum_bytes=MAX_CHILD_OBSERVATION_BYTES
    )
    ack = _decode_canonical_object(stdout_raw, maximum_bytes=MAX_CHILD_ACK_BYTES)
    _exact_keys(observation, CHILD_OBSERVATION_KEYS)
    _exact_keys(ack, CHILD_ACK_KEYS)
    for value in (
        observation["elapsed_monotonic_ns"],
        observation["peak_rss_bytes"],
        observation["pid"],
        observation["ppid"],
        observation["pgid"],
        observation["run_index"],
        observation["semantic_receipt_byte_length"],
        ack["run_index"],
        ack["semantic_receipt_byte_length"],
        ack["observation_byte_length"],
    ):
        _exact_nonnegative_int(value)
    semantic_sha = _sha256(semantic_raw)
    observation_sha = _sha256(observation_raw)
    if (
        observation["schema"] != CHILD_OBSERVATION_SCHEMA
        or ack["schema"] != CHILD_ACK_SCHEMA
        or observation["status"] != expected_status
        or ack["status"] != expected_status
        or observation["launch_nonce"] != nonce
        or ack["launch_nonce"] != nonce
        or observation["run_index"] != run_index
        or ack["run_index"] != run_index
        or observation["pid"] != capture.pid
        or observation["pgid"] != capture.pid
        or observation["ppid"] != os.getpid()
        or observation["verifier_staged_file_sha256_at_observation"] != verifier_sha256
        or observation["semantic_receipt_byte_length"] != len(semantic_raw)
        or observation["semantic_receipt_sha256"] != semantic_sha
        or ack["semantic_receipt_byte_length"] != len(semantic_raw)
        or ack["semantic_receipt_sha256"] != semantic_sha
        or ack["observation_byte_length"] != len(observation_raw)
        or ack["observation_sha256"] != observation_sha
    ):
        raise ReplayHold(HOLD_REPEAT)
    _exact_nonnegative_int(observation["pid"], positive=True)
    _exact_nonnegative_int(observation["ppid"], positive=True)
    _exact_nonnegative_int(observation["pgid"], positive=True)
    return observation, ack


def _validate_child_wire(
    *,
    capture: CaptureResult,
    semantic_path: Path,
    observation_path: Path,
    nonce: str,
    run_index: int,
    snapshot: Snapshot,
    verifier_sha256: str,
) -> tuple[bytes, dict[str, object], bytes, dict[str, object]]:
    if capture.issue_status is not None:
        raise ReplayHold(capture.issue_status)
    if capture.stderr != b"":
        raise ReplayHold(HOLD_REPEAT)
    if capture.exit_code == 2:
        unbound: dict[str, object] | None = None
        try:
            parsed_stdout = _decode_canonical_object(
                capture.stdout, maximum_bytes=MAX_CHILD_ACK_BYTES
            )
            if set(parsed_stdout) == {"schema", "status"}:
                unbound = parsed_stdout
        except ReplayHold:
            pass
        if unbound is not None:
            if (
                unbound["schema"] == CHILD_UNBOUND_HOLD_ACK_SCHEMA
                and unbound["status"] == HOLD_API
                and not os.path.lexists(semantic_path)
                and not os.path.lexists(observation_path)
            ):
                raise ReplayHold(HOLD_API)
            raise ReplayHold(HOLD_REPEAT)
        semantic_raw = _read_published_stable(semantic_path, maximum_bytes=MAX_CHILD_SEMANTIC_BYTES)
        observation_raw = _read_published_stable(
            observation_path, maximum_bytes=MAX_CHILD_OBSERVATION_BYTES
        )
        semantic_hold = _decode_canonical_object(
            semantic_raw, maximum_bytes=MAX_CHILD_SEMANTIC_BYTES
        )
        _exact_keys(semantic_hold, {"schema", "status"})
        hold_status = semantic_hold["status"]
        if (
            semantic_hold["schema"] != CHILD_SEMANTIC_HOLD_SCHEMA
            or type(hold_status) is not str
            or hold_status not in HOLD_STATUSES
        ):
            raise ReplayHold(HOLD_REPEAT)
        _validate_observation_and_ack(
            semantic_raw=semantic_raw,
            observation_raw=observation_raw,
            stdout_raw=capture.stdout,
            capture=capture,
            nonce=nonce,
            run_index=run_index,
            verifier_sha256=verifier_sha256,
            expected_status=hold_status,
        )
        raise ReplayHold(hold_status)
    if capture.exit_code != 0:
        raise ReplayHold(HOLD_REPEAT)
    semantic_raw = _read_published_stable(semantic_path, maximum_bytes=MAX_CHILD_SEMANTIC_BYTES)
    observation_raw = _read_published_stable(
        observation_path, maximum_bytes=MAX_CHILD_OBSERVATION_BYTES
    )
    semantic = _validate_semantic(
        semantic_raw,
        snapshot=snapshot,
        verifier_sha256=verifier_sha256,
    )
    observation, _ = _validate_observation_and_ack(
        semantic_raw=semantic_raw,
        observation_raw=observation_raw,
        stdout_raw=capture.stdout,
        capture=capture,
        nonce=nonce,
        run_index=run_index,
        verifier_sha256=verifier_sha256,
    )
    return semantic_raw, semantic, observation_raw, observation


def _operation_model_preflight(report_root: Path) -> None:
    raw = _read_regular_stable(
        report_root / OPERATION_MODEL_PATH,
        maximum_bytes=MAX_FILE_COMPONENT_BYTES,
    )
    if _sha256(raw) != OPERATION_MODEL_SHA256:
        raise ReplayHold(HOLD_SOURCE)
    try:
        model = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ReplayHold(HOLD_SOURCE) from error
    if (
        type(model) is not dict
        or model.get("schema") != OPERATION_MODEL_SCHEMA
        or model.get("replay", {}).get("input_snapshot_components") != list(COMPONENT_ORDER)
        or model.get("replay", {}).get("repeat_count") != 2
        or model.get("replay", {}).get("serialized") is not True
        or model.get("outer", {}).get("global_monotonic_deadline_seconds") != OUTER_DEADLINE_SECONDS
        or model.get("child", {}).get("process_deadline_seconds") != CHILD_PROCESS_DEADLINE_SECONDS
    ):
        raise ReplayHold(HOLD_SOURCE)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_cli(argv: Sequence[str]) -> tuple[Path, Path, ReceiptTarget]:
    if len(argv) != 6:
        raise ReplayHold(HOLD_API)
    parsed: dict[str, str] = {}
    for index in range(0, len(argv), 2):
        name, value = argv[index : index + 2]
        if (
            name not in {"--report-root", "--bundle", "--outer-receipt"}
            or name in parsed
            or not value
        ):
            raise ReplayHold(HOLD_API)
        parsed[name] = value
    if set(parsed) != {"--report-root", "--bundle", "--outer-receipt"}:
        raise ReplayHold(HOLD_API)
    supplied_report = Path(parsed["--report-root"])
    supplied_bundle = Path(parsed["--bundle"])
    supplied_receipt = Path(parsed["--outer-receipt"])
    if not all(path.is_absolute() for path in (supplied_report, supplied_bundle, supplied_receipt)):
        raise ReplayHold(HOLD_API)
    try:
        report_root = supplied_report.resolve(strict=True)
        bundle_root = supplied_bundle.resolve(strict=True)
        receipt_parent = supplied_receipt.parent.resolve(strict=True)
    except OSError as error:
        raise ReplayHold(HOLD_API) from error
    if not report_root.is_dir() or not bundle_root.is_dir():
        raise ReplayHold(HOLD_API)
    if supplied_receipt.name in {"", ".", ".."}:
        raise ReplayHold(HOLD_API)
    receipt_path = Path(os.path.abspath(receipt_parent / supplied_receipt.name))
    if os.path.lexists(receipt_path):
        raise ReplayHold(HOLD_API)
    if _is_within(receipt_path, report_root) or _is_within(receipt_path, bundle_root):
        raise ReplayHold(HOLD_API)
    try:
        parent_metadata = os.lstat(receipt_path.parent)
    except OSError as error:
        raise ReplayHold(HOLD_API) from error
    if (
        not stat.S_ISDIR(parent_metadata.st_mode)
        or stat.S_ISLNK(parent_metadata.st_mode)
        or parent_metadata.st_uid != os.getuid()
        or stat.S_IMODE(parent_metadata.st_mode) != 0o700
    ):
        raise ReplayHold(HOLD_API)
    return (
        report_root,
        bundle_root,
        ReceiptTarget(receipt_path, _directory_identity(parent_metadata)),
    )


def _prelaunch_time_check(
    *,
    outer_started: float,
    global_deadline: float,
    completed_child_seconds: float,
    remaining_runs: int,
) -> None:
    now = time.monotonic()
    total_elapsed = now - outer_started
    nonchild_elapsed = max(0.0, total_elapsed - completed_child_seconds)
    reserve_remaining = max(0.0, OUTER_NONCHILD_RESERVE_SECONDS - nonchild_elapsed)
    required = remaining_runs * CHILD_PROCESS_DEADLINE_SECONDS + reserve_remaining
    if global_deadline - now + 1e-9 < required:
        raise ReplayHold(HOLD_TIMEOUT)


def _global_time_check(global_deadline: float) -> None:
    if time.monotonic() >= global_deadline:
        raise ReplayHold(HOLD_TIMEOUT)


def _execute_run(
    *,
    run_index: int,
    report_root: Path,
    bundle_root: Path,
    runtime_chain: LinkChain,
    extension_chain: LinkChain,
    reference_raw: bytes | None,
    outer_started: float,
    completed_child_seconds: float,
    remaining_runs: int,
    global_deadline: float,
) -> tuple[RunResult, bytes, float]:
    stage: Path | None = None
    capture: CaptureResult | None = None
    child_elapsed = 0.0
    try:
        current_runtime_chain = _lstat_chain(runtime_chain.launcher)
        current_extension_chain = _gmpy2_link_chain()
        if current_runtime_chain != runtime_chain or current_extension_chain != extension_chain:
            raise ReplayHold(HOLD_SOURCE)
        origin_specs = _component_specs(
            report_root, bundle_root, None, runtime_chain, extension_chain
        )
        origin = _snapshot(origin_specs, staged=False)
        if origin.component("independent_verifier_source")["sha256"] != EXPECTED_VERIFIER_SHA256:
            raise ReplayHold(HOLD_SOURCE)
        if reference_raw is not None and origin.raw != reference_raw:
            raise ReplayHold(HOLD_REPEAT)
        stage = _new_stage((report_root, bundle_root), run_index)
        staged_specs = _component_specs(
            report_root, bundle_root, stage, runtime_chain, extension_chain
        )
        _copy_staged_components(staged_specs, origin)
        stage_post_copy = _snapshot(staged_specs, staged=True)
        if stage_post_copy.raw != origin.raw:
            raise ReplayHold(HOLD_REPEAT)
        _make_inputs_read_only(stage / "inputs")
        stage_pre_launch = _snapshot(staged_specs, staged=True, require_read_only=True)
        if stage_pre_launch.raw != origin.raw:
            raise ReplayHold(HOLD_REPEAT)

        nonce = secrets.token_hex(32)
        if _NONCE_RE.fullmatch(nonce) is None:
            raise ReplayHold(HOLD_API)
        semantic_path = stage / "outputs" / "semantic.json"
        observation_path = stage / "outputs" / "child_observation.json"
        staged_report = stage / "inputs" / "report"
        staged_candidate = stage / "inputs" / "candidate_tree"
        staged_verifier = staged_report / VERIFIER_PATH
        command = (
            os.fspath(runtime_chain.launcher),
            "-I",
            "-B",
            os.fspath(staged_verifier),
            "--report-root",
            os.fspath(staged_report),
            "--bundle",
            os.fspath(staged_candidate),
            "--semantic-receipt",
            os.fspath(semantic_path),
            "--observation",
            os.fspath(observation_path),
            "--launch-nonce",
            nonce,
            "--run-index",
            str(run_index),
        )
        _prelaunch_time_check(
            outer_started=outer_started,
            global_deadline=global_deadline,
            completed_child_seconds=completed_child_seconds,
            remaining_runs=remaining_runs,
        )
        child_started = time.monotonic()
        capture = _capture_child(
            command,
            cwd=stage,
            environment=_child_environment(stage),
            global_deadline=global_deadline,
        )
        child_elapsed = time.monotonic() - child_started
        if capture.issue_status is not None or not all(
            value for key, value in capture.cleanup.items() if key != "stage_absent"
        ):
            raise ReplayHold(capture.issue_status or HOLD_CLEANUP)
        if _lstat_chain(runtime_chain.launcher) != runtime_chain:
            raise ReplayHold(HOLD_SOURCE)
        if _gmpy2_link_chain() != extension_chain:
            raise ReplayHold(HOLD_SOURCE)
        _global_time_check(global_deadline)
        stage_post_exit = _snapshot(staged_specs, staged=True, require_read_only=True)
        if stage_post_exit.raw != origin.raw:
            raise ReplayHold(HOLD_REPEAT)
        verifier_sha = origin.component("independent_verifier_source")["sha256"]
        semantic_raw, semantic, observation_raw, observation = _validate_child_wire(
            capture=capture,
            semantic_path=semantic_path,
            observation_path=observation_path,
            nonce=nonce,
            run_index=run_index,
            snapshot=origin,
            verifier_sha256=verifier_sha,
        )
        capture.cleanup["stage_absent"] = _remove_stage(stage)
        stage = None
        if not all(capture.cleanup.values()):
            raise ReplayHold(HOLD_CLEANUP)
        snapshot_sha256s = {
            "origin_pre_copy": origin.digest,
            "stage_post_copy": stage_post_copy.digest,
            "stage_pre_launch": stage_pre_launch.digest,
            "stage_post_exit": stage_post_exit.digest,
        }
        if set(snapshot_sha256s) != SNAPSHOT_PHASE_KEYS or len(set(snapshot_sha256s.values())) != 1:
            raise ReplayHold(HOLD_REPEAT)
        record = {
            "cleanup": dict(capture.cleanup),
            "exit_code": capture.exit_code,
            "launch_nonce": nonce,
            "observation_byte_length": len(observation_raw),
            "observation_sha256": _sha256(observation_raw),
            "pgid": observation["pgid"],
            "pid": capture.pid,
            "run_index": run_index,
            "semantic_receipt_byte_length": len(semantic_raw),
            "semantic_receipt_sha256": _sha256(semantic_raw),
            "snapshot_sha256s": snapshot_sha256s,
            "stderr_byte_length": len(capture.stderr),
            "stderr_sha256": _sha256(capture.stderr),
            "stdout_byte_length": len(capture.stdout),
            "stdout_sha256": _sha256(capture.stdout),
        }
        _exact_keys(record, OUTER_CHILD_RUN_KEYS)
        return RunResult(record, semantic_raw, semantic), origin.raw, child_elapsed
    except ReplayHold:
        raise
    finally:
        if stage is not None:
            removed = _remove_stage(stage)
            if capture is not None:
                capture.cleanup["stage_absent"] = removed
            if not removed:
                raise ReplayHold(HOLD_CLEANUP)


def _outer_flags(semantic_flags: object) -> dict[str, object]:
    if type(semantic_flags) is not dict:
        raise ReplayHold(HOLD_REPEAT)
    result = dict(semantic_flags)
    result.update(OUTER_ONLY_FLAGS)
    for key, value in REQUIRED_SEMANTIC_FLAGS.items():
        if result.get(key) is not value:
            raise ReplayHold(HOLD_REPEAT)
    return result


def _build_outer_receipt(runs: Sequence[RunResult], snapshot: Snapshot) -> dict[str, object]:
    if len(runs) != 2 or [run.record["run_index"] for run in runs] != [0, 1]:
        raise ReplayHold(HOLD_REPEAT)
    if runs[0].semantic_raw != runs[1].semantic_raw:
        raise ReplayHold(HOLD_REPEAT)
    pids = [run.record["pid"] for run in runs]
    if len(set(pids)) != 2:
        raise ReplayHold(HOLD_REPEAT)
    semantic_raw = runs[0].semantic_raw
    receipt = {
        "child_runs": [run.record for run in runs],
        "flags": _outer_flags(runs[0].semantic["flags"]),
        "input_snapshot_sha256": snapshot.digest,
        "operation_model_sha256": OPERATION_MODEL_SHA256,
        "runtime": snapshot.body["runtime_versions"],
        "schema": OUTER_RECEIPT_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": _sha256(semantic_raw),
        "status": OUTER_PASS_STATUS,
        "verifier_source_sha256": snapshot.component("independent_verifier_source")["sha256"],
    }
    _exact_keys(receipt, OUTER_RECEIPT_KEYS)
    return receipt


def _read_published_at(
    directory_descriptor: int,
    name: str,
    *,
    maximum_bytes: int,
    expected_identity: tuple[int, int, int, int, int, int],
) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    try:
        descriptor = os.open(name, flags, dir_fd=directory_descriptor)
    except OSError as error:
        raise ReplayHold(HOLD_REPEAT) from error
    try:
        before = os.fstat(descriptor)
        if (
            _published_file_identity(before) != expected_identity
            or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size < 0
            or before.st_size > maximum_bytes
        ):
            raise ReplayHold(HOLD_REPEAT)
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1 << 20, remaining))
            if not chunk:
                raise ReplayHold(HOLD_REPEAT)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1) != b"":
            raise ReplayHold(HOLD_REPEAT)
        if _published_file_identity(os.fstat(descriptor)) != expected_identity:
            raise ReplayHold(HOLD_REPEAT)
    finally:
        if not _close_descriptor_confirmed(descriptor):
            raise ReplayHold(HOLD_CLEANUP)
    try:
        lexical = os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except OSError as error:
        raise ReplayHold(HOLD_REPEAT) from error
    if _published_file_identity(lexical) != expected_identity:
        raise ReplayHold(HOLD_REPEAT)
    return b"".join(chunks)


def _publication_parent_stable(publication: PublishedReceipt) -> bool:
    try:
        descriptor_metadata = os.fstat(publication.directory_descriptor)
        lexical_metadata = os.lstat(publication.target.path.parent)
    except OSError:
        return False
    return (
        stat.S_ISDIR(descriptor_metadata.st_mode)
        and not stat.S_ISLNK(lexical_metadata.st_mode)
        and _directory_identity(descriptor_metadata)
        == publication.target.parent_identity
        == _directory_identity(lexical_metadata)
    )


def _close_descriptor_confirmed(descriptor: int) -> bool:
    for _ in range(3):
        try:
            os.close(descriptor)
            return True
        except OSError:
            try:
                os.fstat(descriptor)
            except OSError as probe_error:
                if probe_error.errno == errno.EBADF:
                    return True
    return False


def _cleanup_publication(publication: PublishedReceipt) -> bool:
    """Remove only the exact regular single-link inode created by this process."""
    if publication.closed:
        return False
    removed = False
    try:
        current = os.stat(
            publication.target.path.name,
            dir_fd=publication.directory_descriptor,
            follow_symlinks=False,
        )
        if _published_file_identity(current) != publication.file_identity:
            return False
        os.unlink(
            publication.target.path.name,
            dir_fd=publication.directory_descriptor,
        )
        try:
            os.stat(
                publication.target.path.name,
                dir_fd=publication.directory_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            removed = True
        except OSError:
            removed = False
    except OSError:
        removed = False
    finally:
        publication.closed = _close_descriptor_confirmed(publication.directory_descriptor)
        if not publication.closed:
            removed = False
    return removed


def _close_publication(publication: PublishedReceipt) -> bool:
    if publication.closed:
        return False
    try:
        stable = _publication_parent_stable(publication) and (
            _read_published_at(
                publication.directory_descriptor,
                publication.target.path.name,
                maximum_bytes=MAX_OUTER_RECEIPT_BYTES,
                expected_identity=publication.file_identity,
            )
            == publication.raw
        )
    except ReplayHold:
        stable = False
    if not stable:
        _cleanup_publication(publication)
        return False
    try:
        os.close(publication.directory_descriptor)
    except OSError:
        try:
            os.fstat(publication.directory_descriptor)
        except OSError as probe_error:
            if probe_error.errno == errno.EBADF:
                publication.closed = True
                _cleanup_closed_publication(publication)
                return False
        _cleanup_publication(publication)
        return False
    publication.closed = True
    return True


def _cleanup_closed_publication(publication: PublishedReceipt) -> bool:
    """Reopen the frozen parent and remove only the fully matched owned file."""
    if not publication.closed:
        return _cleanup_publication(publication)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW | os.O_DIRECTORY
    try:
        directory_descriptor = os.open(publication.target.path.parent, flags)
    except OSError:
        return False
    removed = False
    try:
        parent_fd = os.fstat(directory_descriptor)
        parent_path = os.lstat(publication.target.path.parent)
        parent_matches = (
            _directory_identity(parent_fd)
            == publication.target.parent_identity
            == _directory_identity(parent_path)
        )
        if parent_matches:
            try:
                current = os.stat(
                    publication.target.path.name,
                    dir_fd=directory_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                removed = True
            else:
                file_matches = (
                    _published_file_identity(current) == publication.file_identity
                    and _read_published_at(
                        directory_descriptor,
                        publication.target.path.name,
                        maximum_bytes=MAX_OUTER_RECEIPT_BYTES,
                        expected_identity=publication.file_identity,
                    )
                    == publication.raw
                )
                if file_matches:
                    os.unlink(publication.target.path.name, dir_fd=directory_descriptor)
                    try:
                        os.stat(
                            publication.target.path.name,
                            dir_fd=directory_descriptor,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        removed = True
                    except OSError:
                        removed = False
    except (OSError, ReplayHold):
        removed = False
    finally:
        if not _close_descriptor_confirmed(directory_descriptor):
            removed = False
    return removed


def _publish_exclusive(
    target: ReceiptTarget,
    raw: bytes,
    *,
    maximum_bytes: int,
    global_deadline: float | None = None,
) -> PublishedReceipt:
    if global_deadline is not None:
        _global_time_check(global_deadline)
    if (
        len(raw) > maximum_bytes
        or os.path.lexists(target.path)
        or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
    ):
        raise ReplayHold(HOLD_API)
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW | os.O_DIRECTORY
    directory_descriptor: int | None = None
    try:
        directory_descriptor = os.open(target.path.parent, directory_flags)
        parent_descriptor_metadata = os.fstat(directory_descriptor)
        parent_lexical_metadata = os.lstat(target.path.parent)
    except OSError as error:
        if directory_descriptor is not None:
            if not _close_descriptor_confirmed(directory_descriptor):
                raise ReplayHold(HOLD_CLEANUP) from error
        raise ReplayHold(HOLD_API) from error
    assert directory_descriptor is not None
    if (
        not stat.S_ISDIR(parent_descriptor_metadata.st_mode)
        or stat.S_ISLNK(parent_lexical_metadata.st_mode)
        or parent_descriptor_metadata.st_uid != os.getuid()
        or parent_lexical_metadata.st_uid != os.getuid()
        or stat.S_IMODE(parent_descriptor_metadata.st_mode) != 0o700
        or stat.S_IMODE(parent_lexical_metadata.st_mode) != 0o700
        or not (
            _directory_identity(parent_descriptor_metadata)
            == target.parent_identity
            == _directory_identity(parent_lexical_metadata)
        )
    ):
        if not _close_descriptor_confirmed(directory_descriptor):
            raise ReplayHold(HOLD_CLEANUP)
        raise ReplayHold(HOLD_API)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    descriptor: int | None = None
    publication: PublishedReceipt | None = None
    created_exclusive = False
    created_metadata: os.stat_result | None = None
    try:
        descriptor = os.open(
            target.path.name,
            flags,
            0o600,
            dir_fd=directory_descriptor,
        )
        created_exclusive = True
        created_metadata = os.fstat(descriptor)
        if not stat.S_ISREG(created_metadata.st_mode) or created_metadata.st_nlink != 1:
            raise ReplayHold(HOLD_API)
        publication = PublishedReceipt(
            target,
            directory_descriptor,
            _published_file_identity(created_metadata),
            raw,
        )
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ReplayHold(HOLD_API)
            view = view[written:]
            publication.file_identity = _published_file_identity(os.fstat(descriptor))
        os.fsync(descriptor)
        if global_deadline is not None:
            _global_time_check(global_deadline)
        final_metadata = os.fstat(descriptor)
        publication.file_identity = _published_file_identity(final_metadata)
        if (
            not stat.S_ISREG(final_metadata.st_mode)
            or final_metadata.st_nlink != 1
            or final_metadata.st_size != len(raw)
        ):
            raise ReplayHold(HOLD_REPEAT)
        if not _close_descriptor_confirmed(descriptor):
            raise ReplayHold(HOLD_CLEANUP)
        descriptor = None
        first = _read_published_at(
            directory_descriptor,
            target.path.name,
            maximum_bytes=maximum_bytes,
            expected_identity=publication.file_identity,
        )
        second = _read_published_at(
            directory_descriptor,
            target.path.name,
            maximum_bytes=maximum_bytes,
            expected_identity=publication.file_identity,
        )
        if global_deadline is not None:
            _global_time_check(global_deadline)
        if first != raw or second != raw or not _publication_parent_stable(publication):
            raise ReplayHold(HOLD_REPEAT)
        return publication
    except BaseException as error:
        if descriptor is not None:
            if publication is None and created_exclusive:
                try:
                    metadata = created_metadata or os.fstat(descriptor)
                    lexical = os.stat(
                        target.path.name,
                        dir_fd=directory_descriptor,
                        follow_symlinks=False,
                    )
                    if _published_file_identity(metadata) == _published_file_identity(lexical):
                        publication = PublishedReceipt(
                            target,
                            directory_descriptor,
                            _published_file_identity(metadata),
                            raw,
                        )
                except (OSError, MemoryError):
                    publication = None
            if publication is not None:
                try:
                    publication.file_identity = _published_file_identity(os.fstat(descriptor))
                except OSError:
                    pass
            descriptor_closed = _close_descriptor_confirmed(descriptor)
        else:
            descriptor_closed = True
        if publication is not None:
            if not _cleanup_publication(publication):
                raise ReplayHold(HOLD_CLEANUP) from error
        else:
            if not _close_descriptor_confirmed(directory_descriptor):
                raise ReplayHold(HOLD_CLEANUP) from error
            if created_exclusive:
                raise ReplayHold(HOLD_CLEANUP) from error
        if not descriptor_closed:
            raise ReplayHold(HOLD_CLEANUP) from error
        if isinstance(error, ReplayHold):
            raise
        raise ReplayHold(HOLD_API) from error


def run_replay(
    report_root: Path,
    bundle_root: Path,
    receipt_target: ReceiptTarget,
) -> tuple[bytes, PublishedReceipt, float]:
    outer_started = time.monotonic()
    global_deadline = outer_started + OUTER_DEADLINE_SECONDS
    _operation_model_preflight(report_root)
    runtime_chain = _lstat_chain(Path(sys.executable))
    extension_chain = _gmpy2_link_chain()
    initial_specs = _component_specs(report_root, bundle_root, None, runtime_chain, extension_chain)
    initial_snapshot = _snapshot(initial_specs, staged=False)
    if (
        initial_snapshot.component("independent_verifier_source")["sha256"]
        != EXPECTED_VERIFIER_SHA256
    ):
        raise ReplayHold(HOLD_SOURCE)
    runs: list[RunResult] = []
    reference_raw: bytes | None = initial_snapshot.raw
    completed_child_seconds = 0.0
    for run_index in (0, 1):
        _prelaunch_time_check(
            outer_started=outer_started,
            global_deadline=global_deadline,
            completed_child_seconds=completed_child_seconds,
            remaining_runs=2 - run_index,
        )
        run, observed_raw, elapsed = _execute_run(
            run_index=run_index,
            report_root=report_root,
            bundle_root=bundle_root,
            runtime_chain=runtime_chain,
            extension_chain=extension_chain,
            reference_raw=reference_raw,
            outer_started=outer_started,
            completed_child_seconds=completed_child_seconds,
            remaining_runs=2 - run_index,
            global_deadline=global_deadline,
        )
        completed_child_seconds += elapsed
        if observed_raw != initial_snapshot.raw:
            raise ReplayHold(HOLD_REPEAT)
        runs.append(run)
    _global_time_check(global_deadline)
    receipt = _build_outer_receipt(runs, initial_snapshot)
    receipt_raw = _canonical_json_bytes(receipt)
    _global_time_check(global_deadline)
    publication = _publish_exclusive(
        receipt_target,
        receipt_raw,
        maximum_bytes=MAX_OUTER_RECEIPT_BYTES,
        global_deadline=global_deadline,
    )
    try:
        _global_time_check(global_deadline)
        acknowledgement = {
            "outer_receipt_byte_length": len(publication.raw),
            "outer_receipt_sha256": _sha256(publication.raw),
            "schema": OUTER_ACK_SCHEMA,
            "status": OUTER_PASS_STATUS,
        }
        acknowledgement_raw = _canonical_json_bytes(acknowledgement)
        _global_time_check(global_deadline)
    except BaseException as error:
        if not _cleanup_publication(publication):
            raise ReplayHold(HOLD_CLEANUP) from error
        if isinstance(error, ReplayHold):
            raise
        raise ReplayHold(HOLD_API) from error
    if not _close_publication(publication):
        raise ReplayHold(HOLD_CLEANUP)
    try:
        _global_time_check(global_deadline)
    except ReplayHold as error:
        if not _cleanup_closed_publication(publication):
            raise ReplayHold(HOLD_CLEANUP) from error
        raise
    return acknowledgement_raw, publication, global_deadline


def _hold_ack(status: str) -> bytes:
    return _canonical_json_bytes(
        {
            "schema": OUTER_HOLD_ACK_SCHEMA,
            "status": status if status in HOLD_STATUSES else HOLD_API,
        }
    )


def _main(argv: Sequence[str] | None = None) -> int:
    publication: PublishedReceipt | None = None
    try:
        report_root, bundle_root, receipt_target = _validate_cli(
            list(sys.argv[1:] if argv is None else argv)
        )
        acknowledgement, publication, global_deadline = run_replay(
            report_root, bundle_root, receipt_target
        )
    except ReplayHold as error:
        acknowledgement = _hold_ack(error.status)
    except Exception:
        acknowledgement = _hold_ack(HOLD_API)
    if publication is not None:
        try:
            _global_time_check(global_deadline)
        except ReplayHold as error:
            status = error.status
            if not _cleanup_closed_publication(publication):
                status = HOLD_CLEANUP
            publication = None
            acknowledgement = _hold_ack(status)
    try:
        sys.stdout.buffer.write(acknowledgement)
        sys.stdout.buffer.flush()
    except Exception:
        if publication is not None:
            _cleanup_closed_publication(publication)
        return 2
    return 0 if json.loads(acknowledgement)["status"] == OUTER_PASS_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(_main())
