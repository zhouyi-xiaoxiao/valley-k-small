from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as c0_builder
import build_continuum_c1_ideal_refinement_contract_candidate_v1 as producer
import validate_continuum_c1_ideal_refinement_contract_candidate_v1 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = (
    REPORT
    / "artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json"
)


def _contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_published_candidate_rebuilds_byte_for_byte_and_has_pinned_hash() -> None:
    published = CONTRACT.read_bytes()
    rebuilt = producer.build_bytes()
    assert rebuilt == published
    assert rebuilt == c0_builder.canonical_json_bytes(json.loads(rebuilt.decode("ascii")))
    assert hashlib.sha256(rebuilt).hexdigest() == verifier.EXPECTED_CONTRACT_SHA256


def test_four_refinement_families_are_explicit_and_fixed_box() -> None:
    contract = _contract()
    fixed_box = contract["fixed_box"]
    assert fixed_box == verifier.EXPECTED_FIXED_BOX
    preconditions = fixed_box["parameter_preconditions"]
    assert preconditions["D"] == "D>0"
    assert preconditions["W"] == "W>0"
    assert preconditions["gamma"] == "gamma>0"
    assert preconditions["midpoint_interval_nondegenerate"] == "ell_z<r_z"
    assert preconditions["relative_parallel_interval_nondegenerate"] == "ell_r<r_r"
    assert preconditions["midpoint_density_normalizer"] == "C_z>0"
    assert preconditions["relative_parallel_density_normalizer"] == "C_r>0"
    sequences = contract["ideal_refinement_sequences"]
    assert sequences["every_axis_interval_count_tends_to_infinity"] is True
    assert sequences["fixed_box_and_physical_parameters_across_sequence"] is True
    families = sequences["axis_families"]
    assert set(families) == {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
        "cell_centred_reflecting_ou",
        "vertex_centred_reflecting_dual_ou",
    }
    assert families["cell_centred_reflecting_ou"]["N_constraint"] == (
        "integer N>=3 with N->infinity"
    )
    assert families["vertex_centred_reflecting_dual_ou"]["N_constraint"] == (
        "integer N>=2 with N->infinity"
    )


def test_vertex_dual_rate_uses_endpoint_half_volume_factor() -> None:
    vertex = _contract()["ideal_refinement_sequences"]["axis_families"][
        "vertex_centred_reflecting_dual_ou"
    ]
    assert vertex["volumes"] == "nu_0=nu_N=h/2 and nu_i=h for 1<=i<=N-1"
    assert vertex["source_size_relation"] == "size=N+1"
    assert vertex["rate_contract"]["forward_rate"] == (
        "q_(i,i+1)=d/(nu_i*h)*B(Phi_(i+1)-Phi_i)"
    )
    assert "twice" in vertex["endpoint_rate_factor"]


def test_periodic_base_and_half_shift_require_n3_and_wrapping_edge() -> None:
    families = _contract()["ideal_refinement_sequences"]["axis_families"]
    for name, shift in (
        ("cell_centred_periodic_base", "sigma_h=0"),
        ("cell_centred_periodic_half_shift", "sigma_h=h/2"),
    ):
        periodic = families[name]
        assert periodic["N_constraint"] == "integer N>=3 with N->infinity"
        assert periodic["shift"] == shift
        assert periodic["graph"] == (
            "cycle_on_N_cells_with_exactly_one_wrapping_edge_(N-1,0)"
        )
        assert periodic["rates"] == (
            "q_(i,i+1)=q_(i,i-1)=d_y/h^2 and q_ii=-2*d_y/h^2"
        )
        assert periodic["cell_mass"] == "m_i=h/W"


def test_raw_tensor_product_and_one_global_box_gauge_are_exact() -> None:
    tensor = _contract()["tensor_mass_and_rate_contract"]
    assert tensor["raw_tensor_mass"] == (
        "tilde_m_ijk=nu_i^z*nu_j^r*h_y*"
        "exp(-Phi_z(x_i)-Phi_r(x_j))"
    )
    assert tensor["axis_mass_product"] == "m_ijk=m_i^z*m_j^r*m_k^y"
    assert tensor["edge_conductance"] == (
        "an edge parallel to one axis has that axis common conductance "
        "times the masses of the other two axes"
    )
    gauge = tensor["global_box_gauge"]
    assert gauge["scale"] == "g_(h,L)=M_L/sum_ijk_tilde_m_ijk"
    assert gauge["factorization"] == "g_(h,L)=g_h^z*g_h^r/W"
    assert gauge["mass_identity"] == "sum_ijk_pi_h_ijk=M_L"
    assert tensor["ideal_only_not_production_centres"] is True


