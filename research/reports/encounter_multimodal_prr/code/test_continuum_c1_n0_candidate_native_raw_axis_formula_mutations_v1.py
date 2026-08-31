from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest
from test_continuum_c1_n0_candidate_native_raw_axis_formula_v1 import (
    COORDINATES,
    NeutralFixture,
    create_neutral_fixture,
    domain_hash,
    replace_json,
    run_producer,
    run_verifier,
    sha256_file,
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def rewrite_request(fixture: NeutralFixture, mutate: Callable[[dict[str, Any]], None]) -> None:
    request = load(fixture.request)
    mutate(request)
    replace_json(fixture.request, request)


def refresh_member_identity(member: dict[str, Any]) -> None:
    identity = {
        "configuration_order": member["configuration_order"],
        "configuration_semantic_ids": member["configuration_semantic_ids"],
        "coordinate_order": list(COORDINATES),
        "n0_sequence_bindings": member["n0_sequence_bindings"],
        "role_bindings_1_through_4": member["role_bindings"],
        "scalar_convention": member["member_semantics"]["scalar_convention"],
    }
    member["member_identity_sha256"] = domain_hash(
        "encounter-continuum-c1-c2-n0-member-identity-v3", identity
    )


def refresh_member_request_pin(fixture: NeutralFixture) -> None:
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["member_spec"].update(
            {"sha256": sha256_file(fixture.authorities["member_spec"])}
        ),
    )


def refresh_configuration_closure(fixture: NeutralFixture) -> None:
    configuration_sha = sha256_file(fixture.authorities["configuration"])
    reference = load(fixture.authorities["reference_density"])
    reference["source_pins"]["configuration_source"]["sha256"] = configuration_sha
    replace_json(fixture.authorities["reference_density"], reference)
    factorization = load(fixture.authorities["factorization"])
    factorization["source_pins"]["configuration_source"]["sha256"] = configuration_sha
    replace_json(fixture.authorities["factorization"], factorization)
    member = load(fixture.authorities["member_spec"])
    member["role_bindings"]["configuration_source"]["sha256"] = configuration_sha
    member["role_bindings"]["reference_density_source"]["sha256"] = sha256_file(
        fixture.authorities["reference_density"]
    )
    member["role_bindings"]["factorization_source"]["sha256"] = sha256_file(
        fixture.authorities["factorization"]
    )
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        for role in (
            "configuration",
            "factorization",
            "member_spec",
            "reference_density",
        ):
            request["input_authorities"][role]["sha256"] = sha256_file(fixture.authorities[role])

    rewrite_request(fixture, update_request)


def refresh_factorization_binding(fixture: NeutralFixture) -> None:
    factorization_sha = sha256_file(fixture.authorities["factorization"])
    member = load(fixture.authorities["member_spec"])
    member["role_bindings"]["factorization_source"]["sha256"] = factorization_sha
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        request["input_authorities"]["factorization"]["sha256"] = factorization_sha
        request["input_authorities"]["member_spec"]["sha256"] = sha256_file(
            fixture.authorities["member_spec"]
        )

    rewrite_request(fixture, update_request)


def rewrite_output(fixture: NeutralFixture, mutate: Callable[[dict[str, Any]], None]) -> None:
    output = load(fixture.output)
    mutate(output)
    replace_json(fixture.output, output)


def assert_producer_hold(fixture: NeutralFixture, code: str, detail: str | None = None) -> None:
    result = run_producer(fixture)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert code in result.stderr
    if detail is not None:
        assert detail in result.stderr


def assert_verifier_hold(fixture: NeutralFixture, code: str, detail: str | None = None) -> None:
    result = run_verifier(fixture)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert code in result.stderr
    if detail is not None:
        assert detail in result.stderr


def test_rejects_noncanonical_request_bytes(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    fixture.request.chmod(0o600)
    fixture.request.write_bytes(fixture.request.read_bytes() + b" ")
    fixture.request.chmod(0o400)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "request: noncanonical JSON")


