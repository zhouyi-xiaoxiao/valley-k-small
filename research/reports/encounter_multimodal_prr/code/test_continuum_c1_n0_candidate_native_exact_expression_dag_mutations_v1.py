from __future__ import annotations

import copy
import errno
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

import pytest
from test_continuum_c1_n0_candidate_native_exact_expression_dag_v1 import (
    BUILDER,
    BUILDER_MODULE,
    TEMPLATE_DOMAIN,
    VALIDATOR,
    VALIDATOR_MODULE,
    canonical,
    nondegenerate_request,
    run,
    singleton_request,
    write_request,
)


def input_record(value: dict[str, Any], input_id: str) -> dict[str, Any]:
    return next(record for record in value["inputs"] if record["input_id"] == input_id)


def template_sha(template: dict[str, Any]) -> str:
    return hashlib.sha256(TEMPLATE_DOMAIN + canonical(template)).hexdigest()


def assert_build_rejected(
    tmp_path: Path,
    value: dict[str, Any],
    expected: str,
) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    request = tmp_path / "request.json"
    output = tmp_path / "artifact.json"
    write_request(request, value)
    result = run(str(BUILDER), "--request", str(request), "--output", str(output))
    assert result.returncode != 0, result.stdout
    assert expected in result.stderr
    assert not output.exists()


def make_zero_positive(value: dict[str, Any]) -> None:
    input_record(value, "M_L")["lower_exact"] = "0/1"


def make_negative_nonnegative(value: dict[str, Any]) -> None:
    input_record(value, "C_contact")["lower_exact"] = "-1/10"


def make_empty_four_way_intersection(value: dict[str, Any]) -> None:
    direct = input_record(value, "direct_right_kappa_interval")
    direct["lower_exact"] = "7/10"
    direct["upper_exact"] = "4/5"


def make_direct_provenance_alias(value: dict[str, Any]) -> None:
    left = input_record(value, "direct_left_kappa_interval")
    right = input_record(value, "direct_right_kappa_interval")
    right["provenance_lane"] = left["provenance_lane"]


def make_claim_bool_int_alias(value: dict[str, Any]) -> None:
    value["claim_boundary"]["science_executed"] = 0


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (make_zero_positive, "positive interval"),
        (make_negative_nonnegative, "nonnegative interval"),
        (make_empty_four_way_intersection, "empty interval intersection"),
        (make_direct_provenance_alias, "semantic binding drift"),
        (make_claim_bool_int_alias, "exact false claim map"),
    ],
)
def test_interval_and_binding_attacks_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
    expected: str,
) -> None:
    value = copy.deepcopy(nondegenerate_request())
    mutator(value)
    assert_build_rejected(tmp_path, value, expected)


def template_attack(
    mutator: Callable[[dict[str, Any]], None],
) -> Callable[[dict[str, Any]], None]:
    def apply(value: dict[str, Any]) -> None:
        mutator(value["semantic_template"])
        value["semantic_template_sha256"] = template_sha(value["semantic_template"])

    return apply


def replace_with_trivial_dag(template: dict[str, Any]) -> None:
    template["outward_nodes"] = [
        {
            "argument_ids": ["M_L", "S_M"],
            "node_id": "trivial_product",
            "operation": "interval_multiply_nonnegative",
        }
    ]
    template["outward_assertions"] = [
        {
            "assertion_id": "trivial_interval_reflexive",
            "left_id": "trivial_product",
            "relation": "interval_equal",
            "right_id": "trivial_product",
        }
    ]
    template["outward_outputs"] = [
        {"output_name": "trivial_product", "value_id": "trivial_product"}
    ]
    template["formal_nodes"] = [
        {
            "argument_ids": ["M_L"],
            "node_id": "trivial_formula",
            "operation": "formal_identity",
        }
    ]
    template["formal_assertions"] = [
        {
            "assertion_id": "trivial_formula_reflexive",
            "left_id": "trivial_formula",
            "relation": "formal_equal",
            "right_id": "trivial_formula",
        }
    ]
    template["formal_outputs"] = [{"output_name": "trivial_formula", "value_id": "trivial_formula"}]


