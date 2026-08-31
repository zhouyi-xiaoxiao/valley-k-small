from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import pytest
import validate_manuscript_completion_contract_v1 as validator

REPORT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPORT / "artifacts/data/manuscript_completion_contract_v1.json"


def _contract() -> dict[str, object]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert type(payload) is dict
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def test_contract_is_a_fail_closed_pre_f0_freeze() -> None:
    contract = _contract()
    assert validator.load_and_validate_contract(CONTRACT_PATH) == contract
    assert contract["schema_version"] == "encounter_manuscript_completion_contract_v1"
    assert contract["stage"] == "pre_f0_claim_and_terminal_branch_freeze"
    assert contract["status"] == "FROZEN_PRE_F0_NO_SCIENTIFIC_EXECUTION"
    assert contract["authorized_scientific_command"] is None

    state = contract["current_state"]
    assert type(state) is dict
    assert state == {
        "f0_independently_accepted": False,
        "f1_authorized": False,
        "manuscript_complete": False,
        "science_branch_selected": False,
        "submission_eligible": False,
    }

    f0 = contract["f0_acceptance"]
    assert type(f0) is dict
    assert f0["science_free"] is True
    assert f0["positive_budget_primary_controls_evaluated"] is False
    assert f0["production_resource_measurement_required"] is True
    assert f0["independent_semantic_replay_required"] is True
    assert f0["clean_canonical_replicas"] == 2
    assert f0["actual_largest_shape"] == [207, 215, 161]
    assert f0["actual_largest_states"] == 207 * 215 * 161 == 7_165_305
    assert f0["required_capabilities"] == validator.EXPECTED_F0_CAPABILITIES


def test_claim_ceiling_makes_strict_continuum_conditional() -> None:
    claim = _contract()["claim_ceiling"]
    assert type(claim) is dict
    assert claim == validator.EXPECTED_CLAIM_CEILING
    assert claim["strict_continuum_claimed"] is False
    assert (
        claim["strict_continuum_gate"]
        == "CONDITIONAL_ONLY_IF_STRICT_NUMERICAL_CONTINUUM_CLAIMED"
    )
    assert claim["numerical_claim"] == (
        "finite_window_continuum_consistent_physical_d2_evidence"
    )
    assert claim["numerical_topology_window"] == ["1/2", "35/1"]
    assert claim["numerical_tail_checks_end"] == "100/1"
    assert "strict_numerical_continuum_limit" in claim["forbidden_numerical_claims"]
    assert "allocation_cusp" in claim["forbidden_numerical_claims"]


def test_exact_controls_and_frozen_36_row_order() -> None:
    contract = _contract()
    controls = contract["exact_controls"]
    assert type(controls) is dict
    assert controls["budget_binary64_hex"] == float.fromhex(
        "0x1.47ae147ae147bp-7"
    ).hex()
    for control_id in ("lp_m1", "lp_m2", "lp_m3"):
        weights = controls[control_id]
        assert type(weights) is list and len(weights) == 4
        fractions = tuple(Fraction(value) for value in weights)
        assert all(value > 0 for value in fractions)
        assert sum(fractions, Fraction(0)) == 1
    selector = json.loads(
        (
            REPORT
            / "scratch/modal_certificate_exact_selector_method_only_result.json"
        ).read_text(encoding="utf-8")
    )
    for source_id, control_id in (("m1", "lp_m1"), ("m2", "lp_m2"), ("m3", "lp_m3")):
        expected = [
            weight["exact"]
            for weight in selector["selector_results"][source_id]["selected"]["weights"]
        ]
        assert controls[control_id] == expected

    f1 = contract["f1_contract"]
    assert type(f1) is dict
    assert f1["control_order"] == ["lp_m1", "lp_m2", "lp_m3"]
    assert f1["configuration_order"] == validator.EXPECTED_CONFIGURATIONS
    assert len(f1["control_order"]) * len(f1["configuration_order"]) == 36
    assert f1["ordered_rows"] == 36
    assert f1["replicas"] == 2
    assert f1["no_refit"] is True
    assert f1["stop_after_first_hold"] is True


