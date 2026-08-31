#!/usr/bin/env python3
"""Independent source/geometry validator for the symbolic contract.

This verifier imports neither the builder nor a project module.  It
independently authenticates every source, recomputes the exact-rational tube
clearances and common refinement tail, and checks the symbolic strings with
exact key sets.  It is not an independent numerical backend or a machine
proof of the functional analysis; that remains a separate human review.
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

THIS_FILE = Path(__file__).resolve()
REPORT_ROOT = THIS_FILE.parents[1]
DEFAULT_ARTIFACT = (
    REPORT_ROOT / "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json"
)
BUILDER_RELATIVE = "code/build_continuum_c2_source_bound_map_cut_killing_contract_v1.py"

EXPECTED_SCHEMA = "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1"
EXPECTED_STATUS = (
    "IDEAL_SOURCE_BOUND_SYMBOLIC_MAP_CUT_KILLING_CONTRACT_"
    "NO_NUMERIC_CONSTANT_EVALUATION_NO_PRODUCTION_SAME_MEMBER_NO_COMPLETE_C2"
)

PINNED: dict[str, tuple[str, str]] = {
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

RATIONAL_PATTERN = re.compile(r"-?[0-9]+/[1-9][0-9]*")


class ContractError(ValueError):
    """A fail-closed validation error."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def descriptor_snapshot(path: Path) -> bytes:
    """Return one stable regular-file snapshot without following symlinks."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ContractError("O_NOFOLLOW is required for source snapshots")
    flags = os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ContractError(f"regular file required: {path}")
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
        raise ContractError(f"file changed during descriptor snapshot: {path}")
    if (path_state.st_dev, path_state.st_ino) != (after.st_dev, after.st_ino):
        raise ContractError(f"path identity changed during descriptor snapshot: {path}")
    data = b"".join(chunks)
    if len(data) != after.st_size:
        raise ContractError(f"snapshot size mismatch: {path}")
    return data


def encode(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def forbid_number(token: str) -> None:
    raise ContractError(f"non-integer JSON number forbidden: {token}")


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(data: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=no_duplicate_keys,
            parse_float=forbid_number,
            parse_constant=forbid_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"strict JSON failure for {path}: {exc}") from exc
    if type(value) is not dict:
        raise ContractError(f"top-level JSON object required: {path}")
    if encode(value) != data:
        raise ContractError(f"canonical JSON mismatch: {path}")
    return value


def as_fraction(value: Any) -> Fraction:
    if type(value) is not str or RATIONAL_PATTERN.fullmatch(value) is None:
        raise ContractError(f"invalid rational string: {value!r}")
    numerator, denominator = value.split("/", 1)
    result = Fraction(int(numerator), int(denominator))
    if fraction_text(result) != value:
        raise ContractError(f"unreduced rational string: {value}")
    return result


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_keys(value: Any, expected: set[str], context: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ContractError(f"object required: {context}")
    if set(value) != expected:
        raise ContractError(
            f"exact key mismatch for {context}: {sorted(value)} != {sorted(expected)}"
        )
    return value


def require_same(actual: Any, expected: Any, context: str) -> None:
    """Compare nested JSON values without Python's bool/int equivalence."""
    if type(actual) is not type(expected):
        raise ContractError(
            f"type mismatch for {context}: {type(actual).__name__} != {type(expected).__name__}"
        )
    if type(expected) is dict:
        exact_keys(actual, set(expected), context)
        for key in expected:
            require_same(actual[key], expected[key], f"{context}.{key}")
        return
    if type(expected) is list:
        if len(actual) != len(expected):
            raise ContractError(f"list length mismatch for {context}")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected, strict=True)):
            require_same(actual_item, expected_item, f"{context}[{index}]")
        return
    if actual != expected:
        raise ContractError(f"value mismatch for {context}: {actual!r} != {expected!r}")


def load_pinned() -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    json_roles = {
        "configuration_family",
        "factorization",
        "genuine_refinement_family",
        "ideal_formula",
        "killing_geometry",
        "reference_density",
        "round170_geometry_receipt",
    }
    for role, (relative, expected) in PINNED.items():
        path = REPORT_ROOT / relative
        data = descriptor_snapshot(path)
        if sha256(data) != expected:
            raise ContractError(f"pinned source hash drift: {role}")
        if role in json_roles:
            parsed[role] = decode(data, path)
    return parsed


