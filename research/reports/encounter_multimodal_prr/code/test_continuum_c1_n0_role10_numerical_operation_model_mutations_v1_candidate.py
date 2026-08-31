"""Mutation and race tests for the role-10 numerical operation model."""

from __future__ import annotations

import copy
import errno
import importlib.util
import json
import os
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
BUILDER_PATH = CODE / "build_continuum_c1_n0_role10_numerical_operation_model_v1_candidate.py"
VALIDATOR_PATH = CODE / "validate_continuum_c1_n0_role10_numerical_operation_model_v1_candidate.py"


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


builder = load_module("role10_operation_model_builder_mutations", BUILDER_PATH)
validator = load_module("role10_operation_model_validator_mutations", VALIDATOR_PATH)
BASE = builder.build_model()
BASE_RAW = builder.canonical_bytes(BASE)
validator.EXPECTED_MODEL_SHA256 = builder.sha256(BASE_RAW)


def set_nested(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    cursor: Any = value
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement


MUTATIONS: list[tuple[str, tuple[Any, ...], Any]] = [
    ("schema", ("schema",), "encounter_wrong"),
    ("status", ("status",), "EXECUTED"),
    ("claim_true", ("claim_boundary", "complete_C1"), True),
    ("registry_path", ("authority_bindings", "method_parameter_registry", "path"), "x.json"),
    ("registry_sha", ("authority_bindings", "method_parameter_registry", "sha256"), "0" * 64),
    (
        "mirror_sha",
        ("authority_model", "sealed_authentication_mirror", "manifest_sha256"),
        "1" * 64,
    ),
    (
        "mirror_entries",
        ("authority_model", "sealed_authentication_mirror", "entry_count"),
        39,
    ),
    (
        "direct_dependencies",
        ("authority_model", "normative_direct_role_dependencies"),
        [1, 3, 5, 6],
    ),
    ("method_count", ("method_contract", "method_count"), 5),
    (
        "method_digest",
        ("method_contract", "method_record_digests", 0),
        "2" * 64,
    ),
    (
        "method_scope",
        ("method_contract", "selected_records", 0, "parameters", "source_role_scope"),
        ["role9_stationary_physical_integral"],
    ),
    ("file_count", ("artifact_contract", "totals", "files"), 72),
    ("directory_count", ("artifact_contract", "totals", "directories"), 13),
    (
        "top_self_inventory",
        ("artifact_contract", "top_file_inventory", "ordered_paths", 0),
        "manifest.json",
    ),
    (
        "row_path",
        ("artifact_contract", "rows", 0, "row_manifest_path"),
        "rows/row_01/row.json",
    ),
    (
        "contact_count",
        ("artifact_contract", "rows", 0, "contact", "record_count"),
        12_768,
    ),
    (
        "contact_bytes",
        ("artifact_contract", "rows", 7, "contact", "byte_length"),
        553_839,
    ),
    (
        "profile_count",
        ("artifact_contract", "rows", 11, "profiles", 3, "record_count"),
        128,
    ),
    (
        "profile_units",
        ("artifact_contract", "rows", 0, "profiles", 0, "units"),
        "dimensionless",
    ),
    (
        "raw_schema",
        ("artifact_contract", "schemas", "raw_interval_file"),
        "encounter_raw_wrong",
    ),
    (
        "remove_raw_schema_key",
        ("artifact_contract", "schema_key_contracts", "raw_manifest_exact_keys"),
        [
            key
            for key in BASE["artifact_contract"]["schema_key_contracts"]["raw_manifest_exact_keys"]
            if key != "schema"
        ],
    ),
    (
        "remove_top_model_binding",
        ("artifact_contract", "schema_key_contracts", "top_manifest_exact_keys"),
        [
            key
            for key in BASE["artifact_contract"]["schema_key_contracts"]["top_manifest_exact_keys"]
            if key != "operation_model_binding"
        ],
    ),
    (
        "stored_precision",
        ("artifact_contract", "stored_precision_policy", "contact_and_profile_payloads"),
        "producer_384_bit_values",
    ),
    (
        "tangent_strict",
        (
            "numerical_semantics",
            "contact",
            "cell_classification",
            "zero_segment_pair",
        ),
        "nearest_squared_distance_greater_than_radius_squared",
    ),
    (
        "full_strict",
        (
            "numerical_semantics",
            "contact",
            "cell_classification",
            "full_segment_pair",
        ),
        "all_four_corner_squared_distances_less_than_radius_squared",
    ),
    (
        "partial_count",
        ("numerical_semantics", "contact", "derived_expected_partial_cell_count"),
        1_303,
    ),
    (
        "profile_mass_width",
        ("numerical_semantics", "profile", "cell_mass_width_definition"),
        "published_upper_exact-published_lower_exact",
    ),
    (
        "W_inverse_contact",
        ("numerical_semantics", "normalization_boundary", "W_inverse_in_contact"),
        "applied",
    ),
    (
        "W_inverse_profile",
        ("numerical_semantics", "normalization_boundary", "W_inverse_in_profile"),
        "applied",
    ),
    (
        "contact_384_count",
        ("verification_contract", "contact_coverage", "all_partial_cells_at_384"),
        1_303,
    ),
    (
        "contact_512_count",
        (
            "verification_contract",
            "contact_coverage",
            "first_partial_cell_per_row_at_512",
        ),
        1_304,
    ),
    (
        "contact_ratio",
        ("verification_contract", "contact_coverage", "ratio_gate"),
        "none",
    ),
    (
        "profile_coverage",
        (
            "verification_contract",
            "profile_coverage",
            "all_profile_cells_at_paired_384_512",
        ),
        6_851,
    ),
    (
        "profile_ratio",
        ("verification_contract", "profile_coverage", "ratio_gate"),
        "none",
    ),
    ("child_count", ("receipt_contract", "child_observation_count"), 1),
    (
        "semantic_cap",
        ("receipt_contract", "semantic_receipt", "maximum_bytes"),
        2_097_153,
    ),
    (
        "outer_cap",
        ("receipt_contract", "outer_receipt", "maximum_bytes"),
        262_145,
    ),
    (
        "role10_output_count",
        ("receipt_contract", "slot_contract", "role10_output_count"),
        2,
    ),
    (
        "global_slot_count",
        ("receipt_contract", "slot_contract", "global_plan_v2_slot_count"),
        9,
    ),
    (
        "producer_isolation",
        ("invocation_contract", "producer_argv", 1),
        "-B",
    ),
    (
        "outer_isolation",
        ("invocation_contract", "outer_verifier_argv", 2),
        "-E",
    ),
    (
        "shared_numerics",
        ("invocation_contract", "shared_module_boundary", "numerical_source_sets"),
        "shared",
    ),
    (
        "child_deadline",
        ("resource_caps", "child_process_deadline_seconds"),
        1_201,
    ),
    (
        "panel_cap",
        ("resource_caps", "maximum_simpson_panels"),
        4_194_305,
    ),
    (
        "future_code_hashes",
        ("forbidden_surface", "future_code_hashes"),
        "forbidden",
    ),
    (
        "future_parent_mode",
        ("publication_contract", "output_parent", "mode"),
        "0755",
    ),
]


@pytest.mark.parametrize(
    ("name", "path", "replacement"),
    MUTATIONS,
    ids=[mutation[0] for mutation in MUTATIONS],
)
def test_semantic_mutations_are_rejected(
    name: str,
    path: tuple[Any, ...],
    replacement: Any,
) -> None:
    del name
    mutated = copy.deepcopy(BASE)
    set_nested(mutated, path, replacement)
    raw = builder.canonical_bytes(mutated)
    with pytest.raises(validator.OperationModelValidationError):
        validator.validate_value(mutated, raw=raw)


def test_coherent_registry_record_and_binding_repin_is_rejected() -> None:
    mutated = copy.deepcopy(BASE)
    record = mutated["method_contract"]["selected_records"][0]
    record["parameters"]["precision_bits"] = 193
    new_digest = builder._method_digest(record["parameters"])
    record["method_parameter_sha256"] = new_digest
    mutated["method_contract"]["method_record_digests"][0] = new_digest
    mutated["authority_bindings"]["method_parameter_registry"]["sha256"] = "a" * 64
    mutated["method_contract"]["registry_binding"]["sha256"] = "a" * 64
    raw = builder.canonical_bytes(mutated)
    with pytest.raises(validator.OperationModelValidationError):
        validator.validate_value(mutated, raw=raw)


def test_coherent_mirror_repin_and_coverage_mutation_is_rejected() -> None:
    mutated = copy.deepcopy(BASE)
    mirror = mutated["authority_model"]["sealed_authentication_mirror"]
    mirror["manifest_sha256"] = "b" * 64
    mirror["validated_coverage"]["member_v4_partition_file_count"] = 35
    mutated["authority_bindings"]["sealed_authentication_mirror"]["sha256"] = "b" * 64
    raw = builder.canonical_bytes(mutated)
    with pytest.raises(validator.OperationModelValidationError):
        validator.validate_value(mutated, raw=raw)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":1}\n',
        b'{"a":1.0}\n',
        b'{"a":NaN}\n',
        b'{"a":Infinity}\n',
        b'{"z":0,"a":1}\n',
        b"[]\n",
        b"{}\n ",
        b"\xff",
    ],
)
def test_noncanonical_duplicate_float_and_nonobject_json_rejected(raw: bytes) -> None:
    with pytest.raises(validator.OperationModelValidationError):
        validator.parse_canonical_json(raw, "attack")


