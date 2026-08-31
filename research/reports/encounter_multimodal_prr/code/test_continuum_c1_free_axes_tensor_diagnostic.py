from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import continuum_c1_free_axes_tensor_diagnostic as fixture

REPORT = Path(__file__).resolve().parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c1_free_axes_tensor_diagnostic_v1.json"


def _load() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_published_artifact_is_exact_recomputation() -> None:
    assert ARTIFACT.read_bytes() == fixture.canonical_json_bytes(fixture.build_payload())


def test_fixture_is_neutral_and_every_promotion_flag_is_false() -> None:
    payload = _load()
    assert payload["schema"] == fixture.SCHEMA
    assert payload["status"] == fixture.STATUS
    assert payload["refinement_intervals"] == list(fixture.REFINEMENT_INTERVALS)
    assert payload["claim_boundary"] == {
        "control_result_or_scratch_payload_read": False,
        "ideal_fixed_box_free_rates_only": True,
        "neutral_diagnostic_only": True,
        "positive_budget_values_read": False,
        "production_bridge_claimed": False,
        "three_dimensional_array_allocated": False,
    }
    assert payload["promotion_flags"]
    assert all(value is False for value in payload["promotion_flags"].values())
    assert payload["theory_boundary"]["complete_c1"] == "HOLD"
    raw = ARTIFACT.read_text(encoding="utf-8").lower()
    for forbidden in (
        "control_weights",
        "peak_time",
        "root_interval",
        "basin_mass",
        "positive_budget_topology",
    ):
        assert forbidden not in raw


def test_both_cell_centred_ou_parameterizations_are_covered() -> None:
    payload = _load()
    assert payload["encounter_ou_parameter_relation"] == {
        "base_D_exact": str(fixture.ENCOUNTER_D),
        "midpoint_diffusion_equals_D_over_2": True,
        "relative_diffusion_equals_2D": True,
        "shared_gamma_exact": str(fixture.OU_GAMMA),
    }
    for name, expected_diffusion, expected_mean in (
        ("midpoint_ou", fixture.MIDPOINT_SPEC["diffusion"], fixture.MIDPOINT_SPEC["mean"]),
        ("relative_ou", fixture.RELATIVE_SPEC["diffusion"], fixture.RELATIVE_SPEC["mean"]),
    ):
        family = payload[name]
        assert family["alignment"] == "cell_centred"
        assert family["parameters"]["diffusion_exact"] == str(expected_diffusion)
        assert family["parameters"]["mean_exact"] == str(expected_mean)
        assert family["probe"].endswith("with_zero_endpoint_derivatives")
        assert [row["axis_size"] for row in family["rows"]] == list(
            fixture.REFINEMENT_INTERVALS
        )
        assert all(
            row["construction"] == "cell_centred_reflecting_scharfetter_gummel"
            for row in family["rows"]
        )


def test_cell_centred_map_edge_and_neumann_compatible_form_are_second_order() -> None:
    payload = _load()
    for family_name in ("midpoint_ou", "relative_ou"):
        family = payload[family_name]
        orders = family["observed_last_pair_orders"]
        assert 1.9 < orders["rho_sup_error"] < 2.1
        assert 1.9 < orders["edge_interpolant_ratio_sup_error"] < 2.1
        assert 1.85 < orders["probe_form_relative_error"] < 2.15
        for row in family["rows"]:
            assert row["raw_mass_intervals_contain_formula"] is True
            assert row["raw_rate_intervals_contain_formula"] is True
            assert row["raw_conductance_intervals_contain_formula"] is True
            assert float.fromhex(row["gauge_mass_absolute_error_hex"]) == 0.0
            assert float.fromhex(row["physical_cell_partition_absolute_error_hex"]) == 0.0
        for key in (
            "rho_sup_error_hex",
            "edge_interpolant_ratio_sup_error_hex",
            "probe_form_relative_error_hex",
        ):
            errors = [float.fromhex(row[key]) for row in family["rows"]]
            assert all(0.0 < fine < coarse for coarse, fine in zip(errors, errors[1:]))


def test_vertex_dual_geometry_and_endpoint_rate_factor_are_exact() -> None:
    family = _load()["vertex_dual_ou"]
    assert family["alignment"] == "vertex_dual"
    assert family["probe"] == "u(x)=1+x+x^2/4"
    for intervals, row in zip(fixture.REFINEMENT_INTERVALS, family["rows"], strict=True):
        assert row["axis_size"] == intervals + 1
        assert row["construction"] == "vertex_centred_reflecting_scharfetter_gummel"
        assert row["endpoint_half_volumes_exact"] is True
        assert float.fromhex(row["endpoint_outgoing_rate_factor_left_hex"]) == 2.0
        assert float.fromhex(row["endpoint_outgoing_rate_factor_right_hex"]) == 2.0
        assert row["raw_mass_intervals_contain_formula"] is True
        assert row["raw_rate_intervals_contain_formula"] is True
        assert row["raw_conductance_intervals_contain_formula"] is True


