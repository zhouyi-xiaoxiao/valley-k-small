#!/usr/bin/env python3
"""Cell-averaged, successively refined continuation of the matched-budget fold.

This script refines the finite-lattice fold certificate of
``validate_2d_matched_fold.py`` on a square-cell ladder ``n x n`` with
``n in (9, 13, 17, 21, 25)`` and ``h = 1/(n-1)`` per axis.  Three ingredients
differ from the binary-mask certificate:

1. anti-aliased killing fields: every product state carries the fraction of
   its four-dimensional Voronoi product cell (half-cells at the reflecting
   boundaries) inside the continuum killing region
   ``{|x1-x2| < a} ∩ {(x1+x2)/2 in patch}``, computed by tensorized midpoint
   subsampling with four points per axis per particle cell (256 subsamples
   per product cell);
2. control-volume budget matching: the theta-invariant reactivity budget is
   the trapezoidal control-volume quadrature ``B(theta) = <w, kappa_theta>``
   and ``kappa_bar_h`` is recomputed per grid so the budget is exactly
   theta-independent, with the continuum budget recorded from a refined
   quadrature reference;
3. two transport discretizations on the same ladder: the existing upwind
   rates and a Scharfetter-Gummel exponential-fitting scheme, so the fold
   location can be Richardson-extrapolated per discretization and the
   cross-discretization gap of the extrapolants reported.

Fold derivatives remain actions of the sparse generator with the augmented
matrix-exponential parameter sensitivity; no sampled finite differences enter
the fold equations.  A failed fold search is recorded honestly with bounded
scan diagnostics instead of being forced.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.integrate import quad
from scipy.optimize import brentq, root
from scipy.sparse.linalg import expm_multiply
from vkcore.encounter2d import (
    DoiCatalyticPatch,
    RectangularGrid2D,
    build_doi_encounter_2d,
    contact_safe_initial_distribution_2d,
    initial_distribution_diagnostics_2d,
    reflecting_advection_diffusion_generator_2d,
)

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
DATA.mkdir(parents=True, exist_ok=True)

LEVELS = (9, 13, 17, 21, 25, 29, 33, 37, 41)
SUBSAMPLES_PER_AXIS = 4
CHUNK_PRODUCT_STATES = 8192
SERIES_MEMORY_STATES = 5.0e7

REACTION_RADIUS = 0.17
START_ONE = (0.0, 0.5)
START_TWO = (0.28, 0.5)
WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.115,
    "transverse_confinement": 1.5,
}
WALKER_TWO = {
    "diffusion": 0.0008,
    "drift_x": 0.02,
    "transverse_confinement": 1.5,
}
NEAR_CENTRE = (0.25, 0.5)
NEAR_RADIUS = 0.18
NEAR_RATE = 0.5
FAR_CENTRE = (0.72, 0.5)
FAR_RADIUS = 0.20
FAR_RATE = 15.0

DISCRETIZATIONS = ("upwind", "scharfetter_gummel")
SG_CENTRAL_PECLET = 1e-8
MASS_BALANCE_RTOL = 1e-11
BUDGET_MATCH_RTOL = 1e-11
FOLD_ROOT_TOLERANCE = 1e-11
FOLD_RESIDUAL_TOLERANCE = 1e-8
FOLD_DETERMINANT_TOLERANCE = 1e-14
THETA_SEARCH_INTERVAL = (-0.5, 1.0)
TIME_SEARCH_INTERVAL = (0.0, 60.0)
DEFAULT_FOLD_SEEDS = (
    (17.0, 0.25),
    (16.5, 0.30),
    (18.0, 0.15),
    (18.5, 0.28),
    (19.5, -0.10),
    (20.0, -0.30),
    (15.0, 0.40),
    (14.0, 0.45),
)
SCALING_MU = np.asarray(
    (0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05),
    dtype=float,
)
SCALING_FIT_COUNT = 6
SCALING_BRACKET_FACTOR_LIMIT = 64.0
SCAN_THETA_COUNT = 16
SCAN_TIME_MAX = 40.0
SCAN_TIME_POINTS = 401
RICHARDSON_LEVEL_COUNT = 3
CONTINUUM_MIDPOINT_PANELS = (1024, 2048, 4096)
TUBE_MIDPOINT_PANELS = 2048


def _axis_cell_samples(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Return midpoint subsample coordinates and Voronoi widths per axis node.

    The Voronoi cell of node ``i`` is ``[x_i - h/2, x_i + h/2]`` clipped to
    ``[0, 1]``; boundary nodes therefore carry half-cells.  Subsamples are the
    ``s`` midpoint points of the clipped cell, so cell fractions are unbiased
    midpoint-rule estimates of the continuum indicator average over the cell.
    """

    if n < 2:
        raise ValueError("axis must contain at least two nodes")
    spacing = 1.0 / (n - 1)
    nodes = np.arange(n, dtype=float) * spacing
    lower = np.maximum(nodes - 0.5 * spacing, 0.0)
    upper = np.minimum(nodes + 0.5 * spacing, 1.0)
    offsets = (np.arange(SUBSAMPLES_PER_AXIS, dtype=float) + 0.5) / float(
        SUBSAMPLES_PER_AXIS
    )
    samples = lower[:, None] + offsets[None, :] * (upper - lower)[:, None]
    widths = upper - lower
    return samples, widths


