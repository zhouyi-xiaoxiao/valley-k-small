"""Science-free rate-defined tensor FV kernel for the Round-107 F0 gate.

The module deliberately has no production-control defaults and never imports
or evaluates a positive-budget finite-volume row.  A tensor generator is
defined only by nonnegative outward intervals for coordinate-transition rates
and Doi killing.  Its diagonal, uniformization rate, ``delta_Q``, ``delta_P``,
and nonnegative matrix-free ``P.T`` action are derived from those inputs.

The code is an F0 implementation object.  It is not an F1 manifest, a
continuum certificate, or authorization to inspect prospective LP-control
values.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Any, Iterable, Sequence

import gmpy2
import numpy as np
import verified_uniformization_enclosure as reference
from scipy import sparse


class F0VerificationFailure(RuntimeError):
    """Fail-closed F0 outcome with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


HOLD_INTERVAL_INVALID = "HOLD_F0_INTERVAL_INVALID"
HOLD_NEGATIVE_RATE = "HOLD_F0_NEGATIVE_RATE"
HOLD_STORED_DIAGONAL = "HOLD_F0_STORED_DIAGONAL_FORBIDDEN"
HOLD_CONTROL_SOURCE = "HOLD_F0_CONTROL_SOURCE_FORBIDDEN"
HOLD_CONTROL_PARSE = "HOLD_F0_CONTROL_PARSE_FAILED"
HOLD_SUPPORT_NORMALIZATION = "HOLD_F0_SUPPORT_NORMALIZATION_FAILED"
HOLD_INITIAL_MASS = "HOLD_F0_INITIAL_MASS_ENCLOSURE_FAILED"
HOLD_RATE_TOO_LOW = "HOLD_F0_UNIFORMIZATION_RATE_TOO_LOW"
HOLD_ROW_STRUCTURE = "HOLD_F0_ROW_STRUCTURE_FAILED"
HOLD_DELTA_LEDGER = "HOLD_F0_DELTA_LEDGER_FAILED"
HOLD_ACTION = "HOLD_F0_MATRIX_FREE_ACTION_FAILED"
HOLD_TAIL = "HOLD_F0_POISSON_TAIL_LEDGER_FAILED"
HOLD_TIME = "HOLD_F0_EXACT_TIME_CLOSURE_FAILED"
HOLD_ROUNDING = "HOLD_F0_RUNTIME_ROUNDING_FAILED"
HOLD_RESOURCE = "HOLD_F0_RESOURCE_CAP_EXCEEDED"
HOLD_TOPOLOGY = "HOLD_F0_FULL_WINDOW_TOPOLOGY_FAILED"
HOLD_NEWTON = "HOLD_F0_INTERVAL_NEWTON_FAILED"
HOLD_COVERAGE = "HOLD_F0_TIME_TILE_COVERAGE_FAILED"

SELECTOR_SOURCE_KIND = "selector_json_numerator_denominator"
FROZEN_MAXIMUM_DIMENSIONS = 3
FROZEN_MAXIMUM_INCOMING_TERMS_3D = 7
FROZEN_MAXIMUM_FLOATING_OPS_PER_OUTPUT_3D = 13


def _require_fraction(value: Fraction | int, label: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (Fraction, int)):
        raise F0VerificationFailure(
            HOLD_INTERVAL_INVALID,
            f"{label} must be an exact Fraction or integer",
        )
    return Fraction(value)


def _is_strict_fraction(value: Any) -> bool:
    return type(value) is Fraction


def _is_strict_int(value: Any) -> bool:
    return type(value) is int


def _is_strict_float(value: Any) -> bool:
    return type(value) is float


def _fraction_lower(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "fraction does not fit binary64")
    if Fraction.from_float(candidate) > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    return candidate


