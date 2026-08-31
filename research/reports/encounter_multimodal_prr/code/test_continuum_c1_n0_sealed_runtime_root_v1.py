from __future__ import annotations

import errno
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import materialize_continuum_c1_n0_sealed_runtime_root_v1 as materializer
import pytest
import validate_continuum_c1_n0_sealed_runtime_root_receipt_v1 as validator

TEST_INVENTORY_SCHEMA = "test_static_runtime_inventory_v1"
RELATIVE_LAYOUT = (
    ("bin/python3.12", 52_448, 0o555),
    ("site-packages/gmpy2/__init__.py", 412, 0o444),
    ("site-packages/gmpy2/gmpy2.cpython-312-darwin.so", 573_056, 0o444),
    ("site-packages/gmpy2.libs/libgmp.10.dylib", 468_768, 0o444),
    ("site-packages/gmpy2.libs/libmpfr.6.dylib", 469_360, 0o444),
    ("site-packages/gmpy2.libs/libmpc.3.dylib", 152_112, 0o444),
)


@pytest.fixture(autouse=True)
def _remove_bounded_tmp_tree_after_test(tmp_path: Path) -> Any:
    """Make test-owned sealed trees writable, then remove only this tmp_path."""

    yield
    if not tmp_path.exists():
        return
    for directory, directories, files in os.walk(tmp_path, topdown=False, followlinks=False):
        directory_path = Path(directory)
        for name in files:
            path = directory_path / name
            if path.is_symlink():
                continue
            try:
                path.chmod(0o600)
            except FileNotFoundError:
                pass
        for name in directories:
            path = directory_path / name
            if path.is_symlink():
                continue
            try:
                path.chmod(0o700)
            except FileNotFoundError:
                pass
        try:
            directory_path.chmod(0o700)
        except FileNotFoundError:
            pass
    shutil.rmtree(tmp_path)


class _StatView:
    def __init__(self, base: os.stat_result, changes: dict[str, int]) -> None:
        self._base = base
        self._changes = changes

    def __getattr__(self, name: str) -> Any:
        if name in self._changes:
            return self._changes[name]
        return getattr(self._base, name)


class TestCalls(materializer._SystemCalls):
    __test__ = False

    def __init__(
        self,
        *,
        hooks: dict[str, Callable[..., None]] | None = None,
        actual_acl: bool = True,
    ) -> None:
        self.hooks = hooks or {}
        self.actual_acl = actual_acl
        self.current_relative = ""
        self.stat_changes: dict[str, dict[str, int]] = {}
        self.xattr_paths: set[str] = set()
        self.acl_paths: set[str] = set()
        self.trace: list[tuple[str, object]] = []

    def event(self, name: str, **details: object) -> None:
        self.trace.append(("event", name))
        hook = self.hooks.get(name)
        if hook is not None:
            hook(**details)

    def adapt_stat(self, relative_path: str, value: os.stat_result) -> os.stat_result:
        self.current_relative = relative_path
        changes = self.stat_changes.get(relative_path, {})
        if "permission_mode" in changes:
            changes = dict(changes)
            permission_mode = changes.pop("permission_mode")
            changes["st_mode"] = (value.st_mode & ~0o7777) | permission_mode
        return _StatView(value, changes) if changes else value

    def list_xattrs(self, fd: int) -> tuple[bytes, ...]:
        del fd
        return (b"test.xattr",) if self.current_relative in self.xattr_paths else ()

    def clear_xattrs(self, fd: int) -> None:
        del fd

    def has_extended_acl(self, fd: int) -> bool:
        if self.current_relative in self.acl_paths:
            return True
        if self.actual_acl:
            return super().has_extended_acl(fd)
        return False

    def clear_extended_acl(self, fd: int) -> None:
        if self.current_relative in self.acl_paths:
            self.acl_paths.remove(self.current_relative)
            return
        super().clear_extended_acl(fd)

    def rename_exclusive(self, parent_fd: int, source: str, destination: str) -> None:
        self.trace.append(("rename_exclusive_flags", materializer.RENAME_FLAGS))
        super().rename_exclusive(parent_fd, source, destination)

    def fsync(self, fd: int) -> None:
        self.trace.append(("fsync", fd))
        super().fsync(fd)

    def fchmod(self, fd: int, mode: int) -> None:
        self.trace.append(("fchmod", mode))
        super().fchmod(fd, mode)

    def write(self, fd: int, raw: memoryview) -> int:
        self.trace.append(("write", len(raw)))
        return super().write(fd, raw)


class ValidationCalls(validator._ValidationCalls):
    def __init__(self, *, hooks: dict[str, Callable[..., None]] | None = None) -> None:
        self.hooks = hooks or {}
        self.current_relative = ""
        self.stat_changes: dict[str, dict[str, int]] = {}
        self.xattr_paths: set[str] = set()
        self.acl_paths: set[str] = set()

    def event(self, name: str, **details: object) -> None:
        hook = self.hooks.get(name)
        if hook is not None:
            hook(**details)

    def adapt_stat(self, relative_path: str, value: os.stat_result) -> os.stat_result:
        self.current_relative = relative_path
        changes = self.stat_changes.get(relative_path, {})
        if "permission_mode" in changes:
            changes = dict(changes)
            permission_mode = changes.pop("permission_mode")
            changes["st_mode"] = (value.st_mode & ~0o7777) | permission_mode
        return _StatView(value, changes) if changes else value

    def list_xattrs(self, fd: int) -> tuple[bytes, ...]:
        del fd
        return (b"test.xattr",) if self.current_relative in self.xattr_paths else ()

    def has_extended_acl(self, fd: int) -> bool:
        del fd
        return self.current_relative in self.acl_paths


