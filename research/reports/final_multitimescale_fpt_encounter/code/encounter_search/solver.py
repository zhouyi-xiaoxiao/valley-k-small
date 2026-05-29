from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, Literal

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


Start = tuple[int, int]
ReflectMode = Literal["stay", "bounce"]
AbsorptionMode = Literal["co_location", "co_location_or_crossing"]


@dataclass(frozen=True)
class EncounterChain:
    """Sparse absorbing-chain blocks for one reflecting 1D encounter model."""

    N: int
    q1: float
    q2: float
    P1: sp.csr_matrix
    P2: sp.csr_matrix
    P_joint: sp.csr_matrix
    transient_indices: np.ndarray
    diagonal_indices: np.ndarray
    transient_states: tuple[Start, ...]
    Q: sp.csr_matrix
    R: sp.csr_matrix
    reflect_mode: ReflectMode = "stay"

    @cached_property
    def transient_lookup(self) -> dict[int, int]:
        return {int(state): i for i, state in enumerate(self.transient_indices)}

    def full_index(self, x: int, y: int) -> int:
        _check_site(self.N, x)
        _check_site(self.N, y)
        return (int(x) - 1) * self.N + (int(y) - 1)

    def start_position(self, start: Start) -> int:
        x, y = start
        if int(x) == int(y):
            raise ValueError("start must be off-diagonal: a != b")
        state = self.full_index(int(x), int(y))
        try:
            return self.transient_lookup[state]
        except KeyError as exc:
            raise ValueError(f"start {start!r} is not a transient state") from exc


@dataclass(frozen=True)
class ExactDistribution:
    N: int
    q1: float
    q2: float
    start: Start
    times: np.ndarray
    f: np.ndarray
    f_by_k: np.ndarray
    survival: np.ndarray
    mean_truncated: float
    tail_mass: float
    max_mass_balance_error: float
    reached_tol: bool

    @property
    def mass(self) -> float:
        return float(np.sum(self.f))

    @property
    def mean(self) -> float:
        return float(np.dot(self.times, self.f)) if self.times.size else 0.0


@dataclass(frozen=True)
class AbsorptionChain:
    """Sparse total-absorption chain for co-location or crossing encounter."""

    N: int
    q1: float
    q2: float
    reflect_mode: ReflectMode
    absorption_mode: AbsorptionMode
    transient_indices: np.ndarray
    transient_states: tuple[Start, ...]
    Q: sp.csr_matrix
    h: np.ndarray

    @cached_property
    def transient_lookup(self) -> dict[int, int]:
        return {int(state): i for i, state in enumerate(self.transient_indices)}

    def full_index(self, x: int, y: int) -> int:
        _check_site(self.N, x)
        _check_site(self.N, y)
        return (int(x) - 1) * self.N + (int(y) - 1)

    def start_position(self, start: Start) -> int:
        x, y = start
        if int(x) == int(y):
            raise ValueError("start must be off-diagonal: a != b")
        return self.transient_lookup[self.full_index(int(x), int(y))]


@dataclass(frozen=True)
class TotalDistribution:
    N: int
    q1: float
    q2: float
    reflect_mode: ReflectMode
    absorption_mode: AbsorptionMode
    start: Start
    times: np.ndarray
    f: np.ndarray
    survival: np.ndarray
    mean_truncated: float
    tail_mass: float
    max_mass_balance_error: float
    reached_tol: bool

    @property
    def mass(self) -> float:
        return float(np.sum(self.f))

    @property
    def mean(self) -> float:
        return float(np.dot(self.times, self.f)) if self.times.size else 0.0


@dataclass(frozen=True)
class FormulaMoments:
    mean: float
    p_by_k: np.ndarray
    tau_by_k: np.ndarray
    p_tau_by_k: np.ndarray

    @property
    def p_sum(self) -> float:
        return float(np.sum(self.p_by_k))

    @property
    def p_tau_sum(self) -> float:
        return float(np.sum(self.p_tau_by_k))


def _check_site(N: int, x: int) -> None:
    if not 1 <= int(x) <= int(N):
        raise ValueError(f"site must lie in 1..N; got x={x!r}, N={N!r}")


