"""Attack-specific mutations for candidate-native stationary integrals."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

import pytest
from test_continuum_c1_n0_candidate_native_stationary_integrals_v1 import (
    PRODUCER_PATH,
    VERIFIER_PATH,
    canonical,
    file_pin,
    immutable_write,
    make_fixture,
    producer,
    rebuild_member_digests,
    replace_immutable,
    sha256,
    verifier,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("ascii"))
    assert type(value) is dict
    return value


def rewrite_request(fixture: dict[str, Any], request: dict[str, Any]) -> None:
    replace_immutable(fixture["request_path"], request)
    fixture["request"] = request


def repin_authority(
    fixture: dict[str, Any], role: str, path: Path, value: dict[str, Any]
) -> dict[str, Any]:
    replace_immutable(path, value)
    request = load(fixture["request_path"])
    request["input_authorities"][role] = file_pin(path)
    rewrite_request(fixture, request)
    return request


def redigest_and_repin_member(fixture: dict[str, Any], member: dict[str, Any]) -> None:
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    repin_authority(fixture, "member_spec", fixture["member_path"], member)


def repin_configuration_family(fixture: dict[str, Any], configuration: dict[str, Any]) -> None:
    configuration_path = fixture["paths"]["configuration"]
    replace_immutable(configuration_path, configuration)
    configuration_hash = sha256(configuration_path.read_bytes())

    reference_path = fixture["paths"]["reference_density"]
    reference = load(reference_path)
    reference["source_pins"]["configuration_source"]["sha256"] = configuration_hash
    replace_immutable(reference_path, reference)

    member_path = fixture["member_path"]
    member = load(member_path)
    member["role_bindings"]["configuration_source"]["sha256"] = configuration_hash
    member["role_bindings"]["reference_density_source"]["sha256"] = sha256(
        reference_path.read_bytes()
    )
    member["_test_reference_parameters"] = reference["physical_parameter_bundle"]
    rebuild_member_digests(member, configuration)
    replace_immutable(member_path, member)

    request = load(fixture["request_path"])
    for role, path in (
        ("configuration", configuration_path),
        ("reference_density", reference_path),
        ("member_spec", member_path),
    ):
        request["input_authorities"][role] = file_pin(path)
    rewrite_request(fixture, request)
    fixture["objects"]["configuration"] = configuration
    fixture["objects"]["reference"] = reference


def assert_all_inputs_immutable(fixture: dict[str, Any]) -> None:
    paths = [
        fixture["request_path"],
        *fixture["paths"].values(),
        *fixture["partition_paths"].values(),
        PRODUCER_PATH,
        VERIFIER_PATH,
    ]
    for path in paths:
        metadata = os.lstat(path)
        assert stat.S_ISREG(metadata.st_mode)
        assert metadata.st_nlink == 1
        assert metadata.st_mode & 0o222 == 0


def test_oversized_binary64_hex_uses_the_stable_input_hold() -> None:
    oversized = "0x1.0p+999999999999999999999999"
    with pytest.raises(producer.CandidateStationaryFailure) as producer_overflow:
        producer._binary64_fraction(oversized, label="test binary64")
    with pytest.raises(producer.CandidateStationaryFailure) as producer_value:
        producer._binary64_fraction("not-a-hex-float", label="test binary64")
    assert producer_overflow.value.code == producer.HOLD_INPUT
    assert str(producer_overflow.value) == str(producer_value.value)

    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_overflow:
        verifier._hex_q(oversized, "test binary64")
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_value:
        verifier._hex_q("not-a-hex-float", "test binary64")
    assert verifier_overflow.value.code == verifier.HOLD_INPUT
    assert str(verifier_overflow.value) == str(verifier_value.value)


def test_deep_json_is_a_stable_hold_through_both_cli_interfaces(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    request_path = tmp_path / "deep-request.json"
    output_path = tmp_path / "absent-output.json"
    raw = b'{"deep":' + b"[" * 10_000 + b"0" + b"]" * 10_000 + b"}\n"
    immutable_write(request_path, raw)

    assert producer.main(["--request", str(request_path), "--output", str(output_path)]) == 2
    producer_capture = capsys.readouterr()
    assert producer_capture.out == ""
    assert producer_capture.err.startswith(f"{producer.HOLD_INPUT}: request: invalid ASCII JSON")
    assert "Traceback" not in producer_capture.err

    assert verifier.main(["--request", str(request_path), "--output", str(output_path)]) == 2
    verifier_capture = capsys.readouterr()
    assert verifier_capture.out == ""
    assert verifier_capture.err.startswith(f"{verifier.HOLD_INPUT}: request: invalid ASCII JSON")
    assert "Traceback" not in verifier_capture.err


@pytest.mark.parametrize(
    "role",
    [
        "configuration_design",
        "configuration_implementation",
        "configuration_test",
        "configuration_initial_geometry",
        "factorization_initial_partition_bundle",
        "factorization_killing_geometry",
    ],
)
def test_correct_looking_nested_pin_requires_an_existing_authenticated_file(
    tmp_path: Path,
    role: str,
) -> None:
    fixture = make_fixture(tmp_path)
    nested_path = fixture["paths"][role]
    nested_path.chmod(0o600)
    nested_path.unlink()

    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_IMMUTABLE

    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_IMMUTABLE


@pytest.mark.parametrize("implementation", ["producer", "verifier"])
def test_post_read_parent_component_replacement_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    implementation: str,
) -> None:
    fixture = make_fixture(tmp_path)
    original_root = fixture["root"]
    displaced_root = original_root.with_name(f"{original_root.name}-displaced")
    module = producer if implementation == "producer" else verifier
    real_read = module.os.read
    replaced = False

    def replace_parent_after_read(descriptor: int, size: int) -> bytes:
        nonlocal replaced
        raw = real_read(descriptor, size)
        if not replaced:
            original_root.rename(displaced_root)
            original_root.mkdir(mode=0o700)
            replaced = True
        return raw

    monkeypatch.setattr(module.os, "read", replace_parent_after_read)
    if implementation == "producer":
        with pytest.raises(producer.CandidateStationaryFailure) as captured:
            producer.build_from_request(fixture["request_path"], fixture["output_path"])
        assert captured.value.code == producer.HOLD_IMMUTABLE
    else:
        with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
            verifier.validate(fixture["request_path"], fixture["output_path"])
        assert captured.value.code == verifier.HOLD_IMMUTABLE
    assert replaced


def test_bool_integer_alias_is_an_input_schema_hold(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    configuration_path = fixture["paths"]["configuration"]
    configuration = load(configuration_path)
    configuration["configurations"][0]["midpoint"]["size"] = True
    repin_configuration_family(fixture, configuration)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "configuration axis size mismatch" in str(captured.value)


def test_partition_geometry_mutation_reaches_exact_reconstruction_gate(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    coordinate = "midpoint"
    partition_path = fixture["partition_paths"][(0, coordinate)]
    partition = load(partition_path)
    partition["cell_segments_exact"][0][0][1] = "-1/4"
    partition["cell_volumes_exact"][0] = "3/4"
    replace_immutable(partition_path, partition)

    request = load(fixture["request_path"])
    new_hash = sha256(partition_path.read_bytes())
    partition_pin = next(pin for pin in request["partitions"] if pin["coordinate"] == coordinate)
    partition_pin["sha256"] = new_hash

    member_path = fixture["member_path"]
    member = load(member_path)
    member["n0_sequence_bindings"][0]["n0_axes"][0]["partition_sha256"] = new_hash
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    replace_immutable(member_path, member)
    request["input_authorities"]["member_spec"] = file_pin(member_path)
    rewrite_request(fixture, request)

    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "partition geometry mismatch at 0:midpoint" in str(captured.value)


def test_invalid_sentinel_precision_is_a_method_hold(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    method_path = fixture["method_path"]
    registry = load(method_path)
    sentinel = next(
        entry
        for entry in registry["parameters"]
        if entry["parameter_id"] == producer.SENTINEL_PARAMETER_ID
    )
    sentinel["parameters"]["precision_bits"] = 64
    sentinel["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, sentinel["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(captured.value)


def test_coherently_rehashed_raw_precision_seven_is_rejected_by_both_implementations(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    method_path = fixture["method_path"]
    registry = load(method_path)
    raw_primary = next(
        entry
        for entry in registry["parameters"]
        if entry["parameter_id"] == "raw_flux_directed_mpfr_320_v2"
    )
    raw_primary["parameters"]["precision_bits"] = 7
    raw_primary["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, raw_primary["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(producer_error.value)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_METHOD
    assert "parameter record mismatch" in str(verifier_error.value)


def test_selected_boolean_records_reject_integer_aliases(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path / "dense")
    method_path = fixture["method_path"]
    registry = load(method_path)
    primary = next(
        entry
        for entry in registry["parameters"]
        if entry["parameter_id"] == producer.PRIMARY_PARAMETER_ID
    )
    primary["parameters"]["dense_tensor_materialized"] = 0
    primary["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, primary["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(captured.value)

    fixture = make_fixture(tmp_path / "independent")
    method_path = fixture["method_path"]
    registry = load(method_path)
    sentinel = next(
        entry
        for entry in registry["parameters"]
        if entry["parameter_id"] == producer.SENTINEL_PARAMETER_ID
    )
    sentinel["parameters"]["independent_backend"] = 0
    sentinel["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, sentinel["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(captured.value)


def test_v3_registry_boundary_and_top_level_are_exact(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    method_path = fixture["method_path"]
    registry = load(method_path)
    registry["claim_boundary"]["science_executed"] = True
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "boundary" in str(captured.value)

    fixture = make_fixture(tmp_path / "extra")
    method_path = fixture["method_path"]
    registry = load(method_path)
    registry["unexpected"] = False
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "exact-key" in str(captured.value)


def test_v3_registry_rejects_observed_or_result_keys_recursively(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    method_path = fixture["method_path"]
    registry = load(method_path)
    entry = registry["parameters"][-1]
    entry["parameters"]["nested"] = {"observed_output_sha256": "0" * 64}
    entry["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, entry["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD


def test_member_authority_rejects_observed_or_result_keys_recursively(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    member_path = fixture["member_path"]
    member = load(member_path)
    member["source_lineage_evidence"]["observed_role9_value"] = "forbidden"
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "result/observed metadata key" in str(captured.value)


def test_full_registry_order_and_candidate_native_scopes_are_bound(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path / "order")
    method_path = fixture["method_path"]
    registry = load(method_path)
    registry["parameters"][0], registry["parameters"][1] = (
        registry["parameters"][1],
        registry["parameters"][0],
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "cardinality" in str(captured.value)

    fixture = make_fixture(tmp_path / "scope")
    method_path = fixture["method_path"]
    registry = load(method_path)
    entry = registry["parameters"][-1]
    entry["parameters"]["source_role_scope"] = ["legacy_role10"]
    entry["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, entry["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(captured.value)


def test_generic_containment_and_selected_identity_are_exact(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    method_path = fixture["method_path"]
    registry = load(method_path)
    sentinel = next(
        entry
        for entry in registry["parameters"]
        if entry["parameter_id"] == producer.SENTINEL_PARAMETER_ID
    )
    sentinel["parameters"]["containment_relation"] = "primary_320_interval_contains_640_sentinel"
    sentinel["method_parameter_sha256"] = producer._domain_digest(
        producer.PARAMETER_DIGEST_DOMAIN, sentinel["parameters"]
    )
    repin_authority(fixture, "method_parameters", method_path, registry)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "parameter record mismatch" in str(captured.value)

    fixture = make_fixture(tmp_path / "identity")
    request = load(fixture["request_path"])
    request["method_selection"]["primary_parameter_id"] = "raw_flux_directed_mpfr_320_v2"
    rewrite_request(fixture, request)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_METHOD
    assert "identity" in str(captured.value)


def test_member_role_binding_must_match_request_pin(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    member_path = fixture["member_path"]
    member = load(member_path)
    member["role_bindings"]["ideal_formula_source"]["sha256"] = "b" * 64
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "request binding mismatch" in str(captured.value)


def test_member_status_and_all_false_claims_are_bound(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path / "status")
    member_path = fixture["member_path"]
    member = load(member_path)
    member["status"] = "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY"
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as status_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert status_error.value.code == producer.HOLD_MEMBER
    assert "candidate member boundary mismatch" in str(status_error.value)

    fixture = make_fixture(tmp_path / "claim")
    member_path = fixture["member_path"]
    member = load(member_path)
    assert len(member["claim_boundary"]) == 18
    member["claim_boundary"]["science_executed"] = True
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as claim_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert claim_error.value.code == producer.HOLD_MEMBER
    assert "candidate member boundary mismatch" in str(claim_error.value)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_MEMBER
    assert "authority schema" in str(verifier_error.value)


def test_member_factorization_binding_is_request_pinned_and_not_self_authorizing(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    member_path = fixture["member_path"]
    member = load(member_path)
    member["role_bindings"]["factorization_source"] = {
        "path": "artifacts/data/continuum_c1_factorization_source_v1.json",
        "sha256": "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
    }
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "member factorization source: request binding mismatch" in str(captured.value)


def test_member_nested_binding_rejects_unexpected_expected_artifact_pin(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    member_path = fixture["member_path"]
    member = load(member_path)
    member["n0_sequence_bindings"][0]["n0_axes"][0]["expected_artifact_sha256"] = "0" * 64
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "member axis binding 0:midpoint: exact-key mismatch" in str(captured.value)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("refinement_family_id", True),
        ("refinement_family_id", ""),
        ("refinement_member_id", 0),
        ("refinement_member_id", ""),
    ],
)
def test_coherently_redigested_refinement_ids_require_nonempty_exact_strings(
    tmp_path: Path,
    field: str,
    replacement: Any,
) -> None:
    fixture = make_fixture(tmp_path)
    member = load(fixture["member_path"])
    member["configuration_semantic_ids"][0][field] = replacement
    binding = member["n0_sequence_bindings"][0]
    binding[field] = replacement
    for axis in binding["n0_axes"]:
        axis[field] = replacement
    redigest_and_repin_member(fixture, member)

    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_MEMBER
    assert "refinement identity type" in str(producer_error.value)

    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_MEMBER
    assert "refinement identity type" in str(verifier_error.value)


@pytest.mark.parametrize(("row_index", "alias"), [(0, False), (1, True)])
def test_coherently_redigested_sequence_indices_reject_bool_integer_aliases(
    tmp_path: Path,
    row_index: int,
    alias: bool,
) -> None:
    fixture = make_fixture(tmp_path)
    member = load(fixture["member_path"])
    binding = member["n0_sequence_bindings"][row_index]
    binding["configuration_index"] = alias
    binding["sequence_source_row_index"] = alias
    redigest_and_repin_member(fixture, member)

    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_MEMBER
    assert "row identity" in str(producer_error.value)

    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_MEMBER
    assert "row identity" in str(verifier_error.value)


def test_coherently_redigested_sequence_id_must_be_nonempty(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    member = load(fixture["member_path"])
    binding = member["n0_sequence_bindings"][0]
    binding["sequence_id"] = ""
    for axis in binding["n0_axes"]:
        axis["sequence_id"] = ""
    redigest_and_repin_member(fixture, member)

    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_MEMBER
    assert "sequence identity" in str(producer_error.value)

    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_MEMBER
    assert "row identity" in str(verifier_error.value)


def test_request_requires_standalone_factorization_authority(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    request = load(fixture["request_path"])
    del request["input_authorities"]["factorization"]
    rewrite_request(fixture, request)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_REQUEST
    assert "input authorities: exact-key mismatch" in str(captured.value)


def test_factorization_bytes_cannot_be_relabelled_as_another_source(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    factorization_path = fixture["paths"]["factorization"]
    renamed = fixture["root"] / "authorities/renamed_factorization.json"
    immutable_write(renamed, factorization_path.read_bytes())
    member_path = fixture["member_path"]
    member = load(member_path)
    member["role_bindings"]["factorization_source"] = {
        "path": "authorities/renamed_factorization.json",
        "sha256": producer.FACTORIZATION_SHA256,
    }
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    replace_immutable(member_path, member)
    request = load(fixture["request_path"])
    request["input_authorities"]["factorization"] = file_pin(renamed)
    request["input_authorities"]["member_spec"] = file_pin(member_path)
    rewrite_request(fixture, request)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "factorization authority mismatch" in str(captured.value)


def test_formula_reference_and_dynamics_fields_are_exact(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path / "formula")
    formula_path = fixture["paths"]["ideal_formula"]
    formula = load(formula_path)
    formula["potential_formulae"]["midpoint"] = "0/1"
    repin_authority(fixture, "ideal_formula", formula_path, formula)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "formula semantics" in str(captured.value)

    fixture = make_fixture(tmp_path / "reference")
    reference_path = fixture["paths"]["reference_density"]
    reference = load(reference_path)
    reference["normalization"]["periodic_factor"] = "1"
    repin_authority(fixture, "reference_density", reference_path, reference)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "reference semantics" in str(captured.value)

    fixture = make_fixture(tmp_path / "dynamics")
    configuration = load(fixture["paths"]["configuration"])
    configuration["dynamics"]["midpoint_potential_formula"] = "0/1"
    repin_configuration_family(fixture, configuration)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "factorization configuration source: request binding mismatch" in str(captured.value)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("expected_artifact_sha256", "0" * 64),
        ("control_values", []),
        ("control", None),
        ("budget", 0),
        ("outcome", "hidden"),
    ],
)
def test_configuration_rows_reject_unexpected_result_or_control_metadata(
    tmp_path: Path,
    key: str,
    value: Any,
) -> None:
    fixture = make_fixture(tmp_path)
    configuration = load(fixture["paths"]["configuration"])
    configuration["configurations"][0][key] = value
    repin_configuration_family(fixture, configuration)
    with pytest.raises(producer.CandidateStationaryFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert producer_error.value.code == producer.HOLD_INPUT
    assert "configuration row 0: exact-key mismatch" in str(producer_error.value)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as verifier_error:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert verifier_error.value.code == verifier.HOLD_INPUT
    assert "configuration row 0: exact-key mismatch" in str(verifier_error.value)


def test_shape_product_and_reconstruction_counts_are_enforced(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path / "shape")
    configuration = load(fixture["paths"]["configuration"])
    configuration["configurations"][0]["expected_states"] = 26
    configuration["total_state_workload"] = 26
    repin_configuration_family(fixture, configuration)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "configuration row shape mismatch" in str(captured.value)

    fixture = make_fixture(tmp_path / "counts")
    member_path = fixture["member_path"]
    member = load(member_path)
    member["reconstruction_counts"]["axis_edge_count"] = 8
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "reconstruction counts" in str(captured.value)

    fixture = make_fixture(tmp_path / "count_bool")
    member_path = fixture["member_path"]
    member = load(member_path)
    member["reconstruction_counts"]["configuration_count"] = True
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_MEMBER
    assert "reconstruction counts" in str(captured.value)


def test_verifier_mirrors_correlated_member_flag(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    member_path = fixture["member_path"]
    member = load(member_path)
    member["member_semantics"]["one_formula_defined_correlated_member_per_configuration"] = False
    member["_test_reference_parameters"] = fixture["objects"]["reference"][
        "physical_parameter_bundle"
    ]
    rebuild_member_digests(member, fixture["objects"]["configuration"])
    repin_authority(fixture, "member_spec", member_path, member)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == verifier.HOLD_MEMBER
    assert "member cardinality" in str(captured.value)


def test_result_digest_key_is_rejected_before_input_use(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    request = load(fixture["request_path"])
    request["input_authorities"]["member_spec"]["result_sha256"] = "0" * 64
    rewrite_request(fixture, request)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_REQUEST
    assert "result/observed pin" in str(captured.value)


def test_duplicate_request_key_is_not_masked_by_permissions(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    raw = fixture["request_path"].read_bytes()
    attacked = raw.replace(
        b'{\n  "code_inputs":',
        b'{\n  "schema": "duplicate",\n  "code_inputs":',
        1,
    )
    replace_immutable(fixture["request_path"], attacked)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "duplicate" in str(captured.value)


def test_json_float_is_rejected_after_valid_repin(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    configuration_path = fixture["paths"]["configuration"]
    raw = configuration_path.read_bytes().replace(b'"size": 113', b'"size": 113.0', 1)
    replace_immutable(configuration_path, raw)
    request = load(fixture["request_path"])
    request["input_authorities"]["configuration"] = file_pin(configuration_path)
    rewrite_request(fixture, request)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "float" in str(captured.value)


def test_non_nfc_authority_string_is_rejected_after_valid_repin(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    formula_path = fixture["paths"]["ideal_formula"]
    formula = load(formula_path)
    formula["synthetic_note"] = "e\u0301"
    replace_immutable(formula_path, canonical(formula))
    request = load(fixture["request_path"])
    request["input_authorities"]["ideal_formula"] = file_pin(formula_path)
    rewrite_request(fixture, request)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "non-NFC" in str(captured.value)


def test_hardlinked_input_is_rejected_specifically(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    formula_path = fixture["paths"]["ideal_formula"]
    alias = formula_path.with_name("formula-hardlink.json")
    os.link(formula_path, alias)
    assert formula_path.stat().st_nlink == 2
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_IMMUTABLE
    assert "single-link" in str(captured.value)


def test_complete_artifact_semantic_mutation_reaches_verifier_gate(
    tmp_path: Path,
) -> None:
    fixture = make_fixture(tmp_path)
    payload = producer.build_from_request(fixture["request_path"], fixture["output_path"])
    producer._publish(fixture["output_path"], payload)
    artifact = load(fixture["output_path"])
    artifact["rows"][0]["axes"][0]["M_x_pi_cell_intervals"][0]["lower_exact_p_over_q"] = "1/1000000"
    replace_immutable(fixture["output_path"], artifact)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured:
        verifier.validate(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == verifier.HOLD_ARTIFACT
    assert "complete artifact mismatch" in str(captured.value)


def test_code_source_pin_mutation_is_an_input_hash_hold(tmp_path: Path) -> None:
    fixture = make_fixture(tmp_path)
    request = load(fixture["request_path"])
    request["code_inputs"]["producer"]["sha256"] = "f" * 64
    rewrite_request(fixture, request)
    assert_all_inputs_immutable(fixture)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["output_path"])
    assert captured.value.code == producer.HOLD_INPUT
    assert "producer: SHA-256 mismatch" in str(captured.value)
