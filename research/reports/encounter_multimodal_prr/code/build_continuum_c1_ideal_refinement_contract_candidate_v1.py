#!/usr/bin/env python3
"""Build the result-blind C1 ideal refinement/rate contract candidate v1.

Only the three explicitly pinned theorem/geometry/mathematics sources are
opened.  Current finite configurations are copied only as alignment anchors;
they are never promoted to an ``h -> 0`` family.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import build_continuum_c0_model_contract_candidate_v2 as c0
from continuum_c1_ideal_refinement_contract_v1_note_pin import (
    THEOREM_NOTE_RELATIVE,
    THEOREM_NOTE_SHA256,
)

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = (
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

SCHEMA = "encounter_continuum_c1_ideal_refinement_contract_candidate_v1"
STATUS = (
    "HOLD_C1_IDEAL_REFINEMENT_RATE_CONTRACT_CANDIDATE_"
    "FINITE_ANCHORS_ONLY_PRODUCTION_C1_C2_RELEASE_FALSE"
)
PASS_STATUS = (
    "PASS_C1_IDEAL_REFINEMENT_RATE_CONTRACT_REPRODUCIBLE_"
    "BUILD_COMPLETE_C1_FALSE"
)

FROZEN_SOURCES = {
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
    FROZEN_SOURCES[role]["path"] for role in sorted(FROZEN_SOURCES)
]
OPENED_SOURCE_COUNTS = {path: 1 for path in OPENED_SOURCE_PATHS}

CLAIM_BOUNDARY = {
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

SOURCE_POLICY = {
    "allowed_opened_source_roles": sorted(FROZEN_SOURCES),
    "embedded_paths_followed": False,
    "network_access_used": False,
    "positive_budget_scientific_values_read": False,
    "result_or_control_payload_opened": False,
    "scratch_payload_opened": False,
}

FIXED_BOX = {
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

BERNOULLI_AND_OU_RATE = {
    "Bernoulli_function": "B(theta)=theta/(exp(theta)-1), B(0)=1",
    "common_conductance": (
        "c_(i+1/2)=m_i*q_(i,i+1)=m_(i+1)*q_(i+1,i)="
        "g_h*d*exp(-Phi(x_i))*B(Phi_(i+1)-Phi_i)/h"
    ),
    "forward_rate": "q_(i,i+1)=d/(nu_i*h)*B(Phi_(i+1)-Phi_i)",
    "reverse_rate": "q_(i+1,i)=d/(nu_(i+1)*h)*B(Phi_i-Phi_(i+1))",
}

IDEAL_REFINEMENT_SEQUENCES = {
    "axis_families": {
        "cell_centred_periodic_base": {
            "N_constraint": "integer N>=3 with N->infinity",
            "cell_formula": (
                "C_i=[i*h+sigma_h,(i+1)*h+sigma_h) mod W, "
                "represented by two segments if it crosses the seam"
            ),
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
            "cell_formula": (
                "C_i=[i*h+sigma_h,(i+1)*h+sigma_h) mod W, "
                "represented by two segments if it crosses the seam"
            ),
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
            "mass": {
                "axis_gauge": "g_h=integral_I_pi_dx/sum_i_tilde_m_i",
                "gauged": "m_i=g_h*tilde_m_i",
                "raw": "tilde_m_i=nu_i*exp(-Phi(x_i))",
            },
            "positions": "x_i=ell+(i+1/2)*h",
            "rate_contract": BERNOULLI_AND_OU_RATE,
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
            "mass": {
                "axis_gauge": "g_h=integral_I_pi_dx/sum_i_tilde_m_i",
                "gauged": "m_i=g_h*tilde_m_i",
                "raw": "tilde_m_i=nu_i*exp(-Phi(x_i))",
            },
            "positions": "x_i=ell+i*h",
            "rate_contract": BERNOULLI_AND_OU_RATE,
            "source_alignment": "vertex_centred_reflecting_dual",
            "source_size_relation": "size=N+1",
            "volumes": "nu_0=nu_N=h/2 and nu_i=h for 1<=i<=N-1",
        },
    },
    "every_axis_interval_count_tends_to_infinity": True,
    "fixed_box_and_physical_parameters_across_sequence": True,
    "sequence_index": "n",
}

TENSOR_MASS_AND_RATE_CONTRACT = {
    "axis_mass_product": "m_ijk=m_i^z*m_j^r*m_k^y",
    "edge_conductance": (
        "an edge parallel to one axis has that axis common conductance "
        "times the masses of the other two axes"
    ),
    "free_generator": "Q_h^0=Q_z tensor I tensor I + I tensor Q_r tensor I + I tensor I tensor Q_y",
    "global_box_gauge": {
        "box_mass": "M_L=integral_Omega_L_pi_dx=M_z*M_r",
        "factorization": "g_(h,L)=g_h^z*g_h^r/W",
        "gauged_mass": "pi_h_ijk=g_(h,L)*tilde_m_ijk",
        "mass_identity": "sum_ijk_pi_h_ijk=M_L",
        "scale": "g_(h,L)=M_L/sum_ijk_tilde_m_ijk",
    },
    "ideal_only_not_production_centres": True,
    "raw_tensor_mass": (
        "tilde_m_ijk=nu_i^z*nu_j^r*h_y*"
        "exp(-Phi_z(x_i)-Phi_r(x_j))"
    ),
}

MAP_RATE_CONTRACT = {
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

KILLING_AVERAGE_CONTRACT = {
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

PROOF_BRIDGE_BOUNDARY = {
    "bounded_killing_perturbation": "proof_candidate_needs_free_tensor_Mosco_acceptance",
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


class BuildHold(RuntimeError):
    """Fail-closed C1 contract producer error."""


def _read_and_validate_sources(
    *, report: Path = REPORT
) -> tuple[dict[str, Any], dict[str, Any]]:
    note = c0.read_relative_snapshot(report, THEOREM_NOTE_RELATIVE)
    if c0.sha256_bytes(note) != THEOREM_NOTE_SHA256:
        raise BuildHold("theorem note hash mismatch")

    loaded: dict[str, dict[str, Any]] = {}
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
        payload = c0.read_relative_snapshot(report, relative)
        if c0.sha256_bytes(payload) != expected_hash:
            raise BuildHold(f"{role} hash mismatch")
        decoded = c0.parse_source_json(payload)
        c0._scan_result_bearing(decoded)
        if payload != c0.canonical_json_bytes(decoded):
            raise BuildHold(f"{role} is not canonical JSON")
        loaded[role] = decoded

    mathematics = loaded["mathematical_source"]
    family = loaded["configuration_family"]
    if mathematics.get("schema") != "encounter_continuum_c0_mathematical_source_v2":
        raise BuildHold("mathematical source schema mismatch")
    if family.get("schema") != "encounter_physical_configuration_family_control_free_v1":
        raise BuildHold("configuration source schema mismatch")
    if family.get("configuration_count") != 12:
        raise BuildHold("configuration source must contain twelve finite anchors")
    if family.get("contains_control_values") is not False:
        raise BuildHold("configuration source is not control-free")
    return mathematics, family


def _anchor_bindings(family: dict[str, Any]) -> dict[str, Any]:
    rows = family.get("configurations")
    order = family.get("configuration_order")
    if type(rows) is not list or type(order) is not list or len(rows) != len(order):
        raise BuildHold("finite anchor rows/order mismatch")
    bindings: list[dict[str, Any]] = []
    alignment_counts = {
        "cell_centred_periodic_base": 0,
        "cell_centred_periodic_half_shift": 0,
        "cell_centred_reflecting": 0,
        "vertex_centred_reflecting_dual": 0,
    }
    for index, (label, row) in enumerate(zip(order, rows, strict=True)):
        if type(row) is not dict or row.get("label") != label:
            raise BuildHold("finite anchor label/order mismatch")
        axes: dict[str, str] = {}
        sizes: dict[str, int] = {}
        for coordinate in (
            "midpoint",
            "relative_parallel",
            "relative_perpendicular",
        ):
            record = row.get(coordinate)
            if type(record) is not dict:
                raise BuildHold("finite anchor axis is not an object")
            alignment = record.get("alignment")
            size = record.get("size")
            if alignment not in alignment_counts or type(size) is not int or size <= 0:
                raise BuildHold("finite anchor alignment or size is invalid")
            alignment_counts[alignment] += 1
            axes[coordinate] = alignment
            sizes[coordinate] = size
        bindings.append(
            {
                "axis_alignments": axes,
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
    if alignment_counts != expected_counts:
        raise BuildHold("finite anchor alignment coverage mismatch")
    return {
        "alignment_counts_across_36_axes": alignment_counts,
        "configuration_count": len(bindings),
        "configuration_order": order,
        "current_rows_are_h_to_zero_sequences": False,
        "each_row_is_one_finite_mesh_anchor": True,
        "refinement_requires_new_fixed_box_sequences": True,
        "rows": bindings,
        "total_state_workload": family.get("total_state_workload"),
    }


def build_payload(*, report: Path = REPORT) -> dict[str, Any]:
    mathematics, family = _read_and_validate_sources(report=report)
    return {
        "claim_boundary": CLAIM_BOUNDARY,
        "finite_anchor_bindings": _anchor_bindings(family),
        "fixed_box": FIXED_BOX,
        "frozen_sources": FROZEN_SOURCES,
        "identification_and_map_rates": {
            "exact_c0_identification_maps": mathematics["identification_maps"],
            "rate_contract": MAP_RATE_CONTRACT,
        },
        "ideal_refinement_sequences": IDEAL_REFINEMENT_SEQUENCES,
        "killing_average_contract": KILLING_AVERAGE_CONTRACT,
        "proof_bridge_boundary": PROOF_BRIDGE_BOUNDARY,
        "schema": SCHEMA,
        "source_policy": SOURCE_POLICY,
        "status": STATUS,
        "tensor_mass_and_rate_contract": TENSOR_MASS_AND_RATE_CONTRACT,
    }


def build_bytes(*, report: Path = REPORT) -> bytes:
    return c0.canonical_json_bytes(build_payload(report=report))


def _receipt(payload: bytes, action: str) -> dict[str, Any]:
    return {
        "action": action,
        "complete_c1": False,
        "contract_sha256": c0.sha256_bytes(payload),
        "finite_anchor_count": 12,
        "opened_source_counts": OPENED_SOURCE_COUNTS,
        "opened_source_paths": OPENED_SOURCE_PATHS,
        "positive_budget_scientific_values_read": False,
        "production_bridge_proved": False,
        "release_eligible": False,
        "result_or_control_payload_read": False,
        "status": PASS_STATUS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--create", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    action = "create" if args.create else "check"
    try:
        expected = build_bytes()
        if args.create:
            if OUTPUT.exists() or OUTPUT.is_symlink():
                raise BuildHold("C1-v1 output exists; never overwrite, use --check")
            c0._exclusive_publish(OUTPUT, expected)
        observed = c0.read_regular_snapshot(OUTPUT)
        if observed != expected:
            raise BuildHold("published C1-v1 bytes differ from deterministic build")
    except (BuildHold, c0.BuildHold, FileExistsError, OSError) as error:
        print(
            json.dumps(
                {"status": "HOLD_C1_IDEAL_REFINEMENT_BUILD", "message": str(error)},
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(_receipt(observed, action), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
