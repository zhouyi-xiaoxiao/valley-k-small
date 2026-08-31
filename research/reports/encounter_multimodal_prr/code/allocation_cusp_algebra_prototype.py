#!/usr/bin/env python3
"""Small explicit-CSR audit of fixed-budget allocation cusp jets.

This file is deliberately independent of ``positive_b_broad_four_slab.py``.
It checks the column-state sensitivity equations and the direct observable
terms on a five-state killed Markov chain.  It is an algebra prototype, not
physical evidence for the broad four-slab calculation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply


@dataclass(frozen=True)
class Prototype:
    free_row_generator: sparse.csr_matrix
    patch_fields: np.ndarray
    initial: np.ndarray
    reference_weights: np.ndarray
    tangent_basis: np.ndarray
    budget: float


@dataclass(frozen=True)
class JetSnapshot:
    time: float
    theta: np.ndarray
    state: np.ndarray
    tangents: np.ndarray
    time_jets: np.ndarray
    allocation_time_jets: np.ndarray
    cusp_map: np.ndarray
    cusp_jacobian: np.ndarray


def build_prototype() -> Prototype:
    """Return a deterministic irreducible five-state killed chain."""

    free_row_generator = sparse.csr_matrix(
        np.asarray(
            (
                (-1.3, 1.0, 0.3, 0.0, 0.0),
                (0.4, -1.4, 0.8, 0.2, 0.0),
                (0.1, 0.5, -1.5, 0.7, 0.2),
                (0.0, 0.3, 0.5, -1.2, 0.4),
                (0.2, 0.0, 0.2, 0.6, -1.0),
            ),
            dtype=float,
        )
    )
    patch_fields = np.asarray(
        (
            (0.20, 0.10, 0.70, 0.20, 0.10),
            (0.10, 0.50, 0.20, 0.80, 0.10),
            (0.60, 0.20, 0.10, 0.30, 0.70),
            (0.30, 0.70, 0.40, 0.10, 0.50),
        ),
        dtype=float,
    )
    # Representative Euclidean-orthonormal two-plane inside {h: 1^T h=0}.
    # The physical promotion design freezes its own basis from the pinned B=0
    # response SVD; the algebra below is valid for any such fixed two-plane.
    tangent_basis = np.asarray(
        (
            (-0.033395172453772708, 0.047467545274063112),
            (-0.58857115592340892, -0.5698716394048472),
            (0.79006963866593882, -0.25674588852533126),
            (-0.16810331028875719, 0.77914998265611535),
        ),
        dtype=float,
    )
    return Prototype(
        free_row_generator=free_row_generator,
        patch_fields=patch_fields,
        initial=np.asarray((0.31, 0.19, 0.22, 0.17, 0.11), dtype=float),
        reference_weights=np.asarray((0.28, 0.23, 0.21, 0.28), dtype=float),
        tangent_basis=tangent_basis,
        budget=0.17,
    )


def operators(
    model: Prototype,
    theta: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, sparse.csr_matrix, tuple[sparse.csr_matrix, ...]]:
    """Return weights, per-budget killing, row generator, and its tangents."""

    theta_value = np.asarray(theta, dtype=float)
    if theta_value.shape != (2,):
        raise ValueError("theta must contain exactly two allocation coordinates")
    weights = model.reference_weights + model.tangent_basis @ theta_value
    if np.min(weights) <= 0.0 or abs(float(np.sum(weights)) - 1.0) > 1.0e-13:
        raise ValueError("theta left the interior fixed-budget simplex slice")
    kappa = weights @ model.patch_fields
    directions = model.tangent_basis.T @ model.patch_fields
    row_generator = model.free_row_generator - sparse.diags(model.budget * kappa, format="csr")
    row_tangents = tuple(
        sparse.diags(-model.budget * direction, format="csr") for direction in directions
    )
    return weights, kappa, row_generator, row_tangents


def direct_time_jets(
    model: Prototype,
    time: float,
    theta: np.ndarray,
    maximum_order: int = 4,
) -> np.ndarray:
    """Compute f and its exact semidiscrete time jets without sensitivities."""

    if maximum_order < 0:
        raise ValueError("maximum_order must be nonnegative")
    _weights, kappa, row_generator, _row_tangents = operators(model, theta)
    state = np.asarray(
        expm_multiply(float(time) * row_generator.T, model.initial),
        dtype=float,
    )
    observable = np.asarray(kappa, dtype=float)
    jets = []
    for _order in range(maximum_order + 1):
        jets.append(model.budget * float(state @ observable))
        observable = np.asarray(row_generator @ observable, dtype=float)
    return np.asarray(jets, dtype=float)


def snapshot(model: Prototype, time: float, theta: np.ndarray) -> JetSnapshot:
    """Compute state tangents, mixed jets, and the complete cusp Jacobian."""

    theta_value = np.asarray(theta, dtype=float)
    _weights, kappa, row_generator, row_tangents = operators(model, theta_value)
    state_count = model.initial.size
    column_generator = row_generator.T.tocsr()
    column_tangents = tuple(value.T.tocsr() for value in row_tangents)
    zero = sparse.csr_matrix((state_count, state_count), dtype=float)
    augmented = sparse.bmat(
        (
            (column_generator, zero, zero),
            (column_tangents[0], column_generator, zero),
            (column_tangents[1], zero, column_generator),
        ),
        format="csr",
    )
    augmented_initial = np.concatenate(
        (model.initial, np.zeros(state_count, dtype=float), np.zeros(state_count, dtype=float))
    )
    propagated = np.asarray(
        expm_multiply(float(time) * augmented, augmented_initial),
        dtype=float,
    )
    state = propagated[:state_count]
    tangents = propagated[state_count:].reshape(2, state_count)

    directions = model.tangent_basis.T @ model.patch_fields
    observables = [np.asarray(kappa, dtype=float)]
    observable_tangents = [np.asarray(directions, dtype=float)]
    for _order in range(4):
        previous = observables[-1]
        previous_tangents = observable_tangents[-1]
        observables.append(np.asarray(row_generator @ previous, dtype=float))
        observable_tangents.append(
            np.asarray(
                [
                    row_tangents[index] @ previous + row_generator @ previous_tangents[index]
                    for index in range(2)
                ],
                dtype=float,
            )
        )

    time_jets = model.budget * np.asarray(
        [float(state @ observable) for observable in observables],
        dtype=float,
    )
    allocation_time_jets = model.budget * np.asarray(
        [
            [
                float(tangents[index] @ observables[order])
                + float(state @ observable_tangents[order][index])
                for order in range(5)
            ]
            for index in range(2)
        ],
        dtype=float,
    )
    cusp_map = time_jets[1:4].copy()
    cusp_jacobian = np.asarray(
        (
            (time_jets[2], allocation_time_jets[0, 1], allocation_time_jets[1, 1]),
            (time_jets[3], allocation_time_jets[0, 2], allocation_time_jets[1, 2]),
            (time_jets[4], allocation_time_jets[0, 3], allocation_time_jets[1, 3]),
        ),
        dtype=float,
    )
    return JetSnapshot(
        time=float(time),
        theta=theta_value.copy(),
        state=state,
        tangents=tangents,
        time_jets=time_jets,
        allocation_time_jets=allocation_time_jets,
        cusp_map=cusp_map,
        cusp_jacobian=cusp_jacobian,
    )


def finite_difference_cusp_jacobian(
    model: Prototype,
    time: float,
    theta: np.ndarray,
    step: float = 2.0e-5,
) -> np.ndarray:
    """Independently center-difference H=(f_t,f_tt,f_ttt)."""

    theta_value = np.asarray(theta, dtype=float)

    def cusp_map(time_value: float, theta_argument: np.ndarray) -> np.ndarray:
        return direct_time_jets(model, time_value, theta_argument, maximum_order=3)[1:4]

    columns = [
        (cusp_map(time + step, theta_value) - cusp_map(time - step, theta_value)) / (2.0 * step)
    ]
    for index in range(2):
        direction = np.zeros(2, dtype=float)
        direction[index] = step
        columns.append(
            (cusp_map(time, theta_value + direction) - cusp_map(time, theta_value - direction))
            / (2.0 * step)
        )
    return np.column_stack(columns)


def main() -> int:
    model = build_prototype()
    point = snapshot(model, time=1.37, theta=np.asarray((0.017, -0.013)))
    finite_difference = finite_difference_cusp_jacobian(model, point.time, point.theta)
    print(
        "maximum cusp-Jacobian finite-difference error",
        np.max(abs(point.cusp_jacobian - finite_difference)),
    )
    print("projected rank", np.linalg.matrix_rank(point.cusp_jacobian[:2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