def omit_direct_right_path(template: dict[str, Any]) -> None:
    common = next(
        node for node in template["outward_nodes"] if node["node_id"] == "common_kappa_interval"
    )
    common["argument_ids"].remove("direct_right_kappa_interval")


def replace_structural_q_with_unrelated_atom(template: dict[str, Any]) -> None:
    node = next(node for node in template["formal_nodes"] if node["node_id"] == "q_forward_formula")
    node["argument_ids"][0] = "C_contact"


def change_conductance_spectator(template: dict[str, Any]) -> None:
    node = next(
        node for node in template["formal_nodes"] if node["node_id"] == "conductance_formula"
    )
    node["argument_ids"][2] = "mu_M"


def collapse_to_two_profiles(template: dict[str, Any]) -> None:
    node = next(
        node
        for node in template["formal_nodes"]
        if node["node_id"] == "weighted_profile_sum_formula"
    )
    node["argument_ids"] = node["argument_ids"][:2]


def omit_normalizer_inverse(template: dict[str, Any]) -> None:
    node = next(node for node in template["formal_nodes"] if node["node_id"] == "V_formula")
    node["operation"] = "formal_identity"
    node["argument_ids"] = ["contact_weighted_sum_formula"]


def use_polynomial_denominator(template: dict[str, Any]) -> None:
    node = next(node for node in template["formal_nodes"] if node["node_id"] == "V_formula")
    node["argument_ids"][1] = "weighted_profile_sum_formula"


def break_physical_formula(template: dict[str, Any]) -> None:
    node = next(
        node
        for node in template["formal_nodes"]
        if node["node_id"] == "physical_weight_left_formula"
    )
    node["argument_ids"][0] = "W_norm"


def mutate_formal_assertion(template: dict[str, Any]) -> None:
    template["formal_assertions"][-1]["right_id"] = "K_direct_formula"


def mutate_input_shape(template: dict[str, Any]) -> None:
    template["outward_inputs"][0]["semantic_shape"] = "singleton"


@pytest.mark.parametrize(
    "mutator",
    [
        template_attack(replace_with_trivial_dag),
        template_attack(omit_direct_right_path),
        template_attack(replace_structural_q_with_unrelated_atom),
        template_attack(change_conductance_spectator),
        template_attack(collapse_to_two_profiles),
        template_attack(omit_normalizer_inverse),
        template_attack(use_polynomial_denominator),
        template_attack(break_physical_formula),
        template_attack(mutate_formal_assertion),
        template_attack(mutate_input_shape),
    ],
)
def test_attacker_rehashed_template_bypasses_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    value = copy.deepcopy(nondegenerate_request())
    mutator(value)
    assert_build_rejected(tmp_path, value, "fixed semantic template drift")


def test_template_sha_substitution_fails_closed(tmp_path: Path) -> None:
    value = copy.deepcopy(nondegenerate_request())
    value["semantic_template_sha256"] = "0" * 63 + "1"
    assert_build_rejected(tmp_path, value, "semantic template SHA drift")


def test_request_supplied_exact_formal_selectors_fail_closed(tmp_path: Path) -> None:
    top_level = copy.deepcopy(nondegenerate_request())
    top_level["formal_values"] = {"kappa": "3/5"}
    assert_build_rejected(tmp_path / "top", top_level, "request top-level key drift")

    input_level = copy.deepcopy(nondegenerate_request())
    input_level["inputs"][0]["value_exact"] = "8/1"
    assert_build_rejected(
        tmp_path / "input",
        input_level,
        "outward interval input key drift",
    )


