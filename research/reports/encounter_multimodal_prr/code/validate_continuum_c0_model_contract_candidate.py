#!/usr/bin/env python3
"""Fail-closed verifier for the result-blind continuum C0 contract candidate."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"

HOLD_ENCODING = "HOLD_C0_CONTRACT_ENCODING"
HOLD_SCHEMA = "HOLD_C0_CONTRACT_SCHEMA"
HOLD_CLAIMS = "HOLD_C0_CONTRACT_CLAIMS"
HOLD_PARAMETERS = "HOLD_C0_CONTRACT_PARAMETERS"
HOLD_UNITS = "HOLD_C0_CONTRACT_UNITS"
HOLD_CONTINUUM = "HOLD_C0_CONTRACT_CONTINUUM_OBJECT"
HOLD_BOUNDARY = "HOLD_C0_CONTRACT_BOUNDARY"
HOLD_EQUATIONS = "HOLD_C0_CONTRACT_EQUATIONS"
HOLD_IDENTIFICATION = "HOLD_C0_CONTRACT_IDENTIFICATION"
HOLD_SOURCES = "HOLD_C0_CONTRACT_SOURCES"
HOLD_CONTROL = "HOLD_C0_CONTRACT_CONTROL"
HOLD_INITIAL = "HOLD_C0_CONTRACT_INITIAL"
HOLD_KILLING = "HOLD_C0_CONTRACT_KILLING"
HOLD_MESH = "HOLD_C0_CONTRACT_MESH"
PASS_STATUS = "PASS_C0_CONTRACT_CANDIDATE_SEMANTIC_VERIFICATION_ONLY"


class C0ContractHold(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise C0ContractHold(HOLD_ENCODING, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse(payload: bytes) -> dict[str, Any]:
    if not payload.endswith(b"\n") or payload.startswith(b"\xef\xbb\xbf"):
        raise C0ContractHold(HOLD_ENCODING, "contract must be UTF-8 JSON with one final newline")
    try:
        text = payload.decode("utf-8")
        decoded = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=lambda value: (_ for _ in ()).throw(
                C0ContractHold(HOLD_ENCODING, f"nonfinite JSON number: {value}")
            ),
        )
    except C0ContractHold:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise C0ContractHold(HOLD_ENCODING, "invalid UTF-8 JSON") from error
    if type(decoded) is not dict:
        raise C0ContractHold(HOLD_SCHEMA, "top-level contract must be an object")
    return decoded


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def _require_exact(observed: Any, expected: Any, code: str, label: str) -> None:
    if observed != expected or type(observed) is not type(expected):
        raise C0ContractHold(code, f"{label} mismatch")


EXPECTED_TOP_KEYS = {
    "boundary_conditions",
    "claim_boundary",
    "control_contract",
    "continuum_object",
    "equation_contract",
    "finite_volume_identification",
    "frozen_sources",
    "initial_law",
    "killing_field",
    "mesh_contract",
    "physical_parameters",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "status",
}

EXPECTED_CLAIMS = {
    "c0a_operator_realization_proved": True,
    "complete_c0_independently_accepted": False,
    "c1_fixed_box_convergence_proved": False,
    "c2_quantitative_spatial_error_proved": False,
    "c3_derivative_box_error_proved": False,
    "continuum_stationary_topology_proved": False,
    "f0_complete": False,
    "positive_budget_scientific_values_read": False,
    "release_eligible": False,
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
    "W": {"binary64_hex": "0x1.0000000000000p+0", "exact": "1/1", "unit": "length"},
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

EXPECTED_EQUATIONS = [
    "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.6a", "2.7",
    "2.7a", "2.8", "2.8a", "2.9", "2.10", "2.11", "2.12", "2.13",
    "2.14", "2.15", "2.16", "2.17",
]

EXPECTED_IDENTIFICATION = {
    "J_h": "piecewise_constant_cell_value_embedding_from_H_h_to_H_L",
    "P_h": "pi_weighted_cell_average_from_H_L_to_H_h",
    "cell_density": "pi_h_pc_on_C_i=pi_h_i/abs(C_i)",
    "initial_projection": "u_0_h=P_h_u_0_or_H_h_consistent_approximation",
    "killing_projection": "physical_volume_cell_average_no_meshwise_renormalization",
    "stationary_mass_gauge": "sum_i_pi_h_i=integral_Omega_L_pi_dx",
}

EXPECTED_SOURCES = {
    "configuration_family": {
        "path": "artifacts/data/physical_configuration_family_control_free_v1.json",
        "sha256": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    },
    "continuum_program": {
        "path": "notes/continuum_research_program_v2.md",
        "sha256": "cef634e93e0f3f4e339759cc7521baab728a4778a06fffc5ebffd65513144995",
    },
    "initial_source": {
        "path": "artifacts/data/physical_initial_analytic_source_v1.json",
        "sha256": "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
    },
    "killing_geometry_source": {
        "path": "artifacts/data/physical_killing_geometry_source_v1.json",
        "sha256": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    },
    "physical_design": {
        "path": "notes/positive_b_fixed_control_robustness_design_v2.md",
        "sha256": "264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd",
    },
}

EXPECTED_CONTROL = {
    "control_ids": ["m1", "m2", "m3"],
    "exact_weight_rule": "numerator_divided_by_denominator_at_controls_control_id_weights",
    "opaque_result_blind_source_path": (
        "scratch/modal_certificate_exact_selector_method_only_result.json"
    ),
    "opaque_result_blind_source_sha256": (
        "77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98"
    ),
    "weight_constraints": "each_weight_nonnegative_and_exact_sum_one",
}

EXPECTED_INITIAL = {
    "analytic_mass_exact": "1/1",
    "requirements": ["q0_in_X_pi", "q0_nonnegative", "integral_q0_dx_equals_one"],
    "source_path": "artifacts/data/physical_initial_analytic_source_v1.json",
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
    "configuration_order": [
        "O113/Base", "E128/Base", "O129/Base", "O161/Base", "M+", "R+",
        "MR+", "MR+F", "A_M", "A_R", "A_Y", "A_MRY",
    ],
    "source_path": "artifacts/data/physical_configuration_family_control_free_v1.json",
}


def _load_json_file(path: Path, code: str) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise C0ContractHold(code, f"cannot read source {path}") from error
    if type(decoded) is not dict:
        raise C0ContractHold(code, f"source is not an object: {path}")
    return decoded


def _validate_parameters(parameters: Any) -> dict[str, Fraction]:
    _require_exact(parameters, EXPECTED_PARAMETERS, HOLD_PARAMETERS, "physical parameters")
    units = {record["unit"] for record in parameters.values()}
    if units != {
        "length", "length_squared_per_time", "inverse_time",
        "inverse_time_times_longitudinal_measure",
    }:
        raise C0ContractHold(HOLD_UNITS, "parameter units are incomplete")
    exact: dict[str, Fraction] = {}
    for name, record in parameters.items():
        try:
            value = Fraction(record["exact"])
            binary = Fraction.from_float(float.fromhex(record["binary64_hex"]))
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise C0ContractHold(HOLD_PARAMETERS, f"invalid exact parameter {name}") from error
        if value != binary:
            raise C0ContractHold(HOLD_PARAMETERS, f"decimal-for-dyadic drift in {name}")
        exact[name] = value
    if min(exact.values()) <= 0 or 2 * exact["contact_radius_a"] >= exact["W"]:
        raise C0ContractHold(HOLD_PARAMETERS, "positivity or torus cut-locus condition failed")
    if not math.isfinite(float(2 * exact["D"] * exact["W"] / exact["gamma"])):
        raise C0ContractHold(HOLD_PARAMETERS, "normalizer is nonfinite")
    return exact


def _validate_sources(contract: dict[str, Any], report: Path) -> dict[str, dict[str, Any]]:
    _require_exact(contract.get("frozen_sources"), EXPECTED_SOURCES, HOLD_SOURCES, "source roles")
    loaded: dict[str, dict[str, Any]] = {}
    for role, record in EXPECTED_SOURCES.items():
        path = report / record["path"]
        if not path.is_file() or _sha256_file(path) != record["sha256"]:
            raise C0ContractHold(HOLD_SOURCES, f"source hash mismatch for {role}")
        loaded[role] = _load_json_file(path, HOLD_SOURCES) if path.suffix == ".json" else {}
    return loaded


def _axis_bounds(rows: dict[str, Any], label: str, axis: str) -> tuple[float, float]:
    try:
        record = rows[label][axis]
        return (
            float.fromhex(record["lower_binary64_hex"]),
            float.fromhex(record["upper_binary64_hex"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise C0ContractHold(HOLD_MESH, f"invalid {label} {axis} bounds") from error


def verify_contract_bytes(payload: bytes, *, report: Path = REPORT) -> dict[str, Any]:
    contract = _parse(payload)
    if set(contract) != EXPECTED_TOP_KEYS:
        raise C0ContractHold(HOLD_SCHEMA, "top-level key set mismatch")
    _require_exact(
        contract.get("schema"),
        "encounter_continuum_c0_model_contract_candidate_v1",
        HOLD_SCHEMA,
        "schema",
    )
    _require_exact(
        contract.get("status"),
        "HOLD_C0_CANDIDATE_RESULT_BLIND_PENDING_INDEPENDENT_THEORY_AND_HASH_AUDIT",
        HOLD_SCHEMA,
        "status",
    )
    _require_exact(contract.get("physical_dimension"), 2, HOLD_SCHEMA, "physical dimension")
    _require_exact(contract.get("quotient_dimension"), 3, HOLD_SCHEMA, "quotient dimension")
    _require_exact(contract.get("claim_boundary"), EXPECTED_CLAIMS, HOLD_CLAIMS, "claims")
    exact = _validate_parameters(contract.get("physical_parameters"))
    _require_exact(contract.get("continuum_object"), EXPECTED_CONTINUUM, HOLD_CONTINUUM, "continuum")
    _require_exact(contract.get("boundary_conditions"), EXPECTED_BOUNDARY, HOLD_BOUNDARY, "boundary")
    _require_exact(contract.get("equation_contract"), EXPECTED_EQUATIONS, HOLD_EQUATIONS, "equations")
    _require_exact(
        contract.get("finite_volume_identification"),
        EXPECTED_IDENTIFICATION,
        HOLD_IDENTIFICATION,
        "identification maps",
    )
    sources = _validate_sources(contract, report)
    _require_exact(contract.get("control_contract"), EXPECTED_CONTROL, HOLD_CONTROL, "control")
    control_path = report / EXPECTED_CONTROL["opaque_result_blind_source_path"]
    if not control_path.is_file() or _sha256_file(control_path) != EXPECTED_CONTROL[
        "opaque_result_blind_source_sha256"
    ]:
        raise C0ContractHold(HOLD_CONTROL, "opaque control source hash mismatch")
    _require_exact(contract.get("initial_law"), EXPECTED_INITIAL, HOLD_INITIAL, "initial law")
    initial = sources["initial_source"]
    if (
        initial.get("analytic_total_mass_exact") != "1/1"
        or initial.get("physical_dimension") != 2
        or initial.get("quotient_dimension") != 3
        or initial.get("scope") != "physical_initial_law_only_no_control_no_budget"
    ):
        raise C0ContractHold(HOLD_INITIAL, "initial source semantics mismatch")
    _require_exact(contract.get("killing_field"), EXPECTED_KILLING, HOLD_KILLING, "killing")
    killing = sources["killing_geometry_source"]
    try:
        killing_radius = Fraction(killing.get("contact_geometry", {}).get("radius_exact"))
        killing_period = Fraction(
            killing.get("contact_geometry", {}).get("transverse_period_exact")
        )
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise C0ContractHold(HOLD_KILLING, "invalid exact killing geometry") from error
    if (
        killing.get("physical_dimension") != 2
        or killing.get("quotient_dimension") != 3
        or killing.get("support_basis", {}).get("profile_count") != 4
        or killing.get("support_basis", {}).get("analytic_integral_each") != "1/1"
        or killing_radius != exact["contact_radius_a"]
        or killing_period != exact["W"]
    ):
        raise C0ContractHold(HOLD_KILLING, "killing source semantics mismatch")
    killing_flags = killing.get("flags", {})
    if any(
        killing_flags.get(key) is not False
        for key in ("contains_budget_value", "contains_control_values", "positive_budget_executed")
    ):
        raise C0ContractHold(HOLD_KILLING, "killing source crossed result-blind boundary")
    _require_exact(contract.get("mesh_contract"), EXPECTED_MESH, HOLD_MESH, "mesh")
    family = sources["configuration_family"]
    if (
        family.get("configuration_count") != 12
        or family.get("configuration_order") != EXPECTED_MESH["configuration_order"]
        or set(family.get("axis_construction_contracts", {}))
        != set(EXPECTED_MESH["alignment_classes"])
    ):
        raise C0ContractHold(HOLD_MESH, "configuration family mismatch")
    rows = {row.get("label"): row for row in family.get("configurations", [])}
    base_m = _axis_bounds(rows, "O129/Base", "midpoint")
    plus_m = _axis_bounds(rows, "M+", "midpoint")
    base_r = _axis_bounds(rows, "O129/Base", "relative_parallel")
    plus_r = _axis_bounds(rows, "R+", "relative_parallel")
    if not (
        plus_m[0] <= base_m[0] < base_m[1] <= plus_m[1]
        and plus_r[0] <= base_r[0] < base_r[1] <= plus_r[1]
        and _axis_bounds(rows, "MR+", "midpoint") == plus_m
        and _axis_bounds(rows, "MR+", "relative_parallel") == plus_r
        and _axis_bounds(rows, "MR+F", "midpoint") == plus_m
        and _axis_bounds(rows, "MR+F", "relative_parallel") == plus_r
    ):
        raise C0ContractHold(HOLD_MESH, "box nesting mismatch")
    lowered = payload.lower()
    for forbidden in (b"peak_time", b"root_interval", b"positive_budget_result", b"basin_mass"):
        if forbidden in lowered:
            raise C0ContractHold(HOLD_CLAIMS, f"result-bearing token present: {forbidden!r}")
    return {
        "contract_sha256": _sha256_bytes(payload),
        "positive_budget_scientific_values_read": False,
        "release_eligible": False,
        "source_sha256s": {role: record["sha256"] for role, record in EXPECTED_SOURCES.items()},
        "status": PASS_STATUS,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: validate_continuum_c0_model_contract_candidate.py [contract.json]", file=sys.stderr)
        return 2
    path = DEFAULT_CONTRACT if not args else Path(args[0])
    try:
        receipt = verify_contract_bytes(path.read_bytes())
    except (OSError, C0ContractHold) as error:
        code = error.code if isinstance(error, C0ContractHold) else HOLD_ENCODING
        print(json.dumps({"status": code}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
