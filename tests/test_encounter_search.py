from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPORT_CODE = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "reports"
    / "final_multitimescale_fpt_encounter"
    / "code"
)
sys.path.insert(0, str(REPORT_CODE))

from encounter_search.solver import absorbing_pgf_total
from encounter_search.solver import build_absorption_chain
from encounter_search.solver import build_chain
from encounter_search.solver import determinant_pgf_total
from encounter_search.solver import exact_distribution
from encounter_search.solver import exact_total_distribution
from encounter_search.solver import fundamental_moments
from encounter_search.solver import reflecting_transition
from encounter_search.solver import row_stochastic_error
from encounter_search.stage2 import diagnose_curve
from encounter_search.stage2b import f2_has_true_double_peak


def test_reflecting_transition_boundary_rule() -> None:
    P = reflecting_transition(5, 0.6)
    dense = P.toarray()

    assert dense[0].tolist() == pytest.approx([0.7, 0.3, 0.0, 0.0, 0.0])
    assert dense[2].tolist() == pytest.approx([0.0, 0.3, 0.4, 0.3, 0.0])
    assert dense[4].tolist() == pytest.approx([0.0, 0.0, 0.0, 0.3, 0.7])
    assert row_stochastic_error(P) < 1e-12
    assert float(P.data.min()) >= 0.0


def test_bounce_reflection_boundary_rule() -> None:
    P = reflecting_transition(5, 0.6, reflect_mode="bounce")
    dense = P.toarray()

    assert dense[0].tolist() == pytest.approx([0.4, 0.6, 0.0, 0.0, 0.0])
    assert dense[4].tolist() == pytest.approx([0.0, 0.0, 0.0, 0.6, 0.4])
    assert row_stochastic_error(P) < 1e-12


def test_formula_identities_match_forward_distribution() -> None:
    chain = build_chain(5, 0.4, 0.9)
    dist = exact_distribution(chain, (1, 5), survival_tol=1e-13, max_t=50_000)
    moments = fundamental_moments(chain, (1, 5))

    assert dist.reached_tol
    assert dist.mass == pytest.approx(1.0, abs=1e-12)
    assert dist.mean == pytest.approx(moments.mean, rel=0.0, abs=1e-9)
    assert moments.p_sum == pytest.approx(1.0, abs=1e-12)
    assert moments.p_tau_sum == pytest.approx(moments.mean, abs=1e-10)
    assert np.max(np.abs(dist.f - dist.f_by_k.sum(axis=1))) < 1e-13
    assert dist.max_mass_balance_error < 1e-13


def test_walker_swap_symmetry() -> None:
    chain = build_chain(6, 0.3, 0.8)
    swapped = build_chain(6, 0.8, 0.3)

    dist = exact_distribution(chain, (2, 6), survival_tol=1e-13, max_t=50_000)
    dist_swapped = exact_distribution(swapped, (6, 2), survival_tol=1e-13, max_t=50_000)

    assert dist.f.shape == dist_swapped.f.shape
    assert dist.f == pytest.approx(dist_swapped.f, abs=1e-13)
    assert dist.f_by_k == pytest.approx(dist_swapped.f_by_k, abs=1e-13)


def test_crossing_absorption_is_no_later_than_colocation() -> None:
    co_location = build_absorption_chain(5, 0.8, 0.8, absorption_mode="co_location")
    crossing = build_absorption_chain(5, 0.8, 0.8, absorption_mode="co_location_or_crossing")

    dist_coloc = exact_total_distribution(co_location, (2, 3), survival_tol=1e-13, max_t=10_000)
    dist_cross = exact_total_distribution(crossing, (2, 3), survival_tol=1e-13, max_t=10_000)

    assert dist_cross.mean <= dist_coloc.mean
    assert dist_cross.mass == pytest.approx(1.0, abs=1e-12)
    assert dist_cross.max_mass_balance_error < 1e-13


def test_reflection_mirror_symmetry() -> None:
    chain = build_chain(7, 0.45, 0.7)
    left = exact_distribution(chain, (2, 6), survival_tol=1e-13, max_t=50_000)
    right = exact_distribution(chain, (6, 2), survival_tol=1e-13, max_t=50_000)

    assert left.f == pytest.approx(right.f, abs=1e-13)
    assert left.f_by_k == pytest.approx(right.f_by_k[:, ::-1], abs=1e-13)


def test_stage2_rejects_stage1_parity_control() -> None:
    chain = build_chain(21, 0.02, 0.9)
    dist = exact_distribution(chain, (6, 2), survival_tol=1e-12, max_t=30_000)
    diag = diagnose_curve(dist.f)

    assert diag.raw_peaks[:5] == (4, 6, 8, 10, 12)
    assert len(diag.f2_peaks) == 1
    assert diag.label == "artifact"
    assert diag.artifact_reason == "ballistic_short_distance"


def test_stage2b_f2_double_peak_gate_requires_visible_valley() -> None:
    true_two_peak = np.array([0.0, 1.0, 0.72, 0.35, 0.42, 0.62, 0.55, 0.2])
    shoulder_without_valley = np.array([0.0, 1.0, 0.96, 0.93, 0.91, 0.89, 0.83, 0.7])

    assert f2_has_true_double_peak(true_two_peak)
    assert not f2_has_true_double_peak(shoulder_without_valley)


@pytest.mark.parametrize("z", [0.2, 0.5, 0.8, 0.95])
def test_small_n_determinant_green_formula(z: float) -> None:
    chain = build_chain(5, 0.4, 0.9)
    absorbing = absorbing_pgf_total(chain, (1, 5), z)
    determinant = determinant_pgf_total(5, 0.4, 0.9, (1, 5), z)

    assert absorbing == pytest.approx(determinant, abs=1e-11)