def _fraction_upper(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "fraction does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    return candidate


def _fraction_centre(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "fraction centre is nonfinite")
    return candidate


@dataclass(frozen=True)
class OutwardInterval:
    """Finite binary64 endpoints enclosing a real scalar."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.lower)
            or not math.isfinite(self.upper)
            or self.lower > self.upper
        ):
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid finite interval")

    @property
    def lower_fraction(self) -> Fraction:
        return Fraction.from_float(float(self.lower))

    @property
    def upper_fraction(self) -> Fraction:
        return Fraction.from_float(float(self.upper))

    @classmethod
    def from_fraction(cls, value: Fraction | int) -> OutwardInterval:
        exact = _require_fraction(value, "interval point")
        return cls(_fraction_lower(exact), _fraction_upper(exact))

    @classmethod
    def from_fraction_bounds(
        cls,
        lower: Fraction | int,
        upper: Fraction | int,
    ) -> OutwardInterval:
        lo = _require_fraction(lower, "interval lower")
        hi = _require_fraction(upper, "interval upper")
        if lo > hi:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "reversed rational interval")
        return cls(_fraction_lower(lo), _fraction_upper(hi))

    def require_nonnegative(self, label: str) -> None:
        if self.lower < 0.0:
            raise F0VerificationFailure(HOLD_NEGATIVE_RATE, f"{label} has a negative lower bound")

    def centre(self) -> float:
        midpoint = (self.lower_fraction + self.upper_fraction) / 2
        candidate = _fraction_centre(midpoint)
        if candidate < self.lower:
            candidate = self.lower
        if candidate > self.upper:
            candidate = self.upper
        return float(candidate)

    def radius_about(self, centre: float) -> Fraction:
        point = Fraction.from_float(float(centre))
        if point < self.lower_fraction or point > self.upper_fraction:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "centre lies outside interval")
        return max(point - self.lower_fraction, self.upper_fraction - point)

    def add_nonnegative(self, other: OutwardInterval) -> OutwardInterval:
        self.require_nonnegative("left addend")
        other.require_nonnegative("right addend")
        return OutwardInterval.from_fraction_bounds(
            self.lower_fraction + other.lower_fraction,
            self.upper_fraction + other.upper_fraction,
        )

    def multiply_nonnegative(self, other: OutwardInterval) -> OutwardInterval:
        self.require_nonnegative("left factor")
        other.require_nonnegative("right factor")
        return OutwardInterval.from_fraction_bounds(
            self.lower_fraction * other.lower_fraction,
            self.upper_fraction * other.upper_fraction,
        )

    def scale_nonnegative(self, value: Fraction | int) -> OutwardInterval:
        scale = _require_fraction(value, "nonnegative scale")
        if scale < 0:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "negative interval scale")
        return OutwardInterval.from_fraction_bounds(
            scale * self.lower_fraction,
            scale * self.upper_fraction,
        )

    def divide_positive(self, other: OutwardInterval) -> OutwardInterval:
        """Divide two nonnegative intervals when the denominator is positive."""

        self.require_nonnegative("numerator")
        other.require_nonnegative("denominator")
        if other.lower_fraction <= 0:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "denominator contains zero")
        return OutwardInterval.from_fraction_bounds(
            self.lower_fraction / other.upper_fraction,
            self.upper_fraction / other.lower_fraction,
        )

    def contains_fraction(self, value: Fraction | int) -> bool:
        exact = _require_fraction(value, "contained value")
        return self.lower_fraction <= exact <= self.upper_fraction


ZERO_INTERVAL = OutwardInterval.from_fraction(0)
ONE_INTERVAL = OutwardInterval.from_fraction(1)


def _mpfr_from_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=rounding):
        return gmpy2.mpfr(value.numerator) / gmpy2.mpfr(value.denominator)


def _exp_interval(value: Fraction, *, precision_bits: int) -> OutwardInterval:
    lo = _mpfr_from_fraction(value, precision_bits, gmpy2.RoundDown)
    hi = _mpfr_from_fraction(value, precision_bits, gmpy2.RoundUp)
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        exp_lo = gmpy2.exp(lo)
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        exp_hi = gmpy2.exp(hi)
    return OutwardInterval(
        reference._mpfr_to_float_lower(exp_lo),
        reference._mpfr_to_float_upper(exp_hi),
    )


def _bernoulli_positive_interval(
    value: Fraction,
    *,
    precision_bits: int,
) -> OutwardInterval:
    if value <= 0:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "positive Bernoulli input required")
    x_lo = _mpfr_from_fraction(value, precision_bits, gmpy2.RoundDown)
    x_hi = _mpfr_from_fraction(value, precision_bits, gmpy2.RoundUp)
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        denominator_lo = gmpy2.exp(x_lo) - 1
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        denominator_hi = gmpy2.exp(x_hi) - 1
    if denominator_lo <= 0:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "Bernoulli denominator unresolved")
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        lower = x_lo / denominator_hi
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        upper = x_hi / denominator_lo
    return OutwardInterval(
        reference._mpfr_to_float_lower(lower),
        reference._mpfr_to_float_upper(upper),
    )


def scharfetter_gummel_bernoulli_interval(
    delta_potential: Fraction | int,
    *,
    precision_bits: int = 192,
) -> OutwardInterval:
    """Enclose B(x)=x/(exp(x)-1) for an exact rational x."""

    value = _require_fraction(delta_potential, "potential difference")
    if precision_bits < 96:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "MPFR precision is below 96 bits")
    if value == 0:
        return ONE_INTERVAL
    if value > 0:
        return _bernoulli_positive_interval(value, precision_bits=precision_bits)
    positive = -value
    # B(-x)=exp(x) B(x), x>0.  Both factors are positive.
    return _exp_interval(positive, precision_bits=precision_bits).multiply_nonnegative(
        _bernoulli_positive_interval(positive, precision_bits=precision_bits)
    )


@dataclass(frozen=True)
class TensorAxis:
    name: str
    size: int
    periodic: bool
    positions: tuple[Fraction, ...]
    cell_volumes: tuple[Fraction, ...]
    cell_segments: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    forward_rates: tuple[OutwardInterval, ...]
    backward_rates: tuple[OutwardInterval, ...]
    stationary_masses: tuple[OutwardInterval, ...]
    domain_start: Fraction
    domain_width: Fraction
    periodic_shift: Fraction
    construction: str

    def validate(self) -> None:
        if not self.name or self.size < 2:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "axis name/size is invalid")
        collections = (
            self.positions,
            self.cell_volumes,
            self.cell_segments,
            self.forward_rates,
            self.backward_rates,
            self.stationary_masses,
        )
        if any(len(values) != self.size for values in collections):
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "axis array length mismatch")
        if self.domain_width <= 0 or any(volume <= 0 for volume in self.cell_volumes):
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "axis volumes/domain are invalid")
        for label, rates in (
            ("forward rate", self.forward_rates),
            ("backward rate", self.backward_rates),
        ):
            for rate in rates:
                rate.require_nonnegative(label)
        for mass in self.stationary_masses:
            if mass.lower <= 0.0:
                raise F0VerificationFailure(
                    HOLD_INTERVAL_INVALID,
                    "stationary-mass interval is not strictly positive",
                )
        if self.periodic:
            if self.periodic_shift < 0 or self.periodic_shift >= self.domain_width:
                raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "periodic shift is invalid")
        else:
            if self.forward_rates[-1].upper != 0.0 or self.backward_rates[0].upper != 0.0:
                raise F0VerificationFailure(
                    HOLD_ROW_STRUCTURE,
                    "reflecting axis has a transition through a boundary",
                )

    @property
    def has_half_boundary_volumes(self) -> bool:
        if self.periodic or self.size < 3:
            return False
        return bool(
            2 * self.cell_volumes[0] == self.cell_volumes[1]
            and 2 * self.cell_volumes[-1] == self.cell_volumes[-2]
        )


def build_reflecting_sg_axis(
    name: str,
    positions: Sequence[Fraction | int],
    potentials: Sequence[Fraction | int],
    diffusion: Fraction | int,
    *,
    precision_bits: int = 192,
) -> TensorAxis:
    """Build a vertex-centred reflecting SG axis with half end volumes."""

    points = tuple(_require_fraction(value, "axis position") for value in positions)
    energy = tuple(_require_fraction(value, "axis potential") for value in potentials)
    coefficient = _require_fraction(diffusion, "diffusion")
    if len(points) < 3 or len(energy) != len(points) or coefficient <= 0:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "malformed reflecting SG axis")
    if any(left >= right for left, right in zip(points, points[1:], strict=False)):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "axis positions are not increasing")

    boundaries = [points[0]]
    boundaries.extend((left + right) / 2 for left, right in zip(points, points[1:], strict=False))
    boundaries.append(points[-1])
    volumes = tuple(boundaries[index + 1] - boundaries[index] for index in range(len(points)))
    segments = tuple(((boundaries[index], boundaries[index + 1]),) for index in range(len(points)))
    forward = [ZERO_INTERVAL for _ in points]
    backward = [ZERO_INTERVAL for _ in points]
    for left in range(len(points) - 1):
        right = left + 1
        distance = points[right] - points[left]
        delta = energy[right] - energy[left]
        left_factor = coefficient / (volumes[left] * distance)
        right_factor = coefficient / (volumes[right] * distance)
        forward[left] = scharfetter_gummel_bernoulli_interval(
            delta,
            precision_bits=precision_bits,
        ).scale_nonnegative(left_factor)
        backward[right] = scharfetter_gummel_bernoulli_interval(
            -delta,
            precision_bits=precision_bits,
        ).scale_nonnegative(right_factor)

    stationary = tuple(
        _exp_interval(-potential, precision_bits=precision_bits).scale_nonnegative(volume)
        for potential, volume in zip(energy, volumes, strict=True)
    )
    axis = TensorAxis(
        name=name,
        size=len(points),
        periodic=False,
        positions=points,
        cell_volumes=volumes,
        cell_segments=segments,
        forward_rates=tuple(forward),
        backward_rates=tuple(backward),
        stationary_masses=stationary,
        domain_start=points[0],
        domain_width=points[-1] - points[0],
        periodic_shift=Fraction(0),
        construction="vertex_centred_reflecting_scharfetter_gummel",
    )
    axis.validate()
    verify_axis_detailed_balance(axis)
    return axis


def build_cell_centred_reflecting_sg_axis(
    name: str,
    lower: Fraction | int,
    upper: Fraction | int,
    cells: int,
    potential_at: Any,
    diffusion: Fraction | int,
    *,
    precision_bits: int = 192,
) -> TensorAxis:
    """Build an equal-volume cell-centred reflecting SG axis.

    ``potential_at`` is called only on exact-rational cell centres and must
    return an exact ``Fraction`` or integer.  Keeping the coordinate geometry
    exact prevents decimal re-parsing or a rounded face drift from entering
    the production rates.
    """

    domain_lower = _require_fraction(lower, "cell-centred lower bound")
    domain_upper = _require_fraction(upper, "cell-centred upper bound")
    coefficient = _require_fraction(diffusion, "cell-centred diffusion")
    if (
        isinstance(cells, bool)
        or not isinstance(cells, int)
        or cells < 3
        or domain_lower >= domain_upper
        or coefficient <= 0
        or not callable(potential_at)
    ):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "malformed cell-centred SG axis")
    step = (domain_upper - domain_lower) / cells
    positions = tuple(domain_lower + (index + Fraction(1, 2)) * step for index in range(cells))
    potentials = tuple(
        _require_fraction(potential_at(position), "cell-centred potential")
        for position in positions
    )
    volumes = (step,) * cells
    segments = tuple(
        ((domain_lower + index * step, domain_lower + (index + 1) * step),)
        for index in range(cells)
    )
    forward = [ZERO_INTERVAL for _ in positions]
    backward = [ZERO_INTERVAL for _ in positions]
    for left in range(cells - 1):
        right = left + 1
        delta = potentials[right] - potentials[left]
        common_factor = coefficient / (step * step)
        forward[left] = scharfetter_gummel_bernoulli_interval(
            delta,
            precision_bits=precision_bits,
        ).scale_nonnegative(common_factor)
        backward[right] = scharfetter_gummel_bernoulli_interval(
            -delta,
            precision_bits=precision_bits,
        ).scale_nonnegative(common_factor)
    stationary = tuple(
        _exp_interval(-potential, precision_bits=precision_bits).scale_nonnegative(step)
        for potential in potentials
    )
    axis = TensorAxis(
        name=name,
        size=cells,
        periodic=False,
        positions=positions,
        cell_volumes=volumes,
        cell_segments=segments,
        forward_rates=tuple(forward),
        backward_rates=tuple(backward),
        stationary_masses=stationary,
        domain_start=domain_lower,
        domain_width=domain_upper - domain_lower,
        periodic_shift=Fraction(0),
        construction="cell_centred_reflecting_scharfetter_gummel",
    )
    axis.validate()
    verify_axis_detailed_balance(axis)
    return axis


def _mod_fraction(value: Fraction, width: Fraction) -> Fraction:
    quotient = value // width
    return value - quotient * width


def build_periodic_diffusion_axis(
    name: str,
    cells: int,
    width: Fraction | int,
    diffusion: Fraction | int,
    *,
    half_cell_shift: bool = False,
    domain_start: Fraction | int = Fraction(0),
) -> TensorAxis:
    """Build equal periodic FV cells, optionally shifted by half one cell."""

    domain_width = _require_fraction(width, "periodic width")
    domain_lower = _require_fraction(domain_start, "periodic domain start")
    coefficient = _require_fraction(diffusion, "periodic diffusion")
    if not isinstance(cells, int) or cells < 3 or domain_width <= 0 or coefficient <= 0:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "malformed periodic axis")
    step = domain_width / cells
    shift = step / 2 if half_cell_shift else Fraction(0)
    positions = tuple(
        domain_lower + _mod_fraction((index + Fraction(1, 2)) * step + shift, domain_width)
        for index in range(cells)
    )
    volumes = (step,) * cells
    segments: list[tuple[tuple[Fraction, Fraction], ...]] = []
    for index in range(cells):
        start = domain_lower + _mod_fraction(index * step + shift, domain_width)
        stop = start + step
        domain_upper = domain_lower + domain_width
        if stop <= domain_upper:
            segments.append(((start, stop),))
        else:
            segments.append(((start, domain_upper), (domain_lower, stop - domain_width)))
    rate = OutwardInterval.from_fraction(coefficient / (step * step))
    stationary = tuple(OutwardInterval.from_fraction(step) for _ in range(cells))
    axis = TensorAxis(
        name=name,
        size=cells,
        periodic=True,
        positions=positions,
        cell_volumes=volumes,
        cell_segments=tuple(segments),
        forward_rates=(rate,) * cells,
        backward_rates=(rate,) * cells,
        stationary_masses=stationary,
        domain_start=domain_lower,
        domain_width=domain_width,
        periodic_shift=shift,
        construction="cell_centred_periodic_diffusion_half_shift"
        if half_cell_shift
        else "cell_centred_periodic_diffusion",
    )
    axis.validate()
    verify_axis_detailed_balance(axis)
    return axis


def _intervals_overlap(left: OutwardInterval, right: OutwardInterval) -> bool:
    return max(left.lower_fraction, right.lower_fraction) <= min(
        left.upper_fraction,
        right.upper_fraction,
    )


def verify_axis_detailed_balance(axis: TensorAxis) -> None:
    """Verify interval overlap of both conductance reconstructions per edge."""

    axis.validate()
    edges = range(axis.size) if axis.periodic else range(axis.size - 1)
    for left in edges:
        right = (left + 1) % axis.size
        lhs = axis.stationary_masses[left].multiply_nonnegative(axis.forward_rates[left])
        rhs = axis.stationary_masses[right].multiply_nonnegative(axis.backward_rates[right])
        if not _intervals_overlap(lhs, rhs):
            raise F0VerificationFailure(
                HOLD_ROW_STRUCTURE,
                f"detailed-balance conductance intervals are disjoint on {axis.name}:{left}",
            )


def cell_overlap_fractions(
    axis: TensorAxis,
    start: Fraction | int,
    stop: Fraction | int,
    *,
    wraps: bool = False,
) -> tuple[Fraction, ...]:
    """Exact fractions of cells covered by an interval or wrapped arc."""

    axis.validate()
    lower = _require_fraction(start, "overlap start")
    upper = _require_fraction(stop, "overlap stop")
    domain_lo = axis.domain_start
    domain_hi = domain_lo + axis.domain_width
    if axis.periodic:
        lower = _mod_fraction(lower - domain_lo, axis.domain_width) + domain_lo
        upper = _mod_fraction(upper - domain_lo, axis.domain_width) + domain_lo
        use_wrap = wraps or upper < lower
        targets = ((lower, domain_hi), (domain_lo, upper)) if use_wrap else ((lower, upper),)
    else:
        if wraps or lower < domain_lo or upper > domain_hi or lower > upper:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid reflecting overlap")
        targets = ((lower, upper),)

    result: list[Fraction] = []
    for cell_segments, volume in zip(axis.cell_segments, axis.cell_volumes, strict=True):
        overlap = Fraction(0)
        for cell_lo, cell_hi in cell_segments:
            for target_lo, target_hi in targets:
                overlap += max(Fraction(0), min(cell_hi, target_hi) - max(cell_lo, target_lo))
        result.append(overlap / volume)
    return tuple(result)


def _hex_fraction(value: str) -> Fraction:
    """Interpret one frozen binary64 hex word as its exact real dyadic."""

    parsed = float.fromhex(value)
    if not math.isfinite(parsed) or (parsed == 0.0 and value.startswith("-")):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid frozen binary64 hex word")
    return Fraction.from_float(parsed)


@dataclass(frozen=True)
class PhysicalParametersV2:
    """Exact dyadic physical parameters frozen by robustness design v2."""

    budget: Fraction = _hex_fraction("0x1.47ae147ae147bp-7")
    particle_diffusion: Fraction = _hex_fraction("0x1.0624dd2f1a9fcp-9")
    ou_stiffness: Fraction = _hex_fraction("0x1.999999999999ap-4")
    ou_mean: Fraction = _hex_fraction("0x1.e666666666666p-1")
    midpoint_start: Fraction = _hex_fraction("0x1.1eb851eb851ecp-3")
    relative_parallel_start: Fraction = _hex_fraction("-0x1.6666666666666p-2")
    relative_perpendicular_start: Fraction = Fraction(0)
    initial_half_width: Fraction = _hex_fraction("0x1.47ae147ae147bp-6")
    contact_radius: Fraction = _hex_fraction("0x1.47ae147ae147bp-3")
    transverse_period: Fraction = Fraction(1)
    support_half_width: Fraction = _hex_fraction("0x1.47ae147ae147bp-5")
    support_centres: tuple[Fraction, ...] = (
        _hex_fraction("0x1.6666666666666p-2"),
        _hex_fraction("0x1.3333333333333p-1"),
        _hex_fraction("0x1.8000000000000p-1"),
        _hex_fraction("0x1.ccccccccccccdp-1"),
    )

    def validate(self) -> None:
        if (
            self.budget <= 0
            or self.particle_diffusion <= 0
            or self.ou_stiffness <= 0
            or self.initial_half_width <= 0
            or self.contact_radius <= 0
            or self.transverse_period <= 0
            or 2 * self.contact_radius >= self.transverse_period
            or self.support_half_width <= 0
            or len(self.support_centres) != 4
            or tuple(sorted(self.support_centres)) != self.support_centres
        ):
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid v2 physical parameters")


@dataclass(frozen=True)
class PhysicalConfigurationSpec:
    label: str
    midpoint_lower: Fraction
    midpoint_upper: Fraction
    midpoint_size: int
    midpoint_vertex_centred: bool
    relative_lower: Fraction
    relative_upper: Fraction
    relative_size: int
    relative_vertex_centred: bool
    transverse_size: int
    transverse_half_shift: bool
    purpose: str
    expected_states: int

    def validate(self) -> None:
        if (
            not self.label
            or self.midpoint_lower >= self.midpoint_upper
            or self.relative_lower >= self.relative_upper
            or min(self.midpoint_size, self.relative_size, self.transverse_size) < 3
            or self.expected_states
            != self.midpoint_size * self.relative_size * self.transverse_size
        ):
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid physical configuration")


PHYSICAL_CONFIGURATION_ORDER_V2 = (
    "O113/Base",
    "E128/Base",
    "O129/Base",
    "O161/Base",
    "M+",
    "R+",
    "MR+",
    "MR+F",
    "A_M",
    "A_R",
    "A_Y",
    "A_MRY",
)


@lru_cache(maxsize=1)
def physical_configuration_specs_v2() -> tuple[PhysicalConfigurationSpec, ...]:
    """Return the byte-frozen 12-row configuration family in normative order."""

    m0 = _hex_fraction("-0x1.0000000000000p-2")
    m1 = _hex_fraction("0x1.d99999999999ap+0")
    me0 = _hex_fraction("-0x1.199999999999ap-1")
    me1 = _hex_fraction("0x1.1333333333333p+1")
    r0 = _hex_fraction("-0x1.ccccccccccccdp+0")
    r1 = _hex_fraction("0x1.ccccccccccccdp+0")
    re0 = _hex_fraction("-0x1.3333333333333p+1")
    re1 = _hex_fraction("0x1.3333333333333p+1")
    rows = (
        PhysicalConfigurationSpec(
            "O113/Base",
            m0,
            m1,
            113,
            False,
            r0,
            r1,
            113,
            False,
            113,
            False,
            "coarse odd refinement",
            1_442_897,
        ),
        PhysicalConfigurationSpec(
            "E128/Base",
            m0,
            m1,
            128,
            False,
            r0,
            r1,
            128,
            False,
            128,
            False,
            "even parity baseline",
            2_097_152,
        ),
        PhysicalConfigurationSpec(
            "O129/Base",
            m0,
            m1,
            129,
            False,
            r0,
            r1,
            129,
            False,
            129,
            False,
            "primary odd refinement",
            2_146_689,
        ),
        PhysicalConfigurationSpec(
            "O161/Base",
            m0,
            m1,
            161,
            False,
            r0,
            r1,
            161,
            False,
            161,
            False,
            "fine odd refinement",
            4_173_281,
        ),
        PhysicalConfigurationSpec(
            "M+",
            me0,
            me1,
            166,
            False,
            r0,
            r1,
            129,
            False,
            129,
            False,
            "midpoint-box enlargement",
            2_762_406,
        ),
        PhysicalConfigurationSpec(
            "R+",
            m0,
            m1,
            129,
            False,
            re0,
            re1,
            172,
            False,
            129,
            False,
            "relative-box enlargement",
            2_862_252,
        ),
        PhysicalConfigurationSpec(
            "MR+",
            me0,
            me1,
            166,
            False,
            re0,
            re1,
            172,
            False,
            129,
            False,
            "combined box enlargement",
            3_683_208,
        ),
        PhysicalConfigurationSpec(
            "MR+F",
            me0,
            me1,
            207,
            False,
            re0,
            re1,
            215,
            False,
            161,
            False,
            "fine combined-box reference",
            7_165_305,
        ),
        PhysicalConfigurationSpec(
            "A_M",
            m0,
            m1,
            129,
            True,
            r0,
            r1,
            128,
            False,
            128,
            False,
            "midpoint half-cell alignment",
            2_113_536,
        ),
        PhysicalConfigurationSpec(
            "A_R",
            m0,
            m1,
            128,
            False,
            r0,
            r1,
            129,
            True,
            128,
            False,
            "relative half-cell alignment",
            2_113_536,
        ),
        PhysicalConfigurationSpec(
            "A_Y",
            m0,
            m1,
            128,
            False,
            r0,
            r1,
            128,
            False,
            128,
            True,
            "periodic half-cell alignment",
            2_097_152,
        ),
        PhysicalConfigurationSpec(
            "A_MRY",
            m0,
            m1,
            129,
            True,
            r0,
            r1,
            129,
            True,
            128,
            True,
            "combined half-cell alignment",
            2_130_048,
        ),
    )
    if tuple(row.label for row in rows) != PHYSICAL_CONFIGURATION_ORDER_V2:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "physical configuration order drifted")
    for row in rows:
        row.validate()
    if sum(row.expected_states for row in rows) != 34_787_462:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "12-row workload identity drifted")
    return rows


def _quadratic_ou_potential(
    position: Fraction,
    *,
    mean: Fraction,
    stiffness: Fraction,
    diffusion: Fraction,
) -> Fraction:
    return stiffness * (position - mean) ** 2 / (2 * diffusion)


def build_physical_axes_v2(
    spec: PhysicalConfigurationSpec,
    *,
    parameters: PhysicalParametersV2 | None = None,
    precision_bits: int = 192,
) -> tuple[TensorAxis, TensorAxis, TensorAxis]:
    """Construct the exact SG/periodic axes for one frozen v2 row."""

    spec.validate()
    pars = PhysicalParametersV2() if parameters is None else parameters
    pars.validate()
    midpoint_diffusion = pars.particle_diffusion / 2
    relative_diffusion = 2 * pars.particle_diffusion

    def midpoint_potential(position: Fraction) -> Fraction:
        return _quadratic_ou_potential(
            position,
            mean=pars.ou_mean,
            stiffness=pars.ou_stiffness,
            diffusion=midpoint_diffusion,
        )

    def relative_potential(position: Fraction) -> Fraction:
        return _quadratic_ou_potential(
            position,
            mean=Fraction(0),
            stiffness=pars.ou_stiffness,
            diffusion=relative_diffusion,
        )

    if spec.midpoint_vertex_centred:
        midpoint_positions = tuple(
            spec.midpoint_lower
            + index * (spec.midpoint_upper - spec.midpoint_lower) / (spec.midpoint_size - 1)
            for index in range(spec.midpoint_size)
        )
        midpoint = build_reflecting_sg_axis(
            "midpoint",
            midpoint_positions,
            tuple(midpoint_potential(value) for value in midpoint_positions),
            midpoint_diffusion,
            precision_bits=precision_bits,
        )
    else:
        midpoint = build_cell_centred_reflecting_sg_axis(
            "midpoint",
            spec.midpoint_lower,
            spec.midpoint_upper,
            spec.midpoint_size,
            midpoint_potential,
            midpoint_diffusion,
            precision_bits=precision_bits,
        )
    if spec.relative_vertex_centred:
        relative_positions = tuple(
            spec.relative_lower
            + index * (spec.relative_upper - spec.relative_lower) / (spec.relative_size - 1)
            for index in range(spec.relative_size)
        )
        relative = build_reflecting_sg_axis(
            "relative_parallel",
            relative_positions,
            tuple(relative_potential(value) for value in relative_positions),
            relative_diffusion,
            precision_bits=precision_bits,
        )
    else:
        relative = build_cell_centred_reflecting_sg_axis(
            "relative_parallel",
            spec.relative_lower,
            spec.relative_upper,
            spec.relative_size,
            relative_potential,
            relative_diffusion,
            precision_bits=precision_bits,
        )
    transverse = build_periodic_diffusion_axis(
        "relative_perpendicular",
        spec.transverse_size,
        pars.transverse_period,
        relative_diffusion,
        half_cell_shift=spec.transverse_half_shift,
        domain_start=-pars.transverse_period / 2,
    )
    axes = (midpoint, relative, transverse)
    if tuple(axis.size for axis in axes) != (
        spec.midpoint_size,
        spec.relative_size,
        spec.transverse_size,
    ):
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "physical axis shape drifted")
    if math.prod(axis.size for axis in axes) != spec.expected_states:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "physical state count drifted")
    if midpoint.has_half_boundary_volumes != spec.midpoint_vertex_centred:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "midpoint alignment construction drifted")
    if relative.has_half_boundary_volumes != spec.relative_vertex_centred:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "relative alignment construction drifted")
    expected_shift = (
        pars.transverse_period / (2 * spec.transverse_size)
        if spec.transverse_half_shift
        else Fraction(0)
    )
    if transverse.periodic_shift != expected_shift:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "transverse alignment construction drifted")
    return axes


def build_all_physical_axes_v2(
    *,
    parameters: PhysicalParametersV2 | None = None,
    precision_bits: int = 192,
) -> tuple[tuple[PhysicalConfigurationSpec, tuple[TensorAxis, TensorAxis, TensorAxis]], ...]:
    """Build all 12 physical axis triples without evaluating any control."""

    return tuple(
        (
            spec,
            build_physical_axes_v2(
                spec,
                parameters=parameters,
                precision_bits=precision_bits,
            ),
        )
        for spec in physical_configuration_specs_v2()
    )


_BUMP_FOURTH_DERIVATIVE_BOUND = Fraction(322_000)


@lru_cache(maxsize=1)
def _verify_bump_fourth_derivative_bound() -> Fraction:
    """Prove a rational global bound for the normalized-shape numerator's f''''.

    With ``t=1/(1-u^2)>=1``, a triangle bound gives coefficients
    ``24 t^3 + 300 t^4 + 672 t^5 + 624 t^6 + 192 t^7 + 16 t^8``
    times ``exp(-t)``.  For each integer ``k``, ``t^k exp(-t)<=k^k exp(-k)``;
    the truncated positive exponential series supplies an exact rational upper
    bound on ``exp(-k)``.
    """

    coefficients = {3: 24, 4: 300, 5: 672, 6: 624, 7: 192, 8: 16}
    derived = Fraction(0)
    for degree, coefficient in coefficients.items():
        exponential_lower = sum(
            (Fraction(degree**order, math.factorial(order)) for order in range(40)),
            Fraction(0),
        )
        derived += coefficient * Fraction(degree**degree, 1) / exponential_lower
    if derived >= _BUMP_FOURTH_DERIVATIVE_BOUND:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "compact-bump derivative bound failed")
    return _BUMP_FOURTH_DERIVATIVE_BOUND


def _compact_bump_value_interval(value: Fraction, *, precision_bits: int) -> OutwardInterval:
    if value <= -1 or value >= 1:
        return ZERO_INTERVAL
    exponent = -Fraction(1, 1 - value * value)
    return _exp_interval(exponent, precision_bits=precision_bits)


def compact_bump_integral_interval(
    lower: Fraction | int,
    upper: Fraction | int,
    *,
    panels_per_unit: int = 16_384,
    precision_bits: int = 192,
) -> OutwardInterval:
    """Validated composite-Simpson enclosure of the unnormalised C-infinity bump."""

    lo = max(Fraction(-1), _require_fraction(lower, "bump integral lower"))
    hi = min(Fraction(1), _require_fraction(upper, "bump integral upper"))
    if hi <= lo:
        return ZERO_INTERVAL
    if (
        isinstance(panels_per_unit, bool)
        or not isinstance(panels_per_unit, int)
        or panels_per_unit < 32
        or precision_bits < 96
    ):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid bump quadrature contract")
    panel_count = max(2, math.ceil(float((hi - lo) * panels_per_unit)))
    if panel_count % 2:
        panel_count += 1
    step = (hi - lo) / panel_count
    lower_sum = Fraction(0)
    upper_sum = Fraction(0)
    for index in range(panel_count + 1):
        value = _compact_bump_value_interval(
            lo + index * step,
            precision_bits=precision_bits,
        )
        weight = 1 if index in (0, panel_count) else (4 if index % 2 else 2)
        lower_sum += weight * value.lower_fraction
        upper_sum += weight * value.upper_fraction
    nominal_lower = step * lower_sum / 3
    nominal_upper = step * upper_sum / 3
    error = (hi - lo) * step**4 * _verify_bump_fourth_derivative_bound() / 180
    return OutwardInterval.from_fraction_bounds(
        max(Fraction(0), nominal_lower - error),
        nominal_upper + error,
    )


@lru_cache(maxsize=32)
def _compact_bump_normalization_interval(
    panels_per_unit: int,
    precision_bits: int,
) -> OutwardInterval:
    return compact_bump_integral_interval(
        -1,
        1,
        panels_per_unit=panels_per_unit,
        precision_bits=precision_bits,
    )


@dataclass(frozen=True)
class NormalizedBumpProfile:
    centre: Fraction
    half_width: Fraction
    period: Fraction | None
    mass_intervals: tuple[OutwardInterval, ...]
    density_intervals: tuple[OutwardInterval, ...]
    analytic_total_mass: Fraction
    panels_per_unit: int
    precision_bits: int


def build_normalized_bump_profile(
    axis: TensorAxis,
    *,
    centre: Fraction | int,
    half_width: Fraction | int,
    period: Fraction | int | None = None,
    panels_per_unit: int = 16_384,
    precision_bits: int = 192,
) -> NormalizedBumpProfile:
    """Enclose cell masses/densities of the analytically normalized bump."""

    axis.validate()
    location = _require_fraction(centre, "bump centre")
    width = _require_fraction(half_width, "bump half width")
    periodic_width = None if period is None else _require_fraction(period, "bump period")
    if width <= 0 or (periodic_width is not None and 2 * width >= periodic_width):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid normalized bump geometry")
    normalization = _compact_bump_normalization_interval(panels_per_unit, precision_bits)
    images = (location,)
    if periodic_width is not None:
        images = tuple(location + shift * periodic_width for shift in range(-2, 3))
    masses: list[OutwardInterval] = []
    densities: list[OutwardInterval] = []
    for segments, volume in zip(axis.cell_segments, axis.cell_volumes, strict=True):
        raw = ZERO_INTERVAL
        for segment_lower, segment_upper in segments:
            for image_centre in images:
                overlap_lower = max(segment_lower, image_centre - width)
                overlap_upper = min(segment_upper, image_centre + width)
                if overlap_upper <= overlap_lower:
                    continue
                local = compact_bump_integral_interval(
                    (overlap_lower - image_centre) / width,
                    (overlap_upper - image_centre) / width,
                    panels_per_unit=panels_per_unit,
                    precision_bits=precision_bits,
                )
                raw = raw.add_nonnegative(local)
        mass = raw.divide_positive(normalization)
        masses.append(mass)
        densities.append(mass.scale_nonnegative(1 / volume))
    mass_lower = sum((entry.lower_fraction for entry in masses), Fraction(0))
    mass_upper = sum((entry.upper_fraction for entry in masses), Fraction(0))
    if not (mass_lower <= 1 <= mass_upper):
        raise F0VerificationFailure(
            HOLD_SUPPORT_NORMALIZATION,
            "normalized bump partition does not enclose unit mass",
        )
    return NormalizedBumpProfile(
        centre=location,
        half_width=width,
        period=periodic_width,
        mass_intervals=tuple(masses),
        density_intervals=tuple(densities),
        analytic_total_mass=Fraction(1),
        panels_per_unit=panels_per_unit,
        precision_bits=precision_bits,
    )


def _disk_primitive_bounds(
    x: Fraction,
    radius: Fraction,
    *,
    precision_bits: int,
) -> tuple[gmpy2.mpfr, gmpy2.mpfr]:
    """Bounds for 0.5*(x*sqrt(r^2-x^2)+r^2*asin(x/r))."""

    radicand = radius * radius - x * x
    if x < 0 or radicand < 0:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "disk primitive input is invalid")
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        root_lo = gmpy2.sqrt(_mpfr_from_fraction(radicand, precision_bits, gmpy2.RoundDown))
        product_lo = _mpfr_from_fraction(x, precision_bits, gmpy2.RoundDown) * root_lo
        angle_lo = gmpy2.asin(_mpfr_from_fraction(x / radius, precision_bits, gmpy2.RoundDown))
        angle_term_lo = (
            _mpfr_from_fraction(radius * radius, precision_bits, gmpy2.RoundDown) * angle_lo
        )
        lower = (product_lo + angle_term_lo) / 2
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        root_hi = gmpy2.sqrt(_mpfr_from_fraction(radicand, precision_bits, gmpy2.RoundUp))
        product_hi = _mpfr_from_fraction(x, precision_bits, gmpy2.RoundUp) * root_hi
        angle_hi = gmpy2.asin(_mpfr_from_fraction(x / radius, precision_bits, gmpy2.RoundUp))
        angle_term_hi = (
            _mpfr_from_fraction(radius * radius, precision_bits, gmpy2.RoundUp) * angle_hi
        )
        upper = (product_hi + angle_term_hi) / 2
    return lower, upper


def _disk_quadrant_area_interval(
    x: Fraction,
    y: Fraction,
    radius: Fraction,
    *,
    precision_bits: int,
) -> OutwardInterval:
    """Enclose area of the disk in ``[0,x] x [0,y]``."""

    if x <= 0 or y <= 0:
        return ZERO_INTERVAL
    x = min(x, radius)
    y = min(y, radius)
    if x * x + y * y <= radius * radius:
        return OutwardInterval.from_fraction(x * y)
    threshold_radicand = radius * radius - y * y
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        threshold_lo = gmpy2.sqrt(
            _mpfr_from_fraction(threshold_radicand, precision_bits, gmpy2.RoundDown)
        )
        threshold_y_lo = threshold_lo * _mpfr_from_fraction(y, precision_bits, gmpy2.RoundDown)
        threshold_ratio_lo = threshold_lo / _mpfr_from_fraction(
            radius, precision_bits, gmpy2.RoundUp
        )
        threshold_angle_lo = gmpy2.asin(threshold_ratio_lo)
        threshold_angle_term_lo = (
            _mpfr_from_fraction(radius * radius, precision_bits, gmpy2.RoundDown)
            * threshold_angle_lo
        )
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        threshold_hi = gmpy2.sqrt(
            _mpfr_from_fraction(threshold_radicand, precision_bits, gmpy2.RoundUp)
        )
        threshold_y_hi = threshold_hi * _mpfr_from_fraction(y, precision_bits, gmpy2.RoundUp)
        threshold_ratio_hi = threshold_hi / _mpfr_from_fraction(
            radius, precision_bits, gmpy2.RoundDown
        )
        threshold_angle_hi = gmpy2.asin(threshold_ratio_hi)
        threshold_angle_term_hi = (
            _mpfr_from_fraction(radius * radius, precision_bits, gmpy2.RoundUp) * threshold_angle_hi
        )
    primitive_lo, primitive_hi = _disk_primitive_bounds(
        x,
        radius,
        precision_bits=precision_bits,
    )
    # G=H(x)+(t0*y-r^2*asin(t0/r))/2.  The sign-aware endpoint
    # combination is required; evaluating the entire expression in one
    # rounding mode would not enclose the subtraction.
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        lower = primitive_lo + (threshold_y_lo - threshold_angle_term_hi) / 2
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        upper = primitive_hi + (threshold_y_hi - threshold_angle_term_lo) / 2
    lower_float = max(0.0, reference._mpfr_to_float_lower(lower))
    upper_float = min(float(x * y), reference._mpfr_to_float_upper(upper))
    return OutwardInterval(lower_float, upper_float)


def _absolute_quadrant_parts(
    lower: Fraction, upper: Fraction
) -> tuple[tuple[Fraction, Fraction], ...]:
    parts: list[tuple[Fraction, Fraction]] = []
    if lower < 0:
        negative_upper = min(upper, Fraction(0))
        if lower < negative_upper:
            parts.append((-negative_upper, -lower))
    if upper > 0:
        positive_lower = max(lower, Fraction(0))
        if positive_lower < upper:
            parts.append((positive_lower, upper))
    return tuple(parts)


def disk_rectangle_area_interval(
    x_lower: Fraction | int,
    x_upper: Fraction | int,
    y_lower: Fraction | int,
    y_upper: Fraction | int,
    radius: Fraction | int,
    *,
    precision_bits: int = 192,
) -> OutwardInterval:
    """Directed MPFR enclosure of a centred disk/rectangle intersection."""

    x0 = _require_fraction(x_lower, "disk rectangle x lower")
    x1 = _require_fraction(x_upper, "disk rectangle x upper")
    y0 = _require_fraction(y_lower, "disk rectangle y lower")
    y1 = _require_fraction(y_upper, "disk rectangle y upper")
    rad = _require_fraction(radius, "disk radius")
    if x0 >= x1 or y0 >= y1 or rad <= 0 or precision_bits < 96:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "invalid disk rectangle geometry")
    nearest_x = Fraction(0) if x0 <= 0 <= x1 else min(abs(x0), abs(x1))
    nearest_y = Fraction(0) if y0 <= 0 <= y1 else min(abs(y0), abs(y1))
    if nearest_x * nearest_x + nearest_y * nearest_y >= rad * rad:
        return ZERO_INTERVAL
    farthest = max(
        x0 * x0 + y0 * y0,
        x0 * x0 + y1 * y1,
        x1 * x1 + y0 * y0,
        x1 * x1 + y1 * y1,
    )
    rectangle_area = (x1 - x0) * (y1 - y0)
    if farthest <= rad * rad:
        return OutwardInterval.from_fraction(rectangle_area)

    total_lower = Fraction(0)
    total_upper = Fraction(0)
    for xa, xb in _absolute_quadrant_parts(x0, x1):
        for ya, yb in _absolute_quadrant_parts(y0, y1):
            g_bd = _disk_quadrant_area_interval(xb, yb, rad, precision_bits=precision_bits)
            g_ad = _disk_quadrant_area_interval(xa, yb, rad, precision_bits=precision_bits)
            g_bc = _disk_quadrant_area_interval(xb, ya, rad, precision_bits=precision_bits)
            g_ac = _disk_quadrant_area_interval(xa, ya, rad, precision_bits=precision_bits)
            lower = (
                g_bd.lower_fraction
                - g_ad.upper_fraction
                - g_bc.upper_fraction
                + g_ac.lower_fraction
            )
            upper = (
                g_bd.upper_fraction
                - g_ad.lower_fraction
                - g_bc.lower_fraction
                + g_ac.upper_fraction
            )
            total_lower += max(Fraction(0), lower)
            total_upper += max(Fraction(0), upper)
    return OutwardInterval.from_fraction_bounds(
        max(Fraction(0), total_lower),
        min(rectangle_area, total_upper),
    )


def build_contact_fraction_intervals_v2(
    relative_parallel: TensorAxis,
    relative_perpendicular: TensorAxis,
    *,
    radius: Fraction | int,
    precision_bits: int = 192,
) -> tuple[OutwardInterval, ...]:
    """Build exact-placement Doi disk fractions on the relative tensor grid."""

    relative_parallel.validate()
    relative_perpendicular.validate()
    rad = _require_fraction(radius, "contact radius")
    if relative_parallel.periodic or not relative_perpendicular.periodic:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "contact axes have wrong topology")
    if 2 * rad >= relative_perpendicular.domain_width:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "contact disk reaches torus cut locus")
    fractions: list[OutwardInterval] = []
    for x_segments, x_volume in zip(
        relative_parallel.cell_segments,
        relative_parallel.cell_volumes,
        strict=True,
    ):
        for y_segments, y_volume in zip(
            relative_perpendicular.cell_segments,
            relative_perpendicular.cell_volumes,
            strict=True,
        ):
            area = ZERO_INTERVAL
            for x0, x1 in x_segments:
                for y0, y1 in y_segments:
                    area = area.add_nonnegative(
                        disk_rectangle_area_interval(
                            x0,
                            x1,
                            y0,
                            y1,
                            rad,
                            precision_bits=precision_bits,
                        )
                    )
            fraction = area.scale_nonnegative(1 / (x_volume * y_volume))
            # Geometrically the intersection fraction belongs to [0,1].
            # Intersecting with that analytic range removes only outward
            # endpoint padding (not admissible values), including the one-ulp
            # overshoot of a fully covered cell.
            fraction = OutwardInterval(max(0.0, fraction.lower), min(1.0, fraction.upper))
            if fraction.lower < 0.0 or fraction.upper > 1.0:
                raise F0VerificationFailure(
                    HOLD_INTERVAL_INVALID, "contact fraction is outside [0,1]"
                )
            fractions.append(fraction)
    return tuple(fractions)


@dataclass(frozen=True)
class PhysicalConfigurationGeometryV2:
    spec: PhysicalConfigurationSpec
    parameters: PhysicalParametersV2
    axes: tuple[TensorAxis, TensorAxis, TensorAxis]
    support_profiles: tuple[NormalizedBumpProfile, ...]
    contact_fractions_relative: tuple[OutwardInterval, ...]
    initial_profiles: tuple[NormalizedBumpProfile, NormalizedBumpProfile, NormalizedBumpProfile]
    installed_budget_exact: Fraction
    installed_budget_relative_radius: Fraction
    prospective_control_values_read: bool
    positive_budget_primary_control_evaluated: bool

    def validate(self) -> None:
        self.spec.validate()
        self.parameters.validate()
        if (
            tuple(axis.size for axis in self.axes)
            != (
                self.spec.midpoint_size,
                self.spec.relative_size,
                self.spec.transverse_size,
            )
            or len(self.support_profiles) != 4
            or any(profile.analytic_total_mass != 1 for profile in self.support_profiles)
            or len(self.contact_fractions_relative)
            != self.spec.relative_size * self.spec.transverse_size
            or any(profile.analytic_total_mass != 1 for profile in self.initial_profiles)
            or self.installed_budget_exact != self.parameters.budget
            or self.installed_budget_relative_radius != 0
            or self.prospective_control_values_read
            or self.positive_budget_primary_control_evaluated
        ):
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "physical geometry ledger is invalid")


def build_physical_geometry_v2(
    spec: PhysicalConfigurationSpec,
    *,
    parameters: PhysicalParametersV2 | None = None,
    panels_per_unit: int = 16_384,
    precision_bits: int = 192,
) -> PhysicalConfigurationGeometryV2:
    """Build one complete control-blind physical geometry and marginal law."""

    pars = PhysicalParametersV2() if parameters is None else parameters
    axes = build_physical_axes_v2(spec, parameters=pars, precision_bits=precision_bits)
    midpoint, relative, transverse = axes
    supports = tuple(
        build_normalized_bump_profile(
            midpoint,
            centre=centre,
            half_width=pars.support_half_width,
            panels_per_unit=panels_per_unit,
            precision_bits=precision_bits,
        )
        for centre in pars.support_centres
    )
    contact = build_contact_fraction_intervals_v2(
        relative,
        transverse,
        radius=pars.contact_radius,
        precision_bits=precision_bits,
    )
    initial = (
        build_normalized_bump_profile(
            midpoint,
            centre=pars.midpoint_start,
            half_width=pars.initial_half_width,
            panels_per_unit=panels_per_unit,
            precision_bits=precision_bits,
        ),
        build_normalized_bump_profile(
            relative,
            centre=pars.relative_parallel_start,
            half_width=pars.initial_half_width,
            panels_per_unit=panels_per_unit,
            precision_bits=precision_bits,
        ),
        build_normalized_bump_profile(
            transverse,
            centre=pars.relative_perpendicular_start,
            half_width=pars.initial_half_width,
            period=pars.transverse_period,
            panels_per_unit=panels_per_unit,
            precision_bits=precision_bits,
        ),
    )
    geometry = PhysicalConfigurationGeometryV2(
        spec=spec,
        parameters=pars,
        axes=axes,
        support_profiles=supports,
        contact_fractions_relative=contact,
        initial_profiles=initial,
        # Unit-normalized supports, unit transverse period, and exact unit-sum
        # selector weights make the installed functional exactly B.  This is
        # a dependency-aware identity, not an independent interval sum.
        installed_budget_exact=pars.budget,
        installed_budget_relative_radius=Fraction(0),
        prospective_control_values_read=False,
        positive_budget_primary_control_evaluated=False,
    )
    geometry.validate()
    return geometry


def build_physical_killing_intervals_v2(
    geometry: PhysicalConfigurationGeometryV2,
    control: RationalControl,
) -> tuple[OutwardInterval, ...]:
    """Expand a control-blind geometry only after exact selector ingestion."""

    geometry.validate()
    if len(control.weights) != 4 or control.source_kind != SELECTOR_SOURCE_KIND:
        raise F0VerificationFailure(HOLD_CONTROL_SOURCE, "physical control source is invalid")
    relative_contact = geometry.contact_fractions_relative
    full_contact = relative_contact * geometry.spec.midpoint_size
    return build_doi_killing_intervals(
        geometry.axes,
        midpoint_axis=0,
        control=control,
        budget=geometry.parameters.budget,
        support_density_intervals=tuple(
            profile.density_intervals for profile in geometry.support_profiles
        ),
        contact_fractions=full_contact,
    )


def physical_initial_component_intervals_v2(
    geometry: PhysicalConfigurationGeometryV2,
) -> tuple[OutwardInterval, ...]:
    """Expand the three normalized marginal laws in canonical C tensor order."""

    geometry.validate()
    midpoint, relative, transverse = (
        profile.mass_intervals for profile in geometry.initial_profiles
    )
    return tuple(
        m.multiply_nonnegative(r).multiply_nonnegative(y)
        for m in midpoint
        for r in relative
        for y in transverse
    )


@dataclass(frozen=True)
class RationalControl:
    control_id: str
    weights: tuple[Fraction, ...]
    weight_intervals: tuple[OutwardInterval, ...]
    source_sha256: str
    source_kind: str


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_selector_rational_control(
    payload_bytes: bytes,
    *,
    expected_sha256: str,
    control_id: str,
    source_kind: str,
) -> RationalControl:
    """Parse only selected numerator/denominator weights from a pinned JSON.

    Historical raw-hex/raw-S_c values may coexist elsewhere in the artifact as
    comparison evidence, but they can never be selected by this function.
    """

    if source_kind != SELECTOR_SOURCE_KIND:
        raise F0VerificationFailure(
            HOLD_CONTROL_SOURCE,
            "v2 controls must come from selector JSON numerator/denominator strings",
        )
    if _sha256_bytes(payload_bytes) != expected_sha256:
        raise F0VerificationFailure(HOLD_CONTROL_PARSE, "selector JSON hash mismatch")
    try:
        payload = json.loads(payload_bytes)
        if (
            payload["stage"] != "method_only_b0_exact_rational_modal_selector"
            or payload["status"] != "HOLD_METHOD_ONLY_NOT_A_CONTINUUM_OR_F0_CONTROL_CERTIFICATE"
        ):
            raise KeyError("selector top-level boundary")
        row = payload["selector_results"][control_id]
        if row["status"] != "PASS_EXACT_RATIONALIZED_SELECTOR":
            raise KeyError("selector status")
        entries = row["selected"]["weights"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise F0VerificationFailure(HOLD_CONTROL_PARSE, "selector JSON path is invalid") from error
    if not isinstance(entries, list) or len(entries) < 2:
        raise F0VerificationFailure(HOLD_CONTROL_PARSE, "selector weight list is invalid")

    weights: list[Fraction] = []
    for entry in entries:
        try:
            numerator_text = entry["numerator"]
            denominator_text = entry["denominator"]
            exact_text = entry["exact"]
            if not all(
                isinstance(value, str) for value in (numerator_text, denominator_text, exact_text)
            ):
                raise ValueError("weight fields must be strings")
            numerator = int(numerator_text)
            denominator = int(denominator_text)
            value = Fraction(numerator, denominator)
            if value != Fraction(exact_text):
                raise ValueError("exact field disagrees")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            raise F0VerificationFailure(HOLD_CONTROL_PARSE, "malformed rational weight") from error
        if value <= 0:
            raise F0VerificationFailure(HOLD_CONTROL_PARSE, "control weight is not positive")
        weights.append(value)
    if sum(weights, Fraction(0)) != 1:
        raise F0VerificationFailure(HOLD_CONTROL_PARSE, "control weights do not sum exactly to one")
    return RationalControl(
        control_id=control_id,
        weights=tuple(weights),
        weight_intervals=tuple(OutwardInterval.from_fraction(value) for value in weights),
        source_sha256=expected_sha256,
        source_kind=source_kind,
    )


def build_doi_killing_intervals(
    axes: Sequence[TensorAxis],
    *,
    midpoint_axis: int,
    control: RationalControl,
    budget: Fraction | int,
    support_density_intervals: Sequence[Sequence[OutwardInterval]],
    contact_fractions: Sequence[OutwardInterval],
) -> tuple[OutwardInterval, ...]:
    """Build tensor Doi killing intervals from normalized midpoint supports."""

    axis_tuple = tuple(axes)
    if not axis_tuple or not (0 <= midpoint_axis < len(axis_tuple)):
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "midpoint axis is invalid")
    for axis in axis_tuple:
        axis.validate()
    shape = tuple(axis.size for axis in axis_tuple)
    states = math.prod(shape)
    supports = tuple(tuple(row) for row in support_density_intervals)
    if len(supports) != len(control.weights) or any(
        len(row) != shape[midpoint_axis] for row in supports
    ):
        raise F0VerificationFailure(HOLD_SUPPORT_NORMALIZATION, "support array shape mismatch")
    if len(contact_fractions) != states:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "contact array shape mismatch")
    for fraction in contact_fractions:
        fraction.require_nonnegative("contact fraction")
        if fraction.upper > 1.0:
            raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "contact fraction exceeds one")

    midpoint_volumes = axis_tuple[midpoint_axis].cell_volumes
    for row in supports:
        lower = sum(
            (
                entry.lower_fraction * volume
                for entry, volume in zip(row, midpoint_volumes, strict=True)
            ),
            Fraction(0),
        )
        upper = sum(
            (
                entry.upper_fraction * volume
                for entry, volume in zip(row, midpoint_volumes, strict=True)
            ),
            Fraction(0),
        )
        if not (lower <= 1 <= upper):
            raise F0VerificationFailure(
                HOLD_SUPPORT_NORMALIZATION,
                "support-density integral does not enclose one",
            )

    budget_interval = OutwardInterval.from_fraction(_require_fraction(budget, "installed budget"))
    budget_interval.require_nonnegative("installed budget")
    catalyst_by_midpoint: list[OutwardInterval] = []
    for cell in range(shape[midpoint_axis]):
        total = ZERO_INTERVAL
        for weight, support in zip(control.weight_intervals, supports, strict=True):
            total = total.add_nonnegative(weight.multiply_nonnegative(support[cell]))
        catalyst_by_midpoint.append(budget_interval.multiply_nonnegative(total))

    killing: list[OutwardInterval] = []
    for flat, coordinate in enumerate(product(*(range(size) for size in shape))):
        catalyst = catalyst_by_midpoint[coordinate[midpoint_axis]]
        killing.append(catalyst.multiply_nonnegative(contact_fractions[flat]))
    return tuple(killing)


@dataclass(frozen=True)
class InitialStateEnclosure:
    nominal: np.ndarray
    component_intervals: tuple[OutwardInterval, ...]
    l1_error: float
    exact_mass_cap: Fraction
    mass_lower: float
    mass_upper: float
    source_sha256: str


def enclose_initial_state(
    component_intervals: Sequence[OutwardInterval],
    *,
    source_payload_bytes: bytes,
    expected_source_sha256: str,
    exact_mass_cap: Fraction | int = Fraction(1),
    maximum_l1_error: float = 1.0e-12,
) -> InitialStateEnclosure:
    intervals = tuple(component_intervals)
    cap = _require_fraction(exact_mass_cap, "exact mass cap")
    if (
        not intervals
        or cap != 1
        or len(expected_source_sha256) != 64
        or _sha256_bytes(source_payload_bytes) != expected_source_sha256
    ):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial-law metadata is invalid")
    if not math.isfinite(maximum_l1_error) or maximum_l1_error < 0:
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial error cap is invalid")
    for interval in intervals:
        interval.require_nonnegative("initial mass")
    lower = sum((interval.lower_fraction for interval in intervals), Fraction(0))
    upper = sum((interval.upper_fraction for interval in intervals), Fraction(0))
    if not (lower <= 1 <= upper):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial total mass does not enclose one")
    nominal = np.asarray([interval.centre() for interval in intervals], dtype=np.float64)
    error = sum(
        (
            max(
                Fraction.from_float(float(value)) - interval.lower_fraction,
                interval.upper_fraction - Fraction.from_float(float(value)),
            )
            for value, interval in zip(nominal, intervals, strict=True)
        ),
        Fraction(0),
    )
    error_upper = _fraction_upper(error)
    if error_upper > maximum_l1_error:
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial l1 enclosure exceeds cap")
    return InitialStateEnclosure(
        nominal=nominal,
        component_intervals=intervals,
        l1_error=error_upper,
        exact_mass_cap=cap,
        mass_lower=_fraction_lower(lower),
        mass_upper=_fraction_upper(upper),
        source_sha256=expected_source_sha256,
    )


def validate_initial_state_enclosure(
    initial: InitialStateEnclosure,
    *,
    expected_states: int,
) -> None:
    """Recompute every in-memory initial-law field except external source bytes.

    The caller is responsible for pinning ``source_sha256`` to the external
    source object.  This replay prevents a frozen dataclass or its mutable
    NumPy payload from being changed coherently after construction.
    """

    if (
        not isinstance(initial, InitialStateEnclosure)
        or isinstance(expected_states, bool)
        or not isinstance(expected_states, int)
        or expected_states < 1
        or len(initial.component_intervals) != expected_states
        or initial.nominal.shape != (expected_states,)
        or initial.nominal.dtype != np.float64
        or initial.exact_mass_cap != 1
        or len(initial.source_sha256) != 64
    ):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial-law shape/metadata is invalid")
    try:
        int(initial.source_sha256, 16)
    except ValueError as error:
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial-law hash is malformed") from error
    intervals = initial.component_intervals
    for interval in intervals:
        interval.require_nonnegative("initial mass")
    lower = sum((interval.lower_fraction for interval in intervals), Fraction(0))
    upper = sum((interval.upper_fraction for interval in intervals), Fraction(0))
    if not lower <= 1 <= upper:
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial total mass no longer encloses one")
    expected_nominal = np.asarray([interval.centre() for interval in intervals], dtype=np.float64)
    if not np.array_equal(initial.nominal, expected_nominal):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial nominal vector was mutated")
    exact_error = sum(
        (
            max(
                Fraction.from_float(float(value)) - interval.lower_fraction,
                interval.upper_fraction - Fraction.from_float(float(value)),
            )
            for value, interval in zip(expected_nominal, intervals, strict=True)
        ),
        Fraction(0),
    )
    if (
        initial.l1_error != _fraction_upper(exact_error)
        or initial.mass_lower != _fraction_lower(lower)
        or initial.mass_upper != _fraction_upper(upper)
    ):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial enclosure ledger was mutated")


@dataclass(frozen=True)
class RateDefinedTensorKernel:
    axes: tuple[TensorAxis, ...]
    shape: tuple[int, ...]
    killing_intervals: tuple[OutwardInterval, ...]
    killing_center: np.ndarray
    forward_center: tuple[np.ndarray, ...]
    backward_center: tuple[np.ndarray, ...]
    diagonal_center: np.ndarray
    p_forward_center: tuple[np.ndarray, ...]
    p_backward_center: tuple[np.ndarray, ...]
    p_self_center: np.ndarray
    rate: float
    rate_fraction: Fraction
    delta_q: float
    delta_q_exact: Fraction
    delta_p: float
    delta_p_exact: Fraction
    delta_p_direct_exact: Fraction
    delta_p_via_q_exact: Fraction
    p_coefficient_rounding_exact: Fraction
    maximum_target_exit_upper: float
    maximum_center_row_sum: float
    maximum_qhat_abs_row_sum: float
    maximum_qhat_abs_row_sum_exact: Fraction
    killing_inf_upper: float
    killing_inf_uncertainty: float
    killing_inf_uncertainty_exact: Fraction
    maximum_incoming_terms: int
    maximum_floating_ops_per_output: int
    roundoff_gamma_index: int
    construction: str

    @property
    def states(self) -> int:
        return math.prod(self.shape)


def _axis_centers(axis: TensorAxis) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray([interval.centre() for interval in axis.forward_rates], dtype=np.float64),
        np.asarray([interval.centre() for interval in axis.backward_rates], dtype=np.float64),
    )


def _outgoing_for_coordinate(
    axes: tuple[TensorAxis, ...],
    coordinate: tuple[int, ...],
) -> Iterable[tuple[OutwardInterval, int, str]]:
    for dimension, (axis, index) in enumerate(zip(axes, coordinate, strict=True)):
        forward = axis.forward_rates[index]
        backward = axis.backward_rates[index]
        if forward.upper > 0.0:
            yield forward, dimension, "forward"
        if backward.upper > 0.0:
            yield backward, dimension, "backward"


def build_rate_defined_tensor_kernel(
    axes: Sequence[TensorAxis],
    killing_intervals: Sequence[OutwardInterval],
    *,
    uniformization_rate: Fraction | int | None = None,
    stored_diagonal: Sequence[float] | None = None,
) -> RateDefinedTensorKernel:
    """Derive Qhat, Phat, delta_Q, and delta_P from rates plus killing."""

    try:
        reference.verify_binary64_runtime()
    except reference.VerificationFailure as error:
        raise F0VerificationFailure(HOLD_ROUNDING, str(error)) from error
    if stored_diagonal is not None:
        raise F0VerificationFailure(
            HOLD_STORED_DIAGONAL,
            "an independently stored diagonal is not an admissible F0 input",
        )
    axis_tuple = tuple(axes)
    if not axis_tuple or len(axis_tuple) > FROZEN_MAXIMUM_DIMENSIONS:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "tensor dimension is unsupported")
    for axis in axis_tuple:
        axis.validate()
        verify_axis_detailed_balance(axis)
    shape = tuple(axis.size for axis in axis_tuple)
    states = math.prod(shape)
    killing = tuple(killing_intervals)
    if len(killing) != states:
        raise F0VerificationFailure(HOLD_INTERVAL_INVALID, "killing array shape mismatch")
    for interval in killing:
        interval.require_nonnegative("Doi killing")

    axis_centers = tuple(_axis_centers(axis) for axis in axis_tuple)
    forward_center = tuple(row[0] for row in axis_centers)
    backward_center = tuple(row[1] for row in axis_centers)
    killing_center = np.asarray([interval.centre() for interval in killing], dtype=np.float64)
    diagonal_center = np.empty(states, dtype=np.float64)
    diagonal_target_bounds: list[tuple[Fraction, Fraction]] = []
    maximum_exit_upper = Fraction(0)
    maximum_center_exit = Fraction(0)
    delta_q_rows: list[Fraction] = []

    for flat, coordinate in enumerate(product(*(range(size) for size in shape))):
        rate_lower = Fraction(0)
        rate_upper = Fraction(0)
        rate_center_sum = Fraction(0)
        off_diagonal_error = Fraction(0)
        for interval, dimension, direction in _outgoing_for_coordinate(axis_tuple, coordinate):
            index = coordinate[dimension]
            center_array = (
                forward_center[dimension] if direction == "forward" else backward_center[dimension]
            )
            center = float(center_array[index])
            rate_lower += interval.lower_fraction
            rate_upper += interval.upper_fraction
            rate_center_sum += Fraction.from_float(center)
            off_diagonal_error += interval.radius_about(center)
        kill_interval = killing[flat]
        kill_center = Fraction.from_float(float(killing_center[flat]))
        exit_lower = rate_lower + kill_interval.lower_fraction
        exit_upper = rate_upper + kill_interval.upper_fraction
        center_exit = rate_center_sum + kill_center
        maximum_exit_upper = max(maximum_exit_upper, exit_upper)
        maximum_center_exit = max(maximum_center_exit, center_exit)
        target_diagonal_lower = -exit_upper
        target_diagonal_upper = -exit_lower
        center_diagonal = _fraction_lower(-center_exit)
        diagonal_center[flat] = center_diagonal
        center_diagonal_fraction = Fraction.from_float(center_diagonal)
        diagonal_error = max(
            center_diagonal_fraction - target_diagonal_lower,
            target_diagonal_upper - center_diagonal_fraction,
        )
        if diagonal_error < 0:
            raise F0VerificationFailure(HOLD_DELTA_LEDGER, "diagonal interval missed center")
        delta_q_rows.append(off_diagonal_error + diagonal_error)
        diagonal_target_bounds.append((target_diagonal_lower, target_diagonal_upper))

    minimum_rate = max(maximum_exit_upper, maximum_center_exit)
    if uniformization_rate is None:
        rate_value = _fraction_upper(minimum_rate)
        rate_fraction = Fraction.from_float(rate_value)
    else:
        rate_fraction = _require_fraction(uniformization_rate, "uniformization rate")
        rate_value = _fraction_centre(rate_fraction)
        if Fraction.from_float(rate_value) != rate_fraction:
            raise F0VerificationFailure(
                HOLD_RATE_TOO_LOW,
                "uniformization rate must be exactly representable in binary64",
            )
    if rate_fraction <= 0 or rate_fraction < minimum_rate:
        raise F0VerificationFailure(HOLD_RATE_TOO_LOW, "uniformization rate misses an exit bound")

    p_forward: list[np.ndarray] = []
    p_backward: list[np.ndarray] = []
    for forward, backward in zip(forward_center, backward_center, strict=True):
        p_forward.append(
            np.asarray(
                [
                    _fraction_lower(Fraction.from_float(float(value)) / rate_fraction)
                    for value in forward
                ],
                dtype=np.float64,
            )
        )
        p_backward.append(
            np.asarray(
                [
                    _fraction_lower(Fraction.from_float(float(value)) / rate_fraction)
                    for value in backward
                ],
                dtype=np.float64,
            )
        )
    p_self = np.asarray(
        [
            _fraction_lower(Fraction(1) + Fraction.from_float(float(value)) / rate_fraction)
            for value in diagonal_center
        ],
        dtype=np.float64,
    )
    if np.min(p_self, initial=0.0) < 0.0:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "uniformized self coefficient is negative")

    delta_p_direct_rows: list[Fraction] = []
    p_rounding_rows: list[Fraction] = []
    maximum_center_row_sum = Fraction(0)
    maximum_qhat_abs_row_sum = Fraction(0)
    for flat, coordinate in enumerate(product(*(range(size) for size in shape))):
        direct_error = Fraction(0)
        rounding_error = Fraction(0)
        center_row_sum = Fraction.from_float(float(p_self[flat]))
        qhat_abs_row_sum = -Fraction.from_float(float(diagonal_center[flat]))
        for interval, dimension, direction in _outgoing_for_coordinate(axis_tuple, coordinate):
            index = coordinate[dimension]
            q_center_array = (
                forward_center[dimension] if direction == "forward" else backward_center[dimension]
            )
            p_center_array = (
                p_forward[dimension] if direction == "forward" else p_backward[dimension]
            )
            q_center = Fraction.from_float(float(q_center_array[index]))
            p_center_value = Fraction.from_float(float(p_center_array[index]))
            target_lower = interval.lower_fraction / rate_fraction
            target_upper = interval.upper_fraction / rate_fraction
            direct_error += max(p_center_value - target_lower, target_upper - p_center_value)
            rounding_error += abs(q_center / rate_fraction - p_center_value)
            center_row_sum += p_center_value
            qhat_abs_row_sum += q_center
        diagonal_lower, diagonal_upper = diagonal_target_bounds[flat]
        target_self_lower = Fraction(1) + diagonal_lower / rate_fraction
        target_self_upper = Fraction(1) + diagonal_upper / rate_fraction
        p_self_fraction = Fraction.from_float(float(p_self[flat]))
        direct_error += max(
            p_self_fraction - target_self_lower,
            target_self_upper - p_self_fraction,
        )
        exact_qhat_self = (
            Fraction(1) + Fraction.from_float(float(diagonal_center[flat])) / rate_fraction
        )
        rounding_error += abs(exact_qhat_self - p_self_fraction)
        if center_row_sum > 1 or center_row_sum < 0:
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "Phat row is not substochastic")
        maximum_center_row_sum = max(maximum_center_row_sum, center_row_sum)
        maximum_qhat_abs_row_sum = max(maximum_qhat_abs_row_sum, qhat_abs_row_sum)
        delta_p_direct_rows.append(direct_error)
        p_rounding_rows.append(rounding_error)

    delta_q_exact = max(delta_q_rows, default=Fraction(0))
    p_rounding_exact = max(p_rounding_rows, default=Fraction(0))
    delta_p_direct_exact = max(delta_p_direct_rows, default=Fraction(0))
    delta_p_via_q_exact = delta_q_exact / rate_fraction + p_rounding_exact
    if delta_p_direct_exact > delta_p_via_q_exact:
        raise F0VerificationFailure(
            HOLD_DELTA_LEDGER,
            "direct delta_P exceeds the independent delta_Q/lambda ledger",
        )
    delta_p_exact = min(delta_p_direct_exact, delta_p_via_q_exact)
    killing_inf_upper_exact = max(
        (interval.upper_fraction for interval in killing),
        default=Fraction(0),
    )
    killing_inf_uncertainty_exact = max(
        (
            interval.radius_about(float(center))
            for interval, center in zip(killing, killing_center, strict=True)
        ),
        default=Fraction(0),
    )
    maximum_terms = 1 + 2 * len(axis_tuple)
    kernel = RateDefinedTensorKernel(
        axes=axis_tuple,
        shape=shape,
        killing_intervals=killing,
        killing_center=killing_center,
        forward_center=forward_center,
        backward_center=backward_center,
        diagonal_center=diagonal_center,
        p_forward_center=tuple(p_forward),
        p_backward_center=tuple(p_backward),
        p_self_center=p_self,
        rate=rate_value,
        rate_fraction=rate_fraction,
        delta_q=_fraction_upper(delta_q_exact),
        delta_q_exact=delta_q_exact,
        delta_p=_fraction_upper(delta_p_exact),
        delta_p_exact=delta_p_exact,
        delta_p_direct_exact=delta_p_direct_exact,
        delta_p_via_q_exact=delta_p_via_q_exact,
        p_coefficient_rounding_exact=p_rounding_exact,
        maximum_target_exit_upper=_fraction_upper(maximum_exit_upper),
        maximum_center_row_sum=_fraction_upper(maximum_center_row_sum),
        maximum_qhat_abs_row_sum=_fraction_upper(maximum_qhat_abs_row_sum),
        maximum_qhat_abs_row_sum_exact=maximum_qhat_abs_row_sum,
        killing_inf_upper=_fraction_upper(killing_inf_upper_exact),
        killing_inf_uncertainty=_fraction_upper(killing_inf_uncertainty_exact),
        killing_inf_uncertainty_exact=killing_inf_uncertainty_exact,
        maximum_incoming_terms=maximum_terms,
        maximum_floating_ops_per_output=2 * maximum_terms - 1,
        roundoff_gamma_index=2 * maximum_terms,
        construction="rate_defined_tensor_sg_periodic_doi_v1",
    )
    validate_rate_defined_tensor_kernel(kernel)
    return kernel


def _expected_p_centers(
    kernel: RateDefinedTensorKernel,
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...], np.ndarray]:
    forward = tuple(
        np.asarray(
            [
                _fraction_lower(Fraction.from_float(float(value)) / kernel.rate_fraction)
                for value in row
            ],
            dtype=np.float64,
        )
        for row in kernel.forward_center
    )
    backward = tuple(
        np.asarray(
            [
                _fraction_lower(Fraction.from_float(float(value)) / kernel.rate_fraction)
                for value in row
            ],
            dtype=np.float64,
        )
        for row in kernel.backward_center
    )
    self_values = np.asarray(
        [
            _fraction_lower(Fraction(1) + Fraction.from_float(float(value)) / kernel.rate_fraction)
            for value in kernel.diagonal_center
        ],
        dtype=np.float64,
    )
    return forward, backward, self_values


def validate_rate_defined_tensor_kernel(kernel: RateDefinedTensorKernel) -> None:
    """Recompute structural identities and reject mutated ledgers/rows."""

    try:
        reference.verify_binary64_runtime()
    except reference.VerificationFailure as error:
        raise F0VerificationFailure(HOLD_ROUNDING, str(error)) from error
    if kernel.construction != "rate_defined_tensor_sg_periodic_doi_v1":
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "kernel construction tag is invalid")
    if kernel.shape != tuple(axis.size for axis in kernel.axes):
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "kernel tensor shape is invalid")
    if len(kernel.killing_intervals) != kernel.states:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "kernel killing shape is invalid")
    expected_terms = 1 + 2 * len(kernel.axes)
    if (
        kernel.maximum_incoming_terms != expected_terms
        or kernel.maximum_floating_ops_per_output != 2 * expected_terms - 1
        or kernel.roundoff_gamma_index != 2 * expected_terms
        or (len(kernel.axes) == 3 and expected_terms != FROZEN_MAXIMUM_INCOMING_TERMS_3D)
        or (
            len(kernel.axes) == 3
            and 2 * expected_terms - 1 != FROZEN_MAXIMUM_FLOATING_OPS_PER_OUTPUT_3D
        )
    ):
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "incoming-degree/op-count contract changed")
    if Fraction.from_float(kernel.rate) != kernel.rate_fraction or kernel.rate_fraction <= 0:
        raise F0VerificationFailure(HOLD_RATE_TOO_LOW, "kernel rate bytes are inconsistent")
    if Fraction.from_float(kernel.delta_q) < kernel.delta_q_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "delta_Q is understated")
    if Fraction.from_float(kernel.delta_p) < kernel.delta_p_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "delta_P is understated")
    if kernel.delta_p_exact != min(
        kernel.delta_p_direct_exact,
        kernel.delta_p_via_q_exact,
    ):
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "delta_P branches are inconsistent")

    for axis, actual_forward, actual_backward in zip(
        kernel.axes,
        kernel.forward_center,
        kernel.backward_center,
        strict=True,
    ):
        expected_axis_forward, expected_axis_backward = _axis_centers(axis)
        if not np.array_equal(actual_forward, expected_axis_forward):
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "forward Qhat rate mutated")
        if not np.array_equal(actual_backward, expected_axis_backward):
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "backward Qhat rate mutated")
    expected_killing_center = np.asarray(
        [interval.centre() for interval in kernel.killing_intervals],
        dtype=np.float64,
    )
    if not np.array_equal(kernel.killing_center, expected_killing_center):
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "Doi killing centre mutated")

    expected_forward, expected_backward, expected_self = _expected_p_centers(kernel)
    for actual, expected in zip(kernel.p_forward_center, expected_forward, strict=True):
        if not np.array_equal(actual, expected):
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "forward Phat coefficient mutated")
    for actual, expected in zip(kernel.p_backward_center, expected_backward, strict=True):
        if not np.array_equal(actual, expected):
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "backward Phat coefficient mutated")
    if not np.array_equal(kernel.p_self_center, expected_self):
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "self Phat coefficient mutated")

    recomputed_delta_q = Fraction(0)
    recomputed_delta_p = Fraction(0)
    maximum_exit = Fraction(0)
    maximum_row_sum = Fraction(0)
    maximum_p_rounding = Fraction(0)
    maximum_qhat_abs_row_sum = Fraction(0)
    maximum_killing_upper = Fraction(0)
    maximum_killing_uncertainty = Fraction(0)
    for flat, coordinate in enumerate(product(*(range(size) for size in kernel.shape))):
        rate_lower = Fraction(0)
        rate_upper = Fraction(0)
        rate_center = Fraction(0)
        q_error = Fraction(0)
        p_error = Fraction(0)
        p_rounding = Fraction(0)
        row_sum = Fraction.from_float(float(kernel.p_self_center[flat]))
        for interval, dimension, direction in _outgoing_for_coordinate(kernel.axes, coordinate):
            index = coordinate[dimension]
            q_values = (
                kernel.forward_center[dimension]
                if direction == "forward"
                else kernel.backward_center[dimension]
            )
            p_values = (
                kernel.p_forward_center[dimension]
                if direction == "forward"
                else kernel.p_backward_center[dimension]
            )
            q_value = float(q_values[index])
            p_value = Fraction.from_float(float(p_values[index]))
            rate_lower += interval.lower_fraction
            rate_upper += interval.upper_fraction
            rate_center += Fraction.from_float(q_value)
            q_error += interval.radius_about(q_value)
            p_error += max(
                p_value - interval.lower_fraction / kernel.rate_fraction,
                interval.upper_fraction / kernel.rate_fraction - p_value,
            )
            p_rounding += abs(Fraction.from_float(q_value) / kernel.rate_fraction - p_value)
            row_sum += p_value
        kill = kernel.killing_intervals[flat]
        kill_center = Fraction.from_float(float(kernel.killing_center[flat]))
        exit_lower = rate_lower + kill.lower_fraction
        exit_upper = rate_upper + kill.upper_fraction
        center_exit = rate_center + kill_center
        expected_diagonal = _fraction_lower(-center_exit)
        if float(kernel.diagonal_center[flat]) != expected_diagonal:
            raise F0VerificationFailure(
                HOLD_ROW_STRUCTURE, "diagonal is not derived from rates+killing"
            )
        diagonal_fraction = Fraction.from_float(expected_diagonal)
        q_error += max(diagonal_fraction + exit_upper, -exit_lower - diagonal_fraction)
        target_self_lower = Fraction(1) - exit_upper / kernel.rate_fraction
        target_self_upper = Fraction(1) - exit_lower / kernel.rate_fraction
        self_value = Fraction.from_float(float(kernel.p_self_center[flat]))
        p_error += max(self_value - target_self_lower, target_self_upper - self_value)
        p_rounding += abs(Fraction(1) + diagonal_fraction / kernel.rate_fraction - self_value)
        if diagonal_fraction + rate_center > 0:
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "Qhat row is super-stochastic")
        if row_sum < 0 or row_sum > 1:
            raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "Phat row is super-stochastic")
        maximum_exit = max(maximum_exit, exit_upper)
        maximum_row_sum = max(maximum_row_sum, row_sum)
        maximum_qhat_abs_row_sum = max(
            maximum_qhat_abs_row_sum,
            -diagonal_fraction + rate_center,
        )
        maximum_killing_upper = max(maximum_killing_upper, kill.upper_fraction)
        maximum_killing_uncertainty = max(
            maximum_killing_uncertainty,
            kill.radius_about(float(kernel.killing_center[flat])),
        )
        recomputed_delta_q = max(recomputed_delta_q, q_error)
        recomputed_delta_p = max(recomputed_delta_p, p_error)
        maximum_p_rounding = max(maximum_p_rounding, p_rounding)
    if kernel.rate_fraction < maximum_exit:
        raise F0VerificationFailure(HOLD_RATE_TOO_LOW, "rate is below target exit interval")
    if recomputed_delta_q != kernel.delta_q_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "delta_Q exact ledger mutated")
    if recomputed_delta_p != kernel.delta_p_direct_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "direct delta_P ledger mutated")
    recomputed_via_q = recomputed_delta_q / kernel.rate_fraction + maximum_p_rounding
    if maximum_p_rounding != kernel.p_coefficient_rounding_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "Phat rounding ledger mutated")
    if recomputed_via_q != kernel.delta_p_via_q_exact:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "delta_Q/lambda delta_P ledger mutated")
    if kernel.delta_p_exact != min(recomputed_delta_p, recomputed_via_q):
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "selected delta_P ledger mutated")
    if Fraction.from_float(kernel.maximum_target_exit_upper) < maximum_exit:
        raise F0VerificationFailure(HOLD_RATE_TOO_LOW, "target exit upper bound is understated")
    if Fraction.from_float(kernel.maximum_center_row_sum) < maximum_row_sum:
        raise F0VerificationFailure(HOLD_ROW_STRUCTURE, "center row-sum bound is understated")
    if kernel.maximum_qhat_abs_row_sum_exact != maximum_qhat_abs_row_sum:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "Qhat absolute-row ledger mutated")
    if Fraction.from_float(kernel.maximum_qhat_abs_row_sum) < maximum_qhat_abs_row_sum:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "Qhat absolute-row bound understated")
    if Fraction.from_float(kernel.killing_inf_upper) < maximum_killing_upper:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "killing infinity bound understated")
    if kernel.killing_inf_uncertainty_exact != maximum_killing_uncertainty:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "killing uncertainty ledger mutated")
    if Fraction.from_float(kernel.killing_inf_uncertainty) < maximum_killing_uncertainty:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "killing uncertainty understated")


def _flat_index(coordinate: tuple[int, ...], shape: tuple[int, ...]) -> int:
    return int(np.ravel_multi_index(coordinate, shape, order="C"))


def explicit_q_csr(kernel: RateDefinedTensorKernel) -> sparse.csr_matrix:
    """Small-grid oracle for the derived Qhat centre."""

    validate_rate_defined_tensor_kernel(kernel)
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    for coordinate in product(*(range(size) for size in kernel.shape)):
        row = _flat_index(coordinate, kernel.shape)
        for dimension, (axis, index) in enumerate(zip(kernel.axes, coordinate, strict=True)):
            if axis.forward_rates[index].upper > 0.0:
                target = list(coordinate)
                target[dimension] = (index + 1) % axis.size
                rows.append(row)
                columns.append(_flat_index(tuple(target), kernel.shape))
                values.append(float(kernel.forward_center[dimension][index]))
            if axis.backward_rates[index].upper > 0.0:
                target = list(coordinate)
                target[dimension] = (index - 1) % axis.size
                rows.append(row)
                columns.append(_flat_index(tuple(target), kernel.shape))
                values.append(float(kernel.backward_center[dimension][index]))
        rows.append(row)
        columns.append(row)
        values.append(float(kernel.diagonal_center[row]))
    matrix = sparse.csr_matrix((values, (rows, columns)), shape=(kernel.states, kernel.states))
    matrix.sum_duplicates()
    matrix.sort_indices()
    return matrix


def explicit_p_csr(kernel: RateDefinedTensorKernel) -> sparse.csr_matrix:
    """Small-grid oracle for the nonnegative Phat centre."""

    validate_rate_defined_tensor_kernel(kernel)
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    for coordinate in product(*(range(size) for size in kernel.shape)):
        row = _flat_index(coordinate, kernel.shape)
        for dimension, (axis, index) in enumerate(zip(kernel.axes, coordinate, strict=True)):
            if axis.forward_rates[index].upper > 0.0:
                target = list(coordinate)
                target[dimension] = (index + 1) % axis.size
                rows.append(row)
                columns.append(_flat_index(tuple(target), kernel.shape))
                values.append(float(kernel.p_forward_center[dimension][index]))
            if axis.backward_rates[index].upper > 0.0:
                target = list(coordinate)
                target[dimension] = (index - 1) % axis.size
                rows.append(row)
                columns.append(_flat_index(tuple(target), kernel.shape))
                values.append(float(kernel.p_backward_center[dimension][index]))
        rows.append(row)
        columns.append(row)
        values.append(float(kernel.p_self_center[row]))
    matrix = sparse.csr_matrix((values, (rows, columns)), shape=(kernel.states, kernel.states))
    matrix.sum_duplicates()
    matrix.sort_indices()
    return matrix


def _incoming_term(
    values: np.ndarray,
    rates: np.ndarray,
    *,
    axis: int,
    direction: str,
    periodic: bool,
) -> np.ndarray:
    shape = [1] * values.ndim
    shape[axis] = rates.size
    product_values = np.multiply(values, rates.reshape(shape), dtype=np.float64)
    if periodic:
        shift = 1 if direction == "forward" else -1
        return np.roll(product_values, shift=shift, axis=axis)
    result = np.zeros_like(values)
    target = [slice(None)] * values.ndim
    source = [slice(None)] * values.ndim
    if direction == "forward":
        target[axis] = slice(1, None)
        source[axis] = slice(None, -1)
    else:
        target[axis] = slice(None, -1)
        source[axis] = slice(1, None)
    result[tuple(target)] = product_values[tuple(source)]
    return result


def _pairwise_array_sum(terms: Sequence[np.ndarray]) -> np.ndarray:
    work = [np.asarray(term, dtype=np.float64) for term in terms]
    if not work:
        raise F0VerificationFailure(HOLD_ACTION, "empty array reduction")
    while len(work) > 1:
        reduced = [
            np.add(work[index], work[index + 1], dtype=np.float64)
            for index in range(0, len(work) - 1, 2)
        ]
        if len(work) % 2:
            reduced.append(work[-1])
        work = reduced
    return work[0]


def _matrix_free_p_transpose(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
    *,
    check_runtime: bool,
) -> np.ndarray:
    if check_runtime:
        validate_rate_defined_tensor_kernel(kernel)
    vector = np.asarray(state, dtype=np.float64).reshape(-1)
    if (
        vector.shape != (kernel.states,)
        or not np.all(np.isfinite(vector))
        or np.min(vector, initial=0.0) < 0.0
    ):
        raise F0VerificationFailure(HOLD_ACTION, "matrix-free state is malformed")
    shaped = vector.reshape(kernel.shape, order="C")
    terms = [
        np.multiply(shaped, kernel.p_self_center.reshape(kernel.shape, order="C"), dtype=np.float64)
    ]
    for dimension, axis in enumerate(kernel.axes):
        terms.append(
            _incoming_term(
                shaped,
                kernel.p_forward_center[dimension],
                axis=dimension,
                direction="forward",
                periodic=axis.periodic,
            )
        )
        terms.append(
            _incoming_term(
                shaped,
                kernel.p_backward_center[dimension],
                axis=dimension,
                direction="backward",
                periodic=axis.periodic,
            )
        )
    if len(terms) != kernel.maximum_incoming_terms:
        raise F0VerificationFailure(HOLD_ACTION, "incoming-term count changed")
    result = _pairwise_array_sum(terms).reshape(-1, order="C")
    if not np.all(np.isfinite(result)) or np.min(result, initial=0.0) < 0.0:
        raise F0VerificationFailure(HOLD_ACTION, "matrix-free Phat action lost nonnegativity")
    return result


def matrix_free_p_transpose(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
) -> np.ndarray:
    """Apply Phat.T with a frozen pairwise incoming-contribution tree."""

    return _matrix_free_p_transpose(kernel, state, check_runtime=True)


def _matrix_free_q_transpose(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
    *,
    check_runtime: bool,
) -> np.ndarray:
    if check_runtime:
        validate_rate_defined_tensor_kernel(kernel)
    vector = np.asarray(state, dtype=np.float64).reshape(-1)
    if vector.shape != (kernel.states,) or not np.all(np.isfinite(vector)):
        raise F0VerificationFailure(HOLD_ACTION, "matrix-free generator state is malformed")
    shaped = vector.reshape(kernel.shape, order="C")
    terms = [
        np.multiply(
            shaped,
            kernel.diagonal_center.reshape(kernel.shape, order="C"),
            dtype=np.float64,
        )
    ]
    for dimension, axis in enumerate(kernel.axes):
        terms.append(
            _incoming_term(
                shaped,
                kernel.forward_center[dimension],
                axis=dimension,
                direction="forward",
                periodic=axis.periodic,
            )
        )
        terms.append(
            _incoming_term(
                shaped,
                kernel.backward_center[dimension],
                axis=dimension,
                direction="backward",
                periodic=axis.periodic,
            )
        )
    if len(terms) != kernel.maximum_incoming_terms:
        raise F0VerificationFailure(HOLD_ACTION, "generator incoming-term count changed")
    result = _pairwise_array_sum(terms).reshape(-1, order="C")
    if not np.all(np.isfinite(result)):
        raise F0VerificationFailure(HOLD_ACTION, "matrix-free Qhat action became nonfinite")
    return result


def matrix_free_q_transpose(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
) -> np.ndarray:
    """Apply Qhat.T with the same frozen pairwise tensor reduction tree."""

    return _matrix_free_q_transpose(kernel, state, check_runtime=True)


def matrix_free_action_roundoff_bound(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
) -> float:
    vector = np.asarray(state, dtype=np.float64).reshape(-1)
    if vector.shape != (kernel.states,) or np.min(vector, initial=0.0) < 0.0:
        raise F0VerificationFailure(HOLD_ACTION, "action-bound state is malformed")
    mass_upper = reference.l1_upper(vector)
    relative = reference._mul_up(
        reference._mul_up(
            reference.gamma(kernel.roundoff_gamma_index),
            kernel.maximum_center_row_sum,
        ),
        mass_upper,
    )
    absolute = kernel.states * (kernel.maximum_floating_ops_per_output + 2) * reference.FLOAT64_ETA
    return reference._add_up(relative, absolute)


def matrix_free_q_action_roundoff_bound(
    kernel: RateDefinedTensorKernel,
    state: Sequence[float],
) -> float:
    vector = np.asarray(state, dtype=np.float64).reshape(-1)
    if vector.shape != (kernel.states,) or not np.all(np.isfinite(vector)):
        raise F0VerificationFailure(HOLD_ACTION, "generator action-bound state is malformed")
    norm_upper = reference.l1_upper(vector)
    relative = reference._mul_up(
        reference._mul_up(
            reference.gamma(kernel.roundoff_gamma_index),
            kernel.maximum_qhat_abs_row_sum,
        ),
        norm_upper,
    )
    absolute = kernel.states * (kernel.maximum_floating_ops_per_output + 2) * reference.FLOAT64_ETA
    return reference._add_up(relative, absolute)


@dataclass(frozen=True)
class MatrixFreeChunkLedger:
    duration: Fraction
    mean: Fraction
    allocated_tail_tolerance: Fraction
    terms: int
    poisson_tail_upper: float
    precision_bits: int
    maximum_terms_cap: int
    roundoff_gamma_index: int
    delta_p_used: float
    propagated_power_error: float
    weight_error: float
    accumulation_roundoff: float
    output_l1_error: float


@dataclass(frozen=True)
class MatrixFreePropagation:
    nominal: np.ndarray
    l1_error: float
    exact_mass_cap: Fraction
    target_time: Fraction
    elapsed_time: Fraction
    initial_source_sha256: str
    initial_l1_error: float
    kernel_construction: str
    rate_fraction: Fraction
    runtime_rounding_mode: str
    mean_cap: Fraction
    total_tail_tolerance: Fraction
    precision_bits: int
    maximum_terms: int
    maximum_chunks: int
    chunk_count: int
    chunks: tuple[MatrixFreeChunkLedger, ...]


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _matrix_free_propagation_contract(
    kernel: RateDefinedTensorKernel,
    target_time: Fraction | int,
    mean_cap: Fraction | int,
    total_tail_tolerance: Fraction | int,
    precision_bits: int,
    maximum_terms: int,
    maximum_chunks: int,
) -> tuple[Fraction, Fraction, Fraction, int]:
    """Normalize and close the externally pinned propagation contract."""

    time = _require_fraction(target_time, "target time")
    cap = _require_fraction(mean_cap, "mean cap")
    tail = _require_fraction(total_tail_tolerance, "total tail tolerance")
    if (
        time < 0
        or cap <= 0
        or tail <= 0
        or tail >= 1
        or isinstance(precision_bits, bool)
        or not isinstance(precision_bits, int)
        or precision_bits < 96
        or isinstance(maximum_terms, bool)
        or not isinstance(maximum_terms, int)
        or maximum_terms < 1
        or isinstance(maximum_chunks, bool)
        or not isinstance(maximum_chunks, int)
        or maximum_chunks < 1
    ):
        raise F0VerificationFailure(HOLD_TIME, "propagation contract is invalid")
    total_mean = kernel.rate_fraction * time
    chunk_count = max(1, _ceil_fraction(total_mean / cap))
    if chunk_count > maximum_chunks:
        raise F0VerificationFailure(HOLD_RESOURCE, "uniformization chunk cap exceeded")
    return time, cap, tail, chunk_count


def propagate_matrix_free_absolute(
    kernel: RateDefinedTensorKernel,
    initial: InitialStateEnclosure,
    target_time: Fraction | int,
    *,
    mean_cap: Fraction | int = Fraction(500),
    total_tail_tolerance: Fraction | int = Fraction(1, 10**18),
    precision_bits: int = 192,
    maximum_terms: int = 200_000,
    maximum_chunks: int = 100_000,
) -> MatrixFreePropagation:
    """Direct-from-initial exact-time uniformization with matrix-free Phat.T."""

    validate_rate_defined_tensor_kernel(kernel)
    validate_initial_state_enclosure(initial, expected_states=kernel.states)
    time, cap, tail_tolerance, chunk_count = _matrix_free_propagation_contract(
        kernel,
        target_time,
        mean_cap,
        total_tail_tolerance,
        precision_bits,
        maximum_terms,
        maximum_chunks,
    )
    duration = time / chunk_count
    tail_each = tail_tolerance / chunk_count
    vector = np.asarray(initial.nominal, dtype=np.float64).copy()
    state_error = float(initial.l1_error)
    ledgers: list[MatrixFreeChunkLedger] = []
    elapsed = Fraction(0)

    for _ in range(chunk_count):
        mean = kernel.rate_fraction * duration
        try:
            probabilities = reference.poisson_enclosure(
                mean,
                tail_each,
                precision_bits=precision_bits,
                max_terms=maximum_terms,
            )
        except reference.VerificationFailure as error:
            raise F0VerificationFailure(HOLD_TAIL, str(error)) from error
        terms = int(probabilities.midpoint.size)
        accumulator = np.zeros_like(vector)
        power = vector.copy()
        power_error = state_error
        weighted_power_error = 0.0
        weight_error = 0.0
        absolute_accumulation = 0.0
        propagated_power_error = power_error
        for index in range(terms):
            mass_upper = reference.l1_upper(power)
            weight = float(probabilities.midpoint[index])
            accumulator = np.add(
                accumulator,
                np.multiply(weight, power, dtype=np.float64),
                dtype=np.float64,
            )
            weighted_power_error = reference._add_up(
                weighted_power_error,
                reference._mul_up(float(probabilities.upper[index]), power_error),
            )
            weight_error = reference._add_up(
                weight_error,
                reference._mul_up(float(probabilities.radius[index]), mass_upper),
            )
            absolute_accumulation = reference._add_up(
                absolute_accumulation,
                reference._mul_up(abs(weight), mass_upper),
            )
            propagated_power_error = max(propagated_power_error, power_error)
            if index + 1 < terms:
                action_error = matrix_free_action_roundoff_bound(kernel, power)
                coefficient_error = reference._mul_up(kernel.delta_p, mass_upper)
                power = _matrix_free_p_transpose(kernel, power, check_runtime=False)
                power_error = reference._add_up(
                    power_error,
                    coefficient_error,
                    action_error,
                )
        accumulation_gamma = reference.gamma(2 * terms)
        accumulation_underflow = kernel.states * (2 * terms + 1) * reference.FLOAT64_ETA
        accumulation_roundoff = reference._add_up(
            reference._mul_up(accumulation_gamma, absolute_accumulation),
            accumulation_underflow,
        )
        tail_error = reference._mul_up(
            probabilities.tail_upper,
            _fraction_upper(initial.exact_mass_cap),
        )
        output_error = reference._add_up(
            weighted_power_error,
            weight_error,
            accumulation_roundoff,
            tail_error,
        )
        if not np.all(np.isfinite(accumulator)) or not math.isfinite(output_error):
            raise F0VerificationFailure(HOLD_ACTION, "uniformization output is nonfinite")
        ledgers.append(
            MatrixFreeChunkLedger(
                duration=duration,
                mean=mean,
                allocated_tail_tolerance=tail_each,
                terms=terms,
                poisson_tail_upper=float(probabilities.tail_upper),
                precision_bits=precision_bits,
                maximum_terms_cap=maximum_terms,
                roundoff_gamma_index=kernel.roundoff_gamma_index,
                delta_p_used=kernel.delta_p,
                propagated_power_error=propagated_power_error,
                weight_error=weight_error,
                accumulation_roundoff=accumulation_roundoff,
                output_l1_error=output_error,
            )
        )
        vector = accumulator
        state_error = output_error
        elapsed += duration
    propagation = MatrixFreePropagation(
        nominal=vector,
        l1_error=state_error,
        exact_mass_cap=initial.exact_mass_cap,
        target_time=time,
        elapsed_time=elapsed,
        initial_source_sha256=initial.source_sha256,
        initial_l1_error=initial.l1_error,
        kernel_construction=kernel.construction,
        rate_fraction=kernel.rate_fraction,
        runtime_rounding_mode="FE_TONEAREST",
        mean_cap=cap,
        total_tail_tolerance=tail_tolerance,
        precision_bits=precision_bits,
        maximum_terms=maximum_terms,
        maximum_chunks=maximum_chunks,
        chunk_count=chunk_count,
        chunks=tuple(ledgers),
    )
    audit_matrix_free_propagation(
        kernel,
        initial,
        propagation,
        expected_target_time=time,
        expected_mean_cap=cap,
        expected_total_tail_tolerance=tail_tolerance,
        expected_precision_bits=precision_bits,
        expected_maximum_terms=maximum_terms,
        expected_maximum_chunks=maximum_chunks,
    )
    return propagation


def audit_matrix_free_propagation(
    kernel: RateDefinedTensorKernel,
    initial: InitialStateEnclosure,
    propagation: MatrixFreePropagation,
    *,
    expected_target_time: Fraction | int,
    expected_mean_cap: Fraction | int,
    expected_total_tail_tolerance: Fraction | int,
    expected_precision_bits: int,
    expected_maximum_terms: int,
    expected_maximum_chunks: int,
) -> None:
    """Replay every saved propagation byte from an external frozen contract.

    Structural self-consistency is insufficient here: a coherent mutation of
    the nominal state and every error field must still fail.  Consequently
    this verifier deliberately repeats the complete uniformization recurrence
    from the validated initial enclosure and compares the saved ledger and
    final state bit for bit.
    """

    validate_rate_defined_tensor_kernel(kernel)
    validate_initial_state_enclosure(initial, expected_states=kernel.states)
    time, cap, tail_tolerance, chunk_count = _matrix_free_propagation_contract(
        kernel,
        expected_target_time,
        expected_mean_cap,
        expected_total_tail_tolerance,
        expected_precision_bits,
        expected_maximum_terms,
        expected_maximum_chunks,
    )
    if (
        not isinstance(propagation, MatrixFreePropagation)
        or not isinstance(propagation.nominal, np.ndarray)
        or not isinstance(propagation.chunks, tuple)
        or not all(
            _is_strict_fraction(value)
            for value in (
                propagation.exact_mass_cap,
                propagation.target_time,
                propagation.elapsed_time,
                propagation.rate_fraction,
                propagation.mean_cap,
                propagation.total_tail_tolerance,
            )
        )
        or not all(
            _is_strict_float(value)
            for value in (
                propagation.l1_error,
                propagation.initial_l1_error,
            )
        )
        or not all(
            _is_strict_int(value)
            for value in (
                propagation.precision_bits,
                propagation.maximum_terms,
                propagation.maximum_chunks,
                propagation.chunk_count,
            )
        )
        or type(propagation.initial_source_sha256) is not str
        or type(propagation.kernel_construction) is not str
        or type(propagation.runtime_rounding_mode) is not str
    ):
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "saved propagation schema mutated")
    if propagation.runtime_rounding_mode != "FE_TONEAREST":
        raise F0VerificationFailure(HOLD_ROUNDING, "rounding-mode attestation is corrupted")
    if (
        propagation.initial_source_sha256 != initial.source_sha256
        or propagation.exact_mass_cap != initial.exact_mass_cap
        or propagation.initial_l1_error != initial.l1_error
        or propagation.kernel_construction != kernel.construction
        or propagation.rate_fraction != kernel.rate_fraction
    ):
        raise F0VerificationFailure(HOLD_INITIAL_MASS, "initial-law attestation mismatch")
    if (
        propagation.target_time != time
        or propagation.elapsed_time != time
        or propagation.mean_cap != cap
        or propagation.maximum_chunks != expected_maximum_chunks
        or propagation.chunk_count != chunk_count
        or len(propagation.chunks) != chunk_count
    ):
        raise F0VerificationFailure(HOLD_TIME, "saved propagation time/chunk contract mutated")
    if (
        propagation.total_tail_tolerance != tail_tolerance
        or propagation.precision_bits != expected_precision_bits
        or propagation.maximum_terms != expected_maximum_terms
    ):
        raise F0VerificationFailure(HOLD_TAIL, "saved Poisson contract mutated")
    if sum((chunk.duration for chunk in propagation.chunks), Fraction(0)) != time:
        raise F0VerificationFailure(HOLD_TIME, "chunk durations do not close exactly")
    duration = time / chunk_count
    tail_each = tail_tolerance / chunk_count
    vector = np.asarray(initial.nominal, dtype=np.float64).copy()
    state_error = float(initial.l1_error)
    elapsed = Fraction(0)

    for saved_chunk in propagation.chunks:
        if (
            not isinstance(saved_chunk, MatrixFreeChunkLedger)
            or not all(
                _is_strict_fraction(value)
                for value in (
                    saved_chunk.duration,
                    saved_chunk.mean,
                    saved_chunk.allocated_tail_tolerance,
                )
            )
            or not all(
                _is_strict_int(value)
                for value in (
                    saved_chunk.terms,
                    saved_chunk.precision_bits,
                    saved_chunk.maximum_terms_cap,
                    saved_chunk.roundoff_gamma_index,
                )
            )
            or not all(
                _is_strict_float(value)
                for value in (
                    saved_chunk.poisson_tail_upper,
                    saved_chunk.delta_p_used,
                    saved_chunk.propagated_power_error,
                    saved_chunk.weight_error,
                    saved_chunk.accumulation_roundoff,
                    saved_chunk.output_l1_error,
                )
            )
        ):
            raise F0VerificationFailure(HOLD_DELTA_LEDGER, "saved chunk schema mutated")
        mean = kernel.rate_fraction * duration
        try:
            probabilities = reference.poisson_enclosure(
                mean,
                tail_each,
                precision_bits=expected_precision_bits,
                max_terms=expected_maximum_terms,
            )
        except reference.VerificationFailure as error:
            raise F0VerificationFailure(HOLD_TAIL, str(error)) from error
        terms = int(probabilities.midpoint.size)
        accumulator = np.zeros_like(vector)
        power = vector.copy()
        power_error = state_error
        weighted_power_error = 0.0
        weight_error = 0.0
        absolute_accumulation = 0.0
        propagated_power_error = power_error
        for index in range(terms):
            mass_upper = reference.l1_upper(power)
            weight = float(probabilities.midpoint[index])
            accumulator = np.add(
                accumulator,
                np.multiply(weight, power, dtype=np.float64),
                dtype=np.float64,
            )
            weighted_power_error = reference._add_up(
                weighted_power_error,
                reference._mul_up(float(probabilities.upper[index]), power_error),
            )
            weight_error = reference._add_up(
                weight_error,
                reference._mul_up(float(probabilities.radius[index]), mass_upper),
            )
            absolute_accumulation = reference._add_up(
                absolute_accumulation,
                reference._mul_up(abs(weight), mass_upper),
            )
            propagated_power_error = max(propagated_power_error, power_error)
            if index + 1 < terms:
                action_error = matrix_free_action_roundoff_bound(kernel, power)
                coefficient_error = reference._mul_up(kernel.delta_p, mass_upper)
                power = _matrix_free_p_transpose(kernel, power, check_runtime=False)
                power_error = reference._add_up(
                    power_error,
                    coefficient_error,
                    action_error,
                )
        accumulation_gamma = reference.gamma(2 * terms)
        accumulation_underflow = kernel.states * (2 * terms + 1) * reference.FLOAT64_ETA
        accumulation_roundoff = reference._add_up(
            reference._mul_up(accumulation_gamma, absolute_accumulation),
            accumulation_underflow,
        )
        tail_error = reference._mul_up(
            probabilities.tail_upper,
            _fraction_upper(initial.exact_mass_cap),
        )
        output_error = reference._add_up(
            weighted_power_error,
            weight_error,
            accumulation_roundoff,
            tail_error,
        )
        if not np.all(np.isfinite(accumulator)) or not math.isfinite(output_error):
            raise F0VerificationFailure(HOLD_ACTION, "uniformization replay is nonfinite")

        if saved_chunk.duration != duration or saved_chunk.mean != mean:
            raise F0VerificationFailure(HOLD_TIME, "saved chunk time/mean mutated")
        if (
            saved_chunk.allocated_tail_tolerance != tail_each
            or saved_chunk.terms != terms
            or saved_chunk.poisson_tail_upper != float(probabilities.tail_upper)
            or saved_chunk.precision_bits != expected_precision_bits
            or saved_chunk.maximum_terms_cap != expected_maximum_terms
        ):
            raise F0VerificationFailure(HOLD_TAIL, "saved Poisson replay ledger mutated")
        if (
            saved_chunk.roundoff_gamma_index != kernel.roundoff_gamma_index
            or saved_chunk.delta_p_used != kernel.delta_p
            or saved_chunk.propagated_power_error != propagated_power_error
            or saved_chunk.weight_error != weight_error
            or saved_chunk.accumulation_roundoff != accumulation_roundoff
            or saved_chunk.output_l1_error != output_error
        ):
            raise F0VerificationFailure(HOLD_DELTA_LEDGER, "saved error replay ledger mutated")
        vector = accumulator
        state_error = output_error
        elapsed += duration

    if elapsed != time:
        raise F0VerificationFailure(HOLD_TIME, "replayed elapsed time does not close")
    if (
        propagation.nominal.shape != (kernel.states,)
        or propagation.nominal.dtype != np.float64
        or not np.all(np.isfinite(propagation.nominal))
        or np.min(propagation.nominal, initial=0.0) < 0.0
        or not math.isfinite(propagation.l1_error)
        or propagation.l1_error < 0.0
    ):
        raise F0VerificationFailure(HOLD_ACTION, "propagation output is malformed")
    if not np.array_equal(propagation.nominal, vector):
        raise F0VerificationFailure(HOLD_ACTION, "saved nominal state disagrees with replay")
    if propagation.l1_error != state_error:
        raise F0VerificationFailure(HOLD_DELTA_LEDGER, "saved state radius disagrees with replay")


@dataclass(frozen=True)
class MatrixFreeJetEnclosure:
    order: int
    nominal_action: np.ndarray
    action_l1_error: float
    action_l1_upper: float
    scalar_nominal: float
    scalar_radius: float
    scalar_lower: float
    scalar_upper: float
    m_upper: float


def enclose_matrix_free_jets(
    kernel: RateDefinedTensorKernel,
    initial: InitialStateEnclosure,
    propagation: MatrixFreePropagation,
    *,
    expected_target_time: Fraction | int,
    expected_mean_cap: Fraction | int,
    expected_total_tail_tolerance: Fraction | int,
    expected_precision_bits: int,
    expected_maximum_terms: int,
    expected_maximum_chunks: int,
    maximum_order: int = 4,
) -> tuple[MatrixFreeJetEnclosure, ...]:
    """Enclose Qhat actions, scalar jets, and local M_r through order four."""

    audit_matrix_free_propagation(
        kernel,
        initial,
        propagation,
        expected_target_time=expected_target_time,
        expected_mean_cap=expected_mean_cap,
        expected_total_tail_tolerance=expected_total_tail_tolerance,
        expected_precision_bits=expected_precision_bits,
        expected_maximum_terms=expected_maximum_terms,
        expected_maximum_chunks=expected_maximum_chunks,
    )
    if not isinstance(maximum_order, int) or not (0 <= maximum_order <= 8):
        raise F0VerificationFailure(HOLD_ACTION, "unsupported matrix-free jet order")
    if propagation.nominal.shape != (kernel.states,):
        raise F0VerificationFailure(HOLD_ACTION, "jet state shape is invalid")
    q_norm_upper = reference._add_up(kernel.maximum_qhat_abs_row_sum, kernel.delta_q)
    z = np.asarray(propagation.nominal, dtype=np.float64).copy()
    error = float(propagation.l1_error)
    rows: list[MatrixFreeJetEnclosure] = []
    for order in range(maximum_order + 1):
        z_norm = reference.l1_upper(z)
        scalar, dot_roundoff = reference.pairwise_dot(kernel.killing_center, z)
        scalar_radius = reference._add_up(
            dot_roundoff,
            reference._mul_up(kernel.killing_inf_upper, error),
            reference._mul_up(kernel.killing_inf_uncertainty, z_norm),
        )
        action_l1_upper = reference._add_up(z_norm, error)
        rows.append(
            MatrixFreeJetEnclosure(
                order=order,
                nominal_action=z.copy(),
                action_l1_error=error,
                action_l1_upper=action_l1_upper,
                scalar_nominal=scalar,
                scalar_radius=scalar_radius,
                scalar_lower=reference._down(scalar - scalar_radius),
                scalar_upper=reference._next_up_signed(scalar + scalar_radius),
                m_upper=reference._mul_up(kernel.killing_inf_upper, action_l1_upper),
            )
        )
        if order < maximum_order:
            sparse_roundoff = matrix_free_q_action_roundoff_bound(kernel, z)
            coefficient_error = reference._mul_up(kernel.delta_q, z_norm)
            error = reference._add_up(
                reference._mul_up(q_norm_upper, error),
                coefficient_error,
                sparse_roundoff,
            )
            z = _matrix_free_q_transpose(kernel, z, check_runtime=False)
    return tuple(rows)


def canonical_science_free_summary(
    kernel: RateDefinedTensorKernel,
    *,
    label: str,
) -> dict[str, Any]:
    """Return a JSON-safe method summary with no scientific observables."""

    validate_rate_defined_tensor_kernel(kernel)
    if not label.startswith("science_free_"):
        raise F0VerificationFailure(HOLD_CONTROL_SOURCE, "summary label is not science-free")
    structure = tensor_structure_certificate(kernel)
    return {
        "stage": "rate_defined_tensor_f0_method_only",
        "status": "PASS_F0_METHOD_OBJECT_ONLY",
        "label": label,
        "positive_budget_primary_control_evaluated": False,
        "prospective_control_values_read": False,
        "shape": list(kernel.shape),
        "states": kernel.states,
        "rate_hex": float(kernel.rate).hex(),
        "rate_exact": (f"{kernel.rate_fraction.numerator}/{kernel.rate_fraction.denominator}"),
        "delta_q_hex": float(kernel.delta_q).hex(),
        "delta_q_exact": (f"{kernel.delta_q_exact.numerator}/{kernel.delta_q_exact.denominator}"),
        "delta_p_hex": float(kernel.delta_p).hex(),
        "delta_p_exact": (f"{kernel.delta_p_exact.numerator}/{kernel.delta_p_exact.denominator}"),
        "delta_p_direct_exact": (
            f"{kernel.delta_p_direct_exact.numerator}/{kernel.delta_p_direct_exact.denominator}"
        ),
        "delta_p_via_q_exact": (
            f"{kernel.delta_p_via_q_exact.numerator}/{kernel.delta_p_via_q_exact.denominator}"
        ),
        "maximum_incoming_terms": kernel.maximum_incoming_terms,
        "maximum_floating_ops_per_output": kernel.maximum_floating_ops_per_output,
        "construction": kernel.construction,
        "structure_certificate": structure,
        "authorized_scientific_command": None,
    }


def tensor_structure_certificate(kernel: RateDefinedTensorKernel) -> dict[str, Any]:
    """Serialize the construction-level sub-Markov/reversibility proof facts."""

    validate_rate_defined_tensor_kernel(kernel)
    for axis in kernel.axes:
        verify_axis_detailed_balance(axis)
    return {
        "off_diagonal_rate_intervals_nonnegative": True,
        "doi_killing_intervals_nonnegative": True,
        "diagonal_derived_from_rates_plus_killing": True,
        "qhat_rows_nonpositive_exact_dyadic": True,
        "phat_entries_nonnegative_exact_dyadic": True,
        "phat_rows_substochastic_exact_dyadic": True,
        "axis_detailed_balance_by_sg_or_periodic_construction": True,
        "tensor_stationary_mass_strictly_positive": True,
        "dirichlet_form_nonpositive_by_conductances_and_killing": True,
        "half_volume_axes": [axis.name for axis in kernel.axes if axis.has_half_boundary_volumes],
        "periodic_shift_exact": {
            axis.name: f"{axis.periodic_shift.numerator}/{axis.periodic_shift.denominator}"
            for axis in kernel.axes
            if axis.periodic
        },
    }


def _signed_interval(
    lower: Fraction | int,
    upper: Fraction | int,
) -> OutwardInterval:
    return OutwardInterval.from_fraction_bounds(lower, upper)


def _interval_add(left: OutwardInterval, right: OutwardInterval) -> OutwardInterval:
    return _signed_interval(
        left.lower_fraction + right.lower_fraction,
        left.upper_fraction + right.upper_fraction,
    )


def _interval_negate(value: OutwardInterval) -> OutwardInterval:
    return _signed_interval(-value.upper_fraction, -value.lower_fraction)


def _interval_subtract(left: OutwardInterval, right: OutwardInterval) -> OutwardInterval:
    return _interval_add(left, _interval_negate(right))


def _interval_multiply(left: OutwardInterval, right: OutwardInterval) -> OutwardInterval:
    products = (
        left.lower_fraction * right.lower_fraction,
        left.lower_fraction * right.upper_fraction,
        left.upper_fraction * right.lower_fraction,
        left.upper_fraction * right.upper_fraction,
    )
    return _signed_interval(min(products), max(products))


def _interval_divide(left: OutwardInterval, right: OutwardInterval) -> OutwardInterval:
    if right.lower_fraction <= 0 <= right.upper_fraction:
        raise F0VerificationFailure(HOLD_NEWTON, "interval-Newton denominator contains zero")
    reciprocals = (
        Fraction(1, 1) / right.lower_fraction,
        Fraction(1, 1) / right.upper_fraction,
    )
    reciprocal = _signed_interval(min(reciprocals), max(reciprocals))
    return _interval_multiply(left, reciprocal)


def _interval_intersection(
    left: OutwardInterval,
    right: OutwardInterval,
    *,
    failure_code: str = HOLD_TOPOLOGY,
) -> OutwardInterval:
    lower = max(left.lower_fraction, right.lower_fraction)
    upper = min(left.upper_fraction, right.upper_fraction)
    if lower > upper:
        raise F0VerificationFailure(failure_code, "two rigorous interval consequences are disjoint")
    return _signed_interval(lower, upper)


def _interval_sign(value: OutwardInterval) -> int:
    if value.lower_fraction > 0:
        return 1
    if value.upper_fraction < 0:
        return -1
    return 0


@dataclass(frozen=True)
class TimeJetSample:
    """Direct absolute-time jets and local contraction bounds at one time."""

    time: Fraction
    jets: tuple[OutwardInterval, OutwardInterval, OutwardInterval, OutwardInterval]
    m2: Fraction
    m3: Fraction
    m4: Fraction
    direct_from_initial: bool = True

    def validate(self, expected_time: Fraction) -> None:
        if (
            self.time != expected_time
            or len(self.jets) != 4
            or min(self.m2, self.m3, self.m4) < 0
            or not self.direct_from_initial
        ):
            raise F0VerificationFailure(
                HOLD_TIME, "time-jet sample violates absolute-time contract"
            )


@dataclass(frozen=True)
class MatrixFreeAbsoluteTimeJetOracle:
    """Direct adapter from the validated matrix-free semigroup to time tiles."""

    kernel: RateDefinedTensorKernel
    initial: InitialStateEnclosure
    mean_cap: Fraction = Fraction(500)
    total_tail_tolerance: Fraction = Fraction(1, 10**18)
    precision_bits: int = 192
    maximum_terms: int = 200_000
    maximum_chunks: int = 100_000

    def __call__(self, time: Fraction) -> TimeJetSample:
        exact_time = _require_fraction(time, "time-jet oracle target")
        propagation = propagate_matrix_free_absolute(
            self.kernel,
            self.initial,
            exact_time,
            mean_cap=self.mean_cap,
            total_tail_tolerance=self.total_tail_tolerance,
            precision_bits=self.precision_bits,
            maximum_terms=self.maximum_terms,
            maximum_chunks=self.maximum_chunks,
        )
        jets = enclose_matrix_free_jets(
            self.kernel,
            self.initial,
            propagation,
            expected_target_time=exact_time,
            expected_mean_cap=self.mean_cap,
            expected_total_tail_tolerance=self.total_tail_tolerance,
            expected_precision_bits=self.precision_bits,
            expected_maximum_terms=self.maximum_terms,
            expected_maximum_chunks=self.maximum_chunks,
            maximum_order=4,
        )
        sample = TimeJetSample(
            time=exact_time,
            jets=(
                OutwardInterval(jets[0].scalar_lower, jets[0].scalar_upper),
                OutwardInterval(jets[1].scalar_lower, jets[1].scalar_upper),
                OutwardInterval(jets[2].scalar_lower, jets[2].scalar_upper),
                OutwardInterval(jets[3].scalar_lower, jets[3].scalar_upper),
            ),
            m2=Fraction.from_float(jets[2].m_upper),
            m3=Fraction.from_float(jets[3].m_upper),
            m4=Fraction.from_float(jets[4].m_upper),
            direct_from_initial=True,
        )
        sample.validate(exact_time)
        return sample


@dataclass(frozen=True)
class RootBand:
    role: str
    lower: Fraction
    upper: Fraction
    kind: str

    def validate(self) -> None:
        if not self.role or self.lower >= self.upper or self.kind not in {"maximum", "minimum"}:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "root band is malformed")


def physical_root_bands_v2(control_id: str) -> tuple[RootBand, ...]:
    """Return only the predeclared v2 role bands, never a control value."""

    bands = {
        "lp_m1": (RootBand("P1", Fraction(11, 2), Fraction(12), "maximum"),),
        "lp_m2": (
            RootBand("P1", Fraction(2), Fraction(11, 2), "maximum"),
            RootBand("Q1", Fraction(11, 2), Fraction(16), "minimum"),
            RootBand("P2", Fraction(16), Fraction(35), "maximum"),
        ),
        "lp_m3": (
            RootBand("P1", Fraction(2), Fraction(5), "maximum"),
            RootBand("Q1", Fraction(5), Fraction(13, 2), "minimum"),
            RootBand("P2", Fraction(13, 2), Fraction(11), "maximum"),
            RootBand("Q2", Fraction(11), Fraction(17), "minimum"),
            RootBand("P3", Fraction(17), Fraction(35), "maximum"),
        ),
    }
    try:
        selected = bands[control_id]
    except (KeyError, TypeError) as error:
        raise F0VerificationFailure(HOLD_CONTROL_SOURCE, "unknown v2 control role") from error
    for band in selected:
        band.validate()
    return selected


@dataclass(frozen=True)
class TimeTileCertificate:
    lower: Fraction
    upper: Fraction
    depth: int
    derivative: OutwardInterval
    curvature: OutwardInterval
    derivative_sign: int
    candidate: bool
    local_lipschitz_derivative: OutwardInterval
    local_taylor_derivative: OutwardInterval
    local_lipschitz_curvature: OutwardInterval
    local_taylor_curvature: OutwardInterval


@dataclass(frozen=True)
class IntervalNewtonStep:
    index: int
    input_lower: Fraction
    input_upper: Fraction
    midpoint: Fraction
    derivative_at_midpoint: OutwardInterval
    curvature_on_input: OutwardInterval
    newton_image: OutwardInterval
    inclusion_in_interior: bool
    output_lower: Fraction
    output_upper: Fraction


@dataclass(frozen=True)
class RootIntervalCertificate:
    role: str
    kind: str
    band_lower: Fraction
    band_upper: Fraction
    initial_cluster_lower: Fraction
    initial_cluster_upper: Fraction
    final_lower: Fraction
    final_upper: Fraction
    required_curvature_sign: int
    inclusion_observed: bool
    newton_steps: tuple[IntervalNewtonStep, ...]


@dataclass(frozen=True)
class FullWindowTopologyCertificate:
    window_lower: Fraction
    window_upper: Fraction
    initial_tile_width: Fraction
    maximum_bisection_depth: int
    maximum_newton_steps: int
    maximum_root_width: Fraction
    initial_derivative_sign: int
    tiles: tuple[TimeTileCertificate, ...]
    roots: tuple[RootIntervalCertificate, ...]
    complete_window_covered: bool
    unresolved_tiles: int
    prospective_control_values_read: bool
    positive_budget_primary_control_evaluated: bool


def _call_time_oracle(oracle: Any, time: Fraction) -> TimeJetSample:
    if not callable(oracle):
        raise F0VerificationFailure(HOLD_TIME, "time-jet oracle is not callable")
    sample = oracle(time)
    if not isinstance(sample, TimeJetSample):
        raise F0VerificationFailure(HOLD_TIME, "time-jet oracle returned the wrong type")
    sample.validate(time)
    return sample


def enclose_time_tile(
    oracle: Any,
    lower: Fraction | int,
    upper: Fraction | int,
    *,
    depth: int = 0,
) -> TimeTileCertificate:
    """Intersect the v2 local contraction and second-order Taylor enclosures."""

    lo = _require_fraction(lower, "time tile lower")
    hi = _require_fraction(upper, "time tile upper")
    if lo < 0 or lo >= hi or not isinstance(depth, int) or depth < 0:
        raise F0VerificationFailure(HOLD_TIME, "time tile is malformed")
    sample = _call_time_oracle(oracle, lo)
    delta = hi - lo
    j1 = sample.jets[1]
    j2 = sample.jets[2]
    j3 = sample.jets[3]
    derivative_lipschitz = _interval_add(
        j1,
        _signed_interval(-sample.m2 * delta, sample.m2 * delta),
    )
    curvature_lipschitz = _interval_add(
        j2,
        _signed_interval(-sample.m3 * delta, sample.m3 * delta),
    )
    time_interval = _signed_interval(0, delta)
    derivative_taylor = _interval_add(
        _interval_add(j1, _interval_multiply(time_interval, j2)),
        _signed_interval(
            -sample.m3 * delta * delta / 2,
            sample.m3 * delta * delta / 2,
        ),
    )
    curvature_taylor = _interval_add(
        _interval_add(j2, _interval_multiply(time_interval, j3)),
        _signed_interval(
            -sample.m4 * delta * delta / 2,
            sample.m4 * delta * delta / 2,
        ),
    )
    derivative = _interval_intersection(derivative_lipschitz, derivative_taylor)
    curvature = _interval_intersection(curvature_lipschitz, curvature_taylor)
    return TimeTileCertificate(
        lower=lo,
        upper=hi,
        depth=depth,
        derivative=derivative,
        curvature=curvature,
        derivative_sign=_interval_sign(derivative),
        candidate=False,
        local_lipschitz_derivative=derivative_lipschitz,
        local_taylor_derivative=derivative_taylor,
        local_lipschitz_curvature=curvature_lipschitz,
        local_taylor_curvature=curvature_taylor,
    )


def _quarter_tiles(
    lower: Fraction, upper: Fraction, width: Fraction
) -> tuple[tuple[Fraction, Fraction], ...]:
    if lower >= upper or width <= 0:
        raise F0VerificationFailure(HOLD_COVERAGE, "invalid initial tile segment")
    tiles: list[tuple[Fraction, Fraction]] = []
    left = lower
    while left < upper:
        right = min(upper, left + width)
        tiles.append((left, right))
        left = right
    return tuple(tiles)


def _adaptive_tile_segment(
    oracle: Any,
    lower: Fraction,
    upper: Fraction,
    *,
    initial_width: Fraction,
    maximum_depth: int,
    expected_sign: int | None,
    root_curvature_sign: int | None,
    candidate_width: Fraction,
) -> tuple[TimeTileCertificate, ...]:
    leaves: list[TimeTileCertificate] = []

    def visit(left: Fraction, right: Fraction, depth: int) -> None:
        tile = enclose_time_tile(oracle, left, right, depth=depth)
        if tile.derivative_sign:
            if expected_sign is not None and tile.derivative_sign != expected_sign:
                raise F0VerificationFailure(HOLD_TOPOLOGY, "complement derivative sign is wrong")
            leaves.append(tile)
            return
        curvature_sign = _interval_sign(tile.curvature)
        if (
            root_curvature_sign is not None
            and curvature_sign == root_curvature_sign
            and right - left <= candidate_width
        ):
            leaves.append(TimeTileCertificate(**{**tile.__dict__, "candidate": True}))
            return
        if depth >= maximum_depth:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "unresolved tile reached depth cap")
        midpoint = (left + right) / 2
        visit(left, midpoint, depth + 1)
        visit(midpoint, right, depth + 1)

    for left, right in _quarter_tiles(lower, upper, initial_width):
        visit(left, right, 0)
    return tuple(leaves)


def _newton_root_certificate(
    oracle: Any,
    band: RootBand,
    cluster_lower: Fraction,
    cluster_upper: Fraction,
    *,
    required_curvature_sign: int,
    maximum_steps: int,
    maximum_root_width: Fraction,
) -> RootIntervalCertificate:
    lower = cluster_lower
    upper = cluster_upper
    trace: list[IntervalNewtonStep] = []
    inclusion_observed = False
    for index in range(maximum_steps):
        midpoint = Fraction.from_float(float((lower + upper) / 2))
        if not lower < midpoint < upper:
            raise F0VerificationFailure(HOLD_NEWTON, "binary64 midpoint is not interior")
        sample = _call_time_oracle(oracle, midpoint)
        derivative_midpoint = sample.jets[1]
        curvature = enclose_time_tile(oracle, lower, upper).curvature
        if _interval_sign(curvature) != required_curvature_sign:
            raise F0VerificationFailure(HOLD_NEWTON, "root curvature sign is unresolved")
        quotient = _interval_divide(derivative_midpoint, curvature)
        newton = _interval_subtract(OutwardInterval.from_fraction(midpoint), quotient)
        inclusion = newton.lower_fraction > lower and newton.upper_fraction < upper
        inclusion_observed = inclusion_observed or inclusion
        current = _signed_interval(lower, upper)
        output = _interval_intersection(current, newton, failure_code=HOLD_NEWTON)
        trace.append(
            IntervalNewtonStep(
                index=index,
                input_lower=lower,
                input_upper=upper,
                midpoint=midpoint,
                derivative_at_midpoint=derivative_midpoint,
                curvature_on_input=curvature,
                newton_image=newton,
                inclusion_in_interior=inclusion,
                output_lower=output.lower_fraction,
                output_upper=output.upper_fraction,
            )
        )
        lower = output.lower_fraction
        upper = output.upper_fraction
    if not inclusion_observed:
        raise F0VerificationFailure(HOLD_NEWTON, "no interval-Newton interior inclusion occurred")
    if upper - lower > maximum_root_width:
        raise F0VerificationFailure(HOLD_NEWTON, "final root interval exceeds width cap")
    final_curvature = enclose_time_tile(oracle, lower, upper).curvature
    if _interval_sign(final_curvature) != required_curvature_sign:
        raise F0VerificationFailure(HOLD_NEWTON, "final root curvature sign is wrong")
    return RootIntervalCertificate(
        role=band.role,
        kind=band.kind,
        band_lower=band.lower,
        band_upper=band.upper,
        initial_cluster_lower=cluster_lower,
        initial_cluster_upper=cluster_upper,
        final_lower=lower,
        final_upper=upper,
        required_curvature_sign=required_curvature_sign,
        inclusion_observed=inclusion_observed,
        newton_steps=tuple(trace),
    )


def certify_full_window_topology(
    oracle: Any,
    *,
    window_lower: Fraction | int,
    window_upper: Fraction | int,
    root_bands: Sequence[RootBand],
    initial_derivative_sign: int = 1,
    initial_tile_width: Fraction = Fraction(1, 4),
    maximum_bisection_depth: int = 20,
    maximum_newton_steps: int = 12,
    maximum_root_width: Fraction = Fraction(1, 20),
) -> FullWindowTopologyCertificate:
    """Certify every time in a window by strict sign or one unique root box."""

    lower = _require_fraction(window_lower, "window lower")
    upper = _require_fraction(window_upper, "window upper")
    bands = tuple(root_bands)
    if (
        lower < 0
        or lower >= upper
        or initial_derivative_sign not in {-1, 1}
        or initial_tile_width != Fraction(1, 4)
        or maximum_bisection_depth != 20
        or maximum_newton_steps != 12
        or maximum_root_width != Fraction(1, 20)
        or not bands
    ):
        raise F0VerificationFailure(HOLD_TOPOLOGY, "full-window frozen limits are invalid")
    for band in bands:
        band.validate()
    if len({band.role for band in bands}) != len(bands):
        raise F0VerificationFailure(HOLD_TOPOLOGY, "root roles are duplicated")
    if any(
        band.lower < lower or band.upper > upper or (index and bands[index - 1].upper > band.lower)
        for index, band in enumerate(bands)
    ):
        raise F0VerificationFailure(HOLD_TOPOLOGY, "root bands overlap or leave the window")
    grid_points = (lower, upper) + tuple(
        endpoint for band in bands for endpoint in (band.lower, band.upper)
    )
    if any((point * 4).denominator != 1 for point in grid_points):
        raise F0VerificationFailure(
            HOLD_COVERAGE, "window/band endpoints are not quarter-grid dyadics"
        )

    tiles: list[TimeTileCertificate] = []
    roots: list[RootIntervalCertificate] = []
    cursor = lower
    current_sign = initial_derivative_sign
    for band in bands:
        if cursor < band.lower:
            tiles.extend(
                _adaptive_tile_segment(
                    oracle,
                    cursor,
                    band.lower,
                    initial_width=initial_tile_width,
                    maximum_depth=maximum_bisection_depth,
                    expected_sign=current_sign,
                    root_curvature_sign=None,
                    candidate_width=maximum_root_width / 2,
                )
            )
        required_curvature_sign = -1 if band.kind == "maximum" else 1
        if required_curvature_sign != -current_sign:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "root kind disagrees with sign sequence")
        band_tiles = _adaptive_tile_segment(
            oracle,
            band.lower,
            band.upper,
            initial_width=initial_tile_width,
            maximum_depth=maximum_bisection_depth,
            expected_sign=None,
            root_curvature_sign=required_curvature_sign,
            candidate_width=maximum_root_width / 2,
        )
        candidate_indices = [index for index, tile in enumerate(band_tiles) if tile.candidate]
        if not candidate_indices or candidate_indices != list(
            range(candidate_indices[0], candidate_indices[-1] + 1)
        ):
            raise F0VerificationFailure(
                HOLD_TOPOLOGY, "root band has zero or disconnected clusters"
            )
        first_candidate = candidate_indices[0]
        last_candidate = candidate_indices[-1]
        if any(tile.derivative_sign != current_sign for tile in band_tiles[:first_candidate]):
            raise F0VerificationFailure(HOLD_TOPOLOGY, "left root-complement sign is wrong")
        if any(tile.derivative_sign != -current_sign for tile in band_tiles[last_candidate + 1 :]):
            raise F0VerificationFailure(HOLD_TOPOLOGY, "right root-complement sign is wrong")
        cluster_lower = band_tiles[first_candidate].lower
        cluster_upper = band_tiles[last_candidate].upper
        if not band.lower < cluster_lower < cluster_upper < band.upper:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "root cluster touches its frozen band")
        root = _newton_root_certificate(
            oracle,
            band,
            cluster_lower,
            cluster_upper,
            required_curvature_sign=required_curvature_sign,
            maximum_steps=maximum_newton_steps,
            maximum_root_width=maximum_root_width,
        )
        roots.append(root)
        tiles.extend(band_tiles)
        current_sign = -current_sign
        cursor = band.upper
    if cursor < upper:
        tiles.extend(
            _adaptive_tile_segment(
                oracle,
                cursor,
                upper,
                initial_width=initial_tile_width,
                maximum_depth=maximum_bisection_depth,
                expected_sign=current_sign,
                root_curvature_sign=None,
                candidate_width=maximum_root_width / 2,
            )
        )
    ordered = sorted(tiles, key=lambda tile: (tile.lower, tile.upper))
    coverage_cursor = lower
    for tile in ordered:
        if tile.lower != coverage_cursor or tile.upper <= tile.lower:
            raise F0VerificationFailure(HOLD_COVERAGE, "time-tile ledger has a gap or overlap")
        coverage_cursor = tile.upper
    if coverage_cursor != upper:
        raise F0VerificationFailure(HOLD_COVERAGE, "time-tile ledger does not close the window")
    certificate = FullWindowTopologyCertificate(
        window_lower=lower,
        window_upper=upper,
        initial_tile_width=initial_tile_width,
        maximum_bisection_depth=maximum_bisection_depth,
        maximum_newton_steps=maximum_newton_steps,
        maximum_root_width=maximum_root_width,
        initial_derivative_sign=initial_derivative_sign,
        tiles=tuple(ordered),
        roots=tuple(roots),
        complete_window_covered=True,
        unresolved_tiles=0,
        prospective_control_values_read=False,
        positive_budget_primary_control_evaluated=False,
    )
    audit_full_window_topology(
        certificate,
        oracle=oracle,
        expected_window_lower=lower,
        expected_window_upper=upper,
        expected_root_bands=bands,
        expected_initial_derivative_sign=initial_derivative_sign,
    )
    return certificate


def certify_physical_full_window_topology_v2(
    oracle: Any,
    *,
    control_id: str,
) -> FullWindowTopologyCertificate:
    """Apply the immutable v2 ``[0.5,35]`` topology contract to an F0 oracle.

    This wrapper contains role bands and algorithmic limits only.  It has no
    selector-artifact path and therefore cannot inspect or evaluate a
    prospective control.
    """

    return certify_full_window_topology(
        oracle,
        window_lower=Fraction(1, 2),
        window_upper=Fraction(35),
        root_bands=physical_root_bands_v2(control_id),
        initial_derivative_sign=1,
        initial_tile_width=Fraction(1, 4),
        maximum_bisection_depth=20,
        maximum_newton_steps=12,
        maximum_root_width=Fraction(1, 20),
    )


def audit_full_window_topology(
    certificate: FullWindowTopologyCertificate,
    *,
    oracle: Any,
    expected_window_lower: Fraction | int,
    expected_window_upper: Fraction | int,
    expected_root_bands: Sequence[RootBand],
    expected_initial_derivative_sign: int,
) -> None:
    """Replay saved topology against immutable external bands and semantics."""

    lower = _require_fraction(expected_window_lower, "expected window lower")
    upper = _require_fraction(expected_window_upper, "expected window upper")
    bands = tuple(expected_root_bands)
    if (
        not isinstance(certificate, FullWindowTopologyCertificate)
        or lower < 0
        or lower >= upper
        or isinstance(expected_initial_derivative_sign, bool)
        or expected_initial_derivative_sign not in {-1, 1}
        or not bands
    ):
        raise F0VerificationFailure(HOLD_TOPOLOGY, "external topology contract is invalid")
    peak_count = 0
    trough_count = 0
    contract_sign = expected_initial_derivative_sign
    previous_upper = lower
    for band in bands:
        if (
            not isinstance(band, RootBand)
            or type(band.role) is not str
            or type(band.kind) is not str
            or not _is_strict_fraction(band.lower)
            or not _is_strict_fraction(band.upper)
        ):
            raise F0VerificationFailure(HOLD_TOPOLOGY, "external root band has wrong type")
        band.validate()
        if band.lower < previous_upper or band.upper > upper:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "external root bands overlap or escape")
        expected_kind = "maximum" if contract_sign == 1 else "minimum"
        if band.kind != expected_kind:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "external root kinds do not alternate")
        if band.kind == "maximum":
            peak_count += 1
            expected_role = f"P{peak_count}"
        else:
            trough_count += 1
            expected_role = f"Q{trough_count}"
        if band.role != expected_role:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "external root role sequence is invalid")
        previous_upper = band.upper
        contract_sign = -contract_sign
    grid_points = (lower, upper) + tuple(
        endpoint for band in bands for endpoint in (band.lower, band.upper)
    )
    if any((point * 4).denominator != 1 for point in grid_points):
        raise F0VerificationFailure(HOLD_COVERAGE, "external topology is off quarter grid")

    if (
        certificate.window_lower != lower
        or certificate.window_upper != upper
        or certificate.initial_derivative_sign != expected_initial_derivative_sign
        or not isinstance(certificate.tiles, tuple)
        or not isinstance(certificate.roots, tuple)
        or not all(
            _is_strict_fraction(value)
            for value in (
                certificate.window_lower,
                certificate.window_upper,
                certificate.initial_tile_width,
                certificate.maximum_root_width,
            )
        )
        or not all(
            _is_strict_int(value)
            for value in (
                certificate.maximum_bisection_depth,
                certificate.maximum_newton_steps,
                certificate.initial_derivative_sign,
                certificate.unresolved_tiles,
            )
        )
        or certificate.initial_tile_width != Fraction(1, 4)
        or certificate.maximum_bisection_depth != 20
        or certificate.maximum_newton_steps != 12
        or certificate.maximum_root_width != Fraction(1, 20)
        or certificate.complete_window_covered is not True
        or isinstance(certificate.unresolved_tiles, bool)
        or certificate.unresolved_tiles != 0
        or certificate.prospective_control_values_read is not False
        or certificate.positive_budget_primary_control_evaluated is not False
        or len(certificate.roots) != len(bands)
        or not certificate.tiles
    ):
        raise F0VerificationFailure(HOLD_TOPOLOGY, "topology certificate boundary mutated")

    cursor = lower
    component_indices: list[tuple[int, int]] = []
    component_start: int | None = None
    for index, tile in enumerate(certificate.tiles):
        if (
            not isinstance(tile, TimeTileCertificate)
            or not _is_strict_fraction(tile.lower)
            or not _is_strict_fraction(tile.upper)
            or not all(
                isinstance(value, OutwardInterval)
                for value in (
                    tile.derivative,
                    tile.curvature,
                    tile.local_lipschitz_derivative,
                    tile.local_taylor_derivative,
                    tile.local_lipschitz_curvature,
                    tile.local_taylor_curvature,
                )
            )
            or tile.lower != cursor
            or tile.upper <= tile.lower
            or isinstance(tile.depth, bool)
            or not isinstance(tile.depth, int)
            or not 0 <= tile.depth <= 20
            or tile.upper - tile.lower != Fraction(1, 4 * (2**tile.depth))
            or not isinstance(tile.candidate, bool)
            or isinstance(tile.derivative_sign, bool)
            or tile.derivative_sign not in {-1, 0, 1}
        ):
            raise F0VerificationFailure(HOLD_COVERAGE, "saved topology tile geometry mutated")
        recomputed_derivative = _interval_intersection(
            tile.local_lipschitz_derivative,
            tile.local_taylor_derivative,
        )
        recomputed_curvature = _interval_intersection(
            tile.local_lipschitz_curvature,
            tile.local_taylor_curvature,
        )
        replayed_tile = enclose_time_tile(
            oracle,
            tile.lower,
            tile.upper,
            depth=tile.depth,
        )
        curvature_sign = _interval_sign(recomputed_curvature)
        if (
            recomputed_derivative != tile.derivative
            or recomputed_curvature != tile.curvature
            or _interval_sign(recomputed_derivative) != tile.derivative_sign
            or replace(replayed_tile, candidate=tile.candidate) != tile
        ):
            raise F0VerificationFailure(
                HOLD_TOPOLOGY,
                "saved tile interval ledger disagrees with fresh oracle replay",
            )
        if tile.candidate:
            if (
                tile.derivative_sign != 0
                or curvature_sign not in {-1, 1}
                or tile.upper - tile.lower > Fraction(1, 40)
            ):
                raise F0VerificationFailure(HOLD_TOPOLOGY, "saved candidate semantics mutated")
            if component_start is None:
                component_start = index
        else:
            if tile.derivative_sign not in {-1, 1}:
                raise F0VerificationFailure(HOLD_TOPOLOGY, "saved complement is unresolved")
            if component_start is not None:
                component_indices.append((component_start, index - 1))
                component_start = None
        cursor = tile.upper
    if component_start is not None:
        component_indices.append((component_start, len(certificate.tiles) - 1))
    if cursor != upper or len(component_indices) != len(bands):
        raise F0VerificationFailure(HOLD_COVERAGE, "saved root/coverage count is inconsistent")

    current_sign = expected_initial_derivative_sign
    previous_component_end = -1
    for root_index, ((start, end), root, band) in enumerate(
        zip(component_indices, certificate.roots, bands, strict=True)
    ):
        if (
            not isinstance(root, RootIntervalCertificate)
            or type(root.role) is not str
            or type(root.kind) is not str
            or not all(
                _is_strict_fraction(value)
                for value in (
                    root.band_lower,
                    root.band_upper,
                    root.initial_cluster_lower,
                    root.initial_cluster_upper,
                    root.final_lower,
                    root.final_upper,
                )
            )
            or not _is_strict_int(root.required_curvature_sign)
            or type(root.inclusion_observed) is not bool
        ):
            raise F0VerificationFailure(HOLD_TOPOLOGY, "saved root schema mutated")
        for tile in certificate.tiles[previous_component_end + 1 : start]:
            if tile.derivative_sign != current_sign:
                raise F0VerificationFailure(HOLD_TOPOLOGY, "complement sign sequence mutated")
        component = certificate.tiles[start : end + 1]
        cluster_lower = component[0].lower
        cluster_upper = component[-1].upper
        required_curvature_sign = -current_sign
        expected_kind = "maximum" if required_curvature_sign == -1 else "minimum"
        if (
            root.role != band.role
            or root.kind != band.kind
            or root.kind != expected_kind
            or root.band_lower != band.lower
            or root.band_upper != band.upper
            or root.initial_cluster_lower != cluster_lower
            or root.initial_cluster_upper != cluster_upper
            or root.required_curvature_sign != required_curvature_sign
            or not band.lower < cluster_lower < cluster_upper < band.upper
            or any(_interval_sign(tile.curvature) != required_curvature_sign for tile in component)
        ):
            raise F0VerificationFailure(HOLD_TOPOLOGY, "saved root semantics/band binding mutated")
        if (
            not isinstance(root.newton_steps, tuple)
            or len(root.newton_steps) != 12
            or root.inclusion_observed is not True
            or root.final_upper - root.final_lower > Fraction(1, 20)
            or not cluster_lower <= root.final_lower < root.final_upper <= cluster_upper
            or any(step.index != index for index, step in enumerate(root.newton_steps))
            or root.newton_steps[-1].output_lower != root.final_lower
            or root.newton_steps[-1].output_upper != root.final_upper
        ):
            raise F0VerificationFailure(HOLD_NEWTON, "saved interval-Newton trace mutated")
        previous_lower = cluster_lower
        previous_upper = cluster_upper
        inclusion_observed = False
        for index, step in enumerate(root.newton_steps):
            if (
                not isinstance(step, IntervalNewtonStep)
                or not _is_strict_int(step.index)
                or not all(
                    _is_strict_fraction(value)
                    for value in (
                        step.input_lower,
                        step.input_upper,
                        step.midpoint,
                        step.output_lower,
                        step.output_upper,
                    )
                )
                or not all(
                    isinstance(value, OutwardInterval)
                    for value in (
                        step.derivative_at_midpoint,
                        step.curvature_on_input,
                        step.newton_image,
                    )
                )
                or type(step.inclusion_in_interior) is not bool
            ):
                raise F0VerificationFailure(HOLD_NEWTON, "saved Newton step schema mutated")
            midpoint = Fraction.from_float(float((previous_lower + previous_upper) / 2))
            midpoint_sample = _call_time_oracle(oracle, midpoint)
            replayed_curvature = enclose_time_tile(
                oracle,
                previous_lower,
                previous_upper,
            ).curvature
            if (
                step.index != index
                or step.input_lower != previous_lower
                or step.input_upper != previous_upper
                or step.midpoint != midpoint
                or step.derivative_at_midpoint != midpoint_sample.jets[1]
                or step.curvature_on_input != replayed_curvature
                or _interval_sign(step.curvature_on_input) != required_curvature_sign
            ):
                raise F0VerificationFailure(HOLD_NEWTON, "saved Newton input chain mutated")
            quotient = _interval_divide(
                step.derivative_at_midpoint,
                step.curvature_on_input,
            )
            expected_newton = _interval_subtract(
                OutwardInterval.from_fraction(midpoint),
                quotient,
            )
            expected_output = _interval_intersection(
                _signed_interval(previous_lower, previous_upper),
                expected_newton,
                failure_code=HOLD_NEWTON,
            )
            expected_inclusion = (
                expected_newton.lower_fraction > previous_lower
                and expected_newton.upper_fraction < previous_upper
            )
            if (
                expected_newton != step.newton_image
                or expected_output.lower_fraction != step.output_lower
                or expected_output.upper_fraction != step.output_upper
                or step.inclusion_in_interior is not expected_inclusion
            ):
                raise F0VerificationFailure(HOLD_NEWTON, "saved Newton arithmetic mutated")
            inclusion_observed = inclusion_observed or expected_inclusion
            previous_lower = step.output_lower
            previous_upper = step.output_upper
        if not inclusion_observed or inclusion_observed is not root.inclusion_observed:
            raise F0VerificationFailure(HOLD_NEWTON, "saved Newton inclusion ledger mutated")
        final_curvature = enclose_time_tile(
            oracle,
            root.final_lower,
            root.final_upper,
        ).curvature
        if _interval_sign(final_curvature) != required_curvature_sign:
            raise F0VerificationFailure(HOLD_NEWTON, "fresh final-root curvature is unresolved")
        previous_component_end = end
        current_sign = -current_sign
        if root_index and root.final_lower <= certificate.roots[root_index - 1].final_upper:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "saved roots are not strictly ordered")
    for tile in certificate.tiles[previous_component_end + 1 :]:
        if tile.derivative_sign != current_sign:
            raise F0VerificationFailure(HOLD_TOPOLOGY, "final complement sign mutated")


def audit_physical_full_window_topology_v2(
    certificate: FullWindowTopologyCertificate,
    *,
    oracle: Any,
    control_id: str,
) -> None:
    """Audit a saved physical certificate against the immutable v2 contract."""

    audit_full_window_topology(
        certificate,
        oracle=oracle,
        expected_window_lower=Fraction(1, 2),
        expected_window_upper=Fraction(35),
        expected_root_bands=physical_root_bands_v2(control_id),
        expected_initial_derivative_sign=1,
    )
