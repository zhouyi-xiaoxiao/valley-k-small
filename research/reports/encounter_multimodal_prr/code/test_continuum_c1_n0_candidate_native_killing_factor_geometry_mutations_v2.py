"""Semantic mutation tests for the fail-closed role-10 protocol shell."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pytest
import test_continuum_c1_n0_candidate_native_killing_factor_geometry_v2 as base

producer = base.producer
verifier = base.verifier


def refresh_chain(fixture: dict[str, Any]) -> None:
    """Recompute every legitimate protocol digest after an in-memory mutation."""

    plan = fixture["plan"]
    precommit = base.digest(producer.PRECOMMIT_CONTEXT_DOMAIN, plan["shared_context"])
    plan["shared_precommit_context_sha256"] = precommit
    for entry in plan["entries"]:
        projection = {
            key: value for key, value in entry.items() if key != "precommit_projection_sha256"
        }
        entry["precommit_projection_sha256"] = base.digest(
            producer.PRECOMMIT_PROJECTION_DOMAIN, projection
        )
    base.replace_immutable(fixture["plan_path"], plan)

    bundle = fixture["bundle"]
    bundle["replay_plan"] = base.pin(fixture["plan_path"])
    bundle["shared_precommit_context_sha256"] = precommit
    base.replace_immutable(fixture["bundle_path"], bundle)

    commitment = fixture["commitment"]
    commitment["candidate_bundle"] = base.pin(fixture["bundle_path"])
    message = {
        "authority": commitment["authority"],
        "candidate_bundle": commitment["candidate_bundle"],
        "claim_boundary": commitment["claim_boundary"],
        "ordering": commitment["ordering"],
    }
    commitment["commitment_message_sha256"] = base.digest(
        producer.COMMITMENT_MESSAGE_DOMAIN, message
    )
    base.replace_immutable(fixture["commitment_path"], commitment)

    request = fixture["request"]
    request["external_predecessor_commitment"] = base.pin(fixture["commitment_path"])
    request["plan"] = base.pin(fixture["plan_path"])
    request["shared_precommit_context_sha256"] = precommit
    request["shared_replay_context_sha256"] = base.digest(
        producer.REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": base.sha256(
                fixture["commitment_path"].read_bytes()
            ),
            "replay_plan_sha256": base.sha256(fixture["plan_path"].read_bytes()),
            "shared_precommit_context_sha256": precommit,
        },
    )
    base.replace_immutable(fixture["request_path"], request)


def assert_producer_hold(
    fixture: dict[str, Any],
    expected: str,
    detail: str | None = None,
) -> None:
    with pytest.raises(producer.CandidateKillingFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert captured.value.code == expected
    if detail is not None:
        assert detail in captured.value.detail
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()


def assert_verifier_hold(
    fixture: dict[str, Any],
    expected: str,
    detail: str | None = None,
) -> None:
    with pytest.raises(verifier.CandidateKillingVerificationFailure) as captured:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == expected
    if detail is not None:
        assert detail in captured.value.detail
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()


def alias_planned_output(
    fixture: dict[str, Any],
    *,
    entry_index: int,
    output_role: str,
    target: Path,
) -> None:
    entry = fixture["plan"]["entries"][entry_index]
    entry["outputs"][output_role]["path"] = str(target)
    if output_role == "artifact":
        for invocation_role in ("producer", "verifier"):
            argv = entry["invocations"][invocation_role]["argv"]
            argv[argv.index("--output") + 1] = str(target)
    elif output_role == "validation_receipt":
        argv = entry["invocations"]["verifier"]["argv"]
        argv[argv.index("--receipt") + 1] = str(target)
    else:
        raise AssertionError(f"unexpected output role: {output_role}")
    refresh_chain(fixture)


def _mutate_design_authority(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][2]["input_authorities"]["configuration_design"] = base.pin(
        fixture["paths"]["configuration_test"]
    )


def _mutate_partition_identity(fixture: dict[str, Any]) -> None:
    first, second = fixture["plan"]["entries"][2]["partition_path_bindings"][:2]
    first["coordinate"] = second["coordinate"]


def _mutate_role8_external_closure(fixture: dict[str, Any]) -> None:
    fixture["role8_runtime_closure"].pop("python_imports")
    base.replace_immutable(
        fixture["role8_runtime_closure_path"],
        fixture["role8_runtime_closure"],
    )
    fixture["plan"]["entries"][0]["implementation_runtime_closure"] = {
        "path": str(fixture["role8_runtime_closure_path"]),
        "schema": verifier.ROLE8_RUNTIME_CLOSURE_SCHEMA,
        "sha256": base.sha256(fixture["role8_runtime_closure_path"].read_bytes()),
    }


def _mutate_role9_inline_closure(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][1]["implementation_runtime_closure"].pop("verifier")


def _mutate_role8_method_order(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][0]["method_selection"].reverse()


def _mutate_role9_method_identifier(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][1]["method_selection"]["primary_parameter_id"] = (
        "stationary_directed_mpfr_320_uncommitted"
    )


def _mutate_role8_request_schema(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][0]["request"]["schema"] = (
        "encounter_continuum_c1_n0_raw_axis_formula_request_uncommitted"
    )


def _mutate_role9_authority(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][1]["input_authorities"]["configuration_design"] = base.pin(
        fixture["paths"]["configuration_test"]
    )


def _mutate_role8_invocation(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][0]["invocations"]["producer"]["argv"].remove("-I")


def _mutate_role9_invocation(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][1]["invocations"]["verifier"]["argv"].insert(1, "-I")


def _mutate_role8_partition(fixture: dict[str, Any]) -> None:
    fixture["plan"]["entries"][0]["partition_path_bindings"][0]["coordinate"] = "relative_parallel"


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (
            lambda fixture: fixture["plan"].__setitem__(
                "status", "RESULT_BLIND_REPLAY_WITH_UNFROZEN_SEMANTICS"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2].__setitem__("role", True),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["method_selection"].__setitem__(
                "contact_profile_parameter_id",
                "killing_contact_profile_mpfr_192_uncommitted",
            ),
            producer.HOLD_METHOD,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["implementation_runtime_closure"][
                "runtime_requirements"
            ].__setitem__("python_abi", "CPython 0.0"),
            producer.HOLD_RUNTIME,
        ),
        (_mutate_design_authority, producer.HOLD_AUTHORITY),
        (_mutate_partition_identity, producer.HOLD_PARTITION),
        (_mutate_role8_external_closure, producer.HOLD_RUNTIME),
        (_mutate_role9_inline_closure, producer.HOLD_REQUEST),
        (_mutate_role8_method_order, producer.HOLD_METHOD),
        (_mutate_role9_method_identifier, producer.HOLD_METHOD),
        (_mutate_role8_request_schema, producer.HOLD_REQUEST),
        (_mutate_role9_authority, producer.HOLD_AUTHORITY),
        (_mutate_role8_invocation, producer.HOLD_REQUEST),
        (_mutate_role9_invocation, producer.HOLD_REQUEST),
        (_mutate_role8_partition, producer.HOLD_PARTITION),
    ],
)
def test_coherently_repinned_semantic_mutations_hit_named_gates(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
    expected: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    mutator(fixture)
    refresh_chain(fixture)
    assert_producer_hold(fixture, expected)


@pytest.mark.parametrize(
    ("target_kind", "expected_detail"),
    (
        ("reference_density", "planned output aliases a replay dependency"),
        ("runtime_source", "planned output aliases a replay dependency"),
        ("partition", "planned output aliases a replay dependency"),
        ("plan", "planned output aliases a protocol input"),
        ("bundle", "planned output aliases a protocol input"),
        ("commitment", "planned output aliases a protocol input"),
        ("request", "roles 8--10 replay slots collide"),
    ),
)
def test_peer_output_cannot_alias_any_replay_input_after_coherent_repin(
    tmp_path: Path,
    target_kind: str,
    expected_detail: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    first_partition = Path(fixture["plan"]["entries"][0]["partition_path_bindings"][0]["path"])
    targets = {
        "reference_density": fixture["paths"]["reference_density"],
        "runtime_source": fixture["role_sources"][8]["producer"],
        "partition": first_partition,
        "plan": fixture["plan_path"],
        "bundle": fixture["bundle_path"],
        "commitment": fixture["commitment_path"],
        "request": fixture["request_path"],
    }
    alias_planned_output(
        fixture,
        entry_index=0,
        output_role="artifact",
        target=targets[target_kind],
    )
    assert_producer_hold(fixture, producer.HOLD_REQUEST, expected_detail)
    assert_verifier_hold(fixture, verifier.HOLD_REQUEST, expected_detail)


@pytest.mark.parametrize(
    ("entry_index", "output_role"),
    (
        (0, "artifact"),
        (0, "validation_receipt"),
        (1, "artifact"),
        (1, "validation_receipt"),
    ),
)
def test_preexisting_peer_output_is_rejected_and_preserved(
    tmp_path: Path,
    entry_index: int,
    output_role: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    output = fixture["plan"]["entries"][entry_index]["outputs"][output_role]
    path = Path(output["path"])
    payload = base.immutable_write(path, {"foreign": "peer-output"})
    assert_producer_hold(
        fixture,
        producer.HOLD_REQUEST,
        "planned output slot is not fresh",
    )
    assert path.read_bytes() == payload
    assert_verifier_hold(
        fixture,
        verifier.HOLD_REQUEST,
        "planned output slot is not fresh",
    )
    assert path.read_bytes() == payload


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
def test_commitment_future_result_evidence_is_rejected_after_coherent_repin(
    tmp_path: Path,
    container: str,
    field: str,
    value: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["commitment"][container][field] = value
    refresh_chain(fixture)
    assert_producer_hold(
        fixture,
        producer.HOLD_REQUEST,
        "future-result evidence value forbidden",
    )
    assert_verifier_hold(
        fixture,
        verifier.HOLD_REQUEST,
        "future-result evidence value forbidden",
    )


def test_result_leakage_key_is_rejected_by_protocol_parser(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["plan"]["entries"][2]["method_selection"]["expected_result_sha256"] = "0" * 64
    refresh_chain(fixture)
    assert_producer_hold(fixture, producer.HOLD_REQUEST)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda fixture: fixture["plan"]["entries"][0]["invocations"]["producer"]["argv"].append(
            "--result-digest=0" + "0" * 63
        ),
        lambda fixture: fixture["plan"]["entries"][1]["invocations"]["verifier"].__setitem__(
            "cwd",
            str(fixture["root"] / "result-digest"),
        ),
        lambda fixture: fixture["plan"]["entries"][2]["method_selection"].__setitem__(
            "verifier_parameter_id",
            "killing-source/result digest/derived",
        ),
    ],
)
def test_result_digest_in_nested_argv_cwd_or_value_is_rejected_before_semantics(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    fixture = base.make_fixture(tmp_path)
    mutator(fixture)
    refresh_chain(fixture)
    with pytest.raises(producer.CandidateKillingFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert captured.value.code == producer.HOLD_REQUEST
    assert "result leakage string value forbidden" in captured.value.detail
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()


def test_symlinked_ancestor_of_nonselected_role8_closure_is_rejected(
    tmp_path: Path,
) -> None:
    fixture = base.make_fixture(tmp_path)
    alias = tmp_path / "linked-report-root"
    alias.symlink_to(fixture["root"], target_is_directory=True)
    fixture["plan"]["entries"][0]["implementation_runtime_closure"]["path"] = str(
        alias / fixture["role8_runtime_closure_path"].name
    )
    refresh_chain(fixture)
    with pytest.raises(producer.CandidateKillingFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert captured.value.code == producer.HOLD_RUNTIME
    assert "symlinked or unavailable ancestor directory" in captured.value.detail
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()


def test_structural_authentication_cannot_be_promoted(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["commitment"]["claim_boundary"]["cryptographic_authenticity_verified_locally"] = True
    refresh_chain(fixture)
    assert_producer_hold(fixture, producer.HOLD_REQUEST)


def test_non_structural_commitment_is_rejected(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["commitment"]["authentication"]["structural_validation_only"] = False
    refresh_chain(fixture)
    assert_producer_hold(fixture, producer.HOLD_REQUEST)


def test_verifier_uses_the_same_runtime_gate_without_reading_an_artifact(
    tmp_path: Path,
) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["plan"]["entries"][2]["implementation_runtime_closure"]["runtime_requirements"][
        "mpfr"
    ] = "synthetic-mismatch"
    refresh_chain(fixture)
    with pytest.raises(verifier.CandidateKillingVerificationFailure) as captured:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_RUNTIME
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()
