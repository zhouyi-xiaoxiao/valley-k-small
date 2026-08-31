"""Hostile package mutations for the Round-177 predecessor candidate."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
VALIDATOR = REPORT / "code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py"
SOURCE_PACKAGE = REPORT / "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1"

MEMBER = "continuum_c1_c2_n0_member_spec_v3_candidate.json"
PARAMETERS = "continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json"
METHODS = "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json"
POLICY = "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json"
MANIFEST = "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json"
REVIEW_REQUEST = "continuum_c1_c2_n0_external_commitment_review_request_v1.json"
BUNDLE = "bundle.json"
GENERATED_NAMES = [MEMBER, PARAMETERS, METHODS, POLICY, MANIFEST, REVIEW_REQUEST]
FORBIDDEN_BASENAMES = [
    "encounter_c1_gauge_killing_symbolic_candidate_v1.json",
    "encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
]

Mutation = Callable[[dict[str, Any]], None]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def copy_package(tmp_path: Path) -> Path:
    package = tmp_path / "candidate"
    shutil.copytree(SOURCE_PACKAGE, package)
    for path in package.iterdir():
        path.chmod(0o444)
    return package


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run_validator(package: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(VALIDATOR), "--package", str(package.resolve())],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


def write_immutable(path: Path, payload: bytes) -> None:
    if path.exists():
        path.chmod(0o600)
    try:
        path.write_bytes(payload)
    finally:
        path.chmod(0o444)


def assert_rejected(package: Path, expected_error: str) -> None:
    result = run_validator(package)
    assert result.returncode != 0, result.stdout
    assert "ERROR PredecessorAuthorityCandidateValidation:" in result.stderr
    assert "immutable single-link regular package file required" not in result.stderr
    assert expected_error in result.stderr


def set_nested(path: tuple[Any, ...], replacement: Any) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        cursor: Any = value
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement

    return mutate


def update_pin(entries: list[dict[str, Any]], role: str, value: dict[str, Any]) -> None:
    entry = next(item for item in entries if item["role"] == role)
    entry["sha256"] = digest(value)


def refresh_generated_references(values: dict[str, dict[str, Any]]) -> None:
    """Refresh all outer package hashes without repairing attacked semantics."""

    parameter_sha = digest(values[PARAMETERS])
    method_registry = values[METHODS]
    method_registry["parameter_registry"]["sha256"] = parameter_sha

    policy = values[POLICY]
    policy["source_pins"]["member_spec_v3_candidate"]["sha256"] = digest(values[MEMBER])
    policy["source_pins"]["outward_method_registry_v2_candidate"]["sha256"] = digest(
        method_registry
    )

    manifest = values[MANIFEST]
    update_pin(manifest["role_catalog"], "role5_member_spec_candidate", values[MEMBER])
    update_pin(
        manifest["role_catalog"],
        "role6_outward_method_registry_candidate",
        method_registry,
    )
    update_pin(manifest["role_catalog"], "role7_anti_vacuity_policy_candidate", policy)
    update_pin(
        manifest["supporting_evidence"],
        "method_parameter_registry_candidate",
        values[PARAMETERS],
    )

    request = values[REVIEW_REQUEST]
    commitments = request["commitment_set"]
    update_pin(commitments, "member_spec_candidate", values[MEMBER])
    update_pin(commitments, "method_parameter_registry_candidate", values[PARAMETERS])
    update_pin(commitments, "outward_method_registry_candidate", method_registry)
    update_pin(commitments, "anti_vacuity_policy_candidate", policy)
    update_pin(commitments, "predecessor_authority_candidate_manifest", manifest)
    request["requested_external_record"]["must_bind_commitment_message_sha256"] = domain_digest(
        "encounter-external-predecessor-commitment-request-v1", commitments
    )

    bundle = values[BUNDLE]
    by_path = {item["path"]: item for item in bundle["file_inventory"]}
    for name in GENERATED_NAMES:
        payload = canonical(values[name])
        by_path[name]["byte_length"] = len(payload)
        by_path[name]["sha256"] = hashlib.sha256(payload).hexdigest()


def mutate_package(
    tmp_path: Path,
    name: str,
    mutate: Mutation,
    *,
    coherent: bool = True,
) -> Path:
    package = copy_package(tmp_path)
    values = {filename: load(package / filename) for filename in GENERATED_NAMES + [BUNDLE]}
    mutate(values[name])
    if coherent:
        refresh_generated_references(values)
    for filename, value in values.items():
        write_immutable(package / filename, canonical(value))
    return package


def test_unmutated_immutable_clone_reaches_and_passes_semantic_validation(
    tmp_path: Path,
) -> None:
    package = copy_package(tmp_path)
    result = run_validator(package)
    assert result.returncode == 0, result.stderr
    assert "PASS_PREDECESSOR_AUTHORITY_CANDIDATE_VALIDATION" in result.stdout


MEMBER_ATTACKS: list[tuple[str, Mutation]] = [
    (
        "partition_hash",
        set_nested(("n0_sequence_bindings", 0, "n0_axes", 0, "partition_sha256"), "0" * 64),
    ),
    (
        "partition_path",
        set_nested(
            ("n0_sequence_bindings", 0, "n0_axes", 0, "partition_report_relative_path"),
            "artifacts/data/invented_partition.json",
        ),
    ),
    (
        "partition_cell_count",
        set_nested(("n0_sequence_bindings", 0, "n0_axes", 0, "cell_count"), 999),
    ),
    (
        "sequence_id",
        set_nested(("n0_sequence_bindings", 0, "sequence_id"), "invented_sequence"),
    ),
    (
        "sequence_source_hash",
        set_nested(
            ("n0_sequence_bindings", 0, "sequence_source_row_canonical_sha256"),
            "0" * 64,
        ),
    ),
    (
        "row_reorder",
        lambda value: value["n0_sequence_bindings"].__setitem__(
            slice(0, 2), list(reversed(value["n0_sequence_bindings"][:2]))
        ),
    ),
    (
        "axis_reorder",
        lambda value: value["n0_sequence_bindings"][0]["n0_axes"].__setitem__(
            slice(0, 2),
            list(reversed(value["n0_sequence_bindings"][0]["n0_axes"][:2])),
        ),
    ),
    (
        "duplicate_sequence_id",
        lambda value: value["n0_sequence_bindings"][1].__setitem__(
            "sequence_id", value["n0_sequence_bindings"][0]["sequence_id"]
        ),
    ),
    (
        "duplicate_semantic_identity",
        lambda value: value["n0_sequence_bindings"][1].update(
            {
                "refinement_family_id": value["n0_sequence_bindings"][0]["refinement_family_id"],
                "refinement_member_id": value["n0_sequence_bindings"][0]["refinement_member_id"],
            }
        ),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    MEMBER_ATTACKS,
    ids=[name for name, _ in MEMBER_ATTACKS],
)
def test_rejects_coherently_reinventoried_member_attacks(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    assert_rejected(
        mutate_package(tmp_path, MEMBER, mutate),
        f"semantic drift: package payload {MEMBER}",
    )


METHOD_ATTACKS: list[tuple[str, Mutation]] = [
    (
        "producer_code_hash",
        set_nested(("methods", 0, "producer_code_sha256"), "0" * 64),
    ),
    (
        "verifier_code_hash",
        set_nested(("methods", 0, "verifier_code_sha256"), "0" * 64),
    ),
    (
        "parameter_hash",
        set_nested(("methods", 0, "method_parameter_sha256"), "0" * 64),
    ),
    (
        "parameter_source_hash",
        set_nested(("methods", 0, "method_parameter_source_sha256"), "0" * 64),
    ),
    (
        "method_scope",
        set_nested(("methods", 0, "source_role_scope"), ["role10_killing_geometry"]),
    ),
    (
        "omit_killing_method",
        lambda value: (
            value["methods"].pop(),
            value.__setitem__("method_count", value["method_count"] - 1),
        ),
    ),
    (
        "invent_missing_exact_fraction_method",
        lambda value: (
            value["methods"].append(
                {
                    **copy.deepcopy(value["methods"][0]),
                    "method_id": "exact_fraction_expression_dag_v2",
                }
            ),
            value.__setitem__("method_count", value["method_count"] + 1),
            value["method_identity_properties"].__setitem__(
                "missing_candidate_native_method_ids", []
            ),
        ),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    METHOD_ATTACKS,
    ids=[name for name, _ in METHOD_ATTACKS],
)
def test_rejects_coherently_reinventoried_method_attacks(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    assert_rejected(
        mutate_package(tmp_path, METHODS, mutate),
        f"semantic drift: package payload {METHODS}",
    )


POLICY_ATTACKS: list[tuple[str, Mutation]] = [
    (
        "threshold_loosened",
        set_nested(("requirements", "maximum_map_anchor_constant"), "2000000/1"),
    ),
    (
        "current_results_eligible",
        set_nested(("ordering", "current_enclosure_sources_eligible_for_acceptance"), True),
    ),
    (
        "policy_retroactively_sealed",
        set_nested(("ordering", "policy_predecessor_order_independently_sealed"), True),
    ),
    (
        "future_replay_removed",
        set_nested(("ordering", "future_replay_required"), False),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    POLICY_ATTACKS,
    ids=[name for name, _ in POLICY_ATTACKS],
)
def test_rejects_coherently_reinventoried_policy_attacks(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    assert_rejected(
        mutate_package(tmp_path, POLICY, mutate),
        f"semantic drift: package payload {POLICY}",
    )


def remove_subordinate_coherently(manifest: dict[str, Any]) -> None:
    removed = manifest["subordinate_inventory"].pop()
    role = removed["role"]
    dag = manifest["predecessor_prefix_dag"]
    dag["nodes"] = [node for node in dag["nodes"] if node != role]
    dag["edges"] = [edge for edge in dag["edges"] if role not in edge]


MANIFEST_ATTACKS: list[tuple[str, Mutation]] = [
    (
        "dag_self_edge",
        lambda value: value["predecessor_prefix_dag"]["edges"].append(
            ["role5_member_spec_candidate", "role5_member_spec_candidate"]
        ),
    ),
    (
        "dag_back_edge",
        lambda value: value["predecessor_prefix_dag"]["edges"].append(
            ["role5_member_spec_candidate", "initial_partition_bundle"]
        ),
    ),
    (
        "role8_result_insertion",
        lambda value: (
            value["role_catalog"].append(
                {
                    "path": "artifacts/data/fake_role8_results.json",
                    "role": "role8_raw_axis_enclosure",
                    "sha256": "0" * 64,
                }
            ),
            value["predecessor_prefix_dag"]["nodes"].append("role8_raw_axis_enclosure"),
        ),
    ),
    ("coherent_subordinate_omission", remove_subordinate_coherently),
    (
        "subordinate_hash",
        set_nested(("subordinate_inventory", 0, "sha256"), "0" * 64),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    MANIFEST_ATTACKS,
    ids=[name for name, _ in MANIFEST_ATTACKS],
)
def test_rejects_coherently_reinventoried_manifest_attacks(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    assert_rejected(
        mutate_package(tmp_path, MANIFEST, mutate),
        f"semantic drift: package payload {MANIFEST}",
    )


@pytest.mark.parametrize("name", GENERATED_NAMES + [BUNDLE])
def test_rejects_claim_promotion_in_every_package_file(tmp_path: Path, name: str) -> None:
    package = mutate_package(
        tmp_path,
        name,
        lambda value: value["claim_boundary"].__setitem__("release_eligible", True),
    )
    assert_rejected(package, f"semantic drift: package payload {name}")


@pytest.mark.parametrize("blocker_index", range(9))
def test_rejects_clearing_every_blocker(tmp_path: Path, blocker_index: int) -> None:
    package = mutate_package(
        tmp_path,
        BUNDLE,
        lambda value: value["blocking_conditions"][blocker_index].__setitem__("cleared", True),
    )
    assert_rejected(package, f"semantic drift: package payload {BUNDLE}")


REVIEW_REQUEST_ATTACKS: list[tuple[str, Mutation]] = [
    (
        "fake_external_authentication",
        set_nested(("local_state", "external_authentication_present"), True),
    ),
    (
        "fake_candidate_ready",
        set_nested(("local_state", "candidate_ready_for_external_predecessor_commitment"), True),
    ),
    (
        "same_process_declared_external",
        set_nested(("local_state", "local_or_subagent_review_is_external_authentication"), True),
    ),
    (
        "review_request_authorizes_replay",
        set_nested(
            ("requested_external_record", "current_request_may_authorize_roles_8_10_replay"),
            True,
        ),
    ),
    (
        "fake_authentication_record",
        lambda value: value.__setitem__(
            "authentication", {"class": "same_process_or_child_process_assertion"}
        ),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    REVIEW_REQUEST_ATTACKS,
    ids=[name for name, _ in REVIEW_REQUEST_ATTACKS],
)
def test_rejects_fake_external_authority(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    assert_rejected(
        mutate_package(tmp_path, REVIEW_REQUEST, mutate),
        f"semantic drift: package payload {REVIEW_REQUEST}",
    )


def raw_bundle_attacks(original: bytes) -> list[tuple[str, bytes]]:
    duplicate = original.replace(
        b"{\n",
        (
            b'{\n  "schema": '
            b'"encounter_continuum_c1_c2_n0_predecessor_authority_candidate_bundle_v1",\n'
        ),
        1,
    )
    integer_boolean = original.replace(b'"complete_C1": false', b'"complete_C1": 0', 1)
    floating_count = original.replace(
        b'"configuration_count": 12', b'"configuration_count": 12.0', 1
    )
    assert duplicate != original
    assert integer_boolean != original
    assert floating_count != original
    return [
        ("duplicate_key", duplicate),
        ("boolean_replaced_by_integer", integer_boolean),
        ("integer_replaced_by_float", floating_count),
    ]


@pytest.mark.parametrize(
    "attack_name", ["duplicate_key", "boolean_replaced_by_integer", "integer_replaced_by_float"]
)
def test_rejects_noncanonical_duplicate_and_numeric_type_attacks(
    tmp_path: Path,
    attack_name: str,
) -> None:
    package = copy_package(tmp_path)
    attacks = dict(raw_bundle_attacks((package / BUNDLE).read_bytes()))
    write_immutable(package / BUNDLE, attacks[attack_name])
    expected_errors = {
        "duplicate_key": "duplicate or invalid JSON key",
        "boolean_replaced_by_integer": f"semantic drift: package payload {BUNDLE}",
        "integer_replaced_by_float": "non-integer JSON number forbidden",
    }
    assert_rejected(package, expected_errors[attack_name])


@pytest.mark.parametrize("basename", FORBIDDEN_BASENAMES)
def test_rejects_reserved_basename_even_if_added_to_inventory(
    tmp_path: Path,
    basename: str,
) -> None:
    package = copy_package(tmp_path)
    payload = canonical({"schema": "invented_external_authority"})
    write_immutable(package / basename, payload)
    bundle = load(package / BUNDLE)
    bundle["file_inventory"].append(
        {
            "byte_length": len(payload),
            "path": basename,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    )
    write_immutable(package / BUNDLE, canonical(bundle))
    assert_rejected(package, "reserved formal candidate/receipt basename present")
