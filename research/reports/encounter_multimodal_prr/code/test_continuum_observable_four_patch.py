from __future__ import annotations

import json
from pathlib import Path

import continuum_observable_four_patch as design
import numpy as np
import pytest


def test_normalized_bump_rules_are_probability_rules() -> None:
    for order in (72, 104, 136):
        nodes, weights = design.normalized_bump_rule(order)
        assert len(nodes) == len(weights) == order
        assert np.all(np.diff(nodes) > 0.0)
        assert np.min(weights) >= 0.0
        assert np.count_nonzero(weights) >= order - 2
        assert np.sum(weights) == pytest.approx(1.0, abs=3.0e-13)


def test_real_ou_first_derivative_matches_value_difference() -> None:
    times = np.asarray((2.0, 7.0, 15.0))
    targets = np.asarray((-0.2, 0.1, 0.4))
    starts = np.asarray((-0.35, -0.33))
    density, derivative = design.ou_density_and_first_derivative(
        times,
        targets,
        starts,
        diffusion_coefficient=0.004,
        stiffness=0.1,
        mean=0.0,
    )
    step = 2.0e-5
    plus = np.real(
        design.ou_transition_density(
            times + step,
            targets,
            starts,
            diffusion_coefficient=0.004,
            stiffness=0.1,
            mean=0.0,
        )
    )
    minus = np.real(
        design.ou_transition_density(
            times - step,
            targets,
            starts,
            diffusion_coefficient=0.004,
            stiffness=0.1,
            mean=0.0,
        )
    )
    assert density.shape == derivative.shape == plus.shape
    assert derivative == pytest.approx(
        (plus - minus) / (2.0 * step),
        rel=3.0e-9,
        abs=2.0e-10,
    )


def test_affine_cusp_matrix_has_the_declared_slice_null_vector() -> None:
    weights = np.asarray((0.28, 0.20, 0.25, 0.27))
    jets = np.zeros((5, 4))
    jets[0] = (0.8, 1.0, 1.2, 1.4)
    jets[1:4, :3] = np.asarray(
        (
            (0.3, -0.8, 0.2),
            (-0.4, 0.1, 0.7),
            (0.5, 0.9, -0.6),
        )
    )
    jets[1:4, 3] = -(jets[1:4, :3] @ weights[:3]) / weights[3]
    matrix = design.affine_cusp_matrix(jets, weights[0])
    affine_unknown = np.asarray((weights[1], weights[2], 1.0))
    assert matrix @ affine_unknown == pytest.approx(np.zeros(3), abs=2.0e-15)
    assert design.row_normalized_determinant(matrix) == pytest.approx(0.0, abs=2.0e-15)


def _fake_structure(
    *,
    minimum_weight: float,
    valley_margin: float,
    peak_ratio: float,
) -> dict[str, object]:
    return {
        "minimum_weight": minimum_weight,
        "worst_valley_margin_to_0p85": valley_margin,
        "peak_minimum_to_maximum_ratio": peak_ratio,
    }


def test_selection_priority_is_lexicographic_and_deterministic() -> None:
    candidates = [
        {
            "eligible": True,
            "step": 0.12,
            "stationary_structure": _fake_structure(
                minimum_weight=0.10,
                valley_margin=0.20,
                peak_ratio=0.9,
            ),
        },
        {
            "eligible": True,
            "step": 0.11,
            "stationary_structure": _fake_structure(
                minimum_weight=0.11,
                valley_margin=0.01,
                peak_ratio=0.2,
            ),
        },
    ]
    assert design.select_candidate(candidates)["step"] == 0.11
    candidates.extend(
        [
            {
                "eligible": True,
                "step": 0.10,
                "stationary_structure": _fake_structure(
                    minimum_weight=0.11,
                    valley_margin=0.02,
                    peak_ratio=0.2,
                ),
            },
            {
                "eligible": True,
                "step": 0.09,
                "stationary_structure": _fake_structure(
                    minimum_weight=0.11,
                    valley_margin=0.02,
                    peak_ratio=0.3,
                ),
            },
            {
                "eligible": True,
                "step": 0.08,
                "stationary_structure": _fake_structure(
                    minimum_weight=0.11,
                    valley_margin=0.02,
                    peak_ratio=0.3,
                ),
            },
        ]
    )
    assert design.select_candidate(candidates)["step"] == 0.08


def test_candidate_step_grid_is_exact() -> None:
    assert design.candidate_steps(0.02, 0.20, 0.01) == pytest.approx(
        np.arange(0.02, 0.201, 0.01),
        abs=1.0e-14,
    )


