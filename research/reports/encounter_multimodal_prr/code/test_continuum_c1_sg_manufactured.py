from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import continuum_c1_sg_manufactured as fixture

REPORT = Path(__file__).resolve().parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c1_sg_manufactured_v2.json"
MOSCO_CANDIDATE = REPORT / "notes/continuum_c1_fixed_1d_free_ou_mosco_candidate.md"
CONTINUUM_PROGRAM = REPORT / "notes/continuum_research_program_v2.md"


def _load() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _hex(record: dict[str, str], key: str) -> float:
    return float.fromhex(record[key])


def test_published_artifact_is_exact_recomputation() -> None:
    expected = fixture.canonical_json_bytes(fixture.build_payload())
    assert ARTIFACT.read_bytes() == expected


def test_fixture_is_neutral_and_keeps_every_promotion_closed() -> None:
    payload = _load()
    assert payload["schema"] == fixture.SCHEMA
    assert payload["status"] == fixture.STATUS
    assert payload["sizes"] == list(fixture.SIZES)
    assert payload["claim_boundary"] == {
        "c1_mosco_proved": False,
        "c2_error_bound_proved": False,
        "control_or_budget_read": False,
        "fixed_1d_free_ideal_mosco_proved": False,
        "ideal_analytic_scheme_only": True,
        "manufactured_fixture_only": True,
        "positive_budget_scientific_values_read": False,
        "production_centre_mosco_proved": False,
        "release_eligible": False,
    }
    raw = ARTIFACT.read_text(encoding="utf-8").lower()
    for forbidden in ("control_weights", "peak_time", "root_interval", "basin_mass"):
        assert forbidden not in raw

    assert payload["alignment_scope"] == {
        "axis": "midpoint_z",
        "one_dimensional_rule": "cell_centred_reflecting_scharfetter_gummel",
        "periodic_axis_tested": False,
        "tensor_alignment_vector_frozen": False,
        "vertex_dual_tested": False,
    }
    assert payload["independent_formulae"]["density_ratio_cell_extrema"] == (
        "both_cell_endpoints_plus_interior_OU_mean_if_present"
    )


def test_fixture_projection_map_is_explicit_but_c1_map_choice_is_open() -> None:
    payload = _load()
    projection = payload["fixture_projection_map"]
    assert projection == {
        "A_h_J_h_exact_for_piecewise_constants": True,
        "c1_contract_map_choice_closed": False,
        "denominator": "integral_C_i_pi",
        "formula": "A_h[u]_i=(integral_C_i u*pi)/(integral_C_i pi)",
        "weighted_adjoint_error_controlled_by_cell_mass_ratio": True,
        "weighted_adjoint_exact": False,
    }
    assert payload["theorem_map_candidate"] == {
        "J_h_P_h_pointwise_strong_not_operator_norm": True,
        "P_h_J_h_formula": "diag(rho_i)",
        "c1_contract_adoption_complete": False,
        "exact_adjoint": True,
        "formula": "P_h_adj[u]_i=(integral_C_i u*pi)/m_i",
        "physical_cell_mass_preserved": True,
        "proposed_not_independently_accepted": True,
    }


def test_all_rows_separate_raw_interval_containment_from_open_gauge_link() -> None:
    payload = _load()
    for row in payload["rows"]:
        assert row["raw_stationary_mass_interval_containment"] is True
        assert row["raw_conductance_interval_containment"] is True
        assert row["gauged_stationary_mass_interval_containment"] is False
        assert row["gauged_conductance_interval_containment"] is False
        assert float.fromhex(row["gauge_mass_absolute_error_hex"]) == 0.0
        # The omitted Gaussian tail is below binary64 resolution for this box,
        # so the canonical float-hex export rounds the fixed-box mass to 1.
        assert 0.0 < float.fromhex(row["box_mass_hex"]) <= 1.0
        assert float.fromhex(row["density_ratio_min_hex"]) > 0.0
        assert float.fromhex(row["density_ratio_max_hex"]) >= 1.0


def test_constant_function_is_an_exact_structural_zero() -> None:
    payload = _load()
    for row in payload["rows"]:
        constant = row["functions"]["constant"]
        for key in (
            "continuum_energy_hex",
            "discrete_energy_hex",
            "energy_absolute_error_hex",
            "energy_relative_error_hex",
            "norm_identification_absolute_error_hex",
            "projection_l2_error_hex",
        ):
            assert float.fromhex(constant[key]) == 0.0
    assert payload["observed_last_pair_orders"]["functions"]["constant"] == {
        "energy_absolute_error": None,
        "norm_identification_absolute_error": None,
        "projection_l2_error": None,
    }


