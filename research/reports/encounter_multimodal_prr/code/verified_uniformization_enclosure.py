"""Method-only verified uniformization for finite killed CTMCs.

This prototype deliberately does not know any prospective LP control.  It
certifies the action of ``exp(t Q.T)`` for a *given* small sparse row killed
generator whose binary64 entries are interpreted as exact dyadic numbers.

The proof ledger is in the induced l1 norm.  Poisson probabilities are
enclosed with directed MPFR rounding (gmpy2); every binary64 sparse action,
weighted accumulation, generator action, norm, and dot product receives an
explicit roundoff allowance.  The code is a reference/proof prototype, not a
production F1 evaluator.
"""

from __future__ import annotations

import ctypes
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

import gmpy2
import numpy as np
from scipy import sparse

FLOAT64_U = Fraction(1, 2**53)
FLOAT64_ETA = float(np.nextafter(np.float64(0.0), np.float64(1.0)))


class VerificationFailure(RuntimeError):
    """Fail-closed outcome for a malformed or unresolved certificate."""


def verify_binary64_runtime() -> None:
    """Fail if the roundoff model used by the ledger is not observable."""

    info = np.finfo(np.float64)
    if np.dtype(np.float64).itemsize != 8 or info.nmant != 52:
        raise VerificationFailure("runtime is not IEEE binary64")
    try:
        fegetround = ctypes.CDLL(None).fegetround
        fegetround.restype = ctypes.c_int
        # C99/POSIX FE_TONEAREST is zero on the pinned macOS runtime.
        if int(fegetround()) != 0:
            raise VerificationFailure("runtime rounding mode is not round-to-nearest")
    except AttributeError as error:
        raise VerificationFailure("fegetround is unavailable") from error
    eta = np.float64(FLOAT64_ETA)
    if (
        eta == 0.0
        or np.float64(eta * np.float64(1.0)) != eta
        or np.float64(eta + eta) == 0.0
        or float((sparse.csr_matrix([[1.0]]) @ np.asarray([eta], dtype=np.float64))[0])
        != FLOAT64_ETA
    ):
        raise VerificationFailure("subnormals are flushed in a required kernel")


def _up(value: float) -> float:
    value = float(value)
    if math.isnan(value) or value < 0.0:
        raise VerificationFailure("an error bound became negative or NaN")
    if math.isinf(value):
        return value
    return float(np.nextafter(np.float64(value), np.float64(math.inf)))


def _down(value: float) -> float:
    value = float(value)
    if math.isnan(value):
        raise VerificationFailure("an endpoint became NaN")
    if math.isinf(value) and value < 0.0:
        return value
    return float(np.nextafter(np.float64(value), np.float64(-math.inf)))


def _next_up_signed(value: float) -> float:
    value = float(value)
    if math.isnan(value):
        raise VerificationFailure("an endpoint became NaN")
    if math.isinf(value) and value > 0.0:
        return value
    return float(np.nextafter(np.float64(value), np.float64(math.inf)))


def _add_up(*values: float) -> float:
    total = 0.0
    for value in values:
        if not math.isfinite(value) or value < 0.0:
            raise VerificationFailure("outward sum received an invalid operand")
        total = _up(total + float(value))
    return total


def _mul_up(left: float, right: float) -> float:
    if not math.isfinite(left) or not math.isfinite(right) or left < 0.0 or right < 0.0:
        raise VerificationFailure("outward product received an invalid operand")
    return _up(float(left) * float(right))


def _div_up(numerator: float, denominator_lower: float) -> float:
    if (
        not math.isfinite(numerator)
        or not math.isfinite(denominator_lower)
        or numerator < 0.0
        or denominator_lower <= 0.0
    ):
        raise VerificationFailure("outward quotient received an invalid operand")
    return _up(float(numerator) / float(denominator_lower))


def _fraction_upper(value: Fraction) -> float:
    if value < 0:
        raise VerificationFailure("expected a nonnegative rational bound")
    candidate = float(value)
    if math.isinf(candidate):
        return candidate
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    return candidate


