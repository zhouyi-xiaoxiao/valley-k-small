#!/usr/bin/env python3
"""Hostile mutations for the C1/C2 n0 structural-member v4 candidate."""

from __future__ import annotations

import copy
import errno
import importlib.util
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_c2_n0_member_spec_v4_candidate.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_c2_n0_member_spec_v4_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"

Mutation = Callable[[dict[str, Any]], None]


def real(path: Path) -> Path:
    return Path(os.path.realpath(path))


def canonical_leaf(path: Path) -> Path:
    """Canonicalize parent components without resolving an attacked leaf."""
    return real(path.parent) / path.name


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


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(VALIDATOR),
            "--input",
            str(canonical_leaf(path)),
        ],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def run_builder_check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(BUILDER),
            "--check",
            "--output",
            str(canonical_leaf(path)),
        ],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def source_value() -> dict[str, Any]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def write_mutation(tmp_path: Path, mutate: Mutation) -> Path:
    value = copy.deepcopy(source_value())
    mutate(value)
    path = real(tmp_path) / "mutated.json"
    path.write_bytes(canonical(value))
    path.chmod(0o444)
    return path


def set_path(keys: tuple[Any, ...], replacement: Any) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        cursor: Any = value
        for key in keys[:-1]:
            cursor = cursor[key]
        cursor[keys[-1]] = replacement

    return mutate


