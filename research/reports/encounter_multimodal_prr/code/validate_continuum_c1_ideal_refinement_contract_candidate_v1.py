#!/usr/bin/env python3
"""Standalone semantic verifier for the C1 ideal refinement contract v1."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import validate_continuum_c0_model_contract_candidate_v2 as c0
from continuum_c1_ideal_refinement_contract_v1_note_pin import (
    THEOREM_NOTE_RELATIVE,
    THEOREM_NOTE_SHA256,
)

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_CONTRACT = (
    REPORT
    / "artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json"
)
MATHEMATICAL_SOURCE_RELATIVE = Path(
    "artifacts/data/continuum_c0_mathematical_source_v2.json"
)
MATHEMATICAL_SOURCE_SHA256 = (
    "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559"
)
CONFIGURATION_SOURCE_RELATIVE = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
CONFIGURATION_SOURCE_SHA256 = (
    "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
)
EXPECTED_CONTRACT_SHA256 = (
    "93b13d8c6864c54896ff2d71d143856554d8e2de94acd8ba4f43cc3a2534987b"
)

SCHEMA = "encounter_continuum_c1_ideal_refinement_contract_candidate_v1"
STATUS = (
    "HOLD_C1_IDEAL_REFINEMENT_RATE_CONTRACT_CANDIDATE_"
    "FINITE_ANCHORS_ONLY_PRODUCTION_C1_C2_RELEASE_FALSE"
)
PASS_STATUS = (
    "PASS_C1_IDEAL_REFINEMENT_RATE_CONTRACT_SEMANTIC_"
    "VERIFICATION_COMPLETE_C1_FALSE"
)

HOLD_ENCODING = "HOLD_C1_REFINEMENT_V1_ENCODING"
HOLD_SCHEMA = "HOLD_C1_REFINEMENT_V1_SCHEMA"
HOLD_SOURCES = "HOLD_C1_REFINEMENT_V1_SOURCES"
HOLD_CLAIMS = "HOLD_C1_REFINEMENT_V1_CLAIMS"
HOLD_REFINEMENT = "HOLD_C1_REFINEMENT_V1_SEQUENCE"
HOLD_RATES = "HOLD_C1_REFINEMENT_V1_RATES"
HOLD_ANCHORS = "HOLD_C1_REFINEMENT_V1_ANCHORS"
HOLD_MAPS = "HOLD_C1_REFINEMENT_V1_MAPS"
HOLD_TENSOR = "HOLD_C1_REFINEMENT_V1_TENSOR"
HOLD_KILLING = "HOLD_C1_REFINEMENT_V1_KILLING"
HOLD_PROOF = "HOLD_C1_REFINEMENT_V1_PROOF_BOUNDARY"
HOLD_RESULT_BLINDNESS = "HOLD_C1_REFINEMENT_V1_RESULT_BLINDNESS"

EXPECTED_TOP_KEYS = {
    "claim_boundary",
    "finite_anchor_bindings",
    "fixed_box",
    "frozen_sources",
    "identification_and_map_rates",
    "ideal_refinement_sequences",
    "killing_average_contract",
    "proof_bridge_boundary",
    "schema",
    "source_policy",
    "status",
    "tensor_mass_and_rate_contract",
}

EXPECTED_FROZEN_SOURCES = {
    "configuration_family": {
        "path": str(CONFIGURATION_SOURCE_RELATIVE),
        "sha256": CONFIGURATION_SOURCE_SHA256,
    },
    "mathematical_source": {
        "path": str(MATHEMATICAL_SOURCE_RELATIVE),
        "sha256": MATHEMATICAL_SOURCE_SHA256,
    },
    "theorem_note": {
        "path": str(THEOREM_NOTE_RELATIVE),
        "sha256": THEOREM_NOTE_SHA256,
    },
}
OPENED_SOURCE_PATHS = [
    EXPECTED_FROZEN_SOURCES[role]["path"]
    for role in sorted(EXPECTED_FROZEN_SOURCES)
]
OPENED_SOURCE_COUNTS = {path: 1 for path in OPENED_SOURCE_PATHS}

EXPECTED_CLAIMS = {
    "box_exhaustion_for_r1_r2_complete": False,
    "complete_c0": False,
    "complete_c1": False,
    "complete_c2": False,
    "complete_c3": False,
    "continuum_root_margin_certified": False,
    "control_specific_killing_averages_complete": False,
    "finite_anchor_rows_authorize_h_to_zero": False,
    "f0_complete": False,
    "positive_budget_scientific_values_read": False,
    "production_centre_to_ideal_rate_bridge_proved": False,
    "production_gauge_application_complete": False,
    "production_raw_to_gauged_bridge_proved": False,
    "quantitative_cut_cell_rate_proved": False,
    "release_eligible": False,
    "submission_eligible": False,
    "theorem_note_independently_accepted": False,
}

EXPECTED_SOURCE_POLICY = {
    "allowed_opened_source_roles": sorted(EXPECTED_FROZEN_SOURCES),
    "embedded_paths_followed": False,
    "network_access_used": False,
    "positive_budget_scientific_values_read": False,
    "result_or_control_payload_opened": False,
    "scratch_payload_opened": False,
}

EXPECTED_OU_RATE = {
    "Bernoulli_function": "B(theta)=theta/(exp(theta)-1), B(0)=1",
    "common_conductance": (
        "c_(i+1/2)=m_i*q_(i,i+1)=m_(i+1)*q_(i+1,i)="
        "g_h*d*exp(-Phi(x_i))*B(Phi_(i+1)-Phi_i)/h"
    ),
    "forward_rate": "q_(i,i+1)=d/(nu_i*h)*B(Phi_(i+1)-Phi_i)",
    "reverse_rate": "q_(i+1,i)=d/(nu_(i+1)*h)*B(Phi_i-Phi_(i+1))",
}

EXPECTED_FIXED_BOX = {
    "domain": "Omega_L=I_z*x*I_r*x*T_W",
    "fixed_across_each_refinement_sequence": True,
    "maximum_axis_spacing_limit": "max(h_z,h_r,h_y)->0",
    "parameter_preconditions": {
        "D": "D>0",
        "W": "W>0",
        "gamma": "gamma>0",
        "midpoint_density_normalizer": "C_z>0",
        "midpoint_interval_nondegenerate": "ell_z<r_z",
        "midpoint_mean": "zbar in interior(I_z)",
        "relative_parallel_density_normalizer": "C_r>0",
        "relative_parallel_interval_nondegenerate": "ell_r<r_r",
        "relative_parallel_mean": "0 in interior(I_r)",
    },
    "reference_density": (
        "pi(z,r,y)=pi_z(z)*pi_r(r)/W with "
        "pi_a(x)=C_a*exp(-Phi_a(x))"
    ),
    "substitution": {
        "midpoint": {
            "diffusion": "d_z=D/2",
            "mean": "mu_z=zbar",
            "potential": "Phi_z=gamma*(z-zbar)^2/(2*d_z)",
        },
        "relative_parallel": {
            "diffusion": "d_r=2*D",
            "mean": "mu_r=0",
            "potential": "Phi_r=gamma*r^2/(2*d_r)",
        },
        "relative_perpendicular": {
            "diffusion": "d_y=2*D",
            "potential": "Phi_y=0",
        },
    },
}

EXPECTED_OU_MASS = {
    "axis_gauge": "g_h=integral_I_pi_dx/sum_i_tilde_m_i",
    "gauged": "m_i=g_h*tilde_m_i",
    "raw": "tilde_m_i=nu_i*exp(-Phi(x_i))",
}
EXPECTED_PERIODIC_CELL_FORMULA = (
    "C_i=[i*h+sigma_h,(i+1)*h+sigma_h) mod W, "
    "represented by two segments if it crosses the seam"
)
EXPECTED_AXIS_FAMILIES = {
    "cell_centred_periodic_base": {
        "N_constraint": "integer N>=3 with N->infinity",
        "cell_formula": EXPECTED_PERIODIC_CELL_FORMULA,
        "cell_mass": "m_i=h/W",
        "graph": "cycle_on_N_cells_with_exactly_one_wrapping_edge_(N-1,0)",
        "h": "W/N",
        "positions": "y_i=(i+1/2)*h+sigma_h mod W",
        "rates": "q_(i,i+1)=q_(i,i-1)=d_y/h^2 and q_ii=-2*d_y/h^2",
        "shift": "sigma_h=0",
        "source_alignment": "cell_centred_periodic_base",
    },
    "cell_centred_periodic_half_shift": {
        "N_constraint": "integer N>=3 with N->infinity",
        "cell_formula": EXPECTED_PERIODIC_CELL_FORMULA,
        "cell_mass": "m_i=h/W",
        "graph": "cycle_on_N_cells_with_exactly_one_wrapping_edge_(N-1,0)",
        "h": "W/N",
        "positions": "y_i=(i+1/2)*h+sigma_h mod W",
        "rates": "q_(i,i+1)=q_(i,i-1)=d_y/h^2 and q_ii=-2*d_y/h^2",
        "shift": "sigma_h=h/2",
        "source_alignment": "cell_centred_periodic_half_shift",
    },
    "cell_centred_reflecting_ou": {
        "N_constraint": "integer N>=3 with N->infinity",
        "cell_formula": "C_i=[ell+i*h,ell+(i+1)*h]",
        "exterior_rates": "zero_reflecting",
        "h": "(r-ell)/N",
        "index_set": "i=0,...,N-1",
        "mass": EXPECTED_OU_MASS,
        "positions": "x_i=ell+(i+1/2)*h",
        "rate_contract": EXPECTED_OU_RATE,
        "source_alignment": "cell_centred_reflecting",
        "source_size_relation": "size=N",
        "volumes": "nu_i=h",
    },
    "vertex_centred_reflecting_dual_ou": {
        "N_constraint": "integer N>=2 with N->infinity",
        "cell_formula": (
            "dual cells bounded by ell, adjacent vertex midpoints, and r"
        ),
        "endpoint_rate_factor": (
            "nu_0=nu_N=h/2 makes the endpoint outgoing rate twice the "
            "equal-volume rate with the same Bernoulli factor"
        ),
        "exterior_rates": "zero_reflecting",
        "h": "(r-ell)/N",
        "index_set": "i=0,...,N",
        "mass": EXPECTED_OU_MASS,
        "positions": "x_i=ell+i*h",
        "rate_contract": EXPECTED_OU_RATE,
        "source_alignment": "vertex_centred_reflecting_dual",
        "source_size_relation": "size=N+1",
        "volumes": "nu_0=nu_N=h/2 and nu_i=h for 1<=i<=N-1",
    },
}

AXIS_RATE_FIELDS = {
    "cell_centred_periodic_base": {"cell_mass", "graph", "rates"},
    "cell_centred_periodic_half_shift": {"cell_mass", "graph", "rates"},
    "cell_centred_reflecting_ou": {"mass", "rate_contract", "volumes"},
    "vertex_centred_reflecting_dual_ou": {
        "endpoint_rate_factor",
        "mass",
        "rate_contract",
        "volumes",
    },
}

EXPECTED_MAP_RATES = {
    "axis_rho_orders": {
        "cell_centred_reflecting_ou": "max_i_abs(rho_i-1)=O(h^2)",
        "periodic_base_and_half_shift": "rho_i=1 exactly",
        "vertex_dual_endpoints": {
            "left": "rho_0=1-Phi_prime(ell)*h/4+O(h^2)",
            "right": "rho_N=1+Phi_prime(r)*h/4+O(h^2)",
        },
        "vertex_dual_uniform": "max_i_abs(rho_i-1)=O(h)",
    },
    "pointwise_reconstruction": "J_h*P_h*u->u strongly for every fixed u",
    "tensor_ratio": "rho_ijk=rho_i^z*rho_j^r*rho_k^y",
    "uniform_discrete_defect": "delta_h=norm(P_h*J_h-I)=max_ijk_abs(rho_ijk-1)->0",
}

EXPECTED_KILLING = {
    "admissible_field": "one fixed V_c in L_infinity(Omega_L), V_c>=0",
    "cell_average": "V_(h,c,i)=physical_volume(C_i)^(-1)*integral_C_i_V_c_dx",
    "cell_conventions": (
        "actual tensor cells include endpoint dual half volumes and wrapped "
        "periodic segments"
    ),
    "killing_form": "sum_i_pi_h_i*V_(h,c,i)*abs(v_i)^2",
    "qualitative_consistency": (
        "J_h*V_(h,c)->V_c in weighted L2 and 0<=J_h*V_(h,c)<=norm(V_c)_infinity"
    ),
    "reconstructed_multiplier": "K_h_pc_on_C_i=V_(h,c,i)/rho_i",
    "weighted_pi_average_used": False,
}

EXPECTED_PROOF_BOUNDARY = {
    "bounded_killing_perturbation": (
        "proof_candidate_needs_free_tensor_Mosco_acceptance"
    ),
    "free_tensor_route": "direct_reconstructed_strong_resolvent_candidate",
    "functional_calculus": (
        "for f in C_0([0,infinity)), reconstructed f(L_h) converges strongly "
        "assuming exact adjointness, bounded maps, delta_h->0, and one "
        "reconstructed resolvent limit"
    ),
    "positive_time_pairing": (
        "qualitative uniform convergence on t in [tau,T], tau>0, for "
        "lambda^r*exp(-t*lambda), r=0,1,2"
    ),
    "quantitative_error_bound_supplied": False,
}


class C1RefinementHold(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_exact(observed: Any, expected: Any, code: str, label: str) -> None:
    if observed != expected or type(observed) is not type(expected):
        raise C1RefinementHold(code, f"{label} mismatch")


def _parse(payload: bytes) -> dict[str, Any]:
    try:
        return c0._parse_json(payload, code=HOLD_ENCODING, canonical=True)
    except c0.C0V2Hold as error:
        raise C1RefinementHold(HOLD_ENCODING, str(error)) from error


def _read_relative(report: Path, relative: Path, code: str) -> bytes:
    try:
        return c0.read_relative_snapshot(report, relative, code=code)
    except c0.C0V2Hold as error:
        raise C1RefinementHold(code, str(error)) from error


def _load_sources(report: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    note = _read_relative(report, THEOREM_NOTE_RELATIVE, HOLD_SOURCES)
    if _sha256(note) != THEOREM_NOTE_SHA256:
        raise C1RefinementHold(HOLD_SOURCES, "theorem note hash mismatch")

    decoded: dict[str, dict[str, Any]] = {}
    for role, relative, expected_hash in (
        (
            "mathematical_source",
            MATHEMATICAL_SOURCE_RELATIVE,
            MATHEMATICAL_SOURCE_SHA256,
        ),
        (
            "configuration_family",
            CONFIGURATION_SOURCE_RELATIVE,
            CONFIGURATION_SOURCE_SHA256,
        ),
    ):
        payload = _read_relative(report, relative, HOLD_SOURCES)
        if _sha256(payload) != expected_hash:
            raise C1RefinementHold(HOLD_SOURCES, f"{role} hash mismatch")
        try:
            value = c0._parse_json(payload, code=HOLD_SOURCES, canonical=True)
            c0._scan_result_bearing(value, code=HOLD_RESULT_BLINDNESS)
        except c0.C0V2Hold as error:
            code = (
                HOLD_RESULT_BLINDNESS
                if error.code == HOLD_RESULT_BLINDNESS
                else HOLD_SOURCES
            )
            raise C1RefinementHold(code, str(error)) from error
        decoded[role] = value

    mathematics = decoded["mathematical_source"]
    family = decoded["configuration_family"]
    if mathematics.get("schema") != "encounter_continuum_c0_mathematical_source_v2":
        raise C1RefinementHold(HOLD_SOURCES, "mathematical source schema mismatch")
    if family.get("schema") != "encounter_physical_configuration_family_control_free_v1":
        raise C1RefinementHold(HOLD_SOURCES, "configuration source schema mismatch")
    if family.get("contains_control_values") is not False:
        raise C1RefinementHold(HOLD_RESULT_BLINDNESS, "configuration source has controls")
    return mathematics, family


def _expected_anchor_bindings(family: dict[str, Any]) -> dict[str, Any]:
    rows = family.get("configurations")
    order = family.get("configuration_order")
    if type(rows) is not list or type(order) is not list or len(rows) != 12:
        raise C1RefinementHold(HOLD_ANCHORS, "configuration source row count mismatch")
    if len(rows) != len(order):
        raise C1RefinementHold(HOLD_ANCHORS, "configuration order length mismatch")

    counts = {
        "cell_centred_periodic_base": 0,
        "cell_centred_periodic_half_shift": 0,
        "cell_centred_reflecting": 0,
        "vertex_centred_reflecting_dual": 0,
    }
    bindings: list[dict[str, Any]] = []
    for index, (label, row) in enumerate(zip(order, rows, strict=True)):
        if type(row) is not dict or row.get("label") != label:
            raise C1RefinementHold(HOLD_ANCHORS, "source label/order mismatch")
        alignments: dict[str, str] = {}
        sizes: dict[str, int] = {}
        for coordinate in (
            "midpoint",
            "relative_parallel",
            "relative_perpendicular",
        ):
            record = row.get(coordinate)
            if type(record) is not dict:
                raise C1RefinementHold(HOLD_ANCHORS, "source axis is not an object")
            alignment = record.get("alignment")
            size = record.get("size")
            if alignment not in counts or type(size) is not int or size <= 0:
                raise C1RefinementHold(HOLD_ANCHORS, "source alignment invalid")
            counts[alignment] += 1
            alignments[coordinate] = alignment
            sizes[coordinate] = size
        bindings.append(
            {
                "axis_alignments": alignments,
                "axis_sizes": sizes,
                "label": label,
                "source_row_index": index,
            }
        )
    expected_counts = {
        "cell_centred_periodic_base": 10,
        "cell_centred_periodic_half_shift": 2,
        "cell_centred_reflecting": 20,
        "vertex_centred_reflecting_dual": 4,
    }
    if counts != expected_counts:
        raise C1RefinementHold(HOLD_ANCHORS, "source alignment counts mismatch")
    return {
        "alignment_counts_across_36_axes": counts,
        "configuration_count": 12,
        "configuration_order": order,
        "current_rows_are_h_to_zero_sequences": False,
        "each_row_is_one_finite_mesh_anchor": True,
        "refinement_requires_new_fixed_box_sequences": True,
        "rows": bindings,
        "total_state_workload": family.get("total_state_workload"),
    }


def _verify_refinement(contract: dict[str, Any]) -> None:
    fixed = contract.get("fixed_box")
    _require_exact(
        fixed,
        EXPECTED_FIXED_BOX,
        HOLD_REFINEMENT,
        "fixed-box parameters, intervals, normalizers, and axis substitution",
    )

    sequences = contract.get("ideal_refinement_sequences")
    if type(sequences) is not dict or set(sequences) != {
        "axis_families",
        "every_axis_interval_count_tends_to_infinity",
        "fixed_box_and_physical_parameters_across_sequence",
        "sequence_index",
    }:
        raise C1RefinementHold(HOLD_REFINEMENT, "sequence schema mismatch")
    _require_exact(
        sequences.get("every_axis_interval_count_tends_to_infinity"),
        True,
        HOLD_REFINEMENT,
        "axis refinement limit",
    )
    _require_exact(
        sequences.get("fixed_box_and_physical_parameters_across_sequence"),
        True,
        HOLD_REFINEMENT,
        "fixed sequence data",
    )
    _require_exact(
        sequences.get("sequence_index"),
        "n",
        HOLD_REFINEMENT,
        "sequence index",
    )
    families = sequences.get("axis_families")
    if type(families) is not dict or set(families) != set(EXPECTED_AXIS_FAMILIES):
        raise C1RefinementHold(HOLD_REFINEMENT, "axis family set mismatch")
    for family_name, expected_family in EXPECTED_AXIS_FAMILIES.items():
        observed_family = families[family_name]
        if type(observed_family) is not dict or set(observed_family) != set(
            expected_family
        ):
            raise C1RefinementHold(
                HOLD_REFINEMENT,
                f"{family_name} field set mismatch",
            )
        for field, expected_value in expected_family.items():
            code = (
                HOLD_RATES
                if field in AXIS_RATE_FIELDS[family_name]
                else HOLD_REFINEMENT
            )
            _require_exact(
                observed_family.get(field),
                expected_value,
                code,
                f"{family_name} {field}",
            )


def _verify_tensor(contract: dict[str, Any]) -> None:
    tensor = contract.get("tensor_mass_and_rate_contract")
    if type(tensor) is not dict:
        raise C1RefinementHold(HOLD_TENSOR, "tensor contract missing")
    expected = {
        "axis_mass_product": "m_ijk=m_i^z*m_j^r*m_k^y",
        "edge_conductance": (
            "an edge parallel to one axis has that axis common conductance "
            "times the masses of the other two axes"
        ),
        "free_generator": "Q_h^0=Q_z tensor I tensor I + I tensor Q_r tensor I + I tensor I tensor Q_y",
        "ideal_only_not_production_centres": True,
        "raw_tensor_mass": (
            "tilde_m_ijk=nu_i^z*nu_j^r*h_y*"
            "exp(-Phi_z(x_i)-Phi_r(x_j))"
        ),
    }
    if set(tensor) != {*expected, "global_box_gauge"}:
        raise C1RefinementHold(HOLD_TENSOR, "tensor field set mismatch")
    for field, value in expected.items():
        _require_exact(tensor.get(field), value, HOLD_TENSOR, field)
    gauge = tensor.get("global_box_gauge")
    expected_gauge = {
        "box_mass": "M_L=integral_Omega_L_pi_dx=M_z*M_r",
        "factorization": "g_(h,L)=g_h^z*g_h^r/W",
        "gauged_mass": "pi_h_ijk=g_(h,L)*tilde_m_ijk",
        "mass_identity": "sum_ijk_pi_h_ijk=M_L",
        "scale": "g_(h,L)=M_L/sum_ijk_tilde_m_ijk",
    }
    _require_exact(gauge, expected_gauge, HOLD_TENSOR, "global tensor gauge")


def _verify_maps(
    contract: dict[str, Any], mathematical_source: dict[str, Any]
) -> None:
    section = contract.get("identification_and_map_rates")
    if type(section) is not dict or set(section) != {
        "exact_c0_identification_maps",
        "rate_contract",
    }:
        raise C1RefinementHold(HOLD_MAPS, "identification section schema mismatch")
    _require_exact(
        section.get("exact_c0_identification_maps"),
        mathematical_source.get("identification_maps"),
        HOLD_MAPS,
        "C0 identification maps",
    )
    _require_exact(section.get("rate_contract"), EXPECTED_MAP_RATES, HOLD_MAPS, "map rates")
    identities = section["exact_c0_identification_maps"].get("exact_identities")
    required_identities = {
        "A_h_J_h": "I",
        "J_h_A_h": "E_h_pi_weighted_cell_conditional_expectation",
        "J_h_P_h": "rho_h_pc*E_h",
        "P_h": "J_h_adjoint",
        "P_h_J_h": "diag(rho_i)",
        "P_h_relation_to_A_h": "P_h=diag(rho_i)*A_h",
    }
    _require_exact(identities, required_identities, HOLD_MAPS, "map algebra")


def _verify_proof_boundary(contract: dict[str, Any]) -> None:
    proof = contract.get("proof_bridge_boundary")
    _require_exact(
        proof,
        EXPECTED_PROOF_BOUNDARY,
        HOLD_PROOF,
        "functional-calculus and positive-time proof boundary",
    )


def verify_contract_bytes(
    payload: bytes, *, report: Path = REPORT
) -> dict[str, Any]:
    contract = _parse(payload)
    try:
        c0._scan_result_bearing(contract, code=HOLD_RESULT_BLINDNESS)
    except c0.C0V2Hold as error:
        raise C1RefinementHold(HOLD_RESULT_BLINDNESS, str(error)) from error
    if set(contract) != EXPECTED_TOP_KEYS:
        raise C1RefinementHold(HOLD_SCHEMA, "top-level key set mismatch")
    _require_exact(contract.get("schema"), SCHEMA, HOLD_SCHEMA, "schema")
    _require_exact(contract.get("status"), STATUS, HOLD_SCHEMA, "status")
    _require_exact(
        contract.get("frozen_sources"),
        EXPECTED_FROZEN_SOURCES,
        HOLD_SOURCES,
        "frozen sources",
    )
    _require_exact(contract.get("source_policy"), EXPECTED_SOURCE_POLICY, HOLD_CLAIMS, "source policy")
    _require_exact(contract.get("claim_boundary"), EXPECTED_CLAIMS, HOLD_CLAIMS, "claim boundary")

    mathematics, family = _load_sources(report)
    _require_exact(
        contract.get("finite_anchor_bindings"),
        _expected_anchor_bindings(family),
        HOLD_ANCHORS,
        "finite anchor bindings",
    )
    _verify_refinement(contract)
    _verify_tensor(contract)
    _verify_maps(contract, mathematics)
    _require_exact(
        contract.get("killing_average_contract"),
        EXPECTED_KILLING,
        HOLD_KILLING,
        "physical-volume killing averages",
    )
    _verify_proof_boundary(contract)

    if _sha256(payload) != EXPECTED_CONTRACT_SHA256:
        raise C1RefinementHold(HOLD_SCHEMA, "candidate byte hash mismatch")
    return {
        "complete_c1": False,
        "contract_sha256": _sha256(payload),
        "finite_anchor_count": 12,
        "finite_anchors_are_refinement_sequences": False,
        "opened_source_counts": OPENED_SOURCE_COUNTS,
        "opened_source_paths": OPENED_SOURCE_PATHS,
        "positive_budget_scientific_values_read": False,
        "production_bridge_proved": False,
        "release_eligible": False,
        "result_or_control_payload_read": False,
        "status": PASS_STATUS,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print(
            "usage: validate_continuum_c1_ideal_refinement_contract_candidate_v1.py "
            "[contract.json]",
            file=sys.stderr,
        )
        return 2
    path = DEFAULT_CONTRACT if not args else Path(args[0])
    try:
        payload = c0.read_regular_snapshot(path, code=HOLD_ENCODING)
        receipt = verify_contract_bytes(payload)
    except (C1RefinementHold, c0.C0V2Hold) as error:
        code = error.code if hasattr(error, "code") else HOLD_ENCODING
        print(json.dumps({"status": code, "message": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
