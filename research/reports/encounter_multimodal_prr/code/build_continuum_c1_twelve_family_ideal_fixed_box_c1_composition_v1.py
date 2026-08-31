#!/usr/bin/env python3
"""Build the source-bound twelve-family ideal fixed-box C1 composition.

The builder authenticates the theorem/audit chain, reconstructs the exact
support and interior facts needed by the composition, and emits a canonical
string contract.  It does not import project modules, evaluate theorem
constants, construct a production member, or read result-bearing payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

SELF = Path(__file__).resolve()
REPORT = SELF.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json"

SCHEMA = "encounter_continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1"
STATUS = (
    "IDEAL_FIXED_BOX_C1_COMPOSITION_CLOSED_AT_THEOREM_LAYER_"
    "EXISTENCE_CONSTANT_HALF_ORDER_ONLY_"
    "PROJECT_PRODUCTION_COMPLETE_C1_FALSE_COMPUTABLE_C2_FALSE"
)

SOURCES: dict[str, tuple[str, str]] = {
    "round4_note": (
        "notes/continuum_c1_free_form_and_functional_bridge_candidate.md",
        "17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562",
    ),
    "round4_audit": (
        "audits/continuum_c1_refinement_functional_bridge_round4_20260717.md",
        "6ccdcd76a4049e198d13ae45d86570c17d7876a4ef28de8fb3fed0ea1b513134",
    ),
    "round5_note": (
        "notes/continuum_c1_varying_space_resolvent_mosco_candidate.md",
        "0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1",
    ),
    "round5_audit": (
        "audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md",
        "9e1cacca6c9c40675f31acbe743bbeccc74aca29b6378a641e1613ae48e55287",
    ),
    "genuine_refinement_note": (
        "notes/continuum_c1_genuine_joint_refinement_family_v2.md",
        "c312ca42d57af451ffef30c69aed7275ba8d9065eb4d1ae80f8439bd2320a142",
    ),
    "genuine_refinement_artifact": (
        "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9",
    ),
    "round172_audit": (
        "audits/round_172_genuine_joint_refinement_family_v2.md",
        "90415181c06e94e6dd451b3c9c2a8abb32c4127cc0703976b003e26afd10cad0",
    ),
    "source_bound_note": (
        "notes/continuum_c2_source_bound_map_cut_killing_lemma_v1.md",
        "09c84f471e4d0b3b4e927e5c99a12999827b7e060bcc7ce02122a4107d8460ed",
    ),
    "source_bound_artifact": (
        "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json",
        "f977939e97651e1d45d83bc4d80acd3d19e6fac7d4ae90c2803090c25cfa9ee3",
    ),
    "round173_audit": (
        "audits/round_173_source_bound_map_cut_killing_lemma.md",
        "4aacbe7a55a328fc8d5c5f10b9891839b790a953c97a9e495bcb68649a30c7ce",
    ),
    "round10_note": (
        "notes/continuum_c2_one_sided_free_sg_residual_candidate.md",
        "ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4",
    ),
    "round10_audit": (
        "audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md",
        "c00351acc5ff3be67cbb579ccab768e8e226bd29bc730f5d9acb15c5dcc3163d",
    ),
    "round11_note": (
        "notes/continuum_c2_mixed_neumann_periodic_sector_h2_candidate.md",
        "4339385e8489984701aabedbd4ab0a28d69db5b2ffd7e2d1c91d1d4ba63564d9",
    ),
    "round11_audit": (
        "audits/continuum_c2_mixed_neumann_periodic_sector_h2_round11_20260717.md",
        "d3b0aca6203999ba18f08a380847f7253e41fc72272d28f4c4fcde92dbb89a2c",
    ),
    "reference_density": (
        "artifacts/data/continuum_c1_reference_density_source_v1.json",
        "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    ),
    "ideal_formula": (
        "artifacts/data/continuum_c1_ideal_formula_source_v1.json",
        "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    ),
    "factorization": (
        "artifacts/data/continuum_c1_factorization_source_v1.json",
        "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
    ),
    "initial_source": (
        "artifacts/data/physical_initial_analytic_source_v1.json",
        "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
    ),
    "round166_initial_audit": (
        "audits/round_166_physical_initial_source_binding_independent_reaudit.md",
        "f4e4ca3c1d903bcba75c2ec55aa53b76ab8ade8ddffe2be0118d135cd3bd56b3",
    ),
    "composition_note": (
        "notes/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.md",
        "13da61f8a41a6d659800595bb73d6ea717530a3c6b33244f0c39703351a80660",
    ),
}

JSON_ROLES = frozenset(
    {
        "factorization",
        "genuine_refinement_artifact",
        "ideal_formula",
        "initial_source",
        "reference_density",
        "source_bound_artifact",
    }
)
RATIONAL_RE = re.compile(r"-?[0-9]+/[1-9][0-9]*")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def descriptor_snapshot(path: Path) -> bytes:
    """Read one stable regular-file snapshot without following a symlink."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("O_NOFOLLOW is required for source snapshots")
    descriptor = os.open(path, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0))
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"regular file required: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        path_state = os.stat(path, follow_symlinks=False)
    finally:
        os.close(descriptor)
    before_signature = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_signature = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if before_signature != after_signature:
        raise ValueError(f"file changed during descriptor snapshot: {path}")
    if (path_state.st_dev, path_state.st_ino) != (after.st_dev, after.st_ino):
        raise ValueError(f"path identity changed during descriptor snapshot: {path}")
    data = b"".join(chunks)
    if len(data) != after.st_size:
        raise ValueError(f"snapshot size mismatch: {path}")
    return data


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def reject_number(token: str) -> None:
    raise ValueError(f"non-integer JSON number forbidden: {token}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(data: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"strict JSON failure for {path}: {exc}") from exc
    if type(value) is not dict:
        raise ValueError(f"top-level object required: {path}")
    return value


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact(value: Any) -> Fraction:
    if type(value) is not str or RATIONAL_RE.fullmatch(value) is None:
        raise ValueError(f"invalid rational: {value!r}")
    numerator, denominator = value.split("/", 1)
    result = Fraction(int(numerator), int(denominator))
    if fraction_text(result) != value:
        raise ValueError(f"unreduced rational: {value}")
    return result


def exact_hex(value: Any) -> Fraction:
    if type(value) is not str:
        raise ValueError(f"hexadecimal binary64 string required: {value!r}")
    number = float.fromhex(value)
    if not number.hex() == value:
        raise ValueError(f"noncanonical binary64 hexadecimal string: {value}")
    return Fraction.from_float(number)


def require_all_false(value: Any, context: str) -> None:
    if type(value) is not dict or not value:
        raise ValueError(f"nonempty false flag map required: {context}")
    if any(flag is not False for flag in value.values()):
        raise ValueError(f"promotion drift in {context}")


def checked_sources() -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    for role, (relative, expected) in SOURCES.items():
        path = REPORT / relative
        data = descriptor_snapshot(path)
        actual = sha256(data)
        if actual != expected:
            raise ValueError(f"source hash drift for {role}: {actual} != {expected}")
        if role in JSON_ROLES:
            parsed[role] = parse_json(data, path)
    return parsed


def validate_source_semantics(sources: dict[str, dict[str, Any]]) -> None:
    family = sources["genuine_refinement_artifact"]
    if (
        family.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2"
        or family.get("sequence_count") != 12
        or len(family.get("sequences", [])) != 12
    ):
        raise ValueError("genuine refinement schema/count drift")
    require_all_false(family.get("claim_boundary"), "genuine refinement")
    if family["established_scope"].get("genuine_refinement_sequences_defined") is not True:
        raise ValueError("genuine refinement sequence authority lost")

    source_bound = sources["source_bound_artifact"]
    if (
        source_bound.get("schema")
        != "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1"
        or source_bound.get("family_scope", {}).get("finite_family_cardinality") != 12
        or source_bound.get("family_scope", {}).get("labels") != family.get("sequence_order")
    ):
        raise ValueError("source-bound family drift")
    require_all_false(source_bound.get("claim_boundary"), "source-bound contract")
    contract = source_bound.get("symbolic_theorem_contract", {})
    if (
        contract.get("map", {}).get("exact_adjoint") != "P_h=J_h_star"
        or contract.get("killing_multiplier", {}).get("definition") != "K_h_pc=V_h_pc/rho_h_pc"
        or contract.get("round9_residual", {}).get("bound")
        != "abs_R_h_kill<=C_kill*h^(1/2)*norm_u_H2*norm_v_h_1h"
    ):
        raise ValueError("source-bound theorem contract drift")

    reference = sources["reference_density"]
    if (
        reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1"
        or reference.get("normalization", {}).get("restricted_density_retains_global_normalization")
        is not True
    ):
        raise ValueError("reference-density semantics drift")
    require_all_false(reference.get("claim_boundary"), "reference density")

    ideal = sources["ideal_formula"]
    if (
        ideal.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1"
        or ideal.get("formulae", {}).get("exact_adjoint_map")
        != "P_h[u]_i=integral_C_i_u*pi_dx/pi_h_i"
        or ideal.get("formulae", {}).get("discrete_killing") != "k=B*V"
    ):
        raise ValueError("ideal-formula semantics drift")
    require_all_false(ideal.get("claim_boundary"), "ideal formula")

    factorization = sources["factorization"]
    if (
        factorization.get("schema") != "encounter_continuum_c1_factorization_source_v1"
        or factorization.get("profile_basis", {}).get("profile_count") != 4
        or factorization.get("coordinate_and_storage", {}).get("periodic_normalization") != "W^-1"
    ):
        raise ValueError("factorization semantics drift")
    require_all_false(factorization.get("claim_boundary"), "factorization")

    initial = sources["initial_source"]
    if (
        initial.get("schema") != "encounter_physical_initial_analytic_source_v1"
        or initial.get("construction")
        != "independent_product_of_three_analytically_normalized_compact_bumps"
        or initial.get("analytic_total_mass_exact") != "1/1"
        or initial.get("shape_definition") != "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))"
        or initial.get("periodic_wrap") != "sum_over_periodic_images_before_cell_integration"
        or initial.get("scope") != "physical_initial_law_only_no_control_no_budget"
    ):
        raise ValueError("initial-source semantics drift")
    if exact(factorization["profile_basis"]["half_width_exact"]) == exact_hex(
        initial["half_width_binary64_hex"]
    ):
        raise ValueError("profile and initial half-width roles were conflated")


def support_and_interior_rows(
    sources: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], Fraction, Fraction]:
    family = sources["genuine_refinement_artifact"]
    initial = sources["initial_source"]
    half_width = exact_hex(initial["half_width_binary64_hex"])
    centres = {key: exact_hex(value) for key, value in initial["starts_binary64_hex"].items()}
    mean = exact_hex(family["physical_parameter_freeze"]["ou_mean_binary64_hex"])
    rows: list[dict[str, Any]] = []
    support_margins: list[Fraction] = []
    mean_margins: list[Fraction] = []

    for sequence in family["sequences"]:
        axes = sequence.get("axes")
        if type(axes) is not list or len(axes) != 3:
            raise ValueError("three-axis sequence required")
        coordinate_order = [axis.get("coordinate") for axis in axes]
        if coordinate_order != [
            "midpoint",
            "relative_parallel",
            "relative_perpendicular",
        ]:
            raise ValueError("sequence coordinate order drift")
        row_support: list[Fraction] = []
        row_mean: list[Fraction] = []
        for axis in axes[:2]:
            coordinate = axis["coordinate"]
            domain = axis.get("domain", {})
            lower = exact(domain.get("lower_exact"))
            upper = exact(domain.get("upper_exact"))
            if not lower < upper:
                raise ValueError("nondegenerate nonperiodic interval required")
            centre = centres[coordinate]
            left_support = centre - half_width - lower
            right_support = upper - (centre + half_width)
            equilibrium = mean if coordinate == "midpoint" else Fraction(0)
            left_mean = equilibrium - lower
            right_mean = upper - equilibrium
            if min(left_support, right_support, left_mean, right_mean) <= 0:
                raise ValueError(f"support or OU mean leaves box: {sequence['label']}")
            row_support.extend((left_support, right_support))
            row_mean.extend((left_mean, right_mean))
        periodic = axes[2]["domain"]
        period = exact(periodic["period_exact"])
        if half_width * 2 >= period:
            raise ValueError("periodic initial bump reaches the torus cut locus")
        support_margin = min(row_support)
        mean_margin = min(row_mean)
        support_margins.append(support_margin)
        mean_margins.append(mean_margin)
        rows.append(
            {
                "label": sequence["label"],
                "nonperiodic_initial_support_strictly_inside": True,
                "nonperiodic_initial_support_minimum_margin_exact": fraction_text(support_margin),
                "ou_equilibria_strictly_inside": True,
                "ou_equilibria_minimum_margin_exact": fraction_text(mean_margin),
                "periodic_initial_image_sum_smooth_on_torus": True,
                "sequence_id": sequence["sequence_id"],
            }
        )
    return rows, min(support_margins), min(mean_margins)


