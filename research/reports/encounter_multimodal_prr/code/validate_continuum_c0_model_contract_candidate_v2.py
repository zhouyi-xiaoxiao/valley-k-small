#!/usr/bin/env python3
"""Independent fail-closed verifier for the result-blind C0-v2 candidate."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"
V1_RELATIVE = Path("artifacts/data/continuum_c0_model_contract_candidate_v1.json")
V1_SHA256 = "5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66"
EXPECTED_CONTRACT_SHA256 = "688ec0416e414737705631852bb5ecf44530c5fe93e3ca95f3dfdbe8807ead7e"

HOLD_ENCODING = "HOLD_C0_V2_ENCODING"
HOLD_SCHEMA = "HOLD_C0_V2_SCHEMA"
HOLD_CLAIMS = "HOLD_C0_V2_CLAIMS"
HOLD_PARAMETERS = "HOLD_C0_V2_PARAMETERS"
HOLD_CONTINUUM = "HOLD_C0_V2_CONTINUUM"
HOLD_BOUNDARY = "HOLD_C0_V2_BOUNDARY"
HOLD_MAPS = "HOLD_C0_V2_MAPS"
HOLD_GAUGE = "HOLD_C0_V2_GAUGE"
HOLD_OPERATOR = "HOLD_C0_V2_OPERATOR"
HOLD_INITIAL = "HOLD_C0_V2_INITIAL"
HOLD_KILLING = "HOLD_C0_V2_KILLING"
HOLD_MESH = "HOLD_C0_V2_MESH"
HOLD_PRODUCTION = "HOLD_C0_V2_PRODUCTION_BOUNDARY"
HOLD_CONTROL = "HOLD_C0_V2_CONTROL"
HOLD_SOURCES = "HOLD_C0_V2_SOURCES"
HOLD_LEGACY = "HOLD_C0_V2_LEGACY"
HOLD_RESULT_BLINDNESS = "HOLD_C0_V2_RESULT_BLINDNESS"
HOLD_WITNESSES = "HOLD_C0_V2_WITNESSES"
PASS_STATUS = "PASS_C0_V2_CONTRACT_CANDIDATE_SEMANTIC_VERIFICATION_ONLY_BRIDGE_OPEN"
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_JSON_DEPTH = 128
MAX_JSON_NODES = 200_000
MAX_JSON_INTEGER_DIGITS = 128


class C0V2Hold(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


FROZEN_SOURCES = {
    "configuration_family": {
        "path": "artifacts/data/physical_configuration_family_control_free_v1.json",
        "sha256": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    },
    "control_method_commitment": {
        "path": "artifacts/data/continuum_c0_control_method_commitment_v2.json",
        "sha256": "288ad85d5992446a8f3b58416e445a88f1c15a4c71114ba008939d8fbd9a4a97",
    },
    "initial_source": {
        "path": "artifacts/data/physical_initial_analytic_source_v1.json",
        "sha256": "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
    },
    "killing_geometry_source": {
        "path": "artifacts/data/physical_killing_geometry_source_v1.json",
        "sha256": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    },
    "mathematical_source": {
        "path": "artifacts/data/continuum_c0_mathematical_source_v2.json",
        "sha256": "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559",
    },
}

EXPECTED_SOURCE_TOP_KEYS = {
    "configuration_family": {
        "authority",
        "authorizes_scientific_execution",
        "axis_construction_contracts",
        "configuration_count",
        "configuration_order",
        "configurations",
        "contains_budget_value",
        "contains_control_values",
        "coordinate_order",
        "dynamics",
        "initial_geometry",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "scope",
        "status",
        "total_state_workload",
        "workload_semantics",
    },
    "control_method_commitment": {
        "constraints",
        "control_ids",
        "exclusions",
        "future_source",
        "schema",
        "status",
    },
    "initial_source": {
        "analytic_total_mass_exact",
        "construction",
        "coordinate_order",
        "half_width_binary64_hex",
        "marginal_density",
        "normalization",
        "periodic_coordinate",
        "periodic_wrap",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "scope",
        "shape_definition",
        "shared_normalizer_across_cells_and_axes",
        "starts_binary64_hex",
        "transverse_period_exact",
    },
    "killing_geometry_source": {
        "configuration_bundle",
        "contact_geometry",
        "coordinate_order",
        "flags",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "status",
        "support_basis",
    },
    "mathematical_source": {
        "boundary_contract",
        "field_convention",
        "gate_ownership",
        "identification_maps",
        "initial_law",
        "production_boundary",
        "row_generator_and_form",
        "schema",
        "stationary_mass_gauge",
        "status",
        "witnesses",
    },
}

EXPECTED_TOP_KEYS = {
    "boundary_conditions",
    "claim_boundary",
    "control_contract",
    "continuum_object",
    "discrete_operator_convention",
    "equation_contract",
    "finite_volume_identification",
    "frozen_sources",
    "initial_law",
    "killing_field",
    "mesh_contract",
    "physical_dimension",
    "physical_parameters",
    "previous_contract",
    "production_gauge_bridge",
    "quotient_dimension",
    "scalar_convention",
    "schema",
    "source_policy",
    "stationary_mass_gauge",
    "status",
    "witnesses",
}

EXPECTED_CLAIMS = {
    "c0a_operator_realization_proved": True,
    "complete_c0_independently_accepted": False,
    "c1_fixed_box_convergence_proved": False,
    "c2_quantitative_spatial_error_proved": False,
    "c3_derivative_box_error_proved": False,
    "continuum_stationary_topology_proved": False,
    "control_values_committed_for_c0": False,
    "f0_complete": False,
    "gauged_ideal_member_containment_proved_for_every_declared_configuration": False,
    "positive_budget_scientific_values_read": False,
    "production_centre_mosco_proved": False,
    "production_raw_to_gauged_bridge_proved": False,
    "release_eligible": False,
    "sealed_control_source_required_before_complete_c0": True,
}

EXPECTED_PARAMETERS = {
    "B": {
        "binary64_hex": "0x1.47ae147ae147bp-7",
        "exact": "5764607523034235/576460752303423488",
        "unit": "inverse_time_times_longitudinal_measure",
    },
    "D": {
        "binary64_hex": "0x1.0624dd2f1a9fcp-9",
        "exact": "1152921504606847/576460752303423488",
        "unit": "length_squared_per_time",
    },
    "W": {
        "binary64_hex": "0x1.0000000000000p+0",
        "exact": "1/1",
        "unit": "length",
    },
    "contact_radius_a": {
        "binary64_hex": "0x1.47ae147ae147bp-3",
        "exact": "5764607523034235/36028797018963968",
        "unit": "length",
    },
    "gamma": {
        "binary64_hex": "0x1.999999999999ap-4",
        "exact": "3602879701896397/36028797018963968",
        "unit": "inverse_time",
    },
    "zbar": {
        "binary64_hex": "0x1.e666666666666p-1",
        "exact": "4278419646001971/4503599627370496",
        "unit": "length",
    },
}

EXPECTED_CONTINUUM = {
    "coordinate_order": ["midpoint_z", "relative_parallel", "relative_perpendicular"],
    "density_space": "X_pi=L2(pi^-1 dx)",
    "diffusion_matrix": ["D/2", "2*D", "2*D"],
    "drift": ["-gamma*(z-zbar)", "-gamma*relative_parallel", "0"],
    "form_core": "C_c_infinity(R^2)_tensor_C_infinity(T_W)",
    "form_domain": "weighted_H1_closure_of_form_core",
    "normalizer": "2*pi*D*W/gamma",
    "quotient": "R_z_times_R_relative_parallel_times_T_W",
    "reversible_density": (
        "normalizer^-1*exp(-gamma*(z-zbar)^2/D-gamma*relative_parallel^2/(4*D))"
    ),
    "weighted_state_space": "H=L2(pi dx)",
}

EXPECTED_BOUNDARY = {
    "finite_box_midpoint": "reflecting_zero_flux_approximant_only",
    "finite_box_relative_parallel": "reflecting_zero_flux_approximant_only",
    "target_midpoint": "natural_decay_form_realization_no_reflecting_face",
    "target_relative_parallel": "natural_decay_form_realization_no_reflecting_face",
    "target_relative_perpendicular": "periodic_torus_exact",
}

EXPECTED_MAPS = {
    "A_h": {
        "denominator": "M_i_pi",
        "formula": "A_h[u]_i=integral_C_i_u_pi_dx/M_i_pi",
        "kind": "literal_pi_weighted_cell_average",
    },
    "J_h": {
        "formula": "J_h[v]=sum_i_v_i*indicator_C_i",
        "kind": "piecewise_constant_actual_control_volume_reconstruction",
    },
    "P_h": {
        "denominator": "pi_h_i",
        "exact_adjoint_of_J_h": True,
        "formula": "P_h[u]_i=integral_C_i_u_pi_dx/pi_h_i",
        "kind": "exact_adjoint_weighted_cell_map",
    },
    "S_h": {
        "defined_on_all_H_L": False,
        "formula": "S_h[u]_i=u(x_i_rep)",
        "kind": "representative_point_or_nodal_sampling",
        "smooth_or_continuous_recovery_core_only": True,
    },
    "cell_mass": {"formula": "M_i_pi=integral_C_i_pi_dx"},
    "exact_identities": {
        "A_h_J_h": "I",
        "J_h_A_h": "E_h_pi_weighted_cell_conditional_expectation",
        "J_h_P_h": "rho_h_pc*E_h",
        "P_h": "J_h_adjoint",
        "P_h_J_h": "diag(rho_i)",
        "P_h_relation_to_A_h": "P_h=diag(rho_i)*A_h",
    },
    "nonclaims": {
        "J_h_P_h_equals_E_h_claimed": False,
        "J_h_P_h_operator_norm_convergence_claimed": False,
        "P_h_J_h_equals_I_claimed": False,
    },
    "rho_i": {
        "denominator": "pi_h_i",
        "formula": "rho_i=M_i_pi/pi_h_i",
        "numerator": "M_i_pi",
    },
}

EXPECTED_SCALAR = {
    "complex_continuum_inner_product": "integral_conjugate(u)*v*pi_dx",
    "complex_discrete_inner_product": "sum_i_pi_h_i*conjugate(u_i)*v_i",
    "complex_forms_conjugate_first_factor": True,
    "complexification_optional": True,
    "primary_scalar_field": "real",
}

EXPECTED_OPERATOR = {
    "density_ratio_forward_equation": "u_prime=Q_c*u",
    "directed_edge_form": (
        "one_half*sum_i_j_pi_h_i*q_ij*(u_i-u_j)*(v_i-v_j)"
        "+sum_i_pi_h_i*k_i*u_i*v_i"
    ),
    "free_detailed_balance": "pi_h_i*q_ij=pi_h_j*q_ji",
    "free_graph_connected": True,
    "free_offdiagonal_rates_nonnegative": True,
    "free_row_sum": "Q_0*one=0",
    "killed_generator": "Q_c=Q_0-diag(k_i)",
    "killing": "k_i=B*V_h_i>=0",
    "nonnegative_operator": "H_h=-Q_c",
    "probability_forward_equation": "p_prime=transpose(Q_c)*p",
    "row_generator_convention": True,
    "undirected_edge_form": (
        "sum_each_undirected_edge_once_c_ij*(u_i-u_j)*(v_i-v_j)"
        "+sum_i_pi_h_i*k_i*u_i*v_i"
    ),
    "undirected_edge_has_extra_one_half": False,
    "undirected_edge_single_common_conductance": (
        "c_ij=pi_h_i*q_ij=pi_h_j*q_ji"
    ),
}

EXPECTED_GAUGE = {
    "box_mass": "M_L=integral_Omega_L_pi_dx",
    "conditional_renormalization_to_one": False,
    "gauged_mass": "pi_h_i=g_h_L*tilde_pi_h_i",
    "global_mass_identity": "sum_i_pi_h_i=M_L",
    "ideal_common_conductance": (
        "c_ij=g_h_L*tilde_pi_h_i*q_ij=g_h_L*tilde_pi_h_j*q_ji"
    ),
    "raw_reversible_mass": "tilde_pi_h_i",
    "scale_formula": "g_h_L=M_L/sum_i_tilde_pi_h_i",
    "target": "restricted_fixed_box_mass_not_full_space_probability_one",
}

EXPECTED_PRODUCTION = {
    "common_conductance_intervals_constructed_for_every_declared_edge": False,
    "current_single_axis_diagnostic_generalized_to_all_configurations": False,
    "current_single_axis_diagnostic_raw_containment": True,
    "gauge_enclosures_frozen_for_every_declared_configuration": False,
    "gauged_ideal_member_containment_proved_for_every_declared_configuration": False,
    "ideal_analytic_common_conductance_is_mosco_object": True,
    "production_centre_h_to_zero_theorem_claimed": False,
    "production_centres_accepted_as_exactly_reversible": False,
    "production_interval_width_belongs_to": "E_eval_not_E_space",
    "raw_containment_scope": "ungauged_primitives_and_directed_rates_only",
    "raw_to_gauged_bridge_proved": False,
}

EXPECTED_CONTROL = {
    "constraints": {
        "each_weight_nonnegative": True,
        "exact_sum_one_required": True,
        "finite_control_ids_only": True,
    },
    "control_ids": ["m1", "m2", "m3"],
    "exclusions": {
        "actual_control_values_committed_for_c0": False,
        "actual_control_values_included": False,
        "budget_value_included": False,
        "control_payload_path_included": False,
        "positive_budget_result_values_included": False,
        "result_payload_path_included": False,
    },
    "future_source": {
        "required_before_complete_c0": True,
        "requirements": [
            "immutable_exact_rational_control_values",
            "independent_result_blind_review",
            "no_scientific_result_values",
            "separate_hash_bound_source",
        ],
    },
    "schema": "encounter_continuum_c0_control_method_commitment_v2",
    "status": "FROZEN_METHOD_ONLY_NO_CONTROL_VALUES_NO_RESULT_VALUES_COMPLETE_C0_OPEN",
}

EXPECTED_SOURCE_POLICY = {
    "allowed_opened_source_roles": sorted(FROZEN_SOURCES),
    "embedded_source_paths_followed": False,
    "living_continuum_program_pinned": False,
    "opaque_scratch_or_result_payload_opened": False,
    "positive_budget_design_note_opened": False,
    "same_bytes_used_for_source_hash_and_parse": True,
}

EXPECTED_PREVIOUS = {
    "path": str(V1_RELATIVE),
    "sha256": V1_SHA256,
    "supersession_reason": (
        "result_blindness_repair_source_hash_drift_and_ambiguous_P_h_denominator"
    ),
    "v1_bytes_mutated": False,
}

EXPECTED_CONFIGURATION_ORDER = [
    "O113/Base",
    "E128/Base",
    "O129/Base",
    "O161/Base",
    "M+",
    "R+",
    "MR+",
    "MR+F",
    "A_M",
    "A_R",
    "A_Y",
    "A_MRY",
]

EXPECTED_EQUATIONS = [
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.6a",
    "2.7",
    "2.7a",
    "2.8",
    "2.8a",
    "2.9",
    "2.10",
    "2.11",
    "2.12",
    "2.13",
    "2.14",
    "2.15",
    "2.16",
    "2.17",
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.4a",
    "4.4b",
    "4.4c",
    "4.4d",
    "4.5",
    "4.5a",
    "4.5b",
]

EXPECTED_INITIAL = {
    "analytic_mass_exact": "1/1",
    "initial_probability_cell_mass": "p0_h_i=integral_C_i_q0_dx",
    "initial_reference_mass": "pi_h_i",
    "meshwise_renormalization": False,
    "requirements": [
        "q0_in_X_pi",
        "q0_nonnegative",
        "integral_q0_dx_equals_one",
        "support_closure_strictly_inside_every_declared_nonperiodic_box",
    ],
    "source_path": "artifacts/data/physical_initial_analytic_source_v1.json",
    "support_certificate": {
        "configuration_count_checked": 12,
        "global_minimum_clearance_exact": (
            "106645239176133349/288230376151711744"
        ),
        "midpoint_support_closure_exact": [
            "34587645138205413/288230376151711744",
            "46116860184273883/288230376151711744",
        ],
        "nonperiodic_axes_checked": 24,
        "periodic_axes_checked": 12,
        "periodic_support_handled_as_wrapped_arc": True,
        "relative_parallel_support_closure_exact": [
            "-106645239176133339/288230376151711744",
            "-95116024130064869/288230376151711744",
        ],
        "strict_side_inequalities_checked": 48,
        "support_closure_strictly_inside_all_nonperiodic_boxes": True,
    },
    "unique_discrete_density_ratio": "u0_h_i=p0_h_i/pi_h_i=P_h[u0]_i",
}

EXPECTED_KILLING = {
    "contact": (
        "indicator(relative_parallel^2+minimum_image(relative_perpendicular)^2<=a^2)"
    ),
    "field": "W^-1*contact*sum_j(w_c_j*phi_j(midpoint))",
    "profile_count": 4,
    "profiles": "fixed_bounded_nonnegative_unit_integral_compact_bumps",
    "sharp_contact_retained": True,
}

EXPECTED_MESH = {
    "alignment_classes": [
        "cell_centred_reflecting",
        "vertex_centred_reflecting_dual",
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    ],
    "box_nesting_relations": [
        "O129/Base_midpoint_subset_M+_midpoint",
        "O129/Base_relative_subset_R+_relative",
        "M+_and_R+_product_equals_MR+_box",
        "MR+_box_equals_MR+F_box",
    ],
    "configuration_count": 12,
    "configuration_order": EXPECTED_CONFIGURATION_ORDER,
    "source_path": "artifacts/data/physical_configuration_family_control_free_v1.json",
}

EXPECTED_ALIGNMENTS = {
    "cell_centred_reflecting",
    "vertex_centred_reflecting_dual",
    "cell_centred_periodic_base",
    "cell_centred_periodic_half_shift",
}

FORBIDDEN_RESULT_KEYS = {
    "basin_mass",
    "control_weights",
    "mode_count_result",
    "peak_heights",
    "peak_time",
    "positive_budget_result",
    "root_interval",
    "root_times",
    "selected_weights",
    "scientific_result_values",
    "stationary_signature",
}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def _normalize_key(key: str) -> str:
    first = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return re.sub(r"[^a-z0-9]+", "_", first.lower()).strip("_")


def _pairs_hook(code: str):
    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise C0V2Hold(code, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return hook


def _reject_constant(code: str):
    def reject(value: str) -> Any:
        raise C0V2Hold(code, f"nonfinite JSON number: {value}")

    return reject


def _reject_float(code: str):
    def reject(value: str) -> Any:
        raise C0V2Hold(code, f"JSON float forbidden in exact contract/source: {value}")

    return reject


def _parse_int(code: str):
    def parse(value: str) -> int:
        if len(value.lstrip("-")) > MAX_JSON_INTEGER_DIGITS:
            raise C0V2Hold(code, "JSON integer exceeds digit limit")
        try:
            return int(value)
        except ValueError as error:
            raise C0V2Hold(code, "invalid JSON integer") from error

    return parse


def _validate_json_bounds(value: Any, *, code: str) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if depth > MAX_JSON_DEPTH or nodes > MAX_JSON_NODES:
            raise C0V2Hold(code, "JSON exceeds nesting or node limit")
        if type(current) is dict:
            stack.extend((child, depth + 1) for child in current.values())
        elif type(current) is list:
            stack.extend((child, depth + 1) for child in current)


def _parse_json(payload: bytes, *, code: str, canonical: bool) -> dict[str, Any]:
    if len(payload) > MAX_FILE_BYTES:
        raise C0V2Hold(code, "JSON bytes exceed size cap before parsing")
    if payload.startswith(b"\xef\xbb\xbf") or not payload.endswith(b"\n"):
        raise C0V2Hold(code, "UTF-8 JSON must have no BOM and one final newline")
    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_pairs_hook(code),
            parse_constant=_reject_constant(code),
            parse_float=_reject_float(code),
            parse_int=_parse_int(code),
        )
    except C0V2Hold:
        raise
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        MemoryError,
        RecursionError,
        ValueError,
    ) as error:
        raise C0V2Hold(code, "invalid UTF-8 JSON") from error
    if type(decoded) is not dict:
        raise C0V2Hold(code, "top-level JSON must be an object")
    _validate_json_bounds(decoded, code=code)
    if canonical:
        try:
            canonical_payload = canonical_json_bytes(decoded)
        except RecursionError as error:
            raise C0V2Hold(code, "JSON nesting exceeds canonical encoder limit") from error
        if payload != canonical_payload:
            raise C0V2Hold(code, "candidate is not canonical sorted two-space JSON")
    return decoded


def _read_capped(fd: int, *, code: str, label: str) -> bytes:
    blocks: list[bytes] = []
    total = 0
    while True:
        block = os.read(fd, min(1 << 20, MAX_FILE_BYTES - total + 1))
        if not block:
            break
        total += len(block)
        if total > MAX_FILE_BYTES:
            raise C0V2Hold(code, f"source grew beyond size cap: {label}")
        blocks.append(block)
    return b"".join(blocks)


def read_regular_snapshot(path: Path, *, code: str) -> bytes:
    if not hasattr(os, "O_NOFOLLOW"):
        raise C0V2Hold(code, "platform lacks O_NOFOLLOW")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise C0V2Hold(code, f"cannot open regular source: {path}") from error
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise C0V2Hold(code, f"not a regular file: {path}")
        if before.st_size > MAX_FILE_BYTES:
            raise C0V2Hold(code, f"file exceeds size cap: {path}")
        payload = _read_capped(fd, code=code, label=str(path))
        after = os.fstat(fd)
        try:
            named = os.lstat(path)
        except OSError as error:
            raise C0V2Hold(code, f"source name changed during read: {path}") from error
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        if identity != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise C0V2Hold(code, f"source changed during read: {path}")
        if stat.S_ISLNK(named.st_mode) or (named.st_dev, named.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            raise C0V2Hold(code, f"source path was replaced or linked: {path}")
        if len(payload) != before.st_size:
            raise C0V2Hold(code, f"source size changed during read: {path}")
        return payload
    except OSError as error:
        raise C0V2Hold(code, f"regular source read failed: {path}") from error
    finally:
        os.close(fd)


def read_relative_snapshot(root: Path, relative: Path, *, code: str) -> bytes:
    """Open each component with descriptor-relative O_NOFOLLOW semantics."""

    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise C0V2Hold(code, f"invalid relative source path: {relative}")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise C0V2Hold(code, "platform lacks descriptor-safe directory flags")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW | os.O_DIRECTORY
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    descriptors: list[int] = []
    try:
        parent_fd = os.open(root, directory_flags)
        descriptors.append(parent_fd)
        for component in relative.parts[:-1]:
            parent_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            descriptors.append(parent_fd)
        file_fd = os.open(relative.name, file_flags, dir_fd=parent_fd)
        descriptors.append(file_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise C0V2Hold(code, f"source is not regular: {relative}")
        if before.st_size > MAX_FILE_BYTES:
            raise C0V2Hold(code, f"source exceeds size cap: {relative}")
        payload = _read_capped(file_fd, code=code, label=str(relative))
        after = os.fstat(file_fd)
        named = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        if identity != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise C0V2Hold(code, f"source changed during read: {relative}")
        if stat.S_ISLNK(named.st_mode) or (named.st_dev, named.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            raise C0V2Hold(code, f"source name changed during read: {relative}")
        if len(payload) != before.st_size:
            raise C0V2Hold(code, f"source size changed during read: {relative}")
        return payload
    except C0V2Hold:
        raise
    except OSError as error:
        raise C0V2Hold(code, f"cannot open relative source: {relative}") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _require_exact(observed: Any, expected: Any, code: str, label: str) -> None:
    if observed != expected or type(observed) is not type(expected):
        raise C0V2Hold(code, f"{label} mismatch")


def _is_forbidden_payload_path(value: str) -> bool:
    lowered = value.lower().replace("\\", "/")
    segments = {segment for segment in lowered.split("/") if segment}
    exact_names = {
        "scratch",
        "result",
        "results",
        "control",
        "controls",
        "result.json",
        "results.json",
        "control.json",
        "controls.json",
    }
    forbidden_suffixes = (
        "_result.json",
        "-result.json",
        "_results.json",
        "-results.json",
        "_control.json",
        "-control.json",
        "_controls.json",
        "-controls.json",
    )
    return bool(segments & exact_names) or any(
        segment.endswith(forbidden_suffixes) for segment in segments
    )


def _scan_result_bearing(value: Any, *, code: str = HOLD_RESULT_BLINDNESS) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if depth > MAX_JSON_DEPTH or nodes > MAX_JSON_NODES:
            raise C0V2Hold(code, "JSON exceeds nesting or node limit")
        if type(current) is dict:
            for key, child in current.items():
                if _normalize_key(key) in FORBIDDEN_RESULT_KEYS:
                    raise C0V2Hold(code, f"result-bearing key present: {key}")
                stack.append((child, depth + 1))
        elif type(current) is list:
            stack.extend((child, depth + 1) for child in current)
        elif type(current) is str and _is_forbidden_payload_path(current):
            raise C0V2Hold(
                code,
                f"forbidden scratch/result/control path present: {current}",
            )


def _fraction_from_hex(value: Any, code: str, label: str) -> Fraction:
    if type(value) is not str:
        raise C0V2Hold(code, f"{label} is not a binary64 hex string")
    try:
        binary = float.fromhex(value)
    except ValueError as error:
        raise C0V2Hold(code, f"invalid binary64 hex for {label}") from error
    if not math.isfinite(binary):
        raise C0V2Hold(code, f"nonfinite binary64 hex for {label}")
    return Fraction(*binary.as_integer_ratio())


def _fraction(value: Any, code: str, label: str) -> Fraction:
    if type(value) is not str:
        raise C0V2Hold(code, f"{label} is not an exact rational string")
    try:
        exact = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise C0V2Hold(code, f"invalid exact rational for {label}") from error
    return exact


def _wrapped_arc_segments(
    start: Fraction,
    period: Fraction,
    centre: Fraction,
    half_width: Fraction,
) -> tuple[tuple[Fraction, Fraction], ...]:
    if period <= 0 or not 0 < 2 * half_width < period:
        raise C0V2Hold(HOLD_INITIAL, "invalid periodic support arc")
    end = start + period
    normalized = start + ((centre - start) % period)
    lower = normalized - half_width
    upper = normalized + half_width
    if lower < start:
        segments = ((start, upper), (lower + period, end))
    elif upper > end:
        segments = ((start, upper - period), (lower, end))
    else:
        segments = ((lower, upper),)
    ordered = tuple(sorted(segments))
    if (
        any(not start <= left < right <= end for left, right in ordered)
        or sum((right - left for left, right in ordered), Fraction(0)) != 2 * half_width
    ):
        raise C0V2Hold(HOLD_INITIAL, "periodic support arc split is inconsistent")
    return ordered


def _periodic_cell_segments(
    start: Fraction,
    period: Fraction,
    size: int,
    shift: Fraction,
) -> tuple[tuple[Fraction, Fraction], ...]:
    if type(size) is not int or size <= 0 or period <= 0:
        raise C0V2Hold(HOLD_MESH, "invalid periodic cell request")
    end = start + period
    step = period / size
    segments: list[tuple[Fraction, Fraction]] = []
    for index in range(size):
        left = start + ((index * step + shift) % period)
        right = left + step
        if right <= end:
            segments.append((left, right))
        else:
            segments.extend(((left, end), (start, start + right - end)))
    ordered = tuple(sorted(segments))
    if (
        not ordered
        or ordered[0][0] != start
        or ordered[-1][1] != end
        or any(left_end != right_start for (_, left_end), (right_start, _) in zip(ordered, ordered[1:]))
        or sum((right - left for left, right in ordered), Fraction(0)) != period
    ):
        raise C0V2Hold(HOLD_MESH, "periodic cells do not exactly partition the torus")
    return ordered


def _validate_parameters(parameters: Any) -> dict[str, Fraction]:
    _require_exact(parameters, EXPECTED_PARAMETERS, HOLD_PARAMETERS, "physical parameters")
    exact: dict[str, Fraction] = {}
    for name, record in parameters.items():
        rational = _fraction(record["exact"], HOLD_PARAMETERS, name)
        binary = _fraction_from_hex(record["binary64_hex"], HOLD_PARAMETERS, name)
        if rational != binary:
            raise C0V2Hold(HOLD_PARAMETERS, f"exact/binary64 mismatch for {name}")
        exact[name] = rational
    if min(exact.values()) <= 0 or 2 * exact["contact_radius_a"] >= exact["W"]:
        raise C0V2Hold(HOLD_PARAMETERS, "positivity or torus cut-locus condition failed")
    return exact


def _validate_witnesses(witnesses: Any) -> None:
    if type(witnesses) is not dict or set(witnesses) != {
        "complex_positivity",
        "global_gauge",
        "map_denominators",
        "row_column",
    }:
        raise C0V2Hold(HOLD_WITNESSES, "witness key set mismatch")
    maps = witnesses["map_denominators"]
    cell_mass = [_fraction(value, HOLD_WITNESSES, "M") for value in maps.get("M_i_pi", [])]
    discrete_mass = [
        _fraction(value, HOLD_WITNESSES, "pi_h") for value in maps.get("pi_h_i", [])
    ]
    integrals = [
        _fraction(value, HOLD_WITNESSES, "cell integral")
        for value in maps.get("cell_integrals_of_u_pi", [])
    ]
    vector = [_fraction(value, HOLD_WITNESSES, "v") for value in maps.get("v", [])]
    if not (len(cell_mass) == len(discrete_mass) == len(integrals) == len(vector) == 2):
        raise C0V2Hold(HOLD_WITNESSES, "map witness dimension mismatch")
    projection = [integrals[i] / discrete_mass[i] for i in range(2)]
    average = [integrals[i] / cell_mass[i] for i in range(2)]
    rho = [cell_mass[i] / discrete_mass[i] for i in range(2)]
    inner_j = sum((vector[i] * integrals[i] for i in range(2)), Fraction(0))
    inner_p = sum(
        (discrete_mass[i] * vector[i] * projection[i] for i in range(2)), Fraction(0)
    )
    inner_a = sum(
        (discrete_mass[i] * vector[i] * average[i] for i in range(2)), Fraction(0)
    )
    expected_values = {
        "P_h_u": projection,
        "A_h_u": average,
        "rho_i": rho,
    }
    for key, values in expected_values.items():
        observed = [_fraction(value, HOLD_WITNESSES, key) for value in maps.get(key, [])]
        if observed != values:
            raise C0V2Hold(HOLD_WITNESSES, f"recomputed map witness mismatch: {key}")
    if (
        _fraction(maps.get("inner_Jv_u"), HOLD_WITNESSES, "inner J") != inner_j
        or _fraction(maps.get("inner_v_Pu"), HOLD_WITNESSES, "inner P") != inner_p
        or _fraction(
            maps.get("inner_v_Au_wrong_for_adjoint"), HOLD_WITNESSES, "inner A"
        )
        != inner_a
        or inner_j != inner_p
        or inner_a == inner_j
    ):
        raise C0V2Hold(HOLD_WITNESSES, "adjoint denominator witness failed")

    gauge = witnesses["global_gauge"]
    box_mass = _fraction(gauge.get("box_mass"), HOLD_WITNESSES, "box mass")
    raw = [_fraction(value, HOLD_WITNESSES, "raw mass") for value in gauge.get("raw_masses", [])]
    correct = box_mass / sum(raw, Fraction(0))
    gauged = [correct * value for value in raw]
    if (
        _fraction(gauge.get("correct_gauge"), HOLD_WITNESSES, "gauge") != correct
        or [_fraction(value, HOLD_WITNESSES, "gauged mass") for value in gauge.get("gauged_masses", [])]
        != gauged
        or sum(gauged, Fraction(0)) != box_mass
        or gauge.get("unit_sum_normalization_is_wrong") is not True
    ):
        raise C0V2Hold(HOLD_WITNESSES, "global gauge witness failed")

    complex_witness = witnesses["complex_positivity"]
    if (
        complex_witness.get("u") != ["i", "0"]
        or _fraction(
            complex_witness.get("bilinear_edge_square_wrong"), HOLD_WITNESSES, "bilinear"
        )
        != -1
        or _fraction(
            complex_witness.get("sesquilinear_edge_square_correct"),
            HOLD_WITNESSES,
            "sesquilinear",
        )
        != 1
    ):
        raise C0V2Hold(HOLD_WITNESSES, "complex positivity witness failed")

    row = witnesses["row_column"]
    matrix = [
        [_fraction(value, HOLD_WITNESSES, "Q") for value in line]
        for line in row.get("Q", [])
    ]
    mass = [_fraction(value, HOLD_WITNESSES, "pi_h") for value in row.get("pi_h", [])]
    probability = [
        _fraction(value, HOLD_WITNESSES, "probability")
        for value in row.get("probability_column", [])
    ]
    if len(matrix) != 2 or any(len(line) != 2 for line in matrix) or len(mass) != 2:
        raise C0V2Hold(HOLD_WITNESSES, "row witness dimension mismatch")
    if any(sum(line, Fraction(0)) != 0 for line in matrix):
        raise C0V2Hold(HOLD_WITNESSES, "row generator witness has nonzero row sum")
    if mass[0] * matrix[0][1] != mass[1] * matrix[1][0]:
        raise C0V2Hold(HOLD_WITNESSES, "row witness is not reversible")
    qp = [sum((matrix[i][j] * probability[j] for j in range(2)), Fraction(0)) for i in range(2)]
    qtp = [sum((matrix[j][i] * probability[j] for j in range(2)), Fraction(0)) for i in range(2)]
    if (
        sum(qp, Fraction(0))
        != _fraction(row.get("incorrect_Q_p_total_derivative"), HOLD_WITNESSES, "Qp")
        or sum(qtp, Fraction(0))
        != _fraction(row.get("transpose_Q_p_total_derivative"), HOLD_WITNESSES, "Qtp")
        or sum(qp, Fraction(0)) == 0
        or sum(qtp, Fraction(0)) != 0
    ):
        raise C0V2Hold(HOLD_WITNESSES, "row/column witness failed")


def _load_sources(report: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    observed_hashes: dict[str, str] = {}
    for role, descriptor in FROZEN_SOURCES.items():
        relative = Path(descriptor["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise C0V2Hold(HOLD_SOURCES, f"invalid fixed source path for {role}")
        payload = read_relative_snapshot(report, relative, code=HOLD_SOURCES)
        observed_hashes[role] = _sha256(payload)
        if observed_hashes[role] != descriptor["sha256"]:
            raise C0V2Hold(HOLD_SOURCES, f"source hash mismatch for {role}")
        decoded = _parse_json(payload, code=HOLD_SOURCES, canonical=False)
        _scan_result_bearing(decoded)
        if set(decoded) != EXPECTED_SOURCE_TOP_KEYS[role]:
            raise C0V2Hold(HOLD_SOURCES, f"source top-level schema mismatch for {role}")
        if role != "initial_source" and payload != canonical_json_bytes(decoded):
            raise C0V2Hold(HOLD_SOURCES, f"source is not canonical JSON for {role}")
        loaded[role] = decoded
    return loaded, observed_hashes


def _validate_initial_and_mesh(
    contract: dict[str, Any],
    family: dict[str, Any],
    initial: dict[str, Any],
) -> dict[str, Any]:
    if (
        initial.get("schema") != "encounter_physical_initial_analytic_source_v1"
        or initial.get("scope") != "physical_initial_law_only_no_control_no_budget"
        or initial.get("analytic_total_mass_exact") != "1/1"
        or initial.get("construction")
        != "independent_product_of_three_analytically_normalized_compact_bumps"
        or initial.get("periodic_wrap") != "sum_over_periodic_images_before_cell_integration"
        or initial.get("shared_normalizer_across_cells_and_axes") is not True
    ):
        raise C0V2Hold(HOLD_INITIAL, "initial source semantics mismatch")
    if (
        family.get("schema")
        != "encounter_physical_configuration_family_control_free_v1"
        or family.get("scope") != "physical_d2_control_free_axis_and_initial_geometry_only"
        or family.get("contains_budget_value") is not False
        or family.get("contains_control_values") is not False
        or family.get("authorizes_scientific_execution") is not False
    ):
        raise C0V2Hold(HOLD_MESH, "configuration source crossed result-blind scope")
    rows = family.get("configurations")
    order = family.get("configuration_order")
    if type(rows) is not list or order != EXPECTED_CONFIGURATION_ORDER or len(rows) != 12:
        raise C0V2Hold(HOLD_MESH, "configuration enumeration mismatch")
    labels = [row.get("label") if type(row) is dict else None for row in rows]
    if labels != order or len(set(labels)) != len(labels):
        raise C0V2Hold(HOLD_MESH, "configuration labels are missing, reordered, or duplicated")
    if family.get("configuration_count") != len(rows):
        raise C0V2Hold(HOLD_MESH, "configuration count mismatch")
    if set(family.get("axis_construction_contracts", {})) != EXPECTED_ALIGNMENTS:
        raise C0V2Hold(HOLD_MESH, "alignment class mismatch")
    dynamics = family.get("dynamics")
    if type(dynamics) is not dict:
        raise C0V2Hold(HOLD_MESH, "family dynamics are missing")
    torus_start = _fraction(
        dynamics.get("transverse_domain_start_exact"), HOLD_MESH, "torus start"
    )
    torus_period = _fraction(
        dynamics.get("transverse_period_exact"), HOLD_MESH, "torus period"
    )

    half = _fraction_from_hex(initial.get("half_width_binary64_hex"), HOLD_INITIAL, "half width")
    if half <= 0:
        raise C0V2Hold(HOLD_INITIAL, "initial half width is not positive")
    starts = initial.get("starts_binary64_hex")
    if type(starts) is not dict:
        raise C0V2Hold(HOLD_INITIAL, "initial centres missing")
    centres = {
        axis: _fraction_from_hex(starts.get(axis), HOLD_INITIAL, f"initial centre {axis}")
        for axis in ("midpoint", "relative_parallel", "relative_perpendicular")
    }
    source_supports = {
        axis: (centres[axis] - half, centres[axis] + half)
        for axis in ("midpoint", "relative_parallel")
    }
    clearances: list[Fraction] = []
    periodic_checked = 0
    for row in rows:
        shape = row.get("shape")
        if type(shape) is not list or len(shape) != 3:
            raise C0V2Hold(HOLD_MESH, f"invalid shape for {row.get('label')}")
        for index, axis in enumerate(("midpoint", "relative_parallel")):
            axis_record = row.get(axis)
            if type(axis_record) is not dict or axis_record.get("size") != shape[index]:
                raise C0V2Hold(HOLD_MESH, f"invalid {axis} row geometry")
            if axis_record.get("alignment") not in {
                "cell_centred_reflecting",
                "vertex_centred_reflecting_dual",
            }:
                raise C0V2Hold(HOLD_MESH, f"invalid nonperiodic alignment for {axis}")
            lower = _fraction_from_hex(
                axis_record.get("lower_binary64_hex"), HOLD_MESH, f"{axis} lower"
            )
            upper = _fraction_from_hex(
                axis_record.get("upper_binary64_hex"), HOLD_MESH, f"{axis} upper"
            )
            support_lower, support_upper = source_supports[axis]
            if not lower < support_lower < support_upper < upper:
                raise C0V2Hold(HOLD_INITIAL, f"initial support touches/exits {row['label']} {axis}")
            clearances.extend((support_lower - lower, upper - support_upper))
        periodic = row.get("relative_perpendicular")
        if type(periodic) is not dict or periodic.get("size") != shape[2]:
            raise C0V2Hold(HOLD_MESH, "invalid periodic row geometry")
        size = periodic.get("size")
        if type(size) is not int or size <= 0:
            raise C0V2Hold(HOLD_MESH, "invalid periodic size")
        alignment = periodic.get("alignment")
        expected_shift = (
            Fraction(0)
            if alignment == "cell_centred_periodic_base"
            else torus_period / (2 * size)
        )
        if alignment not in {"cell_centred_periodic_base", "cell_centred_periodic_half_shift"}:
            raise C0V2Hold(HOLD_MESH, "invalid periodic alignment")
        if _fraction(periodic.get("periodic_shift_exact"), HOLD_MESH, "periodic shift") != expected_shift:
            raise C0V2Hold(HOLD_MESH, "periodic shift mismatch")
        _periodic_cell_segments(torus_start, torus_period, size, expected_shift)
        if math.prod(shape) != row.get("expected_states"):
            raise C0V2Hold(HOLD_MESH, "state-count mismatch")
        periodic_checked += 1

    period = _fraction(initial.get("transverse_period_exact"), HOLD_INITIAL, "period")
    if period != 1 or period != torus_period or torus_start != Fraction(-1, 2):
        raise C0V2Hold(HOLD_INITIAL, "initial/family torus binding mismatch")
    support_arc = _wrapped_arc_segments(
        torus_start,
        period,
        centres["relative_perpendicular"],
        half,
    )
    if not support_arc:
        raise C0V2Hold(HOLD_INITIAL, "periodic initial support arc is degenerate")
    certificate = contract.get("initial_law", {}).get("support_certificate")
    expected_certificate = {
        "configuration_count_checked": 12,
        "global_minimum_clearance_exact": str(min(clearances)),
        "midpoint_support_closure_exact": [str(value) for value in source_supports["midpoint"]],
        "nonperiodic_axes_checked": 24,
        "periodic_axes_checked": periodic_checked,
        "periodic_support_handled_as_wrapped_arc": True,
        "relative_parallel_support_closure_exact": [
            str(value) for value in source_supports["relative_parallel"]
        ],
        "strict_side_inequalities_checked": 48,
        "support_closure_strictly_inside_all_nonperiodic_boxes": True,
    }
    _require_exact(certificate, expected_certificate, HOLD_INITIAL, "support certificate")
    return expected_certificate


def _validate_killing(
    killing: dict[str, Any],
    family: dict[str, Any],
    exact: dict[str, Fraction],
) -> None:
    if (
        killing.get("schema") != "encounter_physical_killing_geometry_source_v1"
        or killing.get("physical_dimension") != 2
        or killing.get("quotient_dimension") != 3
    ):
        raise C0V2Hold(HOLD_KILLING, "killing source schema/dimension mismatch")
    flags = killing.get("flags", {})
    for key in (
        "contains_budget_value",
        "contains_control_values",
        "positive_budget_executed",
        "science_executed",
    ):
        if flags.get(key) is not False:
            raise C0V2Hold(HOLD_KILLING, f"killing source promoted forbidden flag: {key}")
    contact = killing.get("contact_geometry", {})
    radius = _fraction(contact.get("radius_exact"), HOLD_KILLING, "contact radius")
    period = _fraction(contact.get("transverse_period_exact"), HOLD_KILLING, "contact period")
    basis = killing.get("support_basis", {})
    if (
        radius != exact["contact_radius_a"]
        or period != exact["W"]
        or not 2 * radius < period
        or basis.get("profile_count") != 4
        or basis.get("analytic_integral_each") != "1/1"
    ):
        raise C0V2Hold(HOLD_KILLING, "killing geometry semantics mismatch")
    width = _fraction(basis.get("half_width_exact"), HOLD_KILLING, "patch half width")
    centres = [_fraction(value, HOLD_KILLING, "patch centre") for value in basis.get("centres_exact", [])]
    rows = family.get("configurations")
    if width <= 0 or len(centres) != 4 or type(rows) is not list:
        raise C0V2Hold(HOLD_KILLING, "invalid patch support data")
    for row in rows:
        if type(row) is not dict:
            raise C0V2Hold(HOLD_KILLING, "invalid configuration row for killing support")
        midpoint = row.get("midpoint", {})
        relative = row.get("relative_parallel", {})
        midpoint_lower = _fraction_from_hex(
            midpoint.get("lower_binary64_hex"), HOLD_KILLING, "midpoint lower"
        )
        midpoint_upper = _fraction_from_hex(
            midpoint.get("upper_binary64_hex"), HOLD_KILLING, "midpoint upper"
        )
        relative_lower = _fraction_from_hex(
            relative.get("lower_binary64_hex"), HOLD_KILLING, "relative lower"
        )
        relative_upper = _fraction_from_hex(
            relative.get("upper_binary64_hex"), HOLD_KILLING, "relative upper"
        )
        if any(
            not midpoint_lower < centre - width < centre + width < midpoint_upper
            for centre in centres
        ):
            raise C0V2Hold(
                HOLD_KILLING,
                f"patch support touches/exits {row.get('label')} midpoint box",
            )
        if not relative_lower < -radius < radius < relative_upper:
            raise C0V2Hold(
                HOLD_KILLING,
                f"contact support touches/exits {row.get('label')} relative box",
            )


def verify_contract_bytes(payload: bytes, *, report: Path = REPORT) -> dict[str, Any]:
    contract = _parse_json(payload, code=HOLD_ENCODING, canonical=True)
    _scan_result_bearing(contract)
    if set(contract) != EXPECTED_TOP_KEYS:
        raise C0V2Hold(HOLD_SCHEMA, "top-level key set mismatch")
    _require_exact(
        contract.get("schema"),
        "encounter_continuum_c0_model_contract_candidate_v2",
        HOLD_SCHEMA,
        "schema",
    )
    _require_exact(
        contract.get("status"),
        "HOLD_C0_V2_CANDIDATE_RESULT_BLIND_MAPS_EXPLICIT_PRODUCTION_GAUGE_BRIDGE_OPEN",
        HOLD_SCHEMA,
        "status",
    )
    _require_exact(contract.get("physical_dimension"), 2, HOLD_SCHEMA, "physical dimension")
    _require_exact(contract.get("quotient_dimension"), 3, HOLD_SCHEMA, "quotient dimension")
    _require_exact(contract.get("claim_boundary"), EXPECTED_CLAIMS, HOLD_CLAIMS, "claims")
    _require_exact(contract.get("continuum_object"), EXPECTED_CONTINUUM, HOLD_CONTINUUM, "continuum")
    _require_exact(contract.get("boundary_conditions"), EXPECTED_BOUNDARY, HOLD_BOUNDARY, "boundary")
    exact = _validate_parameters(contract.get("physical_parameters"))
    _require_exact(contract.get("finite_volume_identification"), EXPECTED_MAPS, HOLD_MAPS, "maps")
    _require_exact(contract.get("scalar_convention"), EXPECTED_SCALAR, HOLD_OPERATOR, "scalar convention")
    _require_exact(
        contract.get("discrete_operator_convention"), EXPECTED_OPERATOR, HOLD_OPERATOR, "operator"
    )
    _require_exact(contract.get("stationary_mass_gauge"), EXPECTED_GAUGE, HOLD_GAUGE, "gauge")
    _require_exact(
        contract.get("production_gauge_bridge"), EXPECTED_PRODUCTION, HOLD_PRODUCTION, "production"
    )
    _require_exact(contract.get("control_contract"), EXPECTED_CONTROL, HOLD_CONTROL, "control")
    _require_exact(contract.get("source_policy"), EXPECTED_SOURCE_POLICY, HOLD_SOURCES, "source policy")
    _require_exact(contract.get("frozen_sources"), FROZEN_SOURCES, HOLD_SOURCES, "source roles")
    _require_exact(contract.get("previous_contract"), EXPECTED_PREVIOUS, HOLD_LEGACY, "legacy binding")
    _require_exact(
        contract.get("equation_contract"), EXPECTED_EQUATIONS, HOLD_CONTINUUM, "equations"
    )
    _require_exact(contract.get("initial_law"), EXPECTED_INITIAL, HOLD_INITIAL, "initial law")
    _require_exact(contract.get("killing_field"), EXPECTED_KILLING, HOLD_KILLING, "killing")
    _require_exact(contract.get("mesh_contract"), EXPECTED_MESH, HOLD_MESH, "mesh")
    try:
        _validate_witnesses(contract.get("witnesses"))
    except C0V2Hold:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise C0V2Hold(HOLD_WITNESSES, "malformed exact witness") from error

    sources, observed_hashes = _load_sources(report)
    if sources["mathematical_source"].get("identification_maps") != EXPECTED_MAPS:
        raise C0V2Hold(HOLD_SOURCES, "mathematical source map semantics mismatch")
    if sources["mathematical_source"].get("stationary_mass_gauge") != EXPECTED_GAUGE:
        raise C0V2Hold(HOLD_SOURCES, "mathematical source gauge semantics mismatch")
    if sources["mathematical_source"].get("production_boundary") != EXPECTED_PRODUCTION:
        raise C0V2Hold(HOLD_SOURCES, "mathematical source production boundary mismatch")
    if sources["control_method_commitment"] != EXPECTED_CONTROL:
        raise C0V2Hold(HOLD_CONTROL, "control method commitment mismatch")

    support = _validate_initial_and_mesh(
        contract,
        sources["configuration_family"],
        sources["initial_source"],
    )
    _validate_killing(
        sources["killing_geometry_source"],
        sources["configuration_family"],
        exact,
    )
    legacy = read_relative_snapshot(report, V1_RELATIVE, code=HOLD_LEGACY)
    if _sha256(legacy) != V1_SHA256:
        raise C0V2Hold(HOLD_LEGACY, "historical C0-v1 bytes changed")
    if _sha256(payload) != EXPECTED_CONTRACT_SHA256:
        raise C0V2Hold(HOLD_SCHEMA, "candidate hash differs from audited v2 bytes")
    return {
        "complete_c0": False,
        "contract_sha256": _sha256(payload),
        "control_values_read": False,
        "gauged_ideal_member_containment_proved": False,
        "opened_auxiliary_paths": [str(V1_RELATIVE)],
        "opened_source_paths": [FROZEN_SOURCES[role]["path"] for role in sorted(FROZEN_SOURCES)],
        "positive_budget_scientific_values_read": False,
        "production_raw_to_gauged_bridge_proved": False,
        "release_eligible": False,
        "scratch_or_result_payload_read": False,
        "source_sha256s": observed_hashes,
        "status": PASS_STATUS,
        "support_certificate": support,
        "v1_sha256": _sha256(legacy),
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: validate_continuum_c0_model_contract_candidate_v2.py [contract.json]", file=sys.stderr)
        return 2
    path = DEFAULT_CONTRACT if not args else Path(args[0])
    try:
        payload = read_regular_snapshot(path, code=HOLD_ENCODING)
        receipt = verify_contract_bytes(payload)
    except C0V2Hold as error:
        print(json.dumps({"status": error.code, "message": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
