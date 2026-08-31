from __future__ import annotations

import math
from fractions import Fraction

import gmpy2
import numpy as np
import pytest
import verified_uniformization_enclosure as verified
from scipy import sparse
from scipy.linalg import expm


def mpfr_exp_interval(value: Fraction, precision: int = 256) -> tuple[float, float]:
    lo = verified._mpfr_from_fraction(value, precision, gmpy2.RoundDown)
    hi = verified._mpfr_from_fraction(value, precision, gmpy2.RoundUp)
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=gmpy2.RoundDown):
        exp_lo = gmpy2.exp(lo)
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=gmpy2.RoundUp):
        exp_hi = gmpy2.exp(hi)
    return verified._mpfr_to_float_lower(exp_lo), verified._mpfr_to_float_upper(exp_hi)


def test_one_state_death_contains_directed_mpfr_reference() -> None:
    q = sparse.csr_matrix([[-0.3]])
    kernel = verified.build_exact_dyadic_kernel(q)
    state = verified.propagate_verified(kernel, [1.0], 7.25, mean_cap=1.0)
    exponent = -Fraction.from_float(0.3) * Fraction.from_float(7.25)
    reference_lo, reference_hi = mpfr_exp_interval(exponent)
    lower = state.nominal[0] - state.l1_error
    upper = state.nominal[0] + state.l1_error
    assert lower <= reference_lo <= reference_hi <= upper
    assert state.elapsed_time == Fraction.from_float(7.25)
    assert state.l1_error < 2.0e-13


def test_two_state_birth_and_killing_contains_closed_form() -> None:
    a = 0.25
    b = 0.4
    q = sparse.csr_matrix([[-a, a], [0.0, -b]])
    kernel = verified.build_exact_dyadic_kernel(q)
    time = 3.0
    state = verified.propagate_verified(kernel, [1.0, 0.0], time, mean_cap=0.7)
    p1 = math.exp(-a * time)
    p2 = a / (b - a) * (math.exp(-a * time) - math.exp(-b * time))
    reference = np.asarray([p1, p2])
    assert np.sum(np.abs(state.nominal - reference)) <= state.l1_error + 3.0e-15
    assert state.l1_error < 2.0e-13


def test_scalar_and_generator_actions_cover_dense_reference() -> None:
    q_dense = np.asarray([[-0.25, 0.25], [0.0, -0.4]])
    kernel = verified.build_exact_dyadic_kernel(sparse.csr_matrix(q_dense))
    state = verified.propagate_verified(kernel, [1.0, 0.0], 1.75, mean_cap=0.5)
    killing = np.asarray([0.0, 0.4])
    rows = verified.enclose_actions_and_scalars(kernel, state, killing, maximum_order=3)
    exact_state = np.asarray(
        [
            math.exp(-0.25 * 1.75),
            0.25 / 0.15 * (math.exp(-0.25 * 1.75) - math.exp(-0.4 * 1.75)),
        ]
    )
    z = exact_state.copy()
    for order, row in enumerate(rows):
        scalar = float(killing @ z)
        assert row.order == order
        assert row.scalar_lower <= scalar <= row.scalar_upper
        assert np.sum(np.abs(row.nominal_action - z)) <= row.action_l1_error + 5.0e-14
        assert row.m_upper >= float(np.max(killing) * np.sum(np.abs(z)))
        z = q_dense.T @ z


@pytest.mark.parametrize(
    "q",
    [
        [[-1.0, 1.1], [0.0, -0.2]],
        [[-1.0, -0.1], [0.0, -0.2]],
        [[0.1, 0.0], [0.0, -0.2]],
    ],
)
def test_generator_structure_mutations_fail_closed(q: list[list[float]]) -> None:
    with pytest.raises(verified.VerificationFailure):
        verified.build_exact_dyadic_kernel(sparse.csr_matrix(q))


def test_rate_and_poisson_caps_fail_closed() -> None:
    q = sparse.csr_matrix([[-0.3]])
    with pytest.raises(verified.VerificationFailure):
        verified.build_exact_dyadic_kernel(q, rate=0.2)
    kernel = verified.build_exact_dyadic_kernel(q)
    with pytest.raises(verified.VerificationFailure):
        verified.propagate_verified(kernel, [1.0], 10.0, max_terms=2)
    with pytest.raises(verified.VerificationFailure):
        verified.poisson_enclosure(Fraction(1), Fraction(1, 10), precision_bits=64)


