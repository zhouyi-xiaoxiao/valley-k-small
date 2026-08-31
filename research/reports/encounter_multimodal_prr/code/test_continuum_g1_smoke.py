from __future__ import annotations

from dataclasses import replace

import continuum_g1_smoke as g1
import numpy as np
import pytest


def test_bernoulli_function_and_sg_equilibrium() -> None:
    values = g1.bernoulli_function(np.asarray((-1.0e-8, 0.0, 1.0e-8)))
    assert np.allclose(values, (1.000000005, 1.0, 0.999999995), atol=2.0e-15)
    edges = np.linspace(-1.0, 2.0, 41)
    diffusion = 0.2
    gamma = 0.3
    mean = 0.4
    generator = g1.sg_reflecting_generator(
        edges,
        diffusion=diffusion,
        drift=lambda x: -gamma * (x - mean),
    )
    centres = 0.5 * (edges[:-1] + edges[1:])
    equilibrium = np.exp(-gamma * (centres - mean) ** 2 / (2.0 * diffusion))
    equilibrium /= equilibrium.sum()
    assert np.max(np.abs(generator.sum(axis=1))) < 1.0e-12
    assert np.linalg.norm(generator.T @ equilibrium, ord=np.inf) < 2.0e-13


def test_bump_contact_integrals_and_independent_reference() -> None:
    edges = np.linspace(-0.5, 0.5, 38)
    masses, error_estimate = g1.bump_cell_masses(
        edges,
        centre=0.0,
        half_width=0.08,
        period=1.0,
    )
    assert sum(masses) == pytest.approx(1.0, abs=2.0e-13)
    assert error_estimate < 1.0e-11
    parallel = np.linspace(-0.7, 0.7, 32)
    transverse = np.linspace(-0.5, 0.5, 30)
    fractions, area, area_error_estimate = g1.contact_cell_fractions(
        parallel,
        transverse,
        radius=0.16,
    )
    diagnostics = g1.contact_reference_diagnostics(
        parallel,
        transverse,
        fractions,
        radius=0.16,
    )
    assert np.min(fractions) >= 0.0
    assert np.max(fractions) <= 1.0
    assert area == pytest.approx(np.pi * 0.16**2, rel=2.0e-12)
    assert area_error_estimate < 1.0e-11
    assert diagnostics["maximum_per_cell_fraction_error"] < 2.0e-12
    assert diagnostics["relative_l1_area_error"] < 2.0e-12
    assert max(abs(value) for value in diagnostics["centroid"]) < 1.0e-13
    assert diagnostics["maximum_parallel_reflection_error"] < 1.0e-12
    assert diagnostics["maximum_perpendicular_reflection_error"] < 1.0e-12


def test_wrapped_bump_crosses_the_torus_cut() -> None:
    edges = np.linspace(-0.5, 0.5, 101)
    centres = 0.5 * (edges[:-1] + edges[1:])
    masses, _ = g1.bump_cell_masses(
        edges,
        centre=0.495,
        half_width=0.02,
        period=1.0,
    )
    resultant = np.sum(masses * np.exp(2.0j * np.pi * centres))
    circular_mean = float(np.angle(resultant) / (2.0 * np.pi))
    circular_error = (circular_mean - 0.495 + 0.5) % 1.0 - 0.5
    diagnostics = g1.bump_profile_reference_diagnostics(
        edges,
        masses,
        centre=0.495,
        half_width=0.02,
        period=1.0,
    )
    assert np.sum(masses) == pytest.approx(1.0, abs=2.0e-13)
    assert circular_error == pytest.approx(0.0, abs=2.0e-13)
    assert diagnostics["maximum_per_cell_mass_error"] < 2.0e-12
    assert diagnostics["relative_l1_mass_error"] < 2.0e-12