ATTACKS: list[tuple[str, Mutation]] = [
    ("schema", set_path(("schema",), "encounter_continuum_c1_c2_n0_member_spec_v3_candidate")),
    (
        "status",
        set_path(
            ("status",),
            "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_EXTERNALLY_COMMITTED",
        ),
    ),
    ("claim", set_path(("claim_boundary", "complete_C1"), True)),
    ("claim_int", set_path(("claim_boundary", "complete_C1"), 0)),
    ("identity", set_path(("member_identity_sha256",), "0" * 64)),
    (
        "domainless_identity",
        lambda value: value.__setitem__(
            "member_identity_sha256",
            __import__("hashlib")
            .sha256(
                canonical(
                    {
                        "configuration_order": value["configuration_order"],
                        "configuration_semantic_ids": value["configuration_semantic_ids"],
                        "member_semantics": value["member_semantics"],
                        "n0_sequence_bindings": value["n0_sequence_bindings"],
                        "role_bindings_1_through_4": value["role_bindings"],
                    }
                )
            )
            .hexdigest(),
        ),
    ),
    (
        "configuration_order",
        lambda value: value["configuration_order"].__setitem__(
            slice(0, 2), list(reversed(value["configuration_order"][:2]))
        ),
    ),
    (
        "semantic_authority_label",
        set_path(("configuration_semantic_ids", 0, "authority_label"), "E128/Base"),
    ),
    (
        "semantic_family_empty",
        set_path(("configuration_semantic_ids", 0, "refinement_family_id"), ""),
    ),
    (
        "semantic_member_bool",
        set_path(("configuration_semantic_ids", 0, "refinement_member_id"), False),
    ),
    (
        "member_semantics_missing",
        lambda value: value["member_semantics"].pop("scalar_convention"),
    ),
    (
        "member_semantics_bool_dimension",
        set_path(("member_semantics", "physical_dimension"), True),
    ),
    (
        "member_semantics_endpoint_models",
        set_path(
            ("member_semantics", "every_cartesian_interval_endpoint_combination_is_a_model"),
            True,
        ),
    ),
    (
        "configuration_index_bool",
        set_path(("n0_sequence_bindings", 0, "configuration_index"), False),
    ),
    (
        "source_index_bool",
        set_path(("n0_sequence_bindings", 0, "sequence_source_row_index"), True),
    ),
    (
        "sequence_id",
        set_path(("n0_sequence_bindings", 0, "sequence_id"), ""),
    ),
    (
        "row_label",
        set_path(("n0_sequence_bindings", 0, "authority_label"), "O113/Base/alias"),
    ),
    (
        "row_shape",
        set_path(("n0_sequence_bindings", 0, "n0_anchor_shape", 0), 114),
    ),
    (
        "row_states",
        set_path(("n0_sequence_bindings", 0, "n0_anchor_expected_states"), 1_442_898),
    ),
    (
        "geometry_digest",
        set_path(("n0_sequence_bindings", 0, "configuration_geometry_sha256"), "0" * 64),
    ),
    (
        "physical_digest",
        set_path(("n0_sequence_bindings", 0, "physical_parameter_bundle_sha256"), "0" * 64),
    ),
    (
        "partition_path_escape",
        set_path(
            ("n0_sequence_bindings", 0, "n0_axes", 0, "partition_report_relative_path"),
            "../escape.json",
        ),
    ),
    (
        "partition_digest",
        set_path(("n0_sequence_bindings", 0, "n0_axes", 0, "partition_sha256"), "0" * 64),
    ),
    (
        "axis_order",
        lambda value: value["n0_sequence_bindings"][0]["n0_axes"].__setitem__(
            slice(0, 2),
            list(reversed(value["n0_sequence_bindings"][0]["n0_axes"][:2])),
        ),
    ),
    (
        "periodic_bool",
        set_path(("n0_sequence_bindings", 0, "n0_axes", 2, "periodic"), 1),
    ),
    (
        "factorization_v1_path",
        set_path(
            ("role_bindings", "factorization_source", "path"),
            "artifacts/data/continuum_c1_factorization_source_v1.json",
        ),
    ),
    (
        "factorization_v1_sha",
        set_path(
            ("role_bindings", "factorization_source", "sha256"),
            "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
        ),
    ),
    (
        "role5_registry",
        lambda value: value["role_bindings"].update(
            {
                "method_parameter_registry": {
                    "path": (
                        "artifacts/data/"
                        "continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
                    ),
                    "sha256": "0" * 64,
                }
            }
        ),
    ),
    (
        "top_registry",
        lambda value: value.update(
            {
                "method_parameter_registry": {
                    "path": "forbidden",
                    "sha256": "0" * 64,
                }
            }
        ),
    ),
    (
        "counts_bool",
        set_path(("reconstruction_counts", "configuration_count"), True),
    ),
    (
        "partition_file_count",
        set_path(("identity_properties", "partition_file_count"), 35),
    ),
    (
        "predecessor_sha",
        set_path(("source_lineage_evidence", "predecessor_member_v3", "sha256"), "0" * 64),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    ATTACKS,
    ids=[name for name, _ in ATTACKS],
)
def test_validator_rejects_candidate_semantic_mutations(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    result = run_validator(write_mutation(tmp_path, mutate))
    assert result.returncode != 0, result.stdout
    assert "ERROR MemberSpecV4CandidateValidation:" in result.stderr


def authority_values(module: Any) -> tuple[dict[str, Any], ...]:
    return module.validate_primary_sources()


def validate_in_memory_authorities(
    module: Any,
    monkeypatch: pytest.MonkeyPatch,
    values: list[dict[str, Any]],
) -> None:
    # validate_primary_sources reads bundle before refinement, while its return
    # tuple exposes refinement before bundle.
    iterator = iter(
        [
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[6],
            values[5],
        ]
    )

    def load_next(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return next(iterator)

    monkeypatch.setattr(module, "load_json", load_next)
    module.validate_primary_sources()


def test_coherent_v3_registry_injection_fails_semantically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_coherent_v3_registry")
    values = list(authority_values(module))
    values[0] = copy.deepcopy(values[0])
    values[0]["method_parameter_registry"] = {"path": "forbidden", "sha256": "0" * 64}
    with pytest.raises(module.MemberBuildError, match="registry injection"):
        validate_in_memory_authorities(module, monkeypatch, values)


@pytest.mark.parametrize(
    ("authority_index", "mutate", "message"),
    [
        (
            1,
            lambda value: value["source_pins"]["configuration_source"].__setitem__(
                "sha256", "0" * 64
            ),
            "reference nested configuration",
        ),
        (
            2,
            lambda value: value["member_semantics"].__setitem__(
                "global_gauge_is_single_scalar_per_configuration", False
            ),
            "ideal nested member-semantics",
        ),
        (
            3,
            lambda value: value.__setitem__(
                "schema", "encounter_continuum_c1_factorization_source_v1"
            ),
            "factorization v2 schema",
        ),
        (
            3,
            lambda value: value["source_pins"]["configuration_source"].__setitem__(
                "schema", "wrong"
            ),
            "factorization nested configuration",
        ),
        (
            3,
            lambda value: value["outcome_free_contract"].__setitem__(
                "numeric_enclosure_payload_present", True
            ),
            "factorization outcome-free",
        ),
        (
            4,
            lambda value: value["configuration_order"].__setitem__(
                slice(0, 2), list(reversed(value["configuration_order"][:2]))
            ),
            "configuration source order",
        ),
        (
            5,
            lambda value: value["sequence_order"].__setitem__(
                slice(0, 2), list(reversed(value["sequence_order"][:2]))
            ),
            "joint-refinement order",
        ),
        (
            6,
            lambda value: value["flags"].__setitem__("science_executed", True),
            "partition bundle claim",
        ),
    ],
)
def test_coherently_repinned_authority_semantic_drift_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    authority_index: int,
    mutate: Mutation,
    message: str,
) -> None:
    module = load_module(BUILDER, f"member_v4_coherent_authority_{authority_index}_{message}")
    values = list(authority_values(module))
    values[authority_index] = copy.deepcopy(values[authority_index])
    mutate(values[authority_index])
    with pytest.raises(module.MemberBuildError):
        validate_in_memory_authorities(module, monkeypatch, values)


@pytest.mark.parametrize(
    "scope_key",
    [
        "finite_twelve_family_geometric_uniformity_proved",
        "genuine_refinement_sequences_defined",
        "maximum_axis_spacing_limit_proved",
        "n0_configuration_geometry_anchor_exact",
        "shape_regularity_proved",
    ],
)
def test_validator_rejects_coherently_repinned_joint_refinement_scope_drift(
    monkeypatch: pytest.MonkeyPatch,
    scope_key: str,
) -> None:
    module = load_module(VALIDATOR, f"member_v4_validator_scope_{scope_key}")
    values = [
        module.load(module.V3_RELATIVE, "immutable member v3", normative=True),
        module.load(module.REFERENCE_RELATIVE, "reference authority", normative=True),
        module.load(module.IDEAL_RELATIVE, "ideal authority", normative=True),
        module.load(module.FACTOR_RELATIVE, "factorization v2 authority", normative=True),
        module.load(module.CONFIG_RELATIVE, "configuration authority", normative=True),
        module.load(module.REFINEMENT_RELATIVE, "joint-refinement evidence", normative=False),
        module.load(module.BUNDLE_RELATIVE, "partition bundle", normative=True),
    ]
    values[5] = copy.deepcopy(values[5])
    values[5]["established_scope"][scope_key] = False
    # Supplying already-authenticated parsed authorities models an attacker that
    # coherently repinned the changed refinement bytes at the outer SHA layer.
    iterator = iter([*values[:5], values[6], values[5]])
    monkeypatch.setattr(module, "load", lambda *_args, **_kwargs: next(iterator))
    with pytest.raises(
        module.MemberValidationError,
        match=f"refinement established-scope changed: {scope_key}",
    ):
        module.expected_candidate()


def test_rejects_duplicate_key_float_nonascii_and_deep_json(tmp_path: Path) -> None:
    payloads = {
        "duplicate": ARTIFACT.read_bytes().replace(
            b'{\n  "claim_boundary": {',
            b'{\n  "schema": "duplicate",\n  "claim_boundary": {',
            1,
        ),
        "float": b'{"x": 1.5}\n',
        "nonascii": '{"x":"é"}\n'.encode(),
        "deep": b'{"x":' + b"[" * 5000 + b"0" + b"]" * 5000 + b"}\n",
    }
    for name, payload in payloads.items():
        path = real(tmp_path) / f"{name}.json"
        path.write_bytes(payload)
        path.chmod(0o444)
        result = run_validator(path)
        assert result.returncode != 0
        assert "ERROR MemberSpecV4CandidateValidation:" in result.stderr
        assert "Traceback" not in result.stderr


def test_validator_rejects_symlink_hardlink_and_fifo_without_blocking(
    tmp_path: Path,
) -> None:
    directory = real(tmp_path)
    symlink = directory / "symlink.json"
    symlink.symlink_to(ARTIFACT)
    assert run_validator(symlink).returncode != 0

    clone = directory / "clone.json"
    clone.write_bytes(ARTIFACT.read_bytes())
    clone.chmod(0o444)
    hardlink = directory / "hardlink.json"
    os.link(clone, hardlink)
    assert run_validator(hardlink).returncode != 0

    fifo = directory / "candidate.fifo"
    os.mkfifo(fifo)
    assert run_validator(fifo).returncode != 0


@pytest.mark.parametrize("mode", [0o400, 0o555, 0o644])
def test_builder_check_and_validator_reject_non_0444_mode(
    tmp_path: Path,
    mode: int,
) -> None:
    candidate = real(tmp_path) / f"candidate-{mode:o}.json"
    candidate.write_bytes(ARTIFACT.read_bytes())
    candidate.chmod(mode)
    assert run_builder_check(candidate).returncode != 0
    assert run_validator(candidate).returncode != 0


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
    module = load_module(module_path, f"member_v4_parent_replacement_{function_name}")
    root = real(tmp_path)
    live = root / "live"
    live.mkdir()
    source = live / "source.json"
    source.write_bytes(b"{}\n")
    source.chmod(0o444)
    displaced = root / "displaced"
    alternate = root / "alternate"
    alternate.mkdir()
    redirected = alternate / "source.json"
    redirected.write_bytes(b"{}\n")
    redirected.chmod(0o444)
    original_read = module.os.read
    swapped = False

    def swap_then_read(descriptor: int, count: int) -> bytes:
        nonlocal swapped
        if not swapped:
            live.rename(displaced)
            live.symlink_to(alternate, target_is_directory=True)
            swapped = True
        return original_read(descriptor, count)

    monkeypatch.setattr(module.os, "read", swap_then_read)
    function = getattr(module, function_name)
    with pytest.raises((OSError, RuntimeError)):
        if function_name == "read_regular":
            function(source, "TOCTOU", normative=True)
        else:
            function(source, "TOCTOU", normative=True)


def test_partial_write_failure_cleans_owned_stage_and_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_partial_write")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_write = module.os.write
    calls = 0

    def short_then_fail(descriptor: int, payload: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original_write(descriptor, payload[:7])
        raise OSError(errno.ENOSPC, "injected no space")

    monkeypatch.setattr(module.os, "write", short_then_fail)
    with pytest.raises(OSError):
        module.publish_no_replace(output, b"x" * 100)
    assert not output.exists()
    assert not list(directory.glob(".*.stage"))


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_open_baseexception_uses_authenticated_transaction_without_leak(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    module = load_module(BUILDER, f"member_v4_post_open_{interrupt_type.__name__}")
    directory = real(tmp_path)
    output = directory / "candidate.json"
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
    assert not list(directory.glob(".*.stage"))


def test_post_open_preserves_identical_metadata_foreign_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_foreign_stage")
    directory = real(tmp_path)
    output = directory / "candidate.json"
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
        assert observed.st_nlink == 1
        assert observed.st_size == 0
        assert not observed.st_mode & 0o222
        os.close(foreign)
        raise KeyboardInterrupt

    monkeypatch.setattr(module.StageCreationTransaction, "await_ready", replace_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        module.publish_no_replace(output, b"owned-stage")
    stages = list(directory.glob(".*.stage"))
    assert len(stages) == 1
    observed = stages[0].stat()
    assert (observed.st_dev, observed.st_ino) == foreign_identity
    assert observed.st_nlink == 1
    assert observed.st_size == 0
    assert not observed.st_mode & 0o222
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not output.exists()


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_link_baseexception_rolls_back_owned_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    module = load_module(BUILDER, f"member_v4_post_link_{interrupt_type.__name__}")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_link = module.os.link

    def link_then_interrupt(*args: Any, **kwargs: Any) -> None:
        original_link(*args, **kwargs)
        raise interrupt_type("post-link interruption")

    monkeypatch.setattr(module.os, "link", link_then_interrupt)
    with pytest.raises(interrupt_type):
        module.publish_no_replace(output, b"owned-final")
    assert not output.exists()
    assert not list(directory.glob(".*.stage"))


@pytest.mark.parametrize("mutation_window", ["before_link", "after_link"])
def test_installed_bytes_are_reauthenticated_after_same_inode_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation_window: str,
) -> None:
    module = load_module(BUILDER, f"member_v4_final_ack_{mutation_window}")
    directory = real(tmp_path)
    output = directory / "candidate.json"
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
    with pytest.raises(module.MemberBuildError, match="acknowledgement"):
        module.publish_no_replace(output, payload)
    assert not output.exists()
    assert not list(directory.glob(".*.stage"))


def test_post_link_preserves_foreign_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_foreign_final")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_link = module.os.link
    foreign_payload = b"foreign-final"

    def replace_then_interrupt(
        source: str,
        destination: str,
        **kwargs: Any,
    ) -> None:
        original_link(source, destination, **kwargs)
        os.unlink(destination, dir_fd=kwargs["dst_dir_fd"])
        foreign = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o444,
            dir_fd=kwargs["dst_dir_fd"],
        )
        os.write(foreign, foreign_payload)
        os.close(foreign)
        raise SystemExit("post-link foreign replacement")

    monkeypatch.setattr(module.os, "link", replace_then_interrupt)
    with pytest.raises(SystemExit):
        module.publish_no_replace(output, b"owned-final")
    assert output.read_bytes() == foreign_payload
    assert not list(directory.glob(".*.stage"))


def test_foreign_stage_replacement_during_owned_unlink_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_foreign_stage_at_unlink")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_unlink_owned = module.unlink_owned
    replaced = False
    foreign_identity: tuple[int, int] | None = None

    def replace_stage(parent: int, leaf: str, identity: tuple[int, int]) -> bool:
        nonlocal replaced, foreign_identity
        if not replaced and leaf.endswith(".stage"):
            replaced = True
            os.unlink(leaf, dir_fd=parent)
            foreign = os.open(
                leaf,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o444,
                dir_fd=parent,
            )
            observed = os.fstat(foreign)
            foreign_identity = observed.st_dev, observed.st_ino
            os.close(foreign)
        return original_unlink_owned(parent, leaf, identity)

    monkeypatch.setattr(module, "unlink_owned", replace_stage)
    with pytest.raises(module.MemberBuildError, match="staging identity changed"):
        module.publish_no_replace(output, b"owned-final")
    assert not output.exists()
    stages = list(directory.glob(".*.stage"))
    assert len(stages) == 1
    observed = stages[0].stat()
    assert (observed.st_dev, observed.st_ino) == foreign_identity


def test_fchmod_precedes_file_fsync_and_stage_begins_0400(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_chmod_before_fsync")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_open = module._STAGE_OPEN
    original_fchmod = module.os.fchmod
    original_fsync = module.os.fsync
    events: list[str] = []

    def record_open(
        leaf: str,
        flags: int,
        mode: int,
        *,
        dir_fd: int,
    ) -> int:
        events.append(f"open:{mode:o}")
        return original_open(leaf, flags, mode, dir_fd=dir_fd)

    def record_chmod(descriptor: int, mode: int) -> None:
        events.append(f"chmod:{mode:o}")
        original_fchmod(descriptor, mode)

    def record_fsync(descriptor: int) -> None:
        events.append("fsync")
        original_fsync(descriptor)

    monkeypatch.setattr(module, "_STAGE_OPEN", record_open)
    monkeypatch.setattr(module.os, "fchmod", record_chmod)
    monkeypatch.setattr(module.os, "fsync", record_fsync)
    module.publish_no_replace(output, b"immutable-before-fsync")
    assert events[:3] == ["open:400", "chmod:444", "fsync"]
    assert output.stat().st_mode & 0o777 == 0o444


@pytest.mark.parametrize("window", ["after_fchmod", "directory_fsync"])
def test_fsync_baseexception_windows_clean_owned_objects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    window: str,
) -> None:
    module = load_module(BUILDER, f"member_v4_fsync_window_{window}")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_fsync = module.os.fsync
    calls = 0

    def interrupt_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        target = 1 if window == "after_fchmod" else 2
        if calls == target:
            raise KeyboardInterrupt(window)
        original_fsync(descriptor)

    monkeypatch.setattr(module.os, "fsync", interrupt_fsync)
    with pytest.raises(KeyboardInterrupt):
        module.publish_no_replace(output, b"owned")
    assert not output.exists()
    assert not list(directory.glob(".*.stage"))


def test_stage_descriptor_close_baseexception_cleans_owned_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_stage_close")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_close = module.os.close
    interrupted = False

    def close_then_interrupt(descriptor: int) -> None:
        nonlocal interrupted
        observed = os.fstat(descriptor)
        original_close(descriptor)
        if (
            not interrupted
            and stat_is_regular(observed.st_mode)
            and observed.st_size == len(b"owned")
            and observed.st_mode & 0o777 == 0o444
        ):
            interrupted = True
            raise KeyboardInterrupt("stage close")

    def stat_is_regular(mode: int) -> bool:
        import stat

        return stat.S_ISREG(mode)

    monkeypatch.setattr(module.os, "close", close_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        module.publish_no_replace(output, b"owned")
    assert interrupted
    assert not output.exists()
    assert not list(directory.glob(".*.stage"))


def test_parent_close_baseexception_is_contained_without_fd_or_thread_residue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "member_v4_parent_close")
    directory = real(tmp_path)
    output = directory / "candidate.json"
    original_close = module.os.close
    interrupted = False
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def close_then_raise_once(descriptor: int) -> None:
        nonlocal interrupted
        observed = os.fstat(descriptor)
        original_close(descriptor)
        if not interrupted and os.path.isdir(f"/dev/fd/{descriptor}") is False:
            # The descriptor has already been closed.  Raise only for a directory
            # descriptor in final cleanup; close_safely must contain it.
            import stat

            if stat.S_ISDIR(observed.st_mode):
                interrupted = True
                raise KeyboardInterrupt("parent close")

    monkeypatch.setattr(module.os, "close", close_then_raise_once)
    module.publish_no_replace(output, b"owned")
    assert interrupted
    assert output.read_bytes() == b"owned"
    assert not list(directory.glob(".*.stage"))
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