def test_linear_continuum_energy_matches_d_axis_times_box_mass() -> None:
    payload = _load()
    d_axis = float(fixture.DIFFUSION / 2)
    for row in payload["rows"]:
        observed = _hex(row["functions"]["linear"], "continuum_energy_hex")
        expected = d_axis * float.fromhex(row["box_mass_hex"])
        assert math.isclose(observed, expected, rel_tol=2e-15, abs_tol=0.0)


def test_nonconstant_errors_decrease_monotonically() -> None:
    payload = _load()
    density_errors = [float.fromhex(row["density_ratio_sup_error_hex"]) for row in payload["rows"]]
    assert all(fine < coarse for coarse, fine in zip(density_errors, density_errors[1:]))
    for name in set(fixture.POLYNOMIALS) - {"constant"}:
        for key in (
            "energy_absolute_error_hex",
            "norm_identification_absolute_error_hex",
            "projection_l2_error_hex",
        ):
            errors = [float.fromhex(row["functions"][name][key]) for row in payload["rows"]]
            assert all(0.0 < fine < coarse for coarse, fine in zip(errors, errors[1:]))


def test_last_pair_orders_separate_observed_rates_from_a_proof() -> None:
    payload = _load()
    orders = payload["observed_last_pair_orders"]
    assert 1.0 < orders["density_ratio_sup_error"] < 1.2
    assert 1.9 < orders["cell_mass_ratio_sup_error"] < 2.1
    assert 1.9 < orders["adjoint_map_ratio_sup_error"] < 2.1
    assert 1.9 < orders["ideal_edge_interpolant_ratio_sup_error"] < 2.1
    for name in set(fixture.POLYNOMIALS) - {"constant"}:
        record = orders["functions"][name]
        assert 1.95 < record["energy_absolute_error"] < 2.05
        assert 1.95 < record["norm_identification_absolute_error"] < 2.05
        assert 0.95 < record["projection_l2_error"] < 1.05


def test_finest_density_ratio_is_still_too_large_for_c1_promotion() -> None:
    payload = _load()
    finest = payload["rows"][-1]
    observed = float.fromhex(finest["density_ratio_sup_error_hex"])
    assert 0.1 < observed < 0.2
    assert payload["claim_boundary"]["c1_mosco_proved"] is False


def test_neumann_cubic_really_has_zero_endpoint_derivatives() -> None:
    coefficients = fixture.POLYNOMIALS["neumann_cubic"]
    derivative = fixture._poly_derivative(coefficients)
    for x in (fixture.LOWER, fixture.UPPER):
        y = x - fixture.MEAN
        value = sum(coefficient * y**power for power, coefficient in derivative.items())
        assert value == 0


def test_flat_sentinel_exposes_exact_generic_boundary_order() -> None:
    sentinel = _load()["flat_boundary_order_sentinel"]
    assert sentinel["sizes"] == list(fixture.FLAT_SENTINEL_SIZES)
    assert sentinel["exact_orders_under_uniform_halving"] == {
        "energy_gap": 1,
        "norm_squared_gap": 2,
        "projection_l2_error": 1,
    }
    for row in sentinel["rows"]:
        h = Fraction(row["h_exact"])
        assert row["geometry_and_reflection_exact"] is True
        assert row["interval_formulae_contained"] is True
        assert Fraction(row["discrete_energy_exact"]) == 1 - h / 2
        assert Fraction(row["energy_gap_exact"]) == h / 2
        assert Fraction(row["norm_gap_exact"]) == h**2 / 12
        assert Fraction(row["projection_l2_error_squared_exact"]) == h**2 / 12
        assert Fraction(row["quadratic_continuum_energy_exact"]) == Fraction(4, 3)
        assert Fraction(row["quadratic_discrete_energy_exact"]) == (
            Fraction(4, 3) - 2 * h + Fraction(2, 3) * h**2
        )
        assert Fraction(row["quadratic_energy_gap_exact"]) == 2 * h - Fraction(2, 3) * h**2
    reconstruction = sentinel["interpolant_reconstruction_sentinel"]
    h = Fraction(reconstruction["h_exact"])
    values = tuple(Fraction(value) for value in reconstruction["values"])
    jumps = tuple(
        values[index + 1] - values[index]
        for index in range(len(values) - 1)
    )
    density = Fraction(sentinel["continuum_density_exact"])
    diffusion = Fraction(sentinel["continuum_diffusion_exact"])
    energy = diffusion * density * sum((jump**2 for jump in jumps), Fraction(0)) / h
    norm_squared = density * h * sum((jump**2 for jump in jumps), Fraction(0)) / 12
    assert reconstruction["cells"] == 4
    assert reconstruction["formula"] == "norm_squared=(h^2/(12*d))*discrete_energy"
    assert energy == Fraction(reconstruction["discrete_energy_exact"])
    assert norm_squared == Fraction(reconstruction["reconstruction_l2_norm_squared_exact"])
    assert norm_squared == h**2 * energy / (12 * diffusion)


