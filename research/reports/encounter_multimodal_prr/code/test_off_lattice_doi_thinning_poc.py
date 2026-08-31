from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import off_lattice_doi_thinning_poc as thinning  # noqa: E402


def test_binary64_bump_normalization_matches_independent_quadrature() -> None:
    observed, error = quad(
        lambda value: math.exp(-1.0 / (1.0 - value * value)),
        -1.0,
        1.0,
        epsabs=2.0e-14,
        epsrel=2.0e-14,
        limit=300,
    )
    assert error < 2.0e-13
    assert observed == pytest.approx(thinning.BASE_BUMP_INTEGRAL, abs=2.0e-14)


def test_frozen_lambda_has_an_analytic_strict_margin() -> None:
    parameters = thinning.BroadFourSlabParameters()
    bound = thinning.analytic_killing_bound(parameters)
    assert bound == pytest.approx(0.12452905643850211, rel=2.0e-15)
    assert bound < thinning.FROZEN_LAMBDA
    assert thinning.exact_profile_maximum(parameters) < bound

    for centre, weight in zip(parameters.patch_centres, parameters.weights, strict=True):
        state = thinning.QuotientState(centre, 0.0, 0.0)
        expected = (
            parameters.budget
            * weight
            * math.exp(-1.0)
            / (
                parameters.transverse_width
                * parameters.patch_half_width
                * thinning.BASE_BUMP_INTEGRAL
            )
        )
        assert thinning.broad_four_slab_killing_rate(state, parameters) == pytest.approx(
            expected,
            rel=2.0e-15,
        )
        assert expected < thinning.FROZEN_LAMBDA


def test_contact_boundary_is_unsmoothed_and_boundary_convention_is_measure_zero() -> None:
    parameters = thinning.BroadFourSlabParameters()
    centre = parameters.patch_centres[0]
    inside = thinning.QuotientState(centre, np.nextafter(parameters.contact_radius, 0.0), 0.0)
    boundary = thinning.QuotientState(centre, parameters.contact_radius, 0.0)
    outside = thinning.QuotientState(
        centre,
        np.nextafter(parameters.contact_radius, math.inf),
        0.0,
    )
    assert thinning.broad_four_slab_killing_rate(inside, parameters) > 0.0
    assert thinning.broad_four_slab_killing_rate(boundary, parameters) == 0.0
    assert thinning.broad_four_slab_killing_rate(outside, parameters) == 0.0


class _FixedNormals:
    def __init__(self, values: tuple[float, float, float]) -> None:
        self._values = iter(values)

    def standard_normal(self) -> float:
        return next(self._values)


def test_free_transition_uses_the_exact_ou_and_wrapped_brownian_formula() -> None:
    parameters = thinning.BroadFourSlabParameters()
    state = thinning.QuotientState(0.2, -0.3, 0.49)
    delta = 1.7
    normals = (0.25, -0.5, 1.25)
    observed = thinning.free_transition(  # type: ignore[arg-type]
        state,
        delta,
        _FixedNormals(normals),
        parameters,
    )
    decay = math.exp(-parameters.ou_stiffness * delta)
    factor = -math.expm1(-2.0 * parameters.ou_stiffness * delta)
    midpoint_variance = parameters.particle_diffusion * factor / (2.0 * parameters.ou_stiffness)
    relative_variance = 2.0 * parameters.particle_diffusion * factor / parameters.ou_stiffness
    expected = thinning.QuotientState(
        parameters.ou_mean
        + decay * (state.midpoint - parameters.ou_mean)
        + math.sqrt(midpoint_variance) * normals[0],
        decay * state.relative_parallel + math.sqrt(relative_variance) * normals[1],
        thinning.wrap_periodic(
            state.relative_perp
            + math.sqrt(4.0 * parameters.particle_diffusion * delta) * normals[2],
            parameters.transverse_width,
        ),
    )
    assert observed == expected
    assert (
        thinning.free_transition(  # type: ignore[arg-type]
            state,
            0.0,
            _FixedNormals(normals),
            parameters,
        )
        is state
    )