def test_vertex_endpoint_rho_is_first_order_but_edge_interior_and_form_are_second_order() -> None:
    family = _load()["vertex_dual_ou"]
    orders = family["observed_last_pair_orders"]
    assert 0.95 < orders["endpoint_rho_sup_error"] < 1.05
    assert 0.95 < orders["rho_sup_error"] < 1.05
    assert 1.9 < orders["interior_rho_sup_error"] < 2.1
    assert 1.9 < orders["edge_interpolant_ratio_sup_error"] < 2.1
    assert 1.85 < orders["probe_form_relative_error"] < 2.15
    finest = family["rows"][-1]
    assert float.fromhex(finest["endpoint_rho_sup_error_hex"]) > float.fromhex(
        finest["interior_rho_sup_error_hex"]
    )


def test_periodic_base_and_half_shift_have_exact_mass_rate_and_conductance() -> None:
    periodic = _load()["periodic"]
    assert periodic["fourier_mode"] == fixture.PERIODIC_MODE
    assert len(periodic["rows"]) == 2 * len(fixture.REFINEMENT_INTERVALS)
    for row in periodic["rows"]:
        intervals = row["axis_size"]
        step = fixture.PERIODIC_WIDTH / intervals
        expected_mass = step / fixture.PERIODIC_WIDTH
        expected_rate = fixture.PERIODIC_DIFFUSION / step**2
        expected_conductance = expected_mass * expected_rate
        assert Fraction(row["normalized_cell_mass_exact"]) == expected_mass
        assert Fraction(row["normalized_mass_sum_exact"]) == 1
        assert Fraction(row["periodic_rate_exact"]) == expected_rate
        assert Fraction(row["conductance_exact"]) == expected_conductance
        assert row["raw_builder_mass_intervals_contain_h"] is True
        assert row["rate_intervals_contain_formula"] is True
        assert row["wrapped_cell_count"] == (1 if row["alignment"] == "half_shift" else 0)
        assert math.isclose(
            float.fromhex(row["combined_fourier_norm_squared_hex"]),
            1.0,
            rel_tol=0.0,
            abs_tol=2e-15,
        )


def test_periodic_fourier_recovery_is_second_order_and_shift_invariant() -> None:
    periodic = _load()["periodic"]
    assert 1.95 < periodic["observed_last_pair_order"] < 2.05
    assert float.fromhex(periodic["translation_energy_gap_max_hex"]) == 0.0
    for alignment in ("base", "half_shift"):
        rows = [row for row in periodic["rows"] if row["alignment"] == alignment]
        errors = [float.fromhex(row["fourier_relative_error_hex"]) for row in rows]
        assert all(0.0 < fine < coarse for coarse, fine in zip(errors, errors[1:]))
        assert all(
            float.fromhex(row["fourier_formula_absolute_residual_hex"]) == 0.0
            for row in rows
        )


def test_large_tensor_diagnostic_uses_axis_storage_only() -> None:
    tensor = _load()["tensor_factorization"]["large_axis_only_diagnostic"]
    assert tensor["axis_sizes"] == [256, 256, 256]
    assert tensor["virtual_tensor_cell_count"] == 256**3
    assert tensor["stored_axis_value_count"] == 3 * 256
    assert tensor["largest_live_axis_vector_length"] == 256
    assert tensor["full_tensor_array_allocated"] is False
    terms = [float.fromhex(value) for value in tensor["factorized_energy_terms_hex"]]
    assert all(value > 0.0 for value in terms)
    assert math.isclose(
        sum(terms),
        float.fromhex(tensor["factorized_energy_hex"]),
        rel_tol=2e-15,
        abs_tol=0.0,
    )


def test_exact_streaming_tensor_sentinel_matches_factorization() -> None:
    sentinel = _load()["tensor_factorization"]["small_exact_streaming_sentinel"]
    assert sentinel["full_tensor_values_materialized"] is False
    assert sentinel["identity_exact"] is True
    assert Fraction(sentinel["direct_streaming_norm_exact"]) == Fraction(
        sentinel["factorized_norm_exact"]
    )
    assert Fraction(sentinel["direct_streaming_energy_exact"]) == Fraction(
        sentinel["factorized_energy_exact"]
    )


def test_generator_has_no_dense_array_dependency_or_full_tensor_constructor() -> None:
    source = fixture.HERE.read_text(encoding="utf-8")
    assert "import numpy" not in source
    assert "np." not in source
    assert "meshgrid" not in source
    assert "reshape(" not in source
    assert "full_tensor_array_allocated\": True" not in source
