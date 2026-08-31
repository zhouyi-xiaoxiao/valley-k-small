from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import validate_continuum_c0_model_contract_candidate as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"


def _candidate() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _reject(candidate: dict[str, object], code: str) -> None:
    with pytest.raises(verifier.C0ContractHold) as caught:
        verifier.verify_contract_bytes(verifier.canonical_json_bytes(candidate))
    assert caught.value.code == code


def test_exact_candidate_produces_narrow_nonpromotion_receipt() -> None:
    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert receipt["status"] == verifier.PASS_STATUS
    assert receipt["contract_sha256"] == (
        "5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66"
    )
    assert receipt["positive_budget_scientific_values_read"] is False
    assert receipt["release_eligible"] is False


def test_duplicate_key_and_nonfinite_number_are_rejected() -> None:
    raw = CONTRACT.read_bytes()
    duplicate = raw.replace(b'{\n  "boundary_conditions": {', b'{\n  "schema": "forged",\n  "boundary_conditions": {', 1)
    with pytest.raises(verifier.C0ContractHold) as duplicate_hold:
        verifier.verify_contract_bytes(duplicate)
    assert duplicate_hold.value.code == verifier.HOLD_ENCODING
    nonfinite = raw.replace(b'"physical_dimension": 2', b'"physical_dimension": NaN', 1)
    with pytest.raises(verifier.C0ContractHold) as nonfinite_hold:
        verifier.verify_contract_bytes(nonfinite)
    assert nonfinite_hold.value.code == verifier.HOLD_ENCODING


def test_decimal_for_dyadic_substitution_is_rejected() -> None:
    candidate = _candidate()
    candidate["physical_parameters"]["B"]["exact"] = "1/100"
    _reject(candidate, verifier.HOLD_PARAMETERS)


def test_unit_swap_is_rejected() -> None:
    candidate = _candidate()
    pars = candidate["physical_parameters"]
    pars["B"]["unit"], pars["D"]["unit"] = pars["D"]["unit"], pars["B"]["unit"]
    _reject(candidate, verifier.HOLD_PARAMETERS)


def test_source_role_swap_is_rejected() -> None:
    candidate = _candidate()
    sources = candidate["frozen_sources"]
    sources["initial_source"], sources["killing_geometry_source"] = (
        sources["killing_geometry_source"],
        sources["initial_source"],
    )
    _reject(candidate, verifier.HOLD_SOURCES)


def test_reflecting_target_promotion_is_rejected() -> None:
    candidate = _candidate()
    candidate["boundary_conditions"]["target_midpoint"] = "reflecting_zero_flux"
    _reject(candidate, verifier.HOLD_BOUNDARY)


def test_w_inverse_removal_and_smoothed_contact_are_rejected() -> None:
    candidate = _candidate()
    candidate["killing_field"]["field"] = "contact*sum_j(w_c_j*phi_j(midpoint))"
    _reject(candidate, verifier.HOLD_KILLING)
    candidate = _candidate()
    candidate["killing_field"]["sharp_contact_retained"] = False
    _reject(candidate, verifier.HOLD_KILLING)


def test_box_order_and_alignment_role_mutations_are_rejected() -> None:
    candidate = _candidate()
    candidate["mesh_contract"]["configuration_order"] = list(
        reversed(candidate["mesh_contract"]["configuration_order"])
    )
    _reject(candidate, verifier.HOLD_MESH)
    candidate = _candidate()
    classes = candidate["mesh_contract"]["alignment_classes"]
    classes[0], classes[2] = classes[2], classes[0]
    _reject(candidate, verifier.HOLD_MESH)


def test_identification_map_and_gauge_mutations_are_rejected() -> None:
    candidate = _candidate()
    candidate["finite_volume_identification"]["P_h"] = "unweighted_cell_average"
    _reject(candidate, verifier.HOLD_IDENTIFICATION)
    candidate = _candidate()
    candidate["finite_volume_identification"]["stationary_mass_gauge"] = (
        "sum_i_pi_h_i=1"
    )
    _reject(candidate, verifier.HOLD_IDENTIFICATION)


def test_equation_omission_and_claim_promotion_are_rejected() -> None:
    candidate = _candidate()
    candidate["equation_contract"].remove("2.16")
    _reject(candidate, verifier.HOLD_EQUATIONS)
    candidate = _candidate()
    candidate["claim_boundary"]["complete_c0_independently_accepted"] = True
    _reject(candidate, verifier.HOLD_CLAIMS)


def test_opaque_control_hash_and_control_order_mutations_are_rejected() -> None:
    candidate = _candidate()
    candidate["control_contract"]["opaque_result_blind_source_sha256"] = "0" * 64
    _reject(candidate, verifier.HOLD_CONTROL)
    candidate = _candidate()
    candidate["control_contract"]["control_ids"] = ["m2", "m1", "m3"]
    _reject(candidate, verifier.HOLD_CONTROL)


def test_result_bearing_token_is_rejected_even_under_extra_nested_metadata() -> None:
    candidate = copy.deepcopy(_candidate())
    candidate["claim_boundary"]["peak_time"] = "forbidden"
    _reject(candidate, verifier.HOLD_CLAIMS)
