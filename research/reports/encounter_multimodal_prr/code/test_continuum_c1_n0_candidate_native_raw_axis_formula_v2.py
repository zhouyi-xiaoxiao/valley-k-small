from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2
import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
PRODUCER_SOURCE = CODE / "build_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
VERIFIER_SOURCE = CODE / "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
REQUEST_SCHEMA = "encounter_continuum_c1_n0_raw_axis_formula_request_v3"
REQUEST_STATUS = "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
OUTPUT_SCHEMA = "encounter_c1_n0_raw_axis_formula_primitive_source_v2"
RECEIPT_SCHEMA = "encounter_c1_n0_raw_axis_formula_primitive_validation_receipt_v1"
PLAN_SCHEMA = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v1"
PLAN_STATUS = "RESULT_BLIND_PRECOMMIT_REPLAY_PLAN_NO_EXECUTION_RESULTS"
BUNDLE_SCHEMA = "encounter_continuum_c1_n0_precommit_candidate_bundle_v1"
BUNDLE_STATUS = "RESULT_BLIND_PRECOMMIT_CANDIDATE_BUNDLE_NO_EXECUTION_RESULTS"
COMMITMENT_SCHEMA = "encounter_external_predecessor_commitment_v1"
COMMITMENT_STATUS = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_STRUCTURALLY_BOUND_AUTHENTICITY_NOT_LOCALLY_PROVEN"
)
RUNTIME_CLOSURE_SCHEMA = "encounter_continuum_c1_n0_role8_implementation_runtime_closure_v1"
ROLE9_REQUEST_SCHEMA = "encounter_continuum_c1_n0_stationary_integrals_request_v3"
ROLE9_OUTPUT_SCHEMA = "encounter_c1_n0_stationary_physical_integral_source_v2"
ROLE9_RECEIPT_SCHEMA = "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1"
ROLE10_REQUEST_SCHEMA = "encounter_continuum_c1_n0_killing_factor_geometry_request_v3"
ROLE10_OUTPUT_SCHEMA = "encounter_c1_n0_killing_factor_geometry_source_v2"
ROLE10_RECEIPT_SCHEMA = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v1"
MEMBER_SCHEMA = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
PARAMETER_SCHEMA = "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
PARTITION_SCHEMA = "encounter_exact_axis_partition_v1"
COORDINATES = ("midpoint", "relative_parallel", "relative_perpendicular")
PARAMETER_STATUS = "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
PARAMETER_ORDER = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    "killing_contact_profile_mpfr_192_v3",
    "killing_analytic_disk_area_mpfr_256_v3",
    "killing_source_independent_same_backend_verifier_v3",
    "killing_exact_contact_cell_classification_v3",
)
PYTHON_IMPORTS = {
    "producer": [
        "argparse",
        "dataclasses",
        "fractions",
        "gmpy2",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "secrets",
        "stat",
        "sys",
        "threading",
        "typing",
        "unicodedata",
    ],
    "verifier": [
        "argparse",
        "dataclasses",
        "fractions",
        "gmpy2",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "stat",
        "sys",
        "typing",
        "unicodedata",
    ],
}
PREDECESSOR_CLAIMS = {
    "backend_independence_claimed",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "external_predecessor_commitment_present",
    "formal_outer_open_operation_model_present",
    "formal_selected_source_dag_complete",
    "formal_symbolic_candidate_materialized",
    "one_correlated_distinguished_ideal_member_is_contained",
    "ordered_roles_8_10_replay_executed",
    "policy_predecessor_order_independently_sealed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "root_transfer_complete",
    "science_executed",
    "submission_eligible",
    "symbolic_acceptance_receipt_materialized",
}
REFERENCE_CLAIMS = {
    "box_truncation_proved",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "continuum_topology_proved",
    "production_bridge_accepted",
    "release_eligible",
}
FORMULA_CLAIMS = {
    "binary64_centres_define_ideal_member",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "every_interval_endpoint_combination_is_a_model",
    "production_bridge_accepted",
    "release_eligible",
}


@dataclass(slots=True)
class NeutralFixture:
    root: Path
    report: Path
    producer: Path
    verifier: Path
    request: Path
    output: Path
    receipt: Path
    plan: Path
    bundle: Path
    commitment: Path
    runtime_closure: Path
    authorities: dict[str, Path]
    partitions: list[Path]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def domain_hash(domain: str, value: Any) -> str:
    return sha256_bytes(domain.encode("ascii") + b"\0" + canonical(value))