def gamma(k: int) -> float:
    """Outward binary64 upper bound for Higham's gamma_k."""

    if not isinstance(k, int) or k < 0 or k >= 2**53:
        raise VerificationFailure("invalid gamma index")
    if k == 0:
        return 0.0
    return _fraction_upper(Fraction(k, 2**53 - k))


def _pairwise_sum(values: np.ndarray) -> float:
    work = np.asarray(values, dtype=np.float64).reshape(-1).copy()
    if not np.all(np.isfinite(work)):
        raise VerificationFailure("pairwise reduction received a nonfinite value")
    if work.size == 0:
        return 0.0
    while work.size > 1:
        pairs = work.size // 2
        reduced = np.add(work[: 2 * pairs : 2], work[1 : 2 * pairs : 2], dtype=np.float64)
        if work.size % 2:
            work = np.concatenate((reduced, work[-1:]))
        else:
            work = reduced
    return float(work[0])


def l1_upper(values: np.ndarray) -> float:
    """Upper-bound the exact l1 norm of a binary64 vector."""

    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    depth = int(math.ceil(math.log2(max(1, vector.size))))
    computed = _pairwise_sum(np.abs(vector))
    g = gamma(depth)
    absolute = vector.size * (depth + 1) * FLOAT64_ETA
    if g >= 1.0:
        raise VerificationFailure("pairwise norm bound overflowed")
    numerator = _add_up(computed, absolute)
    denominator_lower = _down(1.0 - g)
    return _div_up(numerator, denominator_lower)


def pairwise_dot(values: np.ndarray, observable: np.ndarray) -> tuple[float, float]:
    """Return a deterministic pairwise dot and a proved roundoff radius."""

    left = np.asarray(values, dtype=np.float64).reshape(-1)
    right = np.asarray(observable, dtype=np.float64).reshape(-1)
    if left.shape != right.shape or not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise VerificationFailure("malformed pairwise dot")
    products = np.multiply(left, right, dtype=np.float64)
    nominal = _pairwise_sum(products)
    depth = int(math.ceil(math.log2(max(1, left.size))))
    g = gamma(depth + 1)
    computed_absolute = _pairwise_sum(np.abs(products))
    underflow = left.size * (depth + 2) * FLOAT64_ETA
    if g >= 1.0:
        raise VerificationFailure("pairwise dot bound overflowed")
    numerator = _add_up(computed_absolute, underflow)
    denominator_lower = _down(1.0 - g)
    exact_absolute_upper = _div_up(numerator, denominator_lower)
    radius = _add_up(_mul_up(g, exact_absolute_upper), underflow)
    return nominal, radius


def _mpfr_from_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=rounding):
        return gmpy2.mpfr(value.numerator) / gmpy2.mpfr(value.denominator)


def _mpfr_to_float_lower(value: gmpy2.mpfr) -> float:
    candidate = float(value)
    with gmpy2.context(
        gmpy2.get_context(), precision=max(128, value.precision), round=gmpy2.RoundToNearest
    ):
        if gmpy2.mpfr(candidate) > value:
            candidate = _down(candidate)
    return candidate


def _mpfr_to_float_upper(value: gmpy2.mpfr) -> float:
    candidate = float(value)
    with gmpy2.context(
        gmpy2.get_context(), precision=max(128, value.precision), round=gmpy2.RoundToNearest
    ):
        if gmpy2.mpfr(candidate) < value:
            candidate = _up(candidate)
    return candidate


@dataclass(frozen=True)
class PoissonEnclosure:
    mean: Fraction
    midpoint: np.ndarray
    radius: np.ndarray
    upper: np.ndarray
    tail_upper: float
    precision_bits: int


