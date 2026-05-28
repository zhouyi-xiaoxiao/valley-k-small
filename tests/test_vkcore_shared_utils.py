from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

from vkcore.peaks import classify_distribution_shape, find_candidate_peaks
from vkcore.plot_style import apply_research_plot_style
from vkcore.validation import (
    check_channel_decomposition,
    check_mass_balance,
    check_nonnegative,
    check_row_stochastic,
    decomposition_error,
    mass_balance_error,
)


def _gaussian(t: np.ndarray, center: float, width: float, amp: float = 1.0) -> np.ndarray:
    return amp * np.exp(-0.5 * ((t - center) / width) ** 2)


def test_synthetic_unimodal_distribution() -> None:
    t = np.arange(80)
    f = _gaussian(t, 25, 7)
    result = classify_distribution_shape(f)
    assert result.classification == "unimodal"
    assert result.metrics["t2"] is None
    assert find_candidate_peaks(f) == (25,)


def test_synthetic_shoulder_like_curve() -> None:
    t = np.arange(100)
    f = _gaussian(t, 25, 4, 1.0) + _gaussian(t, 50, 3, 0.02)
    result = classify_distribution_shape(f)
    assert result.classification == "shoulder"
    assert 0.0 < float(result.metrics["R_peak"]) < 0.025


def test_synthetic_local_bump() -> None:
    t = np.arange(100)
    f = _gaussian(t, 25, 4, 1.0) + _gaussian(t, 48, 4, 0.035)
    result = classify_distribution_shape(f)
    assert result.classification == "local_bump"
    assert 0.0 < float(result.metrics["R_peak"]) < 0.05
    assert int(result.metrics["peak_separation"]) >= 5


def test_synthetic_double_peak() -> None:
    t = np.arange(120)
    f = _gaussian(t, 28, 4, 1.0) + _gaussian(t, 62, 5, 0.18)
    result = classify_distribution_shape(f)
    assert result.classification == "double_peak"
    assert float(result.metrics["R_peak"]) >= 0.05
    assert float(result.metrics["R_valley"]) <= 0.8
    assert int(result.metrics["peak_separation"]) >= 5
    assert result.metrics["t1"] == 28
    assert result.metrics["t2"] == 62


def test_row_stochastic_valid_matrix() -> None:
    P = np.array([[0.2, 0.8], [0.0, 1.0]])
    assert check_nonnegative(P)
    assert check_row_stochastic(P)


def test_row_stochastic_invalid_matrix() -> None:
    with pytest.raises(ValueError, match="row-sum"):
        check_row_stochastic(np.array([[0.2, 0.7], [0.0, 1.0]]))
    with pytest.raises(ValueError, match="negative"):
        check_nonnegative(np.array([[0.5, -1e-4, 0.5]]))


def test_mass_balance_valid_example() -> None:
    f = np.array([0.2, 0.3, 0.1])
    survival = np.array([1.0, 0.8, 0.5, 0.4])
    assert mass_balance_error(f, survival) == pytest.approx(0.0)
    assert check_mass_balance(f, survival)


def test_mass_balance_invalid_example() -> None:
    f = np.array([0.2, 0.25, 0.1])
    survival = np.array([1.0, 0.8, 0.5, 0.4])
    assert mass_balance_error(f, survival) == pytest.approx(0.05)
    with pytest.raises(ValueError, match="mass balance"):
        check_mass_balance(f, survival)


def test_decomposition_valid_and_invalid_examples() -> None:
    a = np.array([0.1, 0.2, 0.3])
    b = np.array([0.05, 0.1, 0.0])
    total = np.array([0.15, 0.3, 0.3])
    assert decomposition_error(total, [a, b]) == pytest.approx(0.0)
    assert check_channel_decomposition(total, {"target1": a, "target2": b})

    bad_total = np.array([0.15, 0.31, 0.3])
    assert decomposition_error(bad_total, [a, b]) == pytest.approx(0.01)
    with pytest.raises(ValueError, match="channel decomposition"):
        check_channel_decomposition(bad_total, [a, b])


def test_apply_research_plot_style_sets_readable_defaults() -> None:
    updates = apply_research_plot_style()
    assert updates["axes.labelsize"] == 15
    assert updates["xtick.labelsize"] == 12
    assert updates["legend.fontsize"] == 12
    assert updates["lines.linewidth"] == 2.0
    assert updates["savefig.dpi"] >= 300