def q(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def immutable_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(canonical(value))
    path.chmod(0o400)


def replace_json(path: Path, value: Any) -> None:
    path.chmod(0o600)
    path.write_bytes(canonical(value))
    path.chmod(0o400)


def copy_immutable(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copyfile(source, target)
    target.chmod(0o400)


def modulo(value: Fraction, period: Fraction) -> Fraction:
    return value - (value // period) * period


def reconstruct_partition(
    coordinate: str, axis: dict[str, Any], dynamics: dict[str, Any]
) -> dict[str, Any]:
    size = axis["size"]
    alignment = axis["alignment"]
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        start = Fraction.from_float(float.fromhex(axis["lower_binary64_hex"]))
        stop = Fraction.from_float(float.fromhex(axis["upper_binary64_hex"]))
        width = stop - start
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            step = width / size
            positions = [start + (Fraction(index) + Fraction(1, 2)) * step for index in range(size)]
            segments = [
                [(start + index * step, start + (index + 1) * step)] for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = width / (size - 1)
            positions = [start + index * step for index in range(size)]
            faces = (
                [start]
                + [start + (Fraction(index) - Fraction(1, 2)) * step for index in range(1, size)]
                + [stop]
            )
            segments = [[(faces[index], faces[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
        periodic = False
    else:
        start = Fraction(dynamics["transverse_domain_start_exact"])
        width = Fraction(dynamics["transverse_period_exact"])
        step = width / size
        shift = Fraction(axis["periodic_shift_exact"])
        positions = [
            start + modulo((Fraction(index) + Fraction(1, 2)) * step + shift, width)
            for index in range(size)
        ]
        stop = start + width
        segments = []
        for index in range(size):
            lower = start + modulo(index * step + shift, width)
            upper = lower + step
            if upper <= stop:
                segments.append([(lower, upper)])
            else:
                segments.append([(lower, stop), (start, start + upper - stop)])
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment.endswith("_base")
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in segments]
    return {
        "cell_segments_exact": [
            [[q(lower), q(upper)] for lower, upper in cell] for cell in segments
        ],
        "cell_volumes_exact": [q(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": q(start),
        "domain_width_exact": q(width),
        "periodic": periodic,
        "periodic_shift_exact": q(shift),
        "positions_exact": [q(value) for value in positions],
        "schema": PARTITION_SCHEMA,
        "size": size,
    }


def method_entry(parameter_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "method_parameter_sha256": domain_hash(
            "encounter-outward-method-parameters-v4", parameters
        ),
        "parameter_id": parameter_id,
        "parameters": parameters,
    }


def false_claims(keys: set[str]) -> dict[str, bool]:
    return {key: False for key in sorted(keys)}


def formula_contract() -> dict[str, str]:
    return {
        "bernoulli": "Bernoulli(s)=s/(exp(s)-1),Bernoulli(0)=1",
        "common_axis_flux": "kappa_edge=mu_i*q_i_to_j=mu_j*q_j_to_i",
        "discrete_killing": "k=B*V",
        "exact_adjoint_map": "P_h[u]_i=integral_C_i_u*pi_dx/pi_h_i",
        "global_gauge": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
        "ideal_axis_mass": "mu_i=cell_volume_i*exp(-potential(representative_i))",
        "map_ratio": "rho_i=M_i_pi/pi_h_i",
        "periodic_axis_mass": "mu_i=cell_volume_i",
        "periodic_rate": "q=D_axis/(cell_width^2)",
        "physical_cell_mass": "M_i_pi=integral_C_i_pi_dx",
        "reconstructed_killing_multiplier": "K=V/rho",
        "reflecting_sg_rate": (
            "q_i_to_j=D_axis/(cell_volume_i*distance_ij)*Bernoulli(potential_j-potential_i)"
        ),
        "tensor_common_conductance": ("c_edge=G*kappa_axis_edge*product_spectator_axis_mu"),
        "tensor_gauged_mass": "pi_h_tensor=G*product_axis_mu",
    }


def axis_contracts() -> dict[str, dict[str, str]]:
    periodic_common = {
        "boundary_rule": "periodic_endpoints_identified_no_duplicate_endpoint",
        "cardinality_semantics": "size_equal_periodic_control_volumes",
        "cell_segments_formula": (
            "[domain_start+mod(i*h+shift,width),"
            "domain_start+mod(i*h+shift,width)+h] split into two ordered segments "
            "when it crosses domain_start+width"
        ),
        "cell_volumes_formula": "h for every cell",
        "positions_formula": ("domain_start+mod((i+1/2)*h+shift,width), i=0,...,size-1"),
        "step_formula": "h=width/size",
    }
    return {
        "cell_centred_periodic_base": {
            **periodic_common,
            "shift_formula": "shift=0",
            "source_construction_tag": "cell_centred_periodic_diffusion",
        },
        "cell_centred_periodic_half_shift": {
            **periodic_common,
            "shift_formula": "shift=h/2",
            "source_construction_tag": "cell_centred_periodic_diffusion_half_shift",
        },
        "cell_centred_reflecting": {
            "boundary_rule": "reflecting_zero_flux_no_transition_through_endpoints",
            "cardinality_semantics": "size_equal_control_volumes",
            "cell_segments_formula": ("C_i=[lower+i*h,lower+(i+1)*h], i=0,...,size-1"),
            "cell_volumes_formula": "h for every cell",
            "positions_formula": "lower+(i+1/2)*h, i=0,...,size-1",
            "source_construction_tag": "cell_centred_reflecting_scharfetter_gummel",
            "step_formula": "h=(upper-lower)/size",
        },
        "vertex_centred_reflecting_dual": {
            "boundary_rule": "reflecting_zero_flux_no_transition_through_endpoints",
            "cardinality_semantics": (
                "size_vertices_and_size_dual_control_volumes_with_size_minus_one_intervals"
            ),
            "cell_segments_formula": (
                "with x_i=lower+i*h and boundaries=(x_0,(x_0+x_1)/2,...,"
                "(x_(size-2)+x_(size-1))/2,x_(size-1)), "
                "C_i=[boundary_i,boundary_(i+1)]"
            ),
            "cell_volumes_formula": "h/2 at i=0 and i=size-1; h otherwise",
            "positions_formula": "lower+i*h, i=0,...,size-1",
            "source_construction_tag": ("vertex_centred_reflecting_scharfetter_gummel"),
            "step_formula": "h=(upper-lower)/(size-1)",
        },
    }


def _neutral_sources(
    root: Path,
    period: Fraction = Fraction(1),
) -> tuple[
    dict[str, Path],
    list[Path],
    list[dict[str, Any]],
    dict[str, Any],
]:
    fixture_root = root / "fixture"
    dynamics = {
        "directed_precision_bits": 192,
        "midpoint_diffusion_formula": "particle_diffusion/2",
        "midpoint_potential_formula": ("ou_stiffness*(x-ou_mean)^2/(2*midpoint_diffusion)"),
        "ou_mean_binary64_hex": float(0.25).hex(),
        "ou_stiffness_binary64_hex": float(0.5).hex(),
        "particle_diffusion_binary64_hex": float(0.25).hex(),
        "relative_diffusion_formula": "2*particle_diffusion",
        "relative_parallel_mean_exact": "0/1",
        "relative_parallel_potential_formula": ("ou_stiffness*x^2/(2*relative_diffusion)"),
        "relative_perpendicular_potential_formula": "0/1",
        "transverse_domain_start_exact": q(-period / 2),
        "transverse_period_exact": q(period),
    }
    rows = [
        {
            "expected_states": 36,
            "label": "Neutral/Base",
            "midpoint": {
                "alignment": "cell_centred_reflecting",
                "lower_binary64_hex": float(-1).hex(),
                "size": 3,
                "upper_binary64_hex": float(2).hex(),
            },
            "purpose": "neutral periodic-base fixture",
            "relative_parallel": {
                "alignment": "cell_centred_reflecting",
                "lower_binary64_hex": float(-1).hex(),
                "size": 3,
                "upper_binary64_hex": float(1).hex(),
            },
            "relative_perpendicular": {
                "alignment": "cell_centred_periodic_base",
                "periodic_shift_exact": "0/1",
                "size": 4,
            },
            "shape": [3, 3, 4],
        },
        {
            "expected_states": 48,
            "label": "Neutral/HalfShift",
            "midpoint": {
                "alignment": "vertex_centred_reflecting_dual",
                "lower_binary64_hex": float(-1).hex(),
                "size": 3,
                "upper_binary64_hex": float(2).hex(),
            },
            "purpose": "neutral vertex-dual and periodic-half-shift fixture",
            "relative_parallel": {
                "alignment": "vertex_centred_reflecting_dual",
                "lower_binary64_hex": float(-1).hex(),
                "size": 4,
                "upper_binary64_hex": float(1).hex(),
            },
            "relative_perpendicular": {
                "alignment": "cell_centred_periodic_half_shift",
                "periodic_shift_exact": q(period / 8),
                "size": 4,
            },
            "shape": [3, 4, 4],
        },
    ]
    order = [row["label"] for row in rows]
    closure_files: dict[str, Path] = {}
    for name in (
        "bridge_design",
        "c0_source",
        "configuration_design",
        "configuration_implementation",
        "configuration_test",
        "factorization_initial_partition_bundle",
        "factorization_killing_geometry",
        "initial_geometry",
        "joint_refinement_family",
        "legacy_member_spec",
        "round176_member_candidate",
    ):
        path = fixture_root / f"{name}.json"
        immutable_json(
            path,
            {
                "fixture_role": name,
                "status": "IMMUTABLE_NEUTRAL_TEST_AUTHORITY_NOT_PRODUCTION",
            },
        )
        closure_files[name] = path
    configuration = {
        "authority": {
            "design_path": "fixture/configuration_design.json",
            "design_sha256": sha256_file(closure_files["configuration_design"]),
            "implementation_path": "fixture/configuration_implementation.json",
            "implementation_sha256": sha256_file(closure_files["configuration_implementation"]),
            "test_path": "fixture/configuration_test.json",
            "test_sha256": sha256_file(closure_files["configuration_test"]),
        },
        "authorizes_scientific_execution": False,
        "axis_construction_contracts": axis_contracts(),
        "configuration_count": len(rows),
        "configuration_order": order,
        "configurations": rows,
        "contains_budget_value": False,
        "contains_control_values": False,
        "coordinate_order": list(COORDINATES),
        "dynamics": dynamics,
        "initial_geometry": {
            "construction": ("independent_product_of_three_analytically_normalized_compact_bumps"),
            "half_width_binary64_hex": float(0.125).hex(),
            "normalization": "I_b=integral_-1^1_b(u)_du",
            "periodic_wrap": "sum_over_periodic_images_before_cell_integration",
            "shape_definition": "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))",
            "source_path": "fixture/initial_geometry.json",
            "source_schema": "encounter_physical_initial_analytic_source_v1",
            "source_sha256": sha256_file(closure_files["initial_geometry"]),
            "starts_binary64_hex": {
                "midpoint": float(0).hex(),
                "relative_parallel": float(0).hex(),
                "relative_perpendicular": float(0).hex(),
            },
        },
        "physical_dimension": 2,
        "quotient_dimension": 3,
        "schema": "encounter_physical_configuration_family_control_free_v1",
        "scope": "physical_d2_control_free_axis_and_initial_geometry_only",
        "status": "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1",
        "total_state_workload": 84,
        "workload_semantics": (
            "sum_of_state_counts_across_the_12_prescribed_axis_triples_for_one_future_control"
        ),
    }
    configuration_path = fixture_root / "configuration.json"
    immutable_json(configuration_path, configuration)

    factorization = {
        "cell_average_formulae": {
            "factorized_profile_cell_average": "V_jmab=W^-1*C_ab*Phi_jm",
        },
        "claim_boundary": false_claims(PREDECESSOR_CLAIMS),
        "contact_geometry": {
            "transverse_period_exact": q(period),
        },
        "coordinate_and_measure_contract": {
            "coordinate_order": list(COORDINATES),
        },
        "dependency_closure": {
            "acyclic": True,
        },
        "enclosure_semantics": {
            "future_numeric_payload_present": False,
        },
        "outcome_free_contract": {
            "numeric_enclosure_payload_present": False,
            "primitive_source_only": True,
        },
        "profile_basis": {
            "profile_count": 4,
        },
        "schema": "encounter_continuum_c1_factorization_source_v2_candidate",
        "source_pins": {
            "configuration_source": {
                "path": "fixture/configuration.json",
                "schema": "encounter_physical_configuration_family_control_free_v1",
                "sha256": sha256_file(configuration_path),
            },
            "initial_partition_bundle": {
                "path": "fixture/factorization_initial_partition_bundle.json",
                "schema": "encounter_control_free_production_initial_stream_v1",
                "sha256": sha256_file(closure_files["factorization_initial_partition_bundle"]),
            },
            "killing_geometry_source": {
                "path": "fixture/factorization_killing_geometry.json",
                "schema": "encounter_physical_killing_geometry_source_v1",
                "sha256": sha256_file(closure_files["factorization_killing_geometry"]),
            },
        },
        "status": (
            "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_NOT_EXTERNALLY_"
            "COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
        ),
        "storage_contract": {
            "tensor_storage_order": "C",
        },
    }
    factorization_path = fixture_root / "factorization.json"
    immutable_json(factorization_path, factorization)

    c0_pin = {
        "path": "fixture/c0_source.json",
        "sha256": sha256_file(closure_files["c0_source"]),
    }
    reference = {
        "boundary_and_measure": {
            "finite_nonperiodic_faces": "reflecting_zero_flux_approximants",
            "finite_periodic_coordinate": "relative_perpendicular_mod_W",
            "physical_cell_measure": ("d_midpoint*d_relative_parallel*d_relative_perpendicular"),
            "target_nonperiodic_domain": "R_times_R",
            "target_periodic_domain": "T_W",
        },
        "claim_boundary": false_claims(REFERENCE_CLAIMS),
        "coordinate_order": list(COORDINATES),
        "diffusion_and_drift": {
            "diffusion_diagonal": [
                "particle_diffusion/2",
                "2*particle_diffusion",
                "2*particle_diffusion",
            ],
            "drift": [
                "-ou_stiffness*(midpoint-ou_mean)",
                "-ou_stiffness*relative_parallel",
                "0/1",
            ],
        },
        "normalization": {
            "box_mass": "M_L=integral_Omega_L_pi_dx",
            "conditional_box_renormalization_used": False,
            "full_space_normalizer": "Z=2*pi*particle_diffusion*W/ou_stiffness",
            "periodic_factor": "1/W",
            "reference_density": (
                "pi=Z^-1*exp[-ou_stiffness*(midpoint-ou_mean)^2/"
                "particle_diffusion-ou_stiffness*relative_parallel^2/"
                "(4*particle_diffusion)]"
            ),
            "restricted_density_retains_global_normalization": True,
        },
        "physical_parameter_bundle": {
            "ou_mean_binary64_hex": dynamics["ou_mean_binary64_hex"],
            "ou_stiffness_binary64_hex": dynamics["ou_stiffness_binary64_hex"],
            "particle_diffusion_binary64_hex": dynamics["particle_diffusion_binary64_hex"],
            "physical_dimension": 2,
            "quotient_dimension": 3,
            "transverse_period_exact": q(period),
        },
        "schema": "encounter_continuum_c1_reference_density_source_v1",
        "source_pins": {
            "c0_mathematical_source": c0_pin,
            "configuration_source": {
                "path": "fixture/configuration.json",
                "sha256": sha256_file(configuration_path),
            },
        },
        "status": ("FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"),
        "unit_table": {
            "box_mass_M_L": "dimensionless_probability",
            "diffusion_coefficients": "length_squared_per_time",
            "full_space_normalizer_Z": "length_cubed",
            "ou_stiffness": "inverse_time",
            "physical_cell_measure": "length_cubed",
            "reference_density_pi": "inverse_length_cubed",
            "spatial_coordinates": "length",
            "transverse_period_W": "length",
        },
    }
    reference_path = fixture_root / "reference.json"
    immutable_json(reference_path, reference)

    formula = {
        "claim_boundary": false_claims(FORMULA_CLAIMS),
        "formulae": formula_contract(),
        "member_semantics": {
            "common_flux_uses_one_formula_defined_exact_value": True,
            "formula_defined_member_is_independent_of_production_centres": True,
            "global_gauge_is_single_scalar_per_configuration": True,
            "one_correlated_distinguished_member_required": True,
        },
        "potential_formulae": {
            "midpoint": "ou_stiffness*(x-ou_mean)^2/particle_diffusion",
            "relative_parallel": "ou_stiffness*x^2/(4*particle_diffusion)",
            "relative_perpendicular": "0/1",
        },
        "schema": "encounter_continuum_c1_ideal_formula_source_v1",
        "source_pins": {
            "c0_mathematical_source": c0_pin,
            "production_bridge_design": {
                "path": "fixture/bridge_design.json",
                "sha256": sha256_file(closure_files["bridge_design"]),
            },
        },
        "status": ("FROZEN_CONTROL_FREE_IDEAL_FORMULA_AUTHORITY_ONLY_NO_PRODUCTION_ACCEPTANCE"),
    }
    formula_path = fixture_root / "formula.json"
    immutable_json(formula_path, formula)

    primary = {
        "aggregation": "exact_Fraction_endpoint_algebra",
        "common_kappa_rule": "intersection_after_formula_witness",
        "precision_bits": 320,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
    }
    sentinel = {
        "containment_relation": (
            "primary_interval_contains_higher_precision_same_backend_sentinel"
        ),
        "independent_backend": False,
        "precision_bits": 640,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
    }
    binary64 = {
        "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
        "precision_bits": 53,
        "rounding_mode": "stored_outward_endpoints",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
    }
    exact = {
        "arithmetic": "Python_Fraction_exact_reduced_rationals",
        "precision_bits": "unbounded_integer_fraction",
        "rounding_mode": "exact",
        "source_role_scope": [
            "role8_raw_axis_formula_primitive",
            "role9_stationary_physical_integral",
            "same_member_mass_flux_composition",
            "symbolic_killing_composition",
        ],
    }
    scopes = {
        "stationary_directed_mpfr_320_v2": ["role9_stationary_physical_integral"],
        "stationary_directed_mpfr_640_sentinel_v2": ["role9_stationary_physical_integral"],
        "raw_flux_directed_mpfr_320_v2": ["role8_raw_axis_formula_primitive"],
        "raw_flux_directed_mpfr_640_sentinel_v2": ["role8_raw_axis_formula_primitive"],
        "raw_flux_binary64_decode_v2": ["role8_raw_axis_formula_primitive"],
        "exact_fraction_expression_dag_v2": exact["source_role_scope"],
        "killing_contact_profile_mpfr_192_v3": ["role10_killing_factor_geometry"],
        "killing_analytic_disk_area_mpfr_256_v3": ["role10_killing_factor_geometry"],
        "killing_source_independent_same_backend_verifier_v3": ["role10_killing_factor_geometry"],
        "killing_exact_contact_cell_classification_v3": ["role10_killing_factor_geometry"],
    }
    parameters_by_id = {
        identifier: {"source_role_scope": scopes[identifier]} for identifier in PARAMETER_ORDER
    }
    parameters_by_id["stationary_directed_mpfr_640_sentinel_v2"]["containment_relation"] = (
        "primary_interval_contains_higher_precision_same_backend_sentinel"
    )
    parameters_by_id["raw_flux_directed_mpfr_320_v2"] = primary
    parameters_by_id["raw_flux_directed_mpfr_640_sentinel_v2"] = sentinel
    parameters_by_id["raw_flux_binary64_decode_v2"] = binary64
    parameters_by_id["exact_fraction_expression_dag_v2"] = exact
    registry = {
        "claim_boundary": false_claims(PREDECESSOR_CLAIMS),
        "parameter_count": 10,
        "parameters": [
            method_entry(identifier, parameters_by_id[identifier]) for identifier in PARAMETER_ORDER
        ],
        "schema": PARAMETER_SCHEMA,
        "status": PARAMETER_STATUS,
    }
    registry_path = fixture_root / "method_parameters.json"
    immutable_json(registry_path, registry)

    partitions: list[Path] = []
    partition_records: list[tuple[str, dict[str, Any], Path]] = []
    for index, row in enumerate(rows):
        slug = "00_neutral_base" if index == 0 else "01_neutral_half_shift"
        for coordinate in COORDINATES:
            partition = reconstruct_partition(coordinate, row[coordinate], dynamics)
            relative = Path("fixture") / "partitions" / slug / f"{coordinate}.partition.json"
            path = root / relative
            immutable_json(path, partition)
            partitions.append(path)
            partition_records.append((relative.as_posix(), partition, path))

    role_bindings = {
        "configuration_source": {
            "path": "fixture/configuration.json",
            "sha256": sha256_file(configuration_path),
        },
        "factorization_source": {
            "path": "fixture/factorization.json",
            "sha256": sha256_file(factorization_path),
        },
        "ideal_formula_source": {
            "path": "fixture/formula.json",
            "sha256": sha256_file(formula_path),
        },
        "reference_density_source": {
            "path": "fixture/reference.json",
            "sha256": sha256_file(reference_path),
        },
    }
    semantic_ids = [
        {
            "authority_label": row["label"],
            "refinement_family_id": "neutral_fixture_family",
            "refinement_member_id": f"neutral_{index}",
        }
        for index, row in enumerate(rows)
    ]
    physical_parameter_hash = domain_hash(
        "encounter-physical-parameter-bundle-v1", reference["physical_parameter_bundle"]
    )
    bindings: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        row_hash = sha256_bytes(canonical(row))
        sequence_id = f"neutral-sequence:{index}:{row['label']}"
        axes = []
        partition_hashes = []
        for coordinate_index, coordinate in enumerate(COORDINATES):
            relative, partition, path = partition_records[3 * index + coordinate_index]
            partition_hash = sha256_file(path)
            axis = {
                "alignment": row[coordinate]["alignment"],
                "cell_count": partition["size"],
                "coordinate": coordinate,
                "exact_box_or_period": {
                    "domain_start_exact": partition["domain_start_exact"],
                    "domain_width_exact": partition["domain_width_exact"],
                },
                "partition_report_relative_path": relative,
                "partition_schema": PARTITION_SCHEMA,
                "partition_sha256": partition_hash,
                "periodic": partition["periodic"],
                "refinement_family_id": "neutral_fixture_family",
                "refinement_member_id": f"neutral_{index}",
                "sequence_id": sequence_id,
                "sequence_source_row_canonical_sha256": row_hash,
            }
            if partition["periodic"]:
                axis["periodic_shift_n0_exact"] = partition["periodic_shift_exact"]
            axes.append(axis)
            partition_hashes.append(partition_hash)
        geometry = {
            "configuration_index": index,
            "configuration_row": row,
            "n0_partition_sha256s": partition_hashes,
        }
        row_manifest_path = fixture_root / "partitions" / f"{index:02d}" / "row_manifest.json"
        immutable_json(
            row_manifest_path,
            {
                "configuration_index": index,
                "fixture_role": "initial_partition_row_manifest",
            },
        )
        bindings.append(
            {
                "authority_label": row["label"],
                "configuration_geometry_sha256": domain_hash(
                    "encounter-configuration-geometry-v1", geometry
                ),
                "configuration_index": index,
                "initial_partition_row_manifest_path": (
                    f"fixture/partitions/{index:02d}/row_manifest.json"
                ),
                "initial_partition_row_manifest_sha256": sha256_file(row_manifest_path),
                "n0_anchor_expected_states": row["expected_states"],
                "n0_anchor_shape": row["shape"],
                "n0_axes": axes,
                "physical_parameter_bundle_sha256": physical_parameter_hash,
                "refinement_family_id": "neutral_fixture_family",
                "refinement_member_id": f"neutral_{index}",
                "sequence_id": sequence_id,
                "sequence_source_row_canonical_sha256": row_hash,
                "sequence_source_row_index": index,
            }
        )
    member_semantics = {
        "configuration_count": len(rows),
        "configuration_rows_are_finite_anchors": True,
        "coordinate_order": list(COORDINATES),
        "every_cartesian_interval_endpoint_combination_is_a_model": False,
        "one_formula_defined_correlated_member_per_configuration": True,
        "physical_dimension": 2,
        "quotient_dimension": 3,
        "scalar_convention": "complex_inner_product_conjugate_first_factor",
    }
    identity = {
        "configuration_order": order,
        "configuration_semantic_ids": semantic_ids,
        "coordinate_order": list(COORDINATES),
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": role_bindings,
        "scalar_convention": member_semantics["scalar_convention"],
    }
    member = {
        "claim_boundary": false_claims(PREDECESSOR_CLAIMS),
        "configuration_order": order,
        "configuration_semantic_ids": semantic_ids,
        "identity_properties": {
            "alignment_counts": {
                "cell_centred_periodic_base": 1,
                "cell_centred_periodic_half_shift": 1,
                "cell_centred_reflecting": 2,
                "vertex_centred_reflecting_dual": 2,
            },
            "candidate_authoritative": False,
            "current_enclosures_bind_this_candidate": False,
            "n0_partition_sha256s_structurally_bound": True,
            "partition_file_count": 6,
            "round172_source_itself_contains_partition_sha256": False,
            "source_roles_1_through_4_only_in_production_role_bindings": True,
        },
        "member_identity_sha256": domain_hash(
            "encounter-continuum-c1-c2-n0-member-identity-v3", identity
        ),
        "member_semantics": member_semantics,
        "n0_sequence_bindings": bindings,
        "reconstruction_counts": {
            "axis_cell_count": 21,
            "axis_count": 6,
            "axis_edge_count": 17,
            "configuration_count": len(rows),
            "periodic_seam_count": 2,
            "profile_index_count": 8,
            "total_virtual_tensor_state_count": 84,
        },
        "role_bindings": role_bindings,
        "schema": MEMBER_SCHEMA,
        "source_lineage_evidence": {
            "initial_partition_bundle": {
                "path": "fixture/factorization_initial_partition_bundle.json",
                "sha256": sha256_file(closure_files["factorization_initial_partition_bundle"]),
            },
            "joint_refinement_family": {
                "path": "fixture/joint_refinement_family.json",
                "sha256": sha256_file(closure_files["joint_refinement_family"]),
            },
            "legacy_member_spec": {
                "path": "fixture/legacy_member_spec.json",
                "sha256": sha256_file(closure_files["legacy_member_spec"]),
            },
            "round176_member_candidate": {
                "path": "fixture/round176_member_candidate.json",
                "sha256": sha256_file(closure_files["round176_member_candidate"]),
            },
        },
        "status": (
            "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_NOT_EXTERNALLY_"
            "COMMITTED_NOT_PRODUCTION_MEMBER"
        ),
    }
    member_path = fixture_root / "member.json"
    immutable_json(member_path, member)
    authorities = {
        "configuration": configuration_path,
        "configuration_design": closure_files["configuration_design"],
        "configuration_implementation": closure_files["configuration_implementation"],
        "configuration_test": closure_files["configuration_test"],
        "factorization": factorization_path,
        "factorization_initial_partition_bundle": closure_files[
            "factorization_initial_partition_bundle"
        ],
        "factorization_killing_geometry": closure_files["factorization_killing_geometry"],
        "ideal_formula": formula_path,
        "member_spec": member_path,
        "method_parameters": registry_path,
        "reference_density": reference_path,
    }
    return authorities, partitions, rows, member


def create_neutral_fixture(tmp_path: Path, *, period: Fraction = Fraction(1)) -> NeutralFixture:
    if period != 1:
        raise ValueError("request-level PASS fixtures use the frozen production period")
    return create_production_shaped_v4_fixture(tmp_path)


def create_production_shaped_v4_fixture(tmp_path: Path) -> NeutralFixture:
    root = tmp_path / "candidate_raw_axis_production_shape"
    root.mkdir(mode=0o700, parents=True)
    root.chmod(0o700)
    clone_report = root / "research/reports/encounter_multimodal_prr"
    artifacts = REPORT / "artifacts/data"
    source_authorities = {
        "anti_vacuity_policy": artifacts
        / "continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json",
        "configuration": artifacts / "physical_configuration_family_control_free_v1.json",
        "configuration_design": REPORT / "notes/positive_b_fixed_control_robustness_design_v2.md",
        "configuration_implementation": REPORT / "code/rate_defined_tensor_f0.py",
        "configuration_initial_geometry": artifacts / "physical_initial_analytic_source_v1.json",
        "configuration_test": REPORT / "code/test_rate_defined_tensor_f0.py",
        "factorization": artifacts / "continuum_c1_factorization_source_v2_candidate.json",
        "factorization_initial_partition_bundle": artifacts
        / "physical_production_initial_stream_v1/bundle.json",
        "factorization_killing_geometry": artifacts / "physical_killing_geometry_source_v1.json",
        "ideal_formula": artifacts / "continuum_c1_ideal_formula_source_v1.json",
        "member_spec": artifacts / "continuum_c1_c2_n0_member_spec_v4_candidate.json",
        "method_parameters": artifacts
        / "continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json",
        "reference_density": artifacts / "continuum_c1_reference_density_source_v1.json",
    }
    authorities: dict[str, Path] = {}
    for role, source in source_authorities.items():
        target = clone_report / source.relative_to(REPORT)
        copy_immutable(source, target)
        authorities[role] = target

    member = json.loads(authorities["member_spec"].read_text(encoding="ascii"))
    partitions: list[Path] = []
    partition_pins: list[dict[str, Any]] = []
    for index, binding in enumerate(member["n0_sequence_bindings"]):
        for coordinate, axis in zip(COORDINATES, binding["n0_axes"], strict=True):
            source = REPORT / axis["partition_report_relative_path"]
            target = clone_report / source.relative_to(REPORT)
            copy_immutable(source, target)
            partitions.append(target)
            partition_pins.append(
                {
                    "configuration_index": index,
                    "coordinate": coordinate,
                    "member_report_relative_path": axis["partition_report_relative_path"],
                    "path": str(target),
                    "sha256": sha256_file(target),
                }
            )

    producer = clone_report / "code/build_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
    verifier = (
        clone_report / "code/validate_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
    )
    copy_immutable(PRODUCER_SOURCE, producer)
    copy_immutable(VERIFIER_SOURCE, verifier)
    peer_sources = {
        9: {
            "producer": (
                clone_report
                / "code/build_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"
            ),
            "verifier": (
                clone_report
                / "code/validate_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"
            ),
        },
        10: {
            "producer": (
                clone_report
                / "code/build_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py"
            ),
            "verifier": (
                clone_report
                / "code/validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py"
            ),
        },
    }
    for sources in peer_sources.values():
        for target in sources.values():
            copy_immutable(REPORT / "code" / target.name, target)
    request_path = root / "request.json"
    output_path = root / "output.json"
    receipt_path = root / "receipt.json"
    plan_path = root / "replay_plan.json"
    bundle_path = root / "precommit_bundle.json"
    commitment_path = root / "synthetic_external_commitment.json"
    runtime_closure_path = root / "role8_runtime_closure.json"
    runtime = {
        "gmp": gmpy2.mp_version(),
        "gmpy2": gmpy2.__version__,
        "mpc": gmpy2.mpc_version(),
        "mpfr": gmpy2.mpfr_version(),
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
    }
    package_directory = Path(gmpy2.__file__).resolve().parent
    extension_candidates = sorted(package_directory.glob("gmpy2*.so"))
    library_directory = package_directory.parent / "gmpy2.libs"
    native_library_paths = {
        "gmpy2_extension": extension_candidates,
        "libgmp": sorted(library_directory.glob("libgmp.*.dylib")),
        "libmpfr": sorted(library_directory.glob("libmpfr.*.dylib")),
        "libmpc": sorted(library_directory.glob("libmpc.*.dylib")),
    }
    assert all(len(paths) == 1 for paths in native_library_paths.values())
    native_libraries = [
        {
            "path": str(native_library_paths[role][0].resolve()),
            "role": role,
            "sha256": sha256_file(native_library_paths[role][0].resolve()),
        }
        for role in ("gmpy2_extension", "libgmp", "libmpfr", "libmpc")
    ]
    python_executable = Path(sys.executable).resolve()
    runtime_closure = {
        "claim_boundary": {
            "complete_report_local_and_native_runtime_closure": True,
            "legacy_scientific_backend_imported": False,
            "result_artifact_dependency_present": False,
        },
        "code_inputs": {
            "producer": {"path": str(producer), "sha256": sha256_file(producer)},
            "verifier": {"path": str(verifier), "sha256": sha256_file(verifier)},
        },
        "native_libraries": native_libraries,
        "native_runtime": runtime,
        "python_executable": {
            "path": str(python_executable),
            "sha256": sha256_file(python_executable),
        },
        "python_imports": PYTHON_IMPORTS,
        "report_local_dependencies": [],
        "schema": RUNTIME_CLOSURE_SCHEMA,
        "status": (
            "FROZEN_SOURCE_SEPARATED_ROLE8_IMPLEMENTATION_RUNTIME_CLOSURE_NO_EXECUTION_RESULT"
        ),
    }
    immutable_json(runtime_closure_path, runtime_closure)

    configuration = json.loads(authorities["configuration"].read_text(encoding="ascii"))
    row_records = [
        {
            "configuration_index": index,
            "configuration_label": row["label"],
            "configuration_row_canonical_sha256": sha256_bytes(canonical(row)),
            "expected_states": row["expected_states"],
            "shape": row["shape"],
        }
        for index, row in enumerate(configuration["configurations"])
    ]
    partition_inventory = [
        {
            "alignment": axis["alignment"],
            "cell_count": axis["cell_count"],
            "configuration_index": index,
            "configuration_label": binding["authority_label"],
            "coordinate": coordinate,
            "partition_report_relative_path": axis["partition_report_relative_path"],
            "partition_schema": axis["partition_schema"],
            "partition_sha256": axis["partition_sha256"],
            "periodic": axis["periodic"],
            "refinement_family_id": axis["refinement_family_id"],
            "refinement_member_id": axis["refinement_member_id"],
            "sequence_id": axis["sequence_id"],
        }
        for index, binding in enumerate(member["n0_sequence_bindings"])
        for coordinate, axis in zip(COORDINATES, binding["n0_axes"], strict=True)
    ]

    def shared_pin(role: str, schema: str) -> dict[str, str]:
        path = authorities[role]
        return {
            "path": path.relative_to(clone_report).as_posix(),
            "schema": schema,
            "sha256": sha256_file(path),
        }

    shared_context = {
        "anti_vacuity_policy": shared_pin(
            "anti_vacuity_policy",
            "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate",
        ),
        "configuration": shared_pin(
            "configuration", "encounter_physical_configuration_family_control_free_v1"
        ),
        "configuration_row_inventory_sha256": domain_hash(
            "encounter-continuum-c1-n0-configuration-row-inventory-v1", row_records
        ),
        "factorization": shared_pin(
            "factorization", "encounter_continuum_c1_factorization_source_v2_candidate"
        ),
        "ideal_formula": shared_pin(
            "ideal_formula", "encounter_continuum_c1_ideal_formula_source_v1"
        ),
        "member_identity_sha256": member["member_identity_sha256"],
        "member_spec": shared_pin("member_spec", MEMBER_SCHEMA),
        "method_parameter_registry": shared_pin("method_parameters", PARAMETER_SCHEMA),
        "partition_inventory_sha256": domain_hash(
            "encounter-continuum-c1-n0-partition-inventory-v1", partition_inventory
        ),
        "reference_density": shared_pin(
            "reference_density", "encounter_continuum_c1_reference_density_source_v1"
        ),
    }
    assert shared_context["configuration_row_inventory_sha256"] == (
        "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
    )
    assert shared_context["partition_inventory_sha256"] == (
        "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
    )
    shared_digest = domain_hash(
        "encounter-continuum-c1-n0-shared-precommit-context-v1", shared_context
    )
    registry = json.loads(authorities["method_parameters"].read_text(encoding="ascii"))
    registry_by_id = {entry["parameter_id"]: entry for entry in registry["parameters"]}
    selected_ids = [
        "raw_flux_directed_mpfr_320_v2",
        "raw_flux_directed_mpfr_640_sentinel_v2",
        "raw_flux_binary64_decode_v2",
        "exact_fraction_expression_dag_v2",
    ]
    selected_methods = [
        {
            "method_parameter_sha256": registry_by_id[identifier]["method_parameter_sha256"],
            "parameter_id": identifier,
        }
        for identifier in selected_ids
    ]
    role8_entry = {
        "entry_id": "role8_raw_axis_formula_primitive",
        "implementation_runtime_closure": {
            "path": str(runtime_closure_path),
            "schema": RUNTIME_CLOSURE_SCHEMA,
            "sha256": sha256_file(runtime_closure_path),
        },
        "input_authorities": {
            role: {"path": str(path), "sha256": sha256_file(path)}
            for role, path in authorities.items()
            if role != "configuration_initial_geometry"
        },
        "invocations": {
            "producer": {
                "argv": [
                    sys.executable,
                    "-I",
                    "-B",
                    str(producer),
                    "--request",
                    str(request_path),
                    "--output",
                    str(output_path),
                ],
                "cwd": str(clone_report),
            },
            "verifier": {
                "argv": [
                    sys.executable,
                    "-I",
                    "-B",
                    str(verifier),
                    "--request",
                    str(request_path),
                    "--output",
                    str(output_path),
                    "--receipt",
                    str(receipt_path),
                ],
                "cwd": str(clone_report),
            },
        },
        "method_selection": selected_methods,
        "outputs": {
            "artifact": {"path": str(output_path), "schema": OUTPUT_SCHEMA},
            "validation_receipt": {"path": str(receipt_path), "schema": RECEIPT_SCHEMA},
        },
        "partition_path_bindings": partition_pins,
        "request": {
            "path": str(request_path),
            "schema": REQUEST_SCHEMA,
            "status": REQUEST_STATUS,
        },
        "role": 8,
    }

    def placeholder_entry(role: int, name: str) -> dict[str, Any]:
        if role == 9:
            request_schema = ROLE9_REQUEST_SCHEMA
            output_schema = ROLE9_OUTPUT_SCHEMA
            receipt_schema = ROLE9_RECEIPT_SCHEMA
            method_selection = {
                "exact_parameter_id": "exact_fraction_expression_dag_v2",
                "primary_parameter_id": "stationary_directed_mpfr_320_v2",
                "sentinel_parameter_id": "stationary_directed_mpfr_640_sentinel_v2",
            }
        elif role == 10:
            request_schema = ROLE10_REQUEST_SCHEMA
            output_schema = ROLE10_OUTPUT_SCHEMA
            receipt_schema = ROLE10_RECEIPT_SCHEMA
            method_selection = {
                "analytic_area_parameter_id": "killing_analytic_disk_area_mpfr_256_v3",
                "classification_parameter_id": ("killing_exact_contact_cell_classification_v3"),
                "contact_profile_parameter_id": "killing_contact_profile_mpfr_192_v3",
                "verifier_parameter_id": ("killing_source_independent_same_backend_verifier_v3"),
            }
        else:
            raise AssertionError("unexpected placeholder role")
        peer_request = root / f"{name}.request.json"
        peer_output = root / f"{name}.artifact.json"
        peer_receipt = root / f"{name}.receipt.json"
        sources = peer_sources[role]
        entry = {
            "entry_id": name,
            "implementation_runtime_closure": {
                "producer": {
                    "path": str(sources["producer"]),
                    "sha256": sha256_file(sources["producer"]),
                },
                "runtime_requirements": runtime,
                "verifier": {
                    "path": str(sources["verifier"]),
                    "sha256": sha256_file(sources["verifier"]),
                },
            },
            "input_authorities": {
                authority_role: {
                    "path": str(path),
                    "sha256": sha256_file(path),
                }
                for authority_role, path in authorities.items()
            },
            "invocations": {
                "producer": {
                    "argv": [
                        sys.executable,
                        str(sources["producer"]),
                        "--request",
                        str(peer_request),
                        "--output",
                        str(peer_output),
                    ],
                    "cwd": str(clone_report),
                },
                "verifier": {
                    "argv": [
                        sys.executable,
                        str(sources["verifier"]),
                        "--request",
                        str(peer_request),
                        "--output",
                        str(peer_output),
                        "--receipt",
                        str(peer_receipt),
                    ],
                    "cwd": str(clone_report),
                },
            },
            "method_selection": method_selection,
            "outputs": {
                "artifact": {
                    "path": str(peer_output),
                    "schema": output_schema,
                },
                "validation_receipt": {
                    "path": str(peer_receipt),
                    "schema": receipt_schema,
                },
            },
            "partition_path_bindings": partition_pins,
            "request": {
                "path": str(peer_request),
                "schema": request_schema,
                "status": REQUEST_STATUS,
            },
            "role": role,
        }
        entry["precommit_projection_sha256"] = domain_hash(
            "encounter-continuum-c1-n0-role-precommit-projection-v1", entry
        )
        return entry

    role8_entry["precommit_projection_sha256"] = domain_hash(
        "encounter-continuum-c1-n0-role-precommit-projection-v1", role8_entry
    )
    plan = {
        "claim_boundary": {
            "external_predecessor_commitment_present": False,
            "ordered_roles_8_10_replay_executed": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "entries": [
            role8_entry,
            placeholder_entry(9, "role9_stationary_physical_integral"),
            placeholder_entry(10, "role10_killing_factor_geometry"),
        ],
        "schema": PLAN_SCHEMA,
        "shared_context": shared_context,
        "shared_precommit_context_sha256": shared_digest,
        "status": PLAN_STATUS,
    }
    immutable_json(plan_path, plan)
    bundle = {
        "claim_boundary": plan["claim_boundary"],
        "member_spec": {
            "path": str(authorities["member_spec"]),
            "sha256": sha256_file(authorities["member_spec"]),
        },
        "method_parameter_registry": {
            "path": str(authorities["method_parameters"]),
            "sha256": sha256_file(authorities["method_parameters"]),
        },
        "replay_plan": {"path": str(plan_path), "sha256": sha256_file(plan_path)},
        "schema": BUNDLE_SCHEMA,
        "shared_precommit_context_sha256": shared_digest,
        "status": BUNDLE_STATUS,
    }
    immutable_json(bundle_path, bundle)
    candidate_bundle_pin = {
        "path": str(bundle_path),
        "sha256": sha256_file(bundle_path),
    }
    commitment_claims = {
        "cryptographic_authenticity_verified_locally": False,
        "externality_proven_by_local_code": False,
        "roles_8_10_outputs_observed": False,
    }
    ordering = {
        "committed_before_roles_8_10_replay": True,
        "no_role_8_10_outputs_observed": True,
        "result_blind_plan": True,
    }
    authority = {
        "authority_identifier": "synthetic-test-authority",
        "trust_domain_identifier": "synthetic-tmp-path-only",
    }
    commitment_message = {
        "authority": authority,
        "candidate_bundle": candidate_bundle_pin,
        "claim_boundary": commitment_claims,
        "ordering": ordering,
    }
    commitment = {
        "authentication": {
            "authentication_class": "independently_audited_predecessor_commit_hash",
            "evidence_identifier": "synthetic-test-evidence-not-production",
            "structural_validation_only": True,
        },
        "authority": authority,
        "candidate_bundle": candidate_bundle_pin,
        "claim_boundary": commitment_claims,
        "commitment_message_sha256": domain_hash(
            "encounter-external-predecessor-commitment-message-v1",
            commitment_message,
        ),
        "ordering": ordering,
        "schema": COMMITMENT_SCHEMA,
        "status": COMMITMENT_STATUS,
    }
    immutable_json(commitment_path, commitment)
    replay_digest = domain_hash(
        "encounter-continuum-c1-n0-shared-replay-context-v1",
        {
            "external_predecessor_commitment_sha256": sha256_file(commitment_path),
            "replay_plan_sha256": sha256_file(plan_path),
            "shared_precommit_context_sha256": shared_digest,
        },
    )
    request = {
        "external_predecessor_commitment": {
            "path": str(commitment_path),
            "sha256": sha256_file(commitment_path),
        },
        "plan": {"path": str(plan_path), "sha256": sha256_file(plan_path)},
        "plan_entry_id": "role8_raw_axis_formula_primitive",
        "role": {"role_id": 8, "role_name": "role8_raw_axis_formula_primitive"},
        "schema": REQUEST_SCHEMA,
        "shared_precommit_context_sha256": shared_digest,
        "shared_replay_context_sha256": replay_digest,
        "status": REQUEST_STATUS,
    }
    immutable_json(request_path, request)
    return NeutralFixture(
        root=root,
        report=clone_report,
        producer=producer,
        verifier=verifier,
        request=request_path,
        output=output_path,
        receipt=receipt_path,
        plan=plan_path,
        bundle=bundle_path,
        commitment=commitment_path,
        runtime_closure=runtime_closure_path,
        authorities=authorities,
        partitions=partitions,
    )


create_production_shaped_v3_fixture = create_production_shaped_v4_fixture


def run_script(
    path: Path, *arguments: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(path), *arguments],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def run_producer(
    fixture: NeutralFixture, *, check: bool = False
) -> subprocess.CompletedProcess[str]:
    arguments = [
        "--request",
        str(fixture.request),
        "--output",
        str(fixture.output),
    ]
    if check:
        arguments.append("--check")
    return run_script(fixture.producer, *arguments, cwd=fixture.report)


def run_verifier(fixture: NeutralFixture) -> subprocess.CompletedProcess[str]:
    return run_script(
        fixture.verifier,
        "--request",
        str(fixture.request),
        "--output",
        str(fixture.output),
        "--receipt",
        str(fixture.receipt),
        cwd=fixture.report,
    )


def load_isolated_module(source: Path, name: str) -> Any:
    specification = importlib.util.spec_from_file_location(name, source)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def walk_keys(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            result.append(key)
            result.extend(walk_keys(item))
    elif isinstance(value, list):
        for item in value:
            result.extend(walk_keys(item))
    return result


def test_production_authority_end_to_end_science_and_source_separation(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    assert "PASS_EXCLUSIVE_PUBLICATION" in produced.stdout
    result = json.loads(fixture.output.read_text(encoding="ascii"))
    assert result["schema"] == OUTPUT_SCHEMA
    assert result["summary"]["all_primary_intervals_contain_sentinels"] is True
    assert result["summary"]["axis_cell_count"] == 5037
    assert result["summary"]["axis_edge_count"] == 5013
    assert result["summary"]["configuration_count"] == 12
    assert result["summary"]["periodic_domain_cut_crossing_edge_count"] == 12
    assert result["summary"]["reflecting_boundary_zero_q_count"] == 48
    assert result["summary"]["total_virtual_tensor_state_count"] == 34_787_462
    assert result["summary"]["nondegenerate_primary_interval_count"] > 0
    assert result["claim_boundary"]["stationary_or_killing_result_consumed"] is False
    assert result["normalization_scope"]["downstream_physical_normalization_applied"] is False
    assert result["normalization_scope"]["periodic_raw_mu_rule"] == (
        "cell_volume_without_period_reciprocal_factor"
    )

    periodic_axes = [row["axes"][2] for row in result["rows"]]
    assert all(axis["periodic_domain_cut_crossing_edge_count"] == 1 for axis in periodic_axes)
    for index, axis in enumerate(periodic_axes):
        partition = json.loads(fixture.partitions[3 * index + 2].read_text(encoding="ascii"))
        expected_mu = [
            {
                "lower_exact_p_over_q": volume,
                "upper_exact_p_over_q": volume,
            }
            for volume in partition["cell_volumes_exact"]
        ]
        assert [cell["raw_mu_interval"] for cell in axis["cells"]] == expected_mu
    reflecting_intervals = [
        cell["raw_mu_interval"]
        for row in result["rows"]
        for axis in row["axes"][:2]
        for cell in axis["cells"]
    ]
    assert any(
        Fraction(interval["lower_exact_p_over_q"]) < Fraction(interval["upper_exact_p_over_q"])
        for interval in reflecting_intervals
    )

    forbidden_output_keys = {
        "m_l",
        "m_pi",
        "global_gauge",
        "pi_h",
        "rho",
        "conductance",
        "c_e",
    }
    assert forbidden_output_keys.isdisjoint(key.lower() for key in walk_keys(result))

    verified = run_verifier(fixture)
    assert verified.returncode == 0, verified.stderr
    assert "PASS_EXCLUSIVE_IMMUTABLE_VALIDATION_RECEIPT_PUBLICATION" in verified.stdout
    receipt = json.loads(fixture.receipt.read_text(encoding="ascii"))
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert "sha256" not in receipt
    assert receipt["artifact"]["sha256"] == sha256_file(fixture.output)
    assert receipt["geometry_inventory"]["sha256"] == result["geometry_inventory"]["sha256"]
    assert stat.S_IMODE(fixture.receipt.stat().st_mode) == 0o444
    assert fixture.receipt.stat().st_uid == os.getuid()
    assert fixture.receipt.stat().st_nlink == 1
    assert receipt["claim_boundary"] == {
        "complete_C1": False,
        "complete_C2": False,
        "externality_proven_by_local_code": False,
        "production_same_member_bridge_accepted": False,
        "release_eligible": False,
        "same_member_role8_role9_pair_accepted": False,
    }
    assert result["replay_binding"]["externality_proven_by_local_code"] is False
    assert result["replay_binding"]["structural_commitment_record_validated"] is True
    assert result["member_binding"]["member_identity_sha256"] == (
        "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
    )
    assert result["geometry_inventory"]["cell_record_count"] == 5037
    assert result["geometry_inventory"]["edge_record_count"] == 5013
    assert result["geometry_inventory"]["reflecting_boundary_record_count"] == 48
    geometry_keys = {key.lower() for key in walk_keys(result["geometry_inventory"])}
    assert not any(token in key for key in geometry_keys for token in ("mu", "q_interval", "kappa"))
    producer_tree = ast.parse(PRODUCER_SOURCE.read_text(encoding="utf-8"))
    verifier_tree = ast.parse(VERIFIER_SOURCE.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for tree in (producer_tree, verifier_tree)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for tree in (producer_tree, verifier_tree)
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(
        module and ("fixed_row_raw_flux" in module or "candidate_native_raw_axis_formula" in module)
        for module in imported_modules
    )


def test_nonunit_period_raw_mu_and_kappa_exclude_inverse_period_factor(
    tmp_path: Path,
) -> None:
    reduced_root = tmp_path / "lower_level_nonunit_period"
    reduced_root.mkdir(mode=0o700)
    _, partitions, _, _ = _neutral_sources(reduced_root, Fraction(3, 2))
    periodic_partitions = [
        json.loads(partitions[index].read_text(encoding="ascii")) for index in (2, 5)
    ]
    cell_width = Fraction(3, 8)
    axis_diffusion = Fraction(1, 2)
    directed_q = axis_diffusion / cell_width**2
    raw_kappa = axis_diffusion / cell_width
    assert directed_q == Fraction(32, 9)
    assert raw_kappa == Fraction(4, 3)
    for partition in periodic_partitions:
        assert partition["domain_width_exact"] == "3/2"
        assert partition["cell_volumes_exact"] == ["3/8"] * 4
    assert cell_width != Fraction(1, 4)
    assert raw_kappa != Fraction(8, 9)


def test_decimal_scharfetter_gummel_oracle_is_hand_independent(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    result = json.loads(fixture.output.read_text(encoding="ascii"))
    axis = result["rows"][0]["axes"][0]
    edge = axis["edges"][0]
    partition = json.loads(fixture.partitions[0].read_text(encoding="ascii"))
    reference = json.loads(fixture.authorities["reference_density"].read_text(encoding="ascii"))
    parameters = reference["physical_parameter_bundle"]

    def decimal_interval(interval: dict[str, str]) -> tuple[Decimal, Decimal]:
        lower = Fraction(interval["lower_exact_p_over_q"])
        upper = Fraction(interval["upper_exact_p_over_q"])
        return (
            Decimal(lower.numerator) / Decimal(lower.denominator),
            Decimal(upper.numerator) / Decimal(upper.denominator),
        )

    def decimal_fraction(value: Fraction) -> Decimal:
        return Decimal(value.numerator) / Decimal(value.denominator)

    with localcontext() as context:
        context.prec = 120
        particle_diffusion = decimal_fraction(
            Fraction.from_float(float.fromhex(parameters["particle_diffusion_binary64_hex"]))
        )
        axis_diffusion = particle_diffusion / Decimal(2)
        stiffness = decimal_fraction(
            Fraction.from_float(float.fromhex(parameters["ou_stiffness_binary64_hex"]))
        )
        mean = decimal_fraction(
            Fraction.from_float(float.fromhex(parameters["ou_mean_binary64_hex"]))
        )
        left_position = decimal_fraction(Fraction(partition["positions_exact"][0]))
        right_position = decimal_fraction(Fraction(partition["positions_exact"][1]))
        left_volume = decimal_fraction(Fraction(partition["cell_volumes_exact"][0]))
        right_volume = decimal_fraction(Fraction(partition["cell_volumes_exact"][1]))
        distance = right_position - left_position
        left_potential = stiffness * (left_position - mean) ** 2 / particle_diffusion
        right_potential = stiffness * (right_position - mean) ** 2 / particle_diffusion
        delta = right_potential - left_potential

        def bernoulli(value: Decimal) -> Decimal:
            return Decimal(1) if value == 0 else value / (value.exp() - Decimal(1))

        mu_left = left_volume * (-left_potential).exp()
        mu_right = right_volume * (-right_potential).exp()
        q_forward = axis_diffusion / (left_volume * distance) * bernoulli(delta)
        q_reverse = axis_diffusion / (right_volume * distance) * bernoulli(-delta)
        kappa_direct_left = (-left_potential).exp() * axis_diffusion / distance * bernoulli(delta)
        kappa_direct_right = (
            (-right_potential).exp() * axis_diffusion / distance * bernoulli(-delta)
        )

        for oracle, interval in (
            (mu_left, axis["cells"][0]["raw_mu_interval"]),
            (mu_right, axis["cells"][1]["raw_mu_interval"]),
            (q_forward, edge["forward_q_interval"]),
            (q_reverse, edge["reverse_q_interval"]),
            (kappa_direct_left, edge["direct_left_kappa_interval"]),
            (kappa_direct_right, edge["direct_right_kappa_interval"]),
            (kappa_direct_left, edge["common_kappa_interval"]),
        ):
            lower, upper = decimal_interval(interval)
            assert lower <= oracle <= upper
        tolerance = Decimal("1e-110")
        assert abs(mu_left * q_forward - mu_right * q_reverse) < tolerance
        assert abs(kappa_direct_left - kappa_direct_right) < tolerance


def test_production_shaped_twelve_row_v4_clone_smoke(tmp_path: Path) -> None:
    fixture = create_production_shaped_v3_fixture(tmp_path)
    assert sha256_file(fixture.authorities["factorization"]) == (
        "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
    )
    assert sha256_file(fixture.authorities["method_parameters"]) == (
        "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5"
    )
    assert sha256_file(fixture.authorities["member_spec"]) == (
        "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
    )
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    result = json.loads(fixture.output.read_text(encoding="ascii"))
    assert result["summary"]["configuration_count"] == 12
    assert result["summary"]["axis_cell_count"] == 5037
    assert result["summary"]["axis_edge_count"] == 5013
    assert result["summary"]["periodic_domain_cut_crossing_edge_count"] == 12
    assert result["summary"]["reflecting_boundary_zero_q_count"] == 48
    assert result["summary"]["total_virtual_tensor_state_count"] == 34_787_462
    assert len(fixture.partitions) == 36
    verified = run_verifier(fixture)
    assert verified.returncode == 0, verified.stderr


def test_read_only_check_is_deterministic_and_non_mutating(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    first = run_producer(fixture)
    assert first.returncode == 0, first.stderr
    before = fixture.output.stat()
    before_bytes = fixture.output.read_bytes()
    checked = run_producer(fixture, check=True)
    after = fixture.output.stat()
    assert checked.returncode == 0, checked.stderr
    assert "PASS_READ_ONLY_CHECK" in checked.stdout
    assert fixture.output.read_bytes() == before_bytes
    assert (before.st_ino, before.st_mtime_ns, before.st_ctime_ns, before.st_mode) == (
        after.st_ino,
        after.st_mtime_ns,
        after.st_ctime_ns,
        after.st_mode,
    )
    assert stat.S_IMODE(after.st_mode) == 0o400
    duplicate_publish = run_producer(fixture)
    assert duplicate_publish.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_OUTPUT: precommitted output slot is not fresh" in (
        duplicate_publish.stderr
    )


def test_read_only_check_allows_only_the_selected_artifact_to_exist(
    tmp_path: Path,
) -> None:
    fixture = create_neutral_fixture(tmp_path)
    produced = run_producer(fixture)
    assert produced.returncode == 0, produced.stderr
    selected_before = fixture.output.read_bytes()
    plan = json.loads(fixture.plan.read_text(encoding="ascii"))
    peer_artifact = Path(plan["entries"][1]["outputs"]["artifact"]["path"])
    immutable_json(peer_artifact, {"foreign": "peer-artifact"})
    peer_before = peer_artifact.read_bytes()

    checked = run_producer(fixture, check=True)
    assert checked.returncode == 2
    assert "precommitted artifact/receipt slot is not fresh" in checked.stderr
    assert fixture.output.read_bytes() == selected_before
    assert peer_artifact.read_bytes() == peer_before


def test_request_is_result_blind_and_uses_only_neutral_fixture_pins(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    request = json.loads(fixture.request.read_text(encoding="ascii"))
    assert set(request) == {
        "external_predecessor_commitment",
        "plan",
        "plan_entry_id",
        "role",
        "schema",
        "shared_precommit_context_sha256",
        "shared_replay_context_sha256",
        "status",
    }
    plan = json.loads(fixture.plan.read_text(encoding="ascii"))
    assert [entry["role"] for entry in plan["entries"]] == [8, 9, 10]
    entry = plan["entries"][0]
    assert set(entry["input_authorities"]) == {
        "anti_vacuity_policy",
        "configuration",
        "configuration_design",
        "configuration_implementation",
        "configuration_test",
        "factorization",
        "factorization_initial_partition_bundle",
        "factorization_killing_geometry",
        "ideal_formula",
        "member_spec",
        "method_parameters",
        "reference_density",
    }
    assert len(entry["partition_path_bindings"]) == 36
    expected_peer_authorities = set(entry["input_authorities"]) | {"configuration_initial_geometry"}
    role9_entry, role10_entry = plan["entries"][1:]
    for peer_entry in (role9_entry, role10_entry):
        assert set(peer_entry["implementation_runtime_closure"]) == {
            "producer",
            "runtime_requirements",
            "verifier",
        }
        assert set(peer_entry["input_authorities"]) == expected_peer_authorities
        assert peer_entry["partition_path_bindings"] == entry["partition_path_bindings"]
        assert peer_entry["invocations"]["producer"]["argv"][0] == sys.executable
        assert peer_entry["invocations"]["verifier"]["argv"][0] == sys.executable
        assert "-I" not in peer_entry["invocations"]["producer"]["argv"]
        assert "-B" not in peer_entry["invocations"]["producer"]["argv"]
        assert peer_entry["invocations"]["producer"]["cwd"] == str(fixture.report)
        assert peer_entry["invocations"]["verifier"]["cwd"] == str(fixture.report)
    assert role9_entry["request"]["schema"] == ROLE9_REQUEST_SCHEMA
    assert role9_entry["outputs"]["artifact"]["schema"] == ROLE9_OUTPUT_SCHEMA
    assert role9_entry["outputs"]["validation_receipt"]["schema"] == ROLE9_RECEIPT_SCHEMA
    assert role9_entry["method_selection"] == {
        "exact_parameter_id": "exact_fraction_expression_dag_v2",
        "primary_parameter_id": "stationary_directed_mpfr_320_v2",
        "sentinel_parameter_id": "stationary_directed_mpfr_640_sentinel_v2",
    }
    assert role10_entry["request"]["schema"] == ROLE10_REQUEST_SCHEMA
    assert role10_entry["outputs"]["artifact"]["schema"] == ROLE10_OUTPUT_SCHEMA
    assert role10_entry["outputs"]["validation_receipt"]["schema"] == ROLE10_RECEIPT_SCHEMA
    assert role10_entry["method_selection"] == {
        "analytic_area_parameter_id": "killing_analytic_disk_area_mpfr_256_v3",
        "classification_parameter_id": "killing_exact_contact_cell_classification_v3",
        "contact_profile_parameter_id": "killing_contact_profile_mpfr_192_v3",
        "verifier_parameter_id": "killing_source_independent_same_backend_verifier_v3",
    }
    assert not fixture.output.exists()
    assert not fixture.receipt.exists()
    forbidden = (
        "artifact_sha",
        "expected_output",
        "expected_result",
        "observed",
        "output_sha",
        "production_result",
        "result_sha",
        "role9_result",
        "role10_result",
    )
    assert not any(fragment in key.lower() for key in walk_keys(plan) for fragment in forbidden)
    all_pinned_paths = [pin["path"] for pin in entry["input_authorities"].values()] + [
        pin["path"] for pin in entry["partition_path_bindings"]
    ]
    assert all(Path(path).is_relative_to(fixture.root) for path in all_pinned_paths)
    assert (
        Path(entry["input_authorities"]["factorization"]["path"])
        .as_posix()
        .endswith("artifacts/data/continuum_c1_factorization_source_v2_candidate.json")
    )
    assert entry["input_authorities"]["factorization"]["sha256"] == (
        "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
    )
    commitment = json.loads(fixture.commitment.read_text(encoding="ascii"))
    assert commitment["authentication"]["structural_validation_only"] is True
    assert commitment["claim_boundary"] == {
        "cryptographic_authenticity_verified_locally": False,
        "externality_proven_by_local_code": False,
        "roles_8_10_outputs_observed": False,
    }


def test_absolute_cli_and_immutable_file_contract(tmp_path: Path) -> None:
    fixture = create_neutral_fixture(tmp_path)
    relative = run_script(
        fixture.producer,
        "--request",
        os.path.relpath(fixture.request, Path.cwd()),
        "--output",
        str(fixture.output),
    )
    assert relative.returncode == 2
    assert "HOLD_CANDIDATE_RAW_AXIS_REQUEST" in relative.stderr
    for path in [
        fixture.producer,
        fixture.verifier,
        fixture.request,
        fixture.plan,
        fixture.bundle,
        fixture.commitment,
        fixture.runtime_closure,
        *fixture.authorities.values(),
        *fixture.partitions,
    ]:
        metadata = path.stat()
        assert stat.S_IMODE(metadata.st_mode) == 0o400
        assert metadata.st_nlink == 1


@pytest.mark.parametrize(
    ("source", "failure_name"),
    (
        (PRODUCER_SOURCE, "CandidateRawAxisFailure"),
        (VERIFIER_SOURCE, "CandidateRawAxisValidationFailure"),
    ),
)
def test_snapshot_rejects_parent_replacement_after_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source: Path,
    failure_name: str,
) -> None:
    module_name = f"_role8_parent_swap_{source.stem}_{id(tmp_path)}"
    module = load_isolated_module(source, module_name)
    parent = tmp_path / source.stem / "live_parent"
    target = parent / "authority.json"
    immutable_json(target, {"authority": "original"})
    retired = parent.with_name("retired_parent")
    original_read = module.os.read
    replacement_done = False

    def replacing_read(descriptor: int, size: int) -> bytes:
        nonlocal replacement_done
        chunk = original_read(descriptor, size)
        if chunk and not replacement_done:
            replacement_done = True
            parent.rename(retired)
            parent.mkdir(mode=0o700)
            immutable_json(parent / target.name, {"authority": "replacement"})
        return chunk

    monkeypatch.setattr(module.os, "read", replacing_read)
    failure = getattr(module, failure_name)
    try:
        with pytest.raises(failure, match="anchored directory chain changed"):
            module.immutable_snapshot(target)
    finally:
        sys.modules.pop(module_name, None)


def _isolated_publisher(tmp_path: Path, label: str) -> tuple[Any, str, Path, Path]:
    module_name = f"_role8_publisher_{label}_{id(tmp_path)}"
    module = load_isolated_module(PRODUCER_SOURCE, module_name)
    parent = tmp_path / label / "output_parent"
    parent.mkdir(mode=0o700, parents=True)
    parent.chmod(0o700)
    return module, module_name, parent, parent / "output.json"


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_publication_stage_transaction_settles_post_ready_interrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "post_open")
    original_await_ready = module.StageCreationTransaction.await_ready
    transactions: list[Any] = []
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def ready_then_interrupt(transaction: Any) -> None:
        original_await_ready(transaction)
        transactions.append(transaction)
        raise interrupt_type("post-ready stage interruption")

    monkeypatch.setattr(
        module.StageCreationTransaction,
        "await_ready",
        ready_then_interrupt,
    )
    try:
        with pytest.raises(interrupt_type, match="post-ready stage interruption"):
            module._publish(output, b"owned-payload\n")
        assert len(transactions) == 1
        assert transactions[0].descriptor is None
        assert not transactions[0]._thread.is_alive()
        assert frozenset(os.listdir("/dev/fd")) == descriptors_before
        assert not output.exists()
        assert not list(parent.glob(f".{output.name}.stage.*"))
    finally:
        sys.modules.pop(module_name, None)


def test_publication_stage_transaction_preserves_identical_metadata_foreign_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "post_open_foreign")
    original_await_ready = module.StageCreationTransaction.await_ready
    foreign_identity: tuple[int, int] | None = None
    transaction_seen: Any = None
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def ready_replace_then_interrupt(transaction: Any) -> None:
        nonlocal foreign_identity, transaction_seen
        original_await_ready(transaction)
        transaction_seen = transaction
        assert transaction.identity is not None
        module.os.unlink(transaction.leaf, dir_fd=transaction.parent_descriptor)
        foreign = module._STAGE_OPEN(
            transaction.leaf,
            module.os.O_WRONLY
            | module.os.O_CREAT
            | module.os.O_EXCL
            | module.os.O_CLOEXEC
            | module.os.O_NONBLOCK
            | module.os.O_NOFOLLOW,
            0o400,
            dir_fd=transaction.parent_descriptor,
        )
        observed = module._STAGE_FSTAT(foreign)
        foreign_identity = (observed.st_dev, observed.st_ino)
        assert foreign_identity != transaction.identity
        assert observed.st_uid == os.getuid()
        assert observed.st_nlink == 1
        assert observed.st_size == 0
        assert not observed.st_mode & 0o222
        module.os.close(foreign)
        raise KeyboardInterrupt("identical-metadata foreign stage")

    monkeypatch.setattr(
        module.StageCreationTransaction,
        "await_ready",
        ready_replace_then_interrupt,
    )
    try:
        with pytest.raises(KeyboardInterrupt, match="identical-metadata foreign stage"):
            module._publish(output, b"owned-payload\n")
        assert transaction_seen is not None
        assert transaction_seen.descriptor is None
        assert not transaction_seen._thread.is_alive()
        assert frozenset(os.listdir("/dev/fd")) == descriptors_before
        assert not output.exists()
        stages = list(parent.glob(f".{output.name}.stage.*"))
        assert len(stages) == 1
        observed = stages[0].stat()
        assert (observed.st_dev, observed.st_ino) == foreign_identity
        assert observed.st_uid == os.getuid()
        assert observed.st_nlink == 1
        assert observed.st_size == 0
        assert not observed.st_mode & 0o222
    finally:
        sys.modules.pop(module_name, None)


def test_publication_rolls_back_partial_write_interrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "partial_write")
    original_write = module.os.write
    interrupted = False

    def partial_write_interrupt(descriptor: int, payload: Any) -> int:
        nonlocal interrupted
        if not interrupted:
            interrupted = True
            original_write(descriptor, payload[:1])
            raise KeyboardInterrupt("after partial stage write")
        return original_write(descriptor, payload)

    monkeypatch.setattr(module.os, "write", partial_write_interrupt)
    try:
        with pytest.raises(KeyboardInterrupt, match="partial stage write"):
            module._publish(output, b"owned-payload\n")
        assert interrupted
        assert not output.exists()
        assert not list(parent.glob(f".{output.name}.stage.*"))
    finally:
        sys.modules.pop(module_name, None)


def test_publication_recovers_final_link_before_assignment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "post_link")
    original_link = module.os.link
    interrupted = False

    def post_link_interrupt(*arguments: Any, **keywords: Any) -> None:
        nonlocal interrupted
        original_link(*arguments, **keywords)
        if not interrupted:
            interrupted = True
            raise KeyboardInterrupt("after successful final link")

    monkeypatch.setattr(module.os, "link", post_link_interrupt)
    try:
        with pytest.raises(KeyboardInterrupt, match="successful final link"):
            module._publish(output, b"owned-payload\n")
        assert interrupted
        assert not output.exists()
        assert not list(parent.glob(f".{output.name}.stage.*"))
    finally:
        sys.modules.pop(module_name, None)


def test_publication_preserves_foreign_final_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "foreign_final")
    original_link = module.os.link
    original_unlink = module.os.unlink
    foreign_payload = b"foreign-replacement\n"
    interrupted = False

    def replace_after_link(
        source: Any,
        destination: Any,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        nonlocal interrupted
        original_link(
            source,
            destination,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
            follow_symlinks=follow_symlinks,
        )
        if not interrupted:
            interrupted = True
            assert dst_dir_fd is not None
            original_unlink(destination, dir_fd=dst_dir_fd)
            descriptor = module.os.open(
                destination,
                module.os.O_WRONLY | module.os.O_CREAT | module.os.O_EXCL | module.os.O_CLOEXEC,
                0o400,
                dir_fd=dst_dir_fd,
            )
            try:
                assert module.os.write(descriptor, foreign_payload) == len(foreign_payload)
                module.os.fchmod(descriptor, 0o400)
                module.os.fsync(descriptor)
            finally:
                module.os.close(descriptor)
            raise KeyboardInterrupt("after foreign final replacement")

    monkeypatch.setattr(module.os, "link", replace_after_link)
    try:
        with pytest.raises(KeyboardInterrupt, match="foreign final replacement"):
            module._publish(output, b"owned-payload\n")
        assert interrupted
        assert output.read_bytes() == foreign_payload
        assert stat.S_IMODE(output.stat().st_mode) == 0o400
        assert not list(parent.glob(f".{output.name}.stage.*"))
    finally:
        sys.modules.pop(module_name, None)


def test_publication_rolls_back_parent_close_interrupt_after_readback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, module_name, parent, output = _isolated_publisher(tmp_path, "post_close")
    original_close = module.os.close
    parent_metadata = parent.stat()
    parent_identity = (parent_metadata.st_dev, parent_metadata.st_ino)
    interrupted = False

    def post_close_interrupt(descriptor: int) -> None:
        nonlocal interrupted
        metadata = module.os.fstat(descriptor)
        is_final_parent = (
            stat.S_ISDIR(metadata.st_mode)
            and (metadata.st_dev, metadata.st_ino) == parent_identity
            and output.exists()
        )
        original_close(descriptor)
        if is_final_parent and not interrupted:
            interrupted = True
            raise KeyboardInterrupt("after successful final parent close")

    monkeypatch.setattr(module.os, "close", post_close_interrupt)
    try:
        with pytest.raises(KeyboardInterrupt, match="successful final parent close"):
            module._publish(output, b"owned-payload\n")
        assert interrupted
        assert not output.exists()
        assert not list(parent.glob(f".{output.name}.stage.*"))
    finally:
        sys.modules.pop(module_name, None)