def poisson_enclosure(
    mean: Fraction,
    tail_tolerance: Fraction,
    *,
    precision_bits: int = 192,
    max_terms: int = 200_000,
) -> PoissonEnclosure:
    """Enclose Poisson weights 0..K and the right tail using directed MPFR.

    Starting at zero is intentional.  Production may replace this by the
    Fox--Glynn scaled representation, but may not replace the directed
    probability/tail ledger.
    """

    if mean < 0 or tail_tolerance <= 0 or tail_tolerance >= 1:
        raise VerificationFailure("invalid Poisson mean or tail tolerance")
    if precision_bits < 96 or max_terms < 1:
        raise VerificationFailure("insufficient MPFR precision or term cap")

    x_lo = _mpfr_from_fraction(mean, precision_bits, gmpy2.RoundDown)
    x_hi = _mpfr_from_fraction(mean, precision_bits, gmpy2.RoundUp)
    tol_lo = _mpfr_from_fraction(tail_tolerance, precision_bits, gmpy2.RoundDown)
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
        w_lo = gmpy2.exp(-x_hi)
    with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
        w_hi = gmpy2.exp(-x_lo)

    lower_values: list[float] = []
    upper_values: list[float] = []
    tail_hi = gmpy2.mpfr(1)
    index = 0
    while index < max_terms:
        lower_values.append(_mpfr_to_float_lower(w_lo))
        upper_values.append(_mpfr_to_float_upper(w_hi))

        denominator = index + 1
        with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundDown):
            next_lo = (w_lo * x_lo) / denominator
        with gmpy2.context(gmpy2.get_context(), precision=precision_bits, round=gmpy2.RoundUp):
            next_hi = (w_hi * x_hi) / denominator
            ratio = x_hi / (denominator + 1)
            if ratio < 1:
                tail_hi = next_hi / (1 - ratio)
            else:
                tail_hi = gmpy2.mpfr(1)
        if ratio < 1 and tail_hi <= tol_lo:
            break
        w_lo, w_hi = next_lo, next_hi
        index += 1
    else:
        raise VerificationFailure("Poisson term cap reached before tail certification")

    lower = np.asarray(lower_values, dtype=np.float64)
    upper = np.asarray(upper_values, dtype=np.float64)
    midpoint = np.asarray(lower + 0.5 * (upper - lower), dtype=np.float64)
    midpoint = np.minimum(np.maximum(midpoint, lower), upper)
    radius = np.maximum(midpoint - lower, upper - midpoint)
    radius = np.nextafter(radius, np.full_like(radius, math.inf))
    return PoissonEnclosure(
        mean=mean,
        midpoint=midpoint,
        radius=radius,
        upper=upper,
        tail_upper=_mpfr_to_float_upper(tail_hi),
        precision_bits=precision_bits,
    )


@dataclass(frozen=True)
class UniformizationKernel:
    q: sparse.csr_matrix
    rate: float
    rate_fraction: Fraction
    p_center: sparse.csr_matrix
    p_transpose: sparse.csr_matrix
    p_induced_error: float
    maximum_center_row_sum: float
    maximum_transpose_row_nnz: int
    exact_q_abs_row_sum: float
    target_q_induced_uncertainty: float


@dataclass(frozen=True)
class KilledGeneratorInterval:
    """Point center plus induced-l1 radius for an exact rate-defined Q."""

    center: sparse.csr_matrix
    induced_l1_radius: float
    maximum_target_exit: float