def test_candidate_observability_gate_checks_both_valleys() -> None:
    roots = [
        {"scaled_second_derivative": -1.0, "scaled_first_derivative_residual": 0.0},
        {"scaled_second_derivative": 1.0, "scaled_first_derivative_residual": 0.0},
        {"scaled_second_derivative": -1.0, "scaled_first_derivative_residual": 0.0},
        {"scaled_second_derivative": 1.0, "scaled_first_derivative_residual": 0.0},
        {"scaled_second_derivative": -1.0, "scaled_first_derivative_residual": 0.0},
    ]
    candidate = {
        "stationary_structure": {
            "minimum_weight": 0.1,
            "weight_sum_residual": 0.0,
            "maximum_count": 3,
            "minimum_count": 2,
            "stationary_root_count": 5,
            "topology": ["maximum", "minimum", "maximum", "minimum", "maximum"],
            "peak_minimum_to_maximum_ratio": 0.8,
            "valley_to_smaller_adjacent_peak_ratios": [0.70, 0.84],
            "roots": roots,
            "unresolved_zero_plateau": False,
            "derivative_at_time_start": 1.0,
            "derivative_at_time_stop": -1.0,
        }
    }
    eligible, gates = design.candidate_is_eligible(
        candidate,
        minimum_peak_ratio=0.1,
        maximum_valley_ratio=0.85,
        minimum_abs_scaled_curvature=1.0e-4,
        maximum_scaled_root_residual=1.0e-9,
    )
    assert eligible
    assert all(gates.values())
    candidate["stationary_structure"]["valley_to_smaller_adjacent_peak_ratios"][1] = 0.86
    eligible, gates = design.candidate_is_eligible(
        candidate,
        minimum_peak_ratio=0.1,
        maximum_valley_ratio=0.85,
        minimum_abs_scaled_curvature=1.0e-4,
        maximum_scaled_root_residual=1.0e-9,
    )
    assert not eligible
    assert not gates["both_valley_floors"]


def test_low_configuration_reproduces_the_known_slice_cusp() -> None:
    configuration = design.NumericalConfiguration(48, 48, 80, 20, 40, 0.5)
    model = design.FourPatchContinuum(configuration)
    cusp, diagnostics = design.locate_cusp(model, (12.0, 14.5))
    assert cusp["time"] == pytest.approx(13.328032, abs=3.0e-5)
    assert cusp["weights"] == pytest.approx(
        [0.28, 0.23019, 0.20932, 0.28049],
        abs=4.0e-4,
    )
    assert cusp["scaled_fourth_derivative"] == pytest.approx(-42.81, abs=0.08)
    assert cusp["unfolding"]["dimensionless_svd_ratio"] > 0.24
    assert diagnostics["maximum_cauchy_vs_real_first_derivative_difference"] < 1.0e-10


def test_polar_contact_check_is_independent_of_half_chord_parameterization() -> None:
    configuration = design.NumericalConfiguration(40, 40, 64, 20, 32, 0.5)
    model = design.FourPatchContinuum(configuration)
    check = design.polar_contact_reference(
        model,
        (5.0, 13.0),
        radial_order=40,
        angular_points=192,
    )
    assert check["maximum_relative_difference"] < 2.0e-11


def test_manifest_is_pinned_and_fail_closed() -> None:
    manifest = design.load_json(design.MANIFEST)
    design.validate_manifest(manifest)
    assert manifest["evidence_timing"] == design.EVIDENCE_TIMING
    assert manifest["required_claim_flags"] == {
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "project_gate_passed": False,
    }
    assert manifest["known_before_freeze"]["passing_step_hint"] == pytest.approx(0.15)


@pytest.mark.skipif(not design.OUTPUT.exists(), reason="formal result not generated yet")
def test_formal_result_observability_and_negative_claim_flags() -> None:
    payload = json.loads(Path(design.OUTPUT).read_text(encoding="utf-8"))
    assert payload["status"] == design.RESULT_STATUS
    assert payload["evidence_timing"] == design.EVIDENCE_TIMING
    assert payload["claim_flags"] == {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "project_gate_passed": False,
        "observable_free_exposure_confirmation_passed": True,
    }
    assert all(payload["gates"].values())
    selected = payload["inward_step_scan"]["selected"]
    assert selected["eligible"]
    assert selected["step"] in design.candidate_steps(0.02, 0.20, 0.01)
    structure = selected["stationary_structure"]
    assert structure["topology"] == [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]
    assert structure["peak_minimum_to_maximum_ratio"] >= 0.10
    assert max(structure["valley_to_smaller_adjacent_peak_ratios"]) <= 0.85
    assert payload["selected_absolute_weight_fine_crosscheck"]["eligible"]
