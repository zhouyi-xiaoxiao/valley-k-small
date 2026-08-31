from __future__ import annotations

import dataclasses
import hashlib
import inspect
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_uniformization as tiny_uniformization
import rate_defined_tensor_f0_production_operator_v1 as operator


def _point(value: Fraction) -> tuple[float, float]:
    exact = float(value)
    assert Fraction.from_float(exact) == value
    return exact, exact


def _small_spec() -> operator.CallerSuppliedOperatorSpec:
    quarter = _point(Fraction(1, 4))
    eighth = _point(Fraction(1, 8))
    zero = (0.0, 0.0)
    one = (1.0, 1.0)
    x = operator.CallerSuppliedAxisSpec(
        name="synthetic_x",
        periodic=False,
        forward=(quarter, zero),
        backward=(zero, quarter),
        stationary_mass=(one, one),
    )
    y = operator.CallerSuppliedAxisSpec(
        name="synthetic_y",
        periodic=True,
        forward=(eighth, eighth, eighth),
        backward=(eighth, eighth, eighth),
        stationary_mass=(one, one, one),
    )
    killing = tuple(
        _point(Fraction(index + 1, 64)) for index in range(6)
    )
    return operator.CallerSuppliedOperatorSpec(
        fixture_role="caller_supplied_operator_oracle",
        tensor_shape=(2, 3),
        axes=(x, y),
        killing=killing,
        block_size=2,
        maximum_working_bytes=20_000,
    )


def _dense_oracle(
    candidate: operator.ProductionOperatorCandidate,
) -> tuple[np.ndarray, np.ndarray]:
    kernel = candidate.kernel
    shape = kernel.contract.tensor_shape
    q = np.zeros((kernel.states, kernel.states), dtype=np.float64)
    for flat in range(kernel.states):
        q[flat, flat] = kernel.diagonal_center[flat]
        coordinates = np.unravel_index(flat, shape)
        for dimension, axis in enumerate(kernel.axes):
            coordinate = coordinates[dimension]
            forward_coordinate = list(coordinates)
            backward_coordinate = list(coordinates)
            if axis.periodic or coordinate + 1 < axis.size:
                forward_coordinate[dimension] = (coordinate + 1) % axis.size
                q[flat, np.ravel_multi_index(tuple(forward_coordinate), shape)] += (
                    kernel.forward_center[dimension][coordinate]
                )
            if axis.periodic or coordinate > 0:
                backward_coordinate[dimension] = (coordinate - 1) % axis.size
                q[flat, np.ravel_multi_index(tuple(backward_coordinate), shape)] += (
                    kernel.backward_center[dimension][coordinate]
                )
    return q, np.eye(kernel.states) + q / kernel.rate


def test_small_caller_analysis_is_opaque_and_receipted() -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    operator.validate_opaque_caller_operator_analysis(analysis)
    receipt = analysis.receipt
    assert receipt.status == operator.CALLER_SUPPLIED_METHOD_STATUS
    assert receipt.stage == operator.METHOD_STAGE
    assert receipt.input_provenance == operator.CALLER_SUPPLIED_UNCLASSIFIED
    assert receipt.tensor_shape == (2, 3)
    assert receipt.state_count == 6
    assert receipt.axis_template_edge_count == 4
    assert receipt.possible_positive_killing_state_count == 6
    assert receipt.guaranteed_positive_killing_state_count == 6
    assert receipt.diagonal_derived_not_supplied
    assert receipt.q_killed_row_identity_enclosed
    assert receipt.p_submarkov
    assert receipt.pairwise_balance_interval_overlap
    assert not receipt.global_detailed_balance_witness
    assert receipt.killing_nonnegative
    assert receipt.packed_science_free_labels_are_backend_schema_only
    assert (
        receipt.source_hash_observation_scope
        == operator.SOURCE_HASH_OBSERVATION_SCOPE
    )
    assert not receipt.source_hashes_authoritative
    assert receipt.external_exact_byte_audit_required
    assert not receipt.external_exact_byte_audit_complete
    assert receipt.maximum_q_row_rounding_deficit == 0
    assert receipt.caller_supplied_unclassified_inputs
    assert not receipt.science_free_input_provenance
    assert not receipt.primary_control_excluded_by_construction
    assert not receipt.budget_excluded_by_construction
    assert not receipt.authorizes_scientific_execution
    assert not receipt.science_executed
    assert not receipt.measured_resource_evidence
    assert not receipt.production_resource_gate
    assert not receipt.f0_pass
    assert not analysis.packed_kernel_exposed
    assert not analysis.science_executed
    assert not analysis.production_resource_gate
    assert not analysis.f0_pass
    assert "kernel" not in {field.name for field in dataclasses.fields(analysis)}
    assert "stationary_masses" not in {
        field.name for field in dataclasses.fields(analysis)
    }
    assert not hasattr(analysis, "kernel")