def rebuild_killed_generator_from_rates(
    free_generator: sparse.spmatrix, killing: Sequence[float]
) -> KilledGeneratorInterval:
    """Define Q from exact dyadic off-diagonal rates and killing.

    Input diagonal bytes are intentionally ignored.  The mathematical target
    diagonal is minus the exact dyadic sum of outgoing rates and killing.  A
    binary64 center is rounded toward minus infinity, and the one-diagonal
    perturbation is returned as an induced-l1 operator radius.
    """

    verify_binary64_runtime()
    free = sparse.csr_matrix(free_generator, dtype=np.float64)
    free.sum_duplicates()
    free.sort_indices()
    if free.shape[0] != free.shape[1] or free.shape[0] == 0:
        raise VerificationFailure("free generator must be nonempty and square")
    kill = np.asarray(killing, dtype=np.float64).reshape(-1)
    if (
        kill.shape != (free.shape[0],)
        or not np.all(np.isfinite(kill))
        or np.min(kill, initial=0.0) < 0.0
    ):
        raise VerificationFailure("killing field is malformed")

    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    maximum_radius = Fraction(0)
    maximum_exit = Fraction(0)
    for row in range(free.shape[0]):
        outgoing: dict[int, Fraction] = {}
        for offset in range(free.indptr[row], free.indptr[row + 1]):
            column = int(free.indices[offset])
            value = Fraction.from_float(float(free.data[offset]))
            if column == row:
                continue
            if value < 0:
                raise VerificationFailure("free generator has a negative off-diagonal rate")
            if value:
                outgoing[column] = outgoing.get(column, Fraction(0)) + value
        exit_rate = sum(outgoing.values(), Fraction(0)) + Fraction.from_float(float(kill[row]))
        maximum_exit = max(maximum_exit, exit_rate)
        exact_diagonal = -exit_rate
        center_diagonal = float(exact_diagonal)
        if Fraction.from_float(center_diagonal) > exact_diagonal:
            center_diagonal = _down(center_diagonal)
        diagonal_radius = exact_diagonal - Fraction.from_float(center_diagonal)
        if diagonal_radius < 0:
            raise VerificationFailure("diagonal reconstruction was not outward")
        maximum_radius = max(maximum_radius, diagonal_radius)
        for column, value in sorted(outgoing.items()):
            rows.append(row)
            columns.append(column)
            values.append(float(value))
        rows.append(row)
        columns.append(row)
        values.append(center_diagonal)

    center = sparse.csr_matrix((values, (rows, columns)), shape=free.shape)
    center.sum_duplicates()
    center.sort_indices()
    return KilledGeneratorInterval(
        center=center,
        induced_l1_radius=_fraction_upper(maximum_radius),
        maximum_target_exit=_fraction_upper(maximum_exit),
    )


def build_exact_dyadic_kernel(
    q: sparse.spmatrix,
    *,
    rate: float | None = None,
    target_q_induced_uncertainty: float = 0.0,
) -> UniformizationKernel:
    """Build and exactly preflight a small binary64 killed-generator kernel.

    Fractions are used here to make the structural and coefficient proof
    independent of binary64 reductions.  A production tensor implementation
    must replace this O(nnz) Fraction pass by an outward rate-stencil proof.
    """

    verify_binary64_runtime()
    if not math.isfinite(target_q_induced_uncertainty) or target_q_induced_uncertainty < 0.0:
        raise VerificationFailure("target-generator uncertainty is invalid")
    matrix = sparse.csr_matrix(q, dtype=np.float64)
    matrix.sum_duplicates()
    matrix.sort_indices()
    if matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0:
        raise VerificationFailure("Q must be a nonempty square matrix")
    if not np.all(np.isfinite(matrix.data)):
        raise VerificationFailure("Q contains nonfinite entries")
    n = matrix.shape[0]
    dense_rows: list[dict[int, Fraction]] = []
    maximum_exit = Fraction(0)
    q_abs_max = Fraction(0)
    for row in range(n):
        entries: dict[int, Fraction] = {}
        for offset in range(matrix.indptr[row], matrix.indptr[row + 1]):
            column = int(matrix.indices[offset])
            value = Fraction.from_float(float(matrix.data[offset]))
            entries[column] = entries.get(column, Fraction(0)) + value
        diagonal = entries.get(row, Fraction(0))
        if diagonal > 0:
            raise VerificationFailure("Q has a positive diagonal")
        for column, value in entries.items():
            if column != row and value < 0:
                raise VerificationFailure("Q has a negative off-diagonal")
        row_sum = sum(entries.values(), Fraction(0))
        if row_sum > 0:
            raise VerificationFailure("Q has a positive exact row sum")
        maximum_exit = max(maximum_exit, -diagonal)
        q_abs_max = max(q_abs_max, sum((abs(value) for value in entries.values()), Fraction(0)))
        dense_rows.append(entries)

    if rate is None:
        rate_value = float(maximum_exit)
        if Fraction.from_float(rate_value) < maximum_exit:
            rate_value = _up(rate_value)
    else:
        rate_value = float(rate)
    if not math.isfinite(rate_value) or rate_value <= 0:
        raise VerificationFailure("uniformization rate must be finite and positive")
    rate_fraction = Fraction.from_float(rate_value)
    if rate_fraction < maximum_exit:
        raise VerificationFailure("uniformization rate is smaller than an exit rate")

    rows: list[int] = []
    columns: list[int] = []
    centers: list[float] = []
    radii_by_row = [Fraction(0) for _ in range(n)]
    for row, entries in enumerate(dense_rows):
        columns_here = set(entries)
        columns_here.add(row)
        for column in sorted(columns_here):
            exact = entries.get(column, Fraction(0)) / rate_fraction
            if column == row:
                exact += 1
            if exact < 0:
                raise VerificationFailure("uniformized matrix has a negative exact entry")
            center = float(exact)
            if center < 0 or not math.isfinite(center):
                raise VerificationFailure("uniformized center is invalid")
            error = abs(exact - Fraction.from_float(center))
            if center != 0.0 or error != 0:
                rows.append(row)
                columns.append(column)
                centers.append(center)
            radii_by_row[row] += error
        exact_row_sum = sum(
            (
                entries.get(column, Fraction(0)) / rate_fraction + (1 if column == row else 0)
                for column in columns_here
            ),
            Fraction(0),
        )
        if exact_row_sum < 0 or exact_row_sum > 1:
            raise VerificationFailure("uniformized exact row is not substochastic")

    p_center = sparse.csr_matrix((centers, (rows, columns)), shape=matrix.shape)
    p_center.sum_duplicates()
    p_center.sort_indices()
    if np.min(p_center.data, initial=0.0) < 0.0:
        raise VerificationFailure("uniformized center lost nonnegativity")
    p_error = max(radii_by_row, default=Fraction(0))
    p_error_upper = _add_up(
        _fraction_upper(p_error),
        _div_up(target_q_induced_uncertainty, rate_value),
    )
    exact_center_row_sum = Fraction(0)
    for row in range(n):
        row_sum = sum(
            (
                Fraction.from_float(float(p_center.data[offset]))
                for offset in range(p_center.indptr[row], p_center.indptr[row + 1])
            ),
            Fraction(0),
        )
        exact_center_row_sum = max(exact_center_row_sum, row_sum)
    p_transpose = p_center.transpose().tocsr()
    row_nnz = np.diff(p_transpose.indptr)
    return UniformizationKernel(
        q=matrix,
        rate=rate_value,
        rate_fraction=rate_fraction,
        p_center=p_center,
        p_transpose=p_transpose,
        p_induced_error=p_error_upper,
        maximum_center_row_sum=_fraction_upper(exact_center_row_sum),
        maximum_transpose_row_nnz=int(np.max(row_nnz, initial=0)),
        exact_q_abs_row_sum=_fraction_upper(q_abs_max),
        target_q_induced_uncertainty=float(target_q_induced_uncertainty),
    )