def test_exact_time_partition_and_sequential_contraction_ledger() -> None:
    q = sparse.csr_matrix([[-0.7, 0.2], [0.0, -0.3]])
    kernel = verified.build_exact_dyadic_kernel(q)
    direct = verified.propagate_verified(kernel, [0.8, 0.2], 4.1, mean_cap=0.4)
    first = verified.propagate_verified(kernel, [0.8, 0.2], 1.3, mean_cap=0.4)
    second_duration = Fraction.from_float(4.1) - Fraction.from_float(1.3)
    sequential = verified.uniformization_chunk(
        kernel,
        first,
        second_duration,
        tail_tolerance=Fraction(1, 10**18),
    )
    distance = float(np.sum(np.abs(direct.nominal - sequential.nominal)))
    assert distance <= direct.l1_error + sequential.l1_error
    assert sequential.elapsed_time == Fraction.from_float(4.1)


def test_pairwise_dot_roundoff_bound_covers_exact_fraction_dot() -> None:
    left = np.asarray([1.0, 1.0e16, -1.0e16, 3.0, -2.0])
    right = np.asarray([0.1, 1.0, 1.0, -0.2, 0.4])
    nominal, radius = verified.pairwise_dot(left, right)
    exact = sum(
        (
            Fraction.from_float(float(a)) * Fraction.from_float(float(b))
            for a, b in zip(left, right)
        ),
        Fraction(0),
    )
    assert abs(Fraction.from_float(nominal) - exact) <= Fraction.from_float(radius)


def test_rate_rebuild_closes_rounded_diagonal_and_carries_perturbation() -> None:
    # The supplied diagonal is deliberately meaningless; only exact dyadic
    # off-diagonal rates and killing define the target killed generator.
    free = sparse.csr_matrix([[99.0, 0.1, 0.2], [0.0, 99.0, 0.25], [0.0, 0.0, 99.0]])
    rebuilt = verified.rebuild_killed_generator_from_rates(free, [0.0, 0.4, 0.3])
    assert rebuilt.induced_l1_radius > 0.0
    kernel = verified.build_exact_dyadic_kernel(
        rebuilt.center,
        target_q_induced_uncertainty=rebuilt.induced_l1_radius,
    )
    state = verified.propagate_verified(kernel, [1.0, 0.0, 0.0], 2.0, mean_cap=0.4)
    target = np.asarray(
        [
            [-(0.1 + 0.2), 0.1, 0.2],
            [0.0, -(0.25 + 0.4), 0.25],
            [0.0, 0.0, -0.3],
        ]
    )
    reference = expm(2.0 * target.T) @ np.asarray([1.0, 0.0, 0.0])
    assert np.sum(np.abs(state.nominal - reference)) <= state.l1_error + 2.0e-14


def test_seeded_small_killed_chains_against_independent_dense_expm() -> None:
    rng = np.random.default_rng(20260714)
    for states in (3, 4, 6):
        rates = rng.uniform(0.0, 0.2, size=(states, states))
        rates[rng.uniform(size=(states, states)) < 0.45] = 0.0
        np.fill_diagonal(rates, 99.0)
        killing = rng.uniform(0.01, 0.15, size=states)
        rebuilt = verified.rebuild_killed_generator_from_rates(sparse.csr_matrix(rates), killing)
        kernel = verified.build_exact_dyadic_kernel(
            rebuilt.center,
            target_q_induced_uncertainty=rebuilt.induced_l1_radius,
        )
        initial = rng.uniform(size=states)
        initial /= np.sum(initial)
        time = float(rng.uniform(0.2, 3.0))
        enclosed = verified.propagate_verified(kernel, initial, time, mean_cap=0.7)
        target = rates.copy()
        for row in range(states):
            target[row, row] = -math.fsum(
                [killing[row], *[rates[row, col] for col in range(states) if col != row]]
            )
        reference = expm(time * target.T) @ initial
        assert np.sum(np.abs(enclosed.nominal - reference)) <= enclosed.l1_error + 5.0e-14


def test_large_mean_poisson_tail_is_certified_without_binary64_exp() -> None:
    weights = verified.poisson_enclosure(Fraction(500), Fraction(1, 10**20), precision_bits=192)
    assert weights.midpoint.size > 500
    assert weights.tail_upper <= 1.0e-20
    assert np.all(weights.midpoint >= 0.0)
    assert np.all(weights.radius >= 0.0)