def test_path_keyed_philox_is_traversal_and_batch_invariant() -> None:
    parameters = thinning.BroadFourSlabParameters()
    ids = list(range(12))
    forward = thinning.simulate_ensemble(
        ids,
        master_seed=711,
        replicate_id=3,
        horizon=8.0,
        parameters=parameters,
        rate_function=thinning.constant_rate_function(0.05),
    )
    reverse = thinning.simulate_ensemble(
        reversed(ids),
        master_seed=711,
        replicate_id=3,
        horizon=8.0,
        parameters=parameters,
        rate_function=thinning.constant_rate_function(0.05),
    )
    assert {record.trajectory_id: record for record in forward} == {
        record.trajectory_id: record for record in reverse
    }
    changed_replicate = thinning.simulate_ensemble(
        ids,
        master_seed=711,
        replicate_id=4,
        horizon=8.0,
        parameters=parameters,
        rate_function=thinning.constant_rate_function(0.05),
    )
    assert forward != changed_replicate


def test_initial_compact_product_samples_remain_inside_declared_supports() -> None:
    parameters = thinning.BroadFourSlabParameters()
    for trajectory_id in range(128):
        state = thinning.sample_initial_state(
            thinning.trajectory_rng(123, 0, trajectory_id),
            parameters,
        )
        assert abs(state.midpoint - parameters.midpoint_start) < parameters.initial_half_width
        assert (
            abs(state.relative_parallel - parameters.relative_parallel_start)
            < parameters.initial_half_width
        )
        assert (
            abs(thinning.wrap_periodic(state.relative_perp, parameters.transverse_width))
            < parameters.initial_half_width
        )


def test_constant_hazard_thinning_matches_analytic_survival_inside_dkw_band() -> None:
    parameters = thinning.BroadFourSlabParameters()
    sample_size = 4096
    hazard = 0.05
    horizon = 30.0
    records = thinning.simulate_ensemble(
        range(sample_size),
        master_seed=99173,
        replicate_id=0,
        horizon=horizon,
        parameters=parameters,
        rate_function=thinning.constant_rate_function(hazard),
    )
    events = thinning.event_time_array(records)
    times = np.asarray((1.0, 3.0, 7.0, 15.0, 30.0))
    observed = thinning.survival_estimates(events, times)
    expected = np.exp(-hazard * times)
    radius = thinning.dkw_half_width(sample_size, 1.0e-6)
    assert np.max(np.abs(observed - expected)) < radius


def test_estimators_close_the_censored_partition_and_keep_exact_counts() -> None:
    events = np.asarray((0.5, 1.0, 2.0, 3.0, math.inf, math.inf))
    assert thinning.basin_counts(events, (1.0, 2.5), 4.0) == [2, 1, 1]
    assert thinning.window_counts(events, (0.5, 2.0, 3.0), 0.2) == [1, 1, 1]
    survival = thinning.survival_estimates(events, np.asarray((1.0, 2.5, 4.0)))
    assert np.array_equal(survival, np.asarray((4 / 6, 3 / 6, 2 / 6)))
    assert (
        sum(thinning.basin_counts(events, (1.0, 2.5), 4.0)) + int(np.count_nonzero(events > 4.0))
        == events.size
    )


def test_power_plan_is_margin_aware_and_not_mislabeled_as_a_run() -> None:
    mass_floor = 0.005
    alternative = 0.005307459366939327
    alpha = 0.02 / 3.0
    production_size = 6_000_000
    power = thinning.mass_detection_power(production_size, mass_floor, alternative, alpha)
    assert power > 0.999
    precision = thinning.nominal_cp_precision_at_size(
        production_size,
        mass_floor,
        alternative,
        alpha,
        0.25,
    )
    assert precision["quarter_margin_passed"]
    assert precision["maximum_radius"] < precision["quarter_margin_target_radius"]

    probabilities = (
        0.0014755815480296034,
        0.0012142342225729486,
        0.0017866740292924895,
        0.0014651531386407997,
        0.0017189852933621585,
    )
    pairs = (
        (probabilities[0], probabilities[1]),
        (probabilities[2], probabilities[1]),
        (probabilities[2], probabilities[3]),
        (probabilities[4], probabilities[3]),
    )
    assert thinning.conservative_joint_contrast_certificate(
        production_size,
        pairs,
        inference_alpha=0.02,
        target_power=0.90,
    )


def test_fail_closed_rate_bound_has_no_clipping_fallback() -> None:
    parameters = thinning.BroadFourSlabParameters()
    with pytest.raises(RuntimeError, match="does not dominate"):
        thinning.simulate_trajectory(
            master_seed=10,
            replicate_id=0,
            trajectory_id=0,
            horizon=100.0,
            parameters=parameters,
            lambda_rate=1.0,
            rate_function=thinning.constant_rate_function(2.0),
        )
