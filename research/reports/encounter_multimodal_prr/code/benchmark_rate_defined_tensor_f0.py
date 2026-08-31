#!/usr/bin/env python3
"""Science-free neutral benchmark for the rate-defined tensor F0 kernel."""

from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from typing import Sequence

import numpy as np
import rate_defined_tensor_f0 as f0


def build_neutral_kernel(profile: str) -> f0.RateDefinedTensorKernel:
    if profile == "neutral-small":
        midpoint_cells, relative_cells, transverse_cells = 17, 16, 16
    elif profile == "neutral-n33":
        midpoint_cells = relative_cells = transverse_cells = 33
    else:
        raise SystemExit("unknown science-free neutral profile")
    midpoint = f0.build_reflecting_sg_axis(
        "neutral_midpoint",
        tuple(Fraction(index, midpoint_cells - 1) for index in range(midpoint_cells)),
        (Fraction(0),) * midpoint_cells,
        Fraction(1, 1000),
    )
    relative = f0.build_periodic_diffusion_axis(
        "neutral_relative",
        relative_cells,
        Fraction(1),
        Fraction(1, 2000),
    )
    transverse = f0.build_periodic_diffusion_axis(
        "neutral_transverse_shifted",
        transverse_cells,
        Fraction(1),
        Fraction(1, 2000),
        half_cell_shift=True,
    )
    shape = (midpoint.size, relative.size, transverse.size)
    # A generic exact synthetic death coefficient, not an installed physical
    # budget and not any prospective control.
    killing = (f0.OutwardInterval.from_fraction(Fraction(1, 256)),) * np.prod(shape)
    return f0.build_rate_defined_tensor_kernel(
        (midpoint, relative, transverse),
        killing,
    )


def run_benchmark(actions: int, profile: str) -> dict[str, object]:
    if not isinstance(actions, int) or not (1 <= actions <= 200):
        raise SystemExit("actions must be in 1..200")
    build_start = time.perf_counter()
    kernel = build_neutral_kernel(profile)
    build_seconds = time.perf_counter() - build_start
    state = np.arange(1, kernel.states + 1, dtype=np.float64)
    state /= np.sum(state)

    # The kernel is audited once above.  Time only the tensor action, matching
    # the production propagation loop, which does not repeat the O(N) exact
    # Fraction audit before every Poisson power.
    matrix_free_start = time.perf_counter()
    matrix_free = state
    for _ in range(actions):
        matrix_free = f0._matrix_free_p_transpose(
            kernel,
            matrix_free,
            check_runtime=False,
        )
    matrix_free_seconds = time.perf_counter() - matrix_free_start

    csr_build_start = time.perf_counter()
    csr = f0.explicit_p_csr(kernel)
    csr_build_seconds = time.perf_counter() - csr_build_start
    csr_start = time.perf_counter()
    explicit = state
    for _ in range(actions):
        explicit = np.asarray(csr.transpose() @ explicit).reshape(-1)
    csr_seconds = time.perf_counter() - csr_start
    distance = float(np.sum(np.abs(matrix_free - explicit)))

    tensor_bytes = sum(
        array.nbytes
        for array in (
            kernel.killing_center,
            kernel.diagonal_center,
            kernel.p_self_center,
            *kernel.forward_center,
            *kernel.backward_center,
            *kernel.p_forward_center,
            *kernel.p_backward_center,
        )
    )
    csr_bytes = csr.data.nbytes + csr.indices.nbytes + csr.indptr.nbytes
    summary = f0.canonical_science_free_summary(
        kernel,
        label=f"science_free_{profile.replace('-', '_')}_tensor_benchmark",
    )
    summary.update(
        {
            "actions": actions,
            "profile": profile,
            "build_seconds": build_seconds,
            "matrix_free_action_seconds": matrix_free_seconds,
            "explicit_csr_build_seconds": csr_build_seconds,
            "explicit_csr_action_seconds": csr_seconds,
            "matrix_free_vs_csr_l1_distance": distance,
            "tensor_numeric_bytes": tensor_bytes,
            "explicit_csr_bytes": csr_bytes,
            "explicit_csr_nnz": int(csr.nnz),
        }
    )
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science-free-neutral", action="store_true")
    parser.add_argument(
        "--profile",
        choices=("neutral-small", "neutral-n33"),
        default="neutral-small",
    )
    parser.add_argument("--actions", type=int, default=20)
    args = parser.parse_args(argv)
    if not args.science_free_neutral:
        raise SystemExit("explicit --science-free-neutral is required")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    print(
        json.dumps(
            run_benchmark(args.actions, args.profile),
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
