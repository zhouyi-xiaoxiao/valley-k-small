#!/usr/bin/env python3
"""Build the source-bound ideal joint-refinement-family authority v2.

The builder uses only standard-library exact rational arithmetic.  It opens
the explicitly pinned control-free sources, reconstructs all twelve anchor
rows, and defines one dyadic ``n in N_0`` sequence per row.  It does not open
production arrays, controls, budgets, results, or scratch payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"

SCHEMA = "encounter_continuum_c1_genuine_joint_refinement_family_v2"
STATUS = (
    "FROZEN_SOURCE_BOUND_12_IDEAL_JOINT_REFINEMENT_SEQUENCES_DEFINED_"
    "PRODUCTION_ACCEPTANCE_C0_C1_C2_C3_RELEASE_FALSE"
)

SOURCES: dict[str, tuple[str, str]] = {
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
    "round4_theorem_note": (
        "notes/continuum_c1_free_form_and_functional_bridge_candidate.md",
        "17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562",
    ),
    "round4_audit": (
        "audits/continuum_c1_refinement_functional_bridge_round4_20260717.md",
        "6ccdcd76a4049e198d13ae45d86570c17d7876a4ef28de8fb3fed0ea1b513134",
    ),
    "round5_theorem_note": (
        "notes/continuum_c1_varying_space_resolvent_mosco_candidate.md",
        "0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1",
    ),
    "round5_audit": (
        "audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md",
        "9e1cacca6c9c40675f31acbe743bbeccc74aca29b6378a641e1613ae48e55287",
    ),
    "fixed_row_anti_vacuity_policy": (
        "artifacts/data/continuum_c1_c2_fixed_row_anti_vacuity_policy_v1.json",
        "c8b9f3aca2b3a516935eeb1fdfb2bf542ba0da2d12ae4c11581f6f1ee607f628",
    ),
    "fixed_row_member_spec": (
        "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json",
        "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef",
    ),
    "successor_theory_note": (
        "notes/continuum_c1_genuine_joint_refinement_family_v2.md",
        "c312ca42d57af451ffef30c69aed7275ba8d9065eb4d1ae80f8439bd2320a142",
    ),
}

JSON_SOURCE_ROLES = {
    "configuration_family",
    "factorization",
    "fixed_row_anti_vacuity_policy",
    "fixed_row_member_spec",
    "ideal_formula",
    "reference_density",
}

COORDINATES = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
NONPERIODIC_ALIGNMENTS = {
    "cell_centred_reflecting",
    "vertex_centred_reflecting_dual",
}
PERIODIC_ALIGNMENTS = {
    "cell_centred_periodic_base",
    "cell_centred_periodic_half_shift",
}
HEX_PATTERN = re.compile(
    r"^(?P<sign>[+-]?)(?:0x)(?P<int>[0-9a-f]+)"
    r"(?:\.(?P<frac>[0-9a-f]*))?p(?P<exp>[+-]?[0-9]+)$"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def reject_float(token: str) -> None:
    raise ValueError(f"floating JSON number forbidden: {token}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_bytes(data: bytes, path: Path) -> dict[str, Any]:
    try:
        text = data.decode("ascii")
        value = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_float=reject_float,
            parse_constant=reject_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid strict JSON source {path}: {exc}") from exc
    if type(value) is not dict:
        raise ValueError(f"top-level JSON object required: {path}")
    if canonical_bytes(value) != data:
        raise ValueError(f"noncanonical JSON source: {path}")
    return value


def exact_hex(value: str) -> Fraction:
    match = HEX_PATTERN.fullmatch(value.lower())
    if match is None:
        raise ValueError(f"unsupported hexadecimal binary rational: {value}")
    fractional = match.group("frac") or ""
    digits = match.group("int") + fractional
    numerator = int(digits, 16)
    denominator = 16 ** len(fractional)
    exponent = int(match.group("exp"))
    if exponent >= 0:
        numerator *= 2**exponent
    else:
        denominator *= 2 ** (-exponent)
    if match.group("sign") == "-":
        numerator = -numerator
    return Fraction(numerator, denominator)


def exact_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def parse_exact_text(value: str) -> Fraction:
    if not re.fullmatch(r"-?[0-9]+/[1-9][0-9]*", value):
        raise ValueError(f"noncanonical rational string: {value}")
    numerator_text, denominator_text = value.split("/", 1)
    result = Fraction(int(numerator_text), int(denominator_text))
    if exact_text(result) != value:
        raise ValueError(f"unreduced rational string: {value}")
    return result


def checked_sources() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    raw: dict[str, bytes] = {}
    parsed: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_sha) in SOURCES.items():
        path = REPORT / relative
        data = path.read_bytes()
        actual_sha = sha256_bytes(data)
        if actual_sha != expected_sha:
            raise ValueError(f"source hash drift for {role}: {actual_sha} != {expected_sha}")
        raw[role] = data
        if role in JSON_SOURCE_ROLES:
            parsed[role] = parse_json_bytes(data, path)
    return raw, parsed


def require_false_map(value: Any, *, context: str) -> None:
    if type(value) is not dict or not value:
        raise ValueError(f"nonempty false-map required: {context}")
    if any(flag is not False for flag in value.values()):
        raise ValueError(f"source promotion flag drift: {context}")


def validate_source_semantics(sources: dict[str, dict[str, Any]]) -> None:
    config = sources["configuration_family"]
    if config.get("schema") != "encounter_physical_configuration_family_control_free_v1":
        raise ValueError("configuration schema drift")
    if config.get("configuration_count") != 12:
        raise ValueError("configuration count drift")
    rows = config.get("configurations")
    order = config.get("configuration_order")
    if (
        type(rows) is not list
        or type(order) is not list
        or [row.get("label") for row in rows] != order
    ):
        raise ValueError("configuration row/order drift")
    if (
        config.get("contains_budget_value") is not False
        or config.get("contains_control_values") is not False
        or config.get("authorizes_scientific_execution") is not False
    ):
        raise ValueError("configuration source scope drift")

    reference = sources["reference_density"]
    if reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1":
        raise ValueError("reference-density schema drift")
    require_false_map(reference.get("claim_boundary"), context="reference density")

    formula = sources["ideal_formula"]
    if formula.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1":
        raise ValueError("ideal-formula schema drift")
    require_false_map(formula.get("claim_boundary"), context="ideal formula")

    factorization = sources["factorization"]
    if factorization.get("schema") != "encounter_continuum_c1_factorization_source_v1":
        raise ValueError("factorization schema drift")
    require_false_map(factorization.get("claim_boundary"), context="factorization")

    policy = sources["fixed_row_anti_vacuity_policy"]
    if policy.get("schema") != "encounter_continuum_c1_c2_fixed_row_anti_vacuity_policy_v1":
        raise ValueError("anti-vacuity policy schema drift")
    policy_claims = policy.get("claim_boundary")
    require_false_map(policy_claims, context="anti-vacuity policy")
    if policy_claims.get("policy_predecessor_order_independently_sealed") is not False:
        raise ValueError("anti-vacuity predecessor-order boundary drift")

    member = sources["fixed_row_member_spec"]
    if member.get("schema") != "encounter_continuum_c1_c2_fixed_row_member_spec_v1":
        raise ValueError("fixed-row member-spec schema drift")
    require_false_map(member.get("claim_boundary"), context="fixed-row member spec")
    if member["claim_boundary"].get("genuine_refinement_sequence_present") is not False:
        raise ValueError("historical member-spec refinement boundary drift")

    dynamics = config.get("dynamics")
    bundle = reference.get("physical_parameter_bundle")
    if type(dynamics) is not dict or type(bundle) is not dict:
        raise ValueError("missing physical parameter bundles")
    for key in (
        "ou_mean_binary64_hex",
        "ou_stiffness_binary64_hex",
        "particle_diffusion_binary64_hex",
        "transverse_period_exact",
    ):
        if dynamics.get(key) != bundle.get(key):
            raise ValueError(f"reference/config parameter mismatch: {key}")


def axis_record(
    coordinate: str,
    source_axis: dict[str, Any],
    dynamics: dict[str, Any],
) -> tuple[dict[str, Any], Fraction, Fraction, int]:
    alignment = source_axis.get("alignment")
    size = source_axis.get("size")
    if type(alignment) is not str or type(size) is not int or size < 2:
        raise ValueError(f"invalid source axis: {coordinate}")

    if alignment in NONPERIODIC_ALIGNMENTS:
        lower_hex = source_axis.get("lower_binary64_hex")
        upper_hex = source_axis.get("upper_binary64_hex")
        if type(lower_hex) is not str or type(upper_hex) is not str:
            raise ValueError(f"missing nonperiodic bounds: {coordinate}")
        lower = exact_hex(lower_hex)
        upper = exact_hex(upper_hex)
        if not lower < upper:
            raise ValueError(f"degenerate nonperiodic interval: {coordinate}")
        width = upper - lower
        if alignment == "vertex_centred_reflecting_dual":
            intervals = size - 1
            size_formula = "size(n)=(size0-1)*2^n+1"
            interval_formula = "interval_count(n)=(size0-1)*2^n"
            minimum_volume_factor = Fraction(1, 2)
            cell_rule = "dual endpoints have h(n)/2; interior dual cells have h(n)"
        else:
            intervals = size
            size_formula = "size(n)=size0*2^n"
            interval_formula = "interval_count(n)=size0*2^n"
            minimum_volume_factor = Fraction(1, 1)
            cell_rule = "all control volumes have length h(n)"
        h0 = width / intervals
        record = {
            "alignment": alignment,
            "anchor_interval_count": intervals,
            "anchor_size": size,
            "cell_rule": cell_rule,
            "coordinate": coordinate,
            "domain": {
                "lower_binary64_hex": lower_hex,
                "lower_exact": exact_text(lower),
                "upper_binary64_hex": upper_hex,
                "upper_exact": exact_text(upper),
                "width_exact": exact_text(width),
            },
            "interval_count_formula": interval_formula,
            "maximum_cell_side_at_n": "h0_exact/2^n",
            "minimum_axis_volume_factor": exact_text(minimum_volume_factor),
            "refinement_index_domain": "N_0",
            "size_formula": size_formula,
            "spacing_formula": "h(n)=h0_exact/2^n",
            "spacing_h0_exact": exact_text(h0),
        }
        minimum_side0 = h0 * minimum_volume_factor
        dual_count = int(alignment == "vertex_centred_reflecting_dual")
        return record, h0, minimum_side0, dual_count

    if alignment not in PERIODIC_ALIGNMENTS:
        raise ValueError(f"unknown alignment: {alignment}")
    period = parse_exact_text(dynamics["transverse_period_exact"])
    start = parse_exact_text(dynamics["transverse_domain_start_exact"])
    h0 = period / size
    shift0 = parse_exact_text(source_axis.get("periodic_shift_exact"))
    expected_shift0 = h0 / 2 if alignment == "cell_centred_periodic_half_shift" else Fraction(0, 1)
    if shift0 != expected_shift0:
        raise ValueError(f"periodic anchor shift mismatch: {coordinate}")
    shift_formula = (
        "sigma(n)=h(n)/2" if alignment == "cell_centred_periodic_half_shift" else "sigma(n)=0"
    )
    record = {
        "alignment": alignment,
        "anchor_interval_count": size,
        "anchor_size": size,
        "cell_rule": ("uniform torus cells; a seam crossing is stored as two ordered segments"),
        "coordinate": coordinate,
        "domain": {
            "period_exact": exact_text(period),
            "start_exact": exact_text(start),
        },
        "interval_count_formula": "interval_count(n)=size0*2^n",
        "maximum_cell_side_at_n": "h0_exact/2^n",
        "minimum_axis_volume_factor": "1/1",
        "periodic_shift_at_n_formula": shift_formula,
        "periodic_shift_n0_exact": exact_text(shift0),
        "refinement_index_domain": "N_0",
        "size_formula": "size(n)=size0*2^n",
        "spacing_formula": "h(n)=h0_exact/2^n",
        "spacing_h0_exact": exact_text(h0),
    }
    return record, h0, h0, 0


def physical_parameter_freeze(config: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    dynamics = config["dynamics"]
    result: dict[str, Any] = {
        "bundle_id": "encounter_control_free_physics_v2",
        "fixed_at_every_level_of_all_twelve_sequences": True,
        "ou_mean_binary64_hex": dynamics["ou_mean_binary64_hex"],
        "ou_mean_exact": exact_text(exact_hex(dynamics["ou_mean_binary64_hex"])),
        "ou_stiffness_binary64_hex": dynamics["ou_stiffness_binary64_hex"],
        "ou_stiffness_exact": exact_text(exact_hex(dynamics["ou_stiffness_binary64_hex"])),
        "particle_diffusion_binary64_hex": dynamics["particle_diffusion_binary64_hex"],
        "particle_diffusion_exact": exact_text(
            exact_hex(dynamics["particle_diffusion_binary64_hex"])
        ),
        "physical_dimension": config["physical_dimension"],
        "quotient_dimension": config["quotient_dimension"],
        "transverse_domain_start_exact": exact_text(
            parse_exact_text(dynamics["transverse_domain_start_exact"])
        ),
        "transverse_period_exact": exact_text(
            parse_exact_text(dynamics["transverse_period_exact"])
        ),
    }
    if (
        result["transverse_period_exact"]
        != reference["physical_parameter_bundle"]["transverse_period_exact"]
    ):
        raise ValueError("reference period mismatch")
    return result


def sequence_records(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dynamics = config["dynamics"]
    records: list[dict[str, Any]] = []
    alignment_counts: dict[str, int] = {}
    global_max_h0: Fraction | None = None
    global_min_side0: Fraction | None = None
    global_max_aspect = Fraction(0, 1)
    global_min_volume_factor = Fraction(1, 1)

    for row_index, row in enumerate(config["configurations"]):
        axes: list[dict[str, Any]] = []
        h0_values: list[Fraction] = []
        minimum_sides: list[Fraction] = []
        dual_axis_count = 0
        for coordinate in COORDINATES:
            source_axis = row.get(coordinate)
            if type(source_axis) is not dict:
                raise ValueError(f"missing axis {coordinate} in row {row_index}")
            axis, h0, minimum_side0, dual_count = axis_record(coordinate, source_axis, dynamics)
            axes.append(axis)
            h0_values.append(h0)
            minimum_sides.append(minimum_side0)
            dual_axis_count += dual_count
            alignment = axis["alignment"]
            alignment_counts[alignment] = alignment_counts.get(alignment, 0) + 1

        source_sizes = [row[coordinate]["size"] for coordinate in COORDINATES]
        if row.get("shape") != source_sizes:
            raise ValueError(f"shape/axis mismatch in row {row_index}")
        expected_states = source_sizes[0] * source_sizes[1] * source_sizes[2]
        if row.get("expected_states") != expected_states:
            raise ValueError(f"expected-state mismatch in row {row_index}")

        row_h0 = max(h0_values)
        row_min_side0 = min(minimum_sides)
        row_aspect = row_h0 / row_min_side0
        volume_factor = Fraction(1, 2**dual_axis_count)
        global_max_h0 = row_h0 if global_max_h0 is None else max(global_max_h0, row_h0)
        global_min_side0 = (
            row_min_side0 if global_min_side0 is None else min(global_min_side0, row_min_side0)
        )
        global_max_aspect = max(global_max_aspect, row_aspect)
        global_min_volume_factor = min(global_min_volume_factor, volume_factor)

        source_row_bytes = canonical_bytes(row)
        records.append(
            {
                "anchor_expected_states": expected_states,
                "anchor_geometry_exactly_reproduced_at_n0": True,
                "anchor_shape": source_sizes,
                "axes": axes,
                "fixed_box_and_alignment_at_every_n": True,
                "label": row["label"],
                "maximum_axis_spacing_at_n": "row_max_h0_exact/2^n",
                "minimum_tensor_volume_factor": exact_text(volume_factor),
                "physical_parameter_bundle_id": "encounter_control_free_physics_v2",
                "purpose": row["purpose"],
                "refinement_index_domain": "N_0",
                "row_cartesian_side_aspect_bound_exact": exact_text(row_aspect),
                "row_max_h0_exact": exact_text(row_h0),
                "sequence_id": (f"encounter_c1_joint_refinement_v2:{row_index}:{row['label']}"),
                "source_row_canonical_sha256": sha256_bytes(source_row_bytes),
                "source_row_index": row_index,
                "state_count_formula": ("product_over_axes_of_size(n); virtual definition only"),
            }
        )

    if global_max_h0 is None or global_min_side0 is None:
        raise ValueError("no configuration rows")
    uniformity = {
        "alignment_counts_across_36_axes": dict(sorted(alignment_counts.items())),
        "finite_family_cardinality": len(records),
        "global_cartesian_side_aspect_bound_exact": exact_text(global_max_aspect),
        "global_max_axis_spacing_at_n": "global_max_h0_exact/2^n",
        "global_max_h0_exact": exact_text(global_max_h0),
        "global_min_axis_cell_side_at_n": "global_min_side_h0_exact/2^n",
        "global_min_side_h0_exact": exact_text(global_min_side0),
        "global_min_tensor_volume_factor": exact_text(global_min_volume_factor),
        "maximum_axis_spacing_tends_to_zero_uniformly_over_12": True,
        "periodic_geometry_metric": "torus_metric_not_storage_segment_length",
        "shape_regularity_uniform_over_12_and_n": True,
        "uniformity_scope": "exactly_the_12_declared_fixed_box_families_only",
    }
    return records, uniformity


def build_payload() -> dict[str, Any]:
    _raw, sources = checked_sources()
    validate_source_semantics(sources)
    config = sources["configuration_family"]
    reference = sources["reference_density"]
    formula = sources["ideal_formula"]
    factorization = sources["factorization"]
    records, uniformity = sequence_records(config)

    source_inventory = {
        role: {"path": relative, "sha256": digest}
        for role, (relative, digest) in sorted(SOURCES.items())
    }
    claims = {
        "box_exhaustion_complete": False,
        "complete_C0": False,
        "complete_C1": False,
        "complete_C2": False,
        "complete_C3": False,
        "concrete_control_specific_killing_constructed": False,
        "control_values_present": False,
        "continuum_root_margin_certified": False,
        "F0_complete": False,
        "F1_complete": False,
        "fixed_row_anti_vacuity_policy_retrospectively_seals_successor": False,
        "positive_budget_present": False,
        "production_n0_correlated_containment_receipt_present": False,
        "production_raw_acceptance": False,
        "production_same_member_bridge_accepted": False,
        "quantitative_cut_cell_or_evaluator_rate_proved": False,
        "release_eligible": False,
        "submission_eligible": False,
        "uniform_operator_or_mosco_constants_proved_for_12_families": False,
    }
    return {
        "anti_vacuity_and_production_boundary": {
            "current_policy_predecessor_order_independently_sealed": False,
            "fixed_row_member_spec_had_genuine_refinement_sequence": False,
            "geometric_n0_match_is_not_production_containment": True,
            "independent_correlated_n0_receipt_still_required": True,
            "marginal_interval_overlap_is_insufficient": True,
            "policy_can_retroactively_seal_this_successor": False,
        },
        "build_provenance": {
            "arithmetic": "python_stdlib_Fraction_exact_rational_only",
            "builder_path": str(HERE.relative_to(REPORT)),
            "builder_sha256": sha256_bytes(HERE.read_bytes()),
            "canonical_json": "utf8_ascii_subset_indent2_sort_keys_newline",
            "dense_tensor_allocation_used": False,
            "network_access_used": False,
            "project_module_imports_used": False,
        },
        "claim_boundary": claims,
        "established_scope": {
            "finite_twelve_family_geometric_uniformity_proved": True,
            "genuine_refinement_sequences_defined": True,
            "global_gauge_product_map_formulae_source_bound": True,
            "maximum_axis_spacing_limit_proved": True,
            "n0_configuration_geometry_anchor_exact": True,
            "physical_volume_killing_average_qualitative_route_proved": True,
            "sequence_count": 12,
            "shape_regularity_proved": True,
        },
        "ideal_gauge_product_map_route": {
            "exact_adjoint_map": formula["formulae"]["exact_adjoint_map"],
            "global_box_gauge": formula["formulae"]["global_gauge"],
            "global_reference_density": reference["normalization"]["reference_density"],
            "map_ratio": formula["formulae"]["map_ratio"],
            "mass_identity": ("sum_tensor_pi_h=box_mass_M_L by exact finite-product algebra"),
            "physical_cell_mass": formula["formulae"]["physical_cell_mass"],
            "production_binary64_centres_define_ideal_member": False,
            "tensor_gauged_mass": formula["formulae"]["tensor_gauged_mass"],
        },
        "joint_refinement_rule": {
            "cell_or_periodic_interval_count": "N(n)=size0*2^n",
            "cell_or_periodic_size": "size(n)=size0*2^n",
            "maximum_spacing": "max_axis_h(n)=max_axis_h0/2^n",
            "periodic_base_shift": "sigma(n)=0",
            "periodic_half_shift": "sigma(n)=h(n)/2",
            "sequence_index": "n in N_0",
            "vertex_interval_count": "N(n)=(size0-1)*2^n",
            "vertex_size": "size(n)=(size0-1)*2^n+1",
        },
        "physical_parameter_freeze": physical_parameter_freeze(config, reference),
        "physical_volume_killing_route": {
            "concrete_control_combination_present": False,
            "contact_average_formula": factorization["cell_average_formulae"]["contact_average"],
            "definition": "V_h_cell=physical_volume(cell)^-1*integral_cell_V_dx",
            "factorized_physical_volume_formula": factorization["cell_average_formulae"][
                "physical_volume_killing_average"
            ],
            "qualitative_conclusion": (
                "for each fixed bounded V, J_h(V_h)->V in L2(pi dx) "
                "and 0<=J_h(V_h)<=norm(V)_infinity"
            ),
            "reconstructed_multiplier": formula["formulae"]["reconstructed_killing_multiplier"],
            "weighted_pi_average_used": False,
        },
        "schema": SCHEMA,
        "sequence_count": len(records),
        "sequence_order": [record["label"] for record in records],
        "sequences": records,
        "source_inventory": source_inventory,
        "source_policy": {
            "allowed_source_roles": sorted(SOURCES),
            "concrete_control_or_budget_payload_opened": False,
            "embedded_paths_followed": False,
            "network_access_used": False,
            "production_raw_array_opened": False,
            "result_or_root_payload_opened": False,
            "source_count": len(SOURCES),
        },
        "status": STATUS,
        "uniform_geometry_certificate": uniformity,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    try:
        payload = build_payload()
        expected = canonical_bytes(payload)
        output = args.output.resolve()
        if args.check:
            actual = output.read_bytes()
            if actual != expected:
                raise ValueError(
                    f"artifact drift: {sha256_bytes(actual)} != {sha256_bytes(expected)}"
                )
            action = "checked"
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(expected)
            action = "wrote"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"HOLD_C1_REFINEMENT_V2_BUILD: {exc}", file=sys.stderr)
        return 1

    print(
        f"PASS_C1_REFINEMENT_V2_BUILD {action}={output} "
        f"sha256={sha256_bytes(expected)} sequences={payload['sequence_count']} "
        "genuine_refinement_sequences_defined=true complete_C1=false "
        "production_same_member_bridge_accepted=false release_eligible=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