@pytest.mark.parametrize(
    ("payload_factory", "expected"),
    [
        (
            lambda: canonical(nondegenerate_request()).replace(
                b'"schema": ',
                b'"schema": "duplicate",\n  "schema": ',
                1,
            ),
            "duplicate",
        ),
        (
            lambda: canonical(nondegenerate_request()).replace(
                b'"lower_exact": "8/1"',
                b'"lower_exact": 1.0',
                1,
            ),
            "non-integer JSON number",
        ),
        (
            lambda: canonical(
                {
                    **nondegenerate_request(),
                    "status": "OUTWARD_INTERVALS_AND_FIXED_FORMAL_IDENTITIES_ONLY_e\u0301",
                }
            ),
            "non-NFC",
        ),
    ],
)
def test_strict_json_attacks_fail_closed(
    tmp_path: Path,
    payload_factory: Callable[[], bytes],
    expected: str,
) -> None:
    request = tmp_path / "request.json"
    output = tmp_path / "artifact.json"
    request.write_bytes(payload_factory())
    request.chmod(0o444)
    result = run(str(BUILDER), "--request", str(request), "--output", str(output))
    assert result.returncode != 0
    assert expected in result.stderr
    assert not output.exists()


def test_noncanonical_rational_and_bool_alias_fail(tmp_path: Path) -> None:
    noncanonical = copy.deepcopy(nondegenerate_request())
    input_record(noncanonical, "M_L")["lower_exact"] = "16/2"
    assert_build_rejected(tmp_path / "fraction", noncanonical, "noncanonical rational")

    bool_alias = copy.deepcopy(nondegenerate_request())
    input_record(bool_alias, "M_L")["lower_exact"] = True
    assert_build_rejected(
        tmp_path / "bool",
        bool_alias,
        "canonical p/q rational required",
    )


def build_pair(tmp_path: Path) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    request = tmp_path / "request.json"
    artifact = tmp_path / "artifact.json"
    write_request(request)
    result = run(str(BUILDER), "--request", str(request), "--output", str(artifact))
    assert result.returncode == 0, result.stderr
    return request, artifact


def artifact_formal_node(value: dict[str, Any], node_id: str) -> dict[str, Any]:
    return next(
        node for node in value["formal_identity_proof"]["nodes"] if node["node_id"] == node_id
    )


def formal_bool_exponent(value: dict[str, Any]) -> None:
    artifact_formal_node(value, "G_formula")["value"]["terms"][0]["exponents"][0] = True


def formal_short_exponent(value: dict[str, Any]) -> None:
    artifact_formal_node(value, "G_formula")["value"]["terms"][0]["exponents"].pop()


def formal_unreduced_coefficient(value: dict[str, Any]) -> None:
    artifact_formal_node(value, "G_formula")["value"]["terms"][0]["coefficient_exact"] = "2/2"


def formal_zero_coefficient(value: dict[str, Any]) -> None:
    artifact_formal_node(value, "G_formula")["value"]["terms"][0]["coefficient_exact"] = "0/1"


def formal_duplicate_monomial(value: dict[str, Any]) -> None:
    terms = artifact_formal_node(value, "G_formula")["value"]["terms"]
    terms.append(copy.deepcopy(terms[0]))


def formal_reorder_terms(value: dict[str, Any]) -> None:
    artifact_formal_node(value, "V_formula")["value"]["terms"].reverse()


def formal_noninvertible_negative_power(value: dict[str, Any]) -> None:
    proof = value["formal_identity_proof"]
    kappa_index = proof["atom_order"].index("kappa")
    term = artifact_formal_node(value, "common_flux_formula")["value"]["terms"][0]
    term["exponents"][kappa_index] = -1


def formal_normalized_identity_tamper(value: dict[str, Any]) -> None:
    output = next(
        record
        for record in value["formal_identity_proof"]["outputs"]
        if record["output_name"] == "physical_weight_left_formula"
    )
    output["value"]["terms"][0]["coefficient_exact"] = "2/1"


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (formal_bool_exponent, "formal exponent vector"),
        (formal_short_exponent, "formal exponent vector"),
        (formal_unreduced_coefficient, "noncanonical rational"),
        (formal_zero_coefficient, "zero formal coefficient"),
        (formal_duplicate_monomial, "strictly canonical"),
        (formal_reorder_terms, "strictly canonical"),
        (formal_noninvertible_negative_power, "noninvertible formal atom"),
        (formal_normalized_identity_tamper, "artifact reconstruction drift"),
    ],
)
def test_formal_artifact_mutations_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
    expected: str,
) -> None:
    request, artifact = build_pair(tmp_path)
    artifact.chmod(0o644)
    value = json.loads(artifact.read_text(encoding="ascii"))
    mutator(value)
    artifact.write_bytes(canonical(value))
    artifact.chmod(0o444)
    result = run(str(VALIDATOR), "--request", str(request), "--artifact", str(artifact))
    assert result.returncode != 0
    assert expected in result.stderr