def test_rejects_duplicate_request_key(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    raw = fixture.request.read_text(encoding="ascii")
    duplicate = raw.replace(
        '  "status": "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT"',
        (
            '  "status": "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT",\n'
            '  "status": "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT"'
        ),
    )
    fixture.request.chmod(0o600)
    fixture.request.write_text(duplicate, encoding="ascii")
    fixture.request.chmod(0o400)
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "duplicate or invalid JSON key")


def test_rejects_observed_result_digest_hidden_in_method_selection(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    rewrite_request(
        fixture,
        lambda request: request["method_selection"].update({"observed_result_sha256": "0" * 64}),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "result/observed pin")


def test_rejects_role9_result_authority_even_when_hash_shaped(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"].update(
            {
                "role9_result": {
                    "path": str(fixture.authorities["reference_density"]),
                    "sha256": sha256_file(fixture.authorities["reference_density"]),
                }
            }
        ),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "result/observed pin")


def test_rejects_authority_sha_substitution(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["reference_density"].update(
            {"sha256": "f" * 64}
        ),
    )
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "reference_density: SHA-256 mismatch"
    )


def test_rejects_writable_authority(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    fixture.authorities["reference_density"].chmod(0o600)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT",
        "read-only, single-link regular",
    )


def test_rejects_hardlinked_authority(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    os.link(
        fixture.authorities["reference_density"],
        fixture.root / "reference-hardlink.json",
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT",
        "read-only, single-link regular",
    )


def test_rejects_symlink_authority(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    alias = fixture.root / "reference-symlink.json"
    alias.symlink_to(fixture.authorities["reference_density"])
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["reference_density"].update(
            {"path": str(alias)}
        ),
    )
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT", "symlink path component"
    )


def test_rejects_symlink_output_parent(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    real_parent = fixture.root / "real-output-parent"
    real_parent.mkdir(mode=0o700)
    alias_parent = fixture.root / "output-parent-alias"
    alias_parent.symlink_to(real_parent, target_is_directory=True)
    aliased_output = alias_parent / "output.json"
    fixture.output = aliased_output
    rewrite_request(
        fixture,
        lambda request: request["output"].update({"path": str(aliased_output)}),
    )
    assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_OUTPUT", "symlink path component")


def test_coherent_partition_hash_rewrite_reaches_geometry_gate(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    partition_index = 2
    partition = load(fixture.partitions[partition_index])
    partition["positions_exact"][0] = "-1/4"
    replace_json(fixture.partitions[partition_index], partition)
    new_partition_sha = sha256_file(fixture.partitions[partition_index])

    member = load(fixture.authorities["member_spec"])
    binding = member["n0_sequence_bindings"][0]
    binding["n0_axes"][2]["partition_sha256"] = new_partition_sha
    row = load(fixture.authorities["configuration"])["configurations"][0]
    binding["configuration_geometry_sha256"] = domain_hash(
        "encounter-configuration-geometry-v1",
        {
            "configuration_index": 0,
            "configuration_row": row,
            "n0_partition_sha256s": [axis["partition_sha256"] for axis in binding["n0_axes"]],
        },
    )
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        request["partitions"][partition_index]["sha256"] = new_partition_sha
        request["input_authorities"]["member_spec"]["sha256"] = sha256_file(
            fixture.authorities["member_spec"]
        )

    rewrite_request(fixture, update_request)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "partition geometry mismatch",
    )


def test_coherent_formula_and_member_rewrite_reaches_formula_gate(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    formula = load(fixture.authorities["ideal_formula"])
    formula["formulae"]["ideal_axis_mass"] = "mu_i=observed_production_mass"
    replace_json(fixture.authorities["ideal_formula"], formula)
    new_formula_sha = sha256_file(fixture.authorities["ideal_formula"])

    member = load(fixture.authorities["member_spec"])
    member["role_bindings"]["ideal_formula_source"]["sha256"] = new_formula_sha
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        request["input_authorities"]["ideal_formula"]["sha256"] = new_formula_sha
        request["input_authorities"]["member_spec"]["sha256"] = sha256_file(
            fixture.authorities["member_spec"]
        )

    rewrite_request(fixture, update_request)
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "formula nested semantics mismatch"
    )


def test_parameter_rehash_cannot_authorize_kappa_hull_rule(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    registry = load(fixture.authorities["method_parameters"])
    primary = registry["parameters"][2]
    primary["parameters"]["common_kappa_rule"] = "convex_hull_without_direct_witness"
    primary["method_parameter_sha256"] = domain_hash(
        "encounter-outward-method-parameters-v3", primary["parameters"]
    )
    replace_json(fixture.authorities["method_parameters"], registry)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["method_parameters"].update(
            {"sha256": sha256_file(fixture.authorities["method_parameters"])}
        ),
    )
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_METHOD", "raw-axis method semantics mismatch"
    )


