from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
REPORT_CODE = ROOT / "research" / "reports" / "encounter_reflecting_mean_validation" / "code"
if str(REPORT_CODE) not in sys.path:
    sys.path.insert(0, str(REPORT_CODE))

from reflecting_encounter import EncounterCase
from reflecting_encounter import assert_diagonal_thresholds
from reflecting_encounter import assert_validation_thresholds
from reflecting_encounter import build_absorbing_joint_transition
from reflecting_encounter import build_joint_transition
from reflecting_encounter import build_reflecting_lazy_transition
from reflecting_encounter import diagonal_indices
from reflecting_encounter import fixed_total_mobility
from reflecting_encounter import fundamental_mean
from reflecting_encounter import validate_diagonal_case
from reflecting_encounter import row_stochastic_error
from reflecting_encounter import validate_case


def test_reflecting_lazy_transition_boundary_rule() -> None:
    P = build_reflecting_lazy_transition(L=5, Q=0.6)

    assert P[0].tolist() == pytest.approx([0.7, 0.3, 0.0, 0.0, 0.0])
    assert P[2].tolist() == pytest.approx([0.0, 0.3, 0.4, 0.3, 0.0])
    assert P[4].tolist() == pytest.approx([0.0, 0.0, 0.0, 0.3, 0.7])
    assert float(np.min(P)) >= 0.0
    assert row_stochastic_error(P) < 1e-12


def test_fixed_total_mobility_formula_and_bounds() -> None:
    Q1, Q2 = fixed_total_mobility(q0=0.35, rho=2.0)
    assert Q1 == pytest.approx(2.0 * 0.35 * 2.0 / 3.0)
    assert Q2 == pytest.approx(2.0 * 0.35 / 3.0)
    assert Q1 / Q2 == pytest.approx(2.0)

    with pytest.raises(ValueError, match="Q_i > 1"):
        fixed_total_mobility(q0=0.8, rho=4.0)


def test_absorbing_joint_transition_stops_diagonal_states() -> None:
    P1 = build_reflecting_lazy_transition(L=5, Q=0.4)
    P2 = build_reflecting_lazy_transition(L=5, Q=0.7)
    joint = build_joint_transition(P1, P2)
    absorbing = build_absorbing_joint_transition(P1, P2)

    assert row_stochastic_error(joint) < 1e-12
    assert row_stochastic_error(absorbing) < 1e-12
    for idx in diagonal_indices(5):
        expected = np.zeros(25)
        expected[idx] = 1.0
        assert absorbing[idx] == pytest.approx(expected)


@pytest.mark.parametrize(
    "case",
    [
        EncounterCase(L=5, x1_0=0, x2_0=4, q0=0.35, rho=0.5),
        EncounterCase(L=5, x1_0=1, x2_0=3, q0=0.35, rho=2.0),
        EncounterCase(L=7, x1_0=1, x2_0=5, q0=0.35, rho=1.0),
        EncounterCase(L=7, x1_0=0, x2_0=6, q0=0.30, rho=4.0),
    ],
)
def test_reflecting_encounter_mean_validation_cases(case: EncounterCase) -> None:
    result = validate_case(case)
    assert_validation_thresholds(result)
    assert result.p1_row_error < 1e-12
    assert result.p2_row_error < 1e-12
    assert result.mass_balance_error < 1e-10
    assert result.mean_difference < 1e-8
    assert result.tail_mass < 1e-12
    assert result.exact_mean > 0.0


@pytest.mark.parametrize(
    "case",
    [
        EncounterCase(L=5, x1_0=0, x2_0=4, q0=0.35, rho=0.5),
        EncounterCase(L=7, x1_0=1, x2_0=5, q0=0.35, rho=4.0),
    ],
)
def test_diagonal_position_decomposition_cases(case: EncounterCase) -> None:
    result = validate_diagonal_case(case)
    assert_diagonal_thresholds(result)

    assert result.f_by_position.shape == (result.times.size, case.L)
    assert np.max(np.abs(result.f_total - result.f_by_position.sum(axis=1))) < 1e-10
    assert result.mass_balance_error < 1e-10
    assert result.decomposition_error < 1e-10
    assert result.tail_mass < 1e-12
    assert all(window.by_position.shape == (case.L,) for window in result.windows)
    assert result.windows[0].name == "early"


def test_diagonal_distribution_matches_fundamental_mean() -> None:
    case = EncounterCase(L=7, x1_0=1, x2_0=5, q0=0.35, rho=4.0)
    result = validate_diagonal_case(case)
    Q1, Q2 = fixed_total_mobility(case.q0, case.rho)
    P1 = build_reflecting_lazy_transition(case.L, Q1)
    P2 = build_reflecting_lazy_transition(case.L, Q2)
    exact_mean, _, _ = fundamental_mean(P1, P2, case.x1_0, case.x2_0)

    assert abs(result.mean - exact_mean) < 1e-8
    assert int(np.argmax(result.windows[0].by_position)) in range(case.L)