def test_bump_reference_does_not_call_production_integrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    edges = np.linspace(-0.5, 0.5, 63)
    observed = g1.bump_cell_masses_reference(
        edges,
        centre=0.48,
        half_width=0.08,
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("independent reference called production bump_cell_masses")

    monkeypatch.setattr(g1, "bump_cell_masses", forbidden)
    diagnostics = g1.bump_profile_reference_diagnostics(
        edges,
        observed,
        centre=0.48,
        half_width=0.08,
    )
    assert diagnostics["maximum_per_cell_mass_error"] == pytest.approx(0.0)
    assert diagnostics["relative_l1_mass_error"] == pytest.approx(0.0)


def test_contact_helpers_reject_nonuniform_edges() -> None:
    with pytest.raises(ValueError, match="uniform"):
        g1.contact_cell_fractions(
            np.asarray((-0.3, -0.1, 0.0, 0.3)),
            np.linspace(-0.5, 0.5, 8),
            radius=0.16,
        )


def test_boundary_layer_mask_is_a_union_without_corner_duplication() -> None:
    mask = g1.boundary_layer_union_mask(5, 6, 7, layers=2)
    expected_count = 5 * 6 * 7 - (5 - 4) * (6 - 4) * 7
    assert np.count_nonzero(mask) == expected_count
    corner_mass = np.zeros((5, 6, 7), dtype=float)
    corner_mass[0, 0, 0] = 1.0
    assert np.sum(corner_mass[mask]) == 1.0


def test_full_installed_budget_is_independent_of_transverse_width() -> None:
    parameters = replace(g1.PilotParameters(), transverse_width=2.0)
    grid = g1.QuotientGrid2D(
        midpoint_cells=7,
        relative_parallel_cells=7,
        relative_perp_cells=7,
        midpoint_bounds=parameters.midpoint_bounds,
        relative_parallel_bounds=parameters.relative_parallel_bounds,
        transverse_width=parameters.transverse_width,
    )
    model = g1.build_model(grid, theta=0.5, parameters=parameters)
    per_transverse_integral = np.sum(model.kappa) * grid.midpoint_spacing
    assert model.physical_budget == pytest.approx(parameters.installed_budget, rel=2.0e-13)
    assert per_transverse_integral == pytest.approx(
        parameters.installed_budget / parameters.transverse_width,
        rel=2.0e-13,
    )


@pytest.fixture(scope="module")
def payload() -> dict:
    return g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=20.0,
        time_points=61,
    )


def test_quotient_operator_and_mass_balance(payload: dict) -> None:
    assert payload["status"] == "PASS"
    assert all(payload["gates"].values())
    assert payload["geometry_and_budget"]["initial_contact_mass"] == 0.0
    assert payload["operator"]["minimum_free_offdiagonal"] >= 0.0
    assert payload["operator"]["free_row_error"] < 1.0e-12
    assert payload["operator"]["killed_mass_balance_error"] < 1.0e-12
    assert payload["operator"]["tensor_killing_max_abs_error"] == 0.0
    assert payload["solve"]["differential_mass_balance_error"] < 1.0e-10