def test_coherent_configuration_role_rewrite_cannot_change_physical_parameters(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    configuration = load(fixture.authorities["configuration"])
    configuration["dynamics"]["particle_diffusion_binary64_hex"] = float(0.5).hex()
    replace_json(fixture.authorities["configuration"], configuration)
    refresh_configuration_closure(fixture)
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_INPUT", "reference/configuration parameter mismatch"
    )


def test_rejects_partition_request_reordering(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)

    def swap(request: dict[str, Any]) -> None:
        request["partitions"][0], request["partitions"][1] = (
            request["partitions"][1],
            request["partitions"][0],
        )

    rewrite_request(fixture, swap)
    assert_producer_hold(
        fixture, "HOLD_CANDIDATE_RAW_AXIS_REQUEST", "invalid/unsorted partition pin"
    )


def test_verifier_rejects_common_kappa_hull_mutation(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr

    def mutate(output: dict[str, Any]) -> None:
        edge = output["rows"][0]["axes"][0]["edges"][0]
        edge["common_kappa_interval"] = edge["forward_product_kappa_interval"]

    rewrite_output(fixture, mutate)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )


def test_verifier_rejects_half_shift_seam_reorientation(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr

    def mutate(output: dict[str, Any]) -> None:
        edges = output["rows"][1]["axes"][2]["edges"]
        edges[2]["periodic_domain_cut_crossing"] = False
        edges[3]["periodic_domain_cut_crossing"] = True

    rewrite_output(fixture, mutate)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )


def test_verifier_rejects_nondegenerate_mu_collapse(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr

    def mutate(output: dict[str, Any]) -> None:
        interval = output["rows"][0]["axes"][0]["cells"][0]["raw_mu_interval"]
        interval["upper_exact_p_over_q"] = interval["lower_exact_p_over_q"]

    rewrite_output(fixture, mutate)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )


def test_verifier_rejects_injected_downstream_quantity(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr

    def mutate(output: dict[str, Any]) -> None:
        output["rows"][0]["rho"] = {
            "lower_exact_p_over_q": "1/1",
            "upper_exact_p_over_q": "1/1",
        }

    rewrite_output(fixture, mutate)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_OUTPUT",
        "independent reconstruction",
    )


