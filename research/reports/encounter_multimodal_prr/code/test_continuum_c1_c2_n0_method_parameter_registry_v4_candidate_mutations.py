"""Hostile mutations for the standalone result-blind method registry v4."""

from __future__ import annotations

import copy
import errno
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
VALIDATOR = REPORT / "code/validate_continuum_c1_c2_n0_method_parameter_registry_v4_candidate.py"
BUILDER = REPORT / "code/build_continuum_c1_c2_n0_method_parameter_registry_v4_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
DOMAIN = "encounter-outward-method-parameters-v4"
Mutation = Callable[[dict[str, Any]], None]


def load_module(path: Path, name: str) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        specification.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def digest(parameters: dict[str, Any]) -> str:
    return hashlib.sha256(DOMAIN.encode("ascii") + b"\0" + canonical(parameters)).hexdigest()


def policy_digest(domain: str, preimage: dict[str, Any]) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical(preimage)).hexdigest()


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(VALIDATOR), "--artifact", str(path)],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def run_builder_check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(BUILDER), "--check", "--output", str(path)],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def source_value() -> dict[str, Any]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def write_mutation(tmp_path: Path, mutate: Mutation) -> Path:
    value = copy.deepcopy(source_value())
    mutate(value)
    path = tmp_path / "mutated.json"
    path.write_bytes(canonical(value))
    path.chmod(0o444)
    return path


def coherently_change_record(index: int) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        record = value["parameters"][index]
        record["parameters"]["uncommitted_extra_parameter"] = index
        record["method_parameter_sha256"] = digest(record["parameters"])

    return mutate


def coherently_set(index: int, key: str, replacement: Any) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        record = value["parameters"][index]
        record["parameters"][key] = replacement
        record["method_parameter_sha256"] = digest(record["parameters"])

    return mutate


def coherently_set_path(
    index: int,
    path: tuple[str, ...],
    replacement: Any,
) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        record = value["parameters"][index]
        cursor = record["parameters"]
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement
        record["method_parameter_sha256"] = digest(record["parameters"])

    return mutate


@pytest.mark.parametrize("index", range(10))
def test_rejects_coherently_redigested_change_to_every_record(
    tmp_path: Path,
    index: int,
) -> None:
    result = run_validator(write_mutation(tmp_path, coherently_change_record(index)))
    assert result.returncode != 0, result.stdout
    assert "method parameter record semantic drift" in result.stderr


ATTACKS: list[tuple[str, Mutation]] = [
    (
        "producer_contact_primitive",
        coherently_set(6, "contact_algorithm", "midpoint_sampling"),
    ),
    (
        "producer_rounding",
        coherently_set(6, "rounding_mode", "nearest"),
    ),
    (
        "producer_remainder",
        coherently_set(6, "support_simpson_remainder", "0/1"),
    ),
    (
        "analytic_containment",
        coherently_set(7, "containment_chain", ["oracle_384_overlaps_saved_256"]),
    ),
    (
        "verifier_source_independence",
        coherently_set(8, "source_independence", "reuse_192_bit_producer_records"),
    ),
    (
        "verifier_contact_cell_sampling",
        coherently_set(
            8,
            "contact_cell_verification",
            "first_partial_contact_cell_per_row_at_512_bits",
        ),
    ),
    (
        "verifier_contact_containment_sampling",
        coherently_set(
            8,
            "contact_containment_relations",
            [
                "published_192_contains_primary_384_for_every_partial_contact_cell",
                "primary_384_contains_sentinel_512_for_every_partial_contact_cell",
                "published_192_contains_sentinel_512_for_every_partial_contact_cell",
            ],
        ),
    ),
    (
        "verifier_backend_claim",
        coherently_set(8, "independent_backend", True),
    ),
    (
        "verifier_tree_resource_cap",
        coherently_set(8, "maximum_tree_files", 257),
    ),
    (
        "verifier_stack_resource_cap",
        coherently_set(8, "maximum_simpson_dfs_stack", 64),
    ),
    (
        "verifier_deadline",
        coherently_set(8, "semantic_deadline_seconds", 0),
    ),
    (
        "verifier_paired_simpson_policy",
        coherently_set(8, "paired_simpson_policy_sha256", "0" * 64),
    ),
    (
        "verifier_sentinel_leaf_rule",
        coherently_set(8, "sentinel_evaluation_rule", "evaluate_every_tree_node"),
    ),
    (
        "classification_zero_rule",
        coherently_set(9, "zero_rule", "corner_sampling_only"),
    ),
    (
        "classification_tangency",
        coherently_set(9, "tangency_convention", "boundary_tangency_has_positive_mass"),
    ),
    (
        "record_order",
        lambda value: value["parameters"].__setitem__(
            slice(0, 2),
            list(reversed(value["parameters"][:2])),
        ),
    ),
    (
        "record_count",
        lambda value: value.__setitem__("parameter_count", 9),
    ),
    (
        "claim",
        lambda value: value["claim_boundary"].__setitem__("complete_C1", True),
    ),
    (
        "status",
        lambda value: value.__setitem__("status", "EXTERNALLY_COMMITTED"),
    ),
    (
        "outcome_key",
        coherently_set(0, "accepted_leaf_output_hash", "0" * 64),
    ),
    (
        "integer_type_confusion",
        lambda value: value.__setitem__("parameter_count", True),
    ),
]