def build_payload() -> dict[str, Any]:
    sources = checked_sources()
    validate_source_semantics(sources)
    rows, global_support_margin, global_mean_margin = support_and_interior_rows(sources)
    family = sources["genuine_refinement_artifact"]
    source_bound = sources["source_bound_artifact"]
    initial = sources["initial_source"]
    factorization = sources["factorization"]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "source_inventory": {
            role: {"path": relative, "sha256": expected}
            for role, (relative, expected) in SOURCES.items()
        },
        "quantifiers": {
            "budget_cap": "B_star_is_arbitrary_fixed_and_finite_with_B_star>=0",
            "budget_range": "for_every_real_B_in_closed_interval_[0,B_star]",
            "control_range": "for_every_real_w_in_Delta3={w_in_R4:w_j>=0,sum_j_w_j=1}",
            "family_range": "for_every_f_in_exactly_the_12_source_defined_families",
            "mesh_limit": "n_in_N_0_and_n_to_infinity_with_h_f(n)=h_f(0)*2^-n",
            "positive_time_range": "for_every_fixed_0<tau<=T<infinity",
            "derivative_orders": [0, 1, 2],
            "sequence_count": 12,
            "sequence_labels": family["sequence_order"],
            "uniform_mesh_envelope": "h_star(n)=H_star*2^-n=max_f_h_f(n)",
        },
        "source_reconstructed_facts": {
            "alignment_counts": family["uniform_geometry_certificate"][
                "alignment_counts_across_36_axes"
            ],
            "global_max_h0_exact": family["uniform_geometry_certificate"]["global_max_h0_exact"],
            "global_initial_support_minimum_margin_exact": fraction_text(global_support_margin),
            "global_ou_equilibrium_minimum_margin_exact": fraction_text(global_mean_margin),
            "initial_half_width_exact": fraction_text(
                exact_hex(initial["half_width_binary64_hex"])
            ),
            "killing_profile_half_width_exact": factorization["profile_basis"]["half_width_exact"],
            "initial_and_killing_profile_half_widths_are_distinct": True,
            "initial_source_total_mass_exact": "1/1",
            "initial_support_and_equilibrium_rows": rows,
            "source_bound_common_tail_start_n": source_bound["family_scope"][
                "common_sufficient_tail_start_n"
            ],
            "vertex_endpoint_half_cells_included": True,
            "wrapped_periodic_cells_included": True,
        },
        "single_ideal_member_definition": {
            "continuum_H": "H_f=L2(Omega_f,pi_dx)",
            "discrete_H": "H_h_f=ell2(pi_h_f)",
            "continuum_form_domain": (
                "V_f={u_in_H1(I_M_f_times_I_R_f_times_(0,W)):trace_Y=0_u=trace_Y=W_u}"
            ),
            "continuum_boundary_conditions": (
                "natural_Neumann_on_M_and_R_faces_and_periodic_trace_in_Y"
            ),
            "discrete_form_domain": (
                "all_of_finite_dimensional_H_h_f_with_periodic_wrap_edges_"
                "and_no_exterior_reflecting_edge"
            ),
            "global_gauge": "G_h_f=M_L_f/(S_M*S_R*S_Y)",
            "gauged_product_mass": "pi_h_f_ijk=G_h_f*mu_M_i*mu_R_j*mu_Y_k",
            "common_conductance": ("c_tensor_edge=G_h_f*kappa_axis_edge*product_spectator_axis_mu"),
            "control_profile": "psi_w=sum_j=1^4_w_j*phi_j_with_w_in_Delta3",
            "continuum_killing": "B*V_w_with_V_w=W^-1*psi_w*indicator_Da",
            "physical_volume_average": "V_h_C=abs_C^-1*integral_C_V_w_dx",
            "discrete_killing": "B*V_h_C",
            "exact_adjoint_map": "P_h[u]_C=integral_C_u*pi_dx/pi_h_C=J_h_star[u]_C",
            "same_H_h_used_for_mosco_resolvent_rate_and_observable": True,
            "production_centres_substituted_at_any_step": False,
        },
        "density_and_map_contract": {
            "rho": "rho_C=integral_C_pi_dx/pi_h_C",
            "rho_bound": "exp(-eta_f(n))<=rho_C<=exp(eta_f(n))",
            "pi_h_pc_ratio_exact": (
                "pi_h_pc(x)/pi(x)=bar_r_M*bar_r_R*"
                "exp(Phi_M(x_M)-Phi_M(rep_M)+Phi_R(x_R)-Phi_R(rep_R))"
            ),
            "pi_h_pc_ratio_bound": ("exp(-eta_f(n))<=pi_h_pc(x)/pi(x)<=exp(eta_f(n))"),
            "pi_h_pc_uniform_convergence": (
                "norm_infinity(pi_h_pc/pi-1)<=exp(Lambda_star*h_f(n))-1_to_0"
            ),
            "exact_compositions": [
                "P_h*J_h=diag(rho)",
                "J_h*P_h=rho_h_pc*E_h",
            ],
            "map_norm_bound": "norm_J_h=norm_P_h<=exp(eta_f(n)/2)",
            "P_h_J_h_defect": "norm(P_h*J_h-I)<=exp(eta_f(n))-1",
            "J_h_P_h_H1_bound": ("norm(J_h*P_h*u-u)_H_f<=C_P*h_f(n)*norm(u)_ordinary_H1"),
            "J_h_P_h_operator_norm_on_all_H_claimed": False,
        },
        "initial_datum_contract": {
            "definition": "u0_f=q0/pi_on_Omega_f",
            "discretization": "u0_h_f=P_h*u0_f",
            "exact_cell_mass": "pi_h_C*u0_h_C=integral_C_q0_dx",
            "nonperiodic_support_inside_all_12_boxes": True,
            "periodic_images_combined_before_cell_integration": True,
            "unit_mass_on_each_fixed_box": True,
            "regularity_proved_from_flat_compact_bump_and_positive_smooth_pi": [
                "u0_f_in_C_infinity",
                "u0_f_in_H2",
                "u0_f_in_H1",
                "u0_f_in_H_f",
            ],
            "initial_projection_bound": (
                "norm(J_h*u0_h_f-u0_f)_H_f<=C_P*h_f(n)*norm(u0_f)_ordinary_H1"
            ),
            "initial_H1_or_H2_norm_numerically_evaluated": False,
            "initial_quantitative_rate_claim_scope": ("existence_constant_ideal_projection_only"),
        },
        "premise_composition": {
            "one_axis": {
                "cell_centred_reflecting_OU": "Round4_fixed_1D_parameter_instance",
                "vertex_centred_reflecting_dual_OU": ("Round4_endpoint_half_volume_lemma"),
                "relative_parallel_OU": "Round4_parameter_substitution_d=2D_mu=0",
                "periodic_base_and_half_shift": "Round4_exact_periodic_free_identity",
                "genuine_sequences": "Round172_v2",
                "interior_equilibria_checked_from_sources": True,
            },
            "tensor": {
                "free_semigroup_factorization": "Round4",
                "free_strong_resolvent": "Round4_Laplace_composition",
                "free_generalized_Mosco": "Round5_Theorem_1_1",
            },
            "bounded_killing": {
                "multiplier": "K_h_pc=V_h_pc/rho_h_pc",
                "convergence_and_uniform_bound": "Round173",
                "generalized_Mosco_perturbation": "Round5_bounded_killing_corollary",
                "uniform_in_w_and_B_under_fixed_B_star": True,
            },
            "positive_time": {
                "C0_functional_calculus": "Round4",
                "finite_positive_time_net": "Round4",
                "moving_observable_pairing": "Round4",
                "no_t_equals_0_uniform_claim": True,
            },
            "half_order_corollary": {
                "free_residual": "Round10",
                "map_and_killing_residual": "Round173",
                "mixed_boundary_sector_and_contour": "Round11",
                "uniform_residual_constant": "C_free+B_star*C_kill",
            },
        },
        "theorem_conclusions": {
            "ideal_fixed_box_C1_composition_closed_at_theorem_layer": True,
            "generalized_Mosco": (
                "a_h_f_w_B_generalized_Mosco_to_a_f_w_B_for_every_quantified_f_w_B"
            ),
            "strong_resolvent": (
                "J_h*(H_h_f_w_B+alpha)^-1*P_h_to_(H_f_w_B+alpha)^-1_strongly_for_every_alpha>0"
            ),
            "positive_time_state": (
                "sup_t_in_[tau,T]_norm(J_h*f_r_t(H_h)*P_h*u0-f_r_t(H)*u0)_H_f_to_0_for_r=0,1,2"
            ),
            "positive_time_contact_observable": (
                "sup_t_in_[tau,T]_abs(F_h_f_w_B_r(t)-F_f_w_B_r(t))_to_0_for_r=0,1,2"
            ),
            "positive_time_reaction_density": (
                "sup_t_in_[tau,T]_abs(g_h_f_w_B_r(t)-g_f_w_B_r(t))_to_0_for_r=0,1,2"
            ),
            "contact_observable_definition": (
                "F_r(t)=(-1)^r*inner(V_w,H_f_w_B^r*exp(-t*H_f_w_B)*u0_f)_H_f"
            ),
            "reaction_density_definition": "g_r(t)=B*F_r(t)",
            "discrete_reaction_density_definition": "g_h_r(t)=B*F_h_r(t)",
            "discrete_observable_uses_same_V_h_and_same_H_h": True,
        },
        "existence_constant_half_order_corollary": {
            "ideal_only": True,
            "uniform_scope": "exactly_F12_times_Delta3_times_[0,B_star]",
            "resolvent": (
                "norm(J_h*(H_h+sigma+lambda)^-1*P_h-"
                "(H+sigma+lambda)^-1)<="
                "C_sec(B_star)*h_star(n)^(1/2)/(sigma+abs(lambda))^(1/2)"
            ),
            "positive_time_operator": (
                "sup_t_norm(J_h*H_h^r*exp(-t*H_h)*P_h-H^r*exp(-t*H))<=C_r*h_star(n)^(1/2)"
            ),
            "positive_time_observable": ("sup_t_abs(F_h_r(t)-F_r(t))<=C_F_r*h_star(n)^(1/2)"),
            "positive_time_reaction_density": (
                "sup_t_abs(g_h_r(t)-g_r(t))<=B_star*C_F_r*h_star(n)^(1/2)"
            ),
            "derivative_orders": [0, 1, 2],
            "requires_tau_strictly_positive": True,
            "theorem_constants_finite_symbolically": True,
            "theorem_constants_numerically_evaluated": False,
            "theorem_constants_outwardly_enclosed": False,
            "computable_C2_certificate": False,
            "production_or_evaluator_error_included": False,
        },
        "established_scope": {
            "full_f_w_B_n_quantifier_closed": True,
            "pi_h_pc_over_pi_uniform_convergence_proved": True,
            "initial_source_regular_enough_for_H1_map_bound": True,
            "one_axis_premises_instantiated": True,
            "free_tensor_generalized_Mosco_proved": True,
            "bounded_killing_generalized_Mosco_proved": True,
            "ideal_fixed_box_strong_resolvent_proved": True,
            "positive_time_r0_r1_r2_state_contact_and_reaction_convergence_proved": True,
            "ideal_half_order_existence_constant_corollary_proved": True,
        },
        "claim_boundary": {
            "F0_complete": False,
            "F1_complete": False,
            "F2_complete": False,
            "F3_complete": False,
            "box_exhaustion_complete_C3": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "computable_C2_certificate": False,
            "continuum_root_margin_certified": False,
            "numerical_theorem_constants_evaluated": False,
            "positive_budget_scientific_result": False,
            "production_complete_C1": False,
            "production_n0_correlated_containment_receipt_present": False,
            "production_raw_acceptance": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
            "root_or_topology_transfer_complete": False,
            "submission_eligible": False,
        },
        "validation_scope": {
            "source_hashes_and_exact_support_geometry_independently_reconstructible": True,
            "single_artifact_descriptor_snapshot_validated_and_hashed": True,
            "symbolic_analysis_representation": (
                "exact_string_contract_plus_pinned_human_audits_not_machine_proof"
            ),
            "human_round174_mathematical_audit_separate_and_required": True,
            "validator_is_independent_numerical_backend": False,
            "authenticated_execution_attested": False,
        },
        "build_provenance": {
            "builder_path": str(SELF.relative_to(REPORT)),
            "builder_sha256": sha256(descriptor_snapshot(SELF)),
            "arithmetic": "python_stdlib_Fraction_exact_rational_for_source_geometry",
            "canonical_json": "utf8_ascii_subset_indent2_sort_keys_newline",
            "snapshot_model": ("O_NOFOLLOW_regular_file_fstat_before_after_path_inode_identity"),
            "source_snapshots_atomic_against_hostile_writer": False,
            "executed_builder_bytes_authenticated": False,
            "project_module_imports_used": False,
            "network_access_used": False,
            "result_or_positive_budget_payload_read": False,
        },
    }
    require_all_false(payload["claim_boundary"], "composition claim boundary")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        payload = build_payload()
        expected = canonical_bytes(payload)
        if arguments.check:
            actual = descriptor_snapshot(arguments.output)
            if actual != expected:
                raise ValueError(f"artifact drift: {sha256(actual)} != expected {sha256(expected)}")
        else:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_bytes(expected)
        print(
            "PASS_C1_COMPOSITION_BUILD "
            f"sha256={sha256(expected)} sequences=12 "
            "ideal_fixed_box_C1_composition=true complete_C1=false "
            "computable_C2=false release_eligible=false"
        )
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR C1CompositionBuild: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