def test_opaque_caller_analysis_cannot_enter_tiny_uniformization() -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    with pytest.raises(
        tiny_uniformization.TinyUniformizationFailure,
        match="kernel has the wrong exact type",
    ):
        tiny_uniformization.tiny_uniformize_transpose(
            analysis,  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            time=Fraction(0),
            tail_tolerance=Fraction(1, 2**36),
        )


def test_arbitrary_three_dimensional_shape_is_supported() -> None:
    zero = (0.0, 0.0)
    rate = _point(Fraction(1, 16))
    mass = (1.0, 1.0)
    axes = tuple(
        operator.CallerSuppliedAxisSpec(
            name=f"synthetic_axis_{dimension}",
            periodic=False,
            forward=(rate,) * (size - 1) + (zero,),
            backward=(zero,) + (rate,) * (size - 1),
            stationary_mass=(mass,) * size,
        )
        for dimension, size in enumerate((2, 3, 4))
    )
    spec = operator.CallerSuppliedOperatorSpec(
        fixture_role="caller_supplied_shape_generalization",
        tensor_shape=(2, 3, 4),
        axes=axes,
        killing=((0.0, 0.0),) * 24,
        block_size=5,
        maximum_working_bytes=20_000,
    )
    analysis = operator.build_caller_supplied_production_operator(spec)
    assert analysis.receipt.state_count == 24
    assert analysis.receipt.axis_template_edge_count == 1 + 2 + 3
    assert analysis.receipt.possible_positive_killing_state_count == 0
    assert analysis.receipt.guaranteed_positive_killing_state_count == 0
    assert analysis.receipt.maximum_killing_upper == 0
    operator.validate_opaque_caller_operator_analysis(analysis)


def test_repeated_killing_avoids_an_o_n_python_endpoint_tuple() -> None:
    spec = _small_spec()
    repeated = dataclasses.replace(
        spec,
        killing=operator.RepeatedCallerSuppliedInterval(0.125, 0.125),
    )
    analysis = operator.build_caller_supplied_production_operator(repeated)
    operator.validate_opaque_caller_operator_analysis(analysis)
    assert analysis.receipt.possible_positive_killing_state_count == 6
    assert analysis.receipt.guaranteed_positive_killing_state_count == 6
    assert analysis.receipt.minimum_killing_lower == Fraction(1, 8)
    assert analysis.receipt.maximum_killing_upper == Fraction(1, 8)
    assert not hasattr(analysis, "kernel")
    assert type(repeated.killing) is operator.RepeatedCallerSuppliedInterval


def test_disjoint_detailed_balance_is_rejected() -> None:
    spec = _small_spec()
    bad_x = dataclasses.replace(
        spec.axes[0],
        stationary_mass=((1.0, 1.0), (2.0, 2.0)),
    )
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.build_caller_supplied_production_operator(
            dataclasses.replace(spec, axes=(bad_x, spec.axes[1]))
        )
    assert failure.value.code == operator.HOLD_DETAILED_BALANCE