def expected_rows(
    sources: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], Fraction, Fraction, int]:
    geometry = sources["killing_geometry"]["contact_geometry"]
    radius = as_fraction(geometry["radius_exact"])
    period = as_fraction(geometry["transverse_period_exact"])
    if not (radius > 0 and 2 * radius < period):
        raise ContractError("radius/cut-locus inequality failed")

    rows: list[dict[str, Any]] = []
    row_h: list[Fraction] = []
    row_clearance: list[Fraction] = []
    family = sources["genuine_refinement_family"]
    for sequence in family["sequences"]:
        axes = sequence["axes"]
        relative = [item for item in axes if item.get("coordinate") == "relative_parallel"]
        if len(relative) != 1:
            raise ContractError("relative axis multiplicity drift")
        domain = relative[0]["domain"]
        lower = as_fraction(domain["lower_exact"])
        upper = as_fraction(domain["upper_exact"])
        lower_margin = -radius - lower
        upper_margin = upper - radius
        torus_margin = period / 2 - radius
        if min(lower_margin, upper_margin, torus_margin) <= 0:
            raise ContractError(f"nonpositive tube margin: {sequence['label']}")
        clearance = min(radius, lower_margin, upper_margin, torus_margin) / 2
        h0 = as_fraction(sequence["row_max_h0_exact"])
        row_h.append(h0)
        row_clearance.append(clearance)
        rows.append(
            {
                "contact_radius_exact": fraction_text(radius),
                "label": sequence["label"],
                "relative_lower_exact": fraction_text(lower),
                "relative_lower_margin_exact": fraction_text(lower_margin),
                "relative_upper_exact": fraction_text(upper),
                "relative_upper_margin_exact": fraction_text(upper_margin),
                "row_max_h0_exact": fraction_text(h0),
                "strict_tube_clearance_exact": fraction_text(clearance),
                "torus_cut_locus_margin_exact": fraction_text(torus_margin),
            }
        )
    global_h = max(row_h)
    global_clearance = min(row_clearance)
    start = 0
    while True:
        h = global_h / 2**start
        if h <= 1 and 2 * h * h <= global_clearance * global_clearance:
            break
        start += 1
        if start > 10_000:
            raise ContractError("no finite common tail")
    return rows, global_h, global_clearance, start


def expected_symbolic_contract() -> dict[str, Any]:
    return {
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
    }