def test_non_nfc_string_rejected() -> None:
    decomposed = unicodedata.normalize("NFD", "é")
    assert decomposed != "é"
    raw = (
        json.dumps({"value": decomposed}, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    with pytest.raises(validator.OperationModelValidationError, match="non-NFC"):
        validator.parse_canonical_json(raw, "non-NFC")


def test_deep_json_rejected() -> None:
    value: Any = 0
    for _ in range(66):
        value = [value]
    with pytest.raises(validator.OperationModelValidationError, match="depth"):
        validator.canonical_bytes({"value": value})


def test_oversized_integer_rejected() -> None:
    with pytest.raises(validator.OperationModelValidationError, match="integer"):
        validator.canonical_bytes({"value": 1 << 65_537})


@pytest.mark.parametrize("module", [builder, validator])
def test_read_rejects_symlink_hardlink_writable_empty_and_oversize(
    module: Any,
    tmp_path: Path,
) -> None:
    payload = BASE_RAW
    immutable = tmp_path / "immutable.json"
    immutable.write_bytes(payload)
    immutable.chmod(0o444)

    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(immutable)
    with pytest.raises((OSError, RuntimeError)):
        module.read_regular(symlink, cap=8_000_000, required_mode=0o444)

    linked = tmp_path / "linked.json"
    os.link(immutable, linked)
    with pytest.raises((OSError, RuntimeError)):
        module.read_regular(immutable, cap=8_000_000, required_mode=0o444)
    linked.unlink()

    writable = tmp_path / "writable.json"
    writable.write_bytes(payload)
    writable.chmod(0o644)
    with pytest.raises((OSError, RuntimeError)):
        module.read_regular(writable, cap=8_000_000, required_mode=0o444)

    empty = tmp_path / "empty.json"
    empty.touch(mode=0o444)
    with pytest.raises((OSError, RuntimeError)):
        module.read_regular(empty, cap=8_000_000, required_mode=0o444)

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"x" * 101)
    oversized.chmod(0o444)
    with pytest.raises((OSError, RuntimeError)):
        module.read_regular(oversized, cap=100, required_mode=0o444)


def test_same_metadata_path_replacement_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "model.json"
    path.write_bytes(BASE_RAW)
    path.chmod(0o444)
    original = path.stat()
    real_read = validator.os.read
    replaced = False

    def read_then_replace(descriptor: int, size: int) -> bytes:
        nonlocal replaced
        payload = real_read(descriptor, size)
        if payload and not replaced:
            replaced = True
            path.unlink()
            path.write_bytes(BASE_RAW)
            path.chmod(0o444)
            os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns))
        return payload

    monkeypatch.setattr(validator.os, "read", read_then_replace)
    with pytest.raises(validator.OperationModelValidationError, match="changed"):
        validator.read_regular(path, cap=8_000_000, required_mode=0o444)