@dataclass(frozen=True)
class ChunkLedger:
    mean: float
    terms: int
    tail_error: float
    propagated_power_error: float
    weight_error: float
    accumulation_roundoff: float
    output_l1_error: float


@dataclass(frozen=True)
class StateEnclosure:
    nominal: np.ndarray
    l1_error: float
    exact_mass_cap: float
    elapsed_time: Fraction
    chunks: tuple[ChunkLedger, ...]


def uniformization_chunk(
    kernel: UniformizationKernel,
    state: StateEnclosure,
    duration: Fraction,
    *,
    tail_tolerance: Fraction,
    precision_bits: int = 192,
    max_terms: int = 200_000,
) -> StateEnclosure:
    if duration < 0:
        raise VerificationFailure("negative propagation duration")
    if duration == 0:
        return state
    vector = np.asarray(state.nominal, dtype=np.float64).reshape(-1)
    if vector.shape != (kernel.q.shape[0],) or not np.all(np.isfinite(vector)):
        raise VerificationFailure("malformed state")
    if np.min(vector, initial=0.0) < 0.0:
        raise VerificationFailure("nominal uniformization state is negative")

    probabilities = poisson_enclosure(
        kernel.rate_fraction * duration,
        tail_tolerance,
        precision_bits=precision_bits,
        max_terms=max_terms,
    )
    terms = int(probabilities.midpoint.size)
    accumulator = np.zeros_like(vector)
    power = vector.copy()
    power_error = float(state.l1_error)
    weighted_power_error = 0.0
    weight_error = 0.0
    absolute_accumulation = 0.0
    propagated_power_error = 0.0
    action_gamma = gamma(2 * max(1, kernel.maximum_transpose_row_nnz))
    underflow_per_action = (
        kernel.q.shape[0] * (2 * max(1, kernel.maximum_transpose_row_nnz) + 1) * FLOAT64_ETA
    )

    for index in range(terms):
        mass_upper = l1_upper(power)
        weight = float(probabilities.midpoint[index])
        accumulator = np.add(
            accumulator,
            np.multiply(weight, power, dtype=np.float64),
            dtype=np.float64,
        )
        if not np.all(np.isfinite(accumulator)):
            raise VerificationFailure("weighted uniformization sum became nonfinite")
        weighted_power_error = _add_up(
            weighted_power_error,
            _mul_up(float(probabilities.upper[index]), power_error),
        )
        weight_error = _add_up(
            weight_error,
            _mul_up(float(probabilities.radius[index]), mass_upper),
        )
        absolute_accumulation = _add_up(
            absolute_accumulation,
            _mul_up(abs(weight), mass_upper),
        )
        propagated_power_error = max(propagated_power_error, power_error)
        if index + 1 < terms:
            next_power = np.asarray(kernel.p_transpose @ power, dtype=np.float64)
            if not np.all(np.isfinite(next_power)) or np.min(next_power, initial=0.0) < 0.0:
                raise VerificationFailure("uniformized sparse action lost positivity or finiteness")
            sparse_roundoff = _add_up(
                _mul_up(_mul_up(action_gamma, kernel.maximum_center_row_sum), mass_upper),
                underflow_per_action,
            )
            coefficient_error = _mul_up(kernel.p_induced_error, mass_upper)
            power_error = _add_up(power_error, sparse_roundoff, coefficient_error)
            power = next_power

    accumulation_gamma = gamma(2 * terms)
    accumulation_underflow = kernel.q.shape[0] * (2 * terms + 1) * FLOAT64_ETA
    accumulation_roundoff = _add_up(
        _mul_up(accumulation_gamma, absolute_accumulation), accumulation_underflow
    )
    tail_error = _mul_up(probabilities.tail_upper, state.exact_mass_cap)
    output_error = _add_up(weighted_power_error, weight_error, accumulation_roundoff, tail_error)
    if not math.isfinite(output_error):
        raise VerificationFailure("uniformization error ledger overflowed")
    ledger = ChunkLedger(
        mean=float(probabilities.mean),
        terms=terms,
        tail_error=tail_error,
        propagated_power_error=propagated_power_error,
        weight_error=weight_error,
        accumulation_roundoff=accumulation_roundoff,
        output_l1_error=output_error,
    )
    return StateEnclosure(
        nominal=accumulator,
        l1_error=output_error,
        exact_mass_cap=state.exact_mass_cap,
        elapsed_time=state.elapsed_time + duration,
        chunks=(*state.chunks, ledger),
    )


