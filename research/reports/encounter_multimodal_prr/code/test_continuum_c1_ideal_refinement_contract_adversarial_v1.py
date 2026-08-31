from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import validate_continuum_c0_model_contract_candidate_v2 as c0
import validate_continuum_c1_ideal_refinement_contract_candidate_v1 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = (
    REPORT
    / "artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json"
)


def _candidate() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _reject(candidate: dict[str, object], code: str) -> None:
    payload = c0.canonical_json_bytes(candidate)
    with pytest.raises(verifier.C1RefinementHold) as caught:
        verifier.verify_contract_bytes(payload)
    assert caught.value.code == code


@pytest.mark.parametrize("claim", sorted(verifier.EXPECTED_CLAIMS))
def test_every_false_promotion_claim_rejects_true(claim: str) -> None:
    candidate = _candidate()
    candidate["claim_boundary"][claim] = True
    _reject(candidate, verifier.HOLD_CLAIMS)


def test_frozen_source_hash_mutation_is_rejected() -> None:
    candidate = _candidate()
    candidate["frozen_sources"]["theorem_note"]["sha256"] = "0" * 64
    _reject(candidate, verifier.HOLD_SOURCES)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("D", "D=0"),
        ("W", "W=0"),
        ("gamma", "gamma=0"),
        ("midpoint_density_normalizer", "C_z=0"),
        ("midpoint_interval_nondegenerate", "ell_z=r_z"),
        ("relative_parallel_density_normalizer", "C_r=0"),
        ("relative_parallel_interval_nondegenerate", "ell_r=r_r"),
    ],
)
def test_fixed_box_positivity_and_nondegeneracy_are_semantically_checked(
    field: str,
    replacement: str,
) -> None:
    candidate = _candidate()
    candidate["fixed_box"]["parameter_preconditions"][field] = replacement
    _reject(candidate, verifier.HOLD_REFINEMENT)


@pytest.mark.parametrize(
    ("axis", "field", "replacement"),
    [
        ("midpoint", "diffusion", "d_z=2*D"),
        ("relative_parallel", "potential", "Phi_r=0"),
        ("relative_perpendicular", "diffusion", "d_y=D/2"),
    ],
)
def test_complete_axis_parameter_substitution_is_semantically_checked(
    axis: str,
    field: str,
    replacement: str,
) -> None:
    candidate = _candidate()
    candidate["fixed_box"]["substitution"][axis][field] = replacement
    _reject(candidate, verifier.HOLD_REFINEMENT)


def test_finite_anchor_cannot_be_promoted_to_refinement_sequence() -> None:
    candidate = _candidate()
    candidate["finite_anchor_bindings"]["current_rows_are_h_to_zero_sequences"] = True
    _reject(candidate, verifier.HOLD_ANCHORS)


def test_finite_anchor_size_or_alignment_mutation_is_rejected() -> None:
    for field, value in (
        ("axis_sizes", {"midpoint": 1}),
        ("axis_alignments", {"midpoint": "forged"}),
    ):
        candidate = _candidate()
        candidate["finite_anchor_bindings"]["rows"][0][field] = value
        _reject(candidate, verifier.HOLD_ANCHORS)


@pytest.mark.parametrize(
    ("family", "replacement"),
    [
        ("cell_centred_reflecting_ou", "integer N>=3 with N fixed"),
        ("vertex_centred_reflecting_dual_ou", "integer N>=2 with N fixed"),
    ],
)
def test_nonperiodic_family_must_refine_n_to_infinity(
    family: str,
    replacement: str,
) -> None:
    candidate = _candidate()
    candidate["ideal_refinement_sequences"]["axis_families"][family][
        "N_constraint"
    ] = replacement
    _reject(candidate, verifier.HOLD_REFINEMENT)


@pytest.mark.parametrize(
    "family",
    [
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
        "cell_centred_reflecting_ou",
        "vertex_centred_reflecting_dual_ou",
    ],
)
def test_every_axis_cell_formula_is_semantically_checked(family: str) -> None:
    candidate = _candidate()
    candidate["ideal_refinement_sequences"]["axis_families"][family][
        "cell_formula"
    ] = "forged_cell_partition"
    _reject(candidate, verifier.HOLD_REFINEMENT)


def test_vertex_half_volume_cannot_be_replaced_by_equal_volume() -> None:
    candidate = _candidate()
    vertex = candidate["ideal_refinement_sequences"]["axis_families"][
        "vertex_centred_reflecting_dual_ou"
    ]
    vertex["volumes"] = "nu_i=h for every i"
    _reject(candidate, verifier.HOLD_RATES)


def test_vertex_rate_cannot_delete_nu_i_denominator() -> None:
    candidate = _candidate()
    vertex = candidate["ideal_refinement_sequences"]["axis_families"][
        "vertex_centred_reflecting_dual_ou"
    ]
    vertex["rate_contract"]["forward_rate"] = (
        "q_(i,i+1)=d/h^2*B(Phi_(i+1)-Phi_i)"
    )
    _reject(candidate, verifier.HOLD_RATES)


@pytest.mark.parametrize(
    "family",
    ["cell_centred_periodic_base", "cell_centred_periodic_half_shift"],
)
def test_periodic_n_less_than_three_is_rejected(family: str) -> None:
    candidate = _candidate()
    candidate["ideal_refinement_sequences"]["axis_families"][family][
        "N_constraint"
    ] = "integer N>=2 with N->infinity"
    _reject(candidate, verifier.HOLD_REFINEMENT)


@pytest.mark.parametrize(
    "family",
    ["cell_centred_periodic_base", "cell_centred_periodic_half_shift"],
)
def test_periodic_wrapping_edge_cannot_be_removed(family: str) -> None:
    candidate = _candidate()
    candidate["ideal_refinement_sequences"]["axis_families"][family][
        "graph"
    ] = "path_graph_without_wrapping_edge"
    _reject(candidate, verifier.HOLD_RATES)


