"""Hostile mutations for the outcome-free role-3 factorization candidate."""

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
VALIDATOR = REPORT / "code/validate_continuum_c1_factorization_source_v2_candidate.py"
BUILDER = REPORT / "code/build_continuum_c1_factorization_source_v2_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"

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


def set_path(keys: tuple[Any, ...], replacement: Any) -> Mutation:
    def mutate(value: dict[str, Any]) -> None:
        cursor: Any = value
        for key in keys[:-1]:
            cursor = cursor[key]
        cursor[keys[-1]] = replacement

    return mutate


ATTACKS: list[tuple[str, Mutation]] = [
    (
        "legacy_receipt_pin",
        lambda value: value["source_pins"].update(
            {
                "two_repeat_geometry_receipt": {
                    "path": "artifacts/data/invented_receipt.json",
                    "schema": "invented",
                    "sha256": "0" * 64,
                }
            }
        ),
    ),
    (
        "geometry_digest",
        set_path(("source_pins", "killing_geometry_source", "sha256"), "0" * 64),
    ),
    (
        "dependency_back_edge",
        lambda value: value["dependency_closure"]["edges"].append(
            {
                "from": "factorization_source_v2_candidate",
                "to": "killing_geometry_source",
            }
        ),
    ),
    (
        "jacobian",
        set_path(
            ("coordinate_and_measure_contract", "longitudinal_absolute_jacobian_exact"),
            "2/1",
        ),
    ),
    (
        "normalization",
        set_path(
            ("coordinate_and_measure_contract", "quotient_density_normalization"),
            "1/1",
        ),
    ),
    (
        "factorization_formula",
        set_path(
            ("cell_average_formulae", "factorized_profile_cell_average"),
            "V_jmab=C_ab*Phi_jm",
        ),
    ),
    (
        "contact_denominator",
        set_path(
            ("cell_average_formulae", "contact_average"),
            "C_ab=integral_indicator_contact_dR_dY",
        ),
    ),
    (
        "profile_order",
        lambda value: value["profile_basis"]["ordered_profile_mapping"].__setitem__(
            slice(0, 2),
            list(reversed(value["profile_basis"]["ordered_profile_mapping"][:2])),
        ),
    ),
    (
        "profile_centre",
        set_path(
            ("profile_basis", "ordered_profile_mapping", 0, "centre_exact"),
            "7/20",
        ),
    ),
    (
        "numeric_payload",
        set_path(("outcome_free_contract", "numeric_enclosure_payload_present"), True),
    ),
    (
        "stronger_claim",
        set_path(("claim_boundary", "complete_C1"), True),
    ),
    (
        "binary64_exact_claim",
        set_path(
            (
                "enclosure_semantics",
                "stored_binary64_endpoints_are_not_exact_averages_or_centres",
            ),
            False,
        ),
    ),
    (
        "storage_order",
        set_path(("storage_contract", "tensor_storage_order"), "Fortran"),
    ),
    (
        "schema",
        set_path(("schema",), "encounter_continuum_c1_factorization_source_v2"),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    ATTACKS,
    ids=[name for name, _ in ATTACKS],
)
def test_rejects_semantic_mutations(
    tmp_path: Path,
    attack_name: str,
    mutate: Mutation,
) -> None:
    assert attack_name
    result = run_validator(write_mutation(tmp_path, mutate))
    assert result.returncode != 0, result.stdout
    assert "ERROR FactorizationSourceV2CandidateValidation:" in result.stderr
    assert "factorization candidate semantic drift" in result.stderr


def test_rejects_duplicate_json_key(tmp_path: Path) -> None:
    payload = ARTIFACT.read_bytes()
    attacked = payload.replace(
        b'{\n  "cell_average_formulae": {',
        b'{\n  "schema": "duplicate",\n  "cell_average_formulae": {',
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
    assert "ERROR FactorizationSourceV2CandidateValidation:" in result.stderr
    assert "Traceback" not in result.stderr


def test_rejects_symlink_and_hardlink(tmp_path: Path) -> None:
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(ARTIFACT)
    symlink_result = run_validator(symlink)
    assert symlink_result.returncode != 0
    assert "ERROR FactorizationSourceV2CandidateValidation:" in symlink_result.stderr

    clone = tmp_path / "clone.json"
    clone.write_bytes(ARTIFACT.read_bytes())
    clone.chmod(0o444)
    hardlink = tmp_path / "hardlink.json"
    os.link(clone, hardlink)
    hardlink_result = run_validator(hardlink)
    assert hardlink_result.returncode != 0
    assert "ERROR FactorizationSourceV2CandidateValidation:" in hardlink_result.stderr


def test_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    fifo = tmp_path / "candidate.fifo"
    os.mkfifo(fifo)
    result = run_validator(fifo)
    assert result.returncode != 0
    assert "ERROR FactorizationSourceV2CandidateValidation:" in result.stderr


@pytest.mark.parametrize("mode", [0o400, 0o555])
def test_builder_check_and_validator_reject_noncanonical_read_only_mode(
    tmp_path: Path,
    mode: int,
) -> None:
    candidate = tmp_path / f"candidate-{mode:o}.json"
    candidate.write_bytes(ARTIFACT.read_bytes())
    candidate.chmod(mode)
    build = run_builder_check(candidate)
    validation = run_validator(candidate)
    assert build.returncode != 0
    assert "ERROR FactorizationSourceV2CandidateBuild:" in build.stderr
    assert validation.returncode != 0
    assert "ERROR FactorizationSourceV2CandidateValidation:" in validation.stderr


@pytest.mark.parametrize(
    ("module_path", "function_name", "extra_arguments"),
    [
        (BUILDER, "read_regular", ("candidate",)),
        (VALIDATOR, "snapshot_file", ("candidate",)),
    ],
)
def test_component_anchored_read_rejects_parent_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_path: Path,
    function_name: str,
    extra_arguments: tuple[str, ...],
) -> None:
    module = load_module(module_path, f"factorization_parent_{function_name}")
    live = tmp_path / "live"
    live.mkdir()
    source_path = live / "source.json"
    source_path.write_bytes(b"ORIGINAL")
    displaced = tmp_path / "displaced"
    alternate = tmp_path / "alternate"
    alternate.mkdir()
    (alternate / "source.json").write_bytes(b"REDIRECTED")
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
    function = getattr(module, function_name)
    with pytest.raises((OSError, ValueError, RuntimeError)):
        function(source_path, *extra_arguments)


def test_failed_partial_publication_leaves_no_final_or_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "factorization_partial_publication")
    output = tmp_path / "candidate.json"
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
    module = load_module(BUILDER, f"factorization_post_open_{interrupt_type.__name__}")
    output = tmp_path / "candidate.json"
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
    module = load_module(BUILDER, "factorization_identical_foreign_stage")
    output = tmp_path / "candidate.json"
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
    module = load_module(BUILDER, f"factorization_post_link_{interrupt_type.__name__}")
    output = tmp_path / "candidate.json"
    original_link = module.os.link

    def link_then_interrupt(*args: Any, **kwargs: Any) -> None:
        original_link(*args, **kwargs)
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
    module = load_module(BUILDER, f"factorization_final_ack_{mutation_window}")
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
    with pytest.raises(module.FactorizationBuildError, match="acknowledgement"):
        module.publish_no_replace(output, payload)
    assert not output.exists()
    assert not list(tmp_path.glob(".*.stage"))


