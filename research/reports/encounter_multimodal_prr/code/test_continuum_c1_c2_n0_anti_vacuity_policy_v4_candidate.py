"""Positive and currentness tests for the successor anti-vacuity policy v4."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
BUILDER_PATH = HERE / "build_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.py"
VALIDATOR_PATH = HERE / "validate_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def builder() -> ModuleType:
    return load_module(BUILDER_PATH, "anti_vacuity_policy_v4_builder_positive")


@pytest.fixture(scope="module")
def validator() -> ModuleType:
    return load_module(VALIDATOR_PATH, "anti_vacuity_policy_v4_validator_positive")


def artifact_value() -> dict[str, Any]:
    return json.loads(ARTIFACT.read_text(encoding="ascii"))


def immutable_metadata(path: Path) -> os.stat_result:
    metadata = path.stat(follow_symlinks=False)
    assert stat.S_ISREG(metadata.st_mode)
    assert stat.S_IMODE(metadata.st_mode) == 0o444
    assert metadata.st_uid == os.getuid()
    assert metadata.st_nlink == 1
    return metadata


def remove_read_only(path: Path) -> None:
    if path.exists() or path.is_symlink():
        path.chmod(0o600, follow_symlinks=False)
        path.unlink()


def test_live_input_hashes_and_immutable_metadata(builder: ModuleType) -> None:
    expected = {
        builder.POLICY_V3_RELATIVE: builder.POLICY_V3_SHA256,
        builder.MEMBER_V4_RELATIVE: builder.MEMBER_V4_SHA256,
        builder.REGISTRY_V4_RELATIVE: builder.REGISTRY_V4_SHA256,
    }
    for relative, digest in expected.items():
        path = REPORT / relative
        immutable_metadata(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_candidate_is_canonical_ascii_single_link(builder: ModuleType) -> None:
    metadata = immutable_metadata(ARTIFACT)
    payload = ARTIFACT.read_bytes()
    assert metadata.st_size == len(payload)
    value = builder.decode_canonical(payload)
    assert builder.canonical_bytes(value) == payload
    assert payload.decode("ascii").encode("ascii") == payload


def test_builder_reconstructs_exact_candidate(builder: ModuleType) -> None:
    expected = builder.canonical_bytes(builder.normative_policy(REPORT))
    assert ARTIFACT.read_bytes() == expected
    assert hashlib.sha256(expected).hexdigest() == builder.sha256(expected)


def test_independent_validator_reconstructs_exact_candidate(
    validator: ModuleType,
) -> None:
    payload, value = validator.validate_paths(REPORT, ARTIFACT)
    assert payload == ARTIFACT.read_bytes()
    assert value == validator.expected_document()
    assert len(value["claim_boundary"]) == 18


def test_cli_check_and_independent_validator_pass() -> None:
    check = subprocess.run(
        [sys.executable, "-I", "-B", os.fspath(BUILDER_PATH), "--check"],
        cwd=REPORT.parents[2],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert check.returncode == 0, check.stderr
    assert "PASS_ANTI_VACUITY_POLICY_V4_CANDIDATE_CHECK" in check.stdout
    verify = subprocess.run(
        [sys.executable, "-I", "-B", os.fspath(VALIDATOR_PATH)],
        cwd=REPORT.parents[2],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert verify.returncode == 0, verify.stderr
    assert "PASS_ANTI_VACUITY_POLICY_V4_CANDIDATE_VALIDATION" in verify.stdout


def test_two_fresh_builds_are_byte_identical(
    builder: ModuleType,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    payload = builder.canonical_bytes(builder.normative_policy(REPORT))
    try:
        builder.publish_no_replace(first, payload)
        builder.publish_no_replace(second, payload)
        assert first.read_bytes() == second.read_bytes() == ARTIFACT.read_bytes()
        immutable_metadata(first)
        immutable_metadata(second)
    finally:
        remove_read_only(first)
        remove_read_only(second)


def test_publication_refuses_replacement(
    builder: ModuleType,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "occupied.json"
    destination.write_bytes(b"foreign")
    before = destination.stat()
    with pytest.raises(builder.PolicyBuildError, match="refusing to replace"):
        builder.publish_no_replace(destination, ARTIFACT.read_bytes())
    after = destination.stat()
    assert destination.read_bytes() == b"foreign"
    assert (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
    assert not list(tmp_path.glob(".occupied.json.*.stage"))


def test_exact_v3_threshold_and_join_lineage(builder: ModuleType) -> None:
    value = artifact_value()
    assert value["requirements"] == builder.V3_REQUIREMENTS
    assert value["join_requirements"] == builder.V3_JOIN_REQUIREMENTS
    assert value["threshold_lineage"] == builder.V3_THRESHOLD_LINEAGE
    assert type(value["requirements"]["minimum_configuration_count"]) is int
    assert value["source_pins"]["policy_v3_lineage"]["sha256"] == (builder.POLICY_V3_SHA256)


def test_exact_successor_member_registry_and_count_bindings(
    builder: ModuleType,
) -> None:
    value = artifact_value()
    pins = value["source_pins"]
    assert pins["member_spec_v4_candidate"] == {
        "member_identity_sha256": builder.MEMBER_V4_IDENTITY_SHA256,
        "path": builder.MEMBER_V4_RELATIVE,
        "schema": builder.MEMBER_V4_SCHEMA,
        "sha256": builder.MEMBER_V4_SHA256,
    }
    assert pins["method_parameter_registry_v4_candidate"] == {
        "path": builder.REGISTRY_V4_RELATIVE,
        "schema": builder.REGISTRY_V4_SCHEMA,
        "sha256": builder.REGISTRY_V4_SHA256,
    }
    assert value["successor_binding_counts"] == builder.SUCCESSOR_BINDING_COUNTS
    assert value["successor_binding_counts"]["member_axis_partition_count"] == 36
    assert value["successor_binding_counts"]["future_fresh_replay_role_catalog_order"] == [8, 9, 10]
    assert (
        value["successor_binding_counts"][
            "future_fresh_replay_role_catalog_order_implies_dependency_edges"
        ]
        is False
    )
    assert "future_fresh_replay_role_order" not in value["successor_binding_counts"]
    assert "role_dependency_edges" not in value["successor_binding_counts"]


def test_all_promotion_claims_are_exact_false(builder: ModuleType) -> None:
    claims = artifact_value()["claim_boundary"]
    assert tuple(sorted(claims)) == tuple(sorted(builder.CLAIM_KEYS))
    assert len(claims) == 18
    assert all(type(value) is bool and value is False for value in claims.values())


def test_result_blind_ordering_is_exact_and_nonretroactive(
    builder: ModuleType,
) -> None:
    value = artifact_value()
    assert value["status"] == builder.STATUS
    assert value["ordering"] == builder.ORDERING
    assert value["ordering"]["current_enclosure_sources_eligible_for_acceptance"] is False
    assert value["ordering"]["prototype_enclosure_sources_eligible_for_acceptance"] is False
    assert value["ordering"]["external_predecessor_commitment_present"] is False
    assert value["ordering"]["future_fresh_roles_8_10_replay_required"] is True
    assert (
        value["ordering"]["future_replay_must_pin_exact_member_registry_policy_replay_plan_hashes"]
        is True
    )
    assert value["ordering"]["result_blind_replay_plan_required"] is True
    assert value["ordering"]["roles_8_9_10_may_execute_in_parallel_after_commitment"] is True
    assert value["ordering"]["policy_predecessor_order_independently_sealed"] is False
    assert value["ordering"]["roles_8_10_outputs_read_while_constructing_this_policy"] is False
    assert value["ordering"]["retroactive_acceptance_authorized"] is False
    assert value["ordering"]["timestamp_ordering_is_sufficient"] is False


def test_only_three_outcome_free_normative_paths_are_bound(
    builder: ModuleType,
) -> None:
    value = artifact_value()
    assert set(value["source_pins"]) == {
        "policy_v3_lineage",
        "member_spec_v4_candidate",
        "method_parameter_registry_v4_candidate",
    }
    assert {
        builder.POLICY_V3_RELATIVE,
        builder.MEMBER_V4_RELATIVE,
        builder.REGISTRY_V4_RELATIVE,
    } == {record["path"] for record in value["source_pins"].values()}
    forbidden_keys = {
        "role8_output",
        "role9_output",
        "role10_output",
        "result_sha256",
        "acceptance_receipt",
        "current_enclosure_sha256",
        "prototype_enclosure_sha256",
    }

    def keys(node: Any) -> set[str]:
        if type(node) is dict:
            return set(node) | set().union(*(keys(item) for item in node.values()))
        if type(node) is list:
            return set().union(*(keys(item) for item in node))
        return set()

    assert keys(value).isdisjoint(forbidden_keys)


def test_validator_is_standalone_not_builder_coupled() -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    assert "import build_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate" not in source
    assert "from build_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate" not in source
