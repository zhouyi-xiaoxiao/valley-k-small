#!/usr/bin/env python3
"""Transition-exact off-lattice Doi thinning proof of principle.

This file is deliberately independent of the finite-volume implementation.  It
contains no grid, reflecting boundary, Scharfetter--Gummel flux, cut-cell
contact fraction, or matrix exponential.  The proof-of-principle command is a
method check only; it does not produce manuscript or publication evidence.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.stats import beta, binom

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OUTPUT = REPORT / "scratch" / "off_lattice_doi_thinning_poc_result.json"

# Integral of exp[-1/(1-u^2)] over (-1,1), independently evaluated at high
# precision and rounded to binary64.  Sampling from the same bump does not use
# this number: the rejection sampler normalizes itself.  The hazard evaluation
# needs it only as a deterministic representation of the continuous profile.
BASE_BUMP_INTEGRAL = 0.4439938161680794

# The elementary proof in ``analytic_killing_bound`` gives 0.1245291... for
# the frozen broad-four-slab inputs.  This deliberately rounded-up homogeneous
# candidate rate is not tuned to sampled paths.
FROZEN_LAMBDA = 0.13


@dataclass(frozen=True)
class BroadFourSlabParameters:
    """Continuous unbounded-cylinder inputs shared with the broad FV family."""

    particle_diffusion: float = 0.002
    ou_stiffness: float = 0.1
    ou_mean: float = 0.95
    transverse_width: float = 1.0
    contact_radius: float = 0.16
    midpoint_start: float = 0.14
    relative_parallel_start: float = -0.35
    relative_perp_start: float = 0.0
    initial_half_width: float = 0.02
    patch_centres: tuple[float, float, float, float] = (0.35, 0.60, 0.75, 0.90)
    patch_half_width: float = 0.04
    weights: tuple[float, float, float, float] = (
        0.28,
        0.27736690132708747,
        0.0857172266153233,
        0.3569158720575891,
    )
    budget: float = 0.01

    def __post_init__(self) -> None:
        positive = (
            self.particle_diffusion,
            self.ou_stiffness,
            self.transverse_width,
            self.contact_radius,
            self.initial_half_width,
            self.patch_half_width,
            self.budget,
        )
        if not all(math.isfinite(value) and value > 0.0 for value in positive):
            raise ValueError("all scale, diffusion, stiffness, and budget inputs must be positive")
        if self.contact_radius >= 0.5 * self.transverse_width:
            raise ValueError("the contact disk must not reach the torus cut locus")
        if 2.0 * self.initial_half_width >= self.transverse_width:
            raise ValueError("the periodic initial bump must fit inside one period")
        centres = np.asarray(self.patch_centres, dtype=float)
        weights = np.asarray(self.weights, dtype=float)
        if centres.shape != (4,) or weights.shape != (4,):
            raise ValueError("exactly four slab centres and weights are required")
        if not np.all(np.diff(centres) > 2.0 * self.patch_half_width):
            raise ValueError("the analytic Lambda=0.13 proof requires disjoint slab supports")
        if np.min(weights) <= 0.0 or abs(float(np.sum(weights)) - 1.0) > 2.0e-14:
            raise ValueError("the four weights must be positive and sum to one")


@dataclass(frozen=True)
class QuotientState:
    midpoint: float
    relative_parallel: float
    relative_perp: float


@dataclass(frozen=True)
class TrajectoryRecord:
    trajectory_id: int
    event_time: float | None
    candidate_count: int
    maximum_rate_seen: float
    accepted_rate: float | None


RateFunction = Callable[[QuotientState, BroadFourSlabParameters], float]


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def wrap_periodic(value: float, period: float) -> float:
    """Return the representative in [-period/2, period/2)."""

    if not math.isfinite(value) or not math.isfinite(period) or period <= 0.0:
        raise ValueError("periodic wrapping requires finite input and positive period")
    return float((value + 0.5 * period) % period - 0.5 * period)


def unit_bump_value(value: float) -> float:
    """Unnormalised C-infinity compact bump on (-1,1)."""

    u = float(value)
    if not math.isfinite(u):
        raise ValueError("bump argument must be finite")
    if abs(u) >= 1.0:
        return 0.0
    return math.exp(-1.0 / (1.0 - u * u))


def normalized_bump_density(value: float, centre: float, half_width: float) -> float:
    if not math.isfinite(half_width) or half_width <= 0.0:
        raise ValueError("bump half-width must be positive")
    return unit_bump_value((float(value) - float(centre)) / half_width) / (
        half_width * BASE_BUMP_INTEGRAL
    )


def analytic_killing_bound(parameters: BroadFourSlabParameters) -> float:
    """Rigorous elementary bound for the disjoint normalized bumps.

    On |u| <= 1/2, the base bump is at least exp(-4/3), so its normalising
    integral I is at least exp(-4/3).  Its global numerator maximum is exp(-1).
    Thus phi_s <= exp(1/3)/s.  Disjoint supports mean at most one weighted bump
    is nonzero at any midpoint.
    """

    centres = np.asarray(parameters.patch_centres, dtype=float)
    if not np.all(np.diff(centres) > 2.0 * parameters.patch_half_width):
        raise ValueError("the disjoint-support bound does not apply")
    return float(
        parameters.budget
        * max(parameters.weights)
        * math.exp(1.0 / 3.0)
        / (parameters.transverse_width * parameters.patch_half_width)
    )


def exact_profile_maximum(parameters: BroadFourSlabParameters) -> float:
    """Binary64 evaluation of the known bump maximum; diagnostic, not the proof bound."""

    return float(
        parameters.budget
        * max(parameters.weights)
        * math.exp(-1.0)
        / (parameters.transverse_width * parameters.patch_half_width * BASE_BUMP_INTEGRAL)
    )


def broad_four_slab_killing_rate(
    state: QuotientState,
    parameters: BroadFourSlabParameters,
) -> float:
    """Evaluate the unsmoothed continuous Doi killing field."""

    transverse_distance = abs(wrap_periodic(state.relative_perp, parameters.transverse_width))
    contact_squared = state.relative_parallel**2 + transverse_distance**2
    if contact_squared >= parameters.contact_radius**2:
        return 0.0
    midpoint_profile = math.fsum(
        weight
        * normalized_bump_density(
            state.midpoint,
            centre,
            parameters.patch_half_width,
        )
        for weight, centre in zip(parameters.weights, parameters.patch_centres, strict=True)
    )
    return float(parameters.budget * midpoint_profile / parameters.transverse_width)


def trajectory_rng(master_seed: int, replicate_id: int, trajectory_id: int) -> np.random.Generator:
    """Return one path-keyed counter-based Philox stream.

    Distinct paths receive distinct 128-bit keys.  Consequently a trajectory's
    random stream is invariant to chunking, scheduling, or traversal order.
    """

    limit = 2**64
    for name, value in (
        ("master_seed", master_seed),
        ("replicate_id", replicate_id),
        ("trajectory_id", trajectory_id),
    ):
        if int(value) != value or not 0 <= value < limit:
            raise ValueError(f"{name} must be an integer in [0,2^64)")
    high_key = (int(master_seed) + int(replicate_id)) % limit
    key = np.asarray((int(trajectory_id), high_key), dtype=np.uint64)
    return np.random.Generator(np.random.Philox(key=key))


def sample_unit_bump(
    rng: np.random.Generator,
    *,
    maximum_attempts: int = 512,
) -> float:
    """Exact rejection sampler for the normalized compact bump shape."""

    if maximum_attempts < 1:
        raise ValueError("maximum_attempts must be positive")
    for _attempt in range(maximum_attempts):
        value = float(rng.uniform(-1.0, 1.0))
        if abs(value) >= 1.0:
            continue
        # Divide the target by its maximum exp(-1).  No numerical
        # normalization constant is needed for sampling.
        acceptance = math.exp(-(value * value) / (1.0 - value * value))
        if float(rng.random()) < acceptance:
            return value
    raise RuntimeError("compact-bump rejection cap reached; no fallback or biased sample used")


def sample_initial_state(
    rng: np.random.Generator,
    parameters: BroadFourSlabParameters,
) -> QuotientState:
    half_width = parameters.initial_half_width
    midpoint = parameters.midpoint_start + half_width * sample_unit_bump(rng)
    relative_parallel = parameters.relative_parallel_start + half_width * sample_unit_bump(rng)
    relative_perp = wrap_periodic(
        parameters.relative_perp_start + half_width * sample_unit_bump(rng),
        parameters.transverse_width,
    )
    return QuotientState(midpoint, relative_parallel, relative_perp)


def free_transition(
    state: QuotientState,
    delta: float,
    rng: np.random.Generator,
    parameters: BroadFourSlabParameters,
) -> QuotientState:
    """Exact free OU/wrapped-Brownian transition over one time increment."""

    dt = float(delta)
    if not math.isfinite(dt) or dt < 0.0:
        raise ValueError("transition time must be finite and nonnegative")
    if dt == 0.0:
        return state
    gamma = parameters.ou_stiffness
    diffusion = parameters.particle_diffusion
    decay = math.exp(-gamma * dt)
    one_minus_decay_squared = -math.expm1(-2.0 * gamma * dt)
    midpoint_variance = diffusion * one_minus_decay_squared / (2.0 * gamma)
    relative_parallel_variance = 2.0 * diffusion * one_minus_decay_squared / gamma
    midpoint = (
        parameters.ou_mean
        + decay * (state.midpoint - parameters.ou_mean)
        + math.sqrt(midpoint_variance) * float(rng.standard_normal())
    )
    relative_parallel = decay * state.relative_parallel + math.sqrt(
        relative_parallel_variance
    ) * float(rng.standard_normal())
    relative_perp = wrap_periodic(
        state.relative_perp + math.sqrt(4.0 * diffusion * dt) * float(rng.standard_normal()),
        parameters.transverse_width,
    )
    return QuotientState(midpoint, relative_parallel, relative_perp)


def simulate_trajectory(
    *,
    master_seed: int,
    replicate_id: int,
    trajectory_id: int,
    horizon: float,
    parameters: BroadFourSlabParameters,
    lambda_rate: float = FROZEN_LAMBDA,
    rate_function: RateFunction = broad_four_slab_killing_rate,
) -> TrajectoryRecord:
    """Simulate one killed path by homogeneous conditional thinning."""

    stop = float(horizon)
    candidate_rate = float(lambda_rate)
    if not math.isfinite(stop) or stop <= 0.0:
        raise ValueError("horizon must be positive and finite")
    if not math.isfinite(candidate_rate) or candidate_rate <= 0.0:
        raise ValueError("lambda_rate must be positive and finite")
    rng = trajectory_rng(master_seed, replicate_id, trajectory_id)
    state = sample_initial_state(rng, parameters)
    time_value = 0.0
    candidates = 0
    maximum_rate_seen = 0.0
    while True:
        candidate_time = time_value + float(rng.exponential(1.0 / candidate_rate))
        if candidate_time > stop:
            return TrajectoryRecord(
                trajectory_id=trajectory_id,
                event_time=None,
                candidate_count=candidates,
                maximum_rate_seen=maximum_rate_seen,
                accepted_rate=None,
            )
        state = free_transition(state, candidate_time - time_value, rng, parameters)
        time_value = candidate_time
        candidates += 1
        killing_rate = float(rate_function(state, parameters))
        if not math.isfinite(killing_rate) or killing_rate < 0.0:
            raise RuntimeError("the killing field returned an invalid rate")
        # Fail closed.  In particular, never clip K/Lambda to one.
        if killing_rate > candidate_rate:
            raise RuntimeError("the declared homogeneous Lambda does not dominate K")
        maximum_rate_seen = max(maximum_rate_seen, killing_rate)
        if float(rng.random()) < killing_rate / candidate_rate:
            return TrajectoryRecord(
                trajectory_id=trajectory_id,
                event_time=time_value,
                candidate_count=candidates,
                maximum_rate_seen=maximum_rate_seen,
                accepted_rate=killing_rate,
            )


def constant_rate_function(rate: float) -> RateFunction:
    value = float(rate)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("constant hazard must be finite and nonnegative")

    def evaluate(
        _state: QuotientState,
        _parameters: BroadFourSlabParameters,
    ) -> float:
        return value

    return evaluate


def simulate_ensemble(
    trajectory_ids: Iterable[int],
    *,
    master_seed: int,
    replicate_id: int,
    horizon: float,
    parameters: BroadFourSlabParameters,
    lambda_rate: float = FROZEN_LAMBDA,
    rate_function: RateFunction = broad_four_slab_killing_rate,
) -> list[TrajectoryRecord]:
    return [
        simulate_trajectory(
            master_seed=master_seed,
            replicate_id=replicate_id,
            trajectory_id=int(trajectory_id),
            horizon=horizon,
            parameters=parameters,
            lambda_rate=lambda_rate,
            rate_function=rate_function,
        )
        for trajectory_id in trajectory_ids
    ]


def event_time_array(records: list[TrajectoryRecord]) -> np.ndarray:
    return np.asarray(
        [math.inf if record.event_time is None else record.event_time for record in records],
        dtype=float,
    )


def dkw_half_width(sample_size: int, alpha: float) -> float:
    if int(sample_size) != sample_size or sample_size < 1:
        raise ValueError("sample_size must be a positive integer")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    return float(math.sqrt(math.log(2.0 / alpha) / (2.0 * sample_size)))


def survival_estimates(event_times: np.ndarray, times: np.ndarray) -> np.ndarray:
    events = np.asarray(event_times, dtype=float)
    grid = np.asarray(times, dtype=float)
    if events.ndim != 1 or events.size < 1 or grid.ndim != 1:
        raise ValueError("events and survival times must be one-dimensional")
    return np.mean(events[:, None] > grid[None, :], axis=0)


def clopper_pearson_interval(
    count: int,
    sample_size: int,
    *,
    lower_tail_alpha: float,
    upper_tail_alpha: float,
) -> tuple[float, float]:
    """Two one-sided exact binomial limits with separately allocated tails."""

    if int(count) != count or int(sample_size) != sample_size or not 0 <= count <= sample_size:
        raise ValueError("count and sample_size are inconsistent")
    if not 0.0 < lower_tail_alpha < 1.0 or not 0.0 < upper_tail_alpha < 1.0:
        raise ValueError("tail alpha values must lie in (0,1)")
    lower = 0.0 if count == 0 else float(beta.ppf(lower_tail_alpha, count, sample_size - count + 1))
    upper = (
        1.0
        if count == sample_size
        else float(beta.ppf(1.0 - upper_tail_alpha, count + 1, sample_size - count))
    )
    return lower, upper


def basin_counts(
    event_times: np.ndarray, valley_times: tuple[float, float], horizon: float
) -> list[int]:
    events = np.asarray(event_times, dtype=float)
    first, second = (float(value) for value in valley_times)
    if not 0.0 < first < second < horizon:
        raise ValueError("valley cuts must be ordered inside the horizon")
    return [
        int(np.count_nonzero(events <= first)),
        int(np.count_nonzero((events > first) & (events <= second))),
        int(np.count_nonzero((events > second) & (events <= horizon))),
    ]


def window_counts(
    event_times: np.ndarray,
    centres: tuple[float, ...],
    half_width: float,
) -> list[int]:
    events = np.asarray(event_times, dtype=float)
    width = float(half_width)
    if not math.isfinite(width) or width <= 0.0:
        raise ValueError("window half-width must be positive")
    windows = [(centre - width, centre + width) for centre in centres]
    if any(left < 0.0 for left, _right in windows):
        raise ValueError("event windows must lie in positive time")
    if any(
        right >= next_left for (_left, right), (next_left, _next_right) in zip(windows, windows[1:])
    ):
        raise ValueError("event windows must be disjoint and ordered")
    return [int(np.count_nonzero((events >= left) & (events < right))) for left, right in windows]


def mass_detection_power(sample_size: int, p0: float, p1: float, alpha: float) -> float:
    """Exact binomial power of the one-sided Clopper--Pearson mass test."""

    if not 0.0 < p0 < p1 < 1.0 or not 0.0 < alpha < 1.0:
        raise ValueError("require 0 < p0 < p1 < 1 and 0 < alpha < 1")
    n = int(sample_size)
    if n != sample_size or n < 1:
        raise ValueError("sample_size must be a positive integer")
    critical_count = int(binom.isf(alpha, n, p0)) + 1
    while critical_count > 0 and binom.sf(critical_count - 2, n, p0) <= alpha:
        critical_count -= 1
    while binom.sf(critical_count - 1, n, p0) > alpha:
        critical_count += 1
    return float(binom.sf(critical_count - 1, n, p1))


def nominal_cp_precision_at_size(
    sample_size: int,
    p0: float,
    p1: float,
    alpha: float,
    margin_fraction: float,
) -> dict[str, float | bool | list[float]]:
    """Evaluate the CP quarter-margin rule at the nominal expected count.

    This is a deterministic precision design, not a power guarantee.  The
    realized run must recompute its actual interval and fail closed.
    """

    if not 0.0 < p0 < p1 < 1.0 or not 0.0 < alpha < 1.0:
        raise ValueError("invalid probability or alpha")
    if not 0.0 < margin_fraction < 1.0:
        raise ValueError("margin_fraction must lie in (0,1)")
    n = int(sample_size)
    if n != sample_size or n < 1:
        raise ValueError("sample_size must be a positive integer")
    radius = margin_fraction * (p1 - p0)
    count = int(round(n * p1))
    lower, upper = clopper_pearson_interval(
        count,
        n,
        lower_tail_alpha=alpha,
        upper_tail_alpha=alpha,
    )
    maximum_radius = max(p1 - lower, upper - p1)
    return {
        "nominal_expected_count": count,
        "interval": [lower, upper],
        "maximum_radius": maximum_radius,
        "quarter_margin_target_radius": radius,
        "quarter_margin_passed": maximum_radius <= radius,
    }


def conservative_joint_contrast_certificate(
    sample_size: int,
    probability_pairs: tuple[tuple[float, float], ...],
    *,
    inference_alpha: float,
    target_power: float,
) -> bool:
    """Certify a sufficient N for simultaneous peak-window > valley-window signs.

    Marginal one-sided CP bounds and binomial tail events are combined by union
    bounds, so the returned size is conservative even though window counts from
    one trajectory are dependent.
    """

    if not probability_pairs or not 0.0 < inference_alpha < 1.0:
        raise ValueError("at least one pair and a valid inference alpha are required")
    if not 0.0 < target_power < 1.0:
        raise ValueError("target_power must lie in (0,1)")
    if any(not 0.0 < valley < peak < 1.0 for peak, valley in probability_pairs):
        raise ValueError("every planning pair must satisfy 0 < valley < peak < 1")
    tail_alpha = inference_alpha / (2.0 * len(probability_pairs))
    tail_failure = (1.0 - target_power) / (2.0 * len(probability_pairs))

    def pair_passes(sample_size: int, peak: float, valley: float) -> bool:
        lower_count = int(binom.ppf(tail_failure, sample_size, peak))
        upper_count = int(binom.isf(tail_failure, sample_size, valley))
        peak_lower, _peak_upper = clopper_pearson_interval(
            lower_count,
            sample_size,
            lower_tail_alpha=tail_alpha,
            upper_tail_alpha=tail_alpha,
        )
        _valley_lower, valley_upper = clopper_pearson_interval(
            upper_count,
            sample_size,
            lower_tail_alpha=tail_alpha,
            upper_tail_alpha=tail_alpha,
        )
        return peak_lower > valley_upper

    n = int(sample_size)
    if n != sample_size or n < 1:
        raise ValueError("sample_size must be a positive integer")
    return all(pair_passes(n, peak, valley) for peak, valley in probability_pairs)


def _records_summary(records: list[TrajectoryRecord], horizon: float) -> dict[str, Any]:
    event_times = event_time_array(records)
    candidate_counts = np.asarray([record.candidate_count for record in records], dtype=int)
    maximum_rates = np.asarray([record.maximum_rate_seen for record in records], dtype=float)
    return {
        "trajectory_count": len(records),
        "reaction_count": int(np.count_nonzero(np.isfinite(event_times))),
        "survival_at_horizon": float(np.mean(event_times > horizon)),
        "candidate_count_sum": int(np.sum(candidate_counts, dtype=np.int64)),
        "candidate_count_maximum": int(np.max(candidate_counts)),
        "maximum_rate_seen": float(np.max(maximum_rates)),
        "maximum_acceptance_probability_seen": float(np.max(maximum_rates) / FROZEN_LAMBDA),
    }


def run_proof_of_principle(
    *,
    constant_trajectories: int = 32768,
    broad_trajectories: int = 16384,
) -> dict[str, Any]:
    if int(constant_trajectories) != constant_trajectories or constant_trajectories < 1:
        raise ValueError("constant_trajectories must be a positive integer")
    if int(broad_trajectories) != broad_trajectories or broad_trajectories < 1:
        raise ValueError("broad_trajectories must be a positive integer")
    parameters = BroadFourSlabParameters()
    analytic_bound = analytic_killing_bound(parameters)
    if not analytic_bound < FROZEN_LAMBDA:
        raise RuntimeError("frozen Lambda does not strictly exceed the analytic bound")

    constant_rate = 0.05
    constant_horizon = 40.0
    constant_grid = np.asarray((1.0, 2.0, 5.0, 10.0, 20.0, 40.0), dtype=float)
    constant_records = simulate_ensemble(
        range(constant_trajectories),
        master_seed=20260713,
        replicate_id=0,
        horizon=constant_horizon,
        parameters=parameters,
        rate_function=constant_rate_function(constant_rate),
    )
    constant_events = event_time_array(constant_records)
    observed_survival = survival_estimates(constant_events, constant_grid)
    exact_survival = np.exp(-constant_rate * constant_grid)
    dkw_alpha = 0.001
    dkw_radius = dkw_half_width(constant_trajectories, dkw_alpha)
    maximum_survival_error = float(np.max(np.abs(observed_survival - exact_survival)))

    broad_horizon = 100.0
    broad_records = simulate_ensemble(
        range(broad_trajectories),
        master_seed=20260713,
        replicate_id=1,
        horizon=broad_horizon,
        parameters=parameters,
    )
    broad_events = event_time_array(broad_records)
    # Result-informed N=97 locations are used only for this non-claiming method
    # smoke.  A production run must replace them with the frozen converged-FV
    # validation targets before inspecting any independent-solver outcomes.
    roots = (
        3.365272251188439,
        5.116225052518206,
        8.66151334474662,
        13.618681444463405,
        22.603279023438112,
    )
    valleys = (roots[1], roots[3])
    basin = basin_counts(broad_events, valleys, broad_horizon)
    censored_survivors = int(np.count_nonzero(broad_events > broad_horizon))
    partition_count_error = int(sum(basin) + censored_survivors - broad_trajectories)
    windows = window_counts(broad_events, roots, 0.4)
    mass_tail_alpha = 0.02 / 3.0
    mass_intervals = [
        clopper_pearson_interval(
            count,
            broad_trajectories,
            lower_tail_alpha=mass_tail_alpha,
            upper_tail_alpha=mass_tail_alpha,
        )
        for count in basin
    ]

    # Preliminary planning values come only from the already disclosed N=97
    # feasibility trace; they do not authorize the independent production run.
    disclosed_mass = 0.005307459366939327
    provisional_production_size = 6_000_000
    mass_power_at_provisional_size = mass_detection_power(
        provisional_production_size,
        0.005,
        disclosed_mass,
        mass_tail_alpha,
    )
    mass_precision = nominal_cp_precision_at_size(
        provisional_production_size,
        0.005,
        disclosed_mass,
        mass_tail_alpha,
        0.25,
    )
    window_probabilities = (
        0.0014755815480296034,
        0.0012142342225729486,
        0.0017866740292924895,
        0.0014651531386407997,
        0.0017189852933621585,
    )
    contrast_pairs = (
        (window_probabilities[0], window_probabilities[1]),
        (window_probabilities[2], window_probabilities[1]),
        (window_probabilities[2], window_probabilities[3]),
        (window_probabilities[4], window_probabilities[3]),
    )
    contrast_power_certificate = conservative_joint_contrast_certificate(
        provisional_production_size,
        contrast_pairs,
        inference_alpha=0.02,
        target_power=0.90,
    )

    return {
        "schema_version": 1,
        "stage": "OFF_LATTICE_DOI_THINNING_PROOF_OF_PRINCIPLE_ONLY",
        "claim_flags": {
            "independent_solver_verified": False,
            "publication_evidence": False,
            "modality_confirmed": False,
            "project_gate_passed": False,
        },
        "method": {
            "state_space": "R midpoint x R relative_parallel x periodic relative_perp",
            "free_transition": "exact OU, exact OU, exact wrapped Brownian between Poisson candidates",
            "killing": "continuous normalized midpoint bumps times unsmoothed disk-contact indicator",
            "candidate_process": "homogeneous Poisson thinning",
            "rng": "NumPy Philox with distinct 128-bit key per replicate and trajectory",
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
        },
        "parameters": asdict(parameters),
        "lambda_certificate": {
            "base_bump_integral_binary64": BASE_BUMP_INTEGRAL,
            "analytic_upper_bound": analytic_bound,
            "binary64_exact_profile_maximum_diagnostic": exact_profile_maximum(parameters),
            "frozen_lambda": FROZEN_LAMBDA,
            "strict_margin": FROZEN_LAMBDA - analytic_bound,
            "acceptance_clipping_forbidden": True,
        },
        "constant_hazard_invariant": {
            **_records_summary(constant_records, constant_horizon),
            "constant_hazard": constant_rate,
            "time_grid": constant_grid.tolist(),
            "observed_survival": observed_survival.tolist(),
            "exact_survival": exact_survival.tolist(),
            "maximum_absolute_survival_error": maximum_survival_error,
            "dkw_alpha": dkw_alpha,
            "dkw_simultaneous_half_width": dkw_radius,
            "dkw_gate_passed": maximum_survival_error <= dkw_radius,
        },
        "broad_configuration_smoke": {
            **_records_summary(broad_records, broad_horizon),
            "root_locations_source": "disclosed N=97 feasibility only; not a production freeze",
            "root_locations": list(roots),
            "window_half_width": 0.4,
            "window_counts": windows,
            "valley_partition_times": list(valleys),
            "basin_counts": basin,
            "censored_survivor_count": censored_survivors,
            "mass_partition_count_error": partition_count_error,
            "basin_mass_estimates": [count / broad_trajectories for count in basin],
            "basin_mass_clopper_pearson_intervals": [list(interval) for interval in mass_intervals],
            "method_smoke_only": True,
        },
        "preliminary_power_plan": {
            "source": "already disclosed N=97 feasibility values; must be recomputed after FV target freeze",
            "familywise_alpha_allocation": {
                "survival_DKW": 0.01,
                "three_basin_masses": 0.02,
                "four_peak_valley_contrasts": 0.02,
            },
            "target_joint_power": 0.90,
            "mass_floor": 0.005,
            "disclosed_smallest_mass_alternative": disclosed_mass,
            "exact_mass_detection_power_at_provisional_size": mass_power_at_provisional_size,
            "nominal_CP_precision_at_provisional_size": mass_precision,
            "joint_contrast_power_at_least_0p90_certified_at_provisional_size": contrast_power_certificate,
            "provisional_rounded_production_size": provisional_production_size,
            "production_run_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-poc", action="store_true", help="run only the bounded method smoke")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--constant-trajectories", type=int, default=32768)
    parser.add_argument("--broad-trajectories", type=int, default=16384)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.run_poc:
        raise SystemExit("proof-of-principle execution requires --run-poc")
    payload = run_proof_of_principle(
        constant_trajectories=args.constant_trajectories,
        broad_trajectories=args.broad_trajectories,
    )
    output = args.output.resolve()
    if REPORT.resolve() not in output.parents:
        raise SystemExit("output must remain inside the owning report")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_json_bytes(payload))
    print(output)


if __name__ == "__main__":
    main()
