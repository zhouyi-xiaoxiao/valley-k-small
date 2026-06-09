"""Edge-parameter guardrail tests added by the 2026-06-09 audit.

Covers the gaps the audit found untested: double-axis reflecting corners on
the 2D grid, the bias_strength = 1-q boundary, and the ring shortcut at the
beta = 1 extreme. All cases must keep kernels row-stochastic and nonnegative
and keep the two-target decomposition identity exact.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

from vkcore.grid2d.two_target_bias_radius import build_reflecting_kernel
from vkcore.ring.two_target import RingTwoTargetConfig, exact_two_target_fpt


def test_grid2d_corner_cells_reflect_on_both_axes() -> None:
    # 3x3 grid, q=1 (no stay mass): every corner must push two of its four
    # moves back onto itself via attempted-outside-stays reflection.
    kernel = build_reflecting_kernel(
        Lx=3,
        Ly=3,
        q=1.0,
        bias_strength=0.0,
        bias_direction="E",
        absorbing=[],
    )
    assert float(np.min(kernel.prob)) >= 0.0
    assert float(np.max(np.abs(kernel.row_sums() - 1.0))) < 1e-12

    corner = kernel.index((0, 0))
    rows = np.where(kernel.src == corner)[0]
    self_mass = float(kernel.prob[rows[np.where(kernel.dst[rows] == corner)[0][0]]])
    # W and S moves both reflect back: 2 * q/4 = 0.5 self mass.
    assert abs(self_mass - 0.5) < 1e-12


def test_grid2d_bias_at_upper_bound_keeps_rows_stochastic() -> None:
    # bias_strength exactly at the documented 1-q ceiling: stay mass hits 0,
    # rows must still sum to one with no negative entries.
    kernel = build_reflecting_kernel(
        Lx=4,
        Ly=4,
        q=0.6,
        bias_strength=0.4,
        bias_direction="N",
        absorbing=[(1, 1)],
    )
    assert float(np.min(kernel.prob)) >= 0.0
    assert float(np.max(np.abs(kernel.row_sums() - 1.0))) < 1e-12


def test_ring_shortcut_extreme_beta_keeps_guardrails() -> None:
    # beta=1 moves the full stay mass through the shortcut; the kernel must
    # stay a proper stochastic matrix and the decomposition must stay exact.
    cfg = RingTwoTargetConfig(
        L=12,
        start=0,
        target1=3,
        target2=9,
        K=2,
        q=0.5,
        beta=1.0,
        shortcut_src=1,
        shortcut_dst=8,
        max_steps=400,
    )
    result = exact_two_target_fpt(cfg)
    assert result.row_stochasticity_error() < 1e-12
    assert float(np.min(result.transition_matrix)) >= 0.0
    assert result.channel_decomposition_error() < 1e-12
    assert result.mass_balance_error() < 1e-12
    # Shortcut source row keeps no stay mass at beta=1.
    src = 1
    assert result.transition_matrix[src, src] < 1e-15
    assert result.transition_matrix[src, 8] > 0.0