def test_foundation_diagnostics_are_machine_readable(payload: dict) -> None:
    assert payload["schema_version"] == 3
    assert payload["stage"] == "G1a_pre_fold_foundations"
    assert payload["continuum_verified"] is False
    budget = payload["geometry_and_budget"]["budget_diagnostics"]
    assert max(budget["patch_integral_absolute_errors"]) < 1.0e-12
    assert max(budget["patch_integral_error_estimates"]) < 1.0e-11
    assert max(budget["endpoint_budget_relative_errors"]) < 1.0e-12
    assert max(budget["endpoint_weight_sum_errors"]) < 1.0e-14
    assert min(budget["endpoint_component_minima"]) >= 0.0
    assert min(budget["endpoint_kappa_minima"]) >= 0.0
    assert min(budget["endpoint_killing_minima"]) >= 0.0
    assert budget["affine_line_weight_nonnegativity_certified"] is True
    assert budget["scaled_budget_derivative_error"] < 1.0e-12
    profiles = payload["geometry_and_budget"]["bump_profile_reference"]
    assert {profile["label"] for profile in profiles["catalyst_profiles"]} == {
        "near",
        "middle",
        "far",
    }
    assert {profile["label"] for profile in profiles["initial_marginals"]} == {
        "midpoint",
        "relative_parallel",
        "relative_perpendicular_wrapped",
    }
    for profile in profiles["catalyst_profiles"] + profiles["initial_marginals"]:
        assert profile["zeroth_moment_error"] < 1.0e-12
        assert abs(profile["first_moment_error"]) <= profile["first_moment_tolerance"]
        assert profile["maximum_per_cell_mass_error"] < 2.0e-12
        assert profile["relative_l1_mass_error"] < 2.0e-12
    moments = payload["geometry_and_budget"]["initial_reconstruction"]
    for coordinate, error in moments["errors"].items():
        assert abs(error) <= moments["tolerances"][coordinate]
    reference = payload["reference_checks"]
    assert reference["tensor_order_sentinel"] is True
    assert reference["dense_sparse_state_relative_error"] < 1.0e-11
    assert reference["one_step_two_half_step_relative_error"] < 1.0e-11
    assert max(reference["jet_relative_errors"]) < 1.0e-6
    rates = payload["operator"]["transport_rate_reference"]
    assert rates["sample_count"] == 12
    assert rates["maximum_absolute_rate_error"] < 1.0e-12
    assert rates["maximum_relative_rate_error"] < 1.0e-12


def test_frozen_configuration_is_persisted(payload: dict) -> None:
    frozen = payload["frozen_configuration"]
    assert frozen["physical_parameters"] == payload["parameters"]
    assert frozen["physical_parameters"]["patch_centres"] == (0.48, 0.67, 0.86)
    assert frozen["physical_parameters"]["patch_half_widths"] == (0.08, 0.08, 0.08)
    assert frozen["control_endpoints"]["lower_weights"] == pytest.approx(g1.LOWER_WEIGHTS)
    assert frozen["control_endpoints"]["upper_weights"] == pytest.approx(g1.UPPER_WEIGHTS)
    assert frozen["box"] == {
        "midpoint_bounds": [-0.25, 1.85],
        "relative_parallel_bounds": [-1.8, 1.8],
        "relative_perpendicular_bounds": [-0.5, 0.5],
    }
    assert frozen["grid_shape"] == [17, 19, 17]
    assert frozen["control_theta"] == 0.5
    assert frozen["time_window"] == [0.0, 20.0]
    assert frozen["time_points"] == 61


def test_public_foundation_api_is_the_payload_source() -> None:
    pars = g1.PilotParameters()
    grid = g1.QuotientGrid2D(
        midpoint_cells=9,
        relative_parallel_cells=9,
        relative_perp_cells=9,
        midpoint_bounds=pars.midpoint_bounds,
        relative_parallel_bounds=pars.relative_parallel_bounds,
        transverse_width=pars.transverse_width,
    )
    model = g1.build_model(grid, theta=0.5, parameters=pars)
    diagnostics = g1.foundation_diagnostics(model)
    gates = g1.foundation_gates(model, diagnostics)
    assert all(gates.values())
    assert diagnostics["bump_profile_reference"]["catalyst_profiles"]
    assert diagnostics["transport_rate_reference"]["sample_count"] == 12


def test_contact_roll_mutation_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    original = g1.contact_cell_fractions

    def shifted(*args, **kwargs):
        fractions, area, error_estimate = original(*args, **kwargs)
        return np.roll(fractions, 3, axis=1), area, error_estimate

    monkeypatch.setattr(g1, "contact_cell_fractions", shifted)
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert not mutated["gates"]["contact_reference_per_cell"]
    assert not mutated["gates"]["contact_centroid"]


