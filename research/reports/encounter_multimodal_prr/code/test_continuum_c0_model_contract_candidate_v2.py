from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as producer
import validate_continuum_c0_model_contract_candidate_v2 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"


def _contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_producer_rebuilds_the_published_candidate_byte_for_byte() -> None:
    published = CONTRACT.read_bytes()
    rebuilt = producer.build_bytes()
    assert rebuilt == published
    assert rebuilt == producer.canonical_json_bytes(json.loads(rebuilt.decode("ascii")))
    assert hashlib.sha256(rebuilt).hexdigest() == verifier.EXPECTED_CONTRACT_SHA256


def test_independent_verifier_receipt_is_narrow_and_nonpromoting() -> None:
    contract = _contract()
    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())

    assert receipt["status"] == verifier.PASS_STATUS
    assert receipt["contract_sha256"] == verifier.EXPECTED_CONTRACT_SHA256
    assert receipt["complete_c0"] is False
    assert receipt["control_values_read"] is False
    assert receipt["gauged_ideal_member_containment_proved"] is False
    assert receipt["positive_budget_scientific_values_read"] is False
    assert receipt["production_raw_to_gauged_bridge_proved"] is False
    assert receipt["release_eligible"] is False
    assert receipt["scratch_or_result_payload_read"] is False

    claims = contract["claim_boundary"]
    for key in (
        "complete_c0_independently_accepted",
        "control_values_committed_for_c0",
        "gauged_ideal_member_containment_proved_for_every_declared_configuration",
        "positive_budget_scientific_values_read",
        "production_centre_mosco_proved",
        "production_raw_to_gauged_bridge_proved",
        "release_eligible",
    ):
        assert claims[key] is False
    assert claims["sealed_control_source_required_before_complete_c0"] is True


def test_five_source_allowlist_excludes_scratch_results_and_living_notes() -> None:
    contract = _contract()
    sources = contract["frozen_sources"]
    expected_roles = {
        "configuration_family",
        "control_method_commitment",
        "initial_source",
        "killing_geometry_source",
        "mathematical_source",
    }
    assert set(sources) == expected_roles
    assert len(sources) == 5
    assert sources == producer.FROZEN_SOURCES == verifier.FROZEN_SOURCES

    for descriptor in sources.values():
        relative = Path(descriptor["path"])
        lowered = relative.as_posix().lower()
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        assert "scratch" not in relative.parts
        assert "result" not in lowered
        assert "continuum_research_program" not in lowered
        assert "positive_b_fixed_control_robustness_design" not in lowered
        assert relative.suffix == ".json"

    policy = contract["source_policy"]
    assert policy == verifier.EXPECTED_SOURCE_POLICY
    assert policy["allowed_opened_source_roles"] == sorted(expected_roles)
    assert policy["embedded_source_paths_followed"] is False
    assert policy["living_continuum_program_pinned"] is False
    assert policy["opaque_scratch_or_result_payload_opened"] is False
    assert policy["positive_budget_design_note_opened"] is False

    exclusions = contract["control_contract"]["exclusions"]
    assert all(value is False for value in exclusions.values())


def test_maps_gauge_operator_and_scalar_conventions_are_unambiguous() -> None:
    contract = _contract()
    maps = contract["finite_volume_identification"]
    assert maps == verifier.EXPECTED_MAPS
    assert maps["P_h"]["denominator"] == "pi_h_i"
    assert maps["P_h"]["exact_adjoint_of_J_h"] is True
    assert maps["A_h"]["denominator"] == "M_i_pi"
    assert maps["S_h"]["defined_on_all_H_L"] is False
    assert maps["S_h"]["smooth_or_continuous_recovery_core_only"] is True
    assert maps["rho_i"]["formula"] == "rho_i=M_i_pi/pi_h_i"
    assert maps["exact_identities"] == {
        "A_h_J_h": "I",
        "J_h_A_h": "E_h_pi_weighted_cell_conditional_expectation",
        "J_h_P_h": "rho_h_pc*E_h",
        "P_h": "J_h_adjoint",
        "P_h_J_h": "diag(rho_i)",
        "P_h_relation_to_A_h": "P_h=diag(rho_i)*A_h",
    }
    assert all(value is False for value in maps["nonclaims"].values())

    gauge = contract["stationary_mass_gauge"]
    assert gauge == verifier.EXPECTED_GAUGE
    assert gauge["scale_formula"] == "g_h_L=M_L/sum_i_tilde_pi_h_i"
    assert gauge["global_mass_identity"] == "sum_i_pi_h_i=M_L"
    assert gauge["conditional_renormalization_to_one"] is False
    assert gauge["target"] == "restricted_fixed_box_mass_not_full_space_probability_one"

    operator = contract["discrete_operator_convention"]
    assert operator == verifier.EXPECTED_OPERATOR
    assert operator["row_generator_convention"] is True
    assert operator["probability_forward_equation"] == "p_prime=transpose(Q_c)*p"
    assert operator["density_ratio_forward_equation"] == "u_prime=Q_c*u"
    assert operator["undirected_edge_has_extra_one_half"] is False
    assert operator["undirected_edge_single_common_conductance"] == (
        "c_ij=pi_h_i*q_ij=pi_h_j*q_ji"
    )

    scalar = contract["scalar_convention"]
    assert scalar == verifier.EXPECTED_SCALAR
    assert scalar["primary_scalar_field"] == "real"
    assert scalar["complex_forms_conjugate_first_factor"] is True


def test_initial_projection_and_support_certificate_are_current() -> None:
    contract = _contract()
    initial = contract["initial_law"]
    certificate = initial["support_certificate"]
    assert initial["initial_probability_cell_mass"] == "p0_h_i=integral_C_i_q0_dx"
    assert initial["unique_discrete_density_ratio"] == (
        "u0_h_i=p0_h_i/pi_h_i=P_h[u0]_i"
    )
    assert initial["meshwise_renormalization"] is False
    assert "support_closure_strictly_inside_every_declared_nonperiodic_box" in initial[
        "requirements"
    ]
    assert certificate["configuration_count_checked"] == 12
    assert certificate["nonperiodic_axes_checked"] == 24
    assert certificate["periodic_axes_checked"] == 12
    assert certificate["strict_side_inequalities_checked"] == 48
    assert certificate["periodic_support_handled_as_wrapped_arc"] is True
    assert certificate["support_closure_strictly_inside_all_nonperiodic_boxes"] is True
    assert Fraction(certificate["global_minimum_clearance_exact"]) > 0

    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert receipt["support_certificate"] == certificate
