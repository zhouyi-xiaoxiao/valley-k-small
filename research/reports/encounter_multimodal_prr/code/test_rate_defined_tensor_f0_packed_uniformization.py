from __future__ import annotations

import ast
import hashlib
import math
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action
import rate_defined_tensor_f0_packed_uniformization as uniformization

MAXIMUM_WORKING_BYTES = 2_000_000
PROVENANCE = hashlib.sha256(b"tiny-uniformization-declared-input").hexdigest()


def _payload(
    rows: tuple[tuple[float, float], ...],
    *,
    role: str,
    logical_shape: tuple[int, ...],
) -> packed.PackedIntervalPayload:
    return packed.create_packed_interval_payload(
        rows,
        role=role,
        logical_shape=logical_shape,
        nonnegative=True,
        block_size=2,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )


def _problem(
    *,
    forward: tuple[float, float] = (0.5, 0.0),
    backward: tuple[float, float] = (0.0, 0.25),
    killing: tuple[float, float] = (0.0, 0.0),
    initial_values: tuple[float, float] = (1.0, 0.0),
    initial_radius: float = 0.0,
) -> tuple[
    packed.PackedTensorKernel,
    rate_action.InternalPointBallInput,
    rate_action.RateActionContract,
]:
    axis_name = "tiny_axis"
    inputs = packed.PackedKernelInputs(
        axes=(
            packed.PackedAxisPayload(
                name=axis_name,
                size=2,
                periodic=False,
                forward=_payload(
                    tuple((value, value) for value in forward),
                    role=f"science_free_axis_{axis_name}_forward",
                    logical_shape=(2,),
                ),
                backward=_payload(
                    tuple((value, value) for value in backward),
                    role=f"science_free_axis_{axis_name}_backward",
                    logical_shape=(2,),
                ),
            ),
        ),
        killing=_payload(
            tuple((value, value) for value in killing),
            role="science_free_killing",
            logical_shape=(2,),
        ),
    )
    kernel = packed.build_packed_tensor_kernel(
        inputs,
        packed.KernelBuildContract(
            tensor_shape=(2,),
            block_size=2,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
            uniformization_rate=Fraction(1),
        ),
    )
    directed_contract = directed.make_directed_action_contract(
        (2,),
        block_size=2,
        maximum_scratch_bytes=MAXIMUM_WORKING_BYTES,
    )
    contract = rate_action.make_rate_action_contract(
        directed_contract,
        maximum_numeric_payload_bytes=MAXIMUM_WORKING_BYTES,
        maximum_total_payload_bytes=MAXIMUM_WORKING_BYTES,
    )
    values = np.array(initial_values, dtype=np.float64)
    values.setflags(write=False)
    raw = hashlib.sha256(memoryview(values).cast("B")).hexdigest()
    vector = packed.CanonicalFloat64Vector(
        logical_shape=(2,),
        values=values,
        raw_sha256=raw,
        nonnegative=True,
        source_sha256=hashlib.sha256(b"tiny-source" + bytes.fromhex(raw)).hexdigest(),
    )
    initial = rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=initial_radius,
        radius_provenance_sha256=PROVENANCE,
    )
    return kernel, initial, contract


def _run(
    *,
    time: Fraction = Fraction(1, 2),
    tail_tolerance: Fraction = Fraction(1, 2**36),
    **problem: object,
) -> uniformization.TinyUniformizationResult:
    kernel, initial, contract = _problem(**problem)
    return uniformization.tiny_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=time,
        tail_tolerance=tail_tolerance,
        maximum_terms=64,
    )


