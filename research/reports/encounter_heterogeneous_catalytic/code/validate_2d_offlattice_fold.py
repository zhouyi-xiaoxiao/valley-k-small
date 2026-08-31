#!/usr/bin/env python3
"""Off-lattice Brownian-dynamics validation of the matched-budget Doi fold.

Continuum model
---------------
Two independent particles ``i = 1, 2`` in the unit square with reflecting
boundaries:

    dX_i = v_i dt + sqrt(2 D_i) dW_i^x
    dY_i = -gamma (Y_i - 1/2) dt + sqrt(2 D_i) dW_i^y

Convention check (lattice <-> continuum).  The CTMC generators built by
``vkcore.encounter2d.reflecting_advection_diffusion_generator_2d`` use
diffusive hop rates ``D / h**2`` and upwind advective rates
``max(+/-v, 0) / h``.  A nearest-neighbour CTMC with hop rate ``D / h**2``
per direction has generator ``(D/h**2)[f(x+h) + f(x-h) - 2 f(x)] ->
D f''(x)``, i.e. the continuum generator ``D Laplacian + v . grad`` with the
transverse drift ``-gamma (y - 1/2)``.  The Ito diffusion whose generator is
``D Laplacian`` is ``dX = sqrt(2 D) dW`` (for ``dX = sigma dW`` the generator
is ``(sigma**2 / 2) d^2/dx^2``).  Hence the SDE above, with the SAME
numerical values of ``D_i``, ``v_i``, and ``gamma`` as the lattice scripts,
is exactly the diffusive ``h -> 0`` limit of the lattice model; no
factor-of-two rescaling of the diffusion coefficients is required.  Omitted
outward jumps on the lattice correspond to the reflecting (zero-flux)
boundary, implemented here as coordinate-wise attempted-step reflection.

Killing (Doi).  While ``|X_1 - X_2| < a`` (Euclidean, a = 0.17) the pair is
killed at rate ``kappa_theta(C)`` evaluated at the midpoint
``C = (X_1 + X_2) / 2`` along the matched-budget path

    kappa_theta(C) = (1 - theta) kappa_bar + theta kappa_pattern(C),
    kappa_pattern(C) = 0.5 1_near(C) + 15 1_far(C),

with the near patch (centre (0.25, 0.5), radius 0.18) and the far patch
(centre (0.72, 0.5), radius 0.20); the patches are disjoint (asserted).
``kappa_bar`` is the CONTINUUM homogeneous matched rate: the integral of
``kappa_pattern`` over the four-dimensional contact tube divided by the tube
volume.  It is computed by the same exact one-dimensional quadrature
reduction as ``validate_2d_matched_fold._continuum_budget_reference`` (the
reduction is an exact rewriting of the 4D tube integral) and cross-checked
here by direct 4D Monte Carlo quadrature.  Killing is applied per
Euler-Maruyama step with probability ``1 - exp(-kappa dt)`` (via expm1).

Run modes
---------
* default: simulate each requested theta, write one JSON per theta plus a
  combined CSV into ``../artifacts/data/``;
* ``--selftest``: validation gate (2), reflecting-square uniformity of the
  x-marginal with ``v = 0`` and ``gamma = 0``;
* ``--convergence-check``: validation gate (4), dt versus dt/2 comparison of
  the ``t in [5, 60]`` histogram in units of Monte Carlo sigma.

Validation gate (1) (``kappa = 0`` kills nothing, from a contact-forcing
start) and gate (3) (per-step kill probability in ``[0, 1]``) run inside the
default mode and are asserted.

The channel recorded for each killed pair is the geometric location of the
midpoint at the kill step: ``near`` / ``far`` when it lies in the respective
patch, ``background`` otherwise (the homogeneous component kills everywhere
inside the contact tube).  Modal-structure output is a smoothed-histogram
diagnostic, not the repository double-peak classifier; no figure is written.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.integrate import quad

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"

REACTION_RADIUS = 0.17
NEAR_CENTRE = (0.25, 0.5)
NEAR_RADIUS = 0.18
NEAR_RATE = 0.5
FAR_CENTRE = (0.72, 0.5)
FAR_RADIUS = 0.20
FAR_RATE = 15.0

DEFAULT_DT = 2e-4
DEFAULT_TMAX = 120.0
DEFAULT_WALKERS = 2_000_000
DEFAULT_CHUNK = 200_000
DEFAULT_SEED = 20260730
DEFAULT_THETAS = (0.12, 0.60)

# Frozen reference for the exact continuum matched rate with the parameters
# above (informational; the binding runtime check is exact-vs-Monte-Carlo).
REFERENCE_KAPPA_BAR = 2.250157222034

WINDOW_LO = 5.0
WINDOW_HI = 60.0
WINDOW_BIN = 0.25
FULL_BIN = 0.25
LOG_BIN_COUNT = 140
LOG_T_LO = 0.05
STRUCTURE_LO = 10.0
STRUCTURE_HI = 30.0
SMOOTH_BINS = 9

CONVERGENCE_BIN = 1.0
CONVERGENCE_MIN_POOLED = 10

SELFTEST_DT = 5e-3
SELFTEST_TMAX = 300.0
SELFTEST_BINS = 20
SELFTEST_MAX_ABS_Z = 5.0

# Entropy tags keep the independent RNG streams of the different modes and
# checks disjoint under one --seed.
TAG_MAIN = 1
TAG_GATE_NO_KILL = 2
TAG_SELFTEST = 3
TAG_CONVERGENCE = 4
TAG_KAPPA_MC = 5

CONVENTION_NOTE = (
    "lattice CTMC hop rates D/h^2 give generator D*Laplacian + v.grad as "
    "h->0, which is the generator of dX = v dt + sqrt(2D) dW; this script "
    "simulates that SDE with the unrescaled lattice parameter values, so the "
    "lattice model's diffusive limit is reproduced exactly"
)


@dataclass(frozen=True)
class PairParameters:
    """Physical parameters of the independent particle pair."""

    diffusion_one: float = 0.0025
    drift_one: float = 0.115
    diffusion_two: float = 0.0008
    drift_two: float = 0.02
    transverse_confinement: float = 1.5
    start_one: tuple[float, float] = (0.0, 0.5)
    start_two: tuple[float, float] = (0.28, 0.5)


DEFAULT_PAIR = PairParameters()


def _assert_patches_disjoint() -> float:
    gap = float(
        np.hypot(
            NEAR_CENTRE[0] - FAR_CENTRE[0],
            NEAR_CENTRE[1] - FAR_CENTRE[1],
        )
        - (NEAR_RADIUS + FAR_RADIUS)
    )
    assert gap > 0.0, (
        "near and far patches overlap; the additive kappa_pattern and the "
        f"geometric channel attribution both assume disjoint patches (gap={gap:g})"
    )
    return gap


def _tube_volume() -> float:
    """4D volume of {(X1, X2) in ([0,1]^2)^2 : |X1 - X2| < a} (exact)."""

    a = REACTION_RADIUS
    return float(np.pi * a**2 - (8.0 / 3.0) * a**3 + 0.5 * a**4)


def _circular_segment_area(radius: float, signed_cut: float) -> float:
    """Area of the disk portion left of a signed vertical cut."""

    cut = float(np.clip(signed_cut, -radius, radius))
    return float(
        cut * np.sqrt(max(0.0, radius**2 - cut**2))
        + radius**2 * (np.arcsin(cut / radius) + 0.5 * np.pi)
    )


def _boundary_clipped_patch_joint_volume(
    centre_x: float,
    radius: float,
    *,
    boundary: str,
) -> float:
    """Exact midpoint-feasible patch volume integrated over the relative disk.

    Same reduction as ``validate_2d_matched_fold._continuum_budget_reference``:
    in (C, r) variables with unit Jacobian, feasibility of both particles
    clips the midpoint to ``C_x in [|r_x|/2, 1 - |r_x|/2]`` (one-sided per
    patch, no y clipping for this geometry), and the r_y integral is the
    analytic chord width ``2 sqrt(a^2 - r_x^2)``.
    """

    if 0.5 - radius <= 0.5 * REACTION_RADIUS:
        raise ValueError("the one-dimensional reduction assumes no y clipping")
    if boundary == "left":
        clearance = centre_x - radius

        def signed_cut(relative_x: float) -> float:
            return 0.5 * relative_x - centre_x

    elif boundary == "right":
        clearance = 1.0 - centre_x - radius

        def signed_cut(relative_x: float) -> float:
            return centre_x - (1.0 - 0.5 * relative_x)

    else:
        raise ValueError("boundary must be left or right")

    def integrand(relative_x: float) -> float:
        available_patch_area = np.pi * radius**2 - _circular_segment_area(
            radius,
            signed_cut(relative_x),
        )
        return float(
            4.0
            * np.sqrt(max(0.0, REACTION_RADIUS**2 - relative_x**2))
            * available_patch_area
        )

    break_point = 2.0 * clearance
    points = [break_point] if 0.0 < break_point < REACTION_RADIUS else None
    value, error = quad(
        integrand,
        0.0,
        REACTION_RADIUS,
        epsabs=1e-14,
        epsrel=1e-13,
        points=points,
        limit=500,
    )
    if error > 2e-13:
        raise RuntimeError(f"continuum patch-volume quadrature error={error:.6g}")
    return float(value)


def continuum_kappa_bar(seed: int, *, mc_samples: int = 100_000_000) -> dict:
    """Exact continuum matched rate with a direct 4D Monte Carlo cross-check."""

    tube_volume = _tube_volume()
    near_joint_volume = _boundary_clipped_patch_joint_volume(
        NEAR_CENTRE[0],
        NEAR_RADIUS,
        boundary="left",
    )
    far_joint_volume = _boundary_clipped_patch_joint_volume(
        FAR_CENTRE[0],
        FAR_RADIUS,
        boundary="right",
    )
    exact = (NEAR_RATE * near_joint_volume + FAR_RATE * far_joint_volume) / tube_volume

    rng = np.random.Generator(
        np.random.Philox(np.random.SeedSequence([seed, TAG_KAPPA_MC]))
    )
    batch = 20_000_000
    drawn = 0
    tube_hits = 0
    near_hits = 0
    far_hits = 0
    while drawn < mc_samples:
        count = min(batch, mc_samples - drawn)
        first = rng.random((count, 2))
        second = rng.random((count, 2))
        squared = np.sum((first - second) ** 2, axis=1)
        tube = squared < REACTION_RADIUS**2
        centre = 0.5 * (first + second)
        in_near = (centre[:, 0] - NEAR_CENTRE[0]) ** 2 + (
            centre[:, 1] - NEAR_CENTRE[1]
        ) ** 2 <= NEAR_RADIUS**2
        in_far = (centre[:, 0] - FAR_CENTRE[0]) ** 2 + (
            centre[:, 1] - FAR_CENTRE[1]
        ) ** 2 <= FAR_RADIUS**2
        tube_hits += int(tube.sum())
        near_hits += int((tube & in_near).sum())
        far_hits += int((tube & in_far).sum())
        drawn += count
    mc_estimate = (
        NEAR_RATE * near_hits / drawn + FAR_RATE * far_hits / drawn
    ) / (tube_hits / drawn)
    relative_difference = mc_estimate / exact - 1.0
    assert abs(relative_difference) < 5e-3, (
        "continuum kappa_bar: exact reduction and 4D Monte Carlo disagree "
        f"(exact={exact:.9g}, mc={mc_estimate:.9g})"
    )
    return {
        "kappa_bar": float(exact),
        "kappa_bar_reference_constant": REFERENCE_KAPPA_BAR,
        "tube_volume": tube_volume,
        "near_patch_joint_volume": near_joint_volume,
        "far_patch_joint_volume": far_joint_volume,
        "mc_cross_check": {
            "samples": int(drawn),
            "kappa_bar_mc": float(mc_estimate),
            "relative_difference": float(relative_difference),
            "tube_volume_mc": tube_hits / drawn,
            "near_joint_volume_mc": near_hits / drawn,
            "far_joint_volume_mc": far_hits / drawn,
        },
        "patch_gap": _assert_patches_disjoint(),
        "definition": (
            "kappa_bar = [integral of kappa_pattern(C) over the 4D contact "
            "tube] / [tube volume]; exact 1D-reduced quadrature identical to "
            "validate_2d_matched_fold._continuum_budget_reference"
        ),
    }


def _reflect(values: np.ndarray) -> None:
    """Coordinate-wise reflection into [0, 1], iterated until inside."""

    while True:
        np.abs(values, out=values)
        over = values > 1.0
        if not over.any():
            return
        values[over] = 2.0 - values[over]


def simulate_chunk(
    rng: np.random.Generator,
    count: int,
    *,
    theta: float,
    kappa_bar: float,
    dt: float,
    step_count: int,
    pair: PairParameters = DEFAULT_PAIR,
    kill_scale: float = 1.0,
    return_positions: bool = False,
) -> dict:
    """Euler-Maruyama evolution of one walker chunk with per-step Doi killing.

    Killed pairs are removed from the arrays at the step of death, so the
    cost of a chunk is proportional to the number of surviving pair-steps.
    """

    sigma_one = np.sqrt(2.0 * pair.diffusion_one * dt)
    sigma_two = np.sqrt(2.0 * pair.diffusion_two * dt)
    drift_one = pair.drift_one * dt
    drift_two = pair.drift_two * dt
    ou_decay = 1.0 - pair.transverse_confinement * dt
    ou_pull = pair.transverse_confinement * dt * 0.5
    base_rate = (1.0 - theta) * kappa_bar * kill_scale
    near_rate = theta * NEAR_RATE * kill_scale
    far_rate = theta * FAR_RATE * kill_scale
    assert base_rate >= 0.0 and near_rate >= 0.0 and far_rate >= 0.0
    contact_squared = REACTION_RADIUS**2

    x1 = np.full(count, pair.start_one[0], dtype=float)
    y1 = np.full(count, pair.start_one[1], dtype=float)
    x2 = np.full(count, pair.start_two[0], dtype=float)
    y2 = np.full(count, pair.start_two[1], dtype=float)

    kill_time_blocks: list[np.ndarray] = []
    kill_channel_blocks: list[np.ndarray] = []
    contact_steps = 0
    kill_probability_max = 0.0
    walker_steps = 0

    for step in range(step_count):
        alive = x1.size
        if alive == 0:
            break
        walker_steps += alive
        noise = rng.standard_normal((4, alive))
        noise[0] *= sigma_one
        noise[1] *= sigma_one
        noise[2] *= sigma_two
        noise[3] *= sigma_two
        x1 += drift_one
        x1 += noise[0]
        y1 *= ou_decay
        y1 += ou_pull
        y1 += noise[1]
        x2 += drift_two
        x2 += noise[2]
        y2 *= ou_decay
        y2 += ou_pull
        y2 += noise[3]
        _reflect(x1)
        _reflect(y1)
        _reflect(x2)
        _reflect(y2)

        gap_x = x1 - x2
        gap_y = y1 - y2
        np.square(gap_x, out=gap_x)
        np.square(gap_y, out=gap_y)
        gap_x += gap_y
        contact_index = np.flatnonzero(gap_x < contact_squared)
        if contact_index.size == 0:
            continue
        contact_steps += int(contact_index.size)
        centre_x = 0.5 * (x1[contact_index] + x2[contact_index])
        centre_y = 0.5 * (y1[contact_index] + y2[contact_index])
        in_near = (centre_x - NEAR_CENTRE[0]) ** 2 + (
            centre_y - NEAR_CENTRE[1]
        ) ** 2 <= NEAR_RADIUS**2
        in_far = (centre_x - FAR_CENTRE[0]) ** 2 + (
            centre_y - FAR_CENTRE[1]
        ) ** 2 <= FAR_RADIUS**2
        kappa = np.full(contact_index.size, base_rate)
        kappa[in_near] += near_rate
        kappa[in_far] += far_rate
        kill_probability = -np.expm1(-kappa * dt)
        step_max = float(kill_probability.max())
        if step_max > kill_probability_max:
            kill_probability_max = step_max
        uniforms = rng.random(contact_index.size)
        killed_local = uniforms < kill_probability
        if not killed_local.any():
            continue
        killed_index = contact_index[killed_local]
        kill_time_blocks.append(
            np.full(killed_index.size, (step + 1) * dt, dtype=float)
        )
        kill_channel_blocks.append(
            np.where(
                in_far[killed_local],
                2,
                np.where(in_near[killed_local], 1, 0),
            ).astype(np.int8)
        )
        keep = np.ones(alive, dtype=bool)
        keep[killed_index] = False
        x1 = x1[keep]
        y1 = y1[keep]
        x2 = x2[keep]
        y2 = y2[keep]

    result = {
        "kill_times": (
            np.concatenate(kill_time_blocks)
            if kill_time_blocks
            else np.empty(0, dtype=float)
        ),
        "kill_channels": (
            np.concatenate(kill_channel_blocks)
            if kill_channel_blocks
            else np.empty(0, dtype=np.int8)
        ),
        "survivors": int(x1.size),
        "contact_steps": int(contact_steps),
        "kill_probability_max": float(kill_probability_max),
        "walker_steps": int(walker_steps),
    }
    if return_positions:
        result["positions"] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    return result


def _theta_entropy(seed: int, theta: float, dt: float, tag: int) -> list[int]:
    return [
        int(seed),
        int(tag),
        int(round(theta * 1e12)),
        int(round(dt * 1e15)),
    ]


def run_theta(
    theta: float,
    *,
    walkers: int,
    chunk: int,
    dt: float,
    tmax: float,
    seed: int,
    kappa_bar: float,
    tag: int = TAG_MAIN,
    verbose: bool = True,
) -> dict:
    """Simulate one theta over independent Philox substream chunks."""

    step_count = int(round(tmax / dt))
    if abs(step_count * dt - tmax) > 1e-9 * max(1.0, tmax):
        raise ValueError("tmax must be an integer multiple of dt")
    chunk_sizes = [chunk] * (walkers // chunk)
    if walkers % chunk:
        chunk_sizes.append(walkers % chunk)
    root = np.random.SeedSequence(_theta_entropy(seed, theta, dt, tag))
    children = root.spawn(len(chunk_sizes))
    kill_times: list[np.ndarray] = []
    kill_channels: list[np.ndarray] = []
    survivors = 0
    contact_steps = 0
    kill_probability_max = 0.0
    walker_steps = 0
    started = time.perf_counter()
    for index, (size, child) in enumerate(zip(chunk_sizes, children)):
        rng = np.random.Generator(np.random.Philox(child))
        outcome = simulate_chunk(
            rng,
            size,
            theta=theta,
            kappa_bar=kappa_bar,
            dt=dt,
            step_count=step_count,
        )
        kill_times.append(outcome["kill_times"])
        kill_channels.append(outcome["kill_channels"])
        survivors += outcome["survivors"]
        contact_steps += outcome["contact_steps"]
        kill_probability_max = max(
            kill_probability_max,
            outcome["kill_probability_max"],
        )
        walker_steps += outcome["walker_steps"]
        if verbose:
            print(
                f"  theta={theta:g} chunk {index + 1}/{len(chunk_sizes)}: "
                f"killed={outcome['kill_times'].size}/{size} "
                f"elapsed={time.perf_counter() - started:.1f}s",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    times = np.concatenate(kill_times)
    channels = np.concatenate(kill_channels)
    assert 0.0 <= kill_probability_max <= 1.0, (
        f"per-step kill probability left [0, 1]: {kill_probability_max!r}"
    )
    return {
        "theta": theta,
        "walkers": int(walkers),
        "kill_times": times,
        "kill_channels": channels,
        "survivors": int(survivors),
        "contact_steps": int(contact_steps),
        "kill_probability_max": float(kill_probability_max),
        "walker_steps": int(walker_steps),
        "runtime_seconds": float(elapsed),
    }


def _histogram_block(times: np.ndarray, edges: np.ndarray) -> dict:
    counts, _ = np.histogram(times, bins=edges)
    return {
        "edges": [float(value) for value in edges],
        "counts": [int(value) for value in counts],
    }


def _modal_structure(edges: np.ndarray, counts: np.ndarray) -> dict:
    """Smoothed-histogram local maxima with a simple prominence measure.

    Diagnostic only; this is not the repository double-peak classifier.  A
    maximum is flagged significant when its prominence exceeds five smoothed
    Poisson sigmas of its own height.
    """

    centres = 0.5 * (edges[:-1] + edges[1:])
    kernel = np.ones(SMOOTH_BINS) / SMOOTH_BINS
    smoothed = np.convolve(counts.astype(float), kernel, mode="same")
    maxima: list[dict] = []
    for index in range(1, smoothed.size - 1):
        if not (
            smoothed[index] > smoothed[index - 1]
            and smoothed[index] >= smoothed[index + 1]
        ):
            continue
        height = float(smoothed[index])
        saddles: list[float] = []
        for direction in (-1, 1):
            probe = index + direction
            lowest = height
            while 0 <= probe < smoothed.size and smoothed[probe] <= height:
                lowest = min(lowest, float(smoothed[probe]))
                probe += direction
            saddles.append(lowest)
        prominence = height - max(saddles)
        sigma = float(np.sqrt(max(height, 1.0) / SMOOTH_BINS))
        maxima.append(
            {
                "time": float(centres[index]),
                "smoothed_height": height,
                "prominence": float(prominence),
                "poisson_sigma": sigma,
                "significant": bool(prominence >= 5.0 * sigma),
            }
        )
    significant = [row for row in maxima if row["significant"]]
    return {
        "smoothing_bins": SMOOTH_BINS,
        "bin_width": float(edges[1] - edges[0]),
        "local_maxima": maxima,
        "significant_maxima": significant,
        "significant_count": len(significant),
        "significant_in_structure_window": [
            row
            for row in significant
            if STRUCTURE_LO <= row["time"] <= STRUCTURE_HI
        ],
        "note": (
            "smoothed-histogram diagnostic with a 5-sigma prominence rule; "
            "not the repository double-peak classifier"
        ),
    }


def summarize_theta(result: dict, *, dt: float, tmax: float) -> dict:
    times = result["kill_times"]
    channels = result["kill_channels"]
    walkers = result["walkers"]
    kills = int(times.size)
    channel_counts = {
        "background": int((channels == 0).sum()),
        "near": int((channels == 1).sum()),
        "far": int((channels == 2).sum()),
    }
    window_mask = (times >= WINDOW_LO) & (times <= WINDOW_HI)
    structure_mask = (times >= STRUCTURE_LO) & (times <= STRUCTURE_HI)
    window_edges = np.arange(WINDOW_LO, WINDOW_HI + 0.5 * WINDOW_BIN, WINDOW_BIN)
    full_edges = np.arange(0.0, tmax + 0.5 * FULL_BIN, FULL_BIN)
    log_edges = np.geomspace(LOG_T_LO, tmax, LOG_BIN_COUNT + 1)
    full_counts, _ = np.histogram(times, bins=full_edges)
    quantile_levels = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
    quantiles = (
        {
            f"q{int(100 * level):02d}": float(value)
            for level, value in zip(quantile_levels, np.quantile(times, quantile_levels))
        }
        if kills
        else {}
    )
    per_channel_window = {}
    for label, code in (("background", 0), ("near", 1), ("far", 2)):
        channel_times = times[window_mask & (channels == code)]
        per_channel_window[label] = _histogram_block(channel_times, window_edges)
    summary = {
        "kills": kills,
        "kill_fraction": kills / walkers,
        "survivors": result["survivors"],
        "survivor_fraction": result["survivors"] / walkers,
        "channel_counts": channel_counts,
        "channel_fractions": {
            key: value / kills if kills else 0.0
            for key, value in channel_counts.items()
        },
        "kills_in_window_5_60": int(window_mask.sum()),
        "kills_in_structure_window_10_30": int(structure_mask.sum()),
        "structure_window_channel_counts": {
            label: int((structure_mask & (channels == code)).sum())
            for label, code in (("background", 0), ("near", 1), ("far", 2))
        },
        "kill_time_quantiles": quantiles,
        "histograms": {
            "log_full_range": _histogram_block(times, log_edges),
            "log_underflow_below_first_edge": int((times < LOG_T_LO).sum()),
            "linear_window_5_60_total": _histogram_block(
                times[window_mask],
                window_edges,
            ),
            "linear_window_5_60_by_channel": per_channel_window,
            "linear_full_range": {
                "edges": [float(value) for value in full_edges],
                "counts": [int(value) for value in full_counts],
            },
        },
        "modal_structure_diagnostic": _modal_structure(full_edges, full_counts),
        "contact_steps": result["contact_steps"],
        "kill_probability_max": result["kill_probability_max"],
        "walker_steps": result["walker_steps"],
        "runtime_seconds": result["runtime_seconds"],
        "walker_steps_per_second": (
            result["walker_steps"] / result["runtime_seconds"]
            if result["runtime_seconds"] > 0.0
            else None
        ),
        "runtime_seconds_per_1e6_walkers": (
            result["runtime_seconds"] * 1e6 / walkers
        ),
    }
    return summary


def gate_no_killing(seed: int, *, dt: float, kappa_bar: float) -> dict:
    """Validation gate (1): with kappa = 0 nothing dies, from forced contact."""

    pair = PairParameters(start_one=(0.40, 0.5), start_two=(0.45, 0.5))
    rng = np.random.Generator(
        np.random.Philox(np.random.SeedSequence([seed, TAG_GATE_NO_KILL]))
    )
    outcome = simulate_chunk(
        rng,
        5_000,
        theta=0.5,
        kappa_bar=kappa_bar,
        dt=dt,
        step_count=int(round(1.0 / dt)),
        pair=pair,
        kill_scale=0.0,
    )
    assert outcome["kill_times"].size == 0, "kappa=0 run produced kills"
    assert outcome["survivors"] == 5_000, "kappa=0 run lost walkers"
    assert outcome["contact_steps"] > 0, (
        "kappa=0 gate never sampled the contact set; the gate is vacuous"
    )
    assert outcome["kill_probability_max"] == 0.0
    return {
        "walkers": 5_000,
        "tmax": 1.0,
        "start_one": [0.40, 0.5],
        "start_two": [0.45, 0.5],
        "contact_steps": outcome["contact_steps"],
        "kills": 0,
        "passed": True,
    }


def selftest_uniform(seed: int, walkers: int) -> dict:
    """Validation gate (2): reflected pure diffusion has a uniform x-marginal.

    Both particles are given ``D = 0.0025``, ``v = 0``, ``gamma = 0`` and no
    killing, so the two x-marginals together provide ``walkers`` independent
    samples of reflected Brownian motion at ``t = SELFTEST_TMAX``.  The
    slowest reflected mode has decayed to ``exp(-D pi^2 t) ~ 6e-4`` there,
    far below the Monte Carlo bin noise.  A larger dt than the production
    default is used deliberately: the gate exercises the reflection code
    path, not the Euler-Maruyama bias.
    """

    pairs = walkers // 2
    pair = PairParameters(
        diffusion_one=0.0025,
        drift_one=0.0,
        diffusion_two=0.0025,
        drift_two=0.0,
        transverse_confinement=0.0,
    )
    rng = np.random.Generator(
        np.random.Philox(np.random.SeedSequence([seed, TAG_SELFTEST]))
    )
    started = time.perf_counter()
    outcome = simulate_chunk(
        rng,
        pairs,
        theta=0.0,
        kappa_bar=0.0,
        dt=SELFTEST_DT,
        step_count=int(round(SELFTEST_TMAX / SELFTEST_DT)),
        pair=pair,
        kill_scale=0.0,
        return_positions=True,
    )
    elapsed = time.perf_counter() - started
    assert outcome["survivors"] == pairs
    samples = np.concatenate(
        (outcome["positions"]["x1"], outcome["positions"]["x2"])
    )
    total = samples.size
    counts, edges = np.histogram(samples, bins=SELFTEST_BINS, range=(0.0, 1.0))
    expected = total / SELFTEST_BINS
    bin_probability = 1.0 / SELFTEST_BINS
    sigma = np.sqrt(total * bin_probability * (1.0 - bin_probability))
    z_scores = (counts - expected) / sigma
    max_abs_z = float(np.max(np.abs(z_scores)))
    sorted_samples = np.sort(samples)
    ecdf = np.arange(1, total + 1) / total
    ks_distance = float(
        np.max(
            np.maximum(
                np.abs(ecdf - sorted_samples),
                np.abs(sorted_samples - (np.arange(total) / total)),
            )
        )
    )
    mean = float(samples.mean())
    mean_sigma = 1.0 / np.sqrt(12.0 * total)
    mean_z = (mean - 0.5) / mean_sigma
    assert max_abs_z < SELFTEST_MAX_ABS_Z, (
        f"x-marginal bin deviates from uniform: max|z|={max_abs_z:.3f}"
    )
    assert abs(mean_z) < SELFTEST_MAX_ABS_Z, (
        f"x-marginal mean deviates from 1/2: z={mean_z:.3f}"
    )
    return {
        "samples": int(total),
        "pairs": int(pairs),
        "dt": SELFTEST_DT,
        "tmax": SELFTEST_TMAX,
        "diffusion": 0.0025,
        "slowest_mode_residual": float(
            np.exp(-0.0025 * np.pi**2 * SELFTEST_TMAX)
        ),
        "bins": SELFTEST_BINS,
        "bin_counts": [int(value) for value in counts],
        "bin_edges": [float(value) for value in edges],
        "max_abs_bin_z": max_abs_z,
        "mean": mean,
        "mean_z": float(mean_z),
        "ks_distance": ks_distance,
        "ks_distance_scaled": float(ks_distance * np.sqrt(total)),
        "runtime_seconds": float(elapsed),
        "passed": True,
    }


def convergence_check(
    theta: float,
    *,
    walkers: int,
    chunk: int,
    dt: float,
    tmax: float,
    seed: int,
    kappa_bar: float,
) -> dict:
    """Validation gate (4): dt versus dt/2 window histogram in MC sigmas.

    Reported, not asserted, per the validation plan.  Bins pooled below
    ``CONVERGENCE_MIN_POOLED`` counts are excluded from the z statistics.
    """

    edges = np.arange(WINDOW_LO, WINDOW_HI + 0.5 * CONVERGENCE_BIN, CONVERGENCE_BIN)
    runs = {}
    for label, step in (("dt", dt), ("dt_half", 0.5 * dt)):
        outcome = run_theta(
            theta,
            walkers=walkers,
            chunk=chunk,
            dt=step,
            tmax=tmax,
            seed=seed,
            kappa_bar=kappa_bar,
            tag=TAG_CONVERGENCE,
            verbose=False,
        )
        counts, _ = np.histogram(outcome["kill_times"], bins=edges)
        runs[label] = {
            "dt": step,
            "counts": counts,
            "walkers": walkers,
            "kill_fraction": outcome["kill_times"].size / walkers,
            "runtime_seconds": outcome["runtime_seconds"],
        }
    counts_a = runs["dt"]["counts"]
    counts_b = runs["dt_half"]["counts"]
    fraction_a = counts_a / walkers
    fraction_b = counts_b / walkers
    pooled = (counts_a + counts_b) / (2.0 * walkers)
    variance = pooled * (1.0 - pooled) * (2.0 / walkers)
    usable = (counts_a + counts_b) >= CONVERGENCE_MIN_POOLED
    z_scores = np.zeros(edges.size - 1)
    z_scores[usable] = (fraction_a[usable] - fraction_b[usable]) / np.sqrt(
        variance[usable]
    )
    z_used = z_scores[usable]
    return {
        "theta": theta,
        "walkers_per_run": int(walkers),
        "window": [WINDOW_LO, WINDOW_HI],
        "bin_width": CONVERGENCE_BIN,
        "bin_edges": [float(value) for value in edges],
        "counts_dt": [int(value) for value in counts_a],
        "counts_dt_half": [int(value) for value in counts_b],
        "kill_fraction_dt": runs["dt"]["kill_fraction"],
        "kill_fraction_dt_half": runs["dt_half"]["kill_fraction"],
        "usable_bins": int(usable.sum()),
        "excluded_bins": int((~usable).sum()),
        "max_abs_z": float(np.max(np.abs(z_used))) if z_used.size else None,
        "mean_abs_z": float(np.mean(np.abs(z_used))) if z_used.size else None,
        "fraction_abs_z_above_2": (
            float(np.mean(np.abs(z_used) > 2.0)) if z_used.size else None
        ),
        "mean_square_z": float(np.mean(z_used**2)) if z_used.size else None,
        "runtime_seconds_dt": runs["dt"]["runtime_seconds"],
        "runtime_seconds_dt_half": runs["dt_half"]["runtime_seconds"],
        "note": (
            "under the no-bias null the per-bin z are approximately standard "
            "normal; with ~55 bins the expected max|z| is about 2.5-3"
        ),
    }


def _write_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = list(rows[0].keys())
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _base_parameters(args: argparse.Namespace) -> dict:
    return {
        "model": "off-lattice Euler-Maruyama pair with Doi midpoint killing",
        "continuum_convention": CONVENTION_NOTE,
        "domain": "unit square, reflecting (attempted-step reflection)",
        "reaction_radius": REACTION_RADIUS,
        "near_patch": {
            "centre": list(NEAR_CENTRE),
            "radius": NEAR_RADIUS,
            "rate": NEAR_RATE,
        },
        "far_patch": {
            "centre": list(FAR_CENTRE),
            "radius": FAR_RADIUS,
            "rate": FAR_RATE,
        },
        "pair": {
            "diffusion_one": DEFAULT_PAIR.diffusion_one,
            "drift_one": DEFAULT_PAIR.drift_one,
            "diffusion_two": DEFAULT_PAIR.diffusion_two,
            "drift_two": DEFAULT_PAIR.drift_two,
            "transverse_confinement": DEFAULT_PAIR.transverse_confinement,
            "start_one": list(DEFAULT_PAIR.start_one),
            "start_two": list(DEFAULT_PAIR.start_two),
        },
        "dt": args.dt,
        "tmax": args.tmax,
        "seed": args.seed,
        "chunk": args.chunk,
        "rng": "numpy Philox, one SeedSequence-spawned substream per chunk",
        "variance_reduction": "none (plain independent walkers)",
        "channel_attribution": (
            "geometric midpoint location at the kill step: near/far patch "
            "membership, else background"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Off-lattice Brownian-dynamics validation of the matched-budget "
            "Doi fold (continuum companion to validate_2d_matched_fold.py)."
        )
    )
    parser.add_argument(
        "--walkers",
        type=lambda value: int(float(value)),
        default=DEFAULT_WALKERS,
        help="pairs per theta (default 2e6; accepts scientific notation)",
    )
    parser.add_argument("--chunk", type=lambda value: int(float(value)), default=DEFAULT_CHUNK)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--tmax", type=float, default=DEFAULT_TMAX)
    parser.add_argument(
        "--theta",
        type=float,
        nargs="+",
        default=list(DEFAULT_THETAS),
        help="one or more theta values in [0, 1]",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run only the reflecting-square uniformity gate and exit",
    )
    parser.add_argument(
        "--selftest-walkers",
        type=lambda value: int(float(value)),
        default=100_000,
    )
    parser.add_argument(
        "--convergence-check",
        action="store_true",
        help="run only the dt versus dt/2 comparison for each theta and exit",
    )
    parser.add_argument(
        "--convergence-walkers",
        type=lambda value: int(float(value)),
        default=200_000,
    )
    args = parser.parse_args()

    if args.dt <= 0.0 or args.tmax <= 0.0:
        raise SystemExit("dt and tmax must be positive")
    if args.walkers <= 0 or args.chunk <= 0:
        raise SystemExit("walkers and chunk must be positive")
    for theta in args.theta:
        if not 0.0 <= theta <= 1.0:
            raise SystemExit(
                f"theta={theta} outside [0, 1]: the homogeneous component "
                "(1-theta)*kappa_bar would be a negative rate"
            )

    DATA.mkdir(parents=True, exist_ok=True)
    _assert_patches_disjoint()

    if args.selftest:
        report = selftest_uniform(args.seed, args.selftest_walkers)
        path = DATA / "offlattice_fold_selftest.json"
        _write_json(path, {"parameters": _base_parameters(args), "selftest": report})
        print(
            "selftest PASS: "
            f"samples={report['samples']} max|z|={report['max_abs_bin_z']:.3f} "
            f"mean_z={report['mean_z']:.3f} "
            f"KS*sqrt(n)={report['ks_distance_scaled']:.3f} "
            f"runtime={report['runtime_seconds']:.1f}s -> {path}"
        )
        return

    kappa_block = continuum_kappa_bar(args.seed)
    kappa_bar = kappa_block["kappa_bar"]
    print(
        f"continuum kappa_bar={kappa_bar:.9f} "
        f"(MC cross-check rel diff {kappa_block['mc_cross_check']['relative_difference']:.2e})"
    )

    if args.convergence_check:
        for theta in args.theta:
            report = convergence_check(
                theta,
                walkers=args.convergence_walkers,
                chunk=args.chunk,
                dt=args.dt,
                tmax=args.tmax,
                seed=args.seed,
                kappa_bar=kappa_bar,
            )
            path = DATA / (
                f"offlattice_fold_dtcheck_theta{theta:g}_"
                f"{args.convergence_walkers}.json"
            )
            _write_json(
                path,
                {
                    "parameters": _base_parameters(args),
                    "kappa_bar": kappa_block,
                    "dt_halving": report,
                },
            )
            print(
                f"dt-halving theta={theta:g}: max|z|={report['max_abs_z']:.2f} "
                f"mean|z|={report['mean_abs_z']:.2f} "
                f"frac|z|>2={report['fraction_abs_z_above_2']:.3f} "
                f"({report['usable_bins']} bins) -> {path}"
            )
        return

    gate_one = gate_no_killing(args.seed, dt=args.dt, kappa_bar=kappa_bar)
    print(
        f"gate kappa=0 PASS: contact_steps={gate_one['contact_steps']} kills=0"
    )

    csv_rows: list[dict] = []
    for theta in args.theta:
        print(f"simulating theta={theta:g} walkers={args.walkers} ...", flush=True)
        result = run_theta(
            theta,
            walkers=args.walkers,
            chunk=args.chunk,
            dt=args.dt,
            tmax=args.tmax,
            seed=args.seed,
            kappa_bar=kappa_bar,
        )
        summary = summarize_theta(result, dt=args.dt, tmax=args.tmax)
        payload = {
            "parameters": {**_base_parameters(args), "theta": theta},
            "kappa_bar": kappa_block,
            "validation_gates": {
                "gate1_kappa_zero_no_kills": gate_one,
                "gate3_kill_probability_max": summary["kill_probability_max"],
                "gate3_kill_probability_in_unit_interval": bool(
                    0.0 <= summary["kill_probability_max"] <= 1.0
                ),
            },
            "results": summary,
        }
        path = DATA / f"offlattice_fold_theta{theta:g}_{args.walkers}.json"
        _write_json(path, payload)
        significant = summary["modal_structure_diagnostic"]["significant_maxima"]
        peak_times = ", ".join(f"{row['time']:.2f}" for row in significant)
        print(
            f"theta={theta:g}: kill_fraction={summary['kill_fraction']:.6f} "
            f"survivors={summary['survivors']} "
            f"channels bg/near/far="
            f"{summary['channel_fractions']['background']:.4f}/"
            f"{summary['channel_fractions']['near']:.4f}/"
            f"{summary['channel_fractions']['far']:.4f} "
            f"kills[10,30]={summary['kills_in_structure_window_10_30']} "
            f"significant maxima at t=[{peak_times}] "
            f"runtime={summary['runtime_seconds']:.1f}s -> {path}"
        )
        csv_rows.append(
            {
                "theta": theta,
                "walkers": args.walkers,
                "dt": args.dt,
                "tmax": args.tmax,
                "seed": args.seed,
                "kappa_bar": kappa_bar,
                "kill_fraction": summary["kill_fraction"],
                "survivors": summary["survivors"],
                "fraction_background": summary["channel_fractions"]["background"],
                "fraction_near": summary["channel_fractions"]["near"],
                "fraction_far": summary["channel_fractions"]["far"],
                "kills_in_window_5_60": summary["kills_in_window_5_60"],
                "kills_in_structure_window_10_30": summary[
                    "kills_in_structure_window_10_30"
                ],
                "significant_maxima_count": len(significant),
                "significant_maxima_times": ";".join(
                    f"{row['time']:.3f}" for row in significant
                ),
                "kill_probability_max": summary["kill_probability_max"],
                "walker_steps": summary["walker_steps"],
                "runtime_seconds": summary["runtime_seconds"],
                "runtime_seconds_per_1e6_walkers": summary[
                    "runtime_seconds_per_1e6_walkers"
                ],
            }
        )
    csv_path = DATA / "offlattice_fold_summary.csv"
    _write_csv(csv_path, csv_rows)
    print(f"combined summary -> {csv_path}")


if __name__ == "__main__":
    main()