def test_pairwise_interval_overlap_does_not_promote_cycle_reversibility() -> None:
    one = (1.0, 1.0)
    two = (2.0, 2.0)
    uncertain_mass = ((1.0, 2.0),) * 3
    cycle = operator.CallerSuppliedAxisSpec(
        name="cycle_counterexample",
        periodic=True,
        forward=(one, one, two),
        backward=(one, one, one),
        stationary_mass=uncertain_mass,
    )
    spec = operator.CallerSuppliedOperatorSpec(
        fixture_role="caller_supplied_cycle_counterexample",
        tensor_shape=(3,),
        axes=(cycle,),
        killing=((0.0, 0.0),) * 3,
        block_size=2,
        maximum_working_bytes=20_000,
    )
    analysis = operator.build_caller_supplied_production_operator(spec)
    assert analysis.receipt.pairwise_balance_interval_overlap
    assert analysis.receipt.axis_template_edge_count == 3
    assert not analysis.receipt.global_detailed_balance_witness
    assert not analysis.receipt.science_free_input_provenance
    operator.validate_opaque_caller_operator_analysis(analysis)


def test_possible_and_guaranteed_positive_killing_counts_are_distinct() -> None:
    spec = dataclasses.replace(
        _small_spec(),
        killing=((0.0, 1.0 / 64.0),) + ((0.0, 0.0),) * 5,
    )
    analysis = operator.build_caller_supplied_production_operator(spec)
    assert analysis.receipt.possible_positive_killing_state_count == 1
    assert analysis.receipt.guaranteed_positive_killing_state_count == 0


def test_closed_fixed_neutral_constructor_has_constructive_global_witness() -> None:
    candidate = operator.build_fixed_neutral_synthetic_operator(
        (2, 3),
        block_size=2,
        maximum_working_bytes=20_000,
    )
    operator.validate_production_operator_candidate(candidate)
    receipt = candidate.receipt
    assert receipt.status == operator.FIXED_NEUTRAL_METHOD_STATUS
    assert receipt.input_provenance == operator.INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1
    assert receipt.fixture_role == operator.FIXED_NEUTRAL_FIXTURE_ROLE
    assert receipt.axis_template_edge_count == 1 + 2
    assert receipt.possible_positive_killing_state_count == 6
    assert receipt.guaranteed_positive_killing_state_count == 6
    assert receipt.pairwise_balance_interval_overlap
    assert receipt.global_detailed_balance_witness
    assert not receipt.caller_supplied_unclassified_inputs
    assert receipt.science_free_input_provenance
    assert receipt.primary_control_excluded_by_construction
    assert receipt.budget_excluded_by_construction
    assert not receipt.authorizes_scientific_execution
    assert not receipt.science_executed
    assert not receipt.measured_resource_evidence
    assert not receipt.production_resource_gate
    assert not receipt.f0_pass
    assert not candidate.science_executed
    assert not candidate.production_resource_gate
    assert not candidate.f0_pass

    q, _ = _dense_oracle(candidate)
    np.testing.assert_array_equal(q.sum(axis=1), np.full(6, -1.0 / 64.0))


@pytest.mark.parametrize(
    ("global_name", "changed_value"),
    (
        ("_FIXED_NEUTRAL_RATE", Fraction(1, 8)),
        ("_FIXED_NEUTRAL_MASS", Fraction(2)),
        ("_FIXED_NEUTRAL_KILLING", Fraction(1, 32)),
    ),
)
def test_fixed_neutral_global_mutations_fail_literal_template_validation(
    monkeypatch: pytest.MonkeyPatch,
    global_name: str,
    changed_value: Fraction,
) -> None:
    monkeypatch.setattr(operator, global_name, changed_value)
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.build_fixed_neutral_synthetic_operator(
            (2, 3),
            block_size=2,
            maximum_working_bytes=20_000,
        )
    assert failure.value.code == operator.HOLD_STRUCTURAL_WITNESS


