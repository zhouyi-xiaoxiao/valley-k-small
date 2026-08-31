"""Hostile mutation tests for the committed role-9 v2 protocol."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Callable

import pytest
import test_continuum_c1_n0_candidate_native_stationary_integrals_v2 as base

producer = base.producer
verifier = base.verifier


def refresh_chain(fixture: dict[str, Any]) -> None:
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
    projection = {
        "authority": commitment["authority"],
        "candidate_bundle": commitment["candidate_bundle"],
        "claim_boundary": commitment["claim_boundary"],
        "ordering": commitment["ordering"],
    }
    commitment["commitment_message_sha256"] = base.digest(
        producer.COMMITMENT_MESSAGE_DOMAIN, projection
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


def refresh_request_for_current_commitment(fixture: dict[str, Any]) -> None:
    request = fixture["request"]
    request["external_predecessor_commitment"] = base.pin(fixture["commitment_path"])
    request["shared_replay_context_sha256"] = base.digest(
        producer.REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": base.sha256(
                fixture["commitment_path"].read_bytes()
            ),
            "replay_plan_sha256": base.sha256(fixture["plan_path"].read_bytes()),
            "shared_precommit_context_sha256": request["shared_precommit_context_sha256"],
        },
    )
    base.replace_immutable(fixture["request_path"], request)


def assert_producer_hold(fixture: dict[str, Any]) -> str:
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert not os.path.lexists(fixture["artifact_path"])
    return captured.value.code


def repin_role8_runtime_closure(fixture: dict[str, Any], closure: dict[str, Any]) -> None:
    base.replace_immutable(fixture["role8_runtime_closure_path"], closure)
    fixture["plan"]["entries"][0]["implementation_runtime_closure"] = {
        **base.pin(fixture["role8_runtime_closure_path"]),
        "schema": producer.ROLE8_RUNTIME_CLOSURE_SCHEMA,
    }
    refresh_chain(fixture)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda closure: closure["claim_boundary"].__setitem__(
            "result_artifact_dependency_present", True
        ),
        lambda closure: closure["native_runtime"].__setitem__("python_abi", "CPython 0.0"),
        lambda closure: closure["python_imports"]["producer"].append("legacy_stationary_backend"),
        lambda closure: closure["native_libraries"].reverse(),
        lambda closure: closure["report_local_dependencies"].append(
            closure["code_inputs"]["producer"]
        ),
        lambda closure: closure["code_inputs"].__setitem__(
            "producer", dict(closure["code_inputs"]["verifier"])
        ),
    ],
)
def test_deep_role8_runtime_closure_mutations_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    fixture = base.make_fixture(tmp_path)
    closure = json.loads(fixture["role8_runtime_closure_path"].read_text(encoding="ascii"))
    mutator(closure)
    repin_role8_runtime_closure(fixture, closure)
    assert assert_producer_hold(fixture) == producer.HOLD_RUNTIME


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (
            lambda fixture: fixture["plan"].__setitem__(
                "status", "RESULT_BLIND_ROLES_8_10_REPLAY_PLAN_NO_EXECUTION_RESULTS"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][1].__setitem__("role", True),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][1]["method_selection"].__setitem__(
                "expected_result_sha256", "0" * 64
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][1]["invocations"]["producer"]["argv"].append(
                "--unplanned"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][1]["implementation_runtime_closure"][
                "runtime_requirements"
            ].__setitem__("python_abi", "CPython 0.0"),
            producer.HOLD_RUNTIME,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][1]["partition_path_bindings"][0].__setitem__(
                "coordinate", "relative_parallel"
            ),
            producer.HOLD_REQUEST,
        ),
    ],
)
def test_coherently_repinned_plan_mutations_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
    expected_code: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    mutator(fixture)
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == expected_code


@pytest.mark.parametrize(
    "mutator",
    [
        lambda fixture: fixture["plan"]["entries"][0]["invocations"]["producer"]["argv"].append(
            f"role8_result_digest={'0' * 64}"
        ),
        lambda fixture: fixture["plan"]["entries"][2]["invocations"]["verifier"].__setitem__(
            "cwd",
            str(fixture["root"] / "role10_result_digest_marker"),
        ),
        lambda fixture: fixture["plan"]["entries"][2]["method_selection"].__setitem__(
            "contact_profile_parameter_id",
            "role10_result_digest_marker",
        ),
    ],
    ids=["role8-argv", "role10-cwd", "role10-value"],
)
def test_nested_string_leakage_fails_closed_on_both_sides(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    fixture = base.make_fixture(tmp_path)
    mutator(fixture)
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST
    base.immutable_write(fixture["artifact_path"], b'{"synthetic":true}\n')
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier._load_request(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_REQUEST
    assert not os.path.lexists(fixture["receipt_path"])


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (
            lambda fixture: fixture["plan"]["entries"][0]["request"].__setitem__(
                "schema", "synthetic_role8_request"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["outputs"]["artifact"].__setitem__(
                "schema", "synthetic_role10_artifact"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][0]["input_authorities"].pop(
                "reference_density"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["method_selection"].__setitem__(
                "contact_profile_parameter_id", "synthetic_uncommitted_method"
            ),
            producer.HOLD_METHOD,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][0]["partition_path_bindings"].reverse(),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["invocations"]["producer"]["argv"].append(
                "--unplanned"
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["implementation_runtime_closure"][
                "producer"
            ].__setitem__("sha256", "0" * 64),
            producer.HOLD_INPUT,
        ),
        (
            lambda fixture: fixture["plan"]["entries"][2]["outputs"]["artifact"].__setitem__(
                "path", fixture["plan"]["entries"][0]["outputs"]["artifact"]["path"]
            ),
            producer.HOLD_REQUEST,
        ),
        (
            lambda fixture: fixture["plan"]["shared_context"]["member_spec"].__setitem__(
                "path", fixture["paths"]["member_spec"].as_posix()
            ),
            producer.HOLD_REQUEST,
        ),
    ],
)
def test_nonselected_role_plan_mutations_fail_closed(
    tmp_path: Path,
    mutator: Callable[[dict[str, Any]], None],
    expected_code: str,
) -> None:
    fixture = base.make_fixture(tmp_path)
    mutator(fixture)
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == expected_code


def _repoint_artifact(entry: dict[str, Any], target: Path) -> None:
    entry["outputs"]["artifact"]["path"] = str(target)
    for invocation_role in ("producer", "verifier"):
        argv = entry["invocations"][invocation_role]["argv"]
        argv[argv.index("--output") + 1] = str(target)


def test_coherently_repinned_peer_artifact_to_reference_density_is_rejected(
    tmp_path: Path,
) -> None:
    fixture = base.make_fixture(tmp_path)
    _repoint_artifact(
        fixture["plan"]["entries"][2],
        fixture["paths"]["reference_density"],
    )
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST
    assert fixture["paths"]["reference_density"].exists()


def test_preexisting_peer_output_slot_is_rejected(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    peer_artifact = Path(fixture["plan"]["entries"][0]["outputs"]["artifact"]["path"])
    base.immutable_write(peer_artifact, b'{"occupied":true}\n')
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST


def test_verifier_rejects_nonselected_role10_method_mutation(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["plan"]["entries"][2]["method_selection"]["contact_profile_parameter_id"] = (
        "synthetic_uncommitted_method"
    )
    refresh_chain(fixture)
    base.immutable_write(fixture["artifact_path"], b'{"synthetic":true}\n')
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier._load_request(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_METHOD
    assert not os.path.lexists(fixture["receipt_path"])


def test_coherently_repinned_permissive_policy_is_rejected(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    policy_path = fixture["paths"]["anti_vacuity_policy"]
    policy = {
        "claim_boundary": {"release_eligible": True},
        "schema": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate",
        "status": "SYNTHETIC_PERMISSIVE_POLICY_MUST_BE_REJECTED",
    }
    base.replace_immutable(policy_path, policy)
    contextual = {
        "path": policy_path.relative_to(fixture["root"]).as_posix(),
        "schema": policy["schema"],
        "sha256": base.sha256(policy_path.read_bytes()),
    }
    fixture["plan"]["shared_context"]["anti_vacuity_policy"] = contextual
    fixture["plan"]["entries"][1]["input_authorities"]["anti_vacuity_policy"] = base.pin(
        policy_path
    )
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST


def test_coherently_recommitted_bundle_member_link_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["bundle"]["member_spec"]["sha256"] = "4" * 64
    base.replace_immutable(fixture["bundle_path"], fixture["bundle"])
    commitment = fixture["commitment"]
    commitment["candidate_bundle"] = base.pin(fixture["bundle_path"])
    commitment["commitment_message_sha256"] = base.digest(
        producer.COMMITMENT_MESSAGE_DOMAIN,
        {
            "authority": commitment["authority"],
            "candidate_bundle": commitment["candidate_bundle"],
            "claim_boundary": commitment["claim_boundary"],
            "ordering": commitment["ordering"],
        },
    )
    base.replace_immutable(fixture["commitment_path"], commitment)
    refresh_request_for_current_commitment(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST


def test_commitment_claimed_cryptographic_validation_is_rejected(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["commitment"]["claim_boundary"]["cryptographic_authenticity_verified_locally"] = True
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST


def test_commitment_non_structural_authentication_is_rejected(tmp_path: Path) -> None:
    fixture = base.make_fixture(tmp_path)
    fixture["commitment"]["authentication"]["structural_validation_only"] = False
    refresh_chain(fixture)
    assert assert_producer_hold(fixture) == producer.HOLD_REQUEST


def _published_fixture(tmp_path: Path) -> dict[str, Any]:
    fixture = base.make_fixture(tmp_path)
    payload = producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    producer._publish(fixture["artifact_path"], payload)
    return fixture


@pytest.mark.parametrize(
    "mutator",
    [
        lambda artifact: artifact["partition_closure"]["nodes"].reverse(),
        lambda artifact: artifact["partition_closure"].__setitem__("sha256", "0" * 64),
        lambda artifact: artifact["axis_stream"].__setitem__("sha256", "1" * 64),
        lambda artifact: artifact["axis_stream"].__setitem__(
            "record_count", artifact["axis_stream"]["record_count"] - 1
        ),
        lambda artifact: artifact["rows"].reverse(),
    ],
)
def test_dag_stream_and_row_order_mutations_are_rejected(
    tmp_path: Path, mutator: Callable[[dict[str, Any]], None]
) -> None:
    fixture = _published_fixture(tmp_path)
    artifact = copy.deepcopy(__import__("json").loads(fixture["artifact_path"].read_text("ascii")))
    mutator(artifact)
    base.replace_immutable(fixture["artifact_path"], artifact)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_ARTIFACT
    assert not os.path.lexists(fixture["receipt_path"])


def test_producer_link_failure_leaves_no_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = base.make_fixture(tmp_path)

    def fail_link(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise OSError("synthetic no-replace link failure")

    monkeypatch.setattr(producer.os, "link", fail_link)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer._publish(fixture["artifact_path"], b'{"complete":true}\n')
    assert captured.value.code == producer.HOLD_OUTPUT
    assert not os.path.lexists(fixture["artifact_path"])
    assert not list(fixture["artifact_path"].parent.glob(".*.stage"))


def test_receipt_link_failure_leaves_no_partial_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = base.make_fixture(tmp_path)

    def fail_link(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise OSError("synthetic receipt link failure")

    monkeypatch.setattr(verifier.os, "link", fail_link)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier._exclusive_publish_receipt(fixture["receipt_path"], b'{"complete":true}\n')
    assert captured.value.code == verifier.HOLD_RECEIPT
    assert not os.path.lexists(fixture["receipt_path"])
    assert not list(fixture["receipt_path"].parent.glob(".*.stage"))


def test_receipt_parent_replacement_is_detected_and_old_parent_cleaned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = base.make_fixture(tmp_path)
    parent = fixture["receipt_path"].parent
    displaced = parent.with_name(f"{parent.name}-displaced")
    real_link = verifier.os.link
    replaced = False

    def replace_parent_after_link(*args: Any, **kwargs: Any) -> None:
        nonlocal replaced
        real_link(*args, **kwargs)
        parent.rename(displaced)
        parent.mkdir(mode=0o700)
        replaced = True

    monkeypatch.setattr(verifier.os, "link", replace_parent_after_link)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier._exclusive_publish_receipt(fixture["receipt_path"], b'{"complete":true}\n')
    assert captured.value.code == verifier.HOLD_RECEIPT
    assert replaced
    assert not os.path.lexists(fixture["receipt_path"])
    assert not os.path.lexists(displaced / fixture["receipt_path"].name)
    assert not list(displaced.glob(".*.stage"))


@pytest.mark.parametrize(
    "target_role",
    [
        "artifact",
        "request",
        "partition",
        "peer_source",
        "peer_runtime_closure",
        "peer_authority",
    ],
)
def test_publication_window_path_swap_removes_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_role: str,
) -> None:
    fixture = _published_fixture(tmp_path)
    if target_role == "artifact":
        target = fixture["artifact_path"]
    elif target_role == "request":
        target = fixture["request_path"]
    elif target_role == "peer_source":
        target = fixture["peer_sources"][10][0]
    elif target_role == "peer_runtime_closure":
        target = fixture["role8_runtime_closure_path"]
    elif target_role == "peer_authority":
        target = fixture["peer_authority_path"]
    else:
        target = Path(fixture["plan"]["entries"][1]["partition_path_bindings"][0]["path"])
    original = target.read_bytes()
    displaced = target.with_name(f"{target.name}.displaced")
    real_link = verifier.os.link
    swapped = False

    def swap_validated_path_after_link(*args: Any, **kwargs: Any) -> None:
        nonlocal swapped
        real_link(*args, **kwargs)
        target.rename(displaced)
        base.immutable_write(target, original)
        swapped = True

    monkeypatch.setattr(verifier.os, "link", swap_validated_path_after_link)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_IMMUTABLE
    assert swapped
    assert not os.path.lexists(fixture["receipt_path"])
    assert not list(fixture["receipt_path"].parent.glob(".*.stage"))


@pytest.mark.parametrize(
    "target_role",
    ["peer_source", "peer_runtime_closure", "peer_authority"],
)
def test_peer_dependency_swap_before_receipt_link_fails_closed_and_cleans_up(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_role: str,
) -> None:
    fixture = _published_fixture(tmp_path)
    if target_role == "peer_source":
        target = fixture["peer_sources"][8][1]
    elif target_role == "peer_runtime_closure":
        target = fixture["role8_runtime_closure_path"]
    else:
        target = fixture["peer_authority_path"]
    original = target.read_bytes()
    displaced = target.with_name(f"{target.name}.displaced")
    real_link = verifier.os.link
    swapped = False

    def swap_peer_dependency_before_link(*args: Any, **kwargs: Any) -> None:
        nonlocal swapped
        target.rename(displaced)
        base.immutable_write(target, original)
        swapped = True
        real_link(*args, **kwargs)

    monkeypatch.setattr(verifier.os, "link", swap_peer_dependency_before_link)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured.value.code == verifier.HOLD_IMMUTABLE
    assert swapped
    assert not os.path.lexists(fixture["receipt_path"])
    assert not list(fixture["receipt_path"].parent.glob(".*.stage"))


def test_hardlinked_immutable_image_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    alias = tmp_path / "alias.json"
    base.immutable_write(source, b'{"complete":true}\n')
    os.link(source, alias)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier._immutable_image(source)
    assert captured.value.code == verifier.HOLD_IMMUTABLE
