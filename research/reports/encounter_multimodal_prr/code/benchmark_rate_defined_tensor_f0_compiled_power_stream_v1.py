"""Measured method benchmark for the compiled packed power-stream backend.

This benchmark has no command-line inputs.  It compares the compiled stream,
which includes both positive reductions at every power, against the current
Python batch action alone.  Consequently the reported speedup is conservative
for action-stream integration.  A timing is never a resource or F0 PASS.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import time
import types
from fractions import Fraction

import numpy as np
import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled


def _python_kernel(source: compiled.GenericPackedTensorInput) -> object:
    class Kernel:
        pass

    kernel = Kernel()
    kernel.states = math.prod(source.tensor_shape)
    kernel.contract = types.SimpleNamespace(
        tensor_shape=source.tensor_shape,
        block_size=source.reduction_block_size,
    )
    kernel.axes = tuple(
        types.SimpleNamespace(size=size, periodic=is_periodic)
        for size, is_periodic in zip(
            source.tensor_shape,
            source.periodic,
            strict=True,
        )
    )
    kernel.p_self_center = source.p_self_center
    kernel.p_forward_center = source.p_forward_center
    kernel.p_backward_center = source.p_backward_center
    return kernel


def _python_stream(
    source: compiled.GenericPackedTensorInput,
    initial: np.ndarray,
    powers: int,
) -> np.ndarray:
    kernel = _python_kernel(source)
    workspace = batched._make_fast_workspace(
        min(kernel.states, source.reduction_block_size)
    )
    current = initial.copy()
    following = np.empty_like(current)
    for _ in range(powers):
        batched._fast_p_transpose_into(
            kernel,
            current,
            following,
            workspace,
        )
        current, following = following, current
    return current


def _heterogeneous_small() -> tuple[
    compiled.GenericPackedTensorInput,
    np.ndarray,
]:
    shape = (2, 3, 2)
    states = math.prod(shape)
    source = compiled.GenericPackedTensorInput(
        tensor_shape=shape,
        periodic=(True, False, True),
        p_self_center=np.asarray(
            [
                float(Fraction(8 + index % 5, 32))
                for index in range(states)
            ],
            dtype=np.float64,
        ),
        p_forward_center=(
            np.asarray([1 / 32, 2 / 32], dtype=np.float64),
            np.asarray([1 / 64, 2 / 64, 0.0], dtype=np.float64),
            np.asarray([2 / 64, 3 / 64], dtype=np.float64),
        ),
        p_backward_center=(
            np.asarray([2 / 32, 1 / 32], dtype=np.float64),
            np.asarray([0.0, 3 / 64, 1 / 64], dtype=np.float64),
            np.asarray([3 / 64, 2 / 64], dtype=np.float64),
        ),
        killing_center=np.asarray(
            [(index + 1) / 256 for index in range(states)],
            dtype=np.float64,
        ),
        reduction_block_size=4,
    )
    initial = np.asarray(
        [float(Fraction(index + 1, 128)) for index in range(states)],
        dtype=np.float64,
    )
    return source, initial


def _neutral_100k() -> tuple[
    compiled.GenericPackedTensorInput,
    np.ndarray,
]:
    shape = (100, 1000)
    states = math.prod(shape)
    source = compiled.GenericPackedTensorInput(
        tensor_shape=shape,
        periodic=(False, False),
        p_self_center=np.full(states, 0.75, dtype=np.float64),
        p_forward_center=(
            np.concatenate((np.full(99, 0.05), np.asarray([0.0]))),
            np.concatenate((np.full(999, 0.025), np.asarray([0.0]))),
        ),
        p_backward_center=(
            np.concatenate((np.asarray([0.0]), np.full(99, 0.05))),
            np.concatenate((np.asarray([0.0]), np.full(999, 0.025))),
        ),
        killing_center=np.full(states, 0.01, dtype=np.float64),
        reduction_block_size=64,
    )
    initial = np.zeros(states, dtype=np.float64)
    initial[states // 2] = 1.0
    return source, initial


def _measure_case(
    name: str,
    source: compiled.GenericPackedTensorInput,
    initial: np.ndarray,
    *,
    powers: int,
    repeats: int,
) -> tuple[dict[str, object], compiled.CompiledBackendReceipt]:
    backend = compiled.build_compiled_power_stream_backend(source)
    compiled_result = backend.run_power_stream(
        initial,
        maximum_power=powers,
    )
    python_result = _python_stream(source, initial, powers)
    if compiled_result.final_power.tobytes() != python_result.tobytes():
        raise RuntimeError(f"{name}: compiled and Python final bytes disagree")
    compiled_durations: list[float] = []
    python_durations: list[float] = []
    repeat_hashes: list[str] = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = backend.run_power_stream(initial, maximum_power=powers)
        compiled_durations.append(time.perf_counter() - started)
        repeat_hashes.append(
            hashlib.sha256(result.final_power.tobytes()).hexdigest()
        )
    for _ in range(repeats):
        started = time.perf_counter()
        _python_stream(source, initial, powers)
        python_durations.append(time.perf_counter() - started)
    compiled_median = statistics.median(compiled_durations)
    python_median = statistics.median(python_durations)
    return (
        {
            "case": name,
            "states": backend.states,
            "dimensions": len(source.tensor_shape),
            "powers": powers,
            "repeats": repeats,
            "compiled_stream_includes_mass_and_killing_dot": True,
            "python_baseline_is_current_batch_action_only": True,
            "compiled_median_seconds": compiled_median,
            "python_median_seconds": python_median,
            "speedup_over_python_action_only": python_median / compiled_median,
            "final_power_byte_equal": True,
            "compiled_output_byte_repeatable": len(set(repeat_hashes)) == 1,
            "resource_pass": False,
            "f0_pass": False,
        },
        backend.receipt,
    )


def main() -> None:
    small_source, small_initial = _heterogeneous_small()
    large_source, large_initial = _neutral_100k()
    small, small_receipt = _measure_case(
        "heterogeneous_3d_small",
        small_source,
        small_initial,
        powers=32,
        repeats=7,
    )
    large, large_receipt = _measure_case(
        "neutral_2d_100k",
        large_source,
        large_initial,
        powers=4,
        repeats=5,
    )
    if small_receipt.build != large_receipt.build:
        raise RuntimeError("benchmark cases did not share one compiled artifact")
    payload = {
        "schema": "rate_defined_tensor_f0_compiled_power_stream_benchmark_v1",
        "status": "MEASURED_METHOD_BENCHMARK_ONLY_NOT_RESOURCE_PASS",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "build": {
            "c_source_sha256": small_receipt.build.c_source_sha256,
            "python_wrapper_sha256": (
                small_receipt.build.python_wrapper_sha256
            ),
            "compiler_binary_sha256": (
                small_receipt.build.compiler_binary_sha256
            ),
            "compiler_identity_sha256": (
                small_receipt.build.compiler_identity_sha256
            ),
            "normalized_compile_command_sha256": (
                small_receipt.build.normalized_compile_command_sha256
            ),
            "post_link_normalization_sha256": (
                small_receipt.build.post_link_normalization_sha256
            ),
            "compiled_binary_sha256": (
                small_receipt.build.compiled_binary_sha256
            ),
            "target_identity_sha256": (
                small_receipt.build.target_identity_sha256
            ),
            "fe_tonearest": small_receipt.build.runtime_probe.tonearest_active,
            "subnormal_preserved": (
                small_receipt.build.runtime_probe.subnormal_arithmetic_preserved
            ),
            "fast_math_enabled": False,
            "fp_contraction_enabled": False,
        },
        "cases": [small, large],
        "input_provenance_classification": (
            compiled.INPUT_PROVENANCE_CLASSIFICATION
        ),
        "authorizes_scientific_execution": False,
        "science_executed": False,
        "resource_pass": False,
        "f0_pass": False,
    }
    print(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