def test_periodic_half_shift_cannot_masquerade_as_base() -> None:
    candidate = _candidate()
    half = candidate["ideal_refinement_sequences"]["axis_families"][
        "cell_centred_periodic_half_shift"
    ]
    half["shift"] = "sigma_h=0"
    _reject(candidate, verifier.HOLD_REFINEMENT)


def test_periodic_rate_or_mass_mutation_is_rejected() -> None:
    for field, value in (
        ("rates", "q=d_y/h"),
        ("cell_mass", "m_i=1/N after hidden unit normalization"),
    ):
        candidate = _candidate()
        periodic = candidate["ideal_refinement_sequences"]["axis_families"][
            "cell_centred_periodic_base"
        ]
        periodic[field] = value
        _reject(candidate, verifier.HOLD_RATES)


def test_raw_tensor_mass_cannot_drop_dual_volumes() -> None:
    candidate = _candidate()
    candidate["tensor_mass_and_rate_contract"]["raw_tensor_mass"] = (
        "tilde_m_ijk=exp(-Phi_z(x_i)-Phi_r(x_j))"
    )
    _reject(candidate, verifier.HOLD_TENSOR)


def test_tensor_edge_conductance_factorization_is_semantically_checked() -> None:
    candidate = _candidate()
    candidate["tensor_mass_and_rate_contract"]["edge_conductance"] = (
        "axis conductance without transverse masses"
    )
    _reject(candidate, verifier.HOLD_TENSOR)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("scale", "g_(h,L)=1/sum_ijk_tilde_m_ijk"),
        ("factorization", "g_(h,L)=g_h^z*g_h^r"),
        ("mass_identity", "sum_ijk_pi_h_ijk=1"),
    ],
)
def test_global_box_gauge_mutations_are_rejected(
    field: str,
    replacement: str,
) -> None:
    candidate = _candidate()
    candidate["tensor_mass_and_rate_contract"]["global_box_gauge"][field] = (
        replacement
    )
    _reject(candidate, verifier.HOLD_TENSOR)


def test_exact_map_denominator_mutation_is_rejected() -> None:
    candidate = _candidate()
    maps = candidate["identification_and_map_rates"][
        "exact_c0_identification_maps"
    ]
    maps["P_h"]["denominator"] = "M_i_pi"
    _reject(candidate, verifier.HOLD_MAPS)


def test_false_operator_norm_map_promotion_is_rejected() -> None:
    candidate = _candidate()
    maps = candidate["identification_and_map_rates"][
        "exact_c0_identification_maps"
    ]
    maps["nonclaims"]["J_h_P_h_operator_norm_convergence_claimed"] = True
    _reject(candidate, verifier.HOLD_MAPS)


def test_vertex_rho_order_cannot_be_promoted_to_second_order() -> None:
    candidate = _candidate()
    rate = candidate["identification_and_map_rates"]["rate_contract"]
    rate["axis_rho_orders"]["vertex_dual_uniform"] = (
        "max_i_abs(rho_i-1)=O(h^2)"
    )
    _reject(candidate, verifier.HOLD_MAPS)


def test_physical_volume_killing_average_cannot_become_pi_weighted() -> None:
    candidate = _candidate()
    killing = candidate["killing_average_contract"]
    killing["cell_average"] = "integral_C_i_V_c*pi_dx/integral_C_i_pi_dx"
    killing["weighted_pi_average_used"] = True
    _reject(candidate, verifier.HOLD_KILLING)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("quantitative_error_bound_supplied", True),
        ("bounded_killing_perturbation", "accepted_complete_C1"),
        ("free_tensor_route", "accepted_generalized_Mosco"),
        ("functional_calculus", "accepted_without_delta_h_or_resolvent_hypotheses"),
    ],
)
def test_proof_candidate_cannot_be_silently_promoted(
    field: str,
    replacement: object,
) -> None:
    candidate = _candidate()
    candidate["proof_bridge_boundary"][field] = replacement
    _reject(candidate, verifier.HOLD_PROOF)


def test_injected_forbidden_payload_path_is_rejected_before_schema() -> None:
    candidate = _candidate()
    candidate["source_policy"]["forbidden_probe"] = (
        "scratch/results/positive_result.json"
    )
    _reject(candidate, verifier.HOLD_RESULT_BLINDNESS)


def test_noncanonical_duplicate_nonfinite_and_deep_json_are_encoding_holds() -> None:
    raw = CONTRACT.read_bytes()
    attacks = (
        raw.replace(b"{\n", b"{ \n", 1),
        raw.replace(b"{\n", b'{\n  "schema": "duplicate",\n', 1),
        raw.replace(b'"configuration_count": 12', b'"configuration_count": NaN', 1),
        b'{"nested":' + b"[" * 2_000 + b"0" + b"]" * 2_000 + b"}\n",
    )
    for attacked in attacks:
        with pytest.raises(verifier.C1RefinementHold) as caught:
            verifier.verify_contract_bytes(attacked)
        assert caught.value.code == verifier.HOLD_ENCODING


def test_direct_bytes_entrypoint_enforces_size_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(verifier.c0, "MAX_FILE_BYTES", 8)
    with pytest.raises(verifier.C1RefinementHold) as caught:
        verifier.verify_contract_bytes(b'{"x":"123456789"}\n')
    assert caught.value.code == verifier.HOLD_ENCODING


def test_fixed_box_domain_change_has_semantic_refinement_hold() -> None:
    candidate = copy.deepcopy(_candidate())
    candidate["fixed_box"]["domain"] = "forged_domain"
    _reject(candidate, verifier.HOLD_REFINEMENT)
