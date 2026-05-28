from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

from vkcore.ring.two_target import (  # noqa: E402
    RingTwoTargetConfig,
    build_transition_matrix,
    exact_two_target_fpt,
    validate_result,
)
from vkcore.validation import check_channel_decomposition, check_row_stochastic  # noqa: E402


def test_ring_two_target_transition_matrix_is_valid_and_absorbing() -> None:
    cfg = RingTwoTargetConfig(
        L=7,
        start=0,
        target1=2,
        target2=5,
        K=2,
        q=0.8,
        drift=0.25,
    )
    P = build_transition_matrix(cfg)

    assert check_row_stochastic(P)
    assert P[cfg.target1, cfg.target1] == pytest.approx(1.0)
    assert P[cfg.target2, cfg.target2] == pytest.approx(1.0)
    assert P[cfg.target1].sum() == pytest.approx(1.0)
    assert P[cfg.target2].sum() == pytest.approx(1.0)


def test_small_ring_exact_channel_decomposition_and_mass_balance() -> None:
    cfg = RingTwoTargetConfig(
        L=5,
        start=0,
        target1=1,
        target2=3,
        K=2,
        q=1.0,
        drift=0.0,
        max_steps=8,
    )
    result = exact_two_target_fpt(cfg)
    errors = validate_result(result)

    assert result.f_total[0] == pytest.approx(0.0)
    assert result.survival[0] == pytest.approx(1.0)
    assert result.f_target1[1] == pytest.approx(0.5)
    assert result.f_target2[1] == pytest.approx(0.0)
    assert result.f_target2[2] == pytest.approx(0.25)
    assert check_channel_decomposition(
        result.f_total,
        [result.f_target1, result.f_target2],
        tol=1e-12,
    )
    assert errors["row_stochasticity_error"] < 1e-12
    assert errors["mass_balance_error"] < 1e-10
    assert errors["channel_decomposition_error"] < 1e-10


def test_start_must_not_be_absorbing_target() -> None:
    cfg = RingTwoTargetConfig(L=5, start=1, target1=1, target2=3)
    with pytest.raises(ValueError, match="start not in absorbing targets"):
        build_transition_matrix(cfg)
