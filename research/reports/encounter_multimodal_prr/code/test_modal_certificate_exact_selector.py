from __future__ import annotations

from fractions import Fraction

import modal_certificate_exact_selector as exact
import pytest


def _synthetic_table(
    rows: tuple[tuple[str, str, str, str], tuple[str, str, str, str]],
    *,
    floor: str = "0.1",
) -> exact.FrozenRationalTable:
    return exact.FrozenRationalTable(
        name="synthetic_m1",
        target_maxima=1,
        checkpoint_times_decimal=("1", "2"),
        desired_signs=(1, -1),
        weight_floor_decimal=floor,
        row_scales_decimal=("2", "3"),
        signed_normalized_coefficients_decimal=rows,
    )


def _fractions(payload: list[dict[str, str]]) -> tuple[Fraction, ...]:
    return tuple(Fraction(row["exact"]) for row in payload)


def test_hex_parser_recovers_f0_exact_raw_sums() -> None:
    expected_sums = {
        "m1": Fraction(36028797018963973, 36028797018963968),
        "m2": Fraction(9007199254740991, 9007199254740992),
        "m3": Fraction(36028797018963967, 36028797018963968),
    }
    for name, expected in expected_sums.items():
        raw = tuple(exact.fraction_from_hex(value) for value in exact.F0_RAW_WEIGHT_HEX[name])
        assert sum(raw, Fraction(0)) == expected
        normalized = exact.f0_exact_control(name)
        assert sum(normalized, Fraction(0)) == 1
        assert all(value > 0 for value in normalized)


def test_exact_vertex_enumeration_and_lexicographic_tie_break() -> None:
    # rho <= w0+w1 gives a one-dimensional optimal face after w2=w3=floor.
    # Exact lexicographic minimization must choose w0=floor, then put the
    # remaining mass into w1; a solver-native arbitrary point is not allowed.
    table = _synthetic_table((
        ("1", "1", "0", "0"),
        ("1", "1", "0", "0"),
    ))
    result = exact.solve_exact_selector(table)
    assert result["status"] == exact.STATUS_PASS
    assert _fractions(result["selected"]["weights"]) == (
        Fraction(1, 10),
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    assert Fraction(result["selected"]["normalized_optimum_rho"]["exact"]) == Fraction(4, 5)
    assert result["enumeration"][
        "all_linear_systems_and_constraint_residuals_used_fraction_exact_arithmetic"
    ]
    assert result["selected"]["exact_feasibility_rechecked"]
    assert result["selected"]["simplex_sum_residual"]["numerator"] == "0"


def test_nonpositive_optimum_is_a_distinct_hold_state() -> None:
    table = _synthetic_table((
        ("1", "0", "0", "0"),
        ("-1", "0", "0", "0"),
    ), floor="0")
    result = exact.solve_exact_selector(table)
    assert result["status"] == exact.STATUS_HOLD_NONPOSITIVE
    assert _fractions(result["selected"]["weights"]) == (
        Fraction(0),
        Fraction(0),
        Fraction(0),
        Fraction(1),
    )
    assert result["selected"]["normalized_optimum_rho"]["numerator"] == "0"


def test_infeasible_simplex_floor_is_a_distinct_hold_state() -> None:
    table = _synthetic_table((
        ("1", "0", "0", "0"),
        ("0", "1", "0", "0"),
    ), floor="0.26")
    result = exact.solve_exact_selector(table)
    assert result["status"] == exact.STATUS_HOLD_INFEASIBLE_FLOOR
    assert result["selected"] is None


def test_table_validation_rejects_zero_scale_and_nonunit_normalization() -> None:
    zero_scale = exact.FrozenRationalTable(
        name="bad",
        target_maxima=1,
        checkpoint_times_decimal=("1", "2"),
        desired_signs=(1, -1),
        weight_floor_decimal="0",
        row_scales_decimal=("1", "0"),
        signed_normalized_coefficients_decimal=(
            ("1", "0", "0", "0"),
            ("0", "1", "0", "0"),
        ),
    )
    zero_result = exact.solve_exact_selector(zero_scale)
    assert zero_result["status"] == exact.STATUS_HOLD_SCALE_ZERO
    assert zero_result["selected"] is None

    nonunit = _synthetic_table((
        ("0.5", "0", "0", "0"),
        ("0", "1", "0", "0"),
    ))
    nonunit_result = exact.solve_exact_selector(nonunit)
    assert nonunit_result["status"] == exact.STATUS_HOLD_INVALID_TABLE
    assert "max norm one" in nonunit_result["validation_error"]


def test_frozen_broad_tables_have_exact_positive_optima() -> None:
    expected_decimal_prefixes = {
        "m1": ("0.03", "0.91", "0.03", "0.03"),
        "m2": ("0.5420243", "0.03", "0.0482450", "0.3797306"),
        "m3": ("0.4016285", "0.2761816", "0.03", "0.2921898"),
    }
    for table in exact.FROZEN_TABLES:
        result = exact.solve_exact_selector(table)
        assert result["status"] == exact.STATUS_PASS
        weights = result["selected"]["weights"]
        assert sum(_fractions(weights), Fraction(0)) == 1
        for item, prefix in zip(weights, expected_decimal_prefixes[table.name], strict=True):
            assert item["decimal_40_significant"].startswith(prefix)
        residuals = result["selected"]["constraint_residuals"]
        assert all(Fraction(row["exact"]) >= 0 for row in residuals.values())


def test_method_result_is_fail_closed_at_continuum_and_f0_boundaries() -> None:
    result = exact.build_method_only_result()
    assert result["status"] == exact.OVERALL_HOLD
    assert result["publication_certificate_status"] == exact.CONTINUUM_HOLD
    assert result["positive_budget_evaluated"] is False
    assert result["primary_finite_volume_grid_evaluated"] is False
    assert result["continuum_kernel_executed_by_this_producer"] is False
    assert result["external_lp_solver_used"] is False
    assert result["gates"]["all_finite_rational_lp_selectors_have_positive_exact_optima"]
    assert not result["gates"]["continuum_derivative_coefficients_outward_interval_certified"]
    assert result["authorized_scientific_command"] is None

    # Rationalizing the coefficient table changes every exact vertex relative
    # to the raw-binary64/S_c controls already frozen in F0.  This must be an
    # explicit compatibility HOLD, never an implicit control replacement.
    for row in result["f0_control_compatibility"].values():
        assert row["status"] == exact.F0_COMPATIBILITY_HOLD
        assert row["weights_exactly_equal"] is False
        assert row["replacement_authorized"] is False
        gap = row["selector_exact_optimality_gap_over_feasible_f0_control"]
        if gap is not None:
            assert Fraction(gap["exact"]) >= 0


def test_main_requires_explicit_method_only_flag() -> None:
    with pytest.raises(SystemExit, match="explicit --execute-method-only-b0 is required"):
        exact.main([])