def test_wide_box_second_order_table_is_labelled_preasymptotic() -> None:
    payload = _load()
    boundary = payload["theory_boundary"]
    assert boundary["form_domain"] == "weighted_H1_no_Neumann_trace_constraint"
    assert boundary["generic_smooth_energy_asymptotic"].startswith("O(h)_")
    assert boundary["neumann_compatible_energy_asymptotic"].startswith("O(h^2)_")
    assert boundary["complete_c1_from_finite_tables"] is False
    coefficient = float.fromhex(payload["fixed_box"]["generic_linear_boundary_coefficient_hex"])
    assert 0.0 < coefficient < 1e-19


def test_uniform_map_and_edge_diagnostics_converge_without_promoting_c1() -> None:
    payload = _load()
    keys = (
        "cell_mass_ratio_sup_error_hex",
        "adjoint_map_ratio_sup_error_hex",
        "ideal_edge_interpolant_ratio_sup_error_hex",
    )
    for key in keys:
        errors = [float.fromhex(row[key]) for row in payload["rows"]]
        assert all(0.0 < fine < coarse for coarse, fine in zip(errors, errors[1:]))
    finest = payload["rows"][-1]
    assert float.fromhex(finest["cell_mass_ratio_sup_error_hex"]) < 0.003
    assert float.fromhex(finest["adjoint_map_ratio_sup_error_hex"]) < 0.003
    assert float.fromhex(finest["ideal_edge_interpolant_ratio_sup_error_hex"]) < 0.006
    assert payload["claim_boundary"]["fixed_1d_free_ideal_mosco_proved"] is False


def test_ideal_scheme_is_separated_from_nonreversible_production_centres() -> None:
    payload = _load()
    assert payload["scheme_boundary"] == {
        "gauged_ideal_form_values_contained_in_production_outward_intervals": False,
        "ideal_analytic_common_conductance_used_for_form": True,
        "production_gauge_linkage_proved": False,
        "production_binary64_centres_exactly_reversible": False,
        "production_centre_limit_claimed": False,
        "production_interval_width_belongs_to": "E_eval_not_Mosco_form",
        "raw_ungauged_axis_values_contained_in_production_outward_intervals": True,
    }
    for row in payload["rows"]:
        residual = float.fromhex(row["production_centre_balance_max_relative_residual_hex"])
        drift = float.fromhex(row["production_centre_recursive_mass_shape_drift_hex"])
        assert 0.0 < residual < 1e-14
        assert 0.0 < drift < 1e-12
    assert payload["claim_boundary"]["production_centre_mosco_proved"] is False


def test_living_theory_notes_freeze_map_and_ideal_scheme_without_promotion() -> None:
    candidate = MOSCO_CANDIDATE.read_text(encoding="utf-8")
    program = CONTINUUM_PROGRAM.read_text(encoding="utf-8")
    assert "All Hilbert spaces and forms in this note are real" in candidate
    assert "ideal analytic" in candidate
    assert "P_h=J_h^*" in candidate
    assert "current production builder stores outward binary64 intervals" in candidate
    assert "containment check is not a production bridge" in candidate
    assert "COMPLETE C1 FALSE" in candidate
    assert "exact-adjoint map" in program
    assert "(P_hu)_i=\\pi_{h,i}^{-1}" in program
    assert "an evaluation expansion point, not the object" in program
    assert "production gauge/application bridge is currently open" in program
    assert "complete fixed-L Mosco/strong-resolvent theorem  = OPEN C1" in program