def test_parent_swap_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = tmp_path / "parent"
    parent.mkdir(mode=0o700)
    path = parent / "model.json"
    path.write_bytes(BASE_RAW)
    path.chmod(0o444)
    backup = tmp_path / "backup"
    real_read = validator.os.read
    swapped = False

    def read_then_swap(descriptor: int, size: int) -> bytes:
        nonlocal swapped
        payload = real_read(descriptor, size)
        if payload and not swapped:
            swapped = True
            parent.rename(backup)
            parent.mkdir(mode=0o700)
            replacement = parent / "model.json"
            replacement.write_bytes(BASE_RAW)
            replacement.chmod(0o444)
        return payload

    monkeypatch.setattr(validator.os, "read", read_then_swap)
    with pytest.raises(validator.OperationModelValidationError, match="directory chain"):
        validator.read_regular(path, cap=8_000_000, required_mode=0o444)


def test_failed_partial_publication_leaves_no_owned_final_or_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    real_write = builder.os.write
    calls = 0

    def short_then_fail(descriptor: int, payload: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_write(descriptor, payload[:7])
        raise OSError(errno.ENOSPC, "injected no space")

    monkeypatch.setattr(builder.os, "write", short_then_fail)
    with pytest.raises(OSError):
        builder.publish_no_replace(output, b"x" * 100)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_open_interrupt_rolls_back_owned_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    original_await = builder.StageCreationTransaction.await_ready

    def await_then_interrupt(transaction: Any) -> None:
        original_await(transaction)
        raise interrupt_type("post-open interruption")

    monkeypatch.setattr(builder.StageCreationTransaction, "await_ready", await_then_interrupt)
    with pytest.raises(interrupt_type):
        builder.publish_no_replace(output, b"owned-stage")
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_post_open_interrupt_preserves_foreign_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    original_await = builder.StageCreationTransaction.await_ready
    foreign_identity: tuple[int, int] | None = None

    def replace_then_interrupt(transaction: Any) -> None:
        nonlocal foreign_identity
        original_await(transaction)
        assert transaction.identity is not None
        os.unlink(transaction.leaf, dir_fd=transaction.parent_descriptor)
        foreign = os.open(
            transaction.leaf,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=transaction.parent_descriptor,
        )
        observed = os.fstat(foreign)
        foreign_identity = observed.st_dev, observed.st_ino
        os.close(foreign)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        builder.StageCreationTransaction,
        "await_ready",
        replace_then_interrupt,
    )
    with pytest.raises(KeyboardInterrupt):
        builder.publish_no_replace(output, b"owned-stage")
    stages = list(tmp_path.glob(".*.stage"))
    assert len(stages) == 1
    assert (stages[0].stat().st_dev, stages[0].stat().st_ino) == foreign_identity
    assert not output.exists()