def test_fixed_heterogeneous_fixture_has_one_root_design_and_exact_db() -> None:
    candidate = operator.build_fixed_heterogeneous_two_state_operator(
        block_size=2,
        maximum_working_bytes=20_000,
    )
    operator.validate_production_operator_candidate(candidate)
    receipt = candidate.receipt
    assert receipt.status == operator.FIXED_HETEROGENEOUS_METHOD_STATUS
    assert (
        receipt.input_provenance
        == operator.INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1
    )
    assert receipt.fixture_role == operator.FIXED_HETEROGENEOUS_FIXTURE_ROLE
    assert receipt.tensor_shape == (2,)
    assert receipt.axis_template_edge_count == 1
    assert receipt.global_detailed_balance_witness
    assert receipt.integrated_one_root_fixture_design
    assert not receipt.topology_executed
    assert not receipt.measured_resource_evidence
    assert not receipt.production_resource_gate
    assert not receipt.f0_pass

    q, p = _dense_oracle(candidate)
    np.testing.assert_array_equal(
        q,
        np.array(((-0.625, 0.5), (0.25, -0.75)), dtype=np.float64),
    )
    np.testing.assert_array_equal(p, np.eye(2) + q / candidate.kernel.rate)
    np.testing.assert_array_equal(
        candidate.stationary_masses[0].intervals,
        np.array(((1.0, 1.0), (2.0, 2.0)), dtype=np.float64),
    )
    assert 1.0 * 0.5 == 2.0 * 0.25

    killing = np.array((0.125, 0.5), dtype=np.float64)
    density_at_zero = killing[0]
    derivative_at_zero = float(q[0] @ killing)
    assert derivative_at_zero == 11.0 / 64.0 > 0.0
    eigenvalues = np.linalg.eigvals(q)
    np.testing.assert_array_equal(eigenvalues.imag, np.zeros(2))
    fast, slow = sorted(eigenvalues.real.tolist())
    slow_coefficient = (
        derivative_at_zero - fast * density_at_zero
    ) / (slow - fast)
    fast_coefficient = density_at_zero - slow_coefficient
    slow_derivative_coefficient = slow * slow_coefficient
    fast_derivative_coefficient = fast * fast_coefficient
    assert slow_derivative_coefficient < 0.0
    assert fast_derivative_coefficient > 0.0
    unique_root_time = math.log(
        -fast_derivative_coefficient / slow_derivative_coefficient
    ) / (slow - fast)
    assert 0.5 < unique_root_time < 35.0


@pytest.mark.parametrize(
    "mutator",
    (
        lambda candidate: dataclasses.replace(
            candidate,
            receipt=dataclasses.replace(
                candidate.receipt,
                source_module_sha256="f" * 64,
            ),
        ),
        lambda candidate: dataclasses.replace(
            candidate,
            receipt=dataclasses.replace(
                candidate.receipt,
                maximum_p_row_deficit=candidate.receipt.maximum_p_row_deficit
                + Fraction(1, 2**53),
            ),
        ),
        lambda candidate: dataclasses.replace(
            candidate,
            receipt=dataclasses.replace(candidate.receipt, f0_pass=True),
        ),
        lambda candidate: dataclasses.replace(
            candidate,
            receipt=dataclasses.replace(
                candidate.receipt,
                global_detailed_balance_witness=True,
            ),
        ),
        lambda candidate: dataclasses.replace(
            candidate,
            receipt=dataclasses.replace(
                candidate.receipt,
                science_free_input_provenance=True,
                primary_control_excluded_by_construction=True,
                budget_excluded_by_construction=True,
            ),
        ),
        lambda candidate: dataclasses.replace(candidate, f0_pass=True),
    ),
)
def test_receipt_and_claim_mutations_are_rejected(mutator: object) -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    mutated = mutator(analysis)  # type: ignore[operator]
    with pytest.raises(operator.ProductionOperatorFailure):
        operator.validate_opaque_caller_operator_analysis(mutated)


def test_owned_kernel_mutation_is_rejected() -> None:
    candidate = operator.build_fixed_neutral_synthetic_operator(
        (2, 3),
        block_size=2,
        maximum_working_bytes=20_000,
    )
    diagonal = candidate.kernel.diagonal_center.copy()
    diagonal[0] = np.nextafter(diagonal[0], -math.inf)
    diagonal.setflags(write=False)
    mutated_kernel = dataclasses.replace(candidate.kernel, diagonal_center=diagonal)
    with pytest.raises(packed.PackedF0Failure):
        operator.validate_production_operator_candidate(
            dataclasses.replace(candidate, kernel=mutated_kernel)
        )


