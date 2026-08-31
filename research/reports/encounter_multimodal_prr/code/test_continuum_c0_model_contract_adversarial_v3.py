from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import validate_continuum_c0_model_contract_candidate_v3 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v3.json"
CONFIGURATION_FAMILY = (
    REPORT / "artifacts/data/physical_configuration_family_control_free_v1.json"
)


def _candidate() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _reject_candidate(candidate: dict[str, object], code: str) -> None:
    payload = verifier.base.canonical_json_bytes(candidate)
    with pytest.raises(verifier.C0V3Hold) as caught:
        verifier.verify_contract_bytes(payload)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("section", "flag"),
    [
        (
            "configuration_geometry_preconditions",
            "each_control_volume_has_finite_positive_physical_volume",
        ),
        ("continuum_measure_preconditions", "M_i_pi_strictly_positive_for_every_declared_cell"),
        ("discrete_mass_preconditions", "tilde_pi_h_i_strictly_positive_for_every_declared_cell"),
        ("map_well_definedness_consequences", "P_h_denominator_nonzero"),
    ],
)
def test_false_well_definedness_precondition_is_rejected(section: str, flag: str) -> None:
    candidate = _candidate()
    candidate["measure_and_partition_preconditions"][section][flag] = False
    _reject_candidate(candidate, verifier.HOLD_PRECONDITIONS)


def test_measure_and_gauge_formula_swap_is_rejected() -> None:
    candidate = _candidate()
    preconditions = candidate["measure_and_partition_preconditions"]
    continuum = preconditions["continuum_measure_preconditions"]
    mass = preconditions["discrete_mass_preconditions"]
    continuum["M_i_pi_formula"], mass["g_h_L_formula"] = (
        mass["g_h_L_formula"],
        continuum["M_i_pi_formula"],
    )
    _reject_candidate(candidate, verifier.HOLD_PRECONDITIONS)


@pytest.mark.parametrize("field", ["path", "sha256"])
def test_immutable_base_path_or_hash_mutation_is_rejected(field: str) -> None:
    candidate = _candidate()
    candidate["base_contract"][field] = "0" * 64 if field == "sha256" else "artifacts/data/v1.json"
    _reject_candidate(candidate, verifier.HOLD_BASE)


@pytest.mark.parametrize(
    "claim",
    [
        "complete_c0_independently_accepted",
        "control_values_committed_for_c0",
        "positive_budget_scientific_values_read",
        "production_raw_to_gauged_bridge_proved",
        "release_eligible",
    ],
)
def test_claim_promotion_is_rejected(claim: str) -> None:
    candidate = _candidate()
    candidate["claim_boundary"][claim] = True
    _reject_candidate(candidate, verifier.HOLD_CLAIMS)


def test_noncanonical_duplicate_and_nonfinite_encodings_are_rejected() -> None:
    raw = CONTRACT.read_bytes()
    noncanonical = raw.replace(b"{\n", b"{ \n", 1)
    duplicate = raw.replace(
        b"{\n",
        b'{\n  "schema": "forged-duplicate",\n',
        1,
    )
    nonfinite = raw.replace(
        b'"declared_configuration_count": 12',
        b'"declared_configuration_count": NaN',
        1,
    )
    for payload in (noncanonical, duplicate, nonfinite):
        with pytest.raises(verifier.C0V3Hold) as caught:
            verifier.verify_contract_bytes(payload)
        assert caught.value.code == verifier.HOLD_ENCODING


def test_injected_result_path_is_rejected_before_schema_acceptance() -> None:
    candidate = _candidate()
    candidate["source_policy"]["forbidden_probe"] = "scratch/results/positive_result.json"
    _reject_candidate(candidate, verifier.HOLD_RESULT_BLINDNESS)


def test_deep_json_is_converted_to_a_v3_encoding_hold() -> None:
    deep = b'{"nested":' + b"[" * 2_000 + b"0" + b"]" * 2_000 + b"}\n"
    huge_integer = b'{"x":' + b"9" * 5_000 + b"}\n"
    for attacked in (deep, huge_integer):
        with pytest.raises(verifier.C0V3Hold) as caught:
            verifier.verify_contract_bytes(attacked)
        assert caught.value.code == verifier.HOLD_ENCODING


def test_v3_direct_bytes_entrypoint_enforces_the_size_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attacked = b'{"x":"123456789"}\n'
    monkeypatch.setattr(verifier.base, "MAX_FILE_BYTES", 8)
    with pytest.raises(verifier.C0V3Hold) as caught:
        verifier.verify_contract_bytes(attacked)
    assert caught.value.code == verifier.HOLD_ENCODING


@pytest.mark.parametrize("attack", ["size", "alignment", "bounds"])
def test_geometry_helper_rejects_cell_size_alignment_and_bounds_attacks(attack: str) -> None:
    family = json.loads(CONFIGURATION_FAMILY.read_text(encoding="utf-8"))
    attacked = copy.deepcopy(family)
    axis = attacked["configurations"][0]["midpoint"]
    if attack == "size":
        axis["size"] = 0
    elif attack == "alignment":
        axis["alignment"] = "periodic_masquerading_as_nonperiodic"
    else:
        axis["lower_binary64_hex"] = axis["upper_binary64_hex"]

    with pytest.raises(verifier.C0V3Hold) as caught:
        verifier._validate_all_geometry(attacked)
    assert caught.value.code == verifier.HOLD_GEOMETRY