def test_two_state_chain_encloses_independent_closed_form() -> None:
    result = _run()
    time = 0.5
    decay = math.exp(-0.75 * time)
    exact = np.array(
        [1.0 / 3.0 + 2.0 * decay / 3.0, 2.0 * (1.0 - decay) / 3.0],
        dtype=np.float64,
    )
    distance = float(np.sum(np.abs(result.nominal - exact)))
    assert distance <= result.l1_radius_upper
    assert result.uniformization_rate == 1
    assert result.poisson_mean == Fraction(1, 2)
    assert result.fixed_rate_rechecked_count == result.resources.p_action_calls + 2
    assert result.poisson.tail_probability_upper <= Fraction(1, 2**36)
    assert result.mass.conditional_target_nonnegative is True
    assert result.mass.authoritative_target_nonnegative_proved is False
    assert result.mass.enclosed_output_mass_upper == 1
    assert result.mass.maximum_target_exit_upper == Fraction(1, 2)
    assert result.mass.uniformization_slack == Fraction(1, 2)


def test_killing_chain_mass_loss_is_enclosed() -> None:
    result = _run(
        forward=(0.0, 0.0),
        backward=(0.0, 0.0),
        killing=(0.5, 0.25),
        time=Fraction(3, 4),
    )
    exact = np.array([math.exp(-3.0 / 8.0), 0.0], dtype=np.float64)
    assert float(np.sum(np.abs(result.nominal - exact))) <= result.l1_radius_upper
    assert 0 <= result.mass.enclosed_output_mass_lower
    assert result.mass.enclosed_output_mass_upper <= 1
    assert result.mass.fixed_uniformized_operator_substochastic is True


def test_zero_time_is_exact_and_uses_no_rate_actions() -> None:
    result = _run(time=Fraction(0), initial_values=(0.25, 0.75))
    assert np.array_equal(result.nominal, np.array([0.25, 0.75], dtype=np.float64))
    assert result.l1_radius_exact_upper == 0
    assert result.l1_radius_upper == 0.0
    assert len(result.poisson.weights) == 1
    assert result.poisson.weights[0].lower == 1
    assert result.poisson.weights[0].upper == 1
    assert result.poisson.tail_probability_upper == 0
    assert result.resources.p_action_calls == 0


def test_exact_poisson_recurrence_and_tail_balance() -> None:
    ledger = uniformization._poisson_recurrence(
        Fraction(3, 4),
        tail_tolerance=Fraction(1, 2**48),
        maximum_terms=64,
    )
    for index in range(1, len(ledger.weights)):
        factor = ledger.mean / index
        assert ledger.weights[index].lower == ledger.weights[index - 1].lower * factor
        assert ledger.weights[index].upper == ledger.weights[index - 1].upper * factor
    assert ledger.normalization_tail_probability_upper == 1 - sum(
        (weight.lower for weight in ledger.weights),
        Fraction(0),
    )
    assert ledger.first_omitted_probability_upper == (
        ledger.weights[-1].upper * ledger.mean / len(ledger.weights)
    )
    assert ledger.geometric_tail_ratio_upper == ledger.mean / (len(ledger.weights) + 1)
    assert ledger.geometric_tail_probability_upper == (
        ledger.first_omitted_probability_upper / (1 - ledger.geometric_tail_ratio_upper)
    )
    assert ledger.tail_probability_upper == min(
        ledger.normalization_tail_probability_upper,
        ledger.geometric_tail_probability_upper,
    )
    assert ledger.tail_probability_lower == max(
        Fraction(0),
        1 - sum((weight.upper for weight in ledger.weights), Fraction(0)),
    )
    assert ledger.exp_mu_lower <= ledger.exp_mu_upper
    assert ledger.exp_remainder_relative_upper <= ledger.requested_tail_tolerance / 8


def test_poisson_endpoints_enclose_independent_alternating_series() -> None:
    mean = Fraction(3, 4)
    ledger = uniformization._poisson_recurrence(
        mean,
        tail_tolerance=Fraction(1, 2**48),
        maximum_terms=64,
    )
    partial = Fraction(1)
    term = Fraction(1)
    even_upper = Fraction(1)
    odd_lower = Fraction(0)
    for degree in range(1, 82):
        term *= -mean / degree
        partial += term
        if degree == 80:
            even_upper = partial
        elif degree == 81:
            odd_lower = partial
    assert ledger.weights[0].lower <= odd_lower <= even_upper <= ledger.weights[0].upper
    factor_sum = Fraction(0)
    factor = Fraction(1)
    for index in range(len(ledger.weights)):
        if index:
            factor *= mean / index
        factor_sum += factor
        assert ledger.weights[index].lower <= odd_lower * factor
        assert ledger.weights[index].upper >= even_upper * factor
    independent_tail_lower = max(Fraction(0), 1 - even_upper * factor_sum)
    independent_tail_upper = 1 - odd_lower * factor_sum
    assert ledger.tail_probability_lower <= independent_tail_lower
    assert ledger.tail_probability_upper >= independent_tail_upper


