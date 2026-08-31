"""Independent Round-118 adversarial checks for the exact-m B=0 theorem.

These tests deliberately remain at zero reaction budget.  They stress algebraic
invariants used by the proof and kill two tempting proof mutations; they are
not interval certificates and are not evidence about the killed process.
"""

from __future__ import annotations

import math

import numpy as np
import pytest


def _posterior_mean(
    x: np.ndarray, centres: np.ndarray, weights: np.ndarray, sigma: float
) -> np.ndarray:
    log_terms = (
        np.log(weights)[None, :]
        - 0.5 * ((x[:, None] - centres[None, :]) / sigma) ** 2
    )
    log_terms -= np.max(log_terms, axis=1, keepdims=True)
    posterior = np.exp(log_terms)
    posterior /= np.sum(posterior, axis=1, keepdims=True)
    return posterior @ centres


@pytest.mark.parametrize("sigma", [0.12, 0.07, 0.04])
def test_weighted_crossover_has_exact_one_ninth_and_nine_odds(sigma: float) -> None:
    centres = np.array([-1.1, -0.25, 0.55, 1.25])
    weights = np.array([0.03, 0.61, 0.07, 0.29])
    for index in range(len(centres) - 1):
        left_c = centres[index]
        right_c = centres[index + 1]
        delta = right_c - left_c
        weighted = (left_c + right_c) / 2 + sigma**2 / delta * math.log(
            weights[index] / weights[index + 1]
        )
        half_width = sigma**2 * math.log(9.0) / delta

        def odds(x: float) -> float:
            log_odds = (
                math.log(weights[index + 1] / weights[index])
                + delta * (x - (left_c + right_c) / 2) / sigma**2
            )
            return math.exp(log_odds)

        assert odds(weighted - half_width) == pytest.approx(1 / 9, rel=2e-13)
        assert odds(weighted) == pytest.approx(1.0, rel=2e-13)
        assert odds(weighted + half_width) == pytest.approx(9.0, rel=2e-13)


def test_unweighted_crossover_mutation_is_killed_by_edge_weight_case() -> None:
    centres = np.array([-0.8, 0.7])
    weights = np.array([0.03, 0.97])
    sigma = 0.11
    delta = centres[1] - centres[0]
    midpoint = float(np.mean(centres))
    weighted = midpoint + sigma**2 / delta * math.log(weights[0] / weights[1])

    def odds(x: float) -> float:
        return math.exp(
            math.log(weights[1] / weights[0])
            + delta * (x - midpoint) / sigma**2
        )

    assert odds(weighted) == pytest.approx(1.0, rel=2e-13)
    assert odds(midpoint) == pytest.approx(0.97 / 0.03, rel=2e-13)
    assert abs(odds(midpoint) - 1.0) > 30.0


def test_fixed_sigma2_crossover_edge_is_not_exp_inverse_sigma_squared() -> None:
    # The Round-112 proof mutation called this ratio exp(-q/sigma^2).
    # At x=s-C*sigma^2/delta it is instead exactly exp(-C), for every sigma.
    constant = 4.25
    observed = []
    for sigma in (0.2, 0.1, 0.05, 0.025):
        delta = 0.73
        s = 0.17
        x = s - constant * sigma**2 / delta
        observed.append(math.exp(delta * (x - s) / sigma**2))
    assert observed == pytest.approx([math.exp(-constant)] * 4, rel=2e-13)


def test_outer_tail_sign_uses_convex_hull_and_cannot_flip() -> None:
    centres = np.array([-1.1, -0.25, 0.55, 1.25])
    weights = np.array([0.999, 0.0003, 0.0002, 0.0005])
    sigma = 0.16
    x = np.array([-2.0, -1.4, 1.5, 2.0])
    means = _posterior_mean(x, centres, weights, sigma)
    slopes = (means - x) / sigma**2
    assert np.all(slopes[:2] > 0.0)
    assert np.all(slopes[2:] < 0.0)


def test_seeded_extreme_weight_and_slow_factor_family_has_exact_signature() -> None:
    rng = np.random.default_rng(118)
    for _ in range(64):
        mode_count = int(rng.integers(1, 7))
        gaps = rng.uniform(0.35, 1.1, size=max(0, mode_count - 1))
        centres = (
            np.concatenate(([0.0], np.cumsum(gaps)))
            if mode_count > 1
            else np.array([0.0])
        )
        centres -= np.mean(centres)
        raw_weights = 10 ** rng.uniform(-3.0, 0.0, size=mode_count)
        weights = raw_weights / np.sum(raw_weights)
        minimum_gap = float(np.min(gaps)) if mode_count > 1 else 1.0
        sigma = 0.025 * minimum_gap

        harmonics = np.arange(1.0, 5.0)
        amplitudes = rng.uniform(-0.6, 0.6, size=4)
        phases = rng.uniform(-math.pi, math.pi, size=4)
        x = np.linspace(
            centres[0] - 1.1 * minimum_gap,
            centres[-1] + 1.1 * minimum_gap,
            50_001,
        )
        means = _posterior_mean(x, centres, weights, sigma)
        slow_log_slope = sum(
            amplitudes[index]
            * harmonics[index]
            * np.cos(harmonics[index] * x + phases[index])
            for index in range(4)
        )
        derivative = slow_log_slope + (means - x) / sigma**2
        strict_crossings = int(
            np.count_nonzero(derivative[:-1] * derivative[1:] < 0.0)
        )

        assert derivative[0] > 0.0
        assert derivative[-1] < 0.0
        assert strict_crossings == 2 * mode_count - 1
