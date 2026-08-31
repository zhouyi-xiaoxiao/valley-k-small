#!/usr/bin/env python3
"""Capped, science-free resource probes for the frozen tensor F0 core.

This utility never reads a selector, a prospective control, or a design note.
It uses only synthetic neutral axes, a repeated synthetic killing interval,
and (for the topology call-count probe) an analytic one-root polynomial.

The allocation modes are deliberately hard-capped below the 7,165,305-state
production shape.  The target-shape mode is static accounting only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import resource
import sys
import time
from fractions import Fraction
from types import SimpleNamespace
from typing import Any, Sequence

import numpy as np
import rate_defined_tensor_f0 as f0

TARGET_SHAPE = (207, 215, 161)
TARGET_STATES = math.prod(TARGET_SHAPE)
MAX_BUILD_STATES = 300_000
MAX_ACTION_STATES = 1_000_000
MAX_ORACLE_STATES = 100_000
SYNTHETIC_KILLING = Fraction(1, 256)


def _rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # macOS reports bytes; Linux reports KiB.
    return value if sys.platform == "darwin" else value * 1024


def _shape(text: str) -> tuple[int, int, int]:
    try:
        values = tuple(int(value) for value in text.lower().split("x"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("shape must be AxBxC") from error
    if len(values) != 3 or min(values) < 3:
        raise argparse.ArgumentTypeError("shape must contain three dimensions >= 3")
    return values


def _fraction(text: str) -> Fraction:
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError("expected an exact rational") from error


def _neutral_axes(shape: tuple[int, int, int]) -> tuple[f0.TensorAxis, ...]:
    midpoint_cells, relative_cells, transverse_cells = shape
    midpoint = f0.build_reflecting_sg_axis(
        "resource_probe_midpoint",
        tuple(Fraction(index, midpoint_cells - 1) for index in range(midpoint_cells)),
        (Fraction(0),) * midpoint_cells,
        Fraction(1, 1000),
    )
    relative = f0.build_periodic_diffusion_axis(
        "resource_probe_relative",
        relative_cells,
        Fraction(1),
        Fraction(1, 2000),
    )
    transverse = f0.build_periodic_diffusion_axis(
        "resource_probe_transverse",
        transverse_cells,
        Fraction(1),
        Fraction(1, 2000),
        half_cell_shift=True,
    )
    return midpoint, relative, transverse


def _neutral_kernel(shape: tuple[int, int, int]) -> f0.RateDefinedTensorKernel:
    axes = _neutral_axes(shape)
    interval = f0.OutwardInterval.from_fraction(SYNTHETIC_KILLING)
    # One shared interval object keeps the probe neutral and makes the frozen
    # builder, rather than a physical interval expansion, the measured object.
    killing = (interval,) * math.prod(shape)
    return f0.build_rate_defined_tensor_kernel(axes, killing)


def _neutral_initial(states: int) -> f0.InitialStateEnclosure:
    payload = b"science-free-neutral-uniform-initial-v1"
    digest = hashlib.sha256(payload).hexdigest()
    interval = f0.OutwardInterval.from_fraction(Fraction(1, states))
    return f0.enclose_initial_state(
        (interval,) * states,
        source_payload_bytes=payload,
        expected_source_sha256=digest,
        maximum_l1_error=1.0e-10,
    )


def _object_sizes() -> dict[str, int | float]:
    intervals = [f0.OutwardInterval(float(index), float(index) + 0.25) for index in range(1_000)]
    fractions = [Fraction(index + 123_456, index + 123_457) for index in range(1_000)]
    interval_bulk = sum(
        sys.getsizeof(value)
        + sys.getsizeof(value.__dict__)
        + sys.getsizeof(value.lower)
        + sys.getsizeof(value.upper)
        + 8
        for value in intervals
    ) / len(intervals)
    fraction_bulk = sum(
        sys.getsizeof(value) + sys.getsizeof(value.numerator) + sys.getsizeof(value.denominator)
        for value in fractions
    ) / len(fractions)
    return {
        "tuple_pointer_bytes": sys.getsizeof((None,)) - sys.getsizeof(tuple()),
        "outward_interval_bulk_deep_bytes_per_entry_including_tuple_slot": interval_bulk,
        "fraction_bulk_deep_bytes_per_value": fraction_bulk,
        "fraction_object_header_bytes_excluding_integer_payloads": sys.getsizeof(Fraction(1, 3)),
        "two_fraction_tuple_header_bytes": sys.getsizeof((Fraction(1), Fraction(2))),
    }


def static_accounting() -> dict[str, Any]:
    n = TARGET_STATES
    full = n * np.dtype(np.float64).itemsize
    sizes = _object_sizes()
    # Retained simultaneously in build_rate_defined_tensor_kernel at the end
    # of its second state loop: one 2-Fraction tuple list and three Fraction
    # lists.  This is intentionally a lower bound: Fraction numerator and
    # denominator integer payloads are excluded.
    builder_python_header_floor_per_state = (
        8
        + int(sizes["two_fraction_tuple_header_bytes"])
        + 2 * int(sizes["fraction_object_header_bytes_excluding_integer_payloads"])
        + 3 * (8 + int(sizes["fraction_object_header_bytes_excluding_integer_payloads"]))
    )
    bulk_interval = float(sizes["outward_interval_bulk_deep_bytes_per_entry_including_tuple_slot"])
    return {
        "stage": "f0_largest_resource_static_accounting",
        "status": "HOLD_LARGEST_ALLOCATION_STATIC_ONLY",
        "prospective_control_values_read": False,
        "positive_budget_primary_control_evaluated": False,
        "target_shape": list(TARGET_SHAPE),
        "target_states": n,
        "object_sizes": sizes,
        "bytes": {
            "one_full_float64_array": full,
            "kernel_three_full_state_numeric_arrays": 3 * full,
            "kernel_axis_numeric_arrays": 4 * sum(TARGET_SHAPE) * 8,
            "one_full_tuple_pointer_vector": n * 8 + sys.getsizeof(tuple()),
            "matrix_free_action_internal_ten_array_peak": 10 * full,
            "jet_five_saved_nominal_action_arrays": 5 * full,
            "propagation_jet_numeric_twenty_array_working_estimate": 20 * full,
            "one_distinct_interval_tuple_bulk_deep_estimate": int(math.ceil(n * bulk_interval)),
            "two_distinct_interval_tuples_bulk_deep_estimate": int(
                math.ceil(2 * n * bulk_interval)
            ),
            "builder_retained_python_header_floor_excluding_integer_payloads": (
                n * builder_python_header_floor_per_state
            ),
        },
        "builder_python_header_floor_bytes_per_state": builder_python_header_floor_per_state,
        "largest_allocation_executed": False,
        "decision": "UNSAFE_TO_BUILD_TARGET_WITH_FROZEN_OBJECT_REPRESENTATION",
    }


def build_probe(shape: tuple[int, int, int]) -> dict[str, Any]:
    states = math.prod(shape)
    if states > MAX_BUILD_STATES:
        raise SystemExit(f"build probe hard cap is {MAX_BUILD_STATES} states")
    start = time.perf_counter()
    cpu_start = time.process_time()
    kernel = _neutral_kernel(shape)
    cpu_elapsed = time.process_time() - cpu_start
    elapsed = time.perf_counter() - start
    return {
        "stage": "f0_neutral_capped_build_probe",
        "shape": list(shape),
        "states": states,
        "seconds": elapsed,
        "cpu_seconds": cpu_elapsed,
        "maximum_rss_bytes": _rss_bytes(),
        "rate": kernel.rate,
        "delta_p": kernel.delta_p,
        "killing_interval_objects_shared": True,
        "hard_state_cap": MAX_BUILD_STATES,
    }


def action_probe(shape: tuple[int, int, int], actions: int) -> dict[str, Any]:
    states = math.prod(shape)
    if states > MAX_ACTION_STATES:
        raise SystemExit(f"action probe hard cap is {MAX_ACTION_STATES} states")
    if not 1 <= actions <= 20:
        raise SystemExit("actions must be in 1..20")
    axes = tuple(
        f0.build_periodic_diffusion_axis(
            f"resource_probe_action_axis_{index}",
            cells,
            Fraction(1),
            Fraction(1, 2000),
        )
        for index, cells in enumerate(shape)
    )
    coefficient = 1.0 / 7.0
    kernel = SimpleNamespace(
        states=states,
        shape=shape,
        axes=axes,
        p_self_center=np.full(states, coefficient, dtype=np.float64),
        p_forward_center=tuple(np.full(axis.size, coefficient, dtype=np.float64) for axis in axes),
        p_backward_center=tuple(np.full(axis.size, coefficient, dtype=np.float64) for axis in axes),
        maximum_incoming_terms=7,
    )
    state = np.full(states, 1.0 / states, dtype=np.float64)
    start = time.perf_counter()
    cpu_start = time.process_time()
    for _ in range(actions):
        state = f0._matrix_free_p_transpose(kernel, state, check_runtime=False)
    cpu_elapsed = time.process_time() - cpu_start
    elapsed = time.perf_counter() - start
    return {
        "stage": "f0_neutral_capped_action_allocation_probe",
        "shape": list(shape),
        "states": states,
        "actions": actions,
        "seconds": elapsed,
        "seconds_per_action": elapsed / actions,
        "cpu_seconds": cpu_elapsed,
        "cpu_seconds_per_action": cpu_elapsed / actions,
        "maximum_rss_bytes": _rss_bytes(),
        "output_mass": float(np.sum(state)),
        "synthetic_kernel_is_certificate": False,
        "hard_state_cap": MAX_ACTION_STATES,
    }


def oracle_probe(shape: tuple[int, int, int], target_time: Fraction) -> dict[str, Any]:
    states = math.prod(shape)
    if states > MAX_ORACLE_STATES:
        raise SystemExit(f"oracle probe hard cap is {MAX_ORACLE_STATES} states")
    start = time.perf_counter()
    cpu_start = time.process_time()
    kernel = _neutral_kernel(shape)
    initial = _neutral_initial(states)
    oracle = f0.MatrixFreeAbsoluteTimeJetOracle(kernel=kernel, initial=initial)
    sample = oracle(target_time)
    cpu_elapsed = time.process_time() - cpu_start
    elapsed = time.perf_counter() - start
    _, _, _, chunks = f0._matrix_free_propagation_contract(
        kernel,
        target_time,
        oracle.mean_cap,
        oracle.total_tail_tolerance,
        oracle.precision_bits,
        oracle.maximum_terms,
        oracle.maximum_chunks,
    )
    mean = kernel.rate_fraction * target_time / chunks
    probabilities = f0.reference.poisson_enclosure(
        mean,
        oracle.total_tail_tolerance / chunks,
        precision_bits=oracle.precision_bits,
        max_terms=oracle.maximum_terms,
    )
    terms = int(probabilities.midpoint.size)
    return {
        "stage": "f0_neutral_capped_absolute_time_oracle_probe",
        "shape": list(shape),
        "states": states,
        "target_time": str(target_time),
        "seconds": elapsed,
        "cpu_seconds": cpu_elapsed,
        "maximum_rss_bytes": _rss_bytes(),
        "chunk_count": chunks,
        "terms_per_chunk": terms,
        "three_pass_p_actions": 3 * chunks * (terms - 1),
        "jet_q_actions": 4,
        "jets_returned": len(sample.jets),
        "hard_state_cap": MAX_ORACLE_STATES,
    }


def validation_probe(shape: tuple[int, int, int], repeats: int) -> dict[str, Any]:
    states = math.prod(shape)
    if states > MAX_ORACLE_STATES:
        raise SystemExit(f"validation probe hard cap is {MAX_ORACLE_STATES} states")
    if not 1 <= repeats <= 5:
        raise SystemExit("validation repeats must be in 1..5")
    kernel = _neutral_kernel(shape)
    initial = _neutral_initial(states)
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    for _ in range(repeats):
        f0.validate_rate_defined_tensor_kernel(kernel)
        f0.validate_initial_state_enclosure(initial, expected_states=states)
    cpu_elapsed = time.process_time() - cpu_start
    wall_elapsed = time.perf_counter() - wall_start
    return {
        "stage": "f0_neutral_capped_exact_validation_probe",
        "shape": list(shape),
        "states": states,
        "repeats": repeats,
        "seconds": wall_elapsed,
        "seconds_per_kernel_plus_initial_validation": wall_elapsed / repeats,
        "cpu_seconds": cpu_elapsed,
        "cpu_seconds_per_kernel_plus_initial_validation": cpu_elapsed / repeats,
        "maximum_rss_bytes": _rss_bytes(),
        "hard_state_cap": MAX_ORACLE_STATES,
    }


class _CountingPolynomialOracle:
    """Rigorous synthetic f(t)=-(t-1)^2 oracle with a narrow derivative radius."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, time_value: Fraction) -> f0.TimeJetSample:
        self.calls += 1
        epsilon = Fraction(1, 1000)
        displacement = time_value - 1
        derivative = -2 * displacement
        return f0.TimeJetSample(
            time=time_value,
            jets=(
                f0.OutwardInterval.from_fraction(-(displacement**2)),
                f0.OutwardInterval.from_fraction_bounds(derivative - epsilon, derivative + epsilon),
                f0.OutwardInterval.from_fraction(-2),
                f0.OutwardInterval.from_fraction(0),
            ),
            m2=Fraction(2),
            m3=Fraction(0),
            m4=Fraction(0),
            direct_from_initial=True,
        )