def test_tiny_mean_boundaries_and_k_zero_one_cases() -> None:
    subnormal_dyadic = Fraction(1, 2**1074)
    tiny = uniformization._poisson_recurrence(
        subnormal_dyadic,
        tail_tolerance=Fraction(1, 2**40),
        maximum_terms=64,
    )
    assert len(tiny.weights) == 1
    assert tiny.tail_probability_upper <= Fraction(1, 2**40)

    at_cap = uniformization._poisson_recurrence(
        Fraction(1),
        tail_tolerance=Fraction(1, 2**40),
        maximum_terms=64,
    )
    assert at_cap.mean == 1
    assert at_cap.tail_probability_upper <= Fraction(1, 2**40)

    k_zero = uniformization._poisson_recurrence(
        Fraction(1, 16),
        tail_tolerance=Fraction(1, 4),
        maximum_terms=64,
    )
    k_one = uniformization._poisson_recurrence(
        Fraction(1, 2),
        tail_tolerance=Fraction(1, 4),
        maximum_terms=64,
    )
    assert len(k_zero.weights) == 1
    assert len(k_one.weights) == 2


def test_all_public_ledgers_are_explicitly_non_authoritative_and_science_free() -> None:
    result = _run(tail_tolerance=Fraction(1, 2**24))
    for output in (
        result,
        result.accepted_rate_action,
        result.poisson,
        result.powers,
        result.mass,
        result.resources,
    ):
        assert output.non_authoritative is True
        assert output.science_free is True
        assert output.fresh_process is False
        assert output.f0_pass is False
    assert result.status == uniformization.METHOD_STATUS
    assert result.resources.production_memory_exact is False
    assert result.resources.production_scale_executed is False
    assert result.jets_complete is False
    assert result.topology_complete is False
    assert result.production_resource_gate is False


def test_accepted_bytes_and_tiny_resource_ledger_are_bound() -> None:
    result = _run(tail_tolerance=Fraction(1, 2**24))
    assert result.accepted_rate_action.source_sha256 == (
        uniformization.ACCEPTED_RATE_ACTION_SOURCE_SHA256
    )
    assert result.accepted_rate_action.packed_source_sha256 == (
        uniformization.ACCEPTED_PACKED_SOURCE_SHA256
    )
    assert result.accepted_rate_action.directed_source_sha256 == (
        uniformization.ACCEPTED_DIRECTED_SOURCE_SHA256
    )
    assert result.accepted_rate_action.test_sha256 == (
        uniformization.ACCEPTED_RATE_ACTION_TEST_SHA256
    )
    assert result.accepted_rate_action.exact_bytes_matched is True
    assert result.resources.state_count == 2
    assert result.resources.state_cap == 64
    assert result.resources.poisson_terms_used <= result.resources.poisson_term_cap
    assert result.resources.poisson_terms_used <= result.resources.maximum_terms_requested
    assert result.resources.maximum_terms_requested == 64
    assert result.resources.poisson_mean_cap == 1
    assert result.resources.exact_state_accumulator_count == 2
    assert result.resources.returned_numpy_payload_bytes == 16
    assert result.resources.declared_peak_excluding_preowned_kernel_upper_bytes >= 32
    assert result.resources.subordinate_peak_excludes_preowned_kernel is True
    assert result.resources.preowned_kernel_numpy_payload_bytes == 208
    assert result.resources.declared_peak_including_preowned_kernel_upper_bytes == (
        result.resources.declared_peak_excluding_preowned_kernel_upper_bytes + 208
    )
    assert result.resources.python_object_payload_measured is False
    assert result.resources.method_diagnostic_only is True
    assert result.resources.exact_memory_claim is False