FINAL_AUDIT_FIELD_PATHS: list[tuple[str, tuple[str, ...]]] = [
    ("contact_aggregate_identity", ("contact_aggregate_identity",)),
    ("contact_containment_relations", ("contact_containment_relations",)),
    ("support_aggregate_identity", ("support_aggregate_identity",)),
    ("support_containment_relations", ("support_containment_relations",)),
    ("maximum_tree_files", ("maximum_tree_files",)),
    ("maximum_tree_directories", ("maximum_tree_directories",)),
    ("maximum_tree_relative_depth", ("maximum_tree_relative_depth",)),
    ("maximum_tree_total_bytes", ("maximum_tree_total_bytes",)),
    ("maximum_json_file_bytes", ("maximum_json_file_bytes",)),
    ("maximum_raw_contact_file_bytes", ("maximum_raw_contact_file_bytes",)),
    ("maximum_raw_support_file_bytes", ("maximum_raw_support_file_bytes",)),
    ("maximum_simpson_panels", ("maximum_simpson_panels",)),
    ("maximum_simpson_dfs_stack", ("maximum_simpson_dfs_stack",)),
    ("maximum_simpson_dyadic_depth", ("maximum_simpson_dyadic_depth",)),
    (
        "maximum_dyadic_coordinate_component_bits",
        ("maximum_dyadic_coordinate_component_bits",),
    ),
    (
        "maximum_mpfr_to_mpq_denominator_bits",
        ("maximum_mpfr_to_mpq_denominator_bits",),
    ),
    (
        "maximum_simpson_exact_component_bits",
        ("maximum_simpson_exact_component_bits",),
    ),
    ("maximum_bump_breakpoints", ("maximum_bump_breakpoints",)),
    ("flat_tail_threshold", ("flat_tail_threshold",)),
    ("semantic_deadline_seconds", ("semantic_deadline_seconds",)),
    ("child_process_deadline_seconds", ("child_process_deadline_seconds",)),
    ("outer_nonchild_reserve_seconds", ("outer_nonchild_reserve_seconds",)),
    ("outer_deadline_seconds", ("outer_deadline_seconds",)),
    (
        "maximum_child_semantic_receipt_bytes",
        ("maximum_child_semantic_receipt_bytes",),
    ),
    ("maximum_child_observation_bytes", ("maximum_child_observation_bytes",)),
    ("maximum_child_ack_bytes", ("maximum_child_ack_bytes",)),
    ("maximum_child_stderr_bytes", ("maximum_child_stderr_bytes",)),
    ("maximum_outer_receipt_bytes", ("maximum_outer_receipt_bytes",)),
    (
        "paired_simpson_policy_digest_domain",
        ("paired_simpson_policy_digest_domain",),
    ),
    ("paired_simpson_policy_preimage", ("paired_simpson_policy_preimage",)),
    ("paired_simpson_policy_sha256", ("paired_simpson_policy_sha256",)),
    ("flat_tail_policy_digest_domain", ("flat_tail_policy_digest_domain",)),
    ("flat_tail_policy_preimage", ("flat_tail_policy_preimage",)),
    ("flat_tail_policy_sha256", ("flat_tail_policy_sha256",)),
    (
        "paired_accepted_panel_rule",
        ("paired_simpson_policy_preimage", "accepted_panel_rule"),
    ),
    (
        "paired_accumulation",
        ("paired_simpson_policy_preimage", "accumulation"),
    ),
    (
        "paired_coordinate_component_bit_cap",
        ("paired_simpson_policy_preimage", "coordinate_component_bit_cap"),
    ),
    (
        "paired_dyadic_depth_cap",
        ("paired_simpson_policy_preimage", "dyadic_depth_cap"),
    ),
    (
        "paired_exact_component_bit_cap",
        ("paired_simpson_policy_preimage", "exact_component_bit_cap"),
    ),
    (
        "paired_execution_model",
        ("paired_simpson_policy_preimage", "execution_model"),
    ),
    (
        "paired_flat_tail_threshold",
        ("paired_simpson_policy_preimage", "flat_tail_threshold"),
    ),
    (
        "paired_maximum_stack_nodes",
        ("paired_simpson_policy_preimage", "maximum_stack_nodes"),
    ),
    (
        "paired_denominator_cap",
        ("paired_simpson_policy_preimage", "mpfr_to_mpq_denominator_bit_cap"),
    ),
    ("paired_panel_cap", ("paired_simpson_policy_preimage", "panel_cap")),
    (
        "paired_primary_target",
        ("paired_simpson_policy_preimage", "primary_target_width_exact"),
    ),
    (
        "paired_remainder_prefilter",
        ("paired_simpson_policy_preimage", "remainder_prefilter"),
    ),
    (
        "paired_root_derivative_rule",
        ("paired_simpson_policy_preimage", "root_derivative_rule"),
    ),
    (
        "paired_sample_rule",
        ("paired_simpson_policy_preimage", "sample_rule"),
    ),
    ("paired_schema", ("paired_simpson_policy_preimage", "schema")),
    (
        "paired_sentinel_rule",
        ("paired_simpson_policy_preimage", "sentinel_rule"),
    ),
    ("paired_traversal", ("paired_simpson_policy_preimage", "traversal")),
    (
        "flat_bump_upper",
        ("flat_tail_policy_preimage", "bump_upper_exact"),
    ),
    (
        "flat_derivative_coefficients",
        ("flat_tail_policy_preimage", "derivative_coefficients"),
    ),
    (
        "flat_derivative_upper",
        ("flat_tail_policy_preimage", "derivative_upper_exact"),
    ),
    (
        "flat_elementary_bound",
        ("flat_tail_policy_preimage", "elementary_bound"),
    ),
    ("flat_schema", ("flat_tail_policy_preimage", "schema")),
    ("flat_threshold", ("flat_tail_policy_preimage", "threshold_exact")),
]


