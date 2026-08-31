"""Independent Round-125 attacks on the science-free rate-defined F0 core.

This file contains no production selector, positive-control, or F1 input.
The two fail-closed regression tests at the end intentionally fail against
the frozen pre-repair core SHA-256 98ae6d219359ad676243786f03441e30d32891847da4bf0fde263af2e084b007.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import replace
from fractions import Fraction
from itertools import product

import numpy as np
import pytest
import rate_defined_tensor_f0 as f0


def _neutral_chain() -> tuple[
    f0.RateDefinedTensorKernel,
    f0.InitialStateEnclosure,
]:
    axis = f0.build_reflecting_sg_axis(
        "round125_neutral_chain",
        (Fraction(0), Fraction(1, 2), Fraction(1)),
        (Fraction(0),) * 3,
        Fraction(1, 100),
    )
    kernel = f0.build_rate_defined_tensor_kernel(
        (axis,),
        (f0.OutwardInterval.from_fraction(Fraction(1, 100)),) * 3,
    )
    source = b"round125-science-free-delta-law"
    initial = f0.enclose_initial_state(
        (f0.ONE_INTERVAL, f0.ZERO_INTERVAL, f0.ZERO_INTERVAL),
        source_payload_bytes=source,
        expected_source_sha256=hashlib.sha256(source).hexdigest(),
    )
    return kernel, initial


def _three_root_oracle(time: Fraction) -> f0.TimeJetSample:
    roots = (Fraction(8, 5), Fraction(31, 10), Fraction(23, 5))
    uncertainty = Fraction(1, 10**9)
    first_sum = sum(roots, Fraction(0))
    pair_sum = roots[0] * roots[1] + roots[0] * roots[2] + roots[1] * roots[2]
    derivative = -(time - roots[0]) * (time - roots[1]) * (time - roots[2])
    curvature = -3 * time * time + 2 * first_sum * time - pair_sum
    third = -6 * time + 2 * first_sum
    return f0.TimeJetSample(
        time=time,
        jets=(
            f0.ZERO_INTERVAL,
            f0.OutwardInterval.from_fraction_bounds(
                derivative - uncertainty,
                derivative + uncertainty,
            ),
            f0.OutwardInterval.from_fraction(curvature),
            f0.OutwardInterval.from_fraction(third),
        ),
        m2=Fraction(50),
        m3=Fraction(25),
        m4=Fraction(6),
    )


def _three_root_certificate() -> f0.FullWindowTopologyCertificate:
    bands = (
        f0.RootBand("P1", Fraction(1), Fraction(9, 4), "maximum"),
        f0.RootBand("Q1", Fraction(5, 2), Fraction(15, 4), "minimum"),
        f0.RootBand("P2", Fraction(4), Fraction(11, 2), "maximum"),
    )
    return f0.certify_full_window_topology(
        _three_root_oracle,
        window_lower=Fraction(1, 2),
        window_upper=Fraction(6),
        root_bands=bands,
    )


def test_delta_p_minimum_has_two_independent_exact_corner_bounds() -> None:
    """Both branches bound every exact target corner, hence so does their min."""

    rng = random.Random(20260714)
    for case in range(24):
        cells = 3 + case % 2
        base = f0.build_periodic_diffusion_axis(
            f"round125_box_{case}",
            cells,
            Fraction(1),
            Fraction(1, 64),
        )
        edges = tuple(
            f0.OutwardInterval.from_fraction_bounds(
                Fraction(rng.randrange(1, 20), 2**10),
                Fraction(rng.randrange(21, 40), 2**10),
            )
            for _ in range(cells)
        )
        axis = replace(
            base,
            forward_rates=edges,
            backward_rates=tuple(edges[(index - 1) % cells] for index in range(cells)),
        )
        killing = tuple(
            f0.OutwardInterval.from_fraction_bounds(
                Fraction(rng.randrange(0, 8), 2**11),
                Fraction(rng.randrange(9, 18), 2**11),
            )
            for _ in range(cells)
        )
        kernel = f0.build_rate_defined_tensor_kernel((axis,), killing)
        phat = f0.explicit_p_csr(kernel).toarray()
        qhat = f0.explicit_q_csr(kernel).toarray()
        observed_p = Fraction(0)
        observed_q = Fraction(0)
        for row in range(cells):
            intervals = (edges[row], edges[(row - 1) % cells], killing[row])
            for corner in product(
                *((entry.lower_fraction, entry.upper_fraction) for entry in intervals)
            ):
                forward, backward, death = corner
                target_q = [Fraction(0) for _ in range(cells)]
                target_q[(row + 1) % cells] += forward
                target_q[(row - 1) % cells] += backward
                target_q[row] = -(forward + backward + death)
                target_p = [value / kernel.rate_fraction for value in target_q]
                target_p[row] += 1
                q_distance = sum(
                    (
                        abs(target - Fraction.from_float(float(center)))
                        for target, center in zip(target_q, qhat[row], strict=True)
                    ),
                    Fraction(0),
                )
                p_distance = sum(
                    (
                        abs(target - Fraction.from_float(float(center)))
                        for target, center in zip(target_p, phat[row], strict=True)
                    ),
                    Fraction(0),
                )
                observed_q = max(observed_q, q_distance)
                observed_p = max(observed_p, p_distance)
        assert observed_q <= kernel.delta_q_exact
        assert observed_p <= kernel.delta_p_direct_exact
        assert observed_p <= kernel.delta_p_via_q_exact
        assert observed_p <= kernel.delta_p_exact
        assert kernel.delta_p_exact == min(
            kernel.delta_p_direct_exact,
            kernel.delta_p_via_q_exact,
        )


def test_directed_disk_geometry_partition_and_reflection() -> None:
    radius = Fraction(1, 4)
    grid = tuple(Fraction(index, 20) for index in range(-5, 6))
    lower = Fraction(0)
    upper = Fraction(0)
    for x0, x1 in zip(grid, grid[1:], strict=False):
        for y0, y1 in zip(grid, grid[1:], strict=False):
            cell = f0.disk_rectangle_area_interval(
                x0,
                x1,
                y0,
                y1,
                radius,
                precision_bits=256,
            )
            reflected = f0.disk_rectangle_area_interval(
                -x1,
                -x0,
                -y1,
                -y0,
                radius,
                precision_bits=256,
            )
            assert cell == reflected
            lower += cell.lower_fraction
            upper += cell.upper_fraction
    disk_area = math.pi * float(radius) ** 2
    assert float(lower) <= disk_area <= float(upper)
    assert float(upper - lower) < 2.0e-15


def test_control_blind_alignment_geometry_is_deterministic() -> None:
    spec = f0.physical_configuration_specs_v2()[-1]
    first = f0.build_physical_geometry_v2(
        spec,
        panels_per_unit=256,
        precision_bits=192,
    )
    second = f0.build_physical_geometry_v2(
        spec,
        panels_per_unit=256,
        precision_bits=192,
    )
    assert first == second
    assert not first.prospective_control_values_read
    assert not first.positive_budget_primary_control_evaluated
    assert math.prod(axis.size for axis in first.axes) == spec.expected_states


def test_saved_propagation_audit_rejects_forged_state_and_zero_error() -> None:
    """P0 reproducer: pre-repair audit accepts a fabricated zero state/error."""

    kernel, initial = _neutral_chain()
    propagation = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        Fraction(1, 2),
        mean_cap=Fraction(1, 10),
        total_tail_tolerance=Fraction(1, 10**12),
    )
    forged_chunks = tuple(
        replace(
            chunk,
            poisson_tail_upper=0.0,
            propagated_power_error=0.0,
            weight_error=0.0,
            accumulation_roundoff=0.0,
            output_l1_error=0.0,
        )
        for chunk in propagation.chunks
    )
    forged = replace(
        propagation,
        nominal=np.zeros_like(propagation.nominal),
        l1_error=0.0,
        chunks=forged_chunks,
    )
    with pytest.raises(f0.F0VerificationFailure):
        f0.audit_matrix_free_propagation(
            kernel,
            initial,
            forged,
            expected_target_time=Fraction(1, 2),
            expected_mean_cap=Fraction(1, 10),
            expected_total_tail_tolerance=Fraction(1, 10**12),
            expected_precision_bits=192,
            expected_maximum_terms=200_000,
            expected_maximum_chunks=100_000,
        )


@pytest.mark.parametrize("mutation", ("invalid_initial_sign", "kind_curvature_mismatch"))
def test_saved_topology_audit_rejects_semantic_mutation(mutation: str) -> None:
    """P1 reproducer: pre-repair audit does not bind saved semantic labels."""

    certificate = _three_root_certificate()
    bands = (
        f0.RootBand("P1", Fraction(1), Fraction(9, 4), "maximum"),
        f0.RootBand("Q1", Fraction(5, 2), Fraction(15, 4), "minimum"),
        f0.RootBand("P2", Fraction(4), Fraction(11, 2), "maximum"),
    )
    if mutation == "invalid_initial_sign":
        forged = replace(certificate, initial_derivative_sign=0)
    else:
        first = replace(certificate.roots[0], kind="minimum")
        forged = replace(certificate, roots=(first,) + certificate.roots[1:])
    with pytest.raises(f0.F0VerificationFailure):
        f0.audit_full_window_topology(
            forged,
            oracle=_three_root_oracle,
            expected_window_lower=Fraction(1, 2),
            expected_window_upper=Fraction(6),
            expected_root_bands=bands,
            expected_initial_derivative_sign=1,
        )