def test_read_only_check_rejects_writable_output(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    fixture.output.chmod(0o600)
    checked = run_producer(fixture, check=True)
    assert checked.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT" in checked.stderr


def test_verifier_rejects_hardlinked_output(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    os.link(fixture.output, fixture.root / "output-hardlink.json")
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_IMMUTABLE_INPUT",
        "single-link file",
    )


def test_v3_registry_boundary_count_scope_and_sentinel_gates(tmp_path: Path) -> None:
    cases = ("schema", "claim", "count", "scope", "sentinel")
    for case in cases:
        fixture = create_neutral_fixture(tmp_path / case)
        registry = load(fixture.authorities["method_parameters"])
        if case == "schema":
            registry["schema"] = (
                "encounter_continuum_c1_c2_n0_method_parameter_registry_v2_candidate"
            )
            detail = "parameter registry boundary mismatch"
        elif case == "claim":
            registry["claim_boundary"]["science_executed"] = True
            detail = "parameter registry boundary mismatch"
        elif case == "count":
            registry["parameter_count"] = 9
            detail = "parameter registry cardinality/order mismatch"
        elif case == "scope":
            entry = registry["parameters"][2]
            entry["parameters"]["source_role_scope"] = ["role8_raw_axis_enclosure"]
            entry["method_parameter_sha256"] = domain_hash(
                "encounter-outward-method-parameters-v3", entry["parameters"]
            )
            detail = "parameter digest mismatch"
        else:
            entry = registry["parameters"][3]
            entry["parameters"]["containment_relation"] = (
                "primary_320_interval_contains_640_sentinel"
            )
            entry["method_parameter_sha256"] = domain_hash(
                "encounter-outward-method-parameters-v3", entry["parameters"]
            )
            detail = "parameter digest mismatch"
        replace_json(fixture.authorities["method_parameters"], registry)
        rewrite_request(
            fixture,
            lambda request: request["input_authorities"]["method_parameters"].update(
                {"sha256": sha256_file(fixture.authorities["method_parameters"])}
            ),
        )
        assert_producer_hold(fixture, "HOLD_CANDIDATE_RAW_AXIS_METHOD", detail)


def test_selected_parameter_boolean_type_is_exact(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    registry = load(fixture.authorities["method_parameters"])
    sentinel = registry["parameters"][3]
    sentinel["parameters"]["independent_backend"] = 0
    sentinel["method_parameter_sha256"] = domain_hash(
        "encounter-outward-method-parameters-v3", sentinel["parameters"]
    )
    replace_json(fixture.authorities["method_parameters"], registry)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["method_parameters"].update(
            {"sha256": sha256_file(fixture.authorities["method_parameters"])}
        ),
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_METHOD",
        "raw-axis method semantics mismatch",
    )


def test_nested_authority_boolean_type_is_exact(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    reference = load(fixture.authorities["reference_density"])
    reference["normalization"]["conditional_box_renormalization_used"] = 0
    replace_json(fixture.authorities["reference_density"], reference)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["reference_density"].update(
            {"sha256": sha256_file(fixture.authorities["reference_density"])}
        ),
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        "reference nested semantics mismatch",
    )


def test_result_observed_keys_are_rejected_recursively_in_every_authority(
    tmp_path: Path,
) -> None:
    cases = {
        "reference_density": (
            lambda value: value["normalization"].update({"observed_density": "none"}),
            "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        ),
        "ideal_formula": (
            lambda value: value["formulae"].update({"result_formula": "none"}),
            "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        ),
        "configuration": (
            lambda value: value["dynamics"].update({"observed_precision": 0}),
            "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        ),
        "factorization": (
            lambda value: value["storage_contract"].update({"observed_geometry": "none"}),
            "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        ),
        "member_spec": (
            lambda value: value["identity_properties"].update({"result_digest": "none"}),
            "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        ),
        "method_parameters": (
            lambda value: value["parameters"][0]["parameters"].update({"observed_value": "none"}),
            "HOLD_CANDIDATE_RAW_AXIS_METHOD",
        ),
    }
    for role, (mutate, code) in cases.items():
        fixture = create_neutral_fixture(tmp_path / role)
        authority = load(fixture.authorities[role])
        mutate(authority)
        replace_json(fixture.authorities[role], authority)
        if role == "configuration":
            refresh_configuration_closure(fixture)
        else:
            rewrite_request(
                fixture,
                lambda request, role=role: request["input_authorities"][role].update(
                    {"sha256": sha256_file(fixture.authorities[role])}
                ),
            )
        assert_producer_hold(
            fixture,
            code,
            "result/observed metadata key forbidden",
        )


def test_verifier_independently_rejects_recursive_registry_injection(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    registry = load(fixture.authorities["method_parameters"])
    registry["parameters"][0]["parameters"]["observed_value"] = "none"
    replace_json(fixture.authorities["method_parameters"], registry)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["method_parameters"].update(
            {"sha256": sha256_file(fixture.authorities["method_parameters"])}
        ),
    )
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_METHOD",
        "result/observed metadata key forbidden",
    )


def test_reference_configuration_source_pin_is_cross_checked(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    reference = load(fixture.authorities["reference_density"])
    reference["source_pins"]["configuration_source"]["sha256"] = "b" * 64
    replace_json(fixture.authorities["reference_density"], reference)
    new_reference_sha = sha256_file(fixture.authorities["reference_density"])
    member = load(fixture.authorities["member_spec"])
    member["role_bindings"]["reference_density_source"]["sha256"] = new_reference_sha
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        request["input_authorities"]["reference_density"]["sha256"] = new_reference_sha
        request["input_authorities"]["member_spec"]["sha256"] = sha256_file(
            fixture.authorities["member_spec"]
        )

    rewrite_request(fixture, update_request)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        "reference configuration source: request-bound source mismatch",
    )


def test_member_false_claim_boundary_is_exact(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    member = load(fixture.authorities["member_spec"])
    member["claim_boundary"]["science_executed"] = True
    replace_json(fixture.authorities["member_spec"], member)
    refresh_member_request_pin(fixture)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "member: false claim boundary mismatch",
    )


def test_member_sequence_indices_reject_bool_after_coherent_rehash(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    member = load(fixture.authorities["member_spec"])
    binding = member["n0_sequence_bindings"][0]
    binding["configuration_index"] = False
    binding["sequence_source_row_index"] = False
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)
    refresh_member_request_pin(fixture)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "candidate row identity mismatch",
    )

    verifier_fixture = create_neutral_fixture(tmp_path / "verifier")
    baseline = run_producer(verifier_fixture)
    assert baseline.returncode == 0, baseline.stderr
    member = load(verifier_fixture.authorities["member_spec"])
    binding = member["n0_sequence_bindings"][0]
    binding["configuration_index"] = False
    binding["sequence_source_row_index"] = False
    refresh_member_identity(member)
    replace_json(verifier_fixture.authorities["member_spec"], member)
    refresh_member_request_pin(verifier_fixture)
    assert_verifier_hold(
        verifier_fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_MEMBER_PARTITION",
        "row identity/binding mismatch",
    )


def test_refinement_semantic_ids_reject_empty_after_coherent_rehash(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    member = load(fixture.authorities["member_spec"])
    semantic = member["configuration_semantic_ids"][0]
    binding = member["n0_sequence_bindings"][0]
    semantic["refinement_family_id"] = ""
    semantic["refinement_member_id"] = ""
    binding["refinement_family_id"] = ""
    binding["refinement_member_id"] = ""
    for axis in binding["n0_axes"]:
        axis["refinement_family_id"] = ""
        axis["refinement_member_id"] = ""
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)
    refresh_member_request_pin(fixture)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "candidate row identity mismatch",
    )


def test_partition_request_index_rejects_bool(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    rewrite_request(
        fixture,
        lambda request: request["partitions"][0].update({"configuration_index": False}),
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_REQUEST",
        "invalid/unsorted partition pin",
    )


def test_binary64_overflow_is_semantic_hold_without_traceback(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    configuration = load(fixture.authorities["configuration"])
    configuration["initial_geometry"]["half_width_binary64_hex"] = "0x1p+999999999999999999999999"
    replace_json(fixture.authorities["configuration"], configuration)
    refresh_configuration_closure(fixture)
    produced = run_producer(fixture)
    assert produced.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_INPUT" in produced.stderr
    assert "invalid binary64" in produced.stderr
    assert "Traceback" not in produced.stderr

    verifier_fixture = create_neutral_fixture(tmp_path / "verifier")
    baseline = run_producer(verifier_fixture)
    assert baseline.returncode == 0, baseline.stderr
    configuration = load(verifier_fixture.authorities["configuration"])
    configuration["initial_geometry"]["half_width_binary64_hex"] = "0x1p+999999999999999999999999"
    replace_json(verifier_fixture.authorities["configuration"], configuration)
    refresh_configuration_closure(verifier_fixture)
    verified = run_verifier(verifier_fixture)
    assert verified.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_INPUT" in verified.stderr
    assert "bad binary64" in verified.stderr
    assert "Traceback" not in verified.stderr


def test_factorization_boundary_and_member_binding_are_authenticated(
    tmp_path: Path,
) -> None:
    boundary_fixture = create_neutral_fixture(tmp_path / "boundary")
    factorization = load(boundary_fixture.authorities["factorization"])
    factorization["claim_boundary"]["science_executed"] = True
    replace_json(boundary_fixture.authorities["factorization"], factorization)
    rewrite_request(
        boundary_fixture,
        lambda request: request["input_authorities"]["factorization"].update(
            {"sha256": sha256_file(boundary_fixture.authorities["factorization"])}
        ),
    )
    assert_producer_hold(
        boundary_fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        "factorization: false claim boundary mismatch",
    )

    binding_fixture = create_neutral_fixture(tmp_path / "binding")
    member = load(binding_fixture.authorities["member_spec"])
    member["role_bindings"]["factorization_source"] = {
        "path": "fixture/nonexistent_factorization.json",
        "sha256": "0" * 64,
    }
    refresh_member_identity(member)
    replace_json(binding_fixture.authorities["member_spec"], member)
    refresh_member_request_pin(binding_fixture)
    assert_producer_hold(
        binding_fixture,
        "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION",
        "member factorization source: request-bound source mismatch",
    )


def test_factorization_complete_normative_bytes_are_hard_bound(tmp_path: Path) -> None:
    for case in ("outcome", "numeric", "cycle", "formula"):
        fixture = create_neutral_fixture(tmp_path / case)
        factorization = load(fixture.authorities["factorization"])
        if case == "outcome":
            factorization["outcome_free_contract"]["production_bridge_present"] = True
        elif case == "numeric":
            factorization["enclosure_semantics"]["future_numeric_payload_present"] = True
        elif case == "cycle":
            factorization["dependency_closure"]["acyclic"] = False
            factorization["dependency_closure"]["edges"].append(
                {
                    "from": "factorization_source_v2_candidate",
                    "to": "configuration_source",
                }
            )
        else:
            factorization["cell_average_formulae"]["contact_average"] = (
                "coherently_rewritten_contact_average"
            )
        replace_json(fixture.authorities["factorization"], factorization)
        refresh_factorization_binding(fixture)
        assert_producer_hold(
            fixture,
            "HOLD_CANDIDATE_RAW_AXIS_INPUT",
            "factorization: exact authority path/SHA mismatch",
        )


def test_verifier_independently_hard_binds_factorization_bytes(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    baseline = run_producer(fixture)
    assert baseline.returncode == 0, baseline.stderr
    factorization = load(fixture.authorities["factorization"])
    factorization["profile_basis"]["profile_count"] = 5
    replace_json(fixture.authorities["factorization"], factorization)
    refresh_factorization_binding(fixture)
    assert_verifier_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_VALIDATOR_INPUT",
        "factorization: exact authority path/SHA mismatch",
    )


def test_factorization_exact_report_relative_path_is_hard_bound(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    wrong_path = fixture.root / "wrong_authority/factorization.json"
    wrong_path.parent.mkdir(mode=0o700)
    fixture.authorities["factorization"].rename(wrong_path)
    fixture.authorities["factorization"] = wrong_path
    member = load(fixture.authorities["member_spec"])
    member["role_bindings"]["factorization_source"]["path"] = "wrong_authority/factorization.json"
    refresh_member_identity(member)
    replace_json(fixture.authorities["member_spec"], member)

    def update_request(request: dict[str, Any]) -> None:
        request["input_authorities"]["factorization"]["path"] = str(wrong_path)
        request["input_authorities"]["member_spec"]["sha256"] = sha256_file(
            fixture.authorities["member_spec"]
        )

    rewrite_request(fixture, update_request)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        "factorization: exact authority path/SHA mismatch",
    )


@pytest.mark.parametrize(
    ("role", "source_pin", "bad_schema", "detail"),
    (
        (
            "factorization_initial_partition_bundle",
            "initial_partition_bundle",
            "encounter_control_free_production_initial_stream_v0",
            "factorization initial partition bundle: nested authority schema mismatch",
        ),
        (
            "factorization_killing_geometry",
            "killing_geometry_source",
            "encounter_physical_killing_geometry_source_v0",
            "factorization killing geometry source: nested authority schema mismatch",
        ),
    ),
)
def test_factorization_nested_authorities_are_parsed_and_schema_validated(
    tmp_path: Path,
    role: str,
    source_pin: str,
    bad_schema: str,
    detail: str,
) -> None:
    fixture = create_neutral_fixture(tmp_path / role)
    nested = load(fixture.authorities[role])
    nested["schema"] = bad_schema
    replace_json(fixture.authorities[role], nested)
    nested_sha = sha256_file(fixture.authorities[role])
    factorization = load(fixture.authorities["factorization"])
    factorization["source_pins"][source_pin]["sha256"] = nested_sha
    replace_json(fixture.authorities["factorization"], factorization)
    refresh_factorization_binding(fixture)

    def update_request(request: dict[str, Any]) -> None:
        request["input_authorities"][role]["sha256"] = nested_sha

    rewrite_request(fixture, update_request)
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        detail,
    )


def test_configuration_authority_bytes_are_authenticated(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    replace_json(
        fixture.authorities["configuration_design"],
        {"fixture_role": "mutated_configuration_design"},
    )
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["configuration_design"].update(
            {"sha256": sha256_file(fixture.authorities["configuration_design"])}
        ),
    )
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_INPUT",
        "configuration design pin: request-bound source mismatch",
    )


def test_fifo_authority_fails_without_blocking(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    fifo = fixture.root / "reference-authority.fifo"
    os.mkfifo(fifo, 0o400)
    rewrite_request(
        fixture,
        lambda request: request["input_authorities"]["reference_density"].update(
            {"path": str(fifo), "sha256": "0" * 64}
        ),
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(fixture.producer),
            "--request",
            str(fixture.request),
            "--output",
            str(fixture.output),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert completed.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT" in completed.stderr


def test_preexisting_output_is_preserved_and_stages_are_absent(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    attacker_bytes = b"attacker-owned-preexisting-output\n"
    fixture.output.write_bytes(attacker_bytes)
    fixture.output.chmod(0o400)
    before = fixture.output.stat()
    assert_producer_hold(
        fixture,
        "HOLD_CANDIDATE_RAW_AXIS_OUTPUT",
        "output already exists",
    )
    after = fixture.output.stat()
    assert fixture.output.read_bytes() == attacker_bytes
    assert (before.st_dev, before.st_ino, before.st_mode) == (
        after.st_dev,
        after.st_ino,
        after.st_mode,
    )
    assert not list(fixture.root.glob(f".{fixture.output.name}.stage.*"))


def test_successful_atomic_publication_leaves_no_stage(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    assert fixture.output.stat().st_nlink == 1
    assert not list(fixture.root.glob(f".{fixture.output.name}.stage.*"))
