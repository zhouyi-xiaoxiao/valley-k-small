"""Adversarial mutations for the successor anti-vacuity policy v4."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
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
    return load_module(BUILDER_PATH, "anti_vacuity_policy_v4_builder_mutations")


@pytest.fixture(scope="module")
def validator() -> ModuleType:
    return load_module(VALIDATOR_PATH, "anti_vacuity_policy_v4_validator_mutations")


def write_immutable(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    path.chmod(0o444)


def clone_normative_inputs(
    tmp_path: Path,
    builder: ModuleType,
) -> tuple[Path, Path]:
    temporary_report = tmp_path / "report"
    for relative in (
        builder.POLICY_V3_RELATIVE,
        builder.MEMBER_V4_RELATIVE,
        builder.REGISTRY_V4_RELATIVE,
    ):
        destination = temporary_report / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPORT / relative, destination)
        destination.chmod(0o444)
    candidate = tmp_path / "candidate.json"
    write_immutable(candidate, ARTIFACT.read_bytes())
    return temporary_report, candidate


def run_validator(
    report: Path,
    artifact: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            os.fspath(VALIDATOR_PATH),
            "--report-root",
            os.fspath(report),
            "--artifact",
            os.fspath(artifact),
        ],
        cwd=REPORT.parents[2],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def mutate_at(
    document: dict[str, Any],
    path: tuple[str, ...],
    replacement: Any,
) -> dict[str, Any]:
    mutated = copy.deepcopy(document)
    target: Any = mutated
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    return mutated


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("requirements", "maximum_gauge_relative_width"), "1/549755813888"),
        (("requirements", "maximum_gauge_relative_width"), "1/2199023255552"),
        (("requirements", "maximum_map_anchor_constant"), "1000001/1"),
        (("requirements", "maximum_map_anchor_constant"), "999999/1"),
        (
            ("requirements", "maximum_reconstructed_killing_anchor_constant"),
            "1000001/1",
        ),
        (
            ("requirements", "maximum_reference_cell_mass_relative_width"),
            "1/549755813888",
        ),
        (
            ("requirements", "maximum_stationary_axis_relative_width"),
            "1/2199023255552",
        ),
        (("requirements", "minimum_configuration_count"), 11),
        (("requirements", "minimum_configuration_count"), 13),
        (
            ("threshold_lineage", "all_exact_thresholds_equal_to_legacy_policy"),
            False,
        ),
        (("threshold_lineage", "post_enclosure_adaptation_allowed"), True),
        (("threshold_lineage", "threshold_loosening_detected"), True),
    ],
)
def test_threshold_loosening_and_tightening_rejected(
    validator: ModuleType,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    mutated = mutate_at(validator.expected_document(), path, replacement)
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutated)


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("join_requirements", "axis_order_exact"), ["relative_parallel"]),
        (
            ("join_requirements", "axis_partition_path_sha_cell_count_equal"),
            False,
        ),
        (("join_requirements", "configuration_count_exactly_12"), False),
        (
            (
                "join_requirements",
                "killing_member_partition_formula_method_unit_binding_equal",
            ),
            False,
        ),
        (("join_requirements", "profile_index_order_exact"), [0, 1, 2]),
        (
            (
                "join_requirements",
                "raw_stationary_member_partition_formula_method_unit_binding_equal",
            ),
            False,
        ),
    ],
)
def test_join_requirement_mutations_rejected(
    validator: ModuleType,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutate_at(validator.expected_document(), path, replacement))


def test_each_promotion_claim_is_rejected(validator: ModuleType) -> None:
    for key in sorted(validator.CLAIM_KEYS):
        mutated = validator.expected_document()
        mutated["claim_boundary"][key] = True
        with pytest.raises(validator.PolicyValidationError, match="promoted"):
            validator.audit_candidate(mutated)


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (
            ("ordering", "current_enclosure_sources_eligible_for_acceptance"),
            True,
        ),
        (
            ("ordering", "prototype_enclosure_sources_eligible_for_acceptance"),
            True,
        ),
        (("ordering", "external_predecessor_commitment_present"), True),
        (("ordering", "future_fresh_roles_8_10_replay_required"), False),
        (
            (
                "ordering",
                "future_replay_must_pin_exact_member_registry_policy_replay_plan_hashes",
            ),
            False,
        ),
        (("ordering", "result_blind_replay_plan_required"), False),
        (
            (
                "ordering",
                "roles_8_9_10_may_execute_in_parallel_after_commitment",
            ),
            False,
        ),
        (
            ("ordering", "policy_predecessor_order_independently_sealed"),
            True,
        ),
        (
            (
                "ordering",
                "roles_8_10_outputs_read_while_constructing_this_policy",
            ),
            True,
        ),
        (("ordering", "retroactive_acceptance_authorized"), True),
        (("ordering", "timestamp_ordering_is_sufficient"), True),
    ],
)
def test_ordering_boundary_mutations_rejected(
    validator: ModuleType,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutate_at(validator.expected_document(), path, replacement))


@pytest.mark.parametrize(
    "injected_key",
    [
        "role8_output",
        "role9_result_sha256",
        "role10_enclosure",
        "current_result",
        "prototype_result",
        "symbolic_acceptance_receipt",
    ],
)
def test_output_result_and_receipt_injection_rejected(
    validator: ModuleType,
    injected_key: str,
) -> None:
    mutated = validator.expected_document()
    mutated[injected_key] = "0" * 64
    with pytest.raises(validator.PolicyValidationError, match="injection"):
        validator.audit_candidate(mutated)


@pytest.mark.parametrize(
    ("injected_key", "injected_value"),
    [
        ("future_fresh_replay_role_order", [8, 9, 10]),
        ("role_dependency_edges", [[8, 9], [9, 10]]),
    ],
)
def test_catalog_order_cannot_be_promoted_to_dependency_edges(
    validator: ModuleType,
    injected_key: str,
    injected_value: Any,
) -> None:
    mutated = validator.expected_document()
    mutated["successor_binding_counts"][injected_key] = injected_value
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutated)


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (
            ("source_pins", "member_spec_v4_candidate", "sha256"),
            "0" * 64,
        ),
        (
            (
                "source_pins",
                "member_spec_v4_candidate",
                "member_identity_sha256",
            ),
            "1" * 64,
        ),
        (
            ("source_pins", "member_spec_v4_candidate", "schema"),
            "encounter_wrong_member",
        ),
        (
            (
                "source_pins",
                "method_parameter_registry_v4_candidate",
                "sha256",
            ),
            "2" * 64,
        ),
        (
            (
                "source_pins",
                "method_parameter_registry_v4_candidate",
                "schema",
            ),
            "encounter_wrong_registry",
        ),
        (("source_pins", "policy_v3_lineage", "sha256"), "3" * 64),
    ],
)
def test_wrong_member_registry_and_policy_pins_rejected(
    validator: ModuleType,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutate_at(validator.expected_document(), path, replacement))


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("requirements", "minimum_configuration_count"), True),
        (
            ("successor_binding_counts", "future_fresh_replay_role_count"),
            True,
        ),
        (
            ("successor_binding_counts", "member_axis_partition_count"),
            True,
        ),
        (
            ("successor_binding_counts", "member_configuration_count"),
            True,
        ),
        (
            ("successor_binding_counts", "registry_parameter_count"),
            True,
        ),
        (
            (
                "successor_binding_counts",
                "future_fresh_replay_role_catalog_order",
            ),
            [8, 9, True],
        ),
        (
            (
                "successor_binding_counts",
                "future_fresh_replay_role_catalog_order_implies_dependency_edges",
            ),
            True,
        ),
    ],
)
def test_boolean_integer_aliases_rejected(
    validator: ModuleType,
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    mutated = mutate_at(validator.expected_document(), path, replacement)
    with pytest.raises(validator.PolicyValidationError):
        validator.audit_candidate(mutated)


@pytest.mark.parametrize(
    "payload",
    [
        b'{"a":1,"a":2}\n',
        b'{"a":1.0}\n',
        b'{"a":NaN}\n',
        b'{"a":Infinity}\n',
        b'{"a":01}\n',
        b'{"a":1}\n\n',
        b'{"z":1,"a":2}\n',
        '{"a":"é"}\n'.encode(),
        ('{"a":' + "9" * 257 + "}\n").encode("ascii"),
        ("[" * 66 + "0" + "]" * 66 + "\n").encode("ascii"),
    ],
)
def test_malformed_noncanonical_and_overdeep_json_rejected(
    validator: ModuleType,
    payload: bytes,
) -> None:
    with pytest.raises(validator.PolicyValidationError):
        validator.decode_canonical(payload)


def test_oversized_json_rejected(validator: ModuleType) -> None:
    payload = b'{"a":"' + b"x" * validator.MAX_JSON_BYTES + b'"}\n'
    with pytest.raises(validator.PolicyValidationError, match="byte cap"):
        validator.decode_canonical(payload)


def test_coherent_v3_threshold_redigest_and_candidate_repin_rejected(
    tmp_path: Path,
    builder: ModuleType,
) -> None:
    temporary_report, candidate_path = clone_normative_inputs(tmp_path, builder)
    v3_path = temporary_report / builder.POLICY_V3_RELATIVE
    candidate = json.loads(candidate_path.read_text(encoding="ascii"))
    v3 = json.loads(v3_path.read_text(encoding="ascii"))
    v3["requirements"]["maximum_gauge_relative_width"] = "1/549755813888"
    v3_payload = builder.canonical_bytes(v3)
    v3_path.chmod(0o600)
    write_immutable(v3_path, v3_payload)
    candidate["requirements"] = copy.deepcopy(v3["requirements"])
    candidate["source_pins"]["policy_v3_lineage"]["sha256"] = hashlib.sha256(v3_payload).hexdigest()
    candidate_path.chmod(0o600)
    write_immutable(candidate_path, builder.canonical_bytes(candidate))
    observed = run_validator(temporary_report, candidate_path)
    assert observed.returncode != 0
    assert "SHA-256 mismatch" in observed.stderr


def test_coherent_registry_semantic_redigest_and_candidate_repin_rejected(
    tmp_path: Path,
    builder: ModuleType,
) -> None:
    temporary_report, candidate_path = clone_normative_inputs(tmp_path, builder)
    registry_path = temporary_report / builder.REGISTRY_V4_RELATIVE
    candidate = json.loads(candidate_path.read_text(encoding="ascii"))
    registry = json.loads(registry_path.read_text(encoding="ascii"))
    record = registry["parameters"][0]
    record["parameters"]["precision_bits"] = 321
    record["method_parameter_sha256"] = hashlib.sha256(
        builder.REGISTRY_DIGEST_DOMAIN + b"\0" + builder.canonical_bytes(record["parameters"])
    ).hexdigest()
    registry_payload = builder.canonical_bytes(registry)
    registry_path.chmod(0o600)
    write_immutable(registry_path, registry_payload)
    candidate["source_pins"]["method_parameter_registry_v4_candidate"]["sha256"] = hashlib.sha256(
        registry_payload
    ).hexdigest()
    candidate_path.chmod(0o600)
    write_immutable(candidate_path, builder.canonical_bytes(candidate))
    observed = run_validator(temporary_report, candidate_path)
    assert observed.returncode != 0
    assert "SHA-256 mismatch" in observed.stderr


def test_builder_opens_only_three_outcome_free_inputs(
    builder: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[Path] = []
    original = builder.read_immutable

    def recording_read(
        path: Path,
        expected_sha256: str | None = None,
        cap: int = builder.MAX_JSON_BYTES,
    ) -> bytes:
        observed.append(path)
        return original(path, expected_sha256, cap)

    monkeypatch.setattr(builder, "read_immutable", recording_read)
    builder.normative_policy(REPORT)
    assert len(observed) == 6
    assert set(observed) == {
        REPORT / builder.POLICY_V3_RELATIVE,
        REPORT / builder.MEMBER_V4_RELATIVE,
        REPORT / builder.REGISTRY_V4_RELATIVE,
    }


def test_read_rejects_wrong_permissions(
    builder: ModuleType,
    tmp_path: Path,
) -> None:
    path = tmp_path / "writable.json"
    path.write_bytes(b"{}\n")
    path.chmod(0o644)
    with pytest.raises(builder.PolicyBuildError, match="0444"):
        builder.read_immutable(path)


def test_read_rejects_symlink(
    builder: ModuleType,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.json"
    write_immutable(target, b"{}\n")
    link = tmp_path / "link.json"
    link.symlink_to(target.name)
    with pytest.raises((OSError, builder.PolicyBuildError)):
        builder.read_immutable(link)


def test_read_rejects_hard_link(
    validator: ModuleType,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.json"
    write_immutable(source, b"{}\n")
    link = tmp_path / "second.json"
    os.link(source, link)
    assert source.stat().st_nlink == 2
    with pytest.raises(validator.PolicyValidationError, match="single-link"):
        validator.read_immutable(source)


def test_read_rejects_fifo_without_blocking(
    validator: ModuleType,
    tmp_path: Path,
) -> None:
    fifo = tmp_path / "input.fifo"
    os.mkfifo(fifo, 0o444)
    with pytest.raises(validator.PolicyValidationError, match="regular"):
        validator.read_immutable(fifo)


def test_read_rejects_owner_mismatch(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "owned.json"
    write_immutable(path, b"{}\n")
    actual_uid = os.getuid()
    monkeypatch.setattr(builder.os, "getuid", lambda: actual_uid + 1)
    with pytest.raises(builder.PolicyBuildError, match="current-user-owned"):
        builder.read_immutable(path)


def test_source_path_swap_during_read_is_rejected(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "swap.json"
    payload = b'{"a":1}\n'
    write_immutable(path, payload)
    original_read = builder.os.read
    swapped = False

    def swapping_read(descriptor: int, count: int) -> bytes:
        nonlocal swapped
        block = original_read(descriptor, count)
        if not swapped:
            swapped = True
            path.unlink()
            write_immutable(path, payload)
        return block

    monkeypatch.setattr(builder.os, "read", swapping_read)
    with pytest.raises(builder.PolicyBuildError, match="changed"):
        builder.read_immutable(path, hashlib.sha256(payload).hexdigest())


def test_publication_interruption_cleans_owned_stage(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "interrupted.json"
    original = builder.StageCreationTransaction.await_ready

    def interrupt_after_ready(transaction: Any) -> None:
        original(transaction)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        builder.StageCreationTransaction,
        "await_ready",
        interrupt_after_ready,
    )
    with pytest.raises(KeyboardInterrupt):
        builder.publish_no_replace(destination, ARTIFACT.read_bytes())
    assert not destination.exists()
    assert not list(tmp_path.glob(".interrupted.json.*.stage"))


def test_publication_write_fault_cleans_owned_stage(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "write-fault.json"

    def fail_write(descriptor: int, payload: bytes) -> int:
        raise OSError("injected write failure")

    monkeypatch.setattr(builder.os, "write", fail_write)
    with pytest.raises(OSError, match="injected"):
        builder.publish_no_replace(destination, ARTIFACT.read_bytes())
    assert not destination.exists()
    assert not list(tmp_path.glob(".write-fault.json.*.stage"))


def test_publication_preserves_foreign_destination_inode(
    builder: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "foreign.json"

    def hostile_link(
        source: str,
        target: str,
        *,
        src_dir_fd: int,
        dst_dir_fd: int,
        follow_symlinks: bool,
    ) -> None:
        assert follow_symlinks is False
        descriptor = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=dst_dir_fd,
        )
        try:
            os.write(descriptor, b"foreign")
        finally:
            os.close(descriptor)
        raise OSError("injected hostile link failure")

    monkeypatch.setattr(builder.os, "link", hostile_link)
    with pytest.raises(OSError, match="hostile"):
        builder.publish_no_replace(destination, ARTIFACT.read_bytes())
    assert destination.read_bytes() == b"foreign"
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
    assert not list(tmp_path.glob(".foreign.json.*.stage"))


def test_output_parent_symlink_is_rejected(
    builder: ModuleType,
    tmp_path: Path,
) -> None:
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)
    with pytest.raises(OSError):
        builder.publish_no_replace(linked / "candidate.json", ARTIFACT.read_bytes())
