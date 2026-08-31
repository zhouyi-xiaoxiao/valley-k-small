from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as v2_producer
import build_continuum_c0_model_contract_candidate_v3 as producer
import validate_continuum_c0_model_contract_candidate_v2 as v2_verifier
import validate_continuum_c0_model_contract_candidate_v3 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v3.json"
BASE_CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"


def _contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_v3_wrapper_rebuilds_the_published_candidate_byte_for_byte() -> None:
    published = CONTRACT.read_bytes()
    rebuilt = producer.build_bytes()
    assert rebuilt == published
    assert rebuilt == v2_producer.canonical_json_bytes(json.loads(rebuilt.decode("ascii")))
    assert hashlib.sha256(rebuilt).hexdigest() == verifier.EXPECTED_CONTRACT_SHA256


def test_v2_base_is_byte_immutable_reproducible_and_semantically_verified() -> None:
    base_bytes = BASE_CONTRACT.read_bytes()
    assert hashlib.sha256(base_bytes).hexdigest() == producer.BASE_SHA256
    assert v2_producer.build_bytes() == base_bytes
    base_receipt = v2_verifier.verify_contract_bytes(base_bytes)
    assert base_receipt["status"] == v2_verifier.PASS_STATUS
    assert base_receipt["contract_sha256"] == producer.BASE_SHA256
    assert base_receipt["complete_c0"] is False
    assert base_receipt["production_raw_to_gauged_bridge_proved"] is False
    assert base_receipt["release_eligible"] is False

    contract = _contract()
    expected_base = {
        "path": str(producer.BASE_RELATIVE),
        "semantic_verification_required": True,
        "sha256": producer.BASE_SHA256,
    }
    assert contract["base_contract"] == expected_base
    assert contract["frozen_sources"]["base_contract"] == {
        "path": str(producer.BASE_RELATIVE),
        "sha256": producer.BASE_SHA256,
    }
    assert contract["source_policy"]["base_v2_verifier_must_pass"] is True
    assert contract["source_policy"]["v2_bytes_mutated"] is False


def test_all_measure_mass_and_map_well_definedness_flags_are_explicit() -> None:
    contract = _contract()
    preconditions = contract["measure_and_partition_preconditions"]
    assert preconditions == verifier.EXPECTED_PRECONDITIONS

    geometry = preconditions["configuration_geometry_preconditions"]
    assert geometry["declared_configuration_count"] == 12
    assert all(
        value is True
        for key, value in geometry.items()
        if key != "declared_configuration_count"
    )

    continuum = preconditions["continuum_measure_preconditions"]
    assert continuum["M_i_pi_formula"] == "M_i_pi=integral_C_i_pi_dx"
    assert all(value is True for key, value in continuum.items() if key != "M_i_pi_formula")

    mass = preconditions["discrete_mass_preconditions"]
    assert mass["g_h_L_formula"] == "g_h_L=M_L/sum_i_tilde_pi_h_i"
    assert mass["pi_h_i_formula"] == "pi_h_i=g_h_L*tilde_pi_h_i"
    assert all(value is True for key, value in mass.items() if not key.endswith("_formula"))

    consequences = preconditions["map_well_definedness_consequences"]
    assert all(value is True for value in consequences.values())
    assert consequences["A_h_denominator_nonzero"] is True
    assert consequences["P_h_denominator_nonzero"] is True
    assert consequences["rho_i_finite_and_strictly_positive"] is True

    boundary = preconditions["verification_boundary"]
    assert boundary["geometry_checked_for_every_declared_configuration"] is True
    assert boundary[
        "raw_mass_positivity_is_an_ideal_model_precondition_not_a_production_interval_claim"
    ] is True
    assert boundary["complete_c0"] is False
    assert boundary["production_raw_to_gauged_bridge_proved"] is False
    assert boundary["release_eligible"] is False


def test_geometry_receipt_covers_every_declared_partition_and_tensor_cell() -> None:
    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert receipt["status"] == verifier.PASS_STATUS
    assert receipt["base_verifier_status"] == v2_verifier.PASS_STATUS
    assert receipt["base_contract_sha256"] == producer.BASE_SHA256
    assert receipt["contract_sha256"] == verifier.EXPECTED_CONTRACT_SHA256
    assert receipt["geometry_receipt"] == {
        "all_declared_control_volumes_positive_and_partitioning": True,
        "axis_partitions_checked": 36,
        "configuration_count_checked": 12,
        "endpoint_half_volume_axes_checked": 4,
        "tensor_cells_accounted_for": 34_787_462,
        "wrapped_periodic_rows_represented": 2,
    }
    assert receipt["map_and_gauge_well_definedness_preconditions_explicit"] is True


def test_v3_receipt_and_claims_remain_strictly_nonpromoting() -> None:
    contract = _contract()
    claims = contract["claim_boundary"]
    assert claims == verifier.EXPECTED_CLAIMS
    for key in (
        "complete_c0_independently_accepted",
        "control_values_committed_for_c0",
        "positive_budget_scientific_values_read",
        "production_raw_to_gauged_bridge_proved",
        "release_eligible",
    ):
        assert claims[key] is False
    assert claims["raw_mass_positivity_is_ideal_model_precondition_only"] is True

    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert receipt["complete_c0"] is False
    assert receipt["control_values_read"] is False
    assert receipt["positive_budget_scientific_values_read"] is False
    assert receipt["production_raw_to_gauged_bridge_proved"] is False
    assert receipt["release_eligible"] is False
    assert receipt["scratch_control_or_result_payload_read"] is False


def test_actual_v3_dependency_open_set_matches_the_receipt(monkeypatch) -> None:
    observed: list[tuple[str, int]] = []
    real_open = os.open

    def audited_open(path, flags, *args, **kwargs):
        observed.append((os.fspath(path), flags))
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", audited_open)
    producer.build_bytes()
    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    actual_names = {
        Path(path).name for path, _flags in observed if Path(path).suffix == ".json"
    }
    declared_names = {
        Path(path).name
        for path in receipt["opened_auxiliary_paths"] + receipt["opened_source_paths"]
    }
    assert actual_names == declared_names
    write_mask = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
    assert all(flags & write_mask == 0 for path, flags in observed if Path(path).suffix == ".json")