@pytest.mark.parametrize(
    ("field_name", "path"),
    FINAL_AUDIT_FIELD_PATHS,
    ids=[name for name, _ in FINAL_AUDIT_FIELD_PATHS],
)
def test_rejects_coherently_redigested_final_audit_field_mutation(
    tmp_path: Path,
    field_name: str,
    path: tuple[str, ...],
) -> None:
    assert field_name
    mutation = coherently_set_path(8, path, None)
    result = run_validator(write_mutation(tmp_path, mutation))
    assert result.returncode != 0, result.stdout
    assert "method parameter record semantic drift at index 8" in result.stderr


def test_rejects_coherently_rehashed_policy_preimage_attack(tmp_path: Path) -> None:
    def mutate(value: dict[str, Any]) -> None:
        record = value["parameters"][8]
        parameters = record["parameters"]
        preimage = parameters["paired_simpson_policy_preimage"]
        preimage["panel_cap"] = 4194303
        parameters["paired_simpson_policy_sha256"] = policy_digest(
            parameters["paired_simpson_policy_digest_domain"],
            preimage,
        )
        record["method_parameter_sha256"] = digest(parameters)

    result = run_validator(write_mutation(tmp_path, mutate))
    assert result.returncode != 0, result.stdout
    assert "method parameter record semantic drift at index 8" in result.stderr


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    ATTACKS,
    ids=[name for name, _ in ATTACKS],
)
def test_rejects_semantic_resource_and_type_mutations(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    result = run_validator(write_mutation(tmp_path, mutate))
    assert result.returncode != 0, result.stdout
    assert "ERROR MethodParameterRegistryV4CandidateValidation:" in result.stderr


def test_rejects_float_json_type(tmp_path: Path) -> None:
    value = source_value()
    value["parameters"][8]["parameters"]["semantic_deadline_seconds"] = 1140.0
    path = tmp_path / "float.json"
    path.write_bytes(canonical(value))
    path.chmod(0o444)
    result = run_validator(path)
    assert result.returncode != 0
    assert "strict JSON decoding failed" in result.stderr


def test_rejects_duplicate_json_key(tmp_path: Path) -> None:
    attacked = ARTIFACT.read_bytes().replace(
        b'{\n  "claim_boundary": {',
        b'{\n  "schema": "duplicate",\n  "claim_boundary": {',
        1,
    )
    path = tmp_path / "duplicate.json"
    path.write_bytes(attacked)
    path.chmod(0o444)
    result = run_validator(path)
    assert result.returncode != 0
    assert "strict JSON decoding failed" in result.stderr


def test_deep_json_fails_without_traceback(tmp_path: Path) -> None:
    path = tmp_path / "deep.json"
    path.write_bytes(b'{"x":' + b"[" * 5000 + b"0" + b"]" * 5000 + b"}\n")
    path.chmod(0o444)
    result = run_validator(path)
    assert result.returncode != 0
    assert "ERROR MethodParameterRegistryV4CandidateValidation:" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_symlink_hardlink_and_fifo_without_blocking(tmp_path: Path) -> None:
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(ARTIFACT)
    assert run_validator(symlink).returncode != 0

    clone = tmp_path / "clone.json"
    clone.write_bytes(ARTIFACT.read_bytes())
    clone.chmod(0o444)
    hardlink = tmp_path / "hardlink.json"
    os.link(clone, hardlink)
    assert run_validator(hardlink).returncode != 0

    fifo = tmp_path / "registry.fifo"
    os.mkfifo(fifo)
    assert run_validator(fifo).returncode != 0


@pytest.mark.parametrize("mode", [0o400, 0o555])
def test_builder_check_and_validator_reject_noncanonical_read_only_mode(
    tmp_path: Path,
    mode: int,
) -> None:
    candidate = tmp_path / f"registry-{mode:o}.json"
    candidate.write_bytes(ARTIFACT.read_bytes())
    candidate.chmod(mode)
    build = run_builder_check(candidate)
    validation = run_validator(candidate)
    assert build.returncode != 0
    assert "ERROR MethodParameterRegistryV4CandidateBuild:" in build.stderr
    assert validation.returncode != 0
    assert "ERROR MethodParameterRegistryV4CandidateValidation:" in validation.stderr


@pytest.mark.parametrize(
    ("module_path", "function_name"),
    [
        (BUILDER, "read_regular"),
        (VALIDATOR, "snapshot"),
    ],
)
def test_component_anchored_read_rejects_parent_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_path: Path,
    function_name: str,
) -> None:
    module = load_module(module_path, f"registry_v4_parent_{function_name}")
    live = tmp_path / "live"
    live.mkdir()
    source_path = live / "registry.json"
    source_path.write_bytes(b"ORIGINAL")
    source_path.chmod(0o444)
    displaced = tmp_path / "displaced"
    alternate = tmp_path / "alternate"
    alternate.mkdir()
    redirected = alternate / "registry.json"
    redirected.write_bytes(b"REDIRECTED")
    redirected.chmod(0o444)
    real_read = module.os.read
    swapped = False

    def swap_then_read(descriptor: int, count: int) -> bytes:
        nonlocal swapped
        if not swapped:
            live.rename(displaced)
            live.symlink_to(alternate, target_is_directory=True)
            swapped = True
        return real_read(descriptor, count)

    monkeypatch.setattr(module.os, "read", swap_then_read)
    with pytest.raises((OSError, ValueError, RuntimeError)):
        getattr(module, function_name)(source_path)


