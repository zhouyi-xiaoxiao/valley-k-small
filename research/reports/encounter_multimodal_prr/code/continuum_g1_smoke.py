#!/usr/bin/env python3
"""Fail-closed operator smoke for the exact physical-d=2 encounter quotient.

This implements the pre-fold G1 foundations only: cell-centred
Scharfetter--Gummel transport, periodic transverse relative diffusion,
mesh-independent smooth catalyst slabs, error-controlled circular contact
fractions, cell-integrated contact-safe initial data, and killed-semigroup mass
balance.  It does not search for or claim a continuum fold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from math import factorial
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy import sparse
from scipy.integrate import quad
from scipy.linalg import expm
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
DEFAULT_OUTPUT = DATA / "continuum_g1_smoke.json"
LOWER_WEIGHTS = np.asarray((0.70, 0.25, 0.05), dtype=float)
UPPER_WEIGHTS = np.asarray((0.05, 0.25, 0.70), dtype=float)
CONTACT_REFERENCE_ORDER = 128
BUMP_REFERENCE_ORDER = 192

BASE_BUMP_INTEGRAL = float(
    quad(
        lambda u: np.exp(-1.0 / (1.0 - u * u)),
        -1.0,
        1.0,
        epsabs=2.0e-15,
        epsrel=2.0e-14,
        limit=200,
    )[0]
)


@dataclass(frozen=True)
class PilotParameters:
    """Frozen physical parameters from the G1 design audit."""

    diffusion: float = 0.0045
    ou_stiffness: float = 0.1
    ou_mean: float = 0.95
    transverse_width: float = 1.0
    contact_radius: float = 0.16
    midpoint_start: float = 0.14
    midpoint_bump_half_width: float = 0.02
    relative_parallel_start: float = -0.35
    relative_perp_start: float = 0.0
    relative_bump_half_width: float = 0.02
    patch_centres: tuple[float, float, float] = (0.48, 0.67, 0.86)
    patch_half_widths: tuple[float, float, float] = (0.08, 0.08, 0.08)
    installed_budget: float = 0.6
    midpoint_bounds: tuple[float, float] = (-0.25, 1.85)
    relative_parallel_bounds: tuple[float, float] = (-1.8, 1.8)


@dataclass(frozen=True)
class QuotientGrid2D:
    """Cell-centred grid in midpoint and the two relative coordinates."""

    midpoint_cells: int
    relative_parallel_cells: int
    relative_perp_cells: int
    midpoint_bounds: tuple[float, float]
    relative_parallel_bounds: tuple[float, float]
    transverse_width: float

    def __post_init__(self) -> None:
        for name, value in (
            ("midpoint_cells", self.midpoint_cells),
            ("relative_parallel_cells", self.relative_parallel_cells),
            ("relative_perp_cells", self.relative_perp_cells),
        ):
            if int(value) != value or value < 3:
                raise ValueError(f"{name} must be an integer of at least three")
        if not self.midpoint_bounds[0] < self.midpoint_bounds[1]:
            raise ValueError("invalid midpoint bounds")
        if not self.relative_parallel_bounds[0] < self.relative_parallel_bounds[1]:
            raise ValueError("invalid relative-parallel bounds")
        if self.transverse_width <= 0.0:
            raise ValueError("transverse_width must be positive")

    @staticmethod
    def _edges(bounds: tuple[float, float], cells: int) -> np.ndarray:
        return np.linspace(bounds[0], bounds[1], cells + 1, dtype=float)

    @property
    def midpoint_edges(self) -> np.ndarray:
        return self._edges(self.midpoint_bounds, self.midpoint_cells)

    @property
    def relative_parallel_edges(self) -> np.ndarray:
        return self._edges(self.relative_parallel_bounds, self.relative_parallel_cells)

    @property
    def relative_perp_edges(self) -> np.ndarray:
        half = 0.5 * self.transverse_width
        return np.linspace(-half, half, self.relative_perp_cells + 1, dtype=float)

    @property
    def midpoint_spacing(self) -> float:
        return float(np.diff(self.midpoint_edges)[0])

    @property
    def relative_parallel_spacing(self) -> float:
        return float(np.diff(self.relative_parallel_edges)[0])

    @property
    def relative_perp_spacing(self) -> float:
        return float(np.diff(self.relative_perp_edges)[0])

    @property
    def state_count(self) -> int:
        return int(self.midpoint_cells * self.relative_parallel_cells * self.relative_perp_cells)


@dataclass(frozen=True)
class QuotientModel:
    parameters: PilotParameters
    grid: QuotientGrid2D
    theta: float
    free_generator: sparse.csr_matrix
    killed_generator: sparse.csr_matrix
    killing: np.ndarray
    killing_derivative: np.ndarray
    initial: np.ndarray
    contact_fraction_relative: np.ndarray
    patch_cell_averages: np.ndarray
    patch_integral_error_estimates: np.ndarray
    initial_integral_error_estimates: np.ndarray
    kappa: np.ndarray
    kappa_derivative: np.ndarray
    contact_area: float
    contact_area_error_estimate: float
    physical_budget: float
    operator_row_error: float
    killed_mass_balance_error: float
    initial_contact_mass: float


def _uniform_spacing(edges: np.ndarray, *, name: str) -> tuple[np.ndarray, float]:
    bounds = np.asarray(edges, dtype=float)
    if bounds.ndim != 1 or bounds.size < 2 or not np.all(np.isfinite(bounds)):
        raise ValueError(f"{name} must be a finite one-dimensional edge array")
    spacing = np.diff(bounds)
    if spacing[0] <= 0.0 or not np.all(spacing > 0.0):
        raise ValueError(f"{name} must be strictly increasing")
    if not np.allclose(spacing, spacing[0], rtol=1.0e-13, atol=1.0e-15):
        raise ValueError(f"{name} must be uniform")
    return bounds, float(spacing[0])


def _control_weights(theta: float) -> np.ndarray:
    return (1.0 - float(theta)) * LOWER_WEIGHTS + float(theta) * UPPER_WEIGHTS


def bernoulli_function(value: float | np.ndarray) -> np.ndarray:
    """Return x/expm1(x), including a stable small-x branch."""

    x = np.asarray(value, dtype=float)
    result = np.empty_like(x)
    small = np.abs(x) < 1.0e-5
    xs = x[small]
    result[small] = 1.0 - xs / 2.0 + xs**2 / 12.0 - xs**4 / 720.0 + xs**6 / 30240.0
    result[~small] = x[~small] / np.expm1(x[~small])
    return result


def sg_reflecting_generator(
    edges: np.ndarray,
    *,
    diffusion: float,
    drift: Callable[[float], float],
) -> sparse.csr_matrix:
    """Return a row CTMC generator for a no-flux one-dimensional SG mesh."""

    bounds = np.asarray(edges, dtype=float)
    if bounds.ndim != 1 or bounds.size < 4:
        raise ValueError("edges must define at least three cells")
    bounds, h = _uniform_spacing(bounds, name="SG edges")
    diffusivity = float(diffusion)
    if diffusivity <= 0.0:
        raise ValueError("diffusion must be positive")

    cells = bounds.size - 1
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    diagonal = np.zeros(cells, dtype=float)
    for left in range(cells - 1):
        face = float(bounds[left + 1])
        peclet = float(drift(face)) * h / diffusivity
        right_rate = diffusivity / h**2 * float(bernoulli_function(-peclet))
        left_rate = diffusivity / h**2 * float(bernoulli_function(peclet))
        if right_rate < 0.0 or left_rate < 0.0:
            raise RuntimeError("SG construction produced a negative transition rate")
        rows.extend((left, left + 1))
        columns.extend((left + 1, left))
        values.extend((right_rate, left_rate))
        diagonal[left] -= right_rate
        diagonal[left + 1] -= left_rate
    rows.extend(range(cells))
    columns.extend(range(cells))
    values.extend(diagonal.tolist())
    return sparse.csr_matrix((values, (rows, columns)), shape=(cells, cells))


def periodic_diffusion_generator(cells: int, spacing: float, diffusion: float) -> sparse.csr_matrix:
    """Return a row generator for periodic one-dimensional diffusion."""

    if cells < 3 or spacing <= 0.0 or diffusion <= 0.0:
        raise ValueError("invalid periodic diffusion parameters")
    rate = float(diffusion / spacing**2)
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    for source in range(cells):
        rows.extend((source, source, source))
        columns.extend(((source - 1) % cells, (source + 1) % cells, source))
        values.extend((rate, rate, -2.0 * rate))
    return sparse.csr_matrix((values, (rows, columns)), shape=(cells, cells))


def _normalized_bump_interval(lower: float, upper: float) -> tuple[float, float]:
    lo = max(-1.0, float(lower))
    hi = min(1.0, float(upper))
    if hi <= lo:
        return 0.0, 0.0
    integral, error = quad(
        lambda u: np.exp(-1.0 / (1.0 - u * u)),
        lo,
        hi,
        epsabs=2.0e-15,
        epsrel=2.0e-13,
        limit=100,
    )
    return float(integral / BASE_BUMP_INTEGRAL), float(error / BASE_BUMP_INTEGRAL)


def bump_cell_masses(
    edges: np.ndarray,
    *,
    centre: float,
    half_width: float,
    period: float | None = None,
) -> tuple[np.ndarray, float]:
    """Integrate a normalized compact bump over every cell."""

    bounds = np.asarray(edges, dtype=float)
    if bounds.ndim != 1 or bounds.size < 2 or not np.all(np.diff(bounds) > 0.0):
        raise ValueError("bump edges must be a strictly increasing one-dimensional array")
    width = float(half_width)
    if width <= 0.0:
        raise ValueError("half_width must be positive")
    if period is not None and 2.0 * width >= period:
        raise ValueError("periodic bump support must be shorter than one period")
    if period is not None and not np.isclose(
        bounds[-1] - bounds[0], period, rtol=1.0e-13, atol=1.0e-14
    ):
        raise ValueError("periodic bump edges must span exactly one period")
    if period is None:
        centres = (float(centre),)
    else:
        domain_midpoint = 0.5 * (bounds[0] + bounds[-1])
        nearest_shift = int(np.round((domain_midpoint - centre) / period))
        centres = tuple(float(centre + (nearest_shift + offset) * period) for offset in (-1, 0, 1))

    masses = np.zeros(bounds.size - 1, dtype=float)
    total_error = 0.0
    for cell, (left, right) in enumerate(zip(bounds[:-1], bounds[1:], strict=True)):
        for shifted_centre in centres:
            if right <= shifted_centre - width or left >= shifted_centre + width:
                continue
            value, error = _normalized_bump_interval(
                (left - shifted_centre) / width,
                (right - shifted_centre) / width,
            )
            masses[cell] += value
            total_error += error
    return masses, float(total_error)


@lru_cache(maxsize=None)
def _bump_reference_normalization(order: int) -> float:
    nodes, weights = _legendre_rule(order)
    values = np.exp(-1.0 / (1.0 - nodes * nodes))
    return float(np.dot(weights, values))


def bump_cell_masses_reference(
    edges: np.ndarray,
    *,
    centre: float,
    half_width: float,
    period: float | None = None,
    order: int = BUMP_REFERENCE_ORDER,
) -> np.ndarray:
    """Independent fixed-Gauss cell masses for the normalized compact bump."""

    bounds = np.asarray(edges, dtype=float)
    if bounds.ndim != 1 or bounds.size < 2 or not np.all(np.diff(bounds) > 0.0):
        raise ValueError("reference bump edges must be strictly increasing")
    width = float(half_width)
    if width <= 0.0 or order < 32:
        raise ValueError("invalid reference bump width or quadrature order")
    if period is not None:
        if 2.0 * width >= period:
            raise ValueError("reference periodic bump support must be shorter than one period")
        if not np.isclose(
            bounds[-1] - bounds[0],
            period,
            rtol=1.0e-13,
            atol=1.0e-14,
        ):
            raise ValueError("reference periodic bump edges must span one period")
        domain_midpoint = 0.5 * (bounds[0] + bounds[-1])
        base_shift = int(np.floor((domain_midpoint - centre) / period + 0.5))
        image_centres = tuple(
            float(centre + (base_shift + offset) * period) for offset in (-1, 0, 1)
        )
    else:
        image_centres = (float(centre),)

    normalization = _bump_reference_normalization(order)
    nodes, weights = _legendre_rule(order)
    masses = np.zeros(bounds.size - 1, dtype=float)
    for cell, (left, right) in enumerate(zip(bounds[:-1], bounds[1:], strict=True)):
        for image_centre in image_centres:
            lower_u = max(-1.0, (left - image_centre) / width)
            upper_u = min(1.0, (right - image_centre) / width)
            if upper_u <= lower_u:
                continue
            midpoint = 0.5 * (lower_u + upper_u)
            half_interval = 0.5 * (upper_u - lower_u)
            transformed = midpoint + half_interval * nodes
            values = np.zeros_like(transformed)
            interior = np.abs(transformed) < 1.0
            values[interior] = np.exp(-1.0 / (1.0 - transformed[interior] * transformed[interior]))
            masses[cell] += half_interval * float(np.dot(weights, values)) / normalization
    return masses


def bump_profile_reference_diagnostics(
    edges: np.ndarray,
    observed_masses: np.ndarray,
    *,
    centre: float,
    half_width: float,
    period: float | None = None,
    reference_order: int = BUMP_REFERENCE_ORDER,
) -> dict[str, Any]:
    """Compare one production bump profile with an independent local reference."""

    bounds = np.asarray(edges, dtype=float)
    observed = np.asarray(observed_masses, dtype=float)
    if observed.shape != (bounds.size - 1,) or not np.all(np.isfinite(observed)):
        raise ValueError("observed bump masses do not match the supplied edges")
    reference = bump_cell_masses_reference(
        bounds,
        centre=centre,
        half_width=half_width,
        period=period,
        order=reference_order,
    )
    difference = np.abs(observed - reference)
    cell_centres = 0.5 * (bounds[:-1] + bounds[1:])
    zeroth_moment = float(np.sum(observed))
    if period is None:
        first_moment = float(observed @ cell_centres)
        moment_error = float(first_moment - centre)
        moment_kind = "linear"
    else:
        resultant = np.sum(observed * np.exp(2.0j * np.pi * cell_centres / period))
        first_moment = float(np.angle(resultant) * period / (2.0 * np.pi))
        moment_error = _wrapped_difference(first_moment, centre, period)
        moment_kind = "circular"
    maximum_cell_width = float(np.max(np.diff(bounds)))
    return {
        "declared_centre": float(centre),
        "half_width": float(half_width),
        "period": None if period is None else float(period),
        "reference_order": int(reference_order),
        "zeroth_moment": zeroth_moment,
        "zeroth_moment_error": float(abs(zeroth_moment - 1.0)),
        "first_moment": first_moment,
        "first_moment_kind": moment_kind,
        "first_moment_error": moment_error,
        "first_moment_tolerance": float(0.5 * maximum_cell_width + 5.0e-13),
        "maximum_per_cell_mass_error": float(np.max(difference)),
        "relative_l1_mass_error": float(np.sum(difference) / np.sum(reference)),
    }


def circle_rectangle_area(
    x_bounds: tuple[float, float],
    y_bounds: tuple[float, float],
    radius: float,
) -> tuple[float, float]:
    """Area of a circle centred at zero intersected with one rectangle."""

    x0, x1 = map(float, x_bounds)
    y0, y1 = map(float, y_bounds)
    a = float(radius)
    if not (x0 < x1 and y0 < y1 and a > 0.0):
        raise ValueError("invalid circle/rectangle geometry")
    nearest_x = 0.0 if x0 <= 0.0 <= x1 else min(abs(x0), abs(x1))
    nearest_y = 0.0 if y0 <= 0.0 <= y1 else min(abs(y0), abs(y1))
    if nearest_x**2 + nearest_y**2 >= a**2:
        return 0.0, 0.0
    farthest = max(
        x0 * x0 + y0 * y0,
        x0 * x0 + y1 * y1,
        x1 * x1 + y0 * y0,
        x1 * x1 + y1 * y1,
    )
    rectangle_area = (x1 - x0) * (y1 - y0)
    if farthest <= a**2:
        return float(rectangle_area), 0.0

    lower = max(x0, -a)
    upper = min(x1, a)
    if upper <= lower:
        return 0.0, 0.0
    split_points = [lower, upper]
    for y in (y0, y1):
        if abs(y) < a:
            critical = float(np.sqrt(max(a * a - y * y, 0.0)))
            for candidate in (-critical, critical):
                if lower < candidate < upper:
                    split_points.append(candidate)
    split_points = sorted(set(split_points))

    def vertical_overlap(x: float) -> float:
        cap = float(np.sqrt(max(a * a - x * x, 0.0)))
        return max(0.0, min(y1, cap) - max(y0, -cap))

    area = 0.0
    error = 0.0
    for left, right in zip(split_points[:-1], split_points[1:], strict=True):
        value, local_error = quad(
            vertical_overlap,
            left,
            right,
            epsabs=5.0e-15,
            epsrel=2.0e-13,
            limit=100,
        )
        area += value
        error += local_error
    return float(area), float(error)


def contact_cell_fractions(
    parallel_edges: np.ndarray,
    perp_edges: np.ndarray,
    *,
    radius: float,
) -> tuple[np.ndarray, float, float]:
    """Return contact fractions, integrated area, and a QUADPACK error estimate."""

    parallel_edges, hx = _uniform_spacing(parallel_edges, name="parallel contact edges")
    perp_edges, hy = _uniform_spacing(perp_edges, name="perpendicular contact edges")
    fractions = np.zeros((parallel_edges.size - 1, perp_edges.size - 1), dtype=float)
    total_area = 0.0
    total_error = 0.0
    for ix, x_bounds in enumerate(zip(parallel_edges[:-1], parallel_edges[1:], strict=True)):
        for iy, y_bounds in enumerate(zip(perp_edges[:-1], perp_edges[1:], strict=True)):
            area, error = circle_rectangle_area(x_bounds, y_bounds, radius)
            fractions[ix, iy] = area / (hx * hy)
            total_area += area
            total_error += error
    if (
        not np.all(np.isfinite(fractions))
        or not np.isfinite(total_area)
        or not np.isfinite(total_error)
        or np.any(fractions < -1.0e-14)
        or np.any(fractions > 1.0 + 1.0e-12)
    ):
        raise RuntimeError("contact integration produced an invalid cell fraction")
    return np.clip(fractions, 0.0, 1.0), float(total_area), float(total_error)


@lru_cache(maxsize=None)
def _legendre_rule(order: int) -> tuple[np.ndarray, np.ndarray]:
    if order < 16:
        raise ValueError("reference Gauss order must be at least 16")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return np.asarray(nodes, dtype=float), np.asarray(weights, dtype=float)


def _fixed_gauss_integral(
    function: Callable[[np.ndarray], np.ndarray],
    lower: float,
    upper: float,
    *,
    order: int,
) -> float:
    if upper <= lower:
        return 0.0
    nodes, weights = _legendre_rule(order)
    midpoint = 0.5 * (lower + upper)
    half_width = 0.5 * (upper - lower)
    return float(half_width * np.dot(weights, function(midpoint + half_width * nodes)))


def circle_rectangle_area_reference(
    x_bounds: tuple[float, float],
    y_bounds: tuple[float, float],
    radius: float,
    *,
    order: int = CONTACT_REFERENCE_ORDER,
) -> float:
    """Independent fixed-Gauss reference integrating horizontal circle chords."""

    x0, x1 = map(float, x_bounds)
    y0, y1 = map(float, y_bounds)
    a = float(radius)
    if not (x0 < x1 and y0 < y1 and a > 0.0):
        raise ValueError("invalid circle/rectangle reference geometry")
    nearest_x = 0.0 if x0 <= 0.0 <= x1 else min(abs(x0), abs(x1))
    nearest_y = 0.0 if y0 <= 0.0 <= y1 else min(abs(y0), abs(y1))
    if nearest_x**2 + nearest_y**2 >= a**2:
        return 0.0
    farthest = max(
        x0 * x0 + y0 * y0,
        x0 * x0 + y1 * y1,
        x1 * x1 + y0 * y0,
        x1 * x1 + y1 * y1,
    )
    rectangle_area = (x1 - x0) * (y1 - y0)
    if farthest <= a**2:
        return float(rectangle_area)

    lower = max(y0, -a)
    upper = min(y1, a)
    split_points = [lower, upper]
    for x in (x0, x1):
        if abs(x) < a:
            critical = float(np.sqrt(max(a * a - x * x, 0.0)))
            for candidate in (-critical, critical):
                if lower < candidate < upper:
                    split_points.append(candidate)
    split_points = sorted(set(split_points))

    def transformed_overlap(angle: np.ndarray) -> np.ndarray:
        cap = a * np.cos(angle)
        overlap = np.maximum(0.0, np.minimum(x1, cap) - np.maximum(x0, -cap))
        return overlap * a * np.cos(angle)

    return float(
        sum(
            _fixed_gauss_integral(
                transformed_overlap,
                float(np.arcsin(np.clip(left / a, -1.0, 1.0))),
                float(np.arcsin(np.clip(right / a, -1.0, 1.0))),
                order=order,
            )
            for left, right in zip(split_points[:-1], split_points[1:], strict=True)
        )
    )


def contact_reference_diagnostics(
    parallel_edges: np.ndarray,
    perp_edges: np.ndarray,
    fractions: np.ndarray,
    *,
    radius: float,
    reference_order: int = CONTACT_REFERENCE_ORDER,
) -> dict[str, Any]:
    """Check local placement against an independent high-order reference."""

    parallel_edges, hx = _uniform_spacing(parallel_edges, name="parallel reference edges")
    perp_edges, hy = _uniform_spacing(perp_edges, name="perpendicular reference edges")
    observed = np.asarray(fractions, dtype=float)
    expected_shape = (parallel_edges.size - 1, perp_edges.size - 1)
    if observed.shape != expected_shape:
        raise ValueError("contact fraction shape does not match the relative grid")
    if not np.all(np.isfinite(observed)):
        raise ValueError("contact fractions must be finite")
    reference = np.zeros_like(observed)
    for ix, x_bounds in enumerate(zip(parallel_edges[:-1], parallel_edges[1:], strict=True)):
        for iy, y_bounds in enumerate(zip(perp_edges[:-1], perp_edges[1:], strict=True)):
            area = circle_rectangle_area_reference(
                x_bounds,
                y_bounds,
                radius,
                order=reference_order,
            )
            reference[ix, iy] = area / (hx * hy)

    cell_area = hx * hy
    observed_area = float(np.sum(observed) * cell_area)
    if observed_area <= 0.0:
        raise ValueError("contact fractions must have positive integrated area")
    x_centres = 0.5 * (parallel_edges[:-1] + parallel_edges[1:])
    y_centres = 0.5 * (perp_edges[:-1] + perp_edges[1:])
    centroid_x = float(np.sum(observed * x_centres[:, None]) * cell_area / observed_area)
    centroid_y = float(np.sum(observed * y_centres[None, :]) * cell_area / observed_area)
    difference = np.abs(observed - reference)
    return {
        "reference_order": int(reference_order),
        "maximum_per_cell_fraction_error": float(np.max(difference)),
        "relative_l1_area_error": float(np.sum(difference) * cell_area / observed_area),
        "centroid": [centroid_x, centroid_y],
        "maximum_parallel_reflection_error": float(np.max(np.abs(observed - observed[::-1, :]))),
        "maximum_perpendicular_reflection_error": float(
            np.max(np.abs(observed - observed[:, ::-1]))
        ),
    }


def _offdiagonal_minimum(matrix: sparse.csr_matrix) -> float:
    offdiagonal = matrix - sparse.diags(matrix.diagonal(), format="csr")
    return float(np.min(offdiagonal.data)) if offdiagonal.nnz else 0.0


def build_model(
    grid: QuotientGrid2D,
    *,
    theta: float,
    parameters: PilotParameters | None = None,
) -> QuotientModel:
    """Assemble one physically budgeted killed quotient operator."""

    pars = PilotParameters() if parameters is None else parameters
    control = float(theta)
    if not 0.0 <= control <= 1.0:
        raise ValueError("theta must lie in [0, 1]")
    if pars.contact_radius >= 0.5 * pars.transverse_width:
        raise ValueError("contact ball reaches the torus cut locus")
    gamma = pars.ou_stiffness
    diffusion = pars.diffusion
    midpoint_generator = sg_reflecting_generator(
        grid.midpoint_edges,
        diffusion=diffusion / 2.0,
        drift=lambda z: -gamma * (z - pars.ou_mean),
    )
    relative_parallel_generator = sg_reflecting_generator(
        grid.relative_parallel_edges,
        diffusion=2.0 * diffusion,
        drift=lambda r: -gamma * r,
    )
    relative_perp_generator = periodic_diffusion_generator(
        grid.relative_perp_cells,
        grid.relative_perp_spacing,
        2.0 * diffusion,
    )
    relative_generator = sparse.kron(
        relative_parallel_generator,
        sparse.eye(grid.relative_perp_cells, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(grid.relative_parallel_cells, format="csr"),
        relative_perp_generator,
        format="csr",
    )
    free = sparse.kron(
        midpoint_generator,
        sparse.eye(grid.relative_parallel_cells * grid.relative_perp_cells, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(grid.midpoint_cells, format="csr"),
        relative_generator,
        format="csr",
    )

    patch_averages: list[np.ndarray] = []
    patch_error_estimates: list[float] = []
    for centre, width in zip(pars.patch_centres, pars.patch_half_widths, strict=True):
        masses, error_estimate = bump_cell_masses(
            grid.midpoint_edges,
            centre=centre,
            half_width=width,
        )
        patch_averages.append(masses / grid.midpoint_spacing)
        patch_error_estimates.append(error_estimate)
    patch_matrix = np.asarray(patch_averages, dtype=float)
    weights = _control_weights(control)
    weight_derivative = UPPER_WEIGHTS - LOWER_WEIGHTS
    budget_density = pars.installed_budget / pars.transverse_width
    kappa = budget_density * (weights @ patch_matrix)
    kappa_derivative = budget_density * (weight_derivative @ patch_matrix)
    physical_budget = float(pars.transverse_width * np.sum(kappa) * grid.midpoint_spacing)

    contact, contact_area, contact_error = contact_cell_fractions(
        grid.relative_parallel_edges,
        grid.relative_perp_edges,
        radius=pars.contact_radius,
    )
    contact_relative = contact.reshape(-1)
    killing = np.kron(kappa, contact_relative)
    killing_derivative = np.kron(kappa_derivative, contact_relative)
    killed = free - sparse.diags(killing, format="csr")

    midpoint_initial, midpoint_initial_error = bump_cell_masses(
        grid.midpoint_edges,
        centre=pars.midpoint_start,
        half_width=pars.midpoint_bump_half_width,
    )
    relative_parallel_initial, relative_parallel_initial_error = bump_cell_masses(
        grid.relative_parallel_edges,
        centre=pars.relative_parallel_start,
        half_width=pars.relative_bump_half_width,
    )
    relative_perp_initial, relative_perp_initial_error = bump_cell_masses(
        grid.relative_perp_edges,
        centre=pars.relative_perp_start,
        half_width=pars.relative_bump_half_width,
        period=pars.transverse_width,
    )
    initial = np.kron(
        midpoint_initial,
        np.kron(relative_parallel_initial, relative_perp_initial),
    )
    initial_contact_mass = float(initial @ np.tile(contact_relative, grid.midpoint_cells))
    free_row_error = float(np.max(np.abs(np.asarray(free.sum(axis=1)).reshape(-1))))
    killed_mass_balance_error = float(
        np.max(np.abs(np.asarray(killed.sum(axis=1)).reshape(-1) + killing))
    )
    if _offdiagonal_minimum(free) < -1.0e-14:
        raise RuntimeError("free generator has a negative off-diagonal entry")
    return QuotientModel(
        parameters=pars,
        grid=grid,
        theta=control,
        free_generator=free,
        killed_generator=killed,
        killing=killing,
        killing_derivative=killing_derivative,
        initial=initial,
        contact_fraction_relative=contact_relative,
        patch_cell_averages=patch_matrix,
        patch_integral_error_estimates=np.asarray(patch_error_estimates, dtype=float),
        initial_integral_error_estimates=np.asarray(
            (
                midpoint_initial_error,
                relative_parallel_initial_error,
                relative_perp_initial_error,
            ),
            dtype=float,
        ),
        kappa=kappa,
        kappa_derivative=kappa_derivative,
        contact_area=contact_area,
        contact_area_error_estimate=contact_error,
        physical_budget=physical_budget,
        operator_row_error=free_row_error,
        killed_mass_balance_error=killed_mass_balance_error,
        initial_contact_mass=initial_contact_mass,
    )


def budget_diagnostics(model: QuotientModel) -> dict[str, Any]:
    """Return patchwise and endpoint checks for the installed material budget."""

    pars = model.parameters
    spacing = model.grid.midpoint_spacing
    patch_integrals = np.sum(model.patch_cell_averages, axis=1) * spacing
    endpoint_budgets = []
    endpoint_kappa_minima = []
    endpoint_killing_minima = []
    endpoint_weights = [LOWER_WEIGHTS.copy(), UPPER_WEIGHTS.copy()]
    for theta in (0.0, 1.0):
        endpoint_kappa = (
            pars.installed_budget
            / pars.transverse_width
            * (_control_weights(theta) @ model.patch_cell_averages)
        )
        endpoint_budgets.append(float(pars.transverse_width * np.sum(endpoint_kappa) * spacing))
        endpoint_kappa_minima.append(float(np.min(endpoint_kappa)))
        endpoint_killing_minima.append(
            float(np.min(np.kron(endpoint_kappa, model.contact_fraction_relative)))
        )
    physical_budget_derivative = float(
        pars.transverse_width * np.sum(model.kappa_derivative) * spacing
    )
    endpoint_relative_errors = [
        abs(value - pars.installed_budget) / pars.installed_budget for value in endpoint_budgets
    ]
    endpoint_weight_sums = [float(np.sum(weights)) for weights in endpoint_weights]
    endpoint_weight_sum_errors = [abs(value - 1.0) for value in endpoint_weight_sums]
    endpoint_component_minima = [float(np.min(weights)) for weights in endpoint_weights]
    affine_line_certified = bool(
        max(endpoint_weight_sum_errors) <= 1.0e-14 and min(endpoint_component_minima) >= -1.0e-14
    )
    return {
        "installed_budget": float(pars.installed_budget),
        "per_transverse_integral": float(np.sum(model.kappa) * spacing),
        "expected_per_transverse_integral": float(pars.installed_budget / pars.transverse_width),
        "physical_budget": float(model.physical_budget),
        "patch_integrals": [float(value) for value in patch_integrals],
        "patch_integral_absolute_errors": [float(abs(value - 1.0)) for value in patch_integrals],
        "patch_integral_error_estimates": [
            float(value) for value in model.patch_integral_error_estimates
        ],
        "endpoint_physical_budgets": endpoint_budgets,
        "endpoint_budget_relative_errors": endpoint_relative_errors,
        "endpoint_weights": [
            [float(component) for component in weights] for weights in endpoint_weights
        ],
        "endpoint_weight_sums": endpoint_weight_sums,
        "endpoint_weight_sum_errors": endpoint_weight_sum_errors,
        "endpoint_component_minima": endpoint_component_minima,
        "endpoint_kappa_minima": endpoint_kappa_minima,
        "endpoint_killing_minima": endpoint_killing_minima,
        "affine_line_weight_nonnegativity_certified": affine_line_certified,
        "affine_line_certificate": (
            "weights are affine in theta; endpoint unit sums and componentwise "
            "nonnegativity imply the same for every theta in [0,1]"
        ),
        "current_weights": [float(value) for value in _control_weights(model.theta)],
        "current_kappa_minimum": float(np.min(model.kappa)),
        "current_killing_minimum": float(np.min(model.killing)),
        "physical_budget_derivative": physical_budget_derivative,
        "scaled_budget_derivative_error": float(
            abs(physical_budget_derivative) / pars.installed_budget
        ),
    }


def _wrapped_difference(value: float, target: float, period: float) -> float:
    return float((value - target + 0.5 * period) % period - 0.5 * period)


def initial_reconstruction_diagnostics(model: QuotientModel) -> dict[str, Any]:
    """Report moments of the piecewise-constant finite-volume initial law."""

    grid = model.grid
    pars = model.parameters
    shaped = model.initial.reshape(
        grid.midpoint_cells,
        grid.relative_parallel_cells,
        grid.relative_perp_cells,
    )
    midpoint_mass = np.sum(shaped, axis=(1, 2))
    parallel_mass = np.sum(shaped, axis=(0, 2))
    perpendicular_mass = np.sum(shaped, axis=(0, 1))
    midpoint_centres = 0.5 * (grid.midpoint_edges[:-1] + grid.midpoint_edges[1:])
    parallel_centres = 0.5 * (grid.relative_parallel_edges[:-1] + grid.relative_parallel_edges[1:])
    perpendicular_centres = 0.5 * (grid.relative_perp_edges[:-1] + grid.relative_perp_edges[1:])
    midpoint_mean = float(midpoint_mass @ midpoint_centres)
    parallel_mean = float(parallel_mass @ parallel_centres)
    circular_resultant = np.sum(
        perpendicular_mass * np.exp(2.0j * np.pi * perpendicular_centres / pars.transverse_width)
    )
    circular_mean = float(np.angle(circular_resultant) * pars.transverse_width / (2.0 * np.pi))
    errors = {
        "midpoint": float(midpoint_mean - pars.midpoint_start),
        "relative_parallel": float(parallel_mean - pars.relative_parallel_start),
        "relative_perpendicular_circular": _wrapped_difference(
            circular_mean,
            pars.relative_perp_start,
            pars.transverse_width,
        ),
    }
    tolerances = {
        "midpoint": float(0.5 * grid.midpoint_spacing + 5.0e-13),
        "relative_parallel": float(0.5 * grid.relative_parallel_spacing + 5.0e-13),
        "relative_perpendicular_circular": float(0.5 * grid.relative_perp_spacing + 5.0e-13),
    }
    return {
        "tolerance_rule": "absolute moment error <= one half of the corresponding cell width",
        "reconstructed_means": {
            "midpoint": midpoint_mean,
            "relative_parallel": parallel_mean,
            "relative_perpendicular_circular": circular_mean,
        },
        "declared_means": {
            "midpoint": float(pars.midpoint_start),
            "relative_parallel": float(pars.relative_parallel_start),
            "relative_perpendicular_circular": float(pars.relative_perp_start),
        },
        "errors": errors,
        "tolerances": tolerances,
        "circular_resultant_magnitude": float(abs(circular_resultant)),
    }


def all_bump_profile_diagnostics(model: QuotientModel) -> dict[str, Any]:
    """Independently check all catalyst and initial bump cell profiles."""

    pars = model.parameters
    grid = model.grid
    catalyst_profiles = []
    for label, centre, width, averages in zip(
        ("near", "middle", "far"),
        pars.patch_centres,
        pars.patch_half_widths,
        model.patch_cell_averages,
        strict=True,
    ):
        diagnostics = bump_profile_reference_diagnostics(
            grid.midpoint_edges,
            averages * grid.midpoint_spacing,
            centre=centre,
            half_width=width,
        )
        diagnostics["label"] = label
        catalyst_profiles.append(diagnostics)

    shaped = model.initial.reshape(
        grid.midpoint_cells,
        grid.relative_parallel_cells,
        grid.relative_perp_cells,
    )
    initial_specs = (
        (
            "midpoint",
            grid.midpoint_edges,
            np.sum(shaped, axis=(1, 2)),
            pars.midpoint_start,
            pars.midpoint_bump_half_width,
            None,
        ),
        (
            "relative_parallel",
            grid.relative_parallel_edges,
            np.sum(shaped, axis=(0, 2)),
            pars.relative_parallel_start,
            pars.relative_bump_half_width,
            None,
        ),
        (
            "relative_perpendicular_wrapped",
            grid.relative_perp_edges,
            np.sum(shaped, axis=(0, 1)),
            pars.relative_perp_start,
            pars.relative_bump_half_width,
            pars.transverse_width,
        ),
    )
    initial_profiles = []
    for label, edges, masses, centre, width, period in initial_specs:
        diagnostics = bump_profile_reference_diagnostics(
            edges,
            masses,
            centre=centre,
            half_width=width,
            period=period,
        )
        diagnostics["label"] = label
        initial_profiles.append(diagnostics)
    return {
        "catalyst_profiles": catalyst_profiles,
        "initial_marginals": initial_profiles,
        "production_patch_error_estimates": [
            float(value) for value in model.patch_integral_error_estimates
        ],
        "production_initial_error_estimates": [
            float(value) for value in model.initial_integral_error_estimates
        ],
    }


def _relative_vector_error(observed: np.ndarray, reference: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(reference, ord=np.inf)), 1.0e-15)
    return float(np.linalg.norm(observed - reference, ord=np.inf) / denominator)


def _finite_difference_weights(nodes: np.ndarray, derivative_order: int) -> np.ndarray:
    vandermonde = np.vstack([nodes**power for power in range(nodes.size)])
    target = np.zeros(nodes.size, dtype=float)
    target[derivative_order] = float(factorial(derivative_order))
    return np.linalg.solve(vandermonde, target)


@lru_cache(maxsize=1)
def small_reference_diagnostics() -> dict[str, Any]:
    """Dense and finite-difference checks on a frozen asymmetric operator."""

    nz, nr, np_ = 4, 5, 6
    z_edges = np.linspace(-0.7, 0.9, nz + 1)
    r_edges = np.linspace(-1.1, 0.8, nr + 1)
    z_generator = sg_reflecting_generator(
        z_edges,
        diffusion=0.13,
        drift=lambda value: -0.27 * (value - 0.18),
    )
    r_generator = sg_reflecting_generator(
        r_edges,
        diffusion=0.21,
        drift=lambda value: -0.19 * (value + 0.07),
    )
    perp_generator = periodic_diffusion_generator(np_, spacing=0.17, diffusion=0.09)
    relative = sparse.kron(
        r_generator,
        sparse.eye(np_, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(nr, format="csr"),
        perp_generator,
        format="csr",
    )
    free = sparse.kron(
        z_generator,
        sparse.eye(nr * np_, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(nz, format="csr"),
        relative,
        format="csr",
    )
    iz, ir, ip = np.indices((nz, nr, np_))
    killing = (0.02 + 0.006 * iz + 0.004 * ir + 0.003 * ip + 0.001 * iz * ip).reshape(-1)
    killed = free - sparse.diags(killing, format="csr")
    initial_z = np.asarray((1.0, 2.0, 4.0, 3.0))
    initial_r = np.asarray((2.0, 1.0, 4.0, 3.0, 5.0))
    initial_p = np.asarray((1.0, 3.0, 2.0, 5.0, 4.0, 6.0))
    initial_z /= np.sum(initial_z)
    initial_r /= np.sum(initial_r)
    initial_p /= np.sum(initial_p)
    initial = np.kron(initial_z, np.kron(initial_r, initial_p))

    time = 0.37
    dense_transition = expm(killed.T.toarray() * time)
    dense_state = np.asarray(dense_transition @ initial, dtype=float)
    sparse_state = np.asarray(expm_multiply(killed.T * time, initial), dtype=float)
    half_state = np.asarray(expm_multiply(killed.T * (0.5 * time), initial), dtype=float)
    two_half_state = np.asarray(
        expm_multiply(killed.T * (0.5 * time), half_state),
        dtype=float,
    )

    first_vector = killed @ killing
    second_vector = killed @ first_vector
    third_vector = killed @ second_vector
    analytic_jets = np.asarray(
        (
            dense_state @ first_vector,
            dense_state @ second_vector,
            dense_state @ third_vector,
        ),
        dtype=float,
    )
    step = 0.01
    step_forward = expm(killed.T.toarray() * step)
    step_backward = expm(-killed.T.toarray() * step)
    sampled_states: dict[int, np.ndarray] = {0: dense_state}
    for offset in range(1, 5):
        sampled_states[offset] = step_forward @ sampled_states[offset - 1]
        sampled_states[-offset] = step_backward @ sampled_states[-offset + 1]
    nodes = np.arange(-4, 5, dtype=float)
    sampled_density = np.asarray(
        [sampled_states[int(offset)] @ killing for offset in nodes],
        dtype=float,
    )
    finite_difference_jets = np.asarray(
        [
            np.dot(_finite_difference_weights(nodes, order), sampled_density) / step**order
            for order in (1, 2, 3)
        ],
        dtype=float,
    )
    jet_relative_errors = np.abs(finite_difference_jets - analytic_jets) / np.maximum(
        np.abs(analytic_jets),
        1.0e-12,
    )

    source = (1, 2, 3)
    source_flat = int(np.ravel_multi_index(source, (nz, nr, np_)))
    row = free.getrow(source_flat)
    observed_neighbours = {
        tuple(int(value) for value in np.unravel_index(target, (nz, nr, np_)))
        for target, rate in zip(row.indices, row.data, strict=True)
        if target != source_flat and rate > 0.0
    }
    expected_neighbours = {
        (0, 2, 3),
        (2, 2, 3),
        (1, 1, 3),
        (1, 3, 3),
        (1, 2, 2),
        (1, 2, 4),
    }
    return {
        "shape": [nz, nr, np_],
        "time": time,
        "dense_sparse_state_relative_error": _relative_vector_error(
            sparse_state,
            dense_state,
        ),
        "one_step_two_half_step_relative_error": _relative_vector_error(
            two_half_state,
            sparse_state,
        ),
        "analytic_jets": [float(value) for value in analytic_jets],
        "finite_difference_jets": [float(value) for value in finite_difference_jets],
        "jet_relative_errors": [float(value) for value in jet_relative_errors],
        "finite_difference_step": step,
        "tensor_order_sentinel": observed_neighbours == expected_neighbours,
        "observed_neighbours": [list(value) for value in sorted(observed_neighbours)],
    }


def _bernoulli_reference_scalar(value: float) -> float:
    x = float(value)
    if abs(x) < 1.0e-6:
        return float(1.0 - x / 2.0 + x * x / 12.0 - x**4 / 720.0)
    return float(x / np.expm1(x))


def transport_rate_diagnostics(model: QuotientModel) -> dict[str, Any]:
    """Compare selected main-model rates with independent analytic SG rates."""

    grid = model.grid
    pars = model.parameters
    shape = (
        grid.midpoint_cells,
        grid.relative_parallel_cells,
        grid.relative_perp_cells,
    )
    samples: list[dict[str, Any]] = []

    def record(
        label: str, source: tuple[int, int, int], target: tuple[int, int, int], expected: float
    ) -> None:
        source_flat = int(np.ravel_multi_index(source, shape))
        target_flat = int(np.ravel_multi_index(target, shape))
        observed = float(model.free_generator[source_flat, target_flat])
        absolute_error = abs(observed - expected)
        samples.append(
            {
                "label": label,
                "source": list(source),
                "target": list(target),
                "observed": observed,
                "expected": float(expected),
                "absolute_error": float(absolute_error),
                "relative_error": float(absolute_error / max(abs(expected), 1.0e-15)),
            }
        )

    iz = min(max(grid.midpoint_cells // 2, 1), grid.midpoint_cells - 2)
    ir = min(max(grid.relative_parallel_cells // 2, 1), grid.relative_parallel_cells - 2)
    ip = grid.relative_perp_cells // 2
    dz = pars.diffusion / 2.0
    hz = grid.midpoint_spacing
    for label, source_z, target_z, face, direction in (
        ("z_interior_right", iz, iz + 1, grid.midpoint_edges[iz + 1], 1),
        ("z_interior_left", iz, iz - 1, grid.midpoint_edges[iz], -1),
        ("z_left_boundary_inward", 0, 1, grid.midpoint_edges[1], 1),
        (
            "z_right_boundary_inward",
            grid.midpoint_cells - 1,
            grid.midpoint_cells - 2,
            grid.midpoint_edges[-2],
            -1,
        ),
    ):
        peclet = -pars.ou_stiffness * (float(face) - pars.ou_mean) * hz / dz
        bernoulli_argument = -peclet if direction > 0 else peclet
        expected = dz / hz**2 * _bernoulli_reference_scalar(bernoulli_argument)
        record(label, (source_z, ir, ip), (target_z, ir, ip), expected)

    dr = 2.0 * pars.diffusion
    hr = grid.relative_parallel_spacing
    fixed_z = grid.midpoint_cells // 2
    for label, source_r, target_r, face, direction in (
        ("r_parallel_interior_right", ir, ir + 1, grid.relative_parallel_edges[ir + 1], 1),
        ("r_parallel_interior_left", ir, ir - 1, grid.relative_parallel_edges[ir], -1),
        ("r_parallel_left_boundary_inward", 0, 1, grid.relative_parallel_edges[1], 1),
        (
            "r_parallel_right_boundary_inward",
            grid.relative_parallel_cells - 1,
            grid.relative_parallel_cells - 2,
            grid.relative_parallel_edges[-2],
            -1,
        ),
    ):
        peclet = -pars.ou_stiffness * float(face) * hr / dr
        bernoulli_argument = -peclet if direction > 0 else peclet
        expected = dr / hr**2 * _bernoulli_reference_scalar(bernoulli_argument)
        record(label, (fixed_z, source_r, ip), (fixed_z, target_r, ip), expected)

    periodic_rate = 2.0 * pars.diffusion / grid.relative_perp_spacing**2
    record(
        "r_perp_interior_right",
        (fixed_z, ir, ip),
        (fixed_z, ir, (ip + 1) % grid.relative_perp_cells),
        periodic_rate,
    )
    record(
        "r_perp_interior_left",
        (fixed_z, ir, ip),
        (fixed_z, ir, (ip - 1) % grid.relative_perp_cells),
        periodic_rate,
    )
    record(
        "r_perp_periodic_wrap_left",
        (fixed_z, ir, 0),
        (fixed_z, ir, grid.relative_perp_cells - 1),
        periodic_rate,
    )
    record(
        "r_perp_periodic_wrap_right",
        (fixed_z, ir, grid.relative_perp_cells - 1),
        (fixed_z, ir, 0),
        periodic_rate,
    )
    return {
        "sample_count": len(samples),
        "samples": samples,
        "maximum_absolute_rate_error": max(sample["absolute_error"] for sample in samples),
        "maximum_relative_rate_error": max(sample["relative_error"] for sample in samples),
    }


def foundation_diagnostics(model: QuotientModel) -> dict[str, Any]:
    """Reusable G1a operator, geometry, budget, and reference diagnostics."""

    pars = model.parameters
    grid = model.grid
    expected_contact_area = float(np.pi * pars.contact_radius**2)
    contact_area_relative_error = float(
        abs(model.contact_area - expected_contact_area) / expected_contact_area
    )
    contact_reference = contact_reference_diagnostics(
        grid.relative_parallel_edges,
        grid.relative_perp_edges,
        model.contact_fraction_relative.reshape(
            grid.relative_parallel_cells,
            grid.relative_perp_cells,
        ),
        radius=pars.contact_radius,
    )
    expected_killing = (
        model.kappa[:, None, None]
        * model.contact_fraction_relative.reshape(
            1,
            grid.relative_parallel_cells,
            grid.relative_perp_cells,
        )
    ).reshape(-1)
    return {
        "expected_contact_area": expected_contact_area,
        "integrated_contact_area": float(model.contact_area),
        "contact_area_relative_error": contact_area_relative_error,
        "contact_area_error_estimate": float(model.contact_area_error_estimate),
        "contact_reference": contact_reference,
        "expected_physical_budget": float(pars.installed_budget),
        "physical_budget": float(model.physical_budget),
        "budget_relative_error": float(
            abs(model.physical_budget - pars.installed_budget) / pars.installed_budget
        ),
        "budget_diagnostics": budget_diagnostics(model),
        "initial_mass_error": float(abs(np.sum(model.initial) - 1.0)),
        "initial_contact_mass": float(model.initial_contact_mass),
        "initial_reconstruction": initial_reconstruction_diagnostics(model),
        "bump_profile_reference": all_bump_profile_diagnostics(model),
        "tensor_killing_max_abs_error": float(np.max(np.abs(model.killing - expected_killing))),
        "transport_rate_reference": transport_rate_diagnostics(model),
        "small_operator_reference": small_reference_diagnostics(),
    }


def foundation_gates(
    model: QuotientModel,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, bool]:
    """Reusable fail-closed gates for G1a and later discovery runners."""

    checks = foundation_diagnostics(model) if diagnostics is None else diagnostics
    budget = checks["budget_diagnostics"]
    contact = checks["contact_reference"]
    initial = checks["initial_reconstruction"]
    bump = checks["bump_profile_reference"]
    reference = checks["small_operator_reference"]
    transport = checks["transport_rate_reference"]
    catalyst_profiles = bump["catalyst_profiles"]
    initial_profiles = bump["initial_marginals"]
    contact_centroid_max_abs = float(np.max(np.abs(contact["centroid"])))
    contact_reflection_max_abs = max(
        contact["maximum_parallel_reflection_error"],
        contact["maximum_perpendicular_reflection_error"],
    )
    initial_moments_within_tolerance = all(
        abs(initial["errors"][coordinate]) <= initial["tolerances"][coordinate]
        for coordinate in initial["errors"]
    )
    jet_relative_errors = reference["jet_relative_errors"]
    return {
        "free_generator_row_sums": model.operator_row_error <= 1.0e-12,
        "free_generator_offdiagonal_nonnegative": _offdiagonal_minimum(model.free_generator)
        >= -1.0e-14,
        "killed_mass_balance": model.killed_mass_balance_error <= 1.0e-12,
        "physical_budget": checks["budget_relative_error"] <= 1.0e-10,
        "patchwise_integrals": max(budget["patch_integral_absolute_errors"], default=np.inf)
        <= 1.0e-10,
        "patch_quadrature_error_estimates": max(
            budget["patch_integral_error_estimates"], default=np.inf
        )
        <= 1.0e-11,
        "patch_profile_zeroth_moments": max(
            profile["zeroth_moment_error"] for profile in catalyst_profiles
        )
        <= 1.0e-10,
        "patch_profile_first_moments": all(
            abs(profile["first_moment_error"]) <= profile["first_moment_tolerance"]
            for profile in catalyst_profiles
        ),
        "patch_profile_reference_per_cell": max(
            profile["maximum_per_cell_mass_error"] for profile in catalyst_profiles
        )
        <= 2.0e-10,
        "patch_profile_reference_l1": max(
            profile["relative_l1_mass_error"] for profile in catalyst_profiles
        )
        <= 2.0e-10,
        "endpoint_physical_budgets": max(budget["endpoint_budget_relative_errors"], default=np.inf)
        <= 1.0e-10,
        "budget_derivative_zero": budget["scaled_budget_derivative_error"] <= 1.0e-10,
        "endpoint_weight_sums": max(budget["endpoint_weight_sum_errors"]) <= 1.0e-14,
        "endpoint_weight_nonnegative": min(budget["endpoint_component_minima"]) >= -1.0e-14,
        "endpoint_kappa_nonnegative": min(budget["endpoint_kappa_minima"]) >= -1.0e-14,
        "endpoint_killing_nonnegative": min(budget["endpoint_killing_minima"]) >= -1.0e-14,
        "affine_control_line_certified": budget["affine_line_weight_nonnegativity_certified"],
        "current_kappa_killing_nonnegative": budget["current_kappa_minimum"] >= -1.0e-14
        and budget["current_killing_minimum"] >= -1.0e-14,
        "contact_area": checks["contact_area_relative_error"] <= 1.0e-10,
        "contact_quadrature_error_estimate": checks["contact_area_error_estimate"] <= 1.0e-11,
        "contact_reference_per_cell": contact["maximum_per_cell_fraction_error"] <= 2.0e-10,
        "contact_reference_l1": contact["relative_l1_area_error"] <= 2.0e-10,
        "contact_centroid": contact_centroid_max_abs <= 1.0e-12,
        "contact_reflections": contact_reflection_max_abs <= 1.0e-11,
        "initial_mass": checks["initial_mass_error"] <= 1.0e-12,
        "initial_reconstructed_moments": initial_moments_within_tolerance,
        "initial_circular_resultant": initial["circular_resultant_magnitude"] >= 0.9,
        "initial_profile_zeroth_moments": max(
            profile["zeroth_moment_error"] for profile in initial_profiles
        )
        <= 1.0e-10,
        "initial_profile_first_moments": all(
            abs(profile["first_moment_error"]) <= profile["first_moment_tolerance"]
            for profile in initial_profiles
        ),
        "initial_profile_reference_per_cell": max(
            profile["maximum_per_cell_mass_error"] for profile in initial_profiles
        )
        <= 2.0e-10,
        "initial_profile_reference_l1": max(
            profile["relative_l1_mass_error"] for profile in initial_profiles
        )
        <= 2.0e-10,
        "initial_contact_safe": checks["initial_contact_mass"] == 0.0,
        "tensor_killing_order": checks["tensor_killing_max_abs_error"] <= 1.0e-14,
        "tensor_operator_sentinel": reference["tensor_order_sentinel"],
        "main_transport_rate_reference": transport["maximum_absolute_rate_error"] <= 1.0e-12
        and transport["maximum_relative_rate_error"] <= 1.0e-12,
        "dense_sparse_exponential": reference["dense_sparse_state_relative_error"] <= 1.0e-11,
        "one_step_two_half_step": reference["one_step_two_half_step_relative_error"] <= 1.0e-11,
        "time_jet_references": jet_relative_errors[0] <= 1.0e-7
        and jet_relative_errors[1] <= 1.0e-6
        and jet_relative_errors[2] <= 1.0e-4,
    }


def boundary_layer_union_mask(
    midpoint_cells: int,
    relative_parallel_cells: int,
    relative_perp_cells: int,
    *,
    layers: int = 2,
) -> np.ndarray:
    """Return the union of outer layers in the two nonperiodic coordinates."""

    shape = (int(midpoint_cells), int(relative_parallel_cells), int(relative_perp_cells))
    if min(shape) < 1 or layers < 1:
        raise ValueError("boundary mask dimensions and layer count must be positive")
    mask = np.zeros(shape, dtype=bool)
    width_z = min(int(layers), shape[0])
    width_r = min(int(layers), shape[1])
    mask[:width_z, :, :] = True
    mask[-width_z:, :, :] = True
    mask[:, :width_r, :] = True
    mask[:, -width_r:, :] = True
    return mask


def solve_smoke(
    model: QuotientModel,
    *,
    time_stop: float,
    time_points: int,
) -> dict[str, Any]:
    """Evaluate a small killed semigroup and exact generator identities."""

    times = np.linspace(0.0, float(time_stop), int(time_points))
    states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            model.initial,
            start=0.0,
            stop=float(time_stop),
            num=int(time_points),
            endpoint=True,
        )
    )
    density = np.asarray(states @ model.killing, dtype=float)
    survival = np.asarray(np.sum(states, axis=1), dtype=float)
    ones = np.ones(model.grid.state_count, dtype=float)
    survival_derivative = np.asarray(states @ (model.killed_generator @ ones), dtype=float)
    differential_mass_error = float(np.max(np.abs(survival_derivative + density)))
    reaction_mass = float(np.trapezoid(density, times))
    quadrature_closure_error = float(abs(reaction_mass + survival[-1] - 1.0))
    first_vector = model.killed_generator @ model.killing
    second_vector = model.killed_generator @ first_vector
    third_vector = model.killed_generator @ second_vector
    first = np.asarray(states @ first_vector, dtype=float)
    second = np.asarray(states @ second_vector, dtype=float)
    third = np.asarray(states @ third_vector, dtype=float)
    shape = (
        time_points,
        model.grid.midpoint_cells,
        model.grid.relative_parallel_cells,
        model.grid.relative_perp_cells,
    )
    reshaped = states.reshape(shape)
    boundary_mask = boundary_layer_union_mask(*shape[1:], layers=2)
    boundary_mass = np.sum(reshaped[:, boundary_mask], axis=1)
    boundary_ratio = np.divide(
        boundary_mass,
        survival,
        out=np.full_like(boundary_mass, np.inf),
        where=survival > 0.0,
    )
    return {
        "time_stop": float(time_stop),
        "time_points": int(time_points),
        "minimum_state_mass": float(np.min(states)),
        "minimum_density": float(np.min(density)),
        "maximum_density": float(np.max(density)),
        "final_survival": float(survival[-1]),
        "maximum_survival_increase": float(np.max(np.diff(survival))),
        "differential_mass_balance_error": differential_mass_error,
        "trapezoid_reaction_mass": reaction_mass,
        "trapezoid_closure_error": quadrature_closure_error,
        "maximum_boundary_layer_fraction": float(np.max(boundary_ratio)),
        "final_boundary_layer_fraction": float(boundary_ratio[-1]),
        "jet_ranges": {
            "f_t": [float(np.min(first)), float(np.max(first))],
            "f_tt": [float(np.min(second)), float(np.max(second))],
            "f_ttt": [float(np.min(third)), float(np.max(third))],
        },
        "sampled_sign_change_count_f_t": int(
            np.count_nonzero(np.signbit(first[:-1]) != np.signbit(first[1:]))
        ),
    }


def build_payload(
    *,
    midpoint_cells: int = 25,
    relative_parallel_cells: int = 25,
    relative_perp_cells: int = 25,
    theta: float = 0.5,
    time_stop: float = 40.0,
    time_points: int = 161,
) -> dict[str, Any]:
    """Build and solve the deterministic G1 smoke configuration."""

    pars = PilotParameters()
    grid = QuotientGrid2D(
        midpoint_cells=midpoint_cells,
        relative_parallel_cells=relative_parallel_cells,
        relative_perp_cells=relative_perp_cells,
        midpoint_bounds=pars.midpoint_bounds,
        relative_parallel_bounds=pars.relative_parallel_bounds,
        transverse_width=pars.transverse_width,
    )
    model = build_model(grid, theta=theta, parameters=pars)
    solve = solve_smoke(model, time_stop=time_stop, time_points=time_points)
    foundation = foundation_diagnostics(model)
    gates = foundation_gates(model, foundation)
    gates.update(
        {
            "state_nonnegative": solve["minimum_state_mass"] >= -1.0e-13,
            "density_nonnegative": solve["minimum_density"] >= -1.0e-13,
            "survival_monotone": solve["maximum_survival_increase"] <= 1.0e-12,
            "differential_mass_balance": solve["differential_mass_balance_error"] <= 1.0e-10,
        }
    )
    return {
        "schema_version": 3,
        "stage": "G1a_pre_fold_foundations",
        "continuum_verified": False,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "claim_scope": (
            "G1 operator/geometry/mass-balance smoke only; not a continuum fold, "
            "mesh-convergence result, cusp, trimodality result, or PRR claim"
        ),
        "generator": str(HERE.relative_to(HERE.parents[4])),
        "parameters": asdict(pars),
        "frozen_configuration": {
            "physical_parameters": asdict(pars),
            "control_endpoints": {
                "lower_weights": [float(value) for value in LOWER_WEIGHTS],
                "upper_weights": [float(value) for value in UPPER_WEIGHTS],
            },
            "box": {
                "midpoint_bounds": [float(value) for value in pars.midpoint_bounds],
                "relative_parallel_bounds": [
                    float(value) for value in pars.relative_parallel_bounds
                ],
                "relative_perpendicular_bounds": [
                    -0.5 * pars.transverse_width,
                    0.5 * pars.transverse_width,
                ],
            },
            "grid_shape": [
                int(midpoint_cells),
                int(relative_parallel_cells),
                int(relative_perp_cells),
            ],
            "control_theta": float(theta),
            "time_window": [0.0, float(time_stop)],
            "time_points": int(time_points),
        },
        "grid": {
            "midpoint_cells": midpoint_cells,
            "relative_parallel_cells": relative_parallel_cells,
            "relative_perp_cells": relative_perp_cells,
            "state_count": grid.state_count,
            "midpoint_spacing": grid.midpoint_spacing,
            "relative_parallel_spacing": grid.relative_parallel_spacing,
            "relative_perp_spacing": grid.relative_perp_spacing,
            "theta": float(theta),
        },
        "geometry_and_budget": {
            "base_bump_integral": BASE_BUMP_INTEGRAL,
            "expected_contact_area": foundation["expected_contact_area"],
            "integrated_contact_area": foundation["integrated_contact_area"],
            "contact_area_relative_error": foundation["contact_area_relative_error"],
            "contact_area_error_estimate": foundation["contact_area_error_estimate"],
            "contact_reference": foundation["contact_reference"],
            "expected_physical_budget": foundation["expected_physical_budget"],
            "physical_budget": foundation["physical_budget"],
            "budget_relative_error": foundation["budget_relative_error"],
            "budget_diagnostics": foundation["budget_diagnostics"],
            "bump_profile_reference": foundation["bump_profile_reference"],
            "initial_mass_error": foundation["initial_mass_error"],
            "initial_contact_mass": foundation["initial_contact_mass"],
            "initial_reconstruction": foundation["initial_reconstruction"],
        },
        "operator": {
            "free_nnz": int(model.free_generator.nnz),
            "killed_nnz": int(model.killed_generator.nnz),
            "minimum_free_offdiagonal": _offdiagonal_minimum(model.free_generator),
            "free_row_error": model.operator_row_error,
            "killed_mass_balance_error": model.killed_mass_balance_error,
            "tensor_killing_max_abs_error": foundation["tensor_killing_max_abs_error"],
            "transport_rate_reference": foundation["transport_rate_reference"],
        },
        "reference_checks": foundation["small_operator_reference"],
        "solve": solve,
        "gates": gates,
        "limitations": [
            "The grid is deliberately too coarse for continuum confirmation.",
            "No fold solve or parameter continuation is performed.",
            "Trapezoid closure is reported but is not a solver gate; differential mass balance is exact.",
            "The unbounded longitudinal process is represented by a finite zero-flux smoke box.",
            "Only the transversely invariant slab family is represented.",
        ],
    }


def _write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + chr(10), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--midpoint-cells", type=int, default=25)
    parser.add_argument("--relative-parallel-cells", type=int, default=25)
    parser.add_argument("--relative-perp-cells", type=int, default=25)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--time-stop", type=float, default=40.0)
    parser.add_argument("--time-points", type=int, default=161)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(
        midpoint_cells=args.midpoint_cells,
        relative_parallel_cells=args.relative_parallel_cells,
        relative_perp_cells=args.relative_perp_cells,
        theta=args.theta,
        time_stop=args.time_stop,
        time_points=args.time_points,
    )
    _write_payload(args.output, payload)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(
        json.dumps(
            {"status": payload["status"], "output": str(args.output), "sha256": digest},
            indent=2,
        )
    )
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