def propagate_verified(
    kernel: UniformizationKernel,
    initial: Sequence[float],
    time: float,
    *,
    initial_l1_error: float = 0.0,
    exact_mass_cap: float = 1.0,
    mean_cap: float = 500.0,
    total_tail_tolerance: float = 1.0e-18,
    precision_bits: int = 192,
    max_terms: int = 200_000,
) -> StateEnclosure:
    vector = np.asarray(initial, dtype=np.float64).reshape(-1)
    if (
        vector.shape != (kernel.q.shape[0],)
        or not np.all(np.isfinite(vector))
        or np.min(vector, initial=0.0) < 0.0
        or not math.isfinite(initial_l1_error)
        or initial_l1_error < 0.0
        or not math.isfinite(exact_mass_cap)
        or exact_mass_cap <= 0.0
        or not math.isfinite(time)
        or time < 0.0
        or not math.isfinite(mean_cap)
        or mean_cap <= 0.0
        or not math.isfinite(total_tail_tolerance)
        or not (0.0 < total_tail_tolerance < 1.0)
    ):
        raise VerificationFailure("invalid propagation inputs")
    elapsed = Fraction.from_float(float(time))
    total_mean = kernel.rate_fraction * elapsed
    chunk_count = max(1, int(math.ceil(float(total_mean) / mean_cap)))
    duration = elapsed / chunk_count
    tail_each = Fraction.from_float(float(total_tail_tolerance)) / chunk_count
    state = StateEnclosure(
        nominal=vector.copy(),
        l1_error=float(initial_l1_error),
        exact_mass_cap=float(exact_mass_cap),
        elapsed_time=Fraction(0),
        chunks=(),
    )
    for _ in range(chunk_count):
        state = uniformization_chunk(
            kernel,
            state,
            duration,
            tail_tolerance=tail_each,
            precision_bits=precision_bits,
            max_terms=max_terms,
        )
    if state.elapsed_time != elapsed:
        raise VerificationFailure("exact-rational time partition failed to close")
    return state