def _check_mobility(q: float, *, name: str) -> float:
    value = float(q)
    if not np.isfinite(value) or value <= 0.0 or value > 1.0:
        raise ValueError(f"{name} must lie in (0, 1]; got {q!r}")
    return value


def reflecting_transition(N: int, q: float, *, reflect_mode: ReflectMode = "stay") -> sp.csr_matrix:
    """Return the sparse reflecting lazy transition matrix on sites 1..N."""

    N_i = int(N)
    q_f = _check_mobility(q, name="q")
    if reflect_mode not in {"stay", "bounce"}:
        raise ValueError(f"unknown reflect_mode={reflect_mode!r}")
    if N_i < 2:
        raise ValueError(f"N must be at least 2; got {N!r}")

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []

    for x0 in range(N_i):
        rows.append(x0)
        cols.append(x0)
        data.append(1.0 - q_f)

        left = x0 - 1
        if left < 0:
            left = x0 if reflect_mode == "stay" else min(x0 + 1, N_i - 1)
        rows.append(x0)
        cols.append(left)
        data.append(q_f / 2.0)

        right = x0 + 1
        if right >= N_i:
            right = x0 if reflect_mode == "stay" else max(x0 - 1, 0)
        rows.append(x0)
        cols.append(right)
        data.append(q_f / 2.0)

    P = sp.coo_matrix((data, (rows, cols)), shape=(N_i, N_i), dtype=float).tocsr()
    P.sum_duplicates()
    return P


def full_state_index(N: int, x: int, y: int) -> int:
    _check_site(N, x)
    _check_site(N, y)
    return (int(x) - 1) * int(N) + (int(y) - 1)


def diagonal_full_indices(N: int) -> np.ndarray:
    return np.array([full_state_index(N, k, k) for k in range(1, int(N) + 1)], dtype=int)


def transient_full_indices(N: int) -> tuple[np.ndarray, tuple[Start, ...]]:
    states: list[Start] = []
    indices: list[int] = []
    for x in range(1, int(N) + 1):
        for y in range(1, int(N) + 1):
            if x == y:
                continue
            states.append((x, y))
            indices.append(full_state_index(N, x, y))
    return np.array(indices, dtype=int), tuple(states)


def build_chain(
    N: int,
    q1: float,
    q2: float,
    *,
    reflect_mode: ReflectMode = "stay",
) -> EncounterChain:
    """Build sparse blocks Q=P[O,O] and R=P[O,D] for the encounter chain."""

    N_i = int(N)
    q1_f = _check_mobility(q1, name="q1")
    q2_f = _check_mobility(q2, name="q2")
    P1 = reflecting_transition(N_i, q1_f, reflect_mode=reflect_mode)
    P2 = reflecting_transition(N_i, q2_f, reflect_mode=reflect_mode)
    P_joint = sp.kron(P1, P2, format="csr")
    O, states = transient_full_indices(N_i)
    D = diagonal_full_indices(N_i)
    Q = P_joint[O, :][:, O].tocsr()
    R = P_joint[O, :][:, D].tocsr()
    return EncounterChain(
        N=N_i,
        q1=q1_f,
        q2=q2_f,
        P1=P1,
        P2=P2,
        P_joint=P_joint,
        transient_indices=O,
        diagonal_indices=D,
        transient_states=states,
        Q=Q,
        R=R,
        reflect_mode=reflect_mode,
    )


