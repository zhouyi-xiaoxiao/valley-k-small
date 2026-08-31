from __future__ import annotations

import math

import exact_m_zero_budget_slow_factor_stress as stress
import pytest


def test_declared_b0_stress_passes_without_positive_budget() -> None:
    result = stress.build_result()
    assert result["status"] == stress.STATUS
    assert result["positive_budget_evaluated"] is False
    assert result["killed_generator_constructed"] is False
    assert all(row["pass"] for row in result["rows"])


def test_every_row_has_exact_alternating_observed_signature() -> None:
    result = stress.build_result()
    for row in result["rows"]:
        expected = row["expected_root_count"]
        assert row["pure_root_count"] == expected
        assert row["slow_root_count"] == expected
        assert row["slow_root_types"] == [
            "max" if index % 2 == 0 else "min" for index in range(expected)
        ]
        assert row["endpoint_signs"] == [1.0, -1.0]


def test_declared_shift_scalings_remain_bounded() -> None:
    result = stress.build_result()
    assert max(row["max_abs_peak_shift_over_sigma2"] for row in result["rows"]) < 1.0
    assert max(row["max_abs_valley_shift_over_sigma4"] for row in result["rows"]) < 8.0


def test_crossover_edge_fixture_is_constant_not_exp_sigma_inverse_square() -> None:
    result = stress.build_result()
    for constant in (1.0, 4.0, 8.0):
        assert result["fixed_crossover_edge_ratios"][str(constant)] == pytest.approx(
            math.exp(-constant), rel=0.0, abs=1e-15
        )


def test_cli_is_fail_closed_without_explicit_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        stress.main([])
    assert exc_info.value.code == 2
    assert "explicit --execute-b0-stress is required" in capsys.readouterr().err