class FaultCalls(TestCalls):
    def __init__(self, method: str, occurrence: int = 1) -> None:
        super().__init__()
        self.method = method
        self.occurrence = occurrence
        self.counts: dict[str, int] = {}

    def _hit(self, name: str) -> None:
        self.counts[name] = self.counts.get(name, 0) + 1
        if name == self.method and self.counts[name] == self.occurrence:
            raise OSError(errno.EIO, f"injected {name} failure")

    def write(self, fd: int, raw: memoryview) -> int:
        self._hit("write")
        return super().write(fd, raw)

    def fsync(self, fd: int) -> None:
        self._hit("fsync")
        super().fsync(fd)

    def fchmod(self, fd: int, mode: int) -> None:
        self._hit("fchmod")
        super().fchmod(fd, mode)

    def rename_exclusive(self, parent_fd: int, source: str, destination: str) -> None:
        self._hit("rename_exclusive")
        super().rename_exclusive(parent_fd, source, destination)


class StageCreationFaultCalls(TestCalls):
    """Inject one failure at a named stage-creation boundary."""

    def __init__(self, stage: Path, operation: str) -> None:
        super().__init__()
        self.stage = stage
        self.operation = operation
        self.fired = False

    def _matches_fd(self, fd: int) -> bool:
        if not self.stage.exists():
            return False
        value = os.fstat(fd)
        current = self.stage.stat()
        return (value.st_dev, value.st_ino) == (current.st_dev, current.st_ino)

    def mkdir(self, path: str, mode: int, *, dir_fd: int) -> None:
        if self.operation == "mkdir" and path == self.stage.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected stage mkdir failure")
        super().mkdir(path, mode, dir_fd=dir_fd)

    def stat(self, path: str, *, dir_fd: int) -> os.stat_result:
        value = super().stat(path, dir_fd=dir_fd)
        if self.operation == "stat" and path == self.stage.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected stage stat failure")
        return value

    def chmod(self, path: str, mode: int, *, dir_fd: int) -> None:
        if self.operation == "chmod" and path == self.stage.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected stage chmod failure")
        super().chmod(path, mode, dir_fd=dir_fd)

    def open(
        self,
        path: str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if self.operation == "open" and path == self.stage.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected stage open failure")
        return super().open(path, flags, mode, dir_fd=dir_fd)

    def fstat(self, fd: int) -> os.stat_result:
        value = super().fstat(fd)
        if self.operation == "fstat" and not self.fired and self._matches_fd(fd):
            self.fired = True
            raise OSError(errno.EIO, "injected stage fstat failure")
        return value

    def clear_xattrs(self, fd: int) -> None:
        if self.operation == "clear_xattrs" and not self.fired and self._matches_fd(fd):
            self.fired = True
            raise OSError(errno.EIO, "injected stage xattr failure")
        super().clear_xattrs(fd)


class NestedCreationFaultCalls(TestCalls):
    """Inject one failure while creating a known object below the stage."""

    def __init__(self, target: Path, operation: str) -> None:
        super().__init__()
        self.target = target
        self.operation = operation
        self.fired = False

    def _matches_fd(self, fd: int) -> bool:
        if not self.target.exists():
            return False
        value = os.fstat(fd)
        current = self.target.stat()
        return (value.st_dev, value.st_ino) == (current.st_dev, current.st_ino)

    def mkdir(self, path: str, mode: int, *, dir_fd: int) -> None:
        if self.operation == "mkdir" and path == self.target.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected nested mkdir failure")
        super().mkdir(path, mode, dir_fd=dir_fd)

    def stat(self, path: str, *, dir_fd: int) -> os.stat_result:
        value = super().stat(path, dir_fd=dir_fd)
        if self.operation == "stat" and path == self.target.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected nested stat failure")
        return value

    def chmod(self, path: str, mode: int, *, dir_fd: int) -> None:
        if self.operation == "chmod" and path == self.target.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected nested chmod failure")
        super().chmod(path, mode, dir_fd=dir_fd)

    def open(
        self,
        path: str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if self.operation == "open" and path == self.target.name and not self.fired:
            self.fired = True
            raise OSError(errno.EIO, "injected nested open failure")
        return super().open(path, flags, mode, dir_fd=dir_fd)

    def fstat(self, fd: int) -> os.stat_result:
        value = super().fstat(fd)
        if self.operation == "fstat" and not self.fired and self._matches_fd(fd):
            self.fired = True
            raise OSError(errno.EIO, "injected nested fstat failure")
        return value

    def clear_xattrs(self, fd: int) -> None:
        if self.operation == "clear_xattrs" and not self.fired and self._matches_fd(fd):
            self.fired = True
            raise OSError(errno.EIO, "injected nested xattr failure")
        super().clear_xattrs(fd)


@dataclass(frozen=True)
class Fixture:
    inventory: bytes
    materializer_config: materializer._Config
    validator_config: validator._ValidationConfig
    parent: Path
    root: Path
    sources: tuple[Path, ...]


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("ascii")


def _fixture(tmp_path: Path) -> Fixture:
    source_root = tmp_path / "sources"
    source_root.mkdir(mode=0o700)
    sources: list[Path] = []
    source_specs: list[materializer._SourceSpec] = []
    validation_files: list[validator._ExpectedFile] = []
    for index, (relative, size, mode) in enumerate(RELATIVE_LAYOUT):
        source = source_root / f"source-{index}"
        raw = bytes([65 + index]) * size
        source.write_bytes(raw)
        sources.append(source)
        digest = hashlib.sha256(raw).hexdigest()
        source_specs.append(
            materializer._SourceSpec(
                str(source),
                relative,
                size,
                digest,
                mode,
            )
        )
        validation_files.append(validator._ExpectedFile(relative, size, digest, mode))
    parent = tmp_path / "publication"
    parent.mkdir(mode=0o700)
    root = parent / "runtime-root"
    inventory = _canonical({"schema": TEST_INVENTORY_SCHEMA})
    config = materializer._Config(
        authority_root=str(root),
        publication_parent=str(parent),
        lock_name=".runtime-root.materialize-v1.lock",
        expected_uid=os.getuid(),
        expected_gid=os.getgid(),
        sources=tuple(source_specs),
        inventory_schema=TEST_INVENTORY_SCHEMA,
        inventory_byte_length=len(inventory),
        inventory_sha256=hashlib.sha256(inventory).hexdigest(),
        deterministic_stage_name=".runtime-root.stage-test",
    )
    validation_config = validator._ValidationConfig(
        authority_root=str(root),
        publication_parent=str(parent),
        lock_name=config.lock_name,
        expected_uid=os.getuid(),
        expected_gid=os.getgid(),
        files=tuple(validation_files),
        inventory_schema=TEST_INVENTORY_SCHEMA,
        inventory_byte_length=len(inventory),
        inventory_sha256=hashlib.sha256(inventory).hexdigest(),
    )
    return Fixture(
        inventory,
        config,
        validation_config,
        parent,
        root,
        tuple(sources),
    )


def _production_schema_inventory_for_fixture(fixture: Fixture) -> bytes:
    root = fixture.materializer_config.authority_root
    sources = fixture.materializer_config.sources

    def record(index: int) -> dict[str, str]:
        return {
            "path": f"{root}/{sources[index].relative_path}",
            "sha256": sources[index].sha256,
        }

    return _canonical(
        {
            "authority_root": root,
            "gmpy2": {
                "extension": record(2),
                "wrapper": record(1),
            },
            "numerical_libraries": [
                {"component": component, **record(index)}
                for component, index in (("gmp", 3), ("mpfr", 4), ("mpc", 5))
            ],
            "python": record(0),
            "schema": materializer.INVENTORY_SCHEMA,
        }
    )


def _materialize(
    fixture: Fixture,
    calls: TestCalls | None = None,
) -> tuple[bytes, TestCalls]:
    selected = calls or TestCalls()
    receipt = materializer._materialize_with_config(
        fixture.inventory,
        fixture.materializer_config,
        selected,
    )
    return receipt, selected


def _validate(
    fixture: Fixture,
    receipt: bytes,
    calls: ValidationCalls | None = None,
) -> dict[str, Any]:
    return validator._validate_with_config(
        receipt,
        fixture.inventory,
        fixture.validator_config,
        calls or ValidationCalls(),
    )


def _assert_hold(fixture: Fixture, calls: TestCalls | None = None) -> None:
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._materialize_with_config(
            fixture.inventory,
            fixture.materializer_config,
            calls or TestCalls(),
        )


def test_public_constants_pin_inventory_root_sources_hashes_sizes_and_modes() -> None:
    assert (
        materializer.INVENTORY_SCHEMA
        == validator.INVENTORY_SCHEMA
        == ("encounter_continuum_c1_n0_runtime_byte_pin_inventory_v1")
    )
    assert materializer.INVENTORY_BYTE_LENGTH == validator.INVENTORY_BYTE_LENGTH == 11_715
    assert (
        materializer.INVENTORY_SHA256
        == validator.INVENTORY_SHA256
        == ("13b70ec6194bbad62e19cea2538f19a8351e6f6ad820ac7a09d0adf25433b8c6")
    )
    assert materializer.AUTHORITY_ROOT == validator.AUTHORITY_ROOT
    assert len(materializer.PUBLIC_SOURCES) == 6
    assert sum(item.byte_length for item in materializer.PUBLIC_SOURCES) == 1_716_156
    assert materializer.PUBLIC_SOURCES[0].source_path.startswith("/opt/homebrew/Cellar/")
    assert all(
        item.source_path.startswith("/Users/ae23069/.local-build/valley-k-small/.venv/")
        for item in materializer.PUBLIC_SOURCES[1:]
    )
    assert all(
        "/Desktop/valley-k-small/.venv/" not in item.source_path
        for item in materializer.PUBLIC_SOURCES
    )
    assert [item.destination_mode for item in materializer.PUBLIC_SOURCES] == [
        0o555,
        0o444,
        0o444,
        0o444,
        0o444,
        0o444,
    ]
    assert materializer.RENAME_FLAGS == 0x14
    assert materializer.XATTR_SHOWCOMPRESSION == validator.XATTR_SHOWCOMPRESSION == 0x20


def test_public_and_private_apis_do_not_accept_caller_root_or_layout_parameters() -> None:
    assert materializer.materialize_sealed_runtime_root_v1.__annotations__ == {
        "static_inventory_bytes": "bytes",
        "return": "bytes",
    }
    assert validator.validate_sealed_runtime_root_receipt_v1.__annotations__ == {
        "receipt_bytes": "bytes",
        "static_inventory_bytes": "bytes",
        "return": "dict[str, Any]",
    }


def test_cli_is_inert_hold(capsys: pytest.CaptureFixture[str]) -> None:
    assert materializer.main() == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("HOLD_C1_N0_SEALED_RUNTIME_ROOT_V1:")


def test_missing_publication_parent_is_a_fail_closed_precondition(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    fixture.parent.rmdir()
    _assert_hold(fixture)
    assert not fixture.parent.exists()
    assert not fixture.root.exists()


def test_group_or_other_writable_publication_parent_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    fixture.parent.chmod(0o777)
    _assert_hold(fixture)
    assert not fixture.root.exists()


def test_caller_umask_cannot_leave_or_publish_mode_zero_objects(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    previous = os.umask(0o777)
    try:
        receipt, _ = _materialize(fixture)
    finally:
        os.umask(previous)
    _validate(fixture, receipt)
    assert fixture.root.stat().st_mode & 0o777 == 0o555
    assert all(path.stat().st_mode & 0o777 in {0o444, 0o555} for path in fixture.root.rglob("*"))


@pytest.mark.parametrize(
    "operation",
    ["mkdir", "stat", "chmod", "open", "fstat", "clear_xattrs"],
)
def test_stage_creation_faults_remove_stage_lock_and_root(
    tmp_path: Path,
    operation: str,
) -> None:
    fixture = _fixture(tmp_path)
    stage = fixture.parent / fixture.materializer_config.deterministic_stage_name
    calls = StageCreationFaultCalls(stage, operation)
    _assert_hold(fixture, calls)
    assert calls.fired
    assert not stage.exists()
    assert not fixture.root.exists()
    assert not (fixture.parent / fixture.materializer_config.lock_name).exists()


@pytest.mark.parametrize(
    ("relative", "operation"),
    [
        ("bin", "mkdir"),
        ("bin", "stat"),
        ("bin", "chmod"),
        ("bin", "open"),
        ("bin", "fstat"),
        ("bin", "clear_xattrs"),
        ("bin/python3.12", "fstat"),
        ("bin/python3.12", "clear_xattrs"),
    ],
)
def test_nested_creation_faults_under_restrictive_umask_leave_no_residue(
    tmp_path: Path,
    relative: str,
    operation: str,
) -> None:
    fixture = _fixture(tmp_path)
    stage = fixture.parent / fixture.materializer_config.deterministic_stage_name
    calls = NestedCreationFaultCalls(stage / relative, operation)
    previous = os.umask(0o777)
    try:
        _assert_hold(fixture, calls)
    finally:
        os.umask(previous)
    assert calls.fired
    assert not stage.exists()
    assert not fixture.root.exists()
    assert not (fixture.parent / fixture.materializer_config.lock_name).exists()


def test_happy_path_exact_tree_receipt_and_independent_validation(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    document = _validate(fixture, receipt)
    assert document["schema"] == materializer.RECEIPT_SCHEMA
    assert document["static_inventory"] == {
        "byte_length": len(fixture.inventory),
        "schema": TEST_INVENTORY_SCHEMA,
        "sha256": hashlib.sha256(fixture.inventory).hexdigest(),
    }
    assert document["summary"] == {
        "directory_count": 5,
        "file_count": 6,
        "total_file_bytes": 1_716_156,
    }
    assert [entry["path"] for entry in document["entries"]] == sorted(
        entry["path"] for entry in document["entries"]
    )
    assert len(document["entries"]) == 11
    assert all(
        {"dev", "ino", "mtime_ns", "ctime_ns", "path", "type", "mode", "uid", "gid", "nlink"}
        <= set(entry)
        for entry in document["entries"]
    )
    assert all(entry["nlink"] == 1 for entry in document["entries"] if entry["type"] == "file")
    assert (
        document["claim_boundary"][
            "historical_fsync_and_rename_attestation_independently_reproven_by_validator"
        ]
        is False
    )
    assert document["validator_scope"] == {
        "can_rebuild_current_tree_from_independent_fds": True,
        "cannot_independently_prove_historical_fsync_or_rename_syscalls": True,
        "does_not_read_or_claim_xattr_values": True,
    }
    assert not (fixture.parent / fixture.materializer_config.lock_name).exists()


def test_real_darwin_provenance_xattr_is_recorded_and_independently_validated(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    receipt = materializer._materialize_with_config(
        fixture.inventory,
        fixture.materializer_config,
        materializer._SystemCalls(),
    )
    document = validator._validate_with_config(
        receipt,
        fixture.inventory,
        fixture.validator_config,
        validator._ValidationCalls(),
    )
    observed = {name for entry in document["entries"] for name in entry["xattrs"]}
    assert "com.apple.provenance" in observed
    assert observed <= {"com.apple.provenance"}
    assert document["materializer"]["permitted_os_managed_xattr_names"] == ["com.apple.provenance"]
    assert document["claim_boundary"]["xattr_values_claimed"] is False


def test_second_invocation_is_hold_and_preserves_first_root(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    identity = (fixture.root.stat().st_dev, fixture.root.stat().st_ino)
    _assert_hold(fixture)
    assert (fixture.root.stat().st_dev, fixture.root.stat().st_ino) == identity
    _validate(fixture, receipt)


@pytest.mark.parametrize("mutation", ["hash", "size", "symlink", "hardlink"])
def test_source_hash_size_symlink_and_hardlink_are_rejected(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _fixture(tmp_path)
    source = fixture.sources[1]
    if mutation == "hash":
        raw = source.read_bytes()
        source.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    elif mutation == "size":
        source.write_bytes(source.read_bytes() + b"x")
    elif mutation == "symlink":
        source.unlink()
        source.symlink_to(fixture.sources[2])
    else:
        os.link(source, source.with_name("source-hardlink"))
    _assert_hold(fixture)
    assert not fixture.root.exists()


def test_source_parent_component_symlink_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    real_parent = fixture.sources[0].parent
    symlink_parent = tmp_path / "source-link"
    symlink_parent.symlink_to(real_parent, target_is_directory=True)
    specs = list(fixture.materializer_config.sources)
    specs[0] = materializer._SourceSpec(
        str(symlink_parent / fixture.sources[0].name),
        specs[0].relative_path,
        specs[0].byte_length,
        specs[0].sha256,
        specs[0].destination_mode,
    )
    changed = materializer._Config(
        **{
            **fixture.materializer_config.__dict__,
            "sources": tuple(specs),
        }
    )
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._materialize_with_config(fixture.inventory, changed, TestCalls())


@pytest.mark.parametrize("mutation", ["content", "hardlink", "pathname"])
def test_concurrent_source_mutation_is_detected_on_same_fd_and_path(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _fixture(tmp_path)
    target = fixture.sources[0]
    fired = False

    def hook(**details: object) -> None:
        nonlocal fired
        spec = details["spec"]
        if (
            fired
            or not isinstance(spec, materializer._SourceSpec)
            or spec.source_path != str(target)
        ):
            return
        fired = True
        if mutation == "content":
            with target.open("r+b") as stream:
                stream.write(b"Z")
                stream.flush()
                os.fsync(stream.fileno())
        elif mutation == "hardlink":
            os.link(target, target.with_name("concurrent-hardlink"))
        else:
            backup = target.with_name("source-replaced")
            target.rename(backup)
            target.write_bytes(backup.read_bytes())

    _assert_hold(fixture, TestCalls(hooks={"after_source_open": hook}))
    assert fired
    assert not fixture.root.exists()


def test_publication_parent_symlink_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    link = tmp_path / "publication-link"
    link.symlink_to(fixture.parent, target_is_directory=True)
    root = link / fixture.root.name
    config = materializer._Config(
        **{
            **fixture.materializer_config.__dict__,
            "authority_root": str(root),
            "publication_parent": str(link),
        }
    )
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._materialize_with_config(fixture.inventory, config, TestCalls())


@pytest.mark.parametrize("kind", ["lock", "stage", "final"])
def test_lock_stage_and_final_preexistence_are_hold(
    tmp_path: Path,
    kind: str,
) -> None:
    fixture = _fixture(tmp_path)
    if kind == "lock":
        target = fixture.parent / fixture.materializer_config.lock_name
        target.write_text("foreign")
    elif kind == "stage":
        target = fixture.parent / fixture.materializer_config.deterministic_stage_name
        target.mkdir()
    else:
        target = fixture.root
        target.mkdir()
    _assert_hold(fixture)
    assert target.exists()


def test_rename_eexist_preserves_foreign_final_and_removes_owned_stage(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)

    def appear(**_details: object) -> None:
        fixture.root.mkdir()
        (fixture.root / "foreign").write_text("preserve")

    _assert_hold(fixture, TestCalls(hooks={"before_publish": appear}))
    assert (fixture.root / "foreign").read_text() == "preserve"
    assert not (fixture.parent / ".runtime-root.stage-test").exists()


def test_rename_unavailable_has_no_ordinary_rename_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path)

    class Unavailable(TestCalls):
        def rename_exclusive(self, parent_fd: int, source: str, destination: str) -> None:
            del parent_fd, source, destination
            raise OSError(errno.ENOSYS, "renameatx_np unavailable")

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("ordinary rename fallback was called")

    monkeypatch.setattr(os, "rename", forbidden)
    _assert_hold(fixture, Unavailable())
    assert not fixture.root.exists()


@pytest.mark.parametrize(
    ("method", "occurrence"),
    [
        ("write", 1),
        ("fsync", 2),
        ("fchmod", 1),
        ("rename_exclusive", 1),
    ],
)
def test_write_fsync_chmod_and_publish_failures_roll_back_owned_tree(
    tmp_path: Path,
    method: str,
    occurrence: int,
) -> None:
    fixture = _fixture(tmp_path)
    _assert_hold(fixture, FaultCalls(method, occurrence))
    assert not fixture.root.exists()
    assert not (fixture.parent / ".runtime-root.stage-test").exists()


def test_parent_path_replacement_is_detected_and_foreign_parent_preserved(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    moved = tmp_path / "publication-owned-moved"

    def replace_parent(**_details: object) -> None:
        fixture.parent.rename(moved)
        fixture.parent.mkdir(mode=0o700)
        (fixture.parent / "foreign").write_text("preserve")

    _assert_hold(fixture, TestCalls(hooks={"before_publish": replace_parent}))
    assert (fixture.parent / "foreign").read_text() == "preserve"
    assert not (moved / ".runtime-root.stage-test").exists()


def test_foreign_root_replacement_after_publish_is_preserved(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    moved = fixture.parent / ".owned-runtime-moved"

    def replace_root(**_details: object) -> None:
        fixture.root.rename(moved)
        fixture.root.mkdir()
        (fixture.root / "foreign").write_text("preserve")

    _assert_hold(fixture, TestCalls(hooks={"after_publish": replace_root}))
    assert (fixture.root / "foreign").read_text() == "preserve"
    assert not moved.exists()


def test_foreign_injection_inside_owned_root_is_preserved_on_incomplete_rollback(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)

    def inject(**_details: object) -> None:
        fixture.root.chmod(0o700)
        (fixture.root / "foreign-injected").write_text("preserve")
        fixture.root.chmod(0o555)

    _assert_hold(fixture, TestCalls(hooks={"after_publish": inject}))
    assert (fixture.root / "foreign-injected").read_text() == "preserve"


def test_foreign_file_replacement_inside_owned_root_is_preserved(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    target = fixture.root / "bin/python3.12"

    def replace_file(**_details: object) -> None:
        target.parent.chmod(0o700)
        target.rename(target.parent / ".owned-python-moved")
        target.write_bytes(b"foreign")
        target.chmod(0o555)
        target.parent.chmod(0o555)

    _assert_hold(fixture, TestCalls(hooks={"after_publish": replace_file}))
    assert target.read_bytes() == b"foreign"


def test_foreign_hardlink_alias_to_owned_file_is_preserved_on_hold(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    target = fixture.root / "bin/python3.12"
    alias = fixture.root / "foreign-hardlink-alias"

    def inject_alias(**_details: object) -> None:
        fixture.root.chmod(0o700)
        os.link(target, alias)
        fixture.root.chmod(0o555)

    _assert_hold(fixture, TestCalls(hooks={"after_publish": inject_alias}))
    assert target.exists()
    assert alias.exists()
    assert target.stat().st_ino == alias.stat().st_ino


def test_lock_replacement_before_success_is_hold_foreign_preserved_owned_removed(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    lock = fixture.parent / fixture.materializer_config.lock_name
    moved = fixture.parent / ".owned-lock-moved"

    def replace_lock(**_details: object) -> None:
        lock.rename(moved)
        lock.write_text("foreign-lock")

    _assert_hold(
        fixture,
        TestCalls(hooks={"before_success_lock_removal": replace_lock}),
    )
    assert lock.read_text() == "foreign-lock"
    assert not moved.exists()
    assert not fixture.root.exists()


def test_foreign_hardlink_alias_to_lock_is_preserved_and_forces_hold(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    lock = fixture.parent / fixture.materializer_config.lock_name
    alias = fixture.parent / ".foreign-lock-hardlink"

    def alias_lock(**_details: object) -> None:
        os.link(lock, alias)

    _assert_hold(
        fixture,
        TestCalls(hooks={"before_success_lock_removal": alias_lock}),
    )
    assert lock.exists()
    assert alias.exists()
    assert lock.stat().st_ino == alias.stat().st_ino
    assert not fixture.root.exists()


def test_nested_directory_swap_during_ack_is_detected_and_foreign_preserved(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    fired = False
    target = fixture.root / "site-packages/gmpy2"
    moved = fixture.root / "site-packages/.owned-gmpy2-moved"

    def swap(**details: object) -> None:
        nonlocal fired
        if fired or details.get("relative") != "site-packages/gmpy2":
            return
        fired = True
        target.parent.chmod(0o700)
        target.rename(moved)
        target.mkdir()
        (target / "foreign").write_text("preserve")
        target.chmod(0o555)
        target.parent.chmod(0o555)

    _assert_hold(fixture, TestCalls(hooks={"after_ack_directory_open": swap}))
    assert fired
    assert (target / "foreign").read_text() == "preserve"


@pytest.mark.parametrize("mutation", ["extra", "missing", "mode", "replacement"])
def test_independent_validator_rejects_live_tree_mutations(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    target = fixture.root / "site-packages/gmpy2/__init__.py"
    if mutation == "extra":
        fixture.root.chmod(0o700)
        (fixture.root / "extra").write_text("x")
        fixture.root.chmod(0o555)
    elif mutation == "missing":
        target.parent.chmod(0o700)
        target.unlink()
        target.parent.chmod(0o555)
    elif mutation == "mode":
        target.chmod(0o644)
    else:
        raw = target.read_bytes()
        target.parent.chmod(0o700)
        target.unlink()
        target.write_bytes(raw)
        target.chmod(0o444)
        target.parent.chmod(0o555)
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt)


@pytest.mark.parametrize(
    ("kind", "relative"),
    [
        ("uid", "."),
        ("gid", "bin/python3.12"),
        ("nlink", "site-packages/gmpy2/__init__.py"),
        ("mode", "site-packages/gmpy2.libs"),
        ("flags", "site-packages"),
        ("xattr", "site-packages/gmpy2"),
        ("acl", "bin"),
    ],
)
def test_independent_validator_rejects_metadata_xattr_acl_and_flags(
    tmp_path: Path,
    kind: str,
    relative: str,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    calls = ValidationCalls()
    if kind == "xattr":
        calls.xattr_paths.add(relative)
    elif kind == "acl":
        calls.acl_paths.add(relative)
    else:
        changes: dict[str, int]
        if kind == "uid":
            changes = {"st_uid": os.getuid() + 1}
        elif kind == "gid":
            changes = {"st_gid": os.getgid() + 1}
        elif kind == "nlink":
            changes = {"st_nlink": 2}
        elif kind == "mode":
            changes = {"permission_mode": 0o755}
        else:
            changes = {"st_flags": 1}
        calls.stat_changes[relative] = changes
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt, calls)


def test_materializer_ack_rejects_injected_uid_gid_nlink_xattr_acl_and_flags(
    tmp_path: Path,
) -> None:
    mutations: list[tuple[str, str, int | None]] = [
        ("uid", "bin/python3.12", os.getuid() + 1),
        ("gid", "site-packages/gmpy2/__init__.py", os.getgid() + 1),
        ("nlink", "site-packages/gmpy2.libs/libgmp.10.dylib", 2),
        ("flags", "site-packages/gmpy2", 1),
        ("xattr", "site-packages", None),
        ("acl", "bin", None),
    ]
    for kind, relative, value in mutations:
        case_root = tmp_path / kind
        case_root.mkdir()
        isolated = _fixture(case_root)
        calls = TestCalls(actual_acl=False)
        if kind == "xattr":
            calls.xattr_paths.add(relative)
        elif kind == "acl":
            calls.acl_paths.add(relative)
        else:
            field = {
                "uid": "st_uid",
                "gid": "st_gid",
                "nlink": "st_nlink",
                "flags": "st_flags",
            }[kind]
            assert value is not None
            calls.stat_changes[relative] = {field: value}
        _assert_hold(isolated, calls)
        assert not isolated.root.exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.__setitem__("schema", "forged"),
        lambda d: d.__setitem__("status", "PASS"),
        lambda d: d.__setitem__("probe", {"status": "PASS"}),
        lambda d: d.__setitem__("result_sha256", "0" * 64),
        lambda d: d["static_inventory"].__setitem__("sha256", "0" * 64),
        lambda d: d["authority_root"].__setitem__("ino", d["authority_root"]["ino"] + 1),
        lambda d: d["entries"][0].__setitem__("ino", d["entries"][0]["ino"] + 1),
        lambda d: d["entries"][1].__setitem__("mtime_ns", 0),
        lambda d: d["materializer"].__setitem__("atomic_publish_flags", 4),
        lambda d: d["materializer"].__setitem__("no_ordinary_rename_fallback", False),
        lambda d: d["claim_boundary"].__setitem__(
            "historical_fsync_and_rename_attestation_independently_reproven_by_validator",
            True,
        ),
        lambda d: d["validator_scope"].__setitem__(
            "cannot_independently_prove_historical_fsync_or_rename_syscalls",
            False,
        ),
    ],
)
def test_receipt_mutations_probe_result_and_overclaims_are_rejected(
    tmp_path: Path,
    mutate: Callable[[dict[str, Any]], Any],
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    document = json.loads(receipt)
    mutate(document)
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, _canonical(document))


@pytest.mark.parametrize("mutation", ["byte", "schema", "duplicate", "nonbytes"])
def test_inventory_mutations_are_rejected_before_materialization(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _fixture(tmp_path)
    raw: object
    if mutation == "byte":
        raw = fixture.inventory.replace(b"test_", b"Test_", 1)
    elif mutation == "schema":
        raw = _canonical({"schema": "forged"})
    elif mutation == "duplicate":
        raw = b'{\n  "schema": "a",\n  "schema": "b"\n}\n'
    else:
        raw = bytearray(fixture.inventory)
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._materialize_with_config(  # type: ignore[arg-type]
            raw,
            fixture.materializer_config,
            TestCalls(),
        )
    assert not fixture.root.exists()


def test_authenticated_inventory_is_semantically_joined_to_both_tree_configs(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    inventory = _production_schema_inventory_for_fixture(fixture)
    pin = {
        "inventory_schema": materializer.INVENTORY_SCHEMA,
        "inventory_byte_length": len(inventory),
        "inventory_sha256": hashlib.sha256(inventory).hexdigest(),
    }
    materializer_config = materializer._Config(**{**fixture.materializer_config.__dict__, **pin})
    validator_config = validator._ValidationConfig(**{**fixture.validator_config.__dict__, **pin})
    materializer._decode_inventory(inventory, materializer_config)
    validator._decode_inventory(inventory, validator_config)

    changed_sources = list(materializer_config.sources)
    changed_sources[0] = materializer._SourceSpec(
        **{
            **changed_sources[0].__dict__,
            "relative_path": "bin/python3.12.changed",
        }
    )
    changed_sources[1] = materializer._SourceSpec(
        **{
            **changed_sources[1].__dict__,
            "relative_path": "site-packages/gmpy2/__init__.changed.py",
        }
    )
    changed_files = list(validator_config.files)
    changed_files[0] = validator._ExpectedFile(
        **{
            **changed_files[0].__dict__,
            "relative_path": "bin/python3.12.changed",
        }
    )
    changed_files[1] = validator._ExpectedFile(
        **{
            **changed_files[1].__dict__,
            "relative_path": "site-packages/gmpy2/__init__.changed.py",
        }
    )
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._decode_inventory(
            inventory,
            materializer._Config(
                **{
                    **materializer_config.__dict__,
                    "sources": tuple(changed_sources),
                }
            ),
        )
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        validator._decode_inventory(
            inventory,
            validator._ValidationConfig(
                **{
                    **validator_config.__dict__,
                    "files": tuple(changed_files),
                }
            ),
        )


@pytest.mark.parametrize(
    "mutation",
    ["authority_root", "python_digest", "library_path", "library_digest"],
)
def test_inventory_semantic_join_rejects_root_and_file_map_mutations(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _fixture(tmp_path)
    document = json.loads(_production_schema_inventory_for_fixture(fixture))
    if mutation == "authority_root":
        document["authority_root"] += ".changed"
    elif mutation == "python_digest":
        document["python"]["sha256"] = "0" * 64
    elif mutation == "library_path":
        document["numerical_libraries"][0]["path"] += ".changed"
    else:
        document["numerical_libraries"][2]["sha256"] = "f" * 64
    inventory = _canonical(document)
    pin = {
        "inventory_schema": materializer.INVENTORY_SCHEMA,
        "inventory_byte_length": len(inventory),
        "inventory_sha256": hashlib.sha256(inventory).hexdigest(),
    }
    with pytest.raises(materializer.SealedRuntimeRootMaterializationFailure):
        materializer._decode_inventory(
            inventory,
            materializer._Config(**{**fixture.materializer_config.__dict__, **pin}),
        )
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        validator._decode_inventory(
            inventory,
            validator._ValidationConfig(**{**fixture.validator_config.__dict__, **pin}),
        )


def test_duplicate_and_noncanonical_receipts_are_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    duplicate = receipt.replace(
        b'{\n  "authority_root"',
        b'{\n  "schema": "duplicate",\n  "authority_root"',
        1,
    )
    for raw in (duplicate, receipt.rstrip(b"\n"), b"\xef\xbb\xbf" + receipt):
        with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
            _validate(fixture, raw)


def test_validator_authenticates_inventory_bytes_not_only_receipt_pin(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    mutated = fixture.inventory.replace(b"test_", b"Test_", 1)
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        validator._validate_with_config(
            receipt,
            mutated,
            fixture.validator_config,
            ValidationCalls(),
        )


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":' + b"[" * 2_000 + b"0" + b"]" * 2_000 + b"}",
        b'{"x":' + b"9" * 5_000 + b"}",
    ],
)
def test_validator_normalizes_pathological_json_to_hold(
    tmp_path: Path,
    raw: bytes,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    assert receipt
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        validator._validate_with_config(
            raw,
            fixture.inventory,
            fixture.validator_config,
            ValidationCalls(),
        )


def test_validator_rejects_live_and_concurrently_appearing_fixed_lock(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    lock = fixture.parent / fixture.materializer_config.lock_name
    lock.write_text("stale")
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt)
    lock.unlink()

    def appear(**_details: object) -> None:
        lock.write_text("concurrent")

    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(
            fixture,
            receipt,
            ValidationCalls(hooks={"before_parent_postcheck": appear}),
        )


def test_validator_rejects_publication_parent_path_rebind(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    moved = tmp_path / "publication-validator-moved"

    def rebind(**_details: object) -> None:
        fixture.parent.rename(moved)
        fixture.parent.mkdir(mode=0o700)
        (fixture.parent / "foreign").write_text("preserve")

    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(
            fixture,
            receipt,
            ValidationCalls(hooks={"before_parent_postcheck": rebind}),
        )
    assert (fixture.parent / "foreign").read_text() == "preserve"


def test_materializer_rejects_late_fixed_root_replacement_after_ack(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    moved = fixture.parent / ".owned-root-after-ack"

    def replace(**_details: object) -> None:
        fixture.root.rename(moved)
        fixture.root.mkdir()
        (fixture.root / "foreign").write_text("preserve")

    _assert_hold(fixture, TestCalls(hooks={"after_ack": replace}))
    assert (fixture.root / "foreign").read_text() == "preserve"
    assert not moved.exists()


def test_validator_rejects_late_fixed_root_replacement(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    moved = fixture.parent / ".validator-owned-root-moved"

    def replace(**_details: object) -> None:
        fixture.root.rename(moved)
        fixture.root.mkdir()
        (fixture.root / "foreign").write_text("preserve")

    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(
            fixture,
            receipt,
            ValidationCalls(hooks={"before_parent_postcheck": replace}),
        )
    assert (fixture.root / "foreign").read_text() == "preserve"


def test_parent_acl_and_flags_are_rejected_by_materializer_and_validator(
    tmp_path: Path,
) -> None:
    materializer_case = tmp_path / "materializer"
    materializer_case.mkdir()
    fixture = _fixture(materializer_case)
    parent_identity = (fixture.parent.stat().st_dev, fixture.parent.stat().st_ino)

    class ParentAclCalls(TestCalls):
        def has_extended_acl(self, fd: int) -> bool:
            value = os.fstat(fd)
            if (value.st_dev, value.st_ino) == parent_identity:
                return True
            return super().has_extended_acl(fd)

    _assert_hold(fixture, ParentAclCalls())
    assert not fixture.root.exists()

    materializer_flags_case = tmp_path / "materializer-flags"
    materializer_flags_case.mkdir()
    fixture = _fixture(materializer_flags_case)
    parent_identity = (fixture.parent.stat().st_dev, fixture.parent.stat().st_ino)

    class ParentFlagMaterializerCalls(TestCalls):
        def fstat(self, fd: int) -> os.stat_result:
            value = super().fstat(fd)
            if (value.st_dev, value.st_ino) == parent_identity:
                return _StatView(value, {"st_flags": 1})  # type: ignore[return-value]
            return value

    _assert_hold(fixture, ParentFlagMaterializerCalls())
    assert not fixture.root.exists()

    validator_flags_case = tmp_path / "validator-flags"
    validator_flags_case.mkdir()
    fixture = _fixture(validator_flags_case)
    receipt, _ = _materialize(fixture)
    parent_identity = (fixture.parent.stat().st_dev, fixture.parent.stat().st_ino)

    class ParentFlagCalls(ValidationCalls):
        def fstat(self, fd: int) -> os.stat_result:
            value = super().fstat(fd)
            if (value.st_dev, value.st_ino) == parent_identity:
                return _StatView(value, {"st_flags": 1})  # type: ignore[return-value]
            return value

    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt, ParentFlagCalls())

    validator_acl_case = tmp_path / "validator-acl"
    validator_acl_case.mkdir()
    fixture = _fixture(validator_acl_case)
    receipt, _ = _materialize(fixture)
    parent_identity = (fixture.parent.stat().st_dev, fixture.parent.stat().st_ino)

    class ParentAclValidationCalls(ValidationCalls):
        def has_extended_acl(self, fd: int) -> bool:
            value = os.fstat(fd)
            return (value.st_dev, value.st_ino) == parent_identity

    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt, ParentAclValidationCalls())


def test_file_security_inspection_mutation_is_detected_by_final_recheck(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    target = fixture.root / "bin/python3.12"

    class MutatingSecurityCalls(ValidationCalls):
        def __init__(self) -> None:
            super().__init__()
            self.fired = False

        def has_extended_acl(self, fd: int) -> bool:
            result = super().has_extended_acl(fd)
            if self.current_relative == "bin/python3.12" and not self.fired:
                self.fired = True
                target.chmod(0o755)
                target.chmod(0o555)
            return result

    calls = MutatingSecurityCalls()
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt, calls)
    assert calls.fired


def test_materializer_final_root_metadata_mutation_is_detected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)

    def mutate(**_details: object) -> None:
        fixture.root.chmod(0o755)
        fixture.root.chmod(0o555)

    _assert_hold(
        fixture,
        TestCalls(hooks={"before_ack_root_final_path_check": mutate}),
    )
    assert not fixture.root.exists()


def test_syscall_trace_has_exact_exclusive_publish_and_ordered_durability(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    receipt, calls = _materialize(fixture)
    _validate(fixture, receipt)
    assert calls.trace.count(("rename_exclusive_flags", 0x14)) == 1
    rename_index = calls.trace.index(("rename_exclusive_flags", 0x14))
    before = calls.trace[:rename_index]
    after = calls.trace[rename_index + 1 :]
    assert sum(name == "write" for name, _ in before) == 6
    assert sum(name == "fchmod" and value in {0o444, 0o555} for name, value in before) >= 11
    assert any(name == "fsync" for name, _ in after)
    event_names = [value for name, value in calls.trace if name == "event"]
    assert event_names.index("before_publish") < event_names.index("after_publish")
    assert event_names.index("after_publish") < event_names.index("before_ack")
    assert event_names.index("before_ack") < event_names.index("after_ack")


def test_real_darwin_no_acl_temp_fd_does_not_call_failing_acl_delete(
    tmp_path: Path,
) -> None:
    path = tmp_path / "no-acl"
    path.write_bytes(b"x")
    fd = os.open(path, os.O_RDWR)
    calls = materializer._SystemCalls()
    try:
        assert calls.has_extended_acl(fd) is False
        materializer._prepare_owned_fd(calls, fd)
        assert calls.has_extended_acl(fd) is False
    finally:
        os.close(fd)


def test_validator_detects_nested_directory_swap_after_fd_open(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt, _ = _materialize(fixture)
    target = fixture.root / "site-packages/gmpy2.libs"
    moved = fixture.root / "site-packages/.gmpy2-libs-moved"
    fired = False

    def swap(**details: object) -> None:
        nonlocal fired
        if fired or details.get("relative") != "site-packages/gmpy2.libs":
            return
        fired = True
        target.parent.chmod(0o700)
        target.rename(moved)
        target.mkdir()
        target.chmod(0o555)
        target.parent.chmod(0o555)

    calls = ValidationCalls(hooks={"after_directory_open": swap})
    with pytest.raises(validator.SealedRuntimeRootReceiptValidationFailure):
        _validate(fixture, receipt, calls)
    assert fired
