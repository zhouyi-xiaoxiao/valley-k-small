from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

import pytest
from test_continuum_c1_n0_candidate_native_raw_axis_formula_v2 import (
    NeutralFixture,
    canonical,
    create_neutral_fixture,
    domain_hash,
    immutable_json,
    load_isolated_module,
    replace_json,
    run_producer,
    run_verifier,
    sha256_file,
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def _commitment_message(commitment: dict[str, Any]) -> dict[str, Any]:
    return {
        "authority": commitment["authority"],
        "candidate_bundle": commitment["candidate_bundle"],
        "claim_boundary": commitment["claim_boundary"],
        "ordering": commitment["ordering"],
    }


def _refresh_request_replay(fixture: NeutralFixture, request: dict[str, Any]) -> None:
    request["shared_replay_context_sha256"] = domain_hash(
        "encounter-continuum-c1-n0-shared-replay-context-v1",
        {
            "external_predecessor_commitment_sha256": request["external_predecessor_commitment"][
                "sha256"
            ],
            "replay_plan_sha256": request["plan"]["sha256"],
            "shared_precommit_context_sha256": request["shared_precommit_context_sha256"],
        },
    )
    replace_json(fixture.request, request)


def reseal_commitment(
    fixture: NeutralFixture,
    commitment: dict[str, Any] | None = None,
) -> None:
    current = load(fixture.commitment) if commitment is None else commitment
    current["commitment_message_sha256"] = domain_hash(
        "encounter-external-predecessor-commitment-message-v1",
        _commitment_message(current),
    )
    replace_json(fixture.commitment, current)
    request = load(fixture.request)
    request["external_predecessor_commitment"]["sha256"] = sha256_file(fixture.commitment)
    _refresh_request_replay(fixture, request)


def reseal_bundle(
    fixture: NeutralFixture,
    bundle: dict[str, Any] | None = None,
) -> None:
    current = load(fixture.bundle) if bundle is None else bundle
    replace_json(fixture.bundle, current)
    commitment = load(fixture.commitment)
    commitment["candidate_bundle"]["sha256"] = sha256_file(fixture.bundle)
    reseal_commitment(fixture, commitment)


def reseal_plan(
    fixture: NeutralFixture,
    plan: dict[str, Any] | None = None,
) -> None:
    current = load(fixture.plan) if plan is None else plan
    for entry in current["entries"]:
        projection = dict(entry)
        projection.pop("precommit_projection_sha256", None)
        entry["precommit_projection_sha256"] = domain_hash(
            "encounter-continuum-c1-n0-role-precommit-projection-v1",
            projection,
        )
    shared_digest = domain_hash(
        "encounter-continuum-c1-n0-shared-precommit-context-v1",
        current["shared_context"],
    )
    current["shared_precommit_context_sha256"] = shared_digest
    replace_json(fixture.plan, current)
    bundle = load(fixture.bundle)
    bundle["replay_plan"]["sha256"] = sha256_file(fixture.plan)
    bundle["shared_precommit_context_sha256"] = shared_digest
    replace_json(fixture.bundle, bundle)
    commitment = load(fixture.commitment)
    commitment["candidate_bundle"]["sha256"] = sha256_file(fixture.bundle)
    commitment["commitment_message_sha256"] = domain_hash(
        "encounter-external-predecessor-commitment-message-v1",
        _commitment_message(commitment),
    )
    replace_json(fixture.commitment, commitment)
    request = load(fixture.request)
    request["plan"]["sha256"] = sha256_file(fixture.plan)
    request["external_predecessor_commitment"]["sha256"] = sha256_file(fixture.commitment)
    request["shared_precommit_context_sha256"] = shared_digest
    _refresh_request_replay(fixture, request)


def mutate_request(
    fixture: NeutralFixture,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    request = load(fixture.request)
    mutation(request)
    replace_json(fixture.request, request)


def alias_planned_output(
    fixture: NeutralFixture,
    *,
    entry_index: int,
    output_role: str,
    target: Path,
) -> None:
    plan = load(fixture.plan)
    entry = plan["entries"][entry_index]
    entry["outputs"][output_role]["path"] = str(target)
    if output_role == "artifact":
        entry["invocations"]["producer"]["argv"][-1] = str(target)
        entry["invocations"]["verifier"]["argv"][-3] = str(target)
    elif output_role == "validation_receipt":
        entry["invocations"]["verifier"]["argv"][-1] = str(target)
    else:
        raise AssertionError(f"unexpected output role: {output_role}")
    reseal_plan(fixture, plan)


def assert_producer_hold(
    fixture: NeutralFixture,
    code: str,
    detail: str | None = None,
) -> None:
    result = run_producer(fixture)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert code in result.stderr
    if detail is not None:
        assert detail in result.stderr


def assert_verifier_hold(
    fixture: NeutralFixture,
    code: str,
    detail: str | None = None,
) -> None:
    result = run_verifier(fixture)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert code in result.stderr
    if detail is not None:
        assert detail in result.stderr


def length_framed_digest(domain: str, records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    domain_bytes = domain.encode("ascii")
    digest.update(len(domain_bytes).to_bytes(8, "big"))
    digest.update(domain_bytes)
    for record in records:
        payload = canonical(record)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def test_rejects_noncanonical_request_bytes(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    fixture.request.chmod(0o600)
    fixture.request.write_bytes(fixture.request.read_bytes() + b" ")
    fixture.request.chmod(0o400)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "noncanonical")


def test_rejects_commitment_pin_hash_substitution(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    mutate_request(
        fixture,
        lambda request: request["external_predecessor_commitment"].update({"sha256": "0" * 64}),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "SHA-256 mismatch")


def test_rejects_commitment_path_substitution_even_with_coherent_hash(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    mutate_request(
        fixture,
        lambda request: request["external_predecessor_commitment"].update(
            {"path": str(fixture.plan), "sha256": sha256_file(fixture.plan)}
        ),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST")


def test_rejects_inner_commitment_schema_after_coherent_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    commitment = load(fixture.commitment)
    commitment["schema"] = "encounter_external_predecessor_commitment_v0"
    reseal_commitment(fixture, commitment)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "schema/status")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authentication_class", "same_process_or_child_process_assertion"),
        ("structural_validation_only", False),
    ),
)
def test_rejects_ineligible_or_promoted_commitment_authentication(
    tmp_path: Path,
    field: str,
    value: Any,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    commitment = load(fixture.commitment)
    commitment["authentication"][field] = value
    reseal_commitment(fixture, commitment)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "authentication")


def test_rejects_commitment_claim_of_locally_proven_externality(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    commitment = load(fixture.commitment)
    commitment["claim_boundary"]["externality_proven_by_local_code"] = True
    reseal_commitment(fixture, commitment)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "claim mismatch")


@pytest.mark.parametrize(
    ("container", "field", "value"),
    (
        ("authentication", "evidence_identifier", "artifact_sha256=deadbeef"),
        ("authority", "authority_identifier", "role10-output-digest"),
        ("authority", "trust_domain_identifier", "PASS receipt"),
        ("authentication", "evidence_identifier", "ｒｅｓｕｌｔ－ｏｕｔｐｕｔ"),
        ("authentication", "evidence_identifier", "artifactsha256deadbeef"),
        ("authority", "authority_identifier", "role10outputdigest"),
    ),
)
def test_rejects_commitment_future_result_evidence_after_coherent_reseal(
    tmp_path: Path,
    container: str,
    field: str,
    value: str,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    commitment = load(fixture.commitment)
    commitment[container][field] = value
    reseal_commitment(fixture, commitment)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "future-result evidence value forbidden",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_REQUEST",
        "future-result evidence value forbidden",
    )


def test_rejects_plan_pin_hash_substitution(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    mutate_request(
        fixture,
        lambda request: request["plan"].update({"sha256": "f" * 64}),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "SHA-256 mismatch")


def test_rejects_plan_schema_after_complete_chain_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["schema"] = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v0"
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "schema/status")


def test_rejects_string_plan_role_and_bool_request_role_id(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["entries"][0]["role"] = "8"
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "entry order")

    fixture = create_neutral_fixture(tmp_path / "bool_alias")
    mutate_request(
        fixture,
        lambda request: request["role"].update({"role_id": True}),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "role mismatch")


def test_rejects_request_slot_path_and_status_drift(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["entries"][0]["request"]["path"] = str(fixture.root / "other-request.json")
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "request slot")

    fixture = create_neutral_fixture(tmp_path / "status")
    plan = load(fixture.plan)
    plan["entries"][0]["request"]["status"] = "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT"
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "request slot")


def test_rejects_exact_argv_or_cwd_drift_after_projection_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["entries"][0]["invocations"]["producer"]["argv"].append("--check")
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "invocation")

    fixture = create_neutral_fixture(tmp_path / "cwd")
    plan = load(fixture.plan)
    plan["entries"][0]["invocations"]["verifier"]["cwd"] = str(fixture.root)
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "invocation")


