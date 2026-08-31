#!/usr/bin/env python3
"""Build the source-bound symbolic map/cut/killing contract.

The builder uses only exact rational arithmetic for source geometry.  It
authenticates the twelve genuine refinement sequences, verifies the three
conditions needed for the Euclidean circle-tube formula, and emits symbolic
analytical constants.  It does not evaluate theorem constants, import project
modules, or construct a concrete control, budget, or production member.
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
OUTPUT = REPORT / "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json"

SCHEMA = "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1"
STATUS = (
    "IDEAL_SOURCE_BOUND_SYMBOLIC_MAP_CUT_KILLING_CONTRACT_"
    "NO_NUMERIC_CONSTANT_EVALUATION_NO_PRODUCTION_SAME_MEMBER_NO_COMPLETE_C2"
)

SOURCES: dict[str, tuple[str, str]] = {
    "genuine_refinement_family": (
        "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9",
    ),
    "configuration_family": (
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
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
    "killing_geometry": (
        "artifacts/data/physical_killing_geometry_source_v1.json",
        "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    ),
    "round170_geometry_receipt": (
        "artifacts/data/physical_production_killing_geometry_two_repeat_outer_receipt_v1.json",
        "d635dfb7dd24fc15731dfd69e20264a5515c3bf82b92569a58cd2bed3264fcd9",
    ),
    "round4_map_note": (
        "notes/continuum_c1_free_form_and_functional_bridge_candidate.md",
        "17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562",
    ),
    "round4_map_audit": (
        "audits/continuum_c1_refinement_functional_bridge_round4_20260717.md",
        "6ccdcd76a4049e198d13ae45d86570c17d7876a4ef28de8fb3fed0ea1b513134",
    ),
    "round9_residual_note": (
        "notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md",
        "4b20189814c763816ea707630ff098c98995afd7d3207808225a320a742508c2",
    ),
    "round9_residual_audit": (
        "audits/continuum_c2_qf2_checkerboard_residual_route_round9_20260717.md",
        "ed1f15c20c93db274989827dae9ccf5f3d36d5d80e1c9ba90052de8edf18b260",
    ),
    "round10_free_residual_note": (
        "notes/continuum_c2_one_sided_free_sg_residual_candidate.md",
        "ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4",
    ),
    "round10_free_residual_audit": (
        "audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md",
        "c00351acc5ff3be67cbb579ccab768e8e226bd29bc730f5d9acb15c5dcc3163d",
    ),
    "round11_sector_note": (
        "notes/continuum_c2_mixed_neumann_periodic_sector_h2_candidate.md",
        "4339385e8489984701aabedbd4ab0a28d69db5b2ffd7e2d1c91d1d4ba63564d9",
    ),
    "round11_sector_audit": (
        "audits/continuum_c2_mixed_neumann_periodic_sector_h2_round11_20260717.md",
        "d3b0aca6203999ba18f08a380847f7253e41fc72272d28f4c4fcde92dbb89a2c",
    ),
    "successor_theory_note": (
        "notes/continuum_c2_source_bound_map_cut_killing_lemma_v1.md",
        "09c84f471e4d0b3b4e927e5c99a12999827b7e060bcc7ce02122a4107d8460ed",
    ),
}

JSON_ROLES = frozenset(
    {
        "configuration_family",
        "factorization",
        "genuine_refinement_family",
        "ideal_formula",
        "killing_geometry",
        "reference_density",
        "round170_geometry_receipt",
    }
)
RATIONAL_RE = re.compile(r"-?[0-9]+/[1-9][0-9]*")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def descriptor_snapshot(path: Path) -> bytes:
    """Read one stable regular-file snapshot without following a symlink.

    This detects ordinary replacement or mutation during the read and checks
    that the descriptor still names the path entry afterward.  It is not a
    defence against a hostile writer capable of defeating metadata checks.
    """
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("O_NOFOLLOW is required for source snapshots")
    flags = os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
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
    signature_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    signature_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if signature_before != signature_after:
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
        raise ValueError(f"top-level JSON object required: {path}")
    if canonical_bytes(value) != data:
        raise ValueError(f"noncanonical JSON source: {path}")
    return value


def exact(text: Any) -> Fraction:
    if type(text) is not str or RATIONAL_RE.fullmatch(text) is None:
        raise ValueError(f"invalid exact rational string: {text!r}")
    numerator, denominator = text.split("/", 1)
    result = Fraction(int(numerator), int(denominator))
    if rational(result) != text:
        raise ValueError(f"unreduced rational string: {text}")
    return result


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def checked_sources() -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    for role, (relative, expected) in SOURCES.items():
        path = REPORT / relative
        data = descriptor_snapshot(path)
        actual = digest(data)
        if actual != expected:
            raise ValueError(f"source hash drift for {role}: {actual} != {expected}")
        if role in JSON_ROLES:
            parsed[role] = parse_json(data, path)
    return parsed


def require_all_false(value: Any, context: str) -> None:
    if type(value) is not dict or not value:
        raise ValueError(f"nonempty false map required: {context}")
    if any(flag is not False for flag in value.values()):
        raise ValueError(f"promotion flag drift: {context}")


def validate_source_scope(sources: dict[str, dict[str, Any]]) -> None:
    family = sources["genuine_refinement_family"]
    if (
        family.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2"
        or family.get("sequence_count") != 12
    ):
        raise ValueError("genuine-family schema/count drift")
    require_all_false(family.get("claim_boundary"), "genuine family")
    if family["established_scope"].get("genuine_refinement_sequences_defined") is not True:
        raise ValueError("genuine sequences are no longer established")

    config = sources["configuration_family"]
    if (
        config.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or config.get("configuration_count") != 12
        or config.get("contains_budget_value") is not False
        or config.get("contains_control_values") is not False
        or config.get("authorizes_scientific_execution") is not False
    ):
        raise ValueError("configuration source scope drift")
    if family.get("sequence_order") != config.get("configuration_order"):
        raise ValueError("family/config order mismatch")

    expected_schemas = {
        "reference_density": "encounter_continuum_c1_reference_density_source_v1",
        "ideal_formula": "encounter_continuum_c1_ideal_formula_source_v1",
        "factorization": "encounter_continuum_c1_factorization_source_v1",
        "killing_geometry": "encounter_physical_killing_geometry_source_v1",
        "round170_geometry_receipt": "encounter_killing_geometry_two_repeat_outer_receipt_v1",
    }
    for role, schema in expected_schemas.items():
        if sources[role].get("schema") != schema:
            raise ValueError(f"source schema drift: {role}")

    for role in ("reference_density", "ideal_formula", "factorization"):
        require_all_false(sources[role].get("claim_boundary"), role)

    geometry_flags = sources["killing_geometry"].get("flags")
    if (
        type(geometry_flags) is not dict
        or geometry_flags.get("contact_geometry_defined") is not True
        or geometry_flags.get("concrete_killing_constructed") is not False
        or geometry_flags.get("contains_budget_value") is not False
        or geometry_flags.get("contains_control_values") is not False
        or geometry_flags.get("full_operator_bound") is not False
    ):
        raise ValueError("killing-geometry scope drift")

    receipt_flags = sources["round170_geometry_receipt"].get("flags")
    if (
        type(receipt_flags) is not dict
        or receipt_flags.get("killing_geometry_bound") is not True
        or receipt_flags.get("concrete_killing_constructed") is not False
        or receipt_flags.get("full_operator_bound") is not False
        or receipt_flags.get("independent_backend") is not False
        or receipt_flags.get("prr_release_authorized") is not False
    ):
        raise ValueError("Round-170 receipt scope drift")

    reference = sources["reference_density"]
    if (
        reference["normalization"].get("conditional_box_renormalization_used") is not False
        or reference["normalization"].get("restricted_density_retains_global_normalization")
        is not True
    ):
        raise ValueError("global density normalization drift")

    formulae = sources["ideal_formula"]["formulae"]
    if (
        formulae.get("map_ratio") != "rho_i=M_i_pi/pi_h_i"
        or formulae.get("reconstructed_killing_multiplier") != "K=V/rho"
        or formulae.get("global_gauge")
        != "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)"
    ):
        raise ValueError("map/gauge/killing formula drift")

    factorization = sources["factorization"]
    if (
        factorization["coordinate_and_storage"].get("periodic_normalization") != "W^-1"
        or factorization["cell_average_formulae"].get("physical_volume_killing_average")
        != "V_j_mab=W^-1*C_ab*Phi_jm"
    ):
        raise ValueError("factorization W normalization drift")


def relative_axis(sequence: dict[str, Any]) -> dict[str, Any]:
    axes = sequence.get("axes")
    if type(axes) is not list:
        raise ValueError("sequence axes missing")
    matches = [axis for axis in axes if axis.get("coordinate") == "relative_parallel"]
    if len(matches) != 1:
        raise ValueError("relative_parallel axis is not unique")
    return matches[0]


def geometry_certificate(
    sources: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], Fraction, Fraction, int]:
    family = sources["genuine_refinement_family"]
    geometry = sources["killing_geometry"]
    a = exact(geometry["contact_geometry"]["radius_exact"])
    width = exact(geometry["contact_geometry"]["transverse_period_exact"])
    if not (a > 0 and 2 * a < width):
        raise ValueError("contact radius does not lie below the torus cut locus")

    family_rows: list[dict[str, Any]] = []
    clearances: list[Fraction] = []
    h0_values: list[Fraction] = []
    for sequence in family["sequences"]:
        axis = relative_axis(sequence)
        domain = axis.get("domain")
        if type(domain) is not dict:
            raise ValueError("relative domain missing")
        lower = exact(domain["lower_exact"])
        upper = exact(domain["upper_exact"])
        lower_margin = -a - lower
        upper_margin = upper - a
        torus_margin = width / 2 - a
        if min(lower_margin, upper_margin, torus_margin) <= 0:
            raise ValueError(f"circle tube has no positive box/chart margin: {sequence['label']}")
        strict_clearance = min(a, lower_margin, upper_margin, torus_margin) / 2
        h0 = exact(sequence["row_max_h0_exact"])
        clearances.append(strict_clearance)
        h0_values.append(h0)
        family_rows.append(
            {
                "contact_radius_exact": rational(a),
                "label": sequence["label"],
                "relative_lower_exact": rational(lower),
                "relative_lower_margin_exact": rational(lower_margin),
                "relative_upper_exact": rational(upper),
                "relative_upper_margin_exact": rational(upper_margin),
                "row_max_h0_exact": rational(h0),
                "strict_tube_clearance_exact": rational(strict_clearance),
                "torus_cut_locus_margin_exact": rational(torus_margin),
            }
        )

    global_h0 = max(h0_values)
    global_clearance = min(clearances)
    tail_start = 0
    while True:
        h = global_h0 / 2**tail_start
        if h <= 1 and 2 * h * h <= global_clearance * global_clearance:
            break
        tail_start += 1
        if tail_start > 10_000:
            raise ValueError("failed to find a finite common tube tail")
    return family_rows, global_h0, global_clearance, tail_start


def build_payload() -> dict[str, Any]:
    sources = checked_sources()
    validate_source_scope(sources)
    rows, global_h0, clearance, tail_start = geometry_certificate(sources)
    builder_sha = digest(descriptor_snapshot(SELF))

    source_inventory = {
        role: {"path": relative, "sha256": expected}
        for role, (relative, expected) in SOURCES.items()
    }
    return {
        "adversarial_preflight": {
            "circle_radius_strictly_below_half_period": True,
            "contact_tube_away_from_periodic_cut_locus_on_common_tail": True,
            "contact_tube_strictly_inside_every_relative_box_on_common_tail": True,
            "dense_tensor_allocation_required": False,
            "global_unconditioned_reference_density_required": True,
            "sharp_contact_indicator_differentiated": False,
            "vertex_endpoint_half_cells_included": True,
            "wrapped_periodic_cells_included": True,
        },
        "build_provenance": {
            "arithmetic": "python_stdlib_Fraction_exact_geometry_only",
            "builder_path": f"code/{SELF.name}",
            "builder_sha256": builder_sha,
            "canonical_json": "utf8_ascii_subset_indent2_sort_keys_newline",
            "executed_builder_bytes_authenticated": False,
            "network_access_used": False,
            "project_module_imports_used": False,
            "snapshot_model": (
                "descriptor_O_NOFOLLOW_fstat_before_after_path_identity_"
                "no_hostile_concurrent_writer_assumed"
            ),
            "source_snapshots_atomic_against_hostile_writer": False,
        },
        "claim_boundary": {
            "F0_complete": False,
            "F1_complete": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "concrete_control_selected": False,
            "numerical_theorem_constants_evaluated": False,
            "positive_budget_present": False,
            "production_n0_correlated_containment_receipt_present": False,
            "production_raw_acceptance": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
            "submission_eligible": False,
        },
        "family_scope": {
            "common_sufficient_tail_start_n": tail_start,
            "finite_family_cardinality": len(rows),
            "global_max_h0_exact": rational(global_h0),
            "global_strict_tube_clearance_exact": rational(clearance),
            "labels": [row["label"] for row in rows],
            "mesh_rule": "h_f(n)=h_f(0)*2^-n",
            "quantifier": "for_each_of_exactly_12_families_for_every_integer_n_at_or_above_common_tail_start",
            "uniform_tail_squared_condition": "2*h_f(n)^2<=global_strict_tube_clearance^2 and h_f(n)<=1",
        },
        "geometry_rows": rows,
        "schema": SCHEMA,
        "source_inventory": source_inventory,
        "status": STATUS,
        "symbolic_theorem_contract": {
            "contact_profile": {
                "field": "V=W^-1*psi(M)*indicator_Da(R,Y)",
                "profile_lipschitz_bound": "L_Psi=norm_b_prime_infinity/(profile_half_width^2*I_b)",
                "profile_sup_bound": "Psi_star=norm_b_infinity/(profile_half_width*I_b)",
                "simplex_scope": "weights_j>=0 and sum_j_weights_j=1",
                "w_normalization_present": True,
            },
            "cut_layer": {
                "cut_cell_union": "subset_of_closed_delta_neighborhood_of_circle_boundary",
                "delta": "sqrt(h_R^2+h_Y^2)<=sqrt(2)*h",
                "physical_volume_average": True,
                "profile_average_bound": "norm_QM_psi_minus_psi_L2_pi<=(L_Psi/W)*h",
                "sharp_indicator_derivative_used": False,
                "tube_area": "area<=pi_circle*((a+delta)^2-(a-delta)^2)=4*pi_circle*a*delta",
                "tube_area_hypotheses": [
                    "delta<a",
                    "a+delta<W/2",
                    "R_lower<-a-delta",
                    "R_upper>a+delta",
                ],
                "weighted_cut_bound": "norm_Vh_minus_V_L2_pi<=C_V_cut*h^(1/2)+(L_Psi/W)*h",
            },
            "killing_multiplier": {
                "definition": "K_h_pc=V_h_pc/rho_h_pc",
                "linfinity_bound": "norm_K_h_pc_infinity<=exp(Lambda_star*H_star)*Psi_star/W",
                "mixed_error_bound": "norm_K_h_pc_minus_V_L2_pi<=C_K_cut*h^(1/2)+C_K_map*h",
            },
            "map": {
                "exact_adjoint": "P_h=J_h_star",
                "exact_compositions": [
                    "P_h*J_h=diag(rho)",
                    "J_h*P_h=rho_h_pc*E_h",
                ],
                "jp_h1_to_l2": "norm_JhPhu_minus_u_L2_pi<=C_P*h*norm_u_H1",
                "norm": "norm_J_h=norm_P_h<=exp(Lambda_star*h/2)",
                "pj_defect": "norm_P_hJ_h_minus_I<=exp(Lambda_star*h)-1<=Lambda_star*exp(Lambda_star*H_star)*h",
            },
            "rho": {
                "axis_cell_integral_ratio": "r_a_i=integral_C_exp_minus_Phi_a_dx/(cell_volume_i*exp_minus_Phi_a_at_representative)",
                "global_gauge": "G=Z^-1*bar_r_M*bar_r_R=M_L/(S_M*S_R*S_Y)",
                "physical_cell_mass_not_representative_mass": True,
                "tensor_factorization": "rho_ijk=(r_M_i/bar_r_M)*(r_R_j/bar_r_R)",
                "two_sided_enclosure": "exp(-eta_f(n))<=rho_ijk<=exp(eta_f(n))",
                "uniform_exponent": "eta_f(n)=L_M_f*h_M_f(n)+L_R_f*h_R_f(n)<=Lambda_star*h_f(n)",
            },
            "round9_residual": {
                "authoritative_complex_convention": "complex_inner_product_conjugate_first_factor",
                "bound": "abs_R_h_kill<=C_kill*h^(1/2)*norm_u_H2*norm_v_h_1h",
                "budget_factor_selected": False,
                "hypotheses": [
                    "quotient_dimension_is_3_for_H2_to_Linfinity",
                    "u_in_H2_on_fixed_mixed_boundary_box",
                    "J_hP_h_map_bound",
                    "K_h_linfinity_bound",
                    "K_h_minus_V_weighted_L2_bound",
                    "uniform_J_h_norm",
                    "h<=1",
                ],
            },
            "symbolic_constant_definitions": {
                "C_K": "exp(Lambda_star*H_star)*Psi_star/W",
                "C_K_cut": "exp(Lambda_star*H_star)*C_V_cut",
                "C_K_map": "exp(Lambda_star*H_star)*(L_Psi/W+Lambda_star*Psi_star/W)",
                "C_P": "sqrt(pi_plus_star)*(C_av+Lambda_star*exp(Lambda_star*H_star))",
                "C_V_cut": "2*2^(1/4)*(Psi_star/W)*sqrt(pi_circle*a*pi_plus_star*L_M_star)",
                "C_av": "sqrt(3)*sqrt(pi_plus_star/pi_minus_star)/pi_circle",
                "C_kill": "exp(Lambda_star*H_star/2)*(C_K*C_P+C_emb*(C_K_cut+C_K_map))",
                "L_M_f": "(2*ou_stiffness/particle_diffusion)*max_endpoint_abs(M-ou_mean)",
                "L_R_f": "(ou_stiffness/(2*particle_diffusion))*max_endpoint_abs(R)",
                "Lambda_star": "max_over_12(L_M_f+L_R_f)",
                "theorem_constants_numerically_evaluated": False,
            },
        },
        "validation_scope": {
            "authenticated_execution_attested": False,
            "exact_geometry_and_source_pins_independently_reconstructible": True,
            "human_mathematical_referee_separate_and_required": True,
            "symbolic_analysis_representation": (
                "exact_string_contract_not_backend_or_machine_proof_replication"
            ),
            "validator_is_independent_numerical_backend": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        payload = build_payload()
        encoded = canonical_bytes(payload)
        if args.check:
            if descriptor_snapshot(args.output) != encoded:
                raise ValueError(f"artifact drift: {args.output}")
            print(
                "PASS source-bound map/cut/killing contract "
                f"sha256={digest(encoded)} tail_start_n={payload['family_scope']['common_sufficient_tail_start_n']}"
            )
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
        print(f"WROTE {args.output} sha256={digest(encoded)}")
        return 0
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