def validate_artifact_snapshot(
    path: Path = DEFAULT_ARTIFACT,
) -> tuple[dict[str, Any], str]:
    artifact_bytes = descriptor_snapshot(path)
    artifact_digest = sha256(artifact_bytes)
    payload = decode(artifact_bytes, path)
    exact_keys(
        payload,
        {
            "adversarial_preflight",
            "build_provenance",
            "claim_boundary",
            "family_scope",
            "geometry_rows",
            "schema",
            "source_inventory",
            "status",
            "symbolic_theorem_contract",
            "validation_scope",
        },
        "top level",
    )
    if payload["schema"] != EXPECTED_SCHEMA or payload["status"] != EXPECTED_STATUS:
        raise ContractError("schema/status drift")

    expected_inventory = {
        role: {"path": relative, "sha256": expected}
        for role, (relative, expected) in PINNED.items()
    }
    require_same(payload["source_inventory"], expected_inventory, "source inventory")
    sources = load_pinned()

    family = sources["genuine_refinement_family"]
    config = sources["configuration_family"]
    if (
        family.get("sequence_count") != 12
        or family.get("sequence_order") != config.get("configuration_order")
        or any(value is not False for value in family.get("claim_boundary", {}).values())
    ):
        raise ContractError("genuine family scope drift")
    if (
        config.get("contains_budget_value") is not False
        or config.get("contains_control_values") is not False
        or config.get("authorizes_scientific_execution") is not False
    ):
        raise ContractError("configuration promotion drift")

    reference = sources["reference_density"]
    if (
        reference["normalization"]["conditional_box_renormalization_used"] is not False
        or reference["normalization"]["restricted_density_retains_global_normalization"] is not True
    ):
        raise ContractError("reference normalization drift")
    formulae = sources["ideal_formula"]["formulae"]
    if (
        formulae["map_ratio"] != "rho_i=M_i_pi/pi_h_i"
        or formulae["reconstructed_killing_multiplier"] != "K=V/rho"
    ):
        raise ContractError("map/killing formula drift")
    if sources["factorization"]["coordinate_and_storage"]["periodic_normalization"] != "W^-1":
        raise ContractError("W normalization drift")
    geometry_flags = sources["killing_geometry"]["flags"]
    receipt_flags = sources["round170_geometry_receipt"]["flags"]
    if (
        geometry_flags["concrete_killing_constructed"] is not False
        or geometry_flags["contains_budget_value"] is not False
        or receipt_flags["concrete_killing_constructed"] is not False
        or receipt_flags["full_operator_bound"] is not False
        or receipt_flags["prr_release_authorized"] is not False
    ):
        raise ContractError("geometry/receipt scope promotion")

    rows, global_h, clearance, tail_start = expected_rows(sources)
    require_same(payload["geometry_rows"], rows, "geometry rows")
    expected_family_scope = {
        "common_sufficient_tail_start_n": tail_start,
        "finite_family_cardinality": 12,
        "global_max_h0_exact": fraction_text(global_h),
        "global_strict_tube_clearance_exact": fraction_text(clearance),
        "labels": [row["label"] for row in rows],
        "mesh_rule": "h_f(n)=h_f(0)*2^-n",
        "quantifier": "for_each_of_exactly_12_families_for_every_integer_n_at_or_above_common_tail_start",
        "uniform_tail_squared_condition": "2*h_f(n)^2<=global_strict_tube_clearance^2 and h_f(n)<=1",
    }
    require_same(payload["family_scope"], expected_family_scope, "family scope")

    expected_preflight = {
        "circle_radius_strictly_below_half_period": True,
        "contact_tube_away_from_periodic_cut_locus_on_common_tail": True,
        "contact_tube_strictly_inside_every_relative_box_on_common_tail": True,
        "dense_tensor_allocation_required": False,
        "global_unconditioned_reference_density_required": True,
        "sharp_contact_indicator_differentiated": False,
        "vertex_endpoint_half_cells_included": True,
        "wrapped_periodic_cells_included": True,
    }
    require_same(
        payload["adversarial_preflight"],
        expected_preflight,
        "adversarial preflight",
    )

    expected_boundary = {
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
    }
    require_same(payload["claim_boundary"], expected_boundary, "claim boundary")
    require_same(
        payload["symbolic_theorem_contract"],
        expected_symbolic_contract(),
        "symbolic theorem contract",
    )
    expected_validation_scope = {
        "authenticated_execution_attested": False,
        "exact_geometry_and_source_pins_independently_reconstructible": True,
        "human_mathematical_referee_separate_and_required": True,
        "symbolic_analysis_representation": (
            "exact_string_contract_not_backend_or_machine_proof_replication"
        ),
        "validator_is_independent_numerical_backend": False,
    }
    require_same(
        payload["validation_scope"],
        expected_validation_scope,
        "validation scope",
    )

    provenance = exact_keys(
        payload["build_provenance"],
        {
            "arithmetic",
            "builder_path",
            "builder_sha256",
            "canonical_json",
            "executed_builder_bytes_authenticated",
            "network_access_used",
            "project_module_imports_used",
            "snapshot_model",
            "source_snapshots_atomic_against_hostile_writer",
        },
        "build provenance",
    )
    if (
        provenance["builder_path"] != BUILDER_RELATIVE
        or provenance["builder_sha256"]
        != sha256(descriptor_snapshot(REPORT_ROOT / BUILDER_RELATIVE))
        or provenance["arithmetic"] != "python_stdlib_Fraction_exact_geometry_only"
        or provenance["canonical_json"] != "utf8_ascii_subset_indent2_sort_keys_newline"
        or provenance["executed_builder_bytes_authenticated"] is not False
        or provenance["network_access_used"] is not False
        or provenance["project_module_imports_used"] is not False
        or provenance["snapshot_model"]
        != (
            "descriptor_O_NOFOLLOW_fstat_before_after_path_identity_"
            "no_hostile_concurrent_writer_assumed"
        )
        or provenance["source_snapshots_atomic_against_hostile_writer"] is not False
    ):
        raise ContractError("build provenance drift")
    return payload, artifact_digest


def validate_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    payload, _artifact_digest = validate_artifact_snapshot(path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args()
    try:
        payload, artifact_digest = validate_artifact_snapshot(args.artifact)
        print(
            "PASS independent source/geometry and exact-string-contract validation "
            f"families={len(payload['geometry_rows'])} "
            f"tail_start_n={payload['family_scope']['common_sufficient_tail_start_n']} "
            f"validated_snapshot_sha256={artifact_digest}"
        )
        return 0
    except (ContractError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