def _single_state_samples(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return per-single-state x/y subsamples and control-volume weights.

    Single-walker state order matches :class:`RectangularGrid2D`:
    ``state = ix * n + iy``.  The control-volume weight of a state is the area
    of its clipped Voronoi cell, i.e. exactly the tensor trapezoidal weight
    ``q_x q_y h^2`` with ``q = 1`` interior and ``q = 1/2`` at boundaries.
    """

    samples, widths = _axis_cell_samples(n)
    index_x = np.repeat(np.arange(n), n)
    index_y = np.tile(np.arange(n), n)
    return samples[index_x], samples[index_y], np.kron(widths, widths)


def _product_control_volume_weights(n: int) -> np.ndarray:
    _, _, single = _single_state_samples(n)
    weights = np.kron(single, single)
    if abs(float(weights.sum()) - 1.0) > 1e-12:
        raise RuntimeError("product control-volume weights do not sum to one")
    return weights


def _cell_fraction_fields(n: int) -> dict[str, np.ndarray]:
    """Return cell-averaged tube and patch killing-region fractions.

    For every product state the returned values are the fraction of the
    four-dimensional product Voronoi cell inside ``{|x1-x2| < a}`` (tube) and
    inside ``{|x1-x2| < a} ∩ {(x1+x2)/2 in patch}`` (near/far), from
    ``SUBSAMPLES_PER_AXIS**4`` tensorized midpoint subsamples.  Chunked so
    peak memory stays far below 4 GB even on the finest ladder level.
    """

    sample_x, sample_y, _ = _single_state_samples(n)
    single_states = n * n
    product_states = single_states * single_states
    frac_tube = np.empty(product_states, dtype=float)
    frac_near = np.empty(product_states, dtype=float)
    frac_far = np.empty(product_states, dtype=float)
    radius_squared = REACTION_RADIUS**2
    near_radius_squared = NEAR_RADIUS**2
    far_radius_squared = FAR_RADIUS**2
    total_subsamples = float(SUBSAMPLES_PER_AXIS**4)
    for start in range(0, product_states, CHUNK_PRODUCT_STATES):
        stop = min(start + CHUNK_PRODUCT_STATES, product_states)
        indices = np.arange(start, stop)
        first = indices // single_states
        second = indices % single_states
        x1 = sample_x[first][:, :, None, None, None]
        y1 = sample_y[first][:, None, :, None, None]
        x2 = sample_x[second][:, None, None, :, None]
        y2 = sample_y[second][:, None, None, None, :]
        dx = x1 - x2
        dy = y1 - y2
        tube = (dx * dx + dy * dy) < radius_squared
        centre_x = 0.5 * (x1 + x2)
        centre_y = 0.5 * (y1 + y2)
        near = (
            (centre_x - NEAR_CENTRE[0]) ** 2 + (centre_y - NEAR_CENTRE[1]) ** 2
            <= near_radius_squared
        ) & tube
        far = (
            (centre_x - FAR_CENTRE[0]) ** 2 + (centre_y - FAR_CENTRE[1]) ** 2
            <= far_radius_squared
        ) & tube
        frac_tube[start:stop] = tube.sum(axis=(1, 2, 3, 4)) / total_subsamples
        frac_near[start:stop] = near.sum(axis=(1, 2, 3, 4)) / total_subsamples
        frac_far[start:stop] = far.sum(axis=(1, 2, 3, 4)) / total_subsamples
    for name, values in (
        ("tube", frac_tube),
        ("near", frac_near),
        ("far", frac_far),
    ):
        if np.any(values < 0.0) or np.any(values > 1.0):
            raise RuntimeError(f"cell {name} fractions escaped [0, 1]")
    if np.any(frac_near + frac_far > frac_tube + 1e-12):
        raise RuntimeError("patch cell fractions exceeded the tube fraction")
    if not np.any(frac_tube > 0.0):
        raise RuntimeError("cell-averaged tube fraction vanished everywhere")
    return {"tube": frac_tube, "near": frac_near, "far": frac_far}


def _scharfetter_gummel_edge_rates(
    diffusion: float,
    spacing: float,
    edge_drift: float,
) -> tuple[float, float]:
    """Return the (forward, backward) exponential-fitting rates for one edge.

    ``forward = (D/h^2) Pe / (1 - exp(-Pe))`` and
    ``backward = (D/h^2) Pe / (exp(Pe) - 1)`` with ``Pe = v_edge h / D``,
    evaluated with the numerically stable ``expm1`` forms.  Below
    ``|Pe| < 1e-8`` the central limit ``(D/h^2)(1 ± Pe/2)`` is used.
    """

    if not np.isfinite(diffusion) or diffusion <= 0.0:
        raise ValueError("Scharfetter-Gummel rates require positive diffusion")
    base = diffusion / spacing**2
    peclet = float(edge_drift) * spacing / diffusion
    if abs(peclet) < SG_CENTRAL_PECLET:
        return base * (1.0 + 0.5 * peclet), base * (1.0 - 0.5 * peclet)
    forward = base * peclet / (-np.expm1(-peclet))
    backward = base * peclet / np.expm1(peclet)
    return float(forward), float(backward)


def scharfetter_gummel_generator_2d(
    grid: RectangularGrid2D,
    *,
    diffusion: float,
    drift_x: float = 0.0,
    transverse_confinement: float = 0.0,
    transverse_centre: float | None = None,
) -> sparse.csr_matrix:
    """Return a Scharfetter-Gummel CTMC generator on the reflecting grid.

    The physical drift is ``(drift_x, -gamma (y - y0))``; ``v_edge`` is the
    drift evaluated at the edge midpoint.  Reflection uses the same omitted
    outward-jump convention as
    :func:`vkcore.encounter2d.reflecting_advection_diffusion_generator_2d`.
    """

    diffusivity = float(diffusion)
    vx = float(drift_x)
    gamma = float(transverse_confinement)
    y0 = float(
        grid.length_y / 2.0 if transverse_centre is None else transverse_centre
    )
    if not np.isfinite(diffusivity) or diffusivity <= 0.0:
        raise ValueError("diffusion must be finite and positive")
    if not np.isfinite(vx):
        raise ValueError("drift_x must be finite")
    if not np.isfinite(gamma) or gamma < 0.0:
        raise ValueError("transverse_confinement must be finite and nonnegative")
    if not np.isfinite(y0) or not 0.0 <= y0 <= grid.length_y:
        raise ValueError("transverse_centre must lie in the physical domain")

    hx = grid.spacing_x
    hy = grid.spacing_y
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    escape = np.zeros(grid.state_count, dtype=float)

    def add_edge(source: int, target: int, rate: float) -> None:
        if not np.isfinite(rate) or rate < 0.0:
            raise RuntimeError(f"Scharfetter-Gummel produced invalid rate {rate!r}")
        rows.append(source)
        columns.append(target)
        values.append(float(rate))
        escape[source] += float(rate)

    forward_x, backward_x = _scharfetter_gummel_edge_rates(diffusivity, hx, vx)
    for ix in range(grid.nx - 1):
        for iy in range(grid.ny):
            left = grid.state_index(ix, iy)
            right = grid.state_index(ix + 1, iy)
            add_edge(left, right, forward_x)
            add_edge(right, left, backward_x)
    for iy in range(grid.ny - 1):
        edge_midpoint_y = (iy + 0.5) * hy
        vy_edge = -gamma * (edge_midpoint_y - y0)
        forward_y, backward_y = _scharfetter_gummel_edge_rates(
            diffusivity,
            hy,
            vy_edge,
        )
        for ix in range(grid.nx):
            low = grid.state_index(ix, iy)
            high = grid.state_index(ix, iy + 1)
            add_edge(low, high, forward_y)
            add_edge(high, low, backward_y)
    for state in range(grid.state_count):
        rows.append(state)
        columns.append(state)
        values.append(float(-escape[state]))
    generator = sparse.csr_matrix(
        (values, (rows, columns)),
        shape=(grid.state_count, grid.state_count),
    )
    _assert_mass_balance(generator, "Scharfetter-Gummel single-walker generator")
    return generator


def _assert_mass_balance(generator: sparse.spmatrix, label: str) -> float:
    """Assert relative row-sum mass balance and return the relative error."""

    row_sums = np.asarray(generator.sum(axis=1)).reshape(-1)
    scale = max(
        float(np.max(np.abs(generator.diagonal()))),
        float(np.finfo(float).tiny),
    )
    relative_error = float(np.max(np.abs(row_sums))) / scale
    if relative_error > MASS_BALANCE_RTOL:
        raise RuntimeError(
            f"{label} violated mass balance: relative row error={relative_error:g}"
        )
    return relative_error


def _clipped_disk_area(radius: float, signed_cut: float) -> float:
    """Area of the disk portion with ``x <= centre_x + signed_cut``."""

    cut = float(np.clip(signed_cut, -radius, radius))
    return float(
        cut * np.sqrt(max(0.0, radius**2 - cut**2))
        + radius**2 * (np.arcsin(cut / radius) + 0.5 * np.pi)
    )


def _patch_available_area(centre_x: float, radius: float, boundary: str, relative_x: float) -> float:
    """Midpoint-feasible patch area for relative separation ``relative_x >= 0``."""

    if boundary == "left":
        return float(
            np.pi * radius**2
            - _clipped_disk_area(radius, 0.5 * relative_x - centre_x)
        )
    if boundary == "right":
        return _clipped_disk_area(radius, (1.0 - 0.5 * relative_x) - centre_x)
    raise ValueError("boundary must be left or right")


def _patch_joint_volume(
    centre_x: float,
    radius: float,
    boundary: str,
) -> dict[str, float]:
    """4D volume of ``{|X1-X2|<a} ∩ {midpoint in patch}`` with refinement audit.

    After the exact change of variables to midpoint and relative coordinates,
    the volume reduces to a one-dimensional integral over ``|r_x|`` with the
    analytic relative-``y`` width and a boundary-clipped disk area.  The
    reduction requires (and asserts) that neither ``y`` clipping nor
    opposite-side ``x`` clipping is active for these patch geometries.
    """

    half_a = 0.5 * REACTION_RADIUS
    if centre_x - radius < -1e-15 or centre_x + radius > 1.0 + 1e-15:
        raise ValueError("patch must lie inside the unit domain")
    if not (0.5 - radius > half_a and 0.5 + radius < 1.0 - half_a):
        raise ValueError("patch geometry would require y clipping")
    if boundary == "left" and centre_x + radius > 1.0 - half_a:
        raise ValueError("left-boundary patch would clip on the right")
    if boundary == "right" and centre_x - radius < half_a:
        raise ValueError("right-boundary patch would clip on the left")

    def integrand(relative_x: float) -> float:
        return float(
            4.0
            * np.sqrt(max(0.0, REACTION_RADIUS**2 - relative_x**2))
            * _patch_available_area(centre_x, radius, boundary, relative_x)
        )

    if boundary == "left":
        break_point = 2.0 * (centre_x - radius)
    else:
        break_point = 2.0 * (1.0 - centre_x - radius)
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
    midpoint_values = []
    for panels in CONTINUUM_MIDPOINT_PANELS:
        nodes = (np.arange(panels, dtype=float) + 0.5) * (REACTION_RADIUS / panels)
        midpoint_values.append(
            float(
                np.sum([integrand(float(node)) for node in nodes])
                * (REACTION_RADIUS / panels)
            )
        )
    return {
        "volume": float(value),
        "adaptive_quadrature_error_estimate": float(error),
        "midpoint_refinement_panels": list(CONTINUUM_MIDPOINT_PANELS),
        "midpoint_refinement_values": midpoint_values,
        "midpoint_refinement_final_gap": abs(midpoint_values[-1] - float(value)),
    }


def _tube_volume_reference() -> dict[str, float]:
    """Analytic 4D encounter-tube volume with a midpoint refinement audit."""

    a = REACTION_RADIUS
    analytic = float(np.pi * a**2 - (8.0 / 3.0) * a**3 + 0.5 * a**4)
    panels = TUBE_MIDPOINT_PANELS
    step = 2.0 * a / panels
    axis = -a + (np.arange(panels, dtype=float) + 0.5) * step
    rx = axis[:, None]
    ry = axis[None, :]
    inside = rx * rx + ry * ry < a * a
    midpoint = float(
        np.sum((1.0 - np.abs(rx)) * (1.0 - np.abs(ry)) * inside) * step * step
    )
    return {
        "analytic": analytic,
        "midpoint_panels_per_axis": panels,
        "midpoint": midpoint,
        "midpoint_gap": abs(midpoint - analytic),
    }


def _continuum_budget_reference() -> dict[str, object]:
    """Continuum budget and homogeneous rate from refined quadratures."""

    near = _patch_joint_volume(NEAR_CENTRE[0], NEAR_RADIUS, "left")
    far = _patch_joint_volume(FAR_CENTRE[0], FAR_RADIUS, "right")
    tube = _tube_volume_reference()
    budget = NEAR_RATE * near["volume"] + FAR_RATE * far["volume"]
    return {
        "budget": float(budget),
        "kappa_bar": float(budget / tube["analytic"]),
        "near_patch_joint_volume": near,
        "far_patch_joint_volume": far,
        "tube_volume": tube,
        "reduction": (
            "midpoint/relative change of variables; one-dimensional adaptive "
            "quadrature over |r_x| with analytic relative-y width, plus "
            "composite-midpoint refinement sequences as the refinement audit"
        ),
    }


@dataclass(frozen=True)
class RefinedFamily:
    """One matched-budget continuation on one grid and one discretization."""

    n: int
    discretization: str
    A0: sparse.csr_matrix
    Atheta: sparse.csr_matrix
    k0: np.ndarray
    ktheta: np.ndarray
    initial: np.ndarray


@dataclass(frozen=True)
class RefinedLevel:
    """Shared per-grid data: fields, weights, budgets, and both families."""

    n: int
    grid: RectangularGrid2D
    weights: np.ndarray
    fractions: dict[str, np.ndarray]
    kappa_pattern: np.ndarray
    kappa_bar: float
    budget: float
    families: dict[str, RefinedFamily]
    shared_record: dict[str, object]
    mass_balance: dict[str, float]


def _operator(
    family: RefinedFamily,
    theta: float,
) -> tuple[sparse.csr_matrix, np.ndarray]:
    return (
        family.A0 + float(theta) * family.Atheta,
        family.k0 + float(theta) * family.ktheta,
    )


def _state(family: RefinedFamily, time_value: float, theta: float) -> np.ndarray:
    operator, _ = _operator(family, theta)
    return np.asarray(
        expm_multiply(operator.T * float(time_value), family.initial),
        dtype=float,
    )


def _state_and_sensitivity(
    family: RefinedFamily,
    time_value: float,
    theta: float,
) -> tuple[np.ndarray, np.ndarray]:
    operator, _ = _operator(family, theta)
    n = family.initial.size
    augmented = sparse.bmat(
        [
            [operator.T, None],
            [family.Atheta.T, operator.T],
        ],
        format="csr",
    )
    augmented_initial = np.concatenate((family.initial, np.zeros(n, dtype=float)))
    value = np.asarray(
        expm_multiply(augmented * float(time_value), augmented_initial),
        dtype=float,
    )
    return value[:n], value[n:]


def _fold_quantities(
    family: RefinedFamily,
    time_value: float,
    theta: float,
    *,
    sensitivity: bool,
) -> dict[str, float]:
    operator, killing = _operator(family, theta)
    if sensitivity:
        state, state_theta = _state_and_sensitivity(family, time_value, theta)
    else:
        state = _state(family, time_value, theta)
        state_theta = None
    Ak = np.asarray(operator @ killing, dtype=float)
    A2k = np.asarray(operator @ Ak, dtype=float)
    A3k = np.asarray(operator @ A2k, dtype=float)
    values = {
        "f": float(np.dot(state, killing)),
        "f_t": float(np.dot(state, Ak)),
        "f_tt": float(np.dot(state, A2k)),
        "f_ttt": float(np.dot(state, A3k)),
        "survival": float(state.sum()),
    }
    if sensitivity:
        assert state_theta is not None
        derivative_Ak = family.Atheta @ killing + operator @ family.ktheta
        derivative_A2k = (
            family.Atheta @ Ak
            + operator @ (family.Atheta @ killing)
            + operator @ (operator @ family.ktheta)
        )
        values["f_ttheta"] = float(
            np.dot(state_theta, Ak) + np.dot(state, derivative_Ak)
        )
        values["f_tt_theta"] = float(
            np.dot(state_theta, A2k) + np.dot(state, derivative_A2k)
        )
        values["state_theta_l1"] = float(np.linalg.norm(state_theta, ord=1))
    return values


def _ft(family: RefinedFamily, time_value: float, theta: float) -> float:
    return _fold_quantities(family, time_value, theta, sensitivity=False)["f_t"]


def _dot_series(
    family: RefinedFamily,
    theta: float,
    times: np.ndarray,
    vectors: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Chunked expm series returning ``<state, vector>`` traces and survival."""

    operator, _ = _operator(family, theta)
    time_array = np.asarray(times, dtype=float)
    if time_array.size < 2 or not np.allclose(
        np.diff(time_array),
        time_array[1] - time_array[0],
        rtol=1e-11,
        atol=1e-14,
    ):
        raise ValueError("series times must be a nontrivial uniform grid")
    time_step = float(time_array[1] - time_array[0])
    series = {name: np.empty(time_array.size, dtype=float) for name in vectors}
    survival = np.empty(time_array.size, dtype=float)
    current = (
        family.initial.copy()
        if time_array[0] == 0.0
        else np.asarray(
            expm_multiply(operator.T * float(time_array[0]), family.initial),
            dtype=float,
        )
    )
    chunk_intervals = int(
        max(8, min(200, SERIES_MEMORY_STATES // max(1, family.initial.size)))
    )
    start_index = 0
    while start_index < time_array.size:
        stop_index = min(start_index + chunk_intervals, time_array.size - 1)
        interval_count = stop_index - start_index
        if interval_count == 0:
            states = current.reshape(1, -1)
        else:
            states = np.asarray(
                expm_multiply(
                    operator.T,
                    current,
                    start=0.0,
                    stop=interval_count * time_step,
                    num=interval_count + 1,
                    endpoint=True,
                ),
                dtype=float,
            )
        local_slice = slice(start_index, stop_index + 1)
        for name, vector in vectors.items():
            series[name][local_slice] = np.dot(states, vector)
        survival[local_slice] = states.sum(axis=1)
        current = states[-1].copy()
        if stop_index == time_array.size - 1:
            break
        start_index = stop_index
    return series, survival


def _evaluate_fold_point(
    family: RefinedFamily,
    time_value: float,
    theta: float,
) -> dict[str, object]:
    """Evaluate residual gates, margins, and nondegeneracy at one point."""

    values = _fold_quantities(family, time_value, theta, sensitivity=True)
    density = float(values["f"])
    density_scale = max(abs(density), float(np.finfo(float).tiny))
    time_scale = abs(float(time_value))
    dimensionless_f_t = abs(values["f_t"]) * time_scale / density_scale
    dimensionless_f_tt = abs(values["f_tt"]) * time_scale**2 / density_scale
    margin_f_ttt = values["f_ttt"] * time_scale**3 / density_scale
    margin_f_ttheta = values["f_ttheta"] * time_scale / density_scale
    determinant = (
        values["f_tt"] * values["f_tt_theta"]
        - values["f_ttheta"] * values["f_ttt"]
    )
    fold_limit_determinant = -values["f_ttheta"] * values["f_ttt"]
    reasons: list[str] = []
    if not (TIME_SEARCH_INTERVAL[0] < time_value < TIME_SEARCH_INTERVAL[1]):
        reasons.append("time outside the declared search interval")
    if not (
        THETA_SEARCH_INTERVAL[0] <= theta <= THETA_SEARCH_INTERVAL[1]
    ):
        reasons.append("theta outside the declared search interval")
    if density <= 0.0 or not np.isfinite(density):
        reasons.append("density at the candidate fold is not positive")
    if max(dimensionless_f_t, dimensionless_f_tt) > FOLD_RESIDUAL_TOLERANCE:
        reasons.append("normalized fold residual gate failed")
    if (
        not np.isfinite(determinant)
        or abs(determinant) <= FOLD_DETERMINANT_TOLERANCE
        or values["f_ttt"] == 0.0
        or values["f_ttheta"] == 0.0
    ):
        reasons.append("fold Jacobian is degenerate")
    return {
        "time": float(time_value),
        "theta": float(theta),
        "theta_physical": bool(0.0 < theta < 1.0),
        "density": density,
        "survival": float(values["survival"]),
        "f_t_residual": float(values["f_t"]),
        "f_tt_residual": float(values["f_tt"]),
        "dimensionless_f_t_residual": float(dimensionless_f_t),
        "dimensionless_f_tt_residual": float(dimensionless_f_tt),
        "max_dimensionless_residual": float(
            max(dimensionless_f_t, dimensionless_f_tt)
        ),
        "f_ttt": float(values["f_ttt"]),
        "f_ttheta": float(values["f_ttheta"]),
        "f_tt_theta": float(values["f_tt_theta"]),
        "normalized_margin_f_ttt": float(margin_f_ttt),
        "normalized_margin_f_ttheta": float(margin_f_ttheta),
        "state_theta_l1": float(values["state_theta_l1"]),
        "jacobian_determinant": float(determinant),
        "fold_limit_determinant": float(fold_limit_determinant),
        "accepted": not reasons,
        "rejection_reasons": reasons,
        "residual_gate_tolerance": FOLD_RESIDUAL_TOLERANCE,
        "nondegeneracy_gate_tolerance": FOLD_DETERMINANT_TOLERANCE,
        "derivative_method": (
            "sparse generator actions plus augmented expm sensitivity"
        ),
    }


class _FoldEvaluationError(RuntimeError):
    """Raised when a Newton iterate leaves the safe evaluation box."""


FOLD_EVALUATION_TIME_BOX = (1e-6, 1e4)
FOLD_EVALUATION_THETA_BOX = (-1e3, 1e3)


def _guarded_fold_point(point: np.ndarray) -> tuple[float, float]:
    time_value = float(point[0])
    theta = float(point[1])
    if (
        not np.isfinite(time_value)
        or not np.isfinite(theta)
        or not FOLD_EVALUATION_TIME_BOX[0] <= time_value <= FOLD_EVALUATION_TIME_BOX[1]
        or not FOLD_EVALUATION_THETA_BOX[0] <= theta <= FOLD_EVALUATION_THETA_BOX[1]
    ):
        raise _FoldEvaluationError(
            f"Newton iterate left the safe evaluation box: {point.tolist()!r}"
        )
    return time_value, theta


def _solve_fold(
    family: RefinedFamily,
    seeds: tuple[tuple[float, float], ...],
) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
    """Newton root solve of ``(f_t, f_tt) = 0`` from a deterministic seed list."""

    def objective(point: np.ndarray) -> np.ndarray:
        time_value, theta = _guarded_fold_point(point)
        values = _fold_quantities(
            family,
            time_value,
            theta,
            sensitivity=True,
        )
        return np.asarray((values["f_t"], values["f_tt"]), dtype=float)

    def jacobian(point: np.ndarray) -> np.ndarray:
        time_value, theta = _guarded_fold_point(point)
        values = _fold_quantities(
            family,
            time_value,
            theta,
            sensitivity=True,
        )
        return np.asarray(
            (
                (values["f_tt"], values["f_ttheta"]),
                (values["f_ttt"], values["f_tt_theta"]),
            ),
            dtype=float,
        )

    attempts: list[dict[str, object]] = []
    for seed in seeds:
        try:
            solution = root(
                objective,
                np.asarray(seed, dtype=float),
                jac=jacobian,
                tol=FOLD_ROOT_TOLERANCE,
            )
        except (_FoldEvaluationError, ValueError, OverflowError) as error:
            attempts.append(
                {
                    "seed": [float(seed[0]), float(seed[1])],
                    "root_success": False,
                    "root_message": f"evaluation aborted: {error}",
                    "solution": None,
                }
            )
            continue
        attempt: dict[str, object] = {
            "seed": [float(seed[0]), float(seed[1])],
            "root_success": bool(solution.success),
            "root_message": str(solution.message),
            "solution": [float(solution.x[0]), float(solution.x[1])],
        }
        if not solution.success:
            attempts.append(attempt)
            continue
        record = _evaluate_fold_point(
            family,
            float(solution.x[0]),
            float(solution.x[1]),
        )
        attempt["evaluation"] = record
        attempts.append(attempt)
        if record["accepted"]:
            fold = dict(record)
            fold["seed"] = [float(seed[0]), float(seed[1])]
            fold["seed_attempts"] = len(attempts)
            return fold, attempts
    return None, attempts


def _no_fold_scan(family: RefinedFamily) -> dict[str, object]:
    """Bounded curvature-branch scan recorded when no fold root is accepted.

    For each theta in a fixed grid over the declared search interval the
    ``f_tt`` sign changes along a uniform time grid are refined by ``brentq``
    and ``f_t`` is evaluated on that curvature branch.  Small normalized
    ``|f_t|`` on the branch would indicate a nearby fold; uniformly large
    values document its absence within the scanned window.  This is a bounded
    diagnostic, not an exhaustive root-count proof.
    """

    thetas = np.linspace(
        THETA_SEARCH_INTERVAL[0],
        THETA_SEARCH_INTERVAL[1],
        SCAN_THETA_COUNT,
    )
    times = np.linspace(0.0, SCAN_TIME_MAX, SCAN_TIME_POINTS)
    branch_rows: list[dict[str, float]] = []
    for theta in thetas:
        operator, killing = _operator(family, float(theta))
        Ak = np.asarray(operator @ killing, dtype=float)
        A2k = np.asarray(operator @ Ak, dtype=float)
        series, _ = _dot_series(
            family,
            float(theta),
            times,
            {"f": killing, "f_t": Ak, "f_tt": A2k},
        )
        second = series["f_tt"]
        crossings = np.flatnonzero(second[:-1] * second[1:] < 0.0)
        for index in crossings:
            if times[index] <= 0.0:
                continue
            branch_time = float(
                brentq(
                    lambda value: _fold_quantities(
                        family,
                        value,
                        float(theta),
                        sensitivity=False,
                    )["f_tt"],
                    float(times[index]),
                    float(times[index + 1]),
                    xtol=1e-10,
                    rtol=1e-12,
                )
            )
            values = _fold_quantities(
                family,
                branch_time,
                float(theta),
                sensitivity=False,
            )
            density_scale = max(abs(values["f"]), float(np.finfo(float).tiny))
            branch_rows.append(
                {
                    "theta": float(theta),
                    "time": branch_time,
                    "f": float(values["f"]),
                    "f_t": float(values["f_t"]),
                    "normalized_f_t": float(
                        abs(values["f_t"]) * branch_time / density_scale
                    ),
                }
            )
    closest = (
        min(branch_rows, key=lambda row: row["normalized_f_t"])
        if branch_rows
        else None
    )
    return {
        "claim_boundary": (
            "bounded curvature-branch scan only; fold absence is not proved "
            "outside the declared theta/time window and seed list"
        ),
        "theta_interval": list(THETA_SEARCH_INTERVAL),
        "theta_points": int(thetas.size),
        "time_interval": [0.0, SCAN_TIME_MAX],
        "time_points": int(times.size),
        "curvature_branch_root_count": len(branch_rows),
        "closest_branch_point": closest,
        "curvature_branch_rows": branch_rows,
    }


def _stationary_point(
    family: RefinedFamily,
    theta: float,
    left: float,
    right: float,
) -> dict[str, float | str]:
    time_value = float(
        brentq(
            lambda value: _ft(family, value, theta),
            float(left),
            float(right),
            xtol=2e-12,
            rtol=2e-14,
        )
    )
    values = _fold_quantities(family, time_value, theta, sensitivity=False)
    return {
        "time": time_value,
        "density": values["f"],
        "f_t_residual": values["f_t"],
        "f_tt": values["f_tt"],
        "kind": "minimum" if values["f_tt"] > 0.0 else "maximum",
    }


def _scaling_spot_check(
    family: RefinedFamily,
    fold: dict[str, object],
) -> dict[str, object]:
    """Eight-offset independent continuation with normal-form comparison.

    The pair-creating side of the fold is chosen from the sign of
    ``-2 f_ttheta / f_ttt`` so a fold whose supercritical direction points to
    ``theta < theta_c`` is still audited rather than aborted.  Row failures
    are recorded honestly and disable the exponent fit instead of raising.
    """

    time_c = float(fold["time"])
    theta_c = float(fold["theta"])
    normal_coefficient = float(fold["f_ttheta"])
    curvature = float(fold["f_ttt"])
    ratio = -2.0 * normal_coefficient / curvature
    side = 1.0 if ratio > 0.0 else -1.0
    half_separation_coefficient = float(np.sqrt(abs(ratio)))
    separation_coefficient = 2.0 * half_separation_coefficient
    prominence_coefficient = float(
        2.0 / 3.0 * abs(curvature) * half_separation_coefficient**3
    )
    rows: list[dict[str, float]] = []
    failures: list[dict[str, float | str]] = []
    for mu in SCALING_MU:
        theta = theta_c + side * float(mu)
        predicted = half_separation_coefficient * float(np.sqrt(mu))
        try:
            factor = 2.0
            while _ft(family, time_c - factor * predicted, theta) > 0.0:
                factor *= 1.5
                if (
                    factor > SCALING_BRACKET_FACTOR_LIMIT
                    or time_c - factor * predicted <= 1e-3
                ):
                    raise RuntimeError("no negative-f_t bracket below the fold time")
            minimum = _stationary_point(
                family,
                theta,
                time_c - factor * predicted,
                time_c,
            )
            factor = 2.0
            while _ft(family, time_c + factor * predicted, theta) > 0.0:
                factor *= 1.5
                if factor > SCALING_BRACKET_FACTOR_LIMIT:
                    raise RuntimeError("no negative-f_t bracket above the fold time")
            maximum = _stationary_point(
                family,
                theta,
                time_c,
                time_c + factor * predicted,
            )
            separation = float(maximum["time"]) - float(minimum["time"])
            prominence = float(maximum["density"]) - float(minimum["density"])
            if separation <= 0.0 or prominence <= 0.0:
                raise RuntimeError(
                    "supercritical continuation did not create a min/max pair"
                )
        except (RuntimeError, ValueError) as error:
            failures.append(
                {"mu": float(mu), "theta": float(theta), "error": str(error)}
            )
            continue
        predicted_separation = separation_coefficient * float(np.sqrt(mu))
        predicted_prominence = prominence_coefficient * float(mu**1.5)
        rows.append(
            {
                "mu": float(mu),
                "theta": float(theta),
                "minimum_time": float(minimum["time"]),
                "maximum_time": float(maximum["time"]),
                "separation": separation,
                "prominence": prominence,
                "normal_form_separation": predicted_separation,
                "normal_form_prominence": predicted_prominence,
                "separation_ratio_to_normal_form": separation
                / predicted_separation,
                "prominence_ratio_to_normal_form": prominence
                / predicted_prominence,
                "minimum_f_t_residual": float(minimum["f_t_residual"]),
                "maximum_f_t_residual": float(maximum["f_t_residual"]),
            }
        )
    fit_mu = {float(mu) for mu in SCALING_MU[:SCALING_FIT_COUNT]}
    fit_rows = [row for row in rows if row["mu"] in fit_mu]
    if len(fit_rows) == SCALING_FIT_COUNT:
        log_mu = np.log([row["mu"] for row in fit_rows])
        separation_fit = np.polyfit(
            log_mu,
            np.log([row["separation"] for row in fit_rows]),
            1,
        )
        prominence_fit = np.polyfit(
            log_mu,
            np.log([row["prominence"] for row in fit_rows]),
            1,
        )
        fit = {
            "status": "ok",
            "fit_points": SCALING_FIT_COUNT,
            "fit_mu_max": float(fit_rows[-1]["mu"]),
            "separation_exponent": float(separation_fit[0]),
            "separation_prefactor": float(np.exp(separation_fit[1])),
            "prominence_exponent": float(prominence_fit[0]),
            "prominence_prefactor": float(np.exp(prominence_fit[1])),
            "expected_separation_exponent": 0.5,
            "expected_prominence_exponent": 1.5,
        }
    else:
        fit = {
            "status": "incomplete_rows",
            "fit_points_available": len(fit_rows),
            "fit_points_required": SCALING_FIT_COUNT,
        }
    return {
        "mu_values": SCALING_MU.tolist(),
        "supercritical_side": side,
        "normal_form_half_separation_coefficient": half_separation_coefficient,
        "normal_form_separation_coefficient": separation_coefficient,
        "normal_form_prominence_coefficient": prominence_coefficient,
        "rows": rows,
        "row_failures": failures,
        "fit": fit,
    }


def _richardson_fit(
    entries: list[tuple[int, float]],
    quantity: str,
) -> dict[str, object]:
    """Fit ``y(h) = y_star + C h^p`` on the three finest accepted levels.

    With exactly three levels and three parameters the least-squares problem
    is exactly determined, so the fit reduces to interpolation: ``p`` solves
    the level-ratio equation by bracketed root finding and ``(y_star, C)``
    follow in closed form.  Nonmonotone level sequences are recorded honestly
    instead of being forced into a positive convergence order.
    """

    base = {
        "quantity": quantity,
        "levels_available": [int(n) for n, _ in entries],
        "values": [float(value) for _, value in entries],
        "fit_form": "y(h) = y_star + C h^p on the three finest levels",
        "note": (
            "three-point least squares is exactly determined and reduces to "
            "interpolation"
        ),
    }
    if len(entries) < RICHARDSON_LEVEL_COUNT:
        return {**base, "status": "insufficient_levels"}
    finest = sorted(entries, key=lambda item: item[0])[-RICHARDSON_LEVEL_COUNT:]
    spacings = np.asarray([1.0 / (n - 1) for n, _ in finest], dtype=float)
    values = np.asarray([value for _, value in finest], dtype=float)
    order = np.argsort(spacings)
    h1, h2, h3 = spacings[order]
    y1, y2, y3 = values[order]
    used = {
        "levels_used": [int(finest[index][0]) for index in order[::-1]][::-1],
        "h_used": [float(h1), float(h2), float(h3)],
        "values_used": [float(y1), float(y2), float(y3)],
    }
    numerator = y2 - y1
    denominator = y3 - y2
    if denominator == 0.0 or numerator / denominator <= 0.0:
        return {
            **base,
            **used,
            "status": "nonmonotone_or_degenerate",
            "fallback_star": float(y1),
        }
    target = numerator / denominator

    def gap(order_p: float) -> float:
        return (h2**order_p - h1**order_p) / (h3**order_p - h2**order_p) - target

    probes = np.logspace(-2, np.log10(16.0), 200)
    bracket = None
    for left, right in zip(probes[:-1], probes[1:]):
        if gap(float(left)) * gap(float(right)) <= 0.0:
            bracket = (float(left), float(right))
            break
    if bracket is None:
        return {
            **base,
            **used,
            "status": "no_order_bracket",
            "fallback_star": float(y1),
        }
    order_p = float(brentq(gap, bracket[0], bracket[1], xtol=1e-13, rtol=1e-14))
    coefficient = float(numerator / (h2**order_p - h1**order_p))
    star = float(y1 - coefficient * h1**order_p)
    residual = float(abs(y3 - (star + coefficient * h3**order_p)))
    return {
        **base,
        **used,
        "status": "ok",
        "p": order_p,
        "star": star,
        "coefficient": coefficient,
        "third_point_residual": residual,
    }


def _selftest() -> dict[str, object]:
    """Executable validation gates for the SG rates and cell fractions."""

    for diffusion, spacing in ((0.0025, 0.125), (0.0008, 1.0 / 24.0), (1.3, 0.05)):
        forward, backward = _scharfetter_gummel_edge_rates(diffusion, spacing, 0.0)
        central = diffusion / spacing**2
        if forward != central or backward != central:
            raise RuntimeError("SG rates at v=0 are not the central rates")

    for peclet in (2e-8, -2e-8):
        forward, backward = _scharfetter_gummel_edge_rates(1.0, 1.0, peclet)
        central_forward = 1.0 + 0.5 * peclet
        central_backward = 1.0 - 0.5 * peclet
        if (
            abs(forward - central_forward) > 1e-12
            or abs(backward - central_backward) > 1e-12
        ):
            raise RuntimeError("SG stable form is discontinuous at the Pe switch")

    for diffusion, spacing, drift in (
        (0.0025, 0.125, 0.115),
        (0.0008, 1.0 / 24.0, -3.7),
        (0.05, 0.05, 12.0),
    ):
        forward, backward = _scharfetter_gummel_edge_rates(
            diffusion,
            spacing,
            drift,
        )
        identity_error = abs((forward - backward) - drift / spacing)
        if identity_error > 1e-10 * max(abs(forward), abs(backward), 1.0):
            raise RuntimeError("SG rates violated forward-backward = v/h")
        if forward < 0.0 or backward < 0.0:
            raise RuntimeError("SG rates went negative")

    for peclet in np.concatenate(
        (-np.logspace(-10, 2, 25), np.logspace(-10, 2, 25))
    ):
        forward, backward = _scharfetter_gummel_edge_rates(1.0, 1.0, float(peclet))
        if forward < 0.0 or backward < 0.0:
            raise RuntimeError("SG rates went negative on the Peclet sweep")

    grid = RectangularGrid2D(7, 7)
    sg_diffusion = scharfetter_gummel_generator_2d(grid, diffusion=0.37)
    upwind_diffusion = reflecting_advection_diffusion_generator_2d(
        grid,
        diffusion=0.37,
    )
    difference = (sg_diffusion - upwind_diffusion).tocoo()
    scale = float(np.max(np.abs(upwind_diffusion.diagonal())))
    if difference.nnz and float(np.max(np.abs(difference.data))) > 1e-12 * scale:
        raise RuntimeError(
            "pure-diffusion SG generator does not match the central generator"
        )

    fields = _cell_fraction_fields(5)
    weights = _product_control_volume_weights(5)
    if abs(float(weights.sum()) - 1.0) > 1e-12:
        raise RuntimeError("selftest control-volume weights lost normalization")
    if not 0.0 < float(np.dot(weights, fields["tube"])) < 1.0:
        raise RuntimeError("selftest tube measure is not inside (0, 1)")

    return {
        "status": "passed",
        "checks": [
            "sg_equals_central_at_zero_drift",
            "sg_stable_form_continuous_at_peclet_switch",
            "sg_forward_minus_backward_equals_advection",
            "sg_nonnegative_on_peclet_sweep",
            "sg_pure_diffusion_matches_central_generator",
            "cell_fractions_and_weights_sane_on_n5",
        ],
    }


def _build_level(n: int, continuum: dict[str, object]) -> RefinedLevel:
    """Assemble fields, budgets, initial law, and both families for level n."""

    grid = RectangularGrid2D(n, n)
    fractions = _cell_fraction_fields(n)
    weights = _product_control_volume_weights(n)
    kappa_pattern = NEAR_RATE * fractions["near"] + FAR_RATE * fractions["far"]
    tube_measure = float(np.dot(weights, fractions["tube"]))
    pattern_budget = float(np.dot(weights, kappa_pattern))
    if tube_measure <= 0.0 or pattern_budget <= 0.0:
        raise RuntimeError(f"level {n} produced an empty tube or pattern budget")
    kappa_bar = pattern_budget / tube_measure
    k0 = kappa_bar * fractions["tube"]
    k1 = kappa_pattern
    ktheta = k1 - k0
    budget_theta0 = float(np.dot(weights, k0))
    budget_theta1 = float(np.dot(weights, k1))
    budget_invariance = (
        max(
            abs(budget_theta0 - pattern_budget),
            abs(budget_theta1 - pattern_budget),
        )
        / pattern_budget
    )
    if budget_invariance > BUDGET_MATCH_RTOL:
        raise RuntimeError(
            f"level {n} budget is not theta-invariant: relative "
            f"error={budget_invariance:g}"
        )
    if float(np.min(k0)) < 0.0 or float(np.min(k1)) < 0.0:
        raise RuntimeError(f"level {n} produced a negative endpoint killing field")

    generator_one = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_ONE,
    )
    generator_two = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_TWO,
    )
    unit_tube = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=(DoiCatalyticPatch((0.5, 0.5), 1.0, 1.0, "tube"),),
        centre_weight=0.5,
    )
    patterned_binary = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=(
            DoiCatalyticPatch(NEAR_CENTRE, NEAR_RADIUS, NEAR_RATE, "near"),
            DoiCatalyticPatch(FAR_CENTRE, FAR_RADIUS, FAR_RATE, "far"),
        ),
        centre_weight=0.5,
    )
    binary_tube_count = int(unit_tube.reactive_state_counts[0])
    binary_near_count, binary_far_count = map(
        int,
        patterned_binary.reactive_state_counts,
    )

    initial = contact_safe_initial_distribution_2d(
        unit_tube,
        START_ONE,
        START_TWO,
    )
    initial_diagnostics = asdict(
        initial_distribution_diagnostics_2d(
            unit_tube,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )
    )

    sg_one = scharfetter_gummel_generator_2d(grid, **WALKER_ONE)
    sg_two = scharfetter_gummel_generator_2d(grid, **WALKER_TWO)
    identity = sparse.eye(grid.state_count, format="csr")
    free_generators = {
        "upwind": unit_tube.free_generator,
        "scharfetter_gummel": (
            sparse.kron(sg_one, identity, format="csr")
            + sparse.kron(identity, sg_two, format="csr")
        ),
    }
    mass_balance: dict[str, float] = {}
    families: dict[str, RefinedFamily] = {}
    Atheta = sparse.diags(-ktheta, format="csr")
    killing_diagonal = sparse.diags(k0, format="csr")
    for name in DISCRETIZATIONS:
        free = free_generators[name].tocsr()
        mass_balance[name] = _assert_mass_balance(
            free,
            f"level {n} {name} free product generator",
        )
        A0 = (free - killing_diagonal).tocsr()
        residual = (free - A0) - killing_diagonal
        if residual.nnz and float(np.max(np.abs(residual.data))) > 1e-13 * max(
            kappa_bar,
            1.0,
        ):
            raise RuntimeError(
                f"level {n} {name} killed generator is not free minus the "
                "nonnegative killing diagonal"
            )
        families[name] = RefinedFamily(
            n=n,
            discretization=name,
            A0=A0,
            Atheta=Atheta,
            k0=k0,
            ktheta=ktheta,
            initial=initial,
        )

    def _fraction_stats(name: str, values: np.ndarray) -> dict[str, float | int]:
        return {
            "field": name,
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "sum": float(np.sum(values)),
            "positive_states": int(np.count_nonzero(values > 0.0)),
            "control_volume_measure": float(np.dot(weights, values)),
        }

    continuum_budget = float(continuum["budget"])
    continuum_kappa_bar = float(continuum["kappa_bar"])
    shared_record: dict[str, object] = {
        "n": n,
        "spacing": grid.spacing_x,
        "single_walker_states": grid.state_count,
        "product_states": int(grid.state_count**2),
        "subsamples_per_axis": SUBSAMPLES_PER_AXIS,
        "subsamples_per_product_cell": int(SUBSAMPLES_PER_AXIS**4),
        "fraction_fields": {
            name: _fraction_stats(name, values)
            for name, values in fractions.items()
        },
        "binary_reference_counts": {
            "tube": binary_tube_count,
            "near": binary_near_count,
            "far": binary_far_count,
        },
        "cell_averaged_positive_counts": {
            name: int(np.count_nonzero(values > 0.0))
            for name, values in fractions.items()
        },
        "kappa_bar": float(kappa_bar),
        "matched_budget": pattern_budget,
        "budget_theta0": budget_theta0,
        "budget_theta1": budget_theta1,
        "budget_invariance_relative_error": float(budget_invariance),
        "budget_match_tolerance": BUDGET_MATCH_RTOL,
        "tube_control_volume_measure": tube_measure,
        "budget_minus_continuum": pattern_budget - continuum_budget,
        "budget_abs_gap_to_continuum": abs(pattern_budget - continuum_budget),
        "kappa_bar_relative_gap_to_continuum": kappa_bar / continuum_kappa_bar
        - 1.0,
        "initial_distribution": initial_diagnostics,
        "initial_cell_averaged_overlap": {
            "tube_fraction_mass": float(np.dot(initial, fractions["tube"])),
            "killing_rate_theta0": float(np.dot(initial, k0)),
            "killing_rate_theta1": float(np.dot(initial, k1)),
            "note": (
                "the initial law is contact-safe for the binary node mask; "
                "cell-averaged fields can overlap its support on coarse grids "
                "and the overlap must vanish under refinement"
            ),
        },
    }
    return RefinedLevel(
        n=n,
        grid=grid,
        weights=weights,
        fractions=fractions,
        kappa_pattern=kappa_pattern,
        kappa_bar=float(kappa_bar),
        budget=pattern_budget,
        families=families,
        shared_record=shared_record,
        mass_balance=mass_balance,
    )


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "cell-averaged successively refined continuation of the "
            "matched-budget 2D fold"
        )
    )
    parser.add_argument(
        "--levels",
        type=int,
        nargs="+",
        default=list(LEVELS),
        help="subset of the declared ladder levels to run",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run the executable validation gates and exit",
    )
    args = parser.parse_args()
    selftest_summary = _selftest()
    if args.selftest:
        print(json.dumps({"selftest": selftest_summary}, indent=2, sort_keys=True))
        return
    requested = tuple(sorted(set(int(value) for value in args.levels)))
    for level in requested:
        if level not in LEVELS:
            raise SystemExit(
                f"unsupported level {level}; declared ladder levels are {LEVELS}"
            )

    continuum = _continuum_budget_reference()
    level_records: list[dict[str, object]] = []
    csv_rows: list[dict[str, object]] = []
    accepted_theta: dict[str, list[tuple[int, float]]] = {
        name: [] for name in DISCRETIZATIONS
    }
    accepted_time: dict[str, list[tuple[int, float]]] = {
        name: [] for name in DISCRETIZATIONS
    }
    margin_sequences: dict[str, list[dict[str, float | int]]] = {
        name: [] for name in DISCRETIZATIONS
    }
    last_fold: dict[str, tuple[float, float]] = {}
    finest_fold_family: dict[str, tuple[int, RefinedFamily, dict] | None] = {
        name: None for name in DISCRETIZATIONS
    }

    for n in requested:
        setup_start = time.perf_counter()
        level = _build_level(n, continuum)
        setup_seconds = float(time.perf_counter() - setup_start)
        level.shared_record["setup_seconds"] = setup_seconds
        discretization_records: dict[str, object] = {}
        for name in DISCRETIZATIONS:
            solve_start = time.perf_counter()
            family = level.families[name]
            seeds = tuple(
                ([last_fold[name]] if name in last_fold else [])
                + list(DEFAULT_FOLD_SEEDS)
            )
            fold, attempts = _solve_fold(family, seeds)
            scan = None if fold is not None else _no_fold_scan(family)
            solve_seconds = float(time.perf_counter() - solve_start)
            record: dict[str, object] = {
                "discretization": name,
                "fold_found": fold is not None,
                "seed_list": [list(seed) for seed in seeds],
                "seed_attempt_count": len(attempts),
                "seed_attempts": attempts,
                "free_generator_mass_balance_relative_error": level.mass_balance[
                    name
                ],
                "solve_seconds": solve_seconds,
            }
            if fold is not None:
                record["fold"] = fold
                last_fold[name] = (float(fold["time"]), float(fold["theta"]))
                accepted_theta[name].append((n, float(fold["theta"])))
                accepted_time[name].append((n, float(fold["time"])))
                margin_sequences[name].append(
                    {
                        "n": n,
                        "spacing": level.grid.spacing_x,
                        "normalized_margin_f_ttt": float(
                            fold["normalized_margin_f_ttt"]
                        ),
                        "normalized_margin_f_ttheta": float(
                            fold["normalized_margin_f_ttheta"]
                        ),
                        "max_dimensionless_residual": float(
                            fold["max_dimensionless_residual"]
                        ),
                    }
                )
                finest_fold_family[name] = (n, family, fold)
            else:
                record["no_fold_scan"] = scan
            discretization_records[name] = record
            csv_rows.append(
                {
                    "n": n,
                    "spacing": level.grid.spacing_x,
                    "discretization": name,
                    "product_states": int(level.grid.state_count**2),
                    "fold_found": fold is not None,
                    "fold_time": "" if fold is None else fold["time"],
                    "fold_theta": "" if fold is None else fold["theta"],
                    "fold_theta_physical": ""
                    if fold is None
                    else fold["theta_physical"],
                    "fold_density": "" if fold is None else fold["density"],
                    "dimensionless_f_t_residual": ""
                    if fold is None
                    else fold["dimensionless_f_t_residual"],
                    "dimensionless_f_tt_residual": ""
                    if fold is None
                    else fold["dimensionless_f_tt_residual"],
                    "normalized_margin_f_ttt": ""
                    if fold is None
                    else fold["normalized_margin_f_ttt"],
                    "normalized_margin_f_ttheta": ""
                    if fold is None
                    else fold["normalized_margin_f_ttheta"],
                    "jacobian_determinant": ""
                    if fold is None
                    else fold["jacobian_determinant"],
                    "kappa_bar": level.kappa_bar,
                    "matched_budget": level.budget,
                    "budget_invariance_relative_error": level.shared_record[
                        "budget_invariance_relative_error"
                    ],
                    "budget_abs_gap_to_continuum": level.shared_record[
                        "budget_abs_gap_to_continuum"
                    ],
                    "frac_tube_sum": level.shared_record["fraction_fields"][
                        "tube"
                    ]["sum"],
                    "binary_tube_states": level.shared_record[
                        "binary_reference_counts"
                    ]["tube"],
                    "initial_tube_fraction_mass": level.shared_record[
                        "initial_cell_averaged_overlap"
                    ]["tube_fraction_mass"],
                    "free_mass_balance_relative_error": level.mass_balance[name],
                    "setup_seconds": setup_seconds,
                    "solve_seconds": solve_seconds,
                }
            )
        level_records.append(
            {
                **level.shared_record,
                "discretizations": discretization_records,
            }
        )

    richardson: dict[str, object] = {}
    for name in DISCRETIZATIONS:
        richardson[name] = {
            "theta_c": _richardson_fit(accepted_theta[name], "theta_c"),
            "time_c": _richardson_fit(accepted_time[name], "time_c"),
            "normalized_margin_sequence": margin_sequences[name],
        }
    theta_stars = {
        name: richardson[name]["theta_c"].get("star")
        for name in DISCRETIZATIONS
    }
    time_stars = {
        name: richardson[name]["time_c"].get("star") for name in DISCRETIZATIONS
    }
    if all(value is not None for value in theta_stars.values()):
        richardson["cross_discretization_theta_star_gap"] = abs(
            float(theta_stars["upwind"])
            - float(theta_stars["scharfetter_gummel"])
        )
    else:
        richardson["cross_discretization_theta_star_gap"] = None
    if all(value is not None for value in time_stars.values()):
        richardson["cross_discretization_time_star_gap"] = abs(
            float(time_stars["upwind"]) - float(time_stars["scharfetter_gummel"])
        )
    else:
        richardson["cross_discretization_time_star_gap"] = None

    scaling: dict[str, object] = {}
    for name in DISCRETIZATIONS:
        finest = finest_fold_family[name]
        if finest is None:
            scaling[name] = {"status": "no_accepted_fold_on_any_level"}
            continue
        finest_n, family, fold = finest
        spot_start = time.perf_counter()
        spot = _scaling_spot_check(family, fold)
        scaling[name] = {
            "status": "ok",
            "n": finest_n,
            "fold_time": float(fold["time"]),
            "fold_theta": float(fold["theta"]),
            "spot_check_seconds": float(time.perf_counter() - spot_start),
            **spot,
        }

    metrics = {
        "schema_version": 1,
        "claim_scope": (
            "cell-averaged square-cell refinement ladder for the matched-budget "
            "fold; per-level results are finite-lattice statements and the "
            "Richardson block is the continuum-limit diagnostic"
        ),
        "selftest": selftest_summary,
        "model": {
            "family_id": "M2D-F-refined",
            "domain": [1.0, 1.0],
            "boundary": "reflecting by omitted outward CTMC jumps",
            "reaction_model": (
                "finite-radius Doi volume sink with cell-averaged masks"
            ),
            "reaction_radius": REACTION_RADIUS,
            "start_one": list(START_ONE),
            "start_two": list(START_TWO),
            "walker_one": WALKER_ONE,
            "walker_two": WALKER_TWO,
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
            "continuation": (
                "kappa_theta=(1-theta) kappa_bar_h chi_tube_cell + theta "
                "[0.5 chi_near_cell + 15 chi_far_cell] with cell-averaged chi"
            ),
            "budget_matching": (
                "trapezoidal control-volume quadrature on the 4D product grid; "
                "kappa_bar_h recomputed per grid for exact theta invariance"
            ),
            "declared_ladder_levels": list(LEVELS),
            "levels_run": list(requested),
            "discretizations": list(DISCRETIZATIONS),
            "initial_distribution": (
                "contact-safe hierarchical selector against the binary node "
                "mask (byte-identical bilinear product when already safe)"
            ),
        },
        "continuum_reference": continuum,
        "levels": level_records,
        "richardson": richardson,
        "scaling_spot_check": scaling,
        "search_protocol": {
            "theta_interval": list(THETA_SEARCH_INTERVAL),
            "time_interval": list(TIME_SEARCH_INTERVAL),
            "default_seeds": [list(seed) for seed in DEFAULT_FOLD_SEEDS],
            "continuation_seeding": (
                "each level is first seeded from the accepted fold of the "
                "previous coarser level for the same discretization"
            ),
            "residual_gate": (
                "|f_t| t / f and |f_tt| t^2 / f both below "
                f"{FOLD_RESIDUAL_TOLERANCE:g}"
            ),
        },
    }

    metrics_json = DATA / "refined_fold_ladder.json"
    metrics_csv = DATA / "refined_fold_ladder.csv"
    _write_json(metrics_json, metrics)
    _write_csv(metrics_csv, csv_rows)
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
