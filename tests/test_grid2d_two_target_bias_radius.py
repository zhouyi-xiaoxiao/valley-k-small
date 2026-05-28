from __future__ import annotations

from math import pi
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

from vkcore.grid2d.two_target_bias_radius import (
    build_reflecting_kernel,
    exact_near_far_decomposition,
    near_target_candidates,
    validation_errors,
)


def test_reflecting_kernel_is_nonnegative_row_stochastic_and_absorbing() -> None:
    near = (2, 3)
    far = (4, 2)
    kernel = build_reflecting_kernel(
        Lx=5,
        Ly=4,
        q=0.6,
        bias_strength=0.15,
        bias_direction="E",
        absorbing=[near, far],
    )

    assert float(np.min(kernel.prob)) >= 0.0
    assert float(np.max(np.abs(kernel.row_sums() - 1.0))) < 1e-12

    for target in (near, far):
        i = kernel.index(target)
        rows = np.where(kernel.src == i)[0]
        assert rows.size == 1
        assert int(kernel.dst[rows[0]]) == i
        assert float(kernel.prob[rows[0]]) == 1.0


def test_near_target_candidates_record_radius_and_relative_theta() -> None:
    candidates = near_target_candidates(
        Lx=7,
        Ly=7,
        start=(3, 3),
        radii=[2.0],
        thetas=[0.0, pi / 2],
        bias_direction="E",
        exclude=[],
    )

    assert [c.coord for c in candidates] == [(5, 3), (3, 5)]
    assert candidates[0].r_actual == 2.0
    assert abs(candidates[0].theta_actual) < 1e-12
    assert abs(candidates[1].theta_actual - pi / 2) < 1e-12


def test_exact_near_far_decomposition_satisfies_mass_balance() -> None:
    start = (1, 2)
    near = (3, 2)
    far = (4, 3)
    kernel = build_reflecting_kernel(
        Lx=5,
        Ly=5,
        q=0.7,
        bias_strength=0.1,
        bias_direction="E",
        absorbing=[near, far],
    )
    decomp = exact_near_far_decomposition(
        kernel=kernel,
        start=start,
        near_target=near,
        far_target=far,
        t_max=80,
    )
    errors = validation_errors(kernel, decomp)

    assert errors["nonnegative_min_probability"] >= 0.0
    assert errors["row_stochasticity_error"] < 1e-12
    assert errors["mass_balance_error"] < 1e-10
    assert errors["decomposition_error"] < 1e-10
    assert np.allclose(decomp.f_total, decomp.f_near + decomp.f_far)
    assert decomp.f_near.sum() > 0.0
    assert decomp.f_far.sum() > 0.0