class InjectedCancellation(BaseException):
    """Cancellation-shaped BaseException for rollback coverage."""


@pytest.mark.parametrize(
    "interrupt_type",
    [KeyboardInterrupt, SystemExit, InjectedCancellation],
)
def test_post_link_interrupt_or_cancellation_rolls_back_owned_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    original_link = builder.os.link

    def link_then_interrupt(*arguments: Any, **keywords: Any) -> None:
        original_link(*arguments, **keywords)
        raise interrupt_type("post-link interruption")

    monkeypatch.setattr(builder.os, "link", link_then_interrupt)
    with pytest.raises(interrupt_type):
        builder.publish_no_replace(output, b"owned-final")
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_missing_atomic_no_replace_capability_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"

    def unsupported(*arguments: Any, **keywords: Any) -> None:
        del arguments, keywords
        raise OSError(errno.ENOTSUP, "atomic no-replace unavailable")

    monkeypatch.setattr(builder.os, "link", unsupported)
    with pytest.raises(OSError, match="atomic no-replace unavailable"):
        builder.publish_no_replace(output, b"owned-final")
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("window", ["before_link", "after_link"])
def test_installed_bytes_reauthenticated_after_same_inode_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    window: str,
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    payload = b"owned-payload"
    corrupted = b"X" + payload[1:]
    original_link = builder.os.link

    def mutate(leaf: str, parent: int) -> None:
        os.chmod(leaf, 0o600, dir_fd=parent)
        descriptor = os.open(
            leaf,
            os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=parent,
        )
        try:
            assert os.write(descriptor, corrupted) == len(corrupted)
        finally:
            os.close(descriptor)
        os.chmod(leaf, 0o444, dir_fd=parent)

    def mutate_around_link(source: str, destination: str, **keywords: Any) -> None:
        if window == "before_link":
            mutate(source, keywords["src_dir_fd"])
        original_link(source, destination, **keywords)
        if window == "after_link":
            mutate(destination, keywords["dst_dir_fd"])

    monkeypatch.setattr(builder.os, "link", mutate_around_link)
    with pytest.raises(builder.OperationModelBuildError):
        builder.publish_no_replace(output, payload)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_post_link_foreign_replacement_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    original_link = builder.os.link
    foreign_payload = b"foreign-final"

    def replace_then_interrupt(
        source: str,
        destination: str,
        **keywords: Any,
    ) -> None:
        original_link(source, destination, **keywords)
        os.unlink(destination, dir_fd=keywords["dst_dir_fd"])
        foreign = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o444,
            dir_fd=keywords["dst_dir_fd"],
        )
        os.write(foreign, foreign_payload)
        os.close(foreign)
        raise SystemExit("post-link foreign replacement")

    monkeypatch.setattr(builder.os, "link", replace_then_interrupt)
    with pytest.raises(SystemExit):
        builder.publish_no_replace(output, b"owned-final")
    assert output.read_bytes() == foreign_payload
    assert stat.S_IMODE(output.stat().st_mode) == 0o444
    assert not list(tmp_path.glob(".*.stage"))