@pytest.mark.parametrize(
    ("module_path", "function_name"),
    [
        (BUILDER, "read_regular"),
        (VALIDATOR, "snapshot"),
    ],
)
def test_rejects_non_0444_empty_oversize_and_multiply_linked_files(
    tmp_path: Path,
    module_path: Path,
    function_name: str,
) -> None:
    module = load_module(module_path, f"registry_v4_boundary_{function_name}")
    function = getattr(module, function_name)

    writable = tmp_path / "writable.json"
    writable.write_bytes(ARTIFACT.read_bytes())
    with pytest.raises((ValueError, RuntimeError)):
        function(writable)

    owner_read_only = tmp_path / "owner-read-only.json"
    owner_read_only.write_bytes(ARTIFACT.read_bytes())
    owner_read_only.chmod(0o400)
    with pytest.raises((ValueError, RuntimeError)):
        function(owner_read_only)

    executable_read_only = tmp_path / "executable-read-only.json"
    executable_read_only.write_bytes(ARTIFACT.read_bytes())
    executable_read_only.chmod(0o555)
    with pytest.raises((ValueError, RuntimeError)):
        function(executable_read_only)

    empty = tmp_path / "empty.json"
    empty.touch(mode=0o444)
    with pytest.raises((ValueError, RuntimeError)):
        function(empty)

    oversize = tmp_path / "oversize.json"
    oversize.write_bytes(b"x" * 1_000_001)
    oversize.chmod(0o444)
    with pytest.raises((ValueError, RuntimeError)):
        function(oversize)

    single = tmp_path / "single.json"
    single.write_bytes(ARTIFACT.read_bytes())
    single.chmod(0o444)
    linked = tmp_path / "linked.json"
    os.link(single, linked)
    with pytest.raises((ValueError, RuntimeError)):
        function(single)


