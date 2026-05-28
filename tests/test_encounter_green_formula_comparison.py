from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "research" / "reports" / "encounter_reflecting_diagonal_decomp" / "code" / "compare_green_formula.py"
spec = importlib.util.spec_from_file_location("compare_green_formula", MODULE_PATH)
assert spec is not None and spec.loader is not None
compare_green_formula = importlib.util.module_from_spec(spec)
sys.modules["compare_green_formula"] = compare_green_formula
spec.loader.exec_module(compare_green_formula)


def test_green_renewal_matches_absorbing_chain_channels() -> None:
    case = compare_green_formula.ComparisonCase(
        "pytest_L5",
        L=5,
        x1_0=0,
        x2_0=4,
        q0=0.35,
        rho=2.0,
    )

    for z in (0.1 + 0j, 0.7 + 0j, 0.45 + 0.15j):
        result = compare_green_formula.compare_case(case, z)
        assert result.abs_error < 1e-12
        assert result.rel_error < 1e-12
        assert result.max_channel_abs_error < 1e-12
        assert result.absorbing_total == pytest.approx(result.green_total)


def test_report_comparison_grid_is_small_and_precise() -> None:
    results = compare_green_formula.iter_comparisons()

    assert len(results) == len(compare_green_formula.CASES) * len(compare_green_formula.Z_VALUES)
    assert max(result.abs_error for result in results) < 1e-12
    assert max(result.max_channel_abs_error for result in results) < 1e-12