def test_predecessor_chain_replays_and_rejects_reset_mutation() -> None:
    result = _run(tail_tolerance=Fraction(1, 2**24))
    powers = result.powers
    assert len(powers.steps) == result.resources.p_action_calls
    assert powers.caller_continuation_inputs_accepted is False
    assert powers.predecessor_chain_complete is True
    for index, step in enumerate(powers.steps):
        assert step.action_index == index
        assert step.chain_sha256 == uniformization._power_step_digest(step)

    assert len(powers.steps) >= 2
    second = powers.steps[1]
    reset = replace(
        second,
        input_nominal_raw_sha256=powers.steps[0].input_nominal_raw_sha256,
        chain_sha256="0" * 64,
    )
    reset = replace(reset, chain_sha256=uniformization._power_step_digest(reset))
    mutated = replace(powers, steps=(powers.steps[0], reset, *powers.steps[2:]))
    with pytest.raises(uniformization.TinyUniformizationFailure, match="skipped or reset"):
        uniformization._validate_power_ledger(mutated)


def test_numpy_cap_rejects_before_first_p_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel, initial, contract = _problem()
    kernel_bytes = uniformization._kernel_numpy_payload_bytes(kernel)
    predicted = kernel_bytes + max(
        3 * initial.nominal.nbytes + min(kernel.states, contract.block_size),
        contract.required_peak_numeric_payload_bytes + initial.nominal.nbytes,
    )
    called = False

    def forbidden_action(*_: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("rate action must not run after a failed preflight")

    monkeypatch.setattr(uniformization, "MAX_TINY_NUMPY_PAYLOAD_BYTES", predicted - 1)
    monkeypatch.setattr(rate_action, "_rate_defined_p_transpose", forbidden_action)
    with pytest.raises(uniformization.TinyUniformizationFailure, match="payload hard cap"):
        uniformization.tiny_uniformize_transpose(
            kernel,
            initial,
            contract,
            time=Fraction(1, 2),
            tail_tolerance=Fraction(1, 2**24),
        )
    assert called is False


def test_fail_closed_bounds_and_nonnegative_input_precondition() -> None:
    with pytest.raises(uniformization.TinyUniformizationFailure, match="mean"):
        uniformization._poisson_recurrence(
            Fraction(5),
            tail_tolerance=Fraction(1, 2**20),
            maximum_terms=32,
        )
    with pytest.raises(uniformization.TinyUniformizationFailure, match="term cap"):
        uniformization._poisson_recurrence(
            Fraction(1),
            tail_tolerance=Fraction(1, 2**70),
            maximum_terms=1,
        )
    with pytest.raises(uniformization.TinyUniformizationFailure, match="nonnegative"):
        _run(initial_values=(0.0, 0.8), initial_radius=0.1)
    with pytest.raises(uniformization.TinyUniformizationFailure, match="negative zero"):
        _run(initial_values=(-0.0, 1.0))


def test_source_hash_mismatch_fails_before_method(monkeypatch: pytest.MonkeyPatch) -> None:
    kernel, initial, contract = _problem()
    monkeypatch.setattr(uniformization, "ACCEPTED_RATE_ACTION_SOURCE_SHA256", "0" * 64)
    with pytest.raises(uniformization.TinyUniformizationFailure, match="byte binding"):
        uniformization.tiny_uniformize_transpose(
            kernel,
            initial,
            contract,
            time=Fraction(1, 2),
            tail_tolerance=Fraction(1, 2**24),
        )


def test_module_import_surface_is_local_and_bounded() -> None:
    source = Path(uniformization.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots <= {
        "__future__",
        "dataclasses",
        "fractions",
        "hashlib",
        "math",
        "numpy",
        "pathlib",
        "rate_defined_tensor_f0_packed",
        "rate_defined_tensor_f0_packed_interval_action",
        "rate_defined_tensor_f0_packed_rate_action",
        "typing",
    }
