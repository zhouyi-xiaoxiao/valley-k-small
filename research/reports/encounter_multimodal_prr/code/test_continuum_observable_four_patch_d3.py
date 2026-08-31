from __future__ import annotations

import inspect
import json
from pathlib import Path

import continuum_observable_four_patch as base
import continuum_observable_four_patch_d3 as design
import numpy as np
import pytest


def test_frozen_configurations_have_declared_orders() -> None:
    assert design.COARSE == base.NumericalConfiguration(56, 56, 56, 12, 48, 0.50)
    assert design.PRIMARY == base.NumericalConfiguration(72, 72, 72, 16, 64, 0.40)
    assert design.FINE == base.NumericalConfiguration(96, 96, 96, 24, 80, 0.30)


def test_transverse_coefficient_derivative_matches_value_difference() -> None:
    configuration = base.NumericalConfiguration(32, 32, 40, 8, 32, 0.5)
    model = design.FourPatchContinuumD3(configuration)
    times = np.asarray((1.0, 5.0, 13.0))
    coefficients, derivative = model._transverse_coefficients(times)
    step = 1.0e-5
    plus, _ = model._transverse_coefficients(times + step)
    minus, _ = model._transverse_coefficients(times - step)
    assert derivative == pytest.approx(
        (plus - minus) / (2.0 * step),
        rel=2.0e-9,
        abs=2.0e-11,
    )
    assert coefficients[:, 0] == pytest.approx(1.0)
    assert derivative[:, 0] == pytest.approx(0.0)


def test_each_transverse_initial_coordinate_uses_the_frozen_compact_bump() -> None:
    configuration = base.NumericalConfiguration(48, 48, 48, 12, 32, 0.5)
    model = design.FourPatchContinuumD3(configuration)
    pars = model.parameters
    starts = pars.relative_perp_start + pars.initial_half_width * model.bump_nodes
    expected = np.asarray(
        [
            np.dot(
                model.bump_weights,
                np.cos(mode * model.omega * starts),
            )
            for mode in model.mode_numbers
        ]
    )
    point_start = np.cos(model.mode_numbers * model.omega * pars.relative_perp_start)
    assert model.transverse_initial_cosine_coefficients == pytest.approx(expected, abs=2.0e-15)
    assert abs(expected[-1] - point_start[-1]) > 1.0e-3


def test_real_channel_derivative_matches_complex_value_difference() -> None:
    configuration = base.NumericalConfiguration(32, 32, 40, 8, 40, 0.4)
    model = design.FourPatchContinuumD3(configuration)
    times = np.asarray((3.0, 9.0, 20.0))
    channels, derivative = model.real_channels_and_first_derivatives(times)
    step = 2.0e-5
    plus = np.real(model.channels(times + step))
    minus = np.real(model.channels(times - step))
    assert channels == pytest.approx(np.real(model.channels(times)), rel=2.0e-13)
    assert derivative == pytest.approx(
        (plus - minus) / (2.0 * step),
        rel=3.0e-8,
        abs=3.0e-10,
    )


def test_direct_spherical_integrand_does_not_use_bessel_disk_tensor() -> None:
    source = inspect.getsource(design.direct_spherical_contact_values)
    assert "model.transverse_disk_integrals" not in source
    assert "j1(" not in source
    configuration = base.NumericalConfiguration(28, 28, 36, 6, 32, 0.5)
    model = design.FourPatchContinuumD3(configuration)
    model.transverse_disk_integrals[:] = np.nan
    values = design.direct_spherical_contact_values(
        model,
        (5.0,),
        radial_order=20,
        polar_order=20,
        azimuthal_points=96,
    )
    assert values.shape == (1,)
    assert np.isfinite(values[0]) and 0.0 < values[0] < 1.0


def test_direct_spherical_reference_agrees_in_low_configuration() -> None:
    configuration = base.NumericalConfiguration(32, 32, 44, 8, 32, 0.5)
    model = design.FourPatchContinuumD3(configuration)
    check = design.spherical_contact_reference(
        model,
        (1.0, 5.0, 13.0, 25.0),
        radial_order=30,
        polar_order=32,
        azimuthal_points=160,
    )
    assert check["maximum_relative_difference"] < 2.0e-11
    assert all(row["direct_spherical"] > 0.0 for row in check["rows"])


def test_low_configuration_reproduces_known_physical_d3_cusp() -> None:
    configuration = base.NumericalConfiguration(40, 40, 44, 10, 40, 0.5)
    model = design.FourPatchContinuumD3(configuration)
    cusp, diagnostics = base.locate_cusp(model, (12.0, 14.0))
    assert cusp["time"] == pytest.approx(12.80973996, abs=4.0e-6)
    assert cusp["weights"] == pytest.approx(
        [0.28, 0.182204, 0.207670, 0.330126],
        abs=3.0e-5,
    )
    assert cusp["scaled_fourth_derivative"] == pytest.approx(-39.8723, abs=0.02)
    assert cusp["unfolding"]["dimensionless_svd_ratio"] > 0.23
    assert diagnostics["maximum_cauchy_vs_real_first_derivative_difference"] < 2.0e-10


def test_manifest_is_pinned_result_informed_and_fail_closed() -> None:
    manifest = base.load_json(design.MANIFEST)
    design.validate_manifest(manifest)
    assert manifest["evidence_timing"] == design.EVIDENCE_TIMING
    assert manifest["known_before_freeze"]["likely_selected_step"] == pytest.approx(0.10)
    assert manifest["required_claim_flags"] == {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
    }
    scan = manifest["inward_step_scan"]
    assert scan["time_spacing"] == pytest.approx(0.002)
    assert scan["candidate_steps"] == pytest.approx(np.arange(0.02, 0.201, 0.01), abs=1.0e-14)
    reference = manifest["spherical_coordinate_check"]
    assert reference == {
        "times": [1.0, 5.0, 13.0, 25.0],
        "radial_order": 36,
        "polar_order": 40,
        "azimuthal_points": 256,
        "maximum_relative_difference": 5e-11,
    }


@pytest.mark.skipif(not design.OUTPUT.exists(), reason="formal result not generated yet")
def test_formal_result_passes_only_the_scoped_physical_d3_claim() -> None:
    payload = json.loads(Path(design.OUTPUT).read_text(encoding="utf-8"))
    assert payload["status"] == design.RESULT_STATUS
    assert payload["evidence_timing"] == design.EVIDENCE_TIMING
    assert payload["claim_flags"] == {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
        "observable_d3_free_exposure_confirmation_passed": True,
    }
    assert all(payload["gates"].values())
    selected = payload["inward_step_scan"]["selected"]
    assert selected["eligible"]
    assert selected["step"] in base.candidate_steps(0.02, 0.20, 0.01)
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
    assert payload["direct_spherical_coordinate_check"]["maximum_relative_difference"] <= 5.0e-11
