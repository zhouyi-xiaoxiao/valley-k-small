from __future__ import annotations

import json
from pathlib import Path

import continuum_weak_budget_design as design
import numpy as np
import pytest


def test_manifest_is_explicitly_result_informed_and_fail_closed() -> None:
    manifest = design.load_json(design.MANIFEST)
    assert manifest["evidence_timing"] == (
        "RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY"
    )
    assert manifest["required_claim_flags"] == {
        "continuum_verified": False,
        "project_gate_passed": False,
        "finite_B_Doi_cusp_verified": False,
    }
    excluded = manifest["known_before_freeze"][
        "geometry_redesign_scratch_excluded_from_artifact_claim"
    ]
    assert excluded["evidence_status"].startswith("UNFROZEN_RESULT_INFORMED_SCRATCH")


def test_leibniz_channels_through_fourth_order() -> None:
    times = np.asarray((0.1, 0.7, 1.4))
    rates = np.asarray((0.3, -0.8, 1.2))
    relative_rate = -0.4
    midpoint = np.empty((5, len(times), 3))
    relative = np.empty((5, len(times)))
    for order in range(5):
        midpoint[order] = np.exp(times[:, None] * rates[None, :]) * rates[None, :] ** order
        relative[order] = np.exp(relative_rate * times) * relative_rate**order
    observed = design.leibniz_channels(midpoint, relative)
    total_rates = rates + relative_rate
    for order in range(5):
        expected = np.exp(times[:, None] * total_rates[None, :]) * total_rates[None, :] ** order
        assert observed[order] == pytest.approx(expected, rel=2.0e-14, abs=2.0e-14)


def test_simplex_enumeration_is_complete_and_exact() -> None:
    weights = design.simplex_weights(100)
    assert weights.shape == (5151, 3)
    assert np.min(weights) == 0.0
    assert np.max(weights) == 1.0
    assert np.sum(weights, axis=1) == pytest.approx(np.ones(5151), abs=2.0e-15)
    assert len({tuple(row) for row in weights.tolist()}) == 5151


def test_sampled_mode_counter_distinguishes_one_and_two_modes() -> None:
    times = np.linspace(0.0, 8.0, 1601)
    one_density = np.exp(-0.5 * (times - 3.0) ** 2)
    one_derivative = -(times - 3.0) * one_density
    one = design.sampled_mode_count(
        one_density,
        one_derivative,
        times,
        minimum_time=0.5,
        relative_density_floor=1.0e-12,
        derivative_zero_relative_tolerance=5.0e-13,
    )
    two_density = np.exp(-4.0 * (times - 2.0) ** 2) + 0.8 * np.exp(-4.0 * (times - 5.0) ** 2)
    two_derivative = -8.0 * (times - 2.0) * np.exp(-4.0 * (times - 2.0) ** 2) - 6.4 * (
        times - 5.0
    ) * np.exp(-4.0 * (times - 5.0) ** 2)
    two = design.sampled_mode_count(
        two_density,
        two_derivative,
        times,
        minimum_time=0.5,
        relative_density_floor=1.0e-12,
        derivative_zero_relative_tolerance=5.0e-13,
    )
    assert one[0:2] == (1, 0)
    assert two[0:2] == (2, 1)


def test_result_artifact_reproduces_only_the_declared_design_claim() -> None:
    payload = json.loads(Path(design.OUTPUT).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_RESULT_INFORMED_WEAK_BUDGET_DESIGN_DIAGNOSTIC"
    assert payload["evidence_timing"] == (
        "RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY"
    )
    assert payload["continuum_verified"] is False
    assert payload["project_gate_passed"] is False
    assert payload["finite_B_Doi_cusp_verified"] is False
    cusp = payload["cusp_reproduction"]
    assert cusp["cusp_time"] == pytest.approx(9.4478, abs=5.0e-3)
    assert cusp["weights"] == pytest.approx([0.3441, 0.2642, 0.3916], abs=5.0e-3)
    assert min(cusp["weights"]) > 0.0
    assert max(cusp["scaled_derivative_residuals_orders_1_to_3"]) < 1.0e-8
    assert cusp["unfolding"]["rank"] == 2
    inward = payload["normal_form_inward_check"]
    assert inward["root_count"] == 3
    assert inward["topology"] == ["maximum", "minimum", "maximum"]
    assert payload["simplex_screen"]["control_count"] == 5151
    assert payload["simplex_screen"]["maximum_sampled_mode_count"] == 2
    assert all(payload["gates"].values())
