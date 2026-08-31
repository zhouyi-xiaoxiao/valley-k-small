"""Main tests for the role-10 sealed authentication-closure mirror."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
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


B = load_module("role10_sealed_mirror_builder_main", BUILD_PATH)
V = load_module("role10_sealed_mirror_validator_main", VALIDATE_PATH)

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


def make_authority_only_root(tmp_path: Path) -> Path:
    root = tmp_path / "authority-only"
    root.mkdir(mode=0o700)
    for relative in AUTHORITY_RELATIVES:
        copy_file(REPORT / relative, root / relative, 0o444)
    return root


def tree_modes(root: Path) -> tuple[set[int], set[int]]:
    directory_modes: set[int] = {stat.S_IMODE(root.stat().st_mode)}
    file_modes: set[int] = set()
    for directory, directories, files in os.walk(root):
        for name in directories:
            directory_modes.add(stat.S_IMODE((Path(directory) / name).stat().st_mode))
        for name in files:
            file_modes.add(stat.S_IMODE((Path(directory) / name).stat().st_mode))
    return directory_modes, file_modes


def test_checked_in_mirror_validates_and_has_exact_boundary() -> None:
    manifest = V.validate_mirror(ARTIFACT, REPORT)
    assert manifest["schema"] == B.SCHEMA == V.SCHEMA
    assert manifest["status"] == B.STATUS == V.STATUS
    assert manifest["entry_count"] == 40
    assert len(manifest["entries"]) == 40
    assert all(value is False for value in manifest["claim_boundary"].values())
    assert set(manifest["claim_boundary"]) == set(B.CLAIM_KEYS)
    assert manifest["coverage"] == {
        "configuration_authority_lineage_file_count": 3,
        "configuration_initial_geometry_file_count": 1,
        "exact_writable_precommit_input_closure_mirrored": True,
        "member_v4_partition_file_count": 36,
        "original_report_relative_suffix_preserved_under_files": True,
        "standalone_content_addressed_validation_without_original_writable_sources": True,
    }
    assert all(manifest["exclusions"].values())


def test_exact_order_semantics_hashes_and_suffixes() -> None:
    manifest = json.loads((ARTIFACT / "manifest.json").read_text("ascii"))
    entries = manifest["entries"]
    assert [entry["semantic_role"] for entry in entries[:4]] == [
        "configuration_design",
        "configuration_implementation",
        "configuration_test",
        "configuration_initial_geometry",
    ]
    partitions = entries[4:]
    assert len(partitions) == 36
    assert [entry["ordinal"] for entry in entries] == list(range(40))
    assert [(entry["configuration_index"], entry["coordinate"]) for entry in partitions] == [
        (index, coordinate)
        for index in range(12)
        for coordinate in ("midpoint", "relative_parallel", "relative_perpendicular")
    ]
    for entry in entries:
        assert entry["mirror_relative_path"] == ("files/" + entry["source_report_relative_path"])
        raw = (ARTIFACT / entry["mirror_relative_path"]).read_bytes()
        assert len(raw) == entry["byte_length"]
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]


def test_manifest_binds_all_accepted_authorities_and_inventories() -> None:
    manifest = json.loads((ARTIFACT / "manifest.json").read_text("ascii"))
    accepted = manifest["accepted_authorities"]
    assert accepted["member_v4"]["sha256"] == B.MEMBER_SHA256
    assert accepted["member_v4"]["member_identity_sha256"] == B.MEMBER_IDENTITY_SHA256
    assert accepted["configuration"]["sha256"] == B.CONFIGURATION_SHA256
    assert accepted["factorization_v2"]["sha256"] == B.FACTORIZATION_SHA256
    assert accepted["initial_partition_bundle"]["sha256"] == B.INITIAL_BUNDLE_SHA256
    assert manifest["mirrored_source_pin"]["sha256"] == B.INITIAL_GEOMETRY_SHA256
    assert (
        manifest["inventory_digests"]["configuration_row_inventory"]["sha256"]
        == B.CONFIGURATION_INVENTORY_SHA256
    )
    assert (
        manifest["inventory_digests"]["member_v4_partition_inventory"]["sha256"]
        == B.PARTITION_INVENTORY_SHA256
    )


def test_mirror_is_fully_sealed_and_single_linked() -> None:
    directory_modes, file_modes = tree_modes(ARTIFACT)
    assert directory_modes == {0o555}
    assert file_modes == {0o444}
    for path in ARTIFACT.rglob("*"):
        assert not path.is_symlink()
        if path.is_file():
            assert path.stat().st_nlink == 1
    assert len([path for path in ARTIFACT.rglob("*") if path.is_file()]) == 41


def test_builder_publishes_under_preexisting_private_parent(tmp_path: Path) -> None:
    source_root = make_source_root(tmp_path)
    publication_parent = tmp_path / "publication"
    publication_parent.mkdir(mode=0o700)
    output = publication_parent / "mirror"
    manifest = B.build_mirror(source_root, output)
    assert stat.S_IMODE(publication_parent.stat().st_mode) == 0o700
    assert manifest["entry_count"] == 40
    assert V.validate_mirror(output, source_root) == manifest
    assert tree_modes(output) == ({0o555}, {0o444})


def test_validator_is_standalone_from_original_writable_sources(tmp_path: Path) -> None:
    authority_root = make_authority_only_root(tmp_path)
    for entry in json.loads((ARTIFACT / "manifest.json").read_text("ascii"))["entries"]:
        assert not (authority_root / entry["source_report_relative_path"]).exists()
    manifest = V.validate_mirror(ARTIFACT, authority_root)
    assert manifest["entry_count"] == 40


def test_builder_refuses_existing_destination_without_replacement(tmp_path: Path) -> None:
    source_root = make_source_root(tmp_path)
    parent = tmp_path / "publication"
    parent.mkdir(mode=0o700)
    output = parent / "mirror"
    output.mkdir(mode=0o700)
    marker = output / "foreign"
    marker.write_text("foreign", encoding="ascii")
    with pytest.raises(B.MirrorBuildError, match="already exists"):
        B.build_mirror(source_root, output)
    assert marker.read_text("ascii") == "foreign"


def test_builder_rejects_a_coherently_changed_writable_source(tmp_path: Path) -> None:
    source_root = make_source_root(tmp_path)
    implementation = source_root / "code/rate_defined_tensor_f0.py"
    implementation.write_bytes(implementation.read_bytes() + b"\n")
    parent = tmp_path / "publication"
    parent.mkdir(mode=0o700)
    with pytest.raises(B.MirrorBuildError, match="accepted source SHA-256 mismatch"):
        B.build_mirror(source_root, parent / "mirror")


def test_builder_and_validator_are_source_separated() -> None:
    builder_source = BUILD_PATH.read_text("utf-8")
    validator_source = VALIDATE_PATH.read_text("utf-8")
    assert "validate_continuum_c1_n0_role10_sealed" not in builder_source
    assert "build_continuum_c1_n0_role10_sealed" not in validator_source
    assert "physical_production_killing_geometry_v1" not in builder_source
    assert "physical_production_killing_geometry_v1" not in validator_source


def test_cli_validation_is_read_only_and_reports_candidate_scope() -> None:
    before = {
        path.relative_to(ARTIFACT).as_posix(): (path.stat().st_mtime_ns, path.stat().st_size)
        for path in ARTIFACT.rglob("*")
        if path.is_file()
    }
    completed = subprocess.run(
        [
            sys.executable,
            str(VALIDATE_PATH),
            "--mirror-root",
            str(ARTIFACT),
            "--authority-root",
            str(REPORT),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "PASS_ROLE10_SEALED_AUTHENTICATION_MIRROR_CANDIDATE" in completed.stdout
    assert "external commitment" not in completed.stdout.lower()
    after = {
        path.relative_to(ARTIFACT).as_posix(): (path.stat().st_mtime_ns, path.stat().st_size)
        for path in ARTIFACT.rglob("*")
        if path.is_file()
    }
    assert after == before


@pytest.mark.skipif(not Path("/tmp").is_symlink(), reason="/tmp is not a symlink ancestor")
def test_builder_cli_accepts_private_tmp_and_rejects_tmp_symlink_ancestor() -> None:
    publication_parent = Path(tempfile.mkdtemp(prefix="role10-sealed-mirror-", dir="/private/tmp"))
    output = publication_parent / "private-path-mirror"
    alias_output = Path("/tmp") / publication_parent.name / "symlink-path-mirror"
    try:
        accepted = subprocess.run(
            [
                sys.executable,
                str(BUILD_PATH),
                "--source-root",
                str(REPORT),
                "--output",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert accepted.returncode == 0
        assert "PASS_ROLE10_SEALED_AUTHENTICATION_MIRROR_CANDIDATE" in accepted.stdout
        assert V.validate_mirror(output, REPORT)["entry_count"] == 40

        rejected = subprocess.run(
            [
                sys.executable,
                str(BUILD_PATH),
                "--source-root",
                str(REPORT),
                "--output",
                str(alias_output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert rejected.returncode == 2
        assert rejected.stdout == ""
        assert rejected.stderr.startswith(
            "HOLD_ROLE10_SEALED_AUTHENTICATION_MIRROR_BUILD: "
            "component-anchored directory open rejected: /tmp/"
        )
        assert "Traceback" not in rejected.stderr
        assert not alias_output.exists()
    finally:
        for directory, directories, _files in os.walk(publication_parent, topdown=True):
            os.chmod(directory, 0o700)
            for name in directories:
                candidate = Path(directory) / name
                if not candidate.is_symlink():
                    candidate.chmod(0o700)
        shutil.rmtree(publication_parent)