@pytest.mark.parametrize("implementation", ["builder", "validator"])
def test_intermediate_parent_replacement_cannot_redirect_reads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    implementation: str,
) -> None:
    outer = tmp_path / "outer"
    live = outer / "live"
    detached = outer / "detached"
    live.mkdir(parents=True)
    retained = live / "request.json"
    write_request(retained, nondegenerate_request())

    module = BUILDER_MODULE if implementation == "builder" else VALIDATOR_MODULE
    error_type = (
        BUILDER_MODULE.DagBuildError
        if implementation == "builder"
        else VALIDATOR_MODULE.DagVerificationError
    )
    original_open = os.open
    replaced = False

    def replacing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        descriptor = original_open(path, flags, mode, dir_fd=dir_fd)
        if path == "live" and dir_fd is not None and not replaced:
            replaced = True
            live.rename(detached)
            live.mkdir()
            write_request(live / "request.json", singleton_request())
        return descriptor

    monkeypatch.setattr(module.os, "open", replacing_open)
    with pytest.raises(error_type, match="directory chain changed"):
        if implementation == "builder":
            module.stable_snapshot(retained, immutable=True)
        else:
            module.retain(retained)
    assert replaced


def test_injected_short_writes_finish_before_atomic_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    payload = b"complete-before-publish" * 257
    original_write = os.write

    def short_write(descriptor: int, data: bytes) -> int:
        return original_write(descriptor, data[: min(17, len(data))])

    monkeypatch.setattr(BUILDER_MODULE.os, "write", short_write)
    BUILDER_MODULE.write_immutable_exclusive(output, payload)
    assert output.read_bytes() == payload
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_injected_short_write_then_enospc_cleans_stage_and_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_write = os.write
    calls = 0

    def short_then_enospc(descriptor: int, data: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original_write(descriptor, data[: min(23, len(data))])
        raise OSError(errno.ENOSPC, "injected no space")

    monkeypatch.setattr(BUILDER_MODULE.os, "write", short_then_enospc)
    with pytest.raises(OSError) as caught:
        BUILDER_MODULE.write_immutable_exclusive(output, b"x" * 4096)
    assert caught.value.errno == errno.ENOSPC
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_parent_fsync_enospc_after_link_removes_complete_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_fsync = os.fsync
    calls = 0

    def fail_parent_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError(errno.ENOSPC, "injected parent fsync failure")
        original_fsync(descriptor)

    monkeypatch.setattr(BUILDER_MODULE.os, "fsync", fail_parent_fsync)
    with pytest.raises(OSError) as caught:
        BUILDER_MODULE.write_immutable_exclusive(output, b"already-complete")
    assert caught.value.errno == errno.ENOSPC
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_keyboard_interrupt_during_write_cleans_owned_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_write = os.write
    calls = 0

    def partial_then_interrupt(descriptor: int, data: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original_write(descriptor, data[: min(19, len(data))])
        raise KeyboardInterrupt

    monkeypatch.setattr(BUILDER_MODULE.os, "write", partial_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"x" * 4096)
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_keyboard_interrupt_after_link_fsync_cleans_owned_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_fsync = os.fsync
    calls = 0

    def interrupt_after_parent_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        original_fsync(descriptor)
        if calls == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(BUILDER_MODULE.os, "fsync", interrupt_after_parent_fsync)
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"complete-but-unacknowledged")
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_keyboard_interrupt_rollback_preserves_foreign_stage_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    foreign_payload = b"foreign-stage-identity"

    def replace_stage_then_interrupt(descriptor: int, data: bytes) -> int:
        del descriptor, data
        stages = list(tmp_path.glob(".candidate-exact-dag-stage-*"))
        assert len(stages) == 1
        stages[0].unlink()
        stages[0].write_bytes(foreign_payload)
        raise KeyboardInterrupt

    monkeypatch.setattr(BUILDER_MODULE.os, "write", replace_stage_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"owned-stage-payload")
    assert not output.exists()
    stages = list(tmp_path.glob(".candidate-exact-dag-stage-*"))
    assert len(stages) == 1
    assert stages[0].read_bytes() == foreign_payload


def test_keyboard_interrupt_rollback_preserves_foreign_final_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    foreign_payload = b"foreign-final-identity"
    original_fsync = os.fsync
    calls = 0

    def replace_final_after_parent_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        original_fsync(descriptor)
        if calls == 2:
            output.unlink()
            output.write_bytes(foreign_payload)
            raise KeyboardInterrupt

    monkeypatch.setattr(BUILDER_MODULE.os, "fsync", replace_final_after_parent_fsync)
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"owned-final-payload")
    assert output.read_bytes() == foreign_payload
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_open_interrupt_transaction_cleans_unacknowledged_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    output = tmp_path / "artifact.json"
    original_await_ready = BUILDER_MODULE.StageCreationTransaction.await_ready
    transactions: list[Any] = []
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def ready_then_interrupt(
        transaction: Any,
    ) -> None:
        original_await_ready(transaction)
        transactions.append(transaction)
        raise interrupt_type("post-open interruption")

    monkeypatch.setattr(
        BUILDER_MODULE.StageCreationTransaction,
        "await_ready",
        ready_then_interrupt,
    )
    with pytest.raises(interrupt_type):
        BUILDER_MODULE.write_immutable_exclusive(output, b"never-written")
    assert len(transactions) == 1
    assert transactions[0].descriptor is None
    assert not transactions[0]._thread.is_alive()
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_post_open_interrupt_preserves_identical_metadata_foreign_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_await_ready = BUILDER_MODULE.StageCreationTransaction.await_ready
    original_open = os.open
    original_close = os.close
    foreign_identity: tuple[int, int] | None = None
    transaction_seen: Any = None
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def ready_replace_then_interrupt(transaction: Any) -> None:
        nonlocal foreign_identity, transaction_seen
        original_await_ready(transaction)
        transaction_seen = transaction
        assert transaction.identity is not None
        os.unlink(transaction.leaf, dir_fd=transaction.parent_descriptor)
        foreign = original_open(
            transaction.leaf,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o444,
            dir_fd=transaction.parent_descriptor,
        )
        observed = os.fstat(foreign)
        foreign_identity = observed.st_dev, observed.st_ino
        assert foreign_identity != transaction.identity
        assert observed.st_uid == os.geteuid()
        assert observed.st_nlink == 1
        assert observed.st_size == 0
        assert not observed.st_mode & 0o222
        original_close(foreign)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        BUILDER_MODULE.StageCreationTransaction,
        "await_ready",
        ready_replace_then_interrupt,
    )
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"owned-stage")
    assert transaction_seen is not None
    assert transaction_seen.descriptor is None
    assert not transaction_seen._thread.is_alive()
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not output.exists()
    stages = list(tmp_path.glob(".candidate-exact-dag-stage-*"))
    assert len(stages) == 1
    observed = stages[0].stat()
    assert (observed.st_dev, observed.st_ino) == foreign_identity
    assert observed.st_uid == os.geteuid()
    assert observed.st_nlink == 1
    assert observed.st_size == 0
    assert not observed.st_mode & 0o222


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_link_interrupt_discovers_and_cleans_unacknowledged_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    output = tmp_path / "artifact.json"
    original_link = os.link

    def link_then_interrupt(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        original_link(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
            follow_symlinks=follow_symlinks,
        )
        raise interrupt_type("post-link interruption")

    monkeypatch.setattr(BUILDER_MODULE.os, "link", link_then_interrupt)
    with pytest.raises(interrupt_type):
        BUILDER_MODULE.write_immutable_exclusive(output, b"complete-before-link")
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_post_link_interrupt_preserves_replacement_final_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    foreign_payload = b"foreign-after-final-link"
    original_link = os.link

    def link_replace_then_interrupt(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        original_link(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
            follow_symlinks=follow_symlinks,
        )
        os.unlink(destination, dir_fd=dst_dir_fd)
        foreign = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o444,
            dir_fd=dst_dir_fd,
        )
        os.write(foreign, foreign_payload)
        os.close(foreign)
        raise SystemExit("post-link replacement")

    monkeypatch.setattr(BUILDER_MODULE.os, "link", link_replace_then_interrupt)
    with pytest.raises(SystemExit):
        BUILDER_MODULE.write_immutable_exclusive(output, b"owned-final")
    assert output.read_bytes() == foreign_payload
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_descriptor_release_interrupt_rolls_back_acknowledged_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    original_release = BUILDER_MODULE.close_descriptors
    calls = 0

    def release_then_interrupt(descriptors: tuple[int, ...] | list[int]) -> None:
        nonlocal calls
        calls += 1
        original_release(descriptors)
        if calls == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(BUILDER_MODULE, "close_descriptors", release_then_interrupt)
    with pytest.raises(KeyboardInterrupt):
        BUILDER_MODULE.write_immutable_exclusive(output, b"fsynced-before-release")
    assert calls == 2
    assert not output.exists()
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


def test_descriptor_release_interrupt_preserves_replacement_final_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "artifact.json"
    foreign_payload = b"foreign-after-descriptor-release"
    original_release = BUILDER_MODULE.close_descriptors
    calls = 0

    def release_replace_then_interrupt(
        descriptors: tuple[int, ...] | list[int],
    ) -> None:
        nonlocal calls
        calls += 1
        original_release(descriptors)
        if calls == 2:
            output.unlink()
            output.write_bytes(foreign_payload)
            raise SystemExit("post-release replacement")

    monkeypatch.setattr(
        BUILDER_MODULE,
        "close_descriptors",
        release_replace_then_interrupt,
    )
    with pytest.raises(SystemExit):
        BUILDER_MODULE.write_immutable_exclusive(output, b"owned-before-release")
    assert calls == 2
    assert output.read_bytes() == foreign_payload
    assert not list(tmp_path.glob(".candidate-exact-dag-stage-*"))


@pytest.mark.parametrize(
    ("consumer", "context"),
    [
        ("builder_request", "request"),
        ("validator_request", "request"),
        ("validator_artifact", "artifact"),
    ],
)
def test_deep_json_recursion_uses_stable_error_interface(
    tmp_path: Path,
    consumer: str,
    context: str,
) -> None:
    deep_payload = b'{"nested":' + b"[" * 100_000 + b"0" + b"]" * 100_000 + b"}\n"
    assert len(deep_payload) < 2_000_000

    request = tmp_path / "request.json"
    artifact = tmp_path / "artifact.json"
    if consumer == "builder_request":
        request.write_bytes(deep_payload)
        request.chmod(0o444)
        result = run(str(BUILDER), "--request", str(request), "--output", str(artifact))
        stable_prefix = "ERROR CandidateNativeExactExpressionDagBuild:"
        assert not artifact.exists()
    elif consumer == "validator_request":
        request.write_bytes(deep_payload)
        request.chmod(0o444)
        artifact.write_bytes(b"{}\n")
        artifact.chmod(0o444)
        result = run(
            str(VALIDATOR),
            "--request",
            str(request),
            "--artifact",
            str(artifact),
        )
        stable_prefix = "ERROR CandidateNativeExactExpressionDagValidation:"
    else:
        write_request(request)
        artifact.write_bytes(deep_payload)
        artifact.chmod(0o444)
        result = run(
            str(VALIDATOR),
            "--request",
            str(request),
            "--artifact",
            str(artifact),
        )
        stable_prefix = "ERROR CandidateNativeExactExpressionDagValidation:"

    assert result.returncode == 1
    assert result.stderr.startswith(stable_prefix)
    assert f"strict JSON failure for {context}:" in result.stderr
    assert "Traceback" not in result.stderr


def test_writable_symlink_hardlink_and_fifo_inputs_fail(tmp_path: Path) -> None:
    writable = tmp_path / "writable.json"
    writable.write_bytes(canonical(nondegenerate_request()))
    result = run(
        str(BUILDER),
        "--request",
        str(writable),
        "--output",
        str(tmp_path / "writable-output.json"),
    )
    assert result.returncode != 0
    assert "immutable single-link" in result.stderr

    anchor = tmp_path / "anchor.json"
    write_request(anchor)
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(anchor)
    result = run(
        str(BUILDER),
        "--request",
        str(symlink),
        "--output",
        str(tmp_path / "symlink-output.json"),
    )
    assert result.returncode != 0
    assert "symlink" in result.stderr

    hardlink = tmp_path / "hardlink.json"
    os.link(anchor, hardlink)
    result = run(
        str(BUILDER),
        "--request",
        str(anchor),
        "--output",
        str(tmp_path / "hardlink-output.json"),
    )
    assert result.returncode != 0
    assert "single-link" in result.stderr

    fifo = tmp_path / "request.pipe"
    os.mkfifo(fifo, 0o444)
    result = run(
        str(BUILDER),
        "--request",
        str(fifo),
        "--output",
        str(tmp_path / "fifo-output.json"),
        timeout=2.0,
    )
    assert result.returncode != 0
    assert "regular file" in result.stderr


def test_fifo_artifact_validator_and_check_fail_without_blocking(tmp_path: Path) -> None:
    request, artifact = build_pair(tmp_path / "pair")
    artifact.chmod(0o644)
    artifact.unlink()
    os.mkfifo(artifact, 0o444)
    result = run(
        str(VALIDATOR),
        "--request",
        str(request),
        "--artifact",
        str(artifact),
        timeout=2.0,
    )
    assert result.returncode != 0
    assert "regular file" in result.stderr

    check_fifo = tmp_path / "check.pipe"
    os.mkfifo(check_fifo, 0o444)
    result = run(
        str(BUILDER),
        "--request",
        str(request),
        "--output",
        str(check_fifo),
        "--check",
        timeout=2.0,
    )
    assert result.returncode != 0
    assert "regular file" in result.stderr


def test_symlink_and_existing_outputs_fail_closed(tmp_path: Path) -> None:
    request = tmp_path / "request.json"
    target = tmp_path / "target.json"
    symlink = tmp_path / "output.json"
    write_request(request)
    target.write_text("sentinel", encoding="ascii")
    symlink.symlink_to(target)
    result = run(str(BUILDER), "--request", str(request), "--output", str(symlink))
    assert result.returncode != 0
    assert target.read_text(encoding="ascii") == "sentinel"

    existing = tmp_path / "existing.json"
    existing.write_text("sentinel", encoding="ascii")
    result = run(str(BUILDER), "--request", str(request), "--output", str(existing))
    assert result.returncode != 0
    assert existing.read_text(encoding="ascii") == "sentinel"


def test_claim_request_substitution_and_artifact_hardlink_fail(tmp_path: Path) -> None:
    request, artifact = build_pair(tmp_path)
    artifact.chmod(0o644)
    value = json.loads(artifact.read_text(encoding="ascii"))
    value["claim_boundary"]["science_executed"] = True
    artifact.write_bytes(canonical(value))
    artifact.chmod(0o444)
    result = run(str(VALIDATOR), "--request", str(request), "--artifact", str(artifact))
    assert result.returncode != 0
    assert "exact false claim map" in result.stderr

    request, artifact = build_pair(tmp_path / "substitution")
    request.chmod(0o644)
    request.write_bytes(canonical(singleton_request()))
    request.chmod(0o444)
    result = run(str(VALIDATOR), "--request", str(request), "--artifact", str(artifact))
    assert result.returncode != 0

    request, artifact = build_pair(tmp_path / "hardlink")
    linked = tmp_path / "linked-artifact.json"
    os.link(artifact, linked)
    result = run(str(VALIDATOR), "--request", str(request), "--artifact", str(artifact))
    assert result.returncode != 0
    assert "single-link" in result.stderr
