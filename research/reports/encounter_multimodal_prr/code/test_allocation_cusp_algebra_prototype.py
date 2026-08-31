from __future__ import annotations

import allocation_cusp_algebra_prototype as prototype
import numpy as np
from numpy.testing import assert_allclose


def test_basis_is_fixed_budget_and_euclidean_orthonormal() -> None:
    model = prototype.build_prototype()
    assert_allclose(np.ones(4) @ model.tangent_basis, np.zeros(2), atol=2.0e-16)
    assert_allclose(model.tangent_basis.T @ model.tangent_basis, np.eye(2), atol=3.0e-16)
    assert_allclose(model.free_row_generator @ np.ones(5), np.zeros(5), atol=2.0e-16)


def test_explicit_csr_state_tangents_match_allocation_finite_differences() -> None:
    model = prototype.build_prototype()
    time = 1.37
    theta = np.asarray((0.017, -0.013))
    observed = prototype.snapshot(model, time, theta)
    step = 2.0e-5
    for index in range(2):
        increment = np.zeros(2)
        increment[index] = step
        _weights_plus, _kappa_plus, row_plus, _tangents_plus = prototype.operators(
            model, theta + increment
        )
        _weights_minus, _kappa_minus, row_minus, _tangents_minus = prototype.operators(
            model, theta - increment
        )
        from scipy.sparse.linalg import expm_multiply

        state_plus = expm_multiply(time * row_plus.T, model.initial)
        state_minus = expm_multiply(time * row_minus.T, model.initial)
        finite_difference = (state_plus - state_minus) / (2.0 * step)
        assert_allclose(observed.tangents[index], finite_difference, rtol=2.0e-9, atol=2.0e-11)


def test_direct_terms_and_mixed_jets_through_f_ttt_theta() -> None:
    model = prototype.build_prototype()
    time = 1.37
    theta = np.asarray((0.017, -0.013))
    observed = prototype.snapshot(model, time, theta)
    step = 2.0e-5
    for index in range(2):
        increment = np.zeros(2)
        increment[index] = step
        plus = prototype.direct_time_jets(model, time, theta + increment)
        minus = prototype.direct_time_jets(model, time, theta - increment)
        finite_difference = (plus - minus) / (2.0 * step)
        # Orders 0--3 include the observable direct term and f_ttt,theta.
        assert_allclose(
            observed.allocation_time_jets[index, :4],
            finite_difference[:4],
            rtol=4.0e-8,
            atol=3.0e-11,
        )


def test_complete_cusp_jacobian_and_fold_null_direction() -> None:
    model = prototype.build_prototype()
    observed = prototype.snapshot(model, 1.37, np.asarray((0.017, -0.013)))
    finite_difference = prototype.finite_difference_cusp_jacobian(
        model,
        observed.time,
        observed.theta,
    )
    assert_allclose(observed.cusp_jacobian, finite_difference, rtol=4.0e-8, atol=5.0e-11)

    fold_jacobian = observed.cusp_jacobian[:2]
    _left, singular_values, right = np.linalg.svd(fold_jacobian)
    tangent = right[-1]
    assert singular_values[-1] > 1.0e-5
    assert np.linalg.norm(fold_jacobian @ tangent) <= 2.0e-15