@dataclass(frozen=True)
class ActionRow:
    order: int
    nominal_action: np.ndarray
    action_l1_error: float
    action_l1_upper: float
    scalar_nominal: float
    scalar_radius: float
    scalar_lower: float
    scalar_upper: float
    m_upper: float


def enclose_actions_and_scalars(
    kernel: UniformizationKernel,
    state: StateEnclosure,
    killing: Sequence[float],
    *,
    maximum_order: int = 3,
    q_induced_uncertainty: float | None = None,
    killing_inf_uncertainty: float = 0.0,
) -> tuple[ActionRow, ...]:
    """Enclose z_r=(Q.T)^r p, k.T z_r, and ||k||inf ||z_r||1."""

    if q_induced_uncertainty is None:
        q_induced_uncertainty = kernel.target_q_induced_uncertainty
    if maximum_order < 0 or maximum_order > 8:
        raise VerificationFailure("unsupported generator-action order")
    k = np.asarray(killing, dtype=np.float64).reshape(-1)
    if (
        k.shape != state.nominal.shape
        or not np.all(np.isfinite(k))
        or np.min(k, initial=0.0) < 0.0
        or not math.isfinite(q_induced_uncertainty)
        or q_induced_uncertainty < 0.0
        or not math.isfinite(killing_inf_uncertainty)
        or killing_inf_uncertainty < 0.0
    ):
        raise VerificationFailure("invalid observable/action inputs")
    qt = kernel.q.transpose().tocsr()
    maximum_nnz = int(np.max(np.diff(qt.indptr), initial=0))
    action_gamma = gamma(2 * max(1, maximum_nnz))
    action_underflow = kernel.q.shape[0] * (2 * max(1, maximum_nnz) + 1) * FLOAT64_ETA
    q_norm_upper = _add_up(kernel.exact_q_abs_row_sum, q_induced_uncertainty)
    k_inf_upper = _add_up(float(np.max(k, initial=0.0)), killing_inf_uncertainty)

    z = np.asarray(state.nominal, dtype=np.float64).copy()
    error = float(state.l1_error)
    rows: list[ActionRow] = []
    for order in range(maximum_order + 1):
        z_norm = l1_upper(z)
        scalar, dot_error = pairwise_dot(k, z)
        observable_error = _add_up(
            _mul_up(k_inf_upper, error),
            _mul_up(killing_inf_uncertainty, z_norm),
        )
        radius = _add_up(dot_error, observable_error)
        action_norm_upper = _add_up(z_norm, error)
        m_upper = _mul_up(k_inf_upper, action_norm_upper)
        rows.append(
            ActionRow(
                order=order,
                nominal_action=z.copy(),
                action_l1_error=error,
                action_l1_upper=action_norm_upper,
                scalar_nominal=scalar,
                scalar_radius=radius,
                scalar_lower=_down(scalar - radius),
                scalar_upper=_next_up_signed(scalar + radius),
                m_upper=m_upper,
            )
        )
        if order < maximum_order:
            next_z = np.asarray(qt @ z, dtype=np.float64)
            if not np.all(np.isfinite(next_z)):
                raise VerificationFailure("generator action became nonfinite")
            sparse_roundoff = _add_up(
                _mul_up(_mul_up(action_gamma, kernel.exact_q_abs_row_sum), z_norm),
                action_underflow,
            )
            coefficient_error = _mul_up(q_induced_uncertainty, z_norm)
            error = _add_up(_mul_up(q_norm_upper, error), sparse_roundoff, coefficient_error)
            z = next_z
    return tuple(rows)