def build_absorption_chain(
    N: int,
    q1: float,
    q2: float,
    *,
    reflect_mode: ReflectMode = "stay",
    absorption_mode: AbsorptionMode = "co_location",
) -> AbsorptionChain:
    """Build a sparse total-absorption chain.

    ``co_location_or_crossing`` absorbs both diagonal landings and off-diagonal
    order reversals caused by one synchronous update.
    """

    if absorption_mode not in {"co_location", "co_location_or_crossing"}:
        raise ValueError(f"unknown absorption_mode={absorption_mode!r}")
    chain = build_chain(N, q1, q2, reflect_mode=reflect_mode)
    if absorption_mode == "co_location":
        h = np.asarray(chain.R.sum(axis=1)).reshape(-1)
        Q = chain.Q.copy()
    else:
        Q_coo = chain.Q.tocoo()
        x = np.array([state[0] for state in chain.transient_states], dtype=int)
        y = np.array([state[1] for state in chain.transient_states], dtype=int)
        old_sign = x[Q_coo.row] - y[Q_coo.row]
        new_sign = x[Q_coo.col] - y[Q_coo.col]
        keep = old_sign * new_sign > 0
        Q = sp.coo_matrix(
            (Q_coo.data[keep], (Q_coo.row[keep], Q_coo.col[keep])),
            shape=chain.Q.shape,
            dtype=float,
        ).tocsr()
        h = 1.0 - np.asarray(Q.sum(axis=1)).reshape(-1)
        h[np.abs(h) < 1e-15] = 0.0
    return AbsorptionChain(
        N=chain.N,
        q1=chain.q1,
        q2=chain.q2,
        reflect_mode=reflect_mode,
        absorption_mode=absorption_mode,
        transient_indices=chain.transient_indices,
        transient_states=chain.transient_states,
        Q=Q.tocsr(),
        h=np.asarray(h, dtype=float),
    )


def exact_distribution(
    chain: EncounterChain,
    start: Start,
    *,
    survival_tol: float = 1e-12,
    max_t: int = 200_000,
) -> ExactDistribution:
    """Compute f_by_k[t,k]=alpha Q^(t-1)R[:,k] by sparse propagation."""

    start_pos = chain.start_position(start)
    m = chain.Q.shape[0]
    alpha = np.zeros(m, dtype=float)
    alpha[start_pos] = 1.0
    current = alpha

    times: list[int] = []
    f_values: list[float] = []
    f_by_k_values: list[np.ndarray] = []
    survival: list[float] = [1.0]
    mean = 0.0
    mass_balance_error = 0.0

    for t in range(1, int(max_t) + 1):
        by_k = np.asarray(current @ chain.R).reshape(-1)
        hit = float(np.sum(by_k))
        next_current = np.asarray(current @ chain.Q).reshape(-1)
        next_survival = float(np.sum(next_current))

        times.append(t)
        f_values.append(hit)
        f_by_k_values.append(by_k)
        survival.append(next_survival)
        mean += float(t) * hit
        mass_balance_error = max(mass_balance_error, abs(hit - (survival[-2] - next_survival)))

        current = next_current
        if next_survival <= float(survival_tol):
            break

    times_arr = np.array(times, dtype=int)
    f_arr = np.array(f_values, dtype=float)
    f_by_k_arr = (
        np.vstack(f_by_k_values) if f_by_k_values else np.empty((0, chain.N), dtype=float)
    )
    survival_arr = np.array(survival, dtype=float)
    return ExactDistribution(
        N=chain.N,
        q1=chain.q1,
        q2=chain.q2,
        start=(int(start[0]), int(start[1])),
        times=times_arr,
        f=f_arr,
        f_by_k=f_by_k_arr,
        survival=survival_arr,
        mean_truncated=float(mean),
        tail_mass=float(survival_arr[-1]) if survival_arr.size else 0.0,
        max_mass_balance_error=float(mass_balance_error),
        reached_tol=bool(survival_arr.size and survival_arr[-1] <= float(survival_tol)),
    )


def exact_total_distribution(
    chain: AbsorptionChain,
    start: Start,
    *,
    survival_tol: float = 1e-12,
    max_t: int = 200_000,
) -> TotalDistribution:
    """Compute total absorption distribution for an ``AbsorptionChain``."""

    start_pos = chain.start_position(start)
    current = np.zeros(chain.Q.shape[0], dtype=float)
    current[start_pos] = 1.0
    times: list[int] = []
    f_values: list[float] = []
    survival: list[float] = [1.0]
    mean = 0.0
    mass_balance_error = 0.0
    for t in range(1, int(max_t) + 1):
        hit = float(current @ chain.h)
        next_current = np.asarray(current @ chain.Q).reshape(-1)
        next_survival = float(np.sum(next_current))
        times.append(t)
        f_values.append(hit)
        survival.append(next_survival)
        mean += float(t) * hit
        mass_balance_error = max(mass_balance_error, abs(hit - (survival[-2] - next_survival)))
        current = next_current
        if next_survival <= float(survival_tol):
            break
    times_arr = np.array(times, dtype=int)
    f_arr = np.array(f_values, dtype=float)
    survival_arr = np.array(survival, dtype=float)
    return TotalDistribution(
        N=chain.N,
        q1=chain.q1,
        q2=chain.q2,
        reflect_mode=chain.reflect_mode,
        absorption_mode=chain.absorption_mode,
        start=(int(start[0]), int(start[1])),
        times=times_arr,
        f=f_arr,
        survival=survival_arr,
        mean_truncated=float(mean),
        tail_mass=float(survival_arr[-1]) if survival_arr.size else 0.0,
        max_mass_balance_error=float(mass_balance_error),
        reached_tol=bool(survival_arr.size and survival_arr[-1] <= float(survival_tol)),
    )