def test_post_link_interrupt_preserves_foreign_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(BUILDER, "factorization_post_link_foreign")
    output = tmp_path / "candidate.json"
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
    assert not list(tmp_path.glob(".*.stage"))


@pytest.mark.parametrize("foreign", [False, True])
def test_parent_descriptor_close_fault_participates_in_rollback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    foreign: bool,
) -> None:
    module = load_module(BUILDER, f"factorization_close_fault_{foreign}")
    output = tmp_path / "candidate.json"
    original_verify = module.verify_live_parent
    original_close = module.os.close
    release_ready = False
    interrupted = False
    foreign_payload = b"foreign-after-parent-close"

    def verify_then_arm(path: Path, descriptor: int) -> None:
        nonlocal release_ready
        original_verify(path, descriptor)
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
    module = load_module(BUILDER, "factorization_chmod_before_fsync")
    output = tmp_path / "candidate.json"
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


@pytest.mark.parametrize(
    ("module_path", "function_name", "arguments"),
    [
        (BUILDER, "read_regular", ("candidate",)),
        (VALIDATOR, "snapshot_file", ("candidate",)),
    ],
)
def test_rejects_non_0444_and_multiply_linked_candidate_files(
    tmp_path: Path,
    module_path: Path,
    function_name: str,
    arguments: tuple[str, ...],
) -> None:
    module = load_module(module_path, f"factorization_immutable_{function_name}")
    function = getattr(module, function_name)

    writable = tmp_path / "writable.json"
    writable.write_bytes(ARTIFACT.read_bytes())
    with pytest.raises((ValueError, RuntimeError)):
        function(writable, *arguments)

    owner_read_only = tmp_path / "owner-read-only.json"
    owner_read_only.write_bytes(ARTIFACT.read_bytes())
    owner_read_only.chmod(0o400)
    with pytest.raises((ValueError, RuntimeError)):
        function(owner_read_only, *arguments)

    executable_read_only = tmp_path / "executable-read-only.json"
    executable_read_only.write_bytes(ARTIFACT.read_bytes())
    executable_read_only.chmod(0o555)
    with pytest.raises((ValueError, RuntimeError)):
        function(executable_read_only, *arguments)

    immutable = tmp_path / "immutable.json"
    immutable.write_bytes(ARTIFACT.read_bytes())
    immutable.chmod(0o444)
    linked = tmp_path / "linked.json"
    os.link(immutable, linked)
    with pytest.raises((ValueError, RuntimeError)):
        function(immutable, *arguments)