def test_source_hash_receipt_is_current_and_bound() -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    assert analysis.receipt.source_module_sha256 == hashlib.sha256(
        Path(operator.__file__).read_bytes()
    ).hexdigest()
    assert analysis.receipt.packed_core_source_sha256 == hashlib.sha256(
        Path(packed.__file__).read_bytes()
    ).hexdigest()
    assert not analysis.receipt.source_hashes_authoritative
    assert analysis.receipt.external_exact_byte_audit_required
    assert not analysis.receipt.external_exact_byte_audit_complete
    assert len(analysis.receipt.input_manifest_sha256) == 64
    assert len(analysis.receipt.kernel_binding_sha256) == 64
    assert len(analysis.receipt.stationary_binding_sha256) == 64
    assert len(analysis.receipt.receipt_sha256) == 64


@pytest.mark.parametrize(
    "unclassified_role",
    (
        "science_free_positive_budget_fixture",
        "science_free_selector_fixture",
        "science_free_prospective_control_fixture",
        "physical_control_fixture",
    ),
)
def test_role_strings_never_promote_caller_provenance(unclassified_role: str) -> None:
    analysis = operator.build_caller_supplied_production_operator(
        dataclasses.replace(_small_spec(), fixture_role=unclassified_role)
    )
    assert analysis.receipt.input_provenance == operator.CALLER_SUPPLIED_UNCLASSIFIED
    assert analysis.receipt.caller_supplied_unclassified_inputs
    assert not analysis.receipt.science_free_input_provenance
    assert not analysis.receipt.primary_control_excluded_by_construction
    assert not analysis.receipt.budget_excluded_by_construction


def test_closed_constructor_has_no_endpoint_role_path_control_or_budget_surface() -> None:
    caller_signature = inspect.signature(
        operator.build_caller_supplied_production_operator
    )
    assert tuple(caller_signature.parameters) == ("spec",)
    fixed_signature = inspect.signature(
        operator.build_fixed_neutral_synthetic_operator
    )
    assert tuple(fixed_signature.parameters) == (
        "tensor_shape",
        "block_size",
        "maximum_working_bytes",
    )
    forbidden_fragments = ("endpoint", "role", "path", "control", "budget")
    assert all(
        all(fragment not in parameter for fragment in forbidden_fragments)
        for parameter in fixed_signature.parameters
    )
    heterogeneous_signature = inspect.signature(
        operator.build_fixed_heterogeneous_two_state_operator
    )
    assert tuple(heterogeneous_signature.parameters) == (
        "block_size",
        "maximum_working_bytes",
    )
    assert all(
        all(fragment not in parameter for fragment in forbidden_fragments)
        for parameter in heterogeneous_signature.parameters
    )
    source = Path(operator.__file__).read_text(encoding="utf-8")
    forbidden_identifiers = tuple("lp_" + suffix for suffix in ("m1", "m2", "m3"))
    assert all(identifier not in source for identifier in forbidden_identifiers)
    assert "selector_result.json" not in source


def test_source_paths_are_frozen_at_import(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    monkeypatch.setattr(operator, "__file__", str(Path(__file__).resolve()))
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.validate_opaque_caller_operator_analysis(analysis)
    assert failure.value.code == operator.HOLD_SOURCE_BINDING


def test_packed_source_path_is_frozen_at_import(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    monkeypatch.setattr(packed, "__file__", str(Path(__file__).resolve()))
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.validate_opaque_caller_operator_analysis(analysis)
    assert failure.value.code == operator.HOLD_SOURCE_BINDING


def test_source_digest_is_frozen_at_import(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    monkeypatch.setattr(operator, "_SOURCE_MODULE_SHA256_AT_IMPORT", "f" * 64)
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.validate_opaque_caller_operator_analysis(analysis)
    assert failure.value.code == operator.HOLD_SOURCE_BINDING


def test_caller_candidate_cannot_be_relabelled_fixed_neutral() -> None:
    analysis = operator.build_caller_supplied_production_operator(_small_spec())
    promoted = dataclasses.replace(
        analysis,
        receipt=dataclasses.replace(
            analysis.receipt,
            input_provenance=operator.INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1,
            fixture_role=operator.FIXED_NEUTRAL_FIXTURE_ROLE,
        ),
    )
    with pytest.raises(operator.ProductionOperatorFailure) as failure:
        operator.validate_opaque_caller_operator_analysis(promoted)
    assert failure.value.code == operator.HOLD_SOURCE_BINDING