def fundamental_moments(chain: EncounterChain, start: Start) -> FormulaMoments:
    """Return mean, p_k, tau_k, and p_k*tau_k from sparse linear solves."""

    start_pos = chain.start_position(start)
    mean_all, p_all, tau_num_all = all_start_fundamental_arrays(chain)
    p_by_k = np.asarray(p_all[start_pos, :], dtype=float)
    tau_num = np.asarray(tau_num_all[start_pos, :], dtype=float)
    tau_by_k = np.divide(
        tau_num,
        p_by_k,
        out=np.full_like(tau_num, np.nan, dtype=float),
        where=p_by_k > 1e-300,
    )
    return FormulaMoments(
        mean=float(mean_all[start_pos]),
        p_by_k=p_by_k,
        tau_by_k=tau_by_k,
        p_tau_by_k=p_by_k * tau_by_k,
    )


def all_start_fundamental_arrays(chain: EncounterChain) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return arrays indexed by transient start: mean, p_k, tau numerator."""

    m = chain.Q.shape[0]
    A = (sp.eye(m, format="csc", dtype=float) - chain.Q.tocsc())
    lu = spla.splu(A)
    mean_all = lu.solve(np.ones(m, dtype=float))
    p_all = lu.solve(chain.R.toarray())
    tau_num_all = lu.solve(p_all)
    return mean_all, p_all, tau_num_all


def row_stochastic_error(P: sp.spmatrix) -> float:
    row_sums = np.asarray(P.sum(axis=1)).reshape(-1)
    return float(np.max(np.abs(row_sums - 1.0))) if row_sums.size else 0.0


def min_entry(P: sp.spmatrix) -> float:
    if P.nnz == 0:
        return 0.0
    return float(P.data.min())


def absorbing_pgf_total(chain: EncounterChain, start: Start, z: complex) -> complex:
    """Return z alpha (I-zQ)^(-1) R 1 for the total encounter PGF."""

    start_pos = chain.start_position(start)
    m = chain.Q.shape[0]
    rhs = np.asarray(chain.R.sum(axis=1)).reshape(-1).astype(complex)
    A = sp.eye(m, format="csc", dtype=complex) - complex(z) * chain.Q.astype(complex).tocsc()
    values = spla.spsolve(A, rhs)
    return complex(z) * complex(values[start_pos])


def determinant_pgf_total(N: int, q1: float, q2: float, start: Start, z: complex) -> complex:
    """Return the determinant Green formula requested for the small-N check."""

    chain = build_chain(N, q1, q2)
    start_full = chain.full_index(*start)
    P = chain.P_joint.toarray().astype(complex)
    G = np.linalg.inv(np.eye(P.shape[0], dtype=complex) - complex(z) * P)
    D = chain.diagonal_indices
    A = G[np.ix_(D, D)]
    g_row = G[start_full, D].reshape(1, -1)
    ones_col = np.ones((D.size, 1), dtype=complex)
    det_A = np.linalg.det(A)
    det_replaced = np.linalg.det(A - ones_col @ g_row)
    return complex(1.0 - det_replaced / det_A)


def iter_ordered_starts(N: int) -> Iterable[Start]:
    for x in range(1, int(N) + 1):
        for y in range(1, int(N) + 1):
            if x != y:
                yield (x, y)
