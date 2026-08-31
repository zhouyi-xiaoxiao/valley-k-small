"""Exhaustive semantic-mutation and installed-byte race tests for role-10 v2."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Iterator

import pytest

CODE = Path(__file__).resolve().parent
VALIDATOR_PATH = CODE / "validate_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py"


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


validator = load_module("role10_operation_model_v2_validator_mutations", VALIDATOR_PATH)


def walk_nodes(
    value: Any,
    parent: dict[str, Any] | list[Any] | None = None,
    key: str | int | None = None,
    path: str = "$",
) -> Iterator[tuple[Any, dict[str, Any] | list[Any] | None, str | int | None, str]]:
    yield value, parent, key, path
    if type(value) is dict:
        for child_key, child in list(value.items()):
            yield from walk_nodes(child, value, child_key, f"{path}/{child_key}")
    elif type(value) is list:
        for index, child in enumerate(list(value)):
            yield from walk_nodes(child, value, index, f"{path}/{index}")


def changed_scalar(value: Any) -> Any:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "__MUTATED__"
    if value is None:
        return False
    raise AssertionError(f"not a JSON scalar: {type(value).__name__}")


def assert_semantic_rejection(value: dict[str, Any], path: str) -> None:
    """Every mutation deliberately bypasses only the separate frozen-byte SHA gate."""

    with pytest.raises(
        validator.OperationModelV2ValidationError,
        match="mismatch|differs|missing|forbidden|expected|must|claim|pointer|schema|topology|"
        "classification|lineage|lock|grammar|argv|future|lifecycle|status|row|artifact",
    ):
        validator.validate_value(value, enforce_frozen_sha=False)


def test_every_scalar_leaf_mutation_is_rejected_without_frozen_sha() -> None:
    model = validator.expected_model()
    nodes = list(walk_nodes(model))
    count = 0
    for value, parent, key, path in nodes:
        if type(value) not in (bool, int, str) and value is not None:
            continue
        assert parent is not None and key is not None
        original = value
        parent[key] = changed_scalar(value)  # type: ignore[index]
        try:
            assert_semantic_rejection(model, path)
        finally:
            parent[key] = original  # type: ignore[index]
        count += 1
    assert count == sum(
        type(value) in (bool, int, str) or value is None for value, _, _, _ in nodes
    )
    assert count >= 2_700


def test_every_object_member_deletion_is_rejected_without_frozen_sha() -> None:
    model = validator.expected_model()
    objects = [(value, path) for value, _, _, path in walk_nodes(model) if type(value) is dict]
    count = 0
    for value, path in objects:
        for key in list(value):
            original = value.pop(key)
            try:
                assert_semantic_rejection(model, f"{path}/{key}:deleted")
            finally:
                value[key] = original
            count += 1
    assert count >= 2_100


def test_every_array_item_deletion_is_rejected_without_frozen_sha() -> None:
    model = validator.expected_model()
    arrays = [(value, path) for value, _, _, path in walk_nodes(model) if type(value) is list]
    count = 0
    for value, path in arrays:
        for index in range(len(value) - 1, -1, -1):
            original = value.pop(index)
            try:
                assert_semantic_rejection(model, f"{path}/{index}:deleted")
            finally:
                value.insert(index, original)
            count += 1
    assert count >= 1_300


def test_every_container_extension_is_rejected_without_frozen_sha() -> None:
    model = validator.expected_model()
    nodes = list(walk_nodes(model))
    count = 0
    for value, _, _, path in nodes:
        if type(value) is dict:
            key = "__unexpected_v2_member__"
            assert key not in value
            value[key] = None
            try:
                assert_semantic_rejection(model, f"{path}/{key}:added")
            finally:
                del value[key]
            count += 1
        elif type(value) is list:
            value.append(None)
            try:
                assert_semantic_rejection(model, f"{path}/-:appended")
            finally:
                value.pop()
            count += 1
    assert count >= 680


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (
            (
                "replay_plan_contract",
                "global_replay_runner_contract",
                "entrypoint_basename",
            ),
            "execute_wrong_runner.py",
        ),
        (
            (
                "replay_plan_contract",
                "runtime_closure",
                "claim_boundary",
                "complete_host_runtime_image",
            ),
            True,
        ),
        (
            (
                "replay_plan_contract",
                "request_contract",
                "join_rules",
                5,
            ),
            "requests_may_disagree",
        ),
        (
            (
                "process_contract",
                "ack_contracts",
                "public_transaction_commit",
                "field_schemas",
                "artifact_binding_sha256",
            ),
            "/wire_schema_contract/objects/artifact_binding",
        ),
        (
            (
                "process_contract",
                "deadline_accounting",
                "phase_caps_seconds",
                "semantic_children_concurrent_including_signal_reap",
            ),
            1_200,
        ),
        (
            (
                "publication_contract",
                "recovery_journal",
                "state_order",
                0,
            ),
            "COMMITTED",
        ),
        (
            (
                "receipt_contract",
                "temporary_child_receipts",
                "paths_in_run_order",
                0,
            ),
            "nested/.semantic-child-0-receipt.json",
        ),
    ],
)
def test_explicit_runner_runtime_ack_deadline_and_journal_mutations_are_rejected(
    path: tuple[str | int, ...], replacement: Any
) -> None:
    model = validator.expected_model()
    parent: Any = model
    for token in path[:-1]:
        parent = parent[token]
    parent[path[-1]] = replacement
    with pytest.raises(validator.OperationModelV2ValidationError):
        validator.validate_value(model, enforce_frozen_sha=False)


def write_frozen(path: Path, raw: bytes = b"abcdefgh") -> None:
    path.write_bytes(raw)
    path.chmod(0o444)


def read_error(path: Path) -> tuple[type[BaseException], ...]:
    del path
    return (OSError, validator.OperationModelV2ValidationError)


def test_immutable_reader_rejects_writable_mode(tmp_path: Path) -> None:
    target = tmp_path / "candidate.json"
    target.write_bytes(b"abcdefgh")
    target.chmod(0o644)
    with pytest.raises(validator.OperationModelV2ValidationError, match="0444"):
        validator.read_immutable(target, label="mode race")


def test_immutable_reader_rejects_hard_link(tmp_path: Path) -> None:
    target = tmp_path / "candidate.json"
    alias = tmp_path / "alias.json"
    write_frozen(target)
    os.link(target, alias)
    with pytest.raises(validator.OperationModelV2ValidationError, match="single-link"):
        validator.read_immutable(target, label="hard-link race")


def test_immutable_reader_rejects_file_symlink(tmp_path: Path) -> None:
    target = tmp_path / "candidate.json"
    alias = tmp_path / "alias.json"
    write_frozen(target)
    alias.symlink_to(target.name)
    with pytest.raises(read_error(alias)):
        validator.read_immutable(alias, label="symlink race")


def test_immutable_reader_rejects_parent_symlink(tmp_path: Path) -> None:
    parent = tmp_path / "real"
    parent.mkdir()
    target = parent / "candidate.json"
    write_frozen(target)
    alias = tmp_path / "alias"
    alias.symlink_to(parent.name, target_is_directory=True)
    with pytest.raises(read_error(alias / target.name)):
        validator.read_immutable(alias / target.name, label="parent symlink race")


def test_immutable_reader_detects_growth_during_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "candidate.json"
    write_frozen(target)
    real_read = os.read
    changed = False

    def racing_read(descriptor: int, size: int) -> bytes:
        nonlocal changed
        chunk = real_read(descriptor, size)
        if not changed:
            changed = True
            target.chmod(0o644)
            with target.open("ab") as stream:
                stream.write(b"x")
            target.chmod(0o444)
        return chunk

    monkeypatch.setattr(validator.os, "read", racing_read)
    with pytest.raises(validator.OperationModelV2ValidationError, match="grew|changed"):
        validator.read_immutable(target, label="growth race")


def test_immutable_reader_detects_installed_inode_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "candidate.json"
    write_frozen(target)
    real_read = os.read
    changed = False

    def racing_read(descriptor: int, size: int) -> bytes:
        nonlocal changed
        chunk = real_read(descriptor, size)
        if not changed:
            changed = True
            target.unlink()
            write_frozen(target, b"ABCDEFGH")
        return chunk

    monkeypatch.setattr(validator.os, "read", racing_read)
    with pytest.raises(
        validator.OperationModelV2ValidationError,
        match="descriptor identity changed|installed path changed",
    ):
        validator.read_immutable(target, label="replacement race")


def test_immutable_reader_detects_parent_inode_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = tmp_path / "parent"
    parent.mkdir()
    target = parent / "candidate.json"
    write_frozen(target)
    displaced = tmp_path / "displaced"
    real_read = os.read
    changed = False

    def racing_read(descriptor: int, size: int) -> bytes:
        nonlocal changed
        chunk = real_read(descriptor, size)
        if not changed:
            changed = True
            parent.rename(displaced)
            parent.mkdir()
            write_frozen(parent / target.name, b"ABCDEFGH")
        return chunk

    monkeypatch.setattr(validator.os, "read", racing_read)
    with pytest.raises(
        validator.OperationModelV2ValidationError, match="parent path identity changed"
    ):
        validator.read_immutable(target, label="parent replacement race")


def test_immutable_reader_detects_mode_change_during_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "candidate.json"
    write_frozen(target)
    real_read = os.read
    changed = False

    def racing_read(descriptor: int, size: int) -> bytes:
        nonlocal changed
        chunk = real_read(descriptor, size)
        if not changed:
            changed = True
            target.chmod(0o400)
        return chunk

    monkeypatch.setattr(validator.os, "read", racing_read)
    with pytest.raises(validator.OperationModelV2ValidationError, match="changed"):
        validator.read_immutable(target, label="mode-change race")


def test_immutable_reader_detects_link_count_change_during_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "candidate.json"
    alias = tmp_path / "late-alias.json"
    write_frozen(target)
    real_read = os.read
    changed = False

    def racing_read(descriptor: int, size: int) -> bytes:
        nonlocal changed
        chunk = real_read(descriptor, size)
        if not changed:
            changed = True
            os.link(target, alias)
        return chunk

    monkeypatch.setattr(validator.os, "read", racing_read)
    with pytest.raises(validator.OperationModelV2ValidationError, match="changed"):
        validator.read_immutable(target, label="link-count race")


def test_semantic_api_requires_observed_bytes_for_sha_mode() -> None:
    model = validator.expected_model()
    with pytest.raises(validator.OperationModelV2ValidationError, match="requires observed"):
        validator.validate_value(model, enforce_frozen_sha=True)