def test_failed_partial_publication_leaves_no_final_or_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_v4_partial_publication")
    output = tmp_path / "registry.json"
    real_write = module.os.write
    calls = 0

    def short_then_fail(descriptor: int, payload: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_write(descriptor, payload[:7])
        raise OSError(errno.ENOSPC, "injected no space")

    monkeypatch.setattr(module.os, "write", short_then_fail)
    with pytest.raises(OSError):
        module.publish_no_replace(output, b"x" * 100)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_open_interrupt_uses_authoritative_stage_transaction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    module = load_module(BUILDER, f"registry_v4_post_open_{interrupt_type.__name__}")
    output = tmp_path / "registry.json"
    original_await = module.StageCreationTransaction.await_ready
    transactions: list[Any] = []
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def await_then_interrupt(transaction: Any) -> None:
        original_await(transaction)
        transactions.append(transaction)
        raise interrupt_type("post-open interruption")

    monkeypatch.setattr(module.StageCreationTransaction, "await_ready", await_then_interrupt)
    with pytest.raises(interrupt_type):
        module.publish_no_replace(output, b"owned-stage")
    assert len(transactions) == 1
    assert transactions[0].descriptor is None
    assert not transactions[0]._thread.is_alive()
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_post_open_interrupt_preserves_identical_metadata_foreign_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_v4_identical_foreign_stage")
    output = tmp_path / "registry.json"
    original_await = module.StageCreationTransaction.await_ready
    foreign_identity: tuple[int, int] | None = None
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def replace_then_interrupt(transaction: Any) -> None:
        nonlocal foreign_identity
        original_await(transaction)
        assert transaction.identity is not None
        os.unlink(transaction.leaf, dir_fd=transaction.parent_descriptor)
        foreign = os.open(
            transaction.leaf,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o400,
            dir_fd=transaction.parent_descriptor,
        )
        observed = os.fstat(foreign)
        foreign_identity = observed.st_dev, observed.st_ino
        assert foreign_identity != transaction.identity
        assert observed.st_uid == os.geteuid()
        assert observed.st_nlink == 1
        assert observed.st_size == 0
        assert not observed.st_mode & 0o222
        os.close(foreign)
        raise KeyboardInterrupt

    monkeypatch.setattr(module.StageCreationTransaction, "await_ready", replace_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        module.publish_no_replace(output, b"owned-stage")
    stages = list(tmp_path.glob(".*.stage"))
    assert len(stages) == 1
    observed = stages[0].stat()
    assert (observed.st_dev, observed.st_ino) == foreign_identity
    assert observed.st_uid == os.geteuid()
    assert observed.st_nlink == 1
    assert observed.st_size == 0
    assert not observed.st_mode & 0o222
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not output.exists()


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_link_interrupt_rolls_back_owned_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    module = load_module(BUILDER, f"registry_v4_post_link_{interrupt_type.__name__}")
    output = tmp_path / "registry.json"
    original_link = module.os.link

    def link_then_interrupt(*arguments: Any, **keywords: Any) -> None:
        original_link(*arguments, **keywords)
        raise interrupt_type("post-link interruption")

    monkeypatch.setattr(module.os, "link", link_then_interrupt)
    with pytest.raises(interrupt_type):
        module.publish_no_replace(output, b"owned-final")
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("mutation_window", ["before_link", "after_link"])
def test_installed_bytes_are_reauthenticated_after_same_inode_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation_window: str,
) -> None:
    module = load_module(BUILDER, f"registry_v4_final_ack_{mutation_window}")
    output = tmp_path / "candidate.json"
    payload = b"owned-payload"
    corrupted = b"X" + payload[1:]
    original_link = module.os.link

    def mutate_named_inode(leaf: str, parent: int) -> None:
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

    def mutate_around_link(source: str, destination: str, **kwargs: Any) -> None:
        if mutation_window == "before_link":
            mutate_named_inode(source, kwargs["src_dir_fd"])
        original_link(source, destination, **kwargs)
        if mutation_window == "after_link":
            mutate_named_inode(destination, kwargs["dst_dir_fd"])

    monkeypatch.setattr(module.os, "link", mutate_around_link)
    with pytest.raises(module.RegistryBuildError, match="acknowledgement"):
        module.publish_no_replace(output, payload)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_post_link_interrupt_preserves_foreign_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_v4_post_link_foreign")
    output = tmp_path / "registry.json"
    original_link = module.os.link
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

    monkeypatch.setattr(module.os, "link", replace_then_interrupt)
    with pytest.raises(SystemExit):
        module.publish_no_replace(output, b"owned-final")
    assert output.read_bytes() == foreign_payload
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("foreign", [False, True])
def test_parent_descriptor_close_fault_participates_in_rollback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    foreign: bool,
) -> None:
    module = load_module(BUILDER, f"registry_v4_close_fault_{foreign}")
    output = tmp_path / "registry.json"
    original_verify = module.verify_live_parent
    original_close = module.os.close
    release_ready = False
    interrupted = False
    foreign_payload = b"foreign-after-parent-close"

    def verify_then_arm(
        path: Path,
        descriptor: int,
        identity: tuple[int, int],
    ) -> None:
        nonlocal release_ready
        original_verify(path, descriptor, identity)
        release_ready = True

    def close_then_interrupt(descriptor: int) -> None:
        nonlocal interrupted
        original_close(descriptor)
        if release_ready and not interrupted:
            interrupted = True
            if foreign:
                output.unlink()
                output.write_bytes(foreign_payload)
            raise KeyboardInterrupt

    monkeypatch.setattr(module, "verify_live_parent", verify_then_arm)
    monkeypatch.setattr(module.os, "close", close_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        module.publish_no_replace(output, b"owned-before-close")
    assert interrupted
    if foreign:
        assert output.read_bytes() == foreign_payload
    else:
        assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_fchmod_precedes_file_fsync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_v4_chmod_before_fsync")
    output = tmp_path / "registry.json"
    original_fchmod = module.os.fchmod
    original_fsync = module.os.fsync
    events: list[str] = []

    def record_chmod(descriptor: int, mode: int) -> None:
        events.append(f"chmod:{mode:o}")
        original_fchmod(descriptor, mode)

    def record_fsync(descriptor: int) -> None:
        events.append("fsync")
        original_fsync(descriptor)

    monkeypatch.setattr(module.os, "fchmod", record_chmod)
    monkeypatch.setattr(module.os, "fsync", record_fsync)
    module.publish_no_replace(output, b"immutable-before-fsync")
    assert events[:2] == ["chmod:444", "fsync"]
    assert output.stat().st_mode & 0o777 == 0o444


def test_concurrent_same_output_has_exactly_one_publisher_and_no_residue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "registry_v4_concurrent_publish")
    output = tmp_path / "registry.json"
    payload = b"same-registry-payload"
    original_link = module.os.link
    link_barrier = threading.Barrier(2)
    results: list[BaseException | None] = []
    results_lock = threading.Lock()

    def synchronized_link(*arguments: Any, **keywords: Any) -> None:
        link_barrier.wait(timeout=5)
        original_link(*arguments, **keywords)

    def publish() -> None:
        error: BaseException | None = None
        try:
            module.publish_no_replace(output, payload)
        except BaseException as caught:
            error = caught
        with results_lock:
            results.append(error)

    monkeypatch.setattr(module.os, "link", synchronized_link)
    workers = [threading.Thread(target=publish) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
    assert not any(worker.is_alive() for worker in workers)
    assert len(results) == 2
    assert sum(error is None for error in results) == 1
    failures = [error for error in results if error is not None]
    assert len(failures) == 1
    assert isinstance(failures[0], module.RegistryBuildError)
    assert output.read_bytes() == payload
    assert output.stat().st_mode & 0o777 == 0o444
    assert output.stat().st_nlink == 1
    assert not list(tmp_path.glob(".*.stage"))