def test_rejects_malformed_peer_plan_entry_after_projection_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["entries"][1]["request"]["path"] = "relative-role9-request.json"
    reseal_plan(fixture, plan)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "canonical absolute path",
    )


def test_rejects_result_leakage_key_in_plan(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["observed_role8_summary"] = {"axis_cell_count": 5037}
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "replay plan")


def test_rejects_result_leakage_value_in_peer_output_slot(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    leaked = fixture.root / f"role9_result_digest_{'a' * 64}.json"
    plan["entries"][1]["outputs"]["artifact"]["path"] = str(leaked)
    plan["entries"][1]["invocations"]["producer"]["argv"][-1] = str(leaked)
    plan["entries"][1]["invocations"]["verifier"]["argv"][-3] = str(leaked)
    reseal_plan(fixture, plan)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "metadata value forbidden",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_REQUEST",
        "metadata value forbidden",
    )


def test_rejects_result_leakage_value_in_request_pin_path(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    leaked = fixture.root / f"role8_result_digest_{'b' * 64}.commitment.json"
    immutable_json(leaked, load(fixture.commitment))
    mutate_request(
        fixture,
        lambda request: request["external_predecessor_commitment"].update(
            {"path": str(leaked), "sha256": sha256_file(leaked)}
        ),
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "metadata value forbidden",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_REQUEST",
        "metadata value forbidden",
    )


def test_rejects_shared_inventory_context_drift_after_full_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["shared_context"]["partition_inventory_sha256"] = "0" * 64
    reseal_plan(fixture, plan)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "inventory differs",
    )