def test_patch_normalization_bias_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = g1.bump_cell_masses

    def biased(edges, *, centre, half_width, period=None):
        masses, error_estimate = original(
            edges,
            centre=centre,
            half_width=half_width,
            period=period,
        )
        if abs(half_width - 0.08) < 1.0e-14 and abs(centre - 0.48) < 1.0e-14:
            masses = 1.2 * masses
        if abs(half_width - 0.08) < 1.0e-14 and abs(centre - 0.86) < 1.0e-14:
            masses = 0.8 * masses
        return masses, error_estimate

    monkeypatch.setattr(g1, "bump_cell_masses", biased)
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert mutated["gates"]["physical_budget"]
    assert not mutated["gates"]["patchwise_integrals"]
    assert not mutated["gates"]["endpoint_physical_budgets"]


def test_all_patch_translation_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = g1.bump_cell_masses

    def translated(edges, *, centre, half_width, period=None):
        masses, error_estimate = original(
            edges,
            centre=centre,
            half_width=half_width,
            period=period,
        )
        if abs(half_width - 0.08) < 1.0e-14 and period is None:
            masses = np.roll(masses, 2)
        return masses, error_estimate

    monkeypatch.setattr(g1, "bump_cell_masses", translated)
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert mutated["gates"]["patchwise_integrals"]
    assert not mutated["gates"]["patch_profile_first_moments"]
    assert not mutated["gates"]["patch_profile_reference_per_cell"]
    assert not mutated["gates"]["patch_profile_reference_l1"]


def test_negative_unit_sum_endpoint_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(g1, "LOWER_WEIGHTS", np.asarray((-0.04, 0.34, 0.70)))
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert mutated["gates"]["endpoint_weight_sums"]
    assert not mutated["gates"]["endpoint_weight_nonnegative"]
    assert not mutated["gates"]["endpoint_kappa_nonnegative"]
    assert not mutated["gates"]["endpoint_killing_nonnegative"]
    assert not mutated["gates"]["affine_control_line_certified"]
    assert mutated["gates"]["current_kappa_killing_nonnegative"]


def test_wrapped_initial_translation_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = g1.bump_cell_masses

    def translated(edges, *, centre, half_width, period=None):
        masses, error_estimate = original(
            edges,
            centre=centre,
            half_width=half_width,
            period=period,
        )
        if period is not None:
            masses = np.roll(masses, 2)
        return masses, error_estimate

    monkeypatch.setattr(g1, "bump_cell_masses", translated)
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert mutated["gates"]["initial_mass"]
    assert not mutated["gates"]["initial_profile_first_moments"]
    assert not mutated["gates"]["initial_profile_reference_per_cell"]
    assert not mutated["gates"]["initial_profile_reference_l1"]


def test_transport_diffusion_swap_mutation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    g1.small_reference_diagnostics()
    original = g1.sg_reflecting_generator
    call_count = 0

    def swapped(edges, *, diffusion, drift):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            diffusion = 2.0 * g1.PilotParameters().diffusion
        elif call_count == 2:
            diffusion = 0.5 * g1.PilotParameters().diffusion
        return original(edges, diffusion=diffusion, drift=drift)

    monkeypatch.setattr(g1, "sg_reflecting_generator", swapped)
    mutated = g1.build_payload(
        midpoint_cells=17,
        relative_parallel_cells=19,
        relative_perp_cells=17,
        theta=0.5,
        time_stop=0.2,
        time_points=3,
    )
    assert mutated["status"] == "FAIL"
    assert not mutated["gates"]["main_transport_rate_reference"]


def test_smoke_result_does_not_claim_a_fold(payload: dict) -> None:
    scope = payload["claim_scope"].lower()
    assert "smoke only" in scope
    assert "not a continuum fold" in scope
    assert "cusp" in scope
    assert "trimodality" in scope
    assert payload["limitations"]
