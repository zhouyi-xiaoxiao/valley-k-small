from __future__ import annotations

import math
from pathlib import Path

import continuum_broad_patch_b0_bridge as bridge
import numpy as np


def test_factor_jet_leibniz_rule_for_exponentials() -> None:
    rates = np.asarray((0.2, -0.3, 0.7, 1.1))
    contact_rate = -0.4
    amplitudes = np.asarray((1.0, 2.0, 3.0, 4.0))
    midpoint = np.asarray([amplitudes * rates**order for order in range(5)])
    contact = np.asarray([contact_rate**order for order in range(5)])
    observed = bridge.combine_factor_jets(midpoint[:, None, :], contact[:, None])[:, 0]
    expected = np.asarray([amplitudes * (rates + contact_rate) ** order for order in range(5)])
    np.testing.assert_allclose(observed, expected, rtol=2.0e-14, atol=2.0e-14)


def test_candidate_parameters_are_the_declared_broad_variant() -> None:
    if not bridge.MANIFEST.exists():
        return
    parameters = bridge.parameters_from_manifest(bridge.load_json(bridge.MANIFEST))
    assert parameters.initial_half_width == 0.02
    assert parameters.patch_half_width == 0.04
    assert parameters.patch_centres == (0.35, 0.60, 0.75, 0.90)
    assert parameters.particle_diffusion == 0.002


def test_small_factorized_mesh_is_conservative_and_has_four_channels() -> None:
    if not bridge.MANIFEST.exists():
        return
    manifest = bridge.load_json(bridge.MANIFEST)
    parameters = bridge.parameters_from_manifest(manifest)
    factors = bridge.build_fv_factors(17, parameters, manifest)
    diagnostics = factors.diagnostics
    assert factors.patch_profiles.shape == (4, 17)
    assert max(abs(value - 1.0) for value in diagnostics["patch_integrals"]) < 2.0e-13
    assert abs(diagnostics["midpoint_initial_mass"] - 1.0) < 2.0e-12
    assert abs(diagnostics["relative_initial_mass"] - 1.0) < 2.0e-12
    assert diagnostics["midpoint_generator_row_error"] < 2.0e-13
    assert diagnostics["relative_generator_row_error"] < 2.0e-13
    assert abs(diagnostics["contact_area"] - math.pi * 0.16**2) < 2.0e-13


def test_point_and_curve_factorizations_agree_on_small_mesh() -> None:
    if not bridge.MANIFEST.exists():
        return
    manifest = bridge.load_json(bridge.MANIFEST)
    parameters = bridge.parameters_from_manifest(manifest)
    factors = bridge.build_fv_factors(17, parameters, manifest)
    times = np.asarray((0.0, 0.5, 1.0))
    curves = bridge.factorized_curves(factors, times, chunk_points=3)
    for index, time in enumerate(times):
        point = bridge.factorized_point(factors, float(time))
        np.testing.assert_allclose(point, curves[:, index], rtol=2.0e-11, atol=2.0e-11)


def test_pinned_seed_restores_global_rng_state() -> None:
    outer_state = np.random.get_state()
    try:
        np.random.seed(20260713)
        state_before_context = np.random.get_state()
        with bridge.pinned_numpy_global_seed(1729):
            _ = np.random.randint(0, 2, size=1000)
        state_after_context = np.random.get_state()
        assert state_before_context[0] == state_after_context[0]
        np.testing.assert_array_equal(state_before_context[1], state_after_context[1])
        assert state_before_context[2:] == state_after_context[2:]
    finally:
        np.random.set_state(outer_state)


def test_seeded_sparse_exponential_probe_is_bitwise_identical() -> None:
    if not bridge.MANIFEST.exists():
        return
    manifest = bridge.load_json(bridge.MANIFEST)
    parameters = bridge.parameters_from_manifest(manifest)
    factors = bridge.build_fv_factors(17, parameters, manifest)
    times = np.asarray((0.0, 0.5, 1.0, 1.5))
    seed = int(manifest["numerical_reproducibility"]["numpy_global_seed"])

    def probe() -> bytes:
        with bridge.pinned_numpy_global_seed(seed):
            curves = bridge.factorized_curves(factors, times, chunk_points=4)
            points = np.asarray([bridge.factorized_point(factors, float(time)) for time in times])
        return (
            np.ascontiguousarray(curves, dtype="<f8").tobytes()
            + np.ascontiguousarray(points, dtype="<f8").tobytes()
        )

    assert probe() == probe()


def test_manifest_is_fail_closed_and_pins_every_dependency() -> None:
    if not bridge.MANIFEST.exists():
        return
    manifest = bridge.load_json(bridge.MANIFEST)
    observed = bridge.validate_manifest(manifest)
    assert manifest["required_claim_flags"] == {
        "preregistered_discovery": False,
        "continuum_interval_verified": False,
        "finite_B_Doi_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "project_gate_passed": False,
    }
    assert manifest["numerical_reproducibility"] == {
        "numpy_global_seed": 1729,
        "restore_numpy_global_rng_state": True,
        "full_rerun_byte_identity_required": True,
        "reason": "SciPy sparse one-norm estimation uses the legacy NumPy global RNG",
    }
    assert set(observed) == {
        "producer",
        "tests",
        "protocol",
        "exact_continuum_dependency",
        "finite_volume_dependency",
        "grid_dependency",
    }


def test_formal_result_retains_scope_and_bridge_rule() -> None:
    if not bridge.OUTPUT.exists():
        return
    result = bridge.load_json(bridge.OUTPUT)
    assert result["status"] == "PASS_RESULT_INFORMED_B0_NUMERICAL_BRIDGE"
    assert result["all_gates_passed"] is True
    assert result["exact_continuum_observability_passed"] is True
    assert result["finite_volume_B0_bridge_passed"] is True
    assert result["preregistered_discovery"] is False
    assert result["continuum_interval_verified"] is False
    assert result["finite_B_Doi_verified"] is False
    assert result["unbounded_domain_FV_limit_verified"] is False
    assert result["project_gate_passed"] is False
    assert result["numerical_reproducibility"]["numpy_global_seed"] == 1729
    assert result["bridge_control_selection"]["selected"]["step"] in (0.11, 0.12, 0.13)
    assert [row["mesh"][0] for row in result["finite_volume_mesh_rows"]] == [65, 97, 129, 193]
    assert all(result["gates"].values())


def test_no_main_tex_is_a_pinned_or_output_path() -> None:
    if not bridge.MANIFEST.exists():
        return
    manifest = bridge.load_json(bridge.MANIFEST)
    paths = [item["path"] for item in manifest["pinned_files"].values()]
    paths.append(str(Path(bridge.OUTPUT).relative_to(bridge.REPORT)))
    assert not any(path.endswith(".tex") for path in paths)