def test_exact_map_algebra_and_alignment_specific_rho_orders_are_frozen() -> None:
    section = _contract()["identification_and_map_rates"]
    identities = section["exact_c0_identification_maps"]["exact_identities"]
    assert identities == {
        "A_h_J_h": "I",
        "J_h_A_h": "E_h_pi_weighted_cell_conditional_expectation",
        "J_h_P_h": "rho_h_pc*E_h",
        "P_h": "J_h_adjoint",
        "P_h_J_h": "diag(rho_i)",
        "P_h_relation_to_A_h": "P_h=diag(rho_i)*A_h",
    }
    rates = section["rate_contract"]
    assert rates["axis_rho_orders"]["cell_centred_reflecting_ou"] == (
        "max_i_abs(rho_i-1)=O(h^2)"
    )
    assert rates["axis_rho_orders"]["vertex_dual_uniform"] == (
        "max_i_abs(rho_i-1)=O(h)"
    )
    assert rates["axis_rho_orders"]["periodic_base_and_half_shift"] == (
        "rho_i=1 exactly"
    )
    nonclaims = section["exact_c0_identification_maps"]["nonclaims"]
    assert nonclaims["J_h_P_h_operator_norm_convergence_claimed"] is False


def test_killing_uses_physical_volume_not_pi_weighted_average() -> None:
    killing = _contract()["killing_average_contract"]
    assert killing["cell_average"] == (
        "V_(h,c,i)=physical_volume(C_i)^(-1)*integral_C_i_V_c_dx"
    )
    assert killing["weighted_pi_average_used"] is False
    assert "endpoint dual half volumes" in killing["cell_conventions"]
    assert "wrapped periodic segments" in killing["cell_conventions"]
    assert killing["reconstructed_multiplier"] == "K_h_pc_on_C_i=V_(h,c,i)/rho_i"


def test_twelve_current_rows_are_only_finite_alignment_anchors() -> None:
    anchors = _contract()["finite_anchor_bindings"]
    assert anchors["configuration_count"] == 12
    assert anchors["current_rows_are_h_to_zero_sequences"] is False
    assert anchors["each_row_is_one_finite_mesh_anchor"] is True
    assert anchors["refinement_requires_new_fixed_box_sequences"] is True
    assert anchors["alignment_counts_across_36_axes"] == {
        "cell_centred_periodic_base": 10,
        "cell_centred_periodic_half_shift": 2,
        "cell_centred_reflecting": 20,
        "vertex_centred_reflecting_dual": 4,
    }
    assert len(anchors["rows"]) == 12
    assert anchors["total_state_workload"] == 34_787_462


def test_every_promotion_and_production_gate_remains_false() -> None:
    claims = _contract()["claim_boundary"]
    assert claims == verifier.EXPECTED_CLAIMS
    assert all(value is False for value in claims.values())


def test_standalone_verifier_receipt_is_strictly_nonpromoting() -> None:
    receipt = verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert receipt["status"] == verifier.PASS_STATUS
    assert receipt["contract_sha256"] == verifier.EXPECTED_CONTRACT_SHA256
    assert receipt["finite_anchor_count"] == 12
    assert receipt["finite_anchors_are_refinement_sequences"] is False
    assert receipt["complete_c1"] is False
    assert receipt["production_bridge_proved"] is False
    assert receipt["release_eligible"] is False
    assert receipt["result_or_control_payload_read"] is False
    assert receipt["opened_source_paths"] == verifier.OPENED_SOURCE_PATHS
    assert receipt["opened_source_counts"] == verifier.OPENED_SOURCE_COUNTS
    assert _contract()["proof_bridge_boundary"] == verifier.EXPECTED_PROOF_BOUNDARY

