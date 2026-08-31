"""Adversarial tests for the role-10 sealed authentication mirror."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
BUILD_PATH = CODE / "build_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate.py"
VALIDATE_PATH = (
    CODE / "validate_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate.py"
)
ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


B = load_module("role10_sealed_mirror_builder_mutations", BUILD_PATH)
V = load_module("role10_sealed_mirror_validator_mutations", VALIDATE_PATH)

AUTHORITY_RELATIVES = (
    B.MEMBER_RELATIVE,
    B.CONFIGURATION_RELATIVE,
    B.FACTORIZATION_RELATIVE,
    B.INITIAL_BUNDLE_RELATIVE,
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def copy_file(source: Path, destination: Path, mode: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination.chmod(mode)


def make_source_root(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir(mode=0o700)
    manifest = json.loads((ARTIFACT / "manifest.json").read_text("ascii"))
    for relative in AUTHORITY_RELATIVES:
        copy_file(REPORT / relative, root / relative, 0o444)
    for entry in manifest["entries"]:
        relative = Path(entry["source_report_relative_path"])
        copy_file(REPORT / relative, root / relative, 0o644)
    return root


def clone_mirror(tmp_path: Path) -> Path:
    root = tmp_path / "mirror"
    shutil.copytree(ARTIFACT, root)
    return root


def unseal(root: Path) -> None:
    root.chmod(0o755)
    for path in root.rglob("*"):
        if path.is_symlink():
            continue
        path.chmod(0o755 if path.is_dir() else 0o644)


def seal(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        path.chmod(0o444)
    directories = [path for path in root.rglob("*") if path.is_dir() and not path.is_symlink()]
    for path in sorted(directories, key=lambda value: len(value.parts), reverse=True):
        path.chmod(0o555)
    root.chmod(0o555)


def mutate_manifest(root: Path, callback: Any) -> None:
    unseal(root)
    path = root / "manifest.json"
    value = json.loads(path.read_text("ascii"))
    callback(value)
    path.write_bytes(canonical(value))
    seal(root)


def test_coherent_redigest_of_mirrored_bytes_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    unseal(root)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text("ascii"))
    entry = manifest["entries"][1]
    target = root / entry["mirror_relative_path"]
    raw = target.read_bytes() + b"\n# coherent-redigest mutation\n"
    target.write_bytes(raw)
    entry["byte_length"] = len(raw)
    entry["sha256"] = hashlib.sha256(raw).hexdigest()
    manifest_path.write_bytes(canonical(manifest))
    seal(root)
    with pytest.raises(V.MirrorValidationError, match="semantic binding mismatch"):
        V.validate_mirror(root, REPORT)


def test_missing_entry_file_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text("ascii"))
    target = root / manifest["entries"][-1]["mirror_relative_path"]
    target.parent.chmod(0o755)
    target.unlink()
    target.parent.chmod(0o555)
    with pytest.raises(V.MirrorValidationError, match="secure open failed"):
        V.validate_mirror(root, REPORT)


def test_extra_entry_file_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    unseal(root)
    extra = root / "files/extra/not-authorized.bin"
    extra.parent.mkdir(parents=True, exist_ok=True)
    extra.write_bytes(b"not an accepted input")
    seal(root)
    with pytest.raises(V.MirrorValidationError, match="missing or extra"):
        V.validate_mirror(root, REPORT)


def test_manifest_reorder_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def reorder(value: dict[str, Any]) -> None:
        value["entries"][4], value["entries"][5] = value["entries"][5], value["entries"][4]

    mutate_manifest(root, reorder)
    with pytest.raises(V.MirrorValidationError, match="semantic binding mismatch"):
        V.validate_mirror(root, REPORT)


def test_manifest_path_traversal_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def traverse(value: dict[str, Any]) -> None:
        value["entries"][0]["mirror_relative_path"] = "files/../escape"

    mutate_manifest(root, traverse)
    with pytest.raises(V.MirrorValidationError):
        V.validate_mirror(root, REPORT)


def test_writable_mirror_file_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text("ascii"))
    target = root / manifest["entries"][0]["mirror_relative_path"]
    target.chmod(0o644)
    with pytest.raises(V.MirrorValidationError, match="mode/type/link-count"):
        V.validate_mirror(root, REPORT)


def test_writable_mirror_directory_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    target = root / "files"
    target.chmod(0o755)
    with pytest.raises(V.MirrorValidationError, match="directory is not mode 0555"):
        V.validate_mirror(root, REPORT)


def test_symlinked_mirror_entry_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text("ascii"))
    target = root / manifest["entries"][0]["mirror_relative_path"]
    replacement = root / manifest["entries"][1]["mirror_relative_path"]
    target.parent.chmod(0o755)
    target.unlink()
    target.symlink_to(replacement)
    target.parent.chmod(0o555)
    with pytest.raises(V.MirrorValidationError, match="secure open failed"):
        V.validate_mirror(root, REPORT)


def test_hardlinked_mirror_entry_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text("ascii"))
    source = root / manifest["entries"][0]["mirror_relative_path"]
    extra = source.with_name("unauthorized-hardlink")
    source.parent.chmod(0o755)
    os.link(source, extra)
    extra.chmod(0o444)
    source.parent.chmod(0o555)
    assert source.stat().st_nlink == 2
    with pytest.raises(V.MirrorValidationError, match="mode/type/link-count"):
        V.validate_mirror(root, REPORT)


def test_validator_detects_path_replacement_after_open(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text("ascii"))
    relative = PurePosixPath(manifest["entries"][0]["mirror_relative_path"])
    target = root / relative
    target.parent.chmod(0o755)
    triggered = False

    def replace_after_open(opened: PurePosixPath, _fd: int) -> None:
        nonlocal triggered
        if triggered or opened != relative:
            return
        triggered = True
        old = target.with_name(target.name + ".opened")
        target.rename(old)
        target.write_bytes(old.read_bytes())
        target.chmod(0o444)

    V._AFTER_MIRROR_OPEN_HOOK = replace_after_open
    try:
        with pytest.raises(V.MirrorValidationError, match="replaced while read"):
            V.validate_mirror(root, REPORT)
    finally:
        V._AFTER_MIRROR_OPEN_HOOK = None
    assert triggered


def test_builder_detects_source_path_replacement_after_open(tmp_path: Path) -> None:
    source_root = make_source_root(tmp_path)
    relative = PurePosixPath("code/rate_defined_tensor_f0.py")
    target = source_root / relative
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    triggered = False

    def replace_after_open(opened: PurePosixPath, _fd: int) -> None:
        nonlocal triggered
        if triggered or opened != relative:
            return
        triggered = True
        old = target.with_name(target.name + ".opened")
        target.rename(old)
        target.write_bytes(old.read_bytes())
        target.chmod(0o644)

    B._AFTER_SOURCE_OPEN_HOOK = replace_after_open
    try:
        with pytest.raises(
            B.MirrorBuildError, match="source changed while read|pathname was replaced"
        ):
            B.build_mirror(source_root, publication / "mirror")
    finally:
        B._AFTER_SOURCE_OPEN_HOOK = None
    assert triggered
    assert not (publication / "mirror").exists()


def test_builder_publication_replacement_race_is_no_replace(tmp_path: Path) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    output = publication / "mirror"
    triggered = False

    def publish_foreign(path: Path) -> None:
        nonlocal triggered
        triggered = True
        path.mkdir(mode=0o700)
        (path / "foreign-marker").write_text("foreign", encoding="ascii")

    B._BEFORE_PUBLISH_HOOK = publish_foreign
    try:
        with pytest.raises(B.MirrorBuildError, match="appeared concurrently"):
            B.build_mirror(source_root, output)
    finally:
        B._BEFORE_PUBLISH_HOOK = None
    assert triggered
    assert (output / "foreign-marker").read_text("ascii") == "foreign"
    assert not any(path.name.startswith(".mirror.stage-") for path in publication.iterdir())


def test_parent_rename_and_replacement_before_publish_fails_closed(
    tmp_path: Path,
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    displaced = tmp_path / "displaced-publication"
    output = publication / "mirror"

    def replace_parent(_path: Path) -> None:
        publication.rename(displaced)
        publication.mkdir(mode=0o700)
        output.mkdir(mode=0o700)
        (output / "foreign-marker").write_text("foreign", encoding="ascii")

    B._BEFORE_PUBLISH_HOOK = replace_parent
    try:
        with pytest.raises(
            B.MirrorBuildError, match="parent pathname was rebound before publication"
        ):
            B.build_mirror(source_root, output)
    finally:
        B._BEFORE_PUBLISH_HOOK = None
    assert (output / "foreign-marker").read_text("ascii") == "foreign"
    assert list(displaced.iterdir()) == []


def test_parent_replacement_after_publish_fails_before_acknowledgement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    displaced = tmp_path / "displaced-publication"
    output = publication / "mirror"
    rename_noreplace = B._rename_noreplace

    def publish_then_replace(parent_fd: int, source: str, destination: str) -> None:
        rename_noreplace(parent_fd, source, destination)
        publication.rename(displaced)
        publication.mkdir(mode=0o700)
        output.mkdir(mode=0o700)
        (output / "foreign-marker").write_text("foreign", encoding="ascii")

    monkeypatch.setattr(B, "_rename_noreplace", publish_then_replace)
    with pytest.raises(B.MirrorBuildError, match="parent pathname was rebound after publication"):
        B.build_mirror(source_root, output)
    assert (output / "foreign-marker").read_text("ascii") == "foreign"
    assert list(displaced.iterdir()) == []


def test_parent_replacement_after_acknowledgement_preserves_foreign_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    displaced = tmp_path / "displaced-publication"
    output = publication / "mirror"
    acknowledge = B._acknowledge

    def acknowledge_then_replace(
        parent_fd: int,
        output_name: str,
        owned_identity: tuple[int, int],
        entries: list[dict[str, Any]],
        manifest_raw: bytes,
    ) -> None:
        acknowledge(parent_fd, output_name, owned_identity, entries, manifest_raw)
        publication.rename(displaced)
        publication.mkdir(mode=0o700)
        output.mkdir(mode=0o700)
        (output / "foreign-marker").write_text("foreign", encoding="ascii")

    monkeypatch.setattr(B, "_acknowledge", acknowledge_then_replace)
    with pytest.raises(
        B.MirrorBuildError, match="parent pathname was rebound after acknowledgement"
    ):
        B.build_mirror(source_root, output)
    assert (output / "foreign-marker").read_text("ascii") == "foreign"
    assert list(displaced.iterdir()) == []


def test_acknowledgement_failure_rolls_back_owned_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    output = publication / "mirror"
    owned_identity: tuple[int, int] | None = None

    def fail_acknowledgement(
        _parent_fd: int,
        _output_name: str,
        identity: tuple[int, int],
        _entries: list[dict[str, Any]],
        _manifest_raw: bytes,
    ) -> None:
        nonlocal owned_identity
        owned_identity = identity
        raise B.MirrorBuildError("injected acknowledgement failure")

    monkeypatch.setattr(B, "_acknowledge", fail_acknowledgement)
    with pytest.raises(B.MirrorBuildError, match="injected acknowledgement failure"):
        B.build_mirror(source_root, output)
    assert owned_identity is not None
    assert not output.exists()
    assert not any(
        (value.st_dev, value.st_ino) == owned_identity
        for value in (path.stat() for path in publication.iterdir())
    )
    assert not any(path.name.startswith(".mirror.stage-") for path in publication.iterdir())


def test_keyboard_interrupt_during_acknowledgement_rolls_back_owned_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    output = publication / "mirror"
    owned_identity: tuple[int, int] | None = None

    def cancel_acknowledgement(
        _parent_fd: int,
        _output_name: str,
        identity: tuple[int, int],
        _entries: list[dict[str, Any]],
        _manifest_raw: bytes,
    ) -> None:
        nonlocal owned_identity
        owned_identity = identity
        raise KeyboardInterrupt

    monkeypatch.setattr(B, "_acknowledge", cancel_acknowledgement)
    with pytest.raises(KeyboardInterrupt):
        B.build_mirror(source_root, output)
    assert owned_identity is not None
    assert not output.exists()
    assert not any(
        (value.st_dev, value.st_ino) == owned_identity
        for value in (path.stat() for path in publication.iterdir())
    )
    assert not any(path.name.startswith(".mirror.stage-") for path in publication.iterdir())


def test_acknowledgement_foreign_replacement_preserved_owned_root_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    output = publication / "mirror"
    displaced = publication / "invocation-owned-displaced"
    owned_identity: tuple[int, int] | None = None

    def replace_then_fail(
        _parent_fd: int,
        _output_name: str,
        identity: tuple[int, int],
        _entries: list[dict[str, Any]],
        _manifest_raw: bytes,
    ) -> None:
        nonlocal owned_identity
        owned_identity = identity
        output.rename(displaced)
        output.mkdir(mode=0o700)
        (output / "foreign-marker").write_text("foreign", encoding="ascii")
        raise B.MirrorBuildError("injected foreign replacement")

    monkeypatch.setattr(B, "_acknowledge", replace_then_fail)
    with pytest.raises(B.MirrorBuildError, match="injected foreign replacement"):
        B.build_mirror(source_root, output)
    assert owned_identity is not None
    assert (output / "foreign-marker").read_text("ascii") == "foreign"
    assert not displaced.exists()
    assert (output.stat().st_dev, output.stat().st_ino) != owned_identity
    assert not any(
        (value.st_dev, value.st_ino) == owned_identity
        for value in (path.stat() for path in publication.iterdir())
    )
    assert not any(path.name.startswith(".mirror.stage-") for path in publication.iterdir())


def test_atomic_no_replace_primitive_unavailable_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = make_source_root(tmp_path)
    publication = tmp_path / "publication"
    publication.mkdir(mode=0o700)
    output = publication / "mirror"
    monkeypatch.setattr(B.ctypes, "CDLL", lambda *_args, **_kwargs: object())
    with pytest.raises(B.MirrorBuildError, match="atomic no-replace rename primitive unavailable"):
        B.build_mirror(source_root, output)
    assert not output.exists()
    assert not any(path.name.startswith(".mirror.stage-") for path in publication.iterdir())
    assert "os.rename(" not in BUILD_PATH.read_text("utf-8")


def test_forbidden_legacy_result_output_tree_is_rejected_without_reading_it(
    tmp_path: Path,
) -> None:
    root = clone_mirror(tmp_path)
    unseal(root)
    forbidden = (
        root / "files/artifacts/data/physical_production_killing_geometry_v1" / "bundle.json"
    )
    forbidden.parent.mkdir(parents=True, exist_ok=True)
    forbidden.write_bytes(b"synthetic marker only; not legacy bytes")
    seal(root)
    with pytest.raises(V.MirrorValidationError, match="missing or extra"):
        V.validate_mirror(root, REPORT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("entry_count", 41),
        ("status", "PASS"),
        ("schema", "wrong"),
    ],
)
def test_manifest_boundary_mutations_are_rejected(tmp_path: Path, field: str, value: Any) -> None:
    root = clone_mirror(tmp_path)

    def mutate(candidate: dict[str, Any]) -> None:
        candidate[field] = value

    mutate_manifest(root, mutate)
    with pytest.raises(V.MirrorValidationError, match=f"manifest {field} mismatch"):
        V.validate_mirror(root, REPORT)


def test_any_true_claim_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def promote(value: dict[str, Any]) -> None:
        value["claim_boundary"]["science_executed"] = True

    mutate_manifest(root, promote)
    with pytest.raises(V.MirrorValidationError, match="claim_boundary mismatch"):
        V.validate_mirror(root, REPORT)


def test_authority_hash_mutation_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def mutate(value: dict[str, Any]) -> None:
        value["accepted_authorities"]["member_v4"]["sha256"] = "0" * 64

    mutate_manifest(root, mutate)
    with pytest.raises(V.MirrorValidationError, match="accepted_authorities mismatch"):
        V.validate_mirror(root, REPORT)


def test_inventory_digest_mutation_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def mutate(value: dict[str, Any]) -> None:
        value["inventory_digests"]["member_v4_partition_inventory"]["sha256"] = "0" * 64

    mutate_manifest(root, mutate)
    with pytest.raises(V.MirrorValidationError, match="inventory_digests mismatch"):
        V.validate_mirror(root, REPORT)


def test_mirrored_initial_source_pin_mutation_is_rejected(tmp_path: Path) -> None:
    root = clone_mirror(tmp_path)

    def mutate(value: dict[str, Any]) -> None:
        value["mirrored_source_pin"]["sha256"] = "0" * 64

    mutate_manifest(root, mutate)
    with pytest.raises(V.MirrorValidationError, match="mirrored_source_pin mismatch"):
        V.validate_mirror(root, REPORT)


def test_authority_file_must_remain_immutable(tmp_path: Path) -> None:
    authority_root = tmp_path / "authorities"
    authority_root.mkdir(mode=0o700)
    for relative in AUTHORITY_RELATIVES:
        copy_file(REPORT / relative, authority_root / relative, 0o444)
    (authority_root / B.MEMBER_RELATIVE).chmod(0o644)
    with pytest.raises(V.MirrorValidationError, match="authority file mode"):
        V.validate_mirror(ARTIFACT, authority_root)


def test_generated_mirror_contains_no_forbidden_path_suffix() -> None:
    manifest = json.loads((ARTIFACT / "manifest.json").read_text("ascii"))
    paths = [entry["source_report_relative_path"] for entry in manifest["entries"]]
    assert all("physical_production_killing_geometry" not in path for path in paths)
    assert all("candidate_native_killing_factor_geometry" not in path for path in paths)
    assert all("/outputs/" not in f"/{path}/" for path in paths)
    assert all("/receipts/" not in f"/{path}/" for path in paths)
