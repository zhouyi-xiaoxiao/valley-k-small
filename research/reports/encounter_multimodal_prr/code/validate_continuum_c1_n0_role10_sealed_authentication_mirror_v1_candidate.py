"""Source-separated validator for the role-10 sealed authentication mirror.

Validation needs only the sealed mirror and the four accepted immutable
authorities (member-v4, configuration, factorization-v2, and initial bundle).
It deliberately does not open any of the original 40 writable source paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Final, NoReturn, Sequence

CODE: Final = Path(__file__).resolve().parent
REPORT: Final = CODE.parent
ARTIFACT_NAME: Final = "continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
DEFAULT_MIRROR: Final = REPORT / "artifacts/data" / ARTIFACT_NAME

SCHEMA: Final = "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
STATUS: Final = (
    "RESULT_BLIND_SEALED_AUTHENTICATION_CLOSURE_MIRROR_CANDIDATE_ONLY_"
    "NOT_EXTERNAL_COMMITMENT_NOT_REPLAY"
)
MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
MEMBER_STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
CONFIGURATION_STATUS: Final = "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_STATUS: Final = (
    "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_NOT_EXTERNALLY_"
    "COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
)
INITIAL_BUNDLE_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
INITIAL_BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
INITIAL_GEOMETRY_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"

MEMBER_RELATIVE: Final = PurePosixPath(
    "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
)
CONFIGURATION_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
FACTORIZATION_RELATIVE: Final = PurePosixPath(
    "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)
INITIAL_BUNDLE_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)
INITIAL_BUNDLE_DIRECTORY: Final = INITIAL_BUNDLE_RELATIVE.parent
INITIAL_GEOMETRY_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_initial_analytic_source_v1.json"
)

MEMBER_SHA256: Final = "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
INITIAL_BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
INITIAL_GEOMETRY_SHA256: Final = "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
CONFIGURATION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-configuration-row-inventory-v1"
PARTITION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-partition-inventory-v1"
CONFIGURATION_INVENTORY_SHA256: Final = (
    "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
)
PARTITION_INVENTORY_SHA256: Final = (
    "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
)
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
EXPECTED_CONFIGURATION_COUNT: Final = 12
EXPECTED_PARTITION_COUNT: Final = 36
EXPECTED_ENTRY_COUNT: Final = 40

CLAIM_KEYS: Final = (
    "candidate_authoritative",
    "external_predecessor_commitment_present",
    "numerical_killing_artifact_present",
    "ordered_roles_8_10_replay_executed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "role10_acceptance_receipt_present",
    "science_executed",
    "submission_eligible",
)
LINEAGE_ROLES: Final = (
    ("configuration_design", "design_path", "design_sha256"),
    ("configuration_implementation", "implementation_path", "implementation_sha256"),
    ("configuration_test", "test_path", "test_sha256"),
)
TOP_LEVEL_KEYS: Final = {
    "accepted_authorities",
    "claim_boundary",
    "coverage",
    "entry_count",
    "entries",
    "exclusions",
    "inventory_digests",
    "mirrored_source_pin",
    "schema",
    "status",
}
BASE_ENTRY_KEYS: Final = {
    "byte_length",
    "mirror_relative_path",
    "ordinal",
    "semantic_role",
    "sha256",
    "source_report_relative_path",
}
PARTITION_ENTRY_KEYS: Final = BASE_ENTRY_KEYS | {
    "configuration_index",
    "configuration_label",
    "coordinate",
}
FORBIDDEN_REPORT_RELATIVE_FRAGMENTS: Final = (
    "physical_production_killing_geometry",
    "candidate_native_killing_factor_geometry",
    "/outputs/",
    "/receipts/",
)

_AFTER_MIRROR_OPEN_HOOK: Callable[[PurePosixPath, int], None] | None = None


class MirrorValidationError(RuntimeError):
    """Fail-closed mirror validation error."""


def _fail(message: str) -> NoReturn:
    raise MirrorValidationError(message)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _domain_digest(domain: str, value: Any) -> str:
    return _sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value))


def _safe_relative(value: str | PurePosixPath, label: str) -> PurePosixPath:
    if type(value) not in {str, PurePosixPath}:
        _fail(f"{label}: path is not text")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in str(value)
    ):
        _fail(f"{label}: unsafe relative path")
    return path


def _open_absolute_directory(path: Path) -> int:
    path = path.absolute()
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open("/", flags)
    try:
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _open_relative_directory(root_fd: int, parts: Sequence[str]) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.dup(root_fd)
    try:
        for part in parts:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _snapshot(
    root_fd: int,
    relative: PurePosixPath,
    *,
    authority: bool,
    invoke_hook: bool = False,
) -> bytes:
    relative = _safe_relative(relative, "snapshot")
    parent_fd = _open_relative_directory(root_fd, relative.parts[:-1])
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(relative.name, flags, dir_fd=parent_fd)
        try:
            before = os.fstat(fd)
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) != 0o444
            ):
                kind = "authority" if authority else "mirror"
                _fail(f"{relative}: {kind} file mode/type/link-count mismatch")
            if invoke_hook and _AFTER_MIRROR_OPEN_HOOK is not None:
                _AFTER_MIRROR_OPEN_HOOK(relative, fd)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1 << 20)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(fd)
            path_after = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                _identity(before) != _identity(after)
                or _identity(before) != _identity(path_after)
                or not stat.S_ISREG(path_after.st_mode)
            ):
                _fail(f"{relative}: file changed or was replaced while read")
            return b"".join(chunks)
        finally:
            os.close(fd)
    except OSError as error:
        _fail(f"{relative}: secure open failed: {error}")
    finally:
        os.close(parent_fd)


def _decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(f"{label}: invalid ASCII JSON: {error}")
    if type(value) is not dict or canonical_bytes(value) != raw:
        _fail(f"{label}: JSON is not canonical")
    return value


def _decode_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(f"{label}: invalid ASCII JSON: {error}")
    if type(value) is not dict:
        _fail(f"{label}: JSON root is not an object")
    return value


def _configuration_inventory(configuration: dict[str, Any]) -> list[dict[str, Any]]:
    rows = configuration.get("configurations")
    if type(rows) is not list or len(rows) != EXPECTED_CONFIGURATION_COUNT:
        _fail("configuration: row cardinality mismatch")
    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if type(row) is not dict:
            _fail("configuration: row type mismatch")
        records.append(
            {
                "configuration_index": index,
                "configuration_label": row.get("label"),
                "configuration_row_canonical_sha256": _sha256(canonical_bytes(row)),
                "expected_states": row.get("expected_states"),
                "shape": row.get("shape"),
            }
        )
    return records


def _partition_inventory(member: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = member.get("n0_sequence_bindings")
    if type(bindings) is not list or len(bindings) != EXPECTED_CONFIGURATION_COUNT:
        _fail("member-v4: binding cardinality mismatch")
    records: list[dict[str, Any]] = []
    for index, binding in enumerate(bindings):
        if type(binding) is not dict or binding.get("configuration_index") != index:
            _fail("member-v4: binding order mismatch")
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != len(COORDINATES):
            _fail("member-v4: axis cardinality mismatch")
        for coordinate, axis in zip(COORDINATES, axes, strict=True):
            if type(axis) is not dict or axis.get("coordinate") != coordinate:
                _fail("member-v4: coordinate order mismatch")
            records.append(
                {
                    "alignment": axis.get("alignment"),
                    "cell_count": axis.get("cell_count"),
                    "configuration_index": index,
                    "configuration_label": binding.get("authority_label"),
                    "coordinate": coordinate,
                    "partition_report_relative_path": axis.get("partition_report_relative_path"),
                    "partition_schema": axis.get("partition_schema"),
                    "partition_sha256": axis.get("partition_sha256"),
                    "periodic": axis.get("periodic"),
                    "refinement_family_id": binding.get("refinement_family_id"),
                    "refinement_member_id": binding.get("refinement_member_id"),
                    "sequence_id": binding.get("sequence_id"),
                }
            )
    return records


def _authority_pin(
    relative: PurePosixPath, schema: str, status: str | None, sha256: str
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "path": relative.as_posix(),
        "schema": schema,
        "sha256": sha256,
    }
    if status is not None:
        value["status"] = status
    return value


def _load_authorities(authority_root_fd: int) -> tuple[dict[str, Any], ...]:
    definitions = (
        (MEMBER_RELATIVE, MEMBER_SHA256, MEMBER_SCHEMA, MEMBER_STATUS, "member-v4"),
        (
            CONFIGURATION_RELATIVE,
            CONFIGURATION_SHA256,
            CONFIGURATION_SCHEMA,
            CONFIGURATION_STATUS,
            "configuration",
        ),
        (
            FACTORIZATION_RELATIVE,
            FACTORIZATION_SHA256,
            FACTORIZATION_SCHEMA,
            FACTORIZATION_STATUS,
            "factorization-v2",
        ),
        (
            INITIAL_BUNDLE_RELATIVE,
            INITIAL_BUNDLE_SHA256,
            INITIAL_BUNDLE_SCHEMA,
            INITIAL_BUNDLE_STATUS,
            "initial bundle",
        ),
    )
    values: list[dict[str, Any]] = []
    for relative, expected_sha, schema, status, label in definitions:
        raw = _snapshot(authority_root_fd, relative, authority=True)
        if _sha256(raw) != expected_sha:
            _fail(f"{label}: accepted SHA-256 mismatch")
        value = _decode_canonical(raw, label)
        if value.get("schema") != schema or value.get("status") != status:
            _fail(f"{label}: schema/status mismatch")
        values.append(value)
    member, configuration, factorization, initial_bundle = values
    if member.get("member_identity_sha256") != MEMBER_IDENTITY_SHA256:
        _fail("member-v4: identity mismatch")
    if (
        configuration.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or initial_bundle.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or initial_bundle.get("configuration_sha256") != CONFIGURATION_SHA256
    ):
        _fail("configuration/initial-bundle join mismatch")
    source_pins = factorization.get("source_pins")
    expected_pins = {
        "configuration_source": {
            "path": CONFIGURATION_RELATIVE.as_posix(),
            "schema": CONFIGURATION_SCHEMA,
            "sha256": CONFIGURATION_SHA256,
        },
        "initial_partition_bundle": {
            "path": INITIAL_BUNDLE_RELATIVE.as_posix(),
            "schema": INITIAL_BUNDLE_SCHEMA,
            "sha256": INITIAL_BUNDLE_SHA256,
        },
    }
    if type(source_pins) is not dict:
        _fail("factorization-v2: source pins missing")
    for key, expected in expected_pins.items():
        if source_pins.get(key) != expected:
            _fail(f"factorization-v2: {key} pin mismatch")
    if (
        _domain_digest(CONFIGURATION_INVENTORY_DOMAIN, _configuration_inventory(configuration))
        != CONFIGURATION_INVENTORY_SHA256
        or _domain_digest(PARTITION_INVENTORY_DOMAIN, _partition_inventory(member))
        != PARTITION_INVENTORY_SHA256
    ):
        _fail("accepted inventory digest mismatch")
    return member, configuration, factorization, initial_bundle


def _expected_entries(
    configuration: dict[str, Any],
    member: dict[str, Any],
    initial_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    authority = configuration.get("authority")
    if type(authority) is not dict or set(authority) != {
        "design_path",
        "design_sha256",
        "implementation_path",
        "implementation_sha256",
        "test_path",
        "test_sha256",
    }:
        _fail("configuration: authority closure mismatch")
    expected: list[dict[str, Any]] = []
    for semantic_role, path_key, sha_key in LINEAGE_ROLES:
        source = _safe_relative(authority[path_key], semantic_role)
        expected.append(
            {
                "mirror_relative_path": (PurePosixPath("files") / source).as_posix(),
                "ordinal": len(expected),
                "semantic_role": semantic_role,
                "sha256": authority[sha_key],
                "source_report_relative_path": source.as_posix(),
            }
        )
    expected.append(
        {
            "mirror_relative_path": (PurePosixPath("files") / INITIAL_GEOMETRY_RELATIVE).as_posix(),
            "ordinal": len(expected),
            "semantic_role": "configuration_initial_geometry",
            "sha256": INITIAL_GEOMETRY_SHA256,
            "source_report_relative_path": INITIAL_GEOMETRY_RELATIVE.as_posix(),
        }
    )
    inventory = initial_bundle.get("file_inventory")
    if type(inventory) is not list:
        _fail("initial bundle: file inventory missing")
    indexed: dict[str, dict[str, Any]] = {}
    for record in inventory:
        if type(record) is not dict or set(record) != {"byte_length", "path", "sha256"}:
            _fail("initial bundle: malformed file inventory")
        if record["path"] in indexed:
            _fail("initial bundle: duplicate inventory path")
        indexed[record["path"]] = record
    analytic = indexed.get("request/analytic_source.json")
    if (
        analytic is None
        or analytic["sha256"] != INITIAL_GEOMETRY_SHA256
        or initial_bundle.get("analytic_source_sha256") != INITIAL_GEOMETRY_SHA256
    ):
        _fail("initial bundle: analytic source binding mismatch")
    expected[3]["byte_length"] = analytic["byte_length"]
    for record in _partition_inventory(member):
        source = _safe_relative(record["partition_report_relative_path"], "member partition")
        try:
            bundle_relative = source.relative_to(INITIAL_BUNDLE_DIRECTORY)
        except ValueError:
            _fail("member partition escapes initial-bundle directory")
        bundle_record = indexed.get(bundle_relative.as_posix())
        if (
            bundle_record is None
            or bundle_record["sha256"] != record["partition_sha256"]
            or record["partition_schema"] != PARTITION_SCHEMA
        ):
            _fail("member/initial-bundle partition binding mismatch")
        expected.append(
            {
                "byte_length": bundle_record["byte_length"],
                "configuration_index": record["configuration_index"],
                "configuration_label": record["configuration_label"],
                "coordinate": record["coordinate"],
                "mirror_relative_path": (PurePosixPath("files") / source).as_posix(),
                "ordinal": len(expected),
                "semantic_role": "member_v4_partition",
                "sha256": record["partition_sha256"],
                "source_report_relative_path": source.as_posix(),
            }
        )
    if len(expected) != EXPECTED_ENTRY_COUNT:
        _fail("expected entry cardinality mismatch")
    return expected


def _expected_static_manifest() -> dict[str, Any]:
    return {
        "accepted_authorities": {
            "configuration": _authority_pin(
                CONFIGURATION_RELATIVE,
                CONFIGURATION_SCHEMA,
                CONFIGURATION_STATUS,
                CONFIGURATION_SHA256,
            ),
            "factorization_v2": _authority_pin(
                FACTORIZATION_RELATIVE,
                FACTORIZATION_SCHEMA,
                FACTORIZATION_STATUS,
                FACTORIZATION_SHA256,
            ),
            "initial_partition_bundle": _authority_pin(
                INITIAL_BUNDLE_RELATIVE,
                INITIAL_BUNDLE_SCHEMA,
                INITIAL_BUNDLE_STATUS,
                INITIAL_BUNDLE_SHA256,
            ),
            "member_v4": {
                **_authority_pin(MEMBER_RELATIVE, MEMBER_SCHEMA, MEMBER_STATUS, MEMBER_SHA256),
                "member_identity_sha256": MEMBER_IDENTITY_SHA256,
            },
        },
        "claim_boundary": dict.fromkeys(CLAIM_KEYS, False),
        "coverage": {
            "configuration_authority_lineage_file_count": 3,
            "configuration_initial_geometry_file_count": 1,
            "exact_writable_precommit_input_closure_mirrored": True,
            "member_v4_partition_file_count": EXPECTED_PARTITION_COUNT,
            "original_report_relative_suffix_preserved_under_files": True,
            "standalone_content_addressed_validation_without_original_writable_sources": True,
        },
        "entry_count": EXPECTED_ENTRY_COUNT,
        "exclusions": {
            "external_commitment_not_created": True,
            "legacy_role10_result_and_output_bytes_excluded": True,
            "numerical_execution_results_excluded": True,
            "replay_requests_plans_bundles_and_commitments_excluded": True,
            "role8_and_role9_outputs_excluded": True,
        },
        "inventory_digests": {
            "configuration_row_inventory": {
                "domain": CONFIGURATION_INVENTORY_DOMAIN,
                "sha256": CONFIGURATION_INVENTORY_SHA256,
            },
            "member_v4_partition_inventory": {
                "domain": PARTITION_INVENTORY_DOMAIN,
                "sha256": PARTITION_INVENTORY_SHA256,
            },
        },
        "mirrored_source_pin": {
            "path": INITIAL_GEOMETRY_RELATIVE.as_posix(),
            "schema": INITIAL_GEOMETRY_SCHEMA,
            "sha256": INITIAL_GEOMETRY_SHA256,
        },
        "schema": SCHEMA,
        "status": STATUS,
    }


def _tree_inventory(root_fd: int) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    directories: set[str] = set()

    def visit(directory_fd: int, prefix: PurePosixPath) -> None:
        for name in sorted(os.listdir(directory_fd)):
            if name in {"", ".", ".."} or "/" in name or "\\" in name:
                _fail("mirror contains an unsafe directory entry")
            value = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            relative = prefix / name
            if stat.S_ISDIR(value.st_mode):
                if stat.S_IMODE(value.st_mode) != 0o555:
                    _fail(f"{relative}: directory is not mode 0555")
                directories.add(relative.as_posix())
                child_fd = os.open(
                    name,
                    os.O_RDONLY
                    | os.O_DIRECTORY
                    | getattr(os, "O_CLOEXEC", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=directory_fd,
                )
                try:
                    visit(child_fd, relative)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(value.st_mode):
                if stat.S_IMODE(value.st_mode) != 0o444 or value.st_nlink != 1:
                    _fail(f"{relative}: file mode/link-count mismatch")
                files.add(relative.as_posix())
            else:
                _fail(f"{relative}: non-regular mirror object")

    visit(root_fd, PurePosixPath("."))
    return files, directories


def validate_mirror(mirror_root: Path, authority_root: Path) -> dict[str, Any]:
    """Validate a sealed mirror without opening any original mirrored source."""

    authority_fd = _open_absolute_directory(authority_root.absolute())
    try:
        member, configuration, _factorization, initial_bundle = _load_authorities(authority_fd)
        expected_entries = _expected_entries(configuration, member, initial_bundle)
    finally:
        os.close(authority_fd)

    mirror_fd = _open_absolute_directory(mirror_root.absolute())
    try:
        if stat.S_IMODE(os.fstat(mirror_fd).st_mode) != 0o555:
            _fail("mirror root is not mode 0555")
        manifest_raw = _snapshot(
            mirror_fd,
            PurePosixPath("manifest.json"),
            authority=False,
            invoke_hook=True,
        )
        manifest = _decode_canonical(manifest_raw, "mirror manifest")
        if set(manifest) != TOP_LEVEL_KEYS:
            _fail("manifest top-level key mismatch")
        static = _expected_static_manifest()
        for key, expected in static.items():
            if manifest.get(key) != expected:
                _fail(f"manifest {key} mismatch")
        entries = manifest.get("entries")
        if type(entries) is not list or len(entries) != EXPECTED_ENTRY_COUNT:
            _fail("manifest entry cardinality mismatch")

        expected_files = {"manifest.json"}
        expected_directories: set[str] = set()
        for index, (entry, expected) in enumerate(zip(entries, expected_entries, strict=True)):
            if type(entry) is not dict:
                _fail("manifest entry is not an object")
            expected_keys = (
                PARTITION_ENTRY_KEYS
                if expected["semantic_role"] == "member_v4_partition"
                else BASE_ENTRY_KEYS
            )
            if set(entry) != expected_keys:
                _fail(f"manifest entry {index}: key mismatch")
            for key, value in expected.items():
                if key != "byte_length" and entry.get(key) != value:
                    _fail(f"manifest entry {index}: semantic binding mismatch")
            if type(entry.get("byte_length")) is not int or entry["byte_length"] <= 0:
                _fail(f"manifest entry {index}: invalid byte length")
            if "byte_length" in expected and entry["byte_length"] != expected["byte_length"]:
                _fail(f"manifest entry {index}: authority byte-length mismatch")
            source = _safe_relative(entry["source_report_relative_path"], "manifest source")
            mirror_relative = _safe_relative(entry["mirror_relative_path"], "manifest mirror")
            if mirror_relative != PurePosixPath("files") / source:
                _fail(f"manifest entry {index}: suffix preservation mismatch")
            padded_source = f"/{source.as_posix()}/"
            if any(fragment in padded_source for fragment in FORBIDDEN_REPORT_RELATIVE_FRAGMENTS):
                _fail(f"manifest entry {index}: forbidden legacy/output path")
            raw = _snapshot(mirror_fd, mirror_relative, authority=False, invoke_hook=True)
            if len(raw) != entry["byte_length"] or _sha256(raw) != expected["sha256"]:
                _fail(f"manifest entry {index}: mirrored bytes mismatch")
            if entry["semantic_role"] == "configuration_initial_geometry":
                geometry = _decode_json(raw, "mirrored initial geometry")
                if geometry.get("schema") != INITIAL_GEOMETRY_SCHEMA:
                    _fail("mirrored initial geometry schema mismatch")
            elif entry["semantic_role"] == "member_v4_partition":
                partition = _decode_canonical(raw, "mirrored partition")
                if (
                    partition.get("schema") != PARTITION_SCHEMA
                    or partition.get("coordinate") != entry["coordinate"]
                ):
                    _fail(f"manifest entry {index}: partition semantic mismatch")
            expected_files.add(mirror_relative.as_posix())
            parent = mirror_relative.parent
            while parent != PurePosixPath("."):
                expected_directories.add(parent.as_posix())
                parent = parent.parent
        files, directories = _tree_inventory(mirror_fd)
        if files != expected_files or directories != expected_directories:
            _fail("mirror contains missing or extra filesystem entries")
        return manifest
    finally:
        os.close(mirror_fd)


def _parse_cli(argv: Sequence[str] | None = None) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--mirror-root", default=str(DEFAULT_MIRROR))
    parser.add_argument("--authority-root", default=str(REPORT))
    arguments = parser.parse_args(argv)
    mirror_root = Path(arguments.mirror_root)
    authority_root = Path(arguments.authority_root)
    if not mirror_root.is_absolute() or not authority_root.is_absolute():
        _fail("CLI paths must be absolute")
    return mirror_root, authority_root


def main(argv: Sequence[str] | None = None) -> int:
    try:
        mirror_root, authority_root = _parse_cli(argv)
        manifest = validate_mirror(mirror_root, authority_root)
    except MirrorValidationError as error:
        print(
            f"HOLD_ROLE10_SEALED_AUTHENTICATION_MIRROR_VALIDATION: {error}",
            file=sys.stderr,
        )
        return 2
    print(
        "PASS_ROLE10_SEALED_AUTHENTICATION_MIRROR_CANDIDATE "
        f"entries={manifest['entry_count']} mirror={mirror_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