def topology_count_probe() -> dict[str, Any]:
    oracle = _CountingPolynomialOracle()
    certificate = f0.certify_full_window_topology(
        oracle,
        window_lower=Fraction(0),
        window_upper=Fraction(2),
        root_bands=(f0.RootBand("P1", Fraction(1, 2), Fraction(3, 2), "maximum"),),
        initial_derivative_sign=1,
    )
    return {
        "stage": "f0_synthetic_full_topology_call_count_probe",
        "status": "PASS_METHOD_ONLY_SYNTHETIC_TOPOLOGY",
        "oracle_calls_including_fresh_audit": oracle.calls,
        "saved_tiles": len(certificate.tiles),
        "saved_roots": len(certificate.roots),
        "candidate_tiles": sum(tile.candidate for tile in certificate.tiles),
        "prospective_control_values_read": False,
        "positive_budget_primary_control_evaluated": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science-free-neutral", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("static", "build", "action", "oracle", "validate", "topology-count"),
        required=True,
    )
    parser.add_argument("--shape", type=_shape, default=(17, 16, 16))
    parser.add_argument("--actions", type=int, default=3)
    parser.add_argument("--target-time", type=_fraction, default=Fraction(1, 2))
    args = parser.parse_args(argv)
    if not args.science_free_neutral:
        raise SystemExit("explicit --science-free-neutral is required")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "static":
        payload = static_accounting()
    elif args.mode == "build":
        payload = build_probe(args.shape)
    elif args.mode == "action":
        payload = action_probe(args.shape, args.actions)
    elif args.mode == "oracle":
        payload = oracle_probe(args.shape, args.target_time)
    elif args.mode == "validate":
        payload = validation_probe(args.shape, args.actions)
    else:
        payload = topology_count_probe()
    payload.update(
        {
            "probe_core_sha256": "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5",
            "largest_allocation_executed": False,
            "authorized_scientific_command": None,
        }
    )
    print(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