def test_rejects_absolute_shared_authority_pin_after_full_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["shared_context"]["member_spec"]["path"] = str(fixture.authorities["member_spec"])
    reseal_plan(fixture, plan)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "invalid relative source pin",
    )


def test_rejects_selected_method_record_drift_after_projection_reseal(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    plan["entries"][0]["method_selection"][0]["method_parameter_sha256"] = "0" * 64
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_METHOD", "selected method")


def test_rejects_runtime_closure_drift_after_full_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    closure = load(fixture.runtime_closure)
    closure["native_runtime"]["mpfr"] = "synthetic-drift"
    replace_json(fixture.runtime_closure, closure)
    plan = load(fixture.plan)
    plan["entries"][0]["implementation_runtime_closure"]["sha256"] = sha256_file(
        fixture.runtime_closure
    )
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_RUNTIME", "version mismatch")


def test_rejects_runtime_native_library_role_drift_after_full_reseal(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    closure = load(fixture.runtime_closure)
    closure["native_libraries"][0]["role"] = "libgmp"
    replace_json(fixture.runtime_closure, closure)
    plan = load(fixture.plan)
    plan["entries"][0]["implementation_runtime_closure"]["sha256"] = sha256_file(
        fixture.runtime_closure
    )
    reseal_plan(fixture, plan)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_RUNTIME",
        "role/order mismatch",
    )


def test_rejects_bundle_member_pin_drift_after_coherent_reseal(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    bundle = load(fixture.bundle)
    bundle["member_spec"]["sha256"] = sha256_file(fixture.authorities["method_parameters"])
    reseal_bundle(fixture, bundle)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "bundle member")


def test_rejects_partition_execution_order_drift(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    bindings = plan["entries"][0]["partition_path_bindings"]
    bindings[0], bindings[1] = bindings[1], bindings[0]
    reseal_plan(fixture, plan)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "unsorted")


@pytest.mark.parametrize(
    "target_kind",
    (
        "reference_density",
        "runtime_source",
        "partition",
        "plan",
        "bundle",
        "commitment",
    ),
)
def test_rejects_peer_artifact_alias_to_any_replay_input(
    tmp_path: Path,
    target_kind: str,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    targets = {
        "reference_density": fixture.authorities["reference_density"],
        "runtime_source": fixture.producer,
        "partition": fixture.partitions[0],
        "plan": fixture.plan,
        "bundle": fixture.bundle,
        "commitment": fixture.commitment,
    }
    alias_planned_output(
        fixture,
        entry_index=1,
        output_role="artifact",
        target=targets[target_kind],
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "planned output aliases",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_REQUEST",
        "planned output aliases",
    )


def test_rejects_peer_artifact_alias_to_another_replay_slot(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    role10_receipt = Path(plan["entries"][2]["outputs"]["validation_receipt"]["path"])
    alias_planned_output(
        fixture,
        entry_index=1,
        output_role="artifact",
        target=role10_receipt,
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "paths are not unique",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_REQUEST",
        "paths are not unique",
    )


@pytest.mark.parametrize(
    ("entry_index", "output_role"),
    (
        (1, "artifact"),
        (1, "validation_receipt"),
        (2, "artifact"),
        (2, "validation_receipt"),
    ),
)
def test_preexisting_peer_output_slots_are_preserved(
    tmp_path: Path,
    entry_index: int,
    output_role: str,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    plan = load(fixture.plan)
    peer_path = Path(plan["entries"][entry_index]["outputs"][output_role]["path"])
    immutable_json(peer_path, {"foreign": "peer-output"})
    before = peer_path.read_bytes()
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_OUTPUT",
        "artifact/receipt slot is not fresh",
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "artifact/receipt slot is not fresh",
    )
    assert peer_path.read_bytes() == before


def test_preexisting_artifact_and_receipt_slots_are_preserved(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    immutable_json(fixture.output, {"foreign": "artifact"})
    before = fixture.output.read_bytes()
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_OUTPUT", "not fresh")
    assert fixture.output.read_bytes() == before

    fixture = create_neutral_fixture(tmp_path / "receipt")
    immutable_json(fixture.receipt, {"foreign": "receipt"})
    before = fixture.receipt.read_bytes()
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_OUTPUT", "not fresh")
    assert fixture.receipt.read_bytes() == before


def test_verifier_rejects_geometry_digest_mutation(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    output = load(fixture.output)
    output["geometry_inventory"]["sha256"] = "0" * 64
    replace_json(fixture.output, output)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )
    assert not fixture.receipt.exists()


def test_verifier_rejects_coherently_rehashed_geometry_order_mutation(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    output = load(fixture.output)
    geometry = output["geometry_inventory"]
    records = geometry["records"]
    records[1], records[2] = records[2], records[1]
    geometry["sha256"] = length_framed_digest(geometry["digest_domain"], records)
    replace_json(fixture.output, output)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )
    assert not fixture.receipt.exists()


@pytest.mark.parametrize(
    "target_kind",
    ("peer_runtime_source", "peer_only_authority", "partition"),
)
def test_postpublication_same_byte_peer_input_replacement_removes_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    target_kind: str,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    plan = load(fixture.plan)
    targets = {
        "peer_runtime_source": Path(
            plan["entries"][1]["implementation_runtime_closure"]["producer"]["path"]
        ),
        "peer_only_authority": fixture.authorities["configuration_initial_geometry"],
        "partition": fixture.partitions[0],
    }
    target = targets[target_kind]
    module_name = f"role8_v2_peer_replacement_{target_kind}_{id(tmp_path)}"
    module = load_isolated_module(fixture.verifier, module_name)
    monkeypatch.chdir(fixture.report)
    original_publish = module._publish_receipt
    replaced = False

    def publish_then_replace(path: Path, payload: bytes) -> tuple[int, int]:
        nonlocal replaced
        identity = original_publish(path, payload)
        replacement = target.with_name(f".{target.name}.same-byte-replacement")
        replacement.write_bytes(target.read_bytes())
        replacement.chmod(0o400)
        os.replace(replacement, target)
        replaced = True
        return identity

    monkeypatch.setattr(module, "_publish_receipt", publish_then_replace)
    try:
        returncode = module.main(
            [
                "--request",
                str(fixture.request),
                "--output",
                str(fixture.output),
                "--receipt",
                str(fixture.receipt),
            ]
        )
        captured = capsys.readouterr()
        assert replaced is True
        assert returncode == 2
        assert "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_IMMUTABLE" in captured.err
        assert "retained input image changed" in captured.err
        assert not fixture.receipt.exists()
    finally:
        import sys

        sys.modules.pop(module_name, None)


def test_receipt_publication_post_link_swap_preserves_foreign_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    module = load_isolated_module(fixture.verifier, "role8_v2_receipt_toctou")
    monkeypatch.chdir(fixture.report)
    receipt = module.validate(fixture.request, fixture.output)
    payload = module.canonical_bytes(receipt)
    real_link = os.link

    def swap_after_link(
        source: str,
        destination: str,
        *,
        src_dir_fd: int,
        dst_dir_fd: int,
        follow_symlinks: bool,
    ) -> None:
        real_link(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
            follow_symlinks=follow_symlinks,
        )
        os.unlink(destination, dir_fd=dst_dir_fd)
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o400,
            dir_fd=dst_dir_fd,
        )
        try:
            os.write(descriptor, b"FOREIGN-RECEIPT")
        finally:
            os.close(descriptor)

    monkeypatch.setattr(module.os, "link", swap_after_link)
    with pytest.raises(module.CandidateRawAxisValidationFailure, match="installation mismatch"):
        module._publish_receipt(fixture.receipt, payload)
    assert fixture.receipt.read_bytes() == b"FOREIGN-RECEIPT"
    assert not list(fixture.root.glob(f".{fixture.receipt.name}.stage.*"))


def test_postpublication_dependency_drift_removes_owned_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    module = load_isolated_module(fixture.verifier, "role8_v2_dependency_toctou")
    monkeypatch.chdir(fixture.report)
    original_capture = module._capture_receipt_dependencies
    capture_count = 0

    def drifting_capture(receipt: dict[str, Any]) -> tuple[Any, ...]:
        nonlocal capture_count
        state = original_capture(receipt)
        capture_count += 1
        if capture_count == 2:
            return (
                *state,
                (
                    str(fixture.root / "synthetic-drift"),
                    "0" * 64,
                    (0, 0, 0, 0, 0, 0, 0, 0),
                ),
            )
        return state

    monkeypatch.setattr(module, "_capture_receipt_dependencies", drifting_capture)
    result = module.main(
        [
            "--request",
            str(fixture.request),
            "--output",
            str(fixture.output),
            "--receipt",
            str(fixture.receipt),
        ]
    )
    captured = capsys.readouterr()
    assert result == 2
    assert capture_count == 2
    assert "receipt dependency identity drift after publication" in captured.err
    assert not fixture.receipt.exists()
    assert not list(fixture.root.glob(f".{fixture.receipt.name}.stage.*"))