def test_every_pinned_source_hash_matches_current_bytes() -> None:
    sources = _contract()["immutable_sources"]
    assert type(sources) is dict and sources
    for label, record in sources.items():
        assert type(label) is str and label
        assert type(record) is dict
        relative = record["path"]
        expected = record["sha256"]
        assert type(relative) is str and not relative.startswith("/")
        assert type(expected) is str and len(expected) == 64
        source = REPORT / relative
        assert source.is_file(), f"missing pinned source: {relative}"
        assert _sha256(source) == expected, f"pinned source drifted: {relative}"


def test_terminal_branches_prohibit_illegal_downstream_promotion() -> None:
    branches = _contract()["terminal_branches"]
    assert type(branches) is dict
    assert set(branches) == set(validator.EXPECTED_BRANCHES)
    for name in (
        "HOLD_F0_METHOD_OR_RESOURCE",
        "HOLD_F1_SCIENCE",
        "HOLD_F1_METHOD_OR_RESOURCE",
        "HOLD_F2_PLAN_OR_RESOURCE",
    ):
        branch = branches[name]
        if name != "HOLD_F2_PLAN_OR_RESOURCE":
            assert branch["f2_permitted"] is False
        assert branch["f3_permitted"] is False
        assert branch["independent_validation_claim_permitted"] is False
    assert branches["HOLD_F0_METHOD_OR_RESOURCE"]["f1_permitted"] is False
    assert branches["HOLD_F3_SCIENCE"][
        "deterministic_f1_claim_permitted_at_exact_scope"
    ] is True
    assert branches["HOLD_F3_SCIENCE"][
        "independent_validation_claim_permitted"
    ] is False
    assert branches["PASS_VALIDATED_D2"]["submission_still_requires_editorial_and_final_audits"]


def test_complete_no_refit_field_set_is_exact() -> None:
    no_refit = _contract()["no_refit"]
    assert no_refit == {
        "after_independent_f0_acceptance": True,
        "forbidden_changes": validator.EXPECTED_NO_REFIT_FIELDS,
    }


@pytest.mark.parametrize(
    "mutator",
    [
        lambda payload: payload["exact_controls"].__setitem__(
            "lp_m1",
            ["91/100", "3/100", "3/100", "3/100"],
        ),
        lambda payload: payload["claim_ceiling"].pop("theorem_claim"),
        lambda payload: payload["claim_ceiling"]["forbidden_numerical_claims"].pop(),
        lambda payload: payload.pop("no_refit"),
        lambda payload: payload["terminal_branches"]["PASS_VALIDATED_D2"].__setitem__(
            "independent_validation_claim_permitted",
            False,
        ),
        lambda payload: payload["terminal_branches"]["PASS_VALIDATED_D2"].__setitem__(
            "manuscript_action",
            "promote_any_available_result",
        ),
        lambda payload: payload["terminal_branches"]["HOLD_F2_PLAN_OR_RESOURCE"][
            "required_statuses"
        ].__setitem__("f2", "PASS_F2_PLAN"),
        lambda payload: payload["f0_acceptance"]["required_capabilities"].pop(),
        lambda payload: payload["immutable_sources"].pop("fixed_control_design"),
        lambda payload: payload["immutable_sources"]["fixed_control_design"].update(
            {
                "path": "README.md",
                "sha256": hashlib.sha256((REPORT / "README.md").read_bytes()).hexdigest(),
            }
        ),
        lambda payload: payload.__setitem__("limitations", []),
        lambda payload: payload.__setitem__("scientific_execution_authorized", True),
    ],
)
def test_claim_bearing_mutations_fail_closed(mutator) -> None:
    mutation = deepcopy(_contract())
    mutator(mutation)
    with pytest.raises(validator.ContractValidationError):
        validator.validate_contract_payload(mutation)
