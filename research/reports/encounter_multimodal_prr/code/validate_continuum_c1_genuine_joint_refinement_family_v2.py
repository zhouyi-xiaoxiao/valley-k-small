#!/usr/bin/env python3
"""Independent verifier for the genuine joint refinement-family authority v2.

This module intentionally imports neither the builder nor any project module.
It independently parses the pinned sources, reconstructs all exact-rational
mesh data, and compares the complete canonical authority object.
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

SELF = Path(__file__).resolve()
REPORT_ROOT = SELF.parents[1]
DEFAULT_ARTIFACT = (
    REPORT_ROOT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
)
BUILDER_RELATIVE = "code/build_continuum_c1_genuine_joint_refinement_family_v2.py"

EXPECTED_SCHEMA = "encounter_continuum_c1_genuine_joint_refinement_family_v2"
EXPECTED_STATUS = (
    "FROZEN_SOURCE_BOUND_12_IDEAL_JOINT_REFINEMENT_SEQUENCES_DEFINED_"
    "PRODUCTION_ACCEPTANCE_C0_C1_C2_C3_RELEASE_FALSE"
)

PINNED: dict[str, tuple[str, str]] = {
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

JSON_ROLES = frozenset(
    {
        "configuration_family",
        "factorization",
        "fixed_row_anti_vacuity_policy",
        "fixed_row_member_spec",
        "ideal_formula",
        "reference_density",
    }
)
AXIS_ORDER = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
REFLECTING = frozenset(
    {
        "cell_centred_reflecting",
        "vertex_centred_reflecting_dual",
    }
)
PERIODIC = frozenset(
    {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    }
)
HEX_RE = re.compile(
    r"^(?P<sign>[+-]?)0x(?P<whole>[0-9a-f]+)"
    r"(?:\.(?P<fraction>[0-9a-f]*))?p(?P<power>[+-]?[0-9]+)$"
)
RATIONAL_RE = re.compile(r"-?[0-9]+/[1-9][0-9]*")


class VerificationError(ValueError):
    """A fail-closed authority validation error."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def forbidden_json_number(token: str) -> None:
    raise VerificationError(f"non-integer JSON number forbidden: {token}")


def reject_repeated_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise VerificationError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def decode_json(data: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=reject_repeated_keys,
            parse_float=forbidden_json_number,
            parse_constant=forbidden_json_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, VerificationError) as exc:
        raise VerificationError(f"strict JSON parse failed for {path}: {exc}") from exc
    if type(value) is not dict:
        raise VerificationError(f"top-level object required: {path}")
    if encode_canonical(value) != data:
        raise VerificationError(f"canonical JSON mismatch: {path}")
    return value


def from_hex(text: str) -> Fraction:
    match = HEX_RE.fullmatch(text.lower())
    if match is None:
        raise VerificationError(f"invalid hexadecimal rational: {text}")
    fractional = match.group("fraction") or ""
    integer = int(match.group("whole") + fractional, 16)
    divisor = 16 ** len(fractional)
    power = int(match.group("power"))
    if power < 0:
        divisor *= 2 ** (-power)
    else:
        integer *= 2**power
    if match.group("sign") == "-":
        integer = -integer
    return Fraction(integer, divisor)


def from_rational(text: Any) -> Fraction:
    if type(text) is not str or RATIONAL_RE.fullmatch(text) is None:
        raise VerificationError(f"invalid rational string: {text!r}")
    numerator, denominator = text.split("/", 1)
    value = Fraction(int(numerator), int(denominator))
    if rational(value) != text:
        raise VerificationError(f"rational is not reduced: {text}")
    return value


def rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def load_authorities() -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_digest) in PINNED.items():
        path = REPORT_ROOT / relative
        data = path.read_bytes()
        if digest(data) != expected_digest:
            raise VerificationError(f"pinned source hash drift: {role}")
        if role in JSON_ROLES:
            parsed[role] = decode_json(data, path)
    return parsed


def verify_authority_scope(authorities: dict[str, dict[str, Any]]) -> None:
    configuration = authorities["configuration_family"]
    if (
        configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or configuration.get("configuration_count") != 12
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
        or configuration.get("authorizes_scientific_execution") is not False
    ):
        raise VerificationError("configuration-family source scope drift")
    rows = configuration.get("configurations")
    order = configuration.get("configuration_order")
    if (
        type(rows) is not list
        or type(order) is not list
        or [row.get("label") for row in rows] != order
    ):
        raise VerificationError("configuration-family order drift")

    expected_schemas = {
        "reference_density": "encounter_continuum_c1_reference_density_source_v1",
        "ideal_formula": "encounter_continuum_c1_ideal_formula_source_v1",
        "factorization": "encounter_continuum_c1_factorization_source_v1",
        "fixed_row_anti_vacuity_policy": (
            "encounter_continuum_c1_c2_fixed_row_anti_vacuity_policy_v1"
        ),
        "fixed_row_member_spec": ("encounter_continuum_c1_c2_fixed_row_member_spec_v1"),
    }
    for role, schema in expected_schemas.items():
        source = authorities[role]
        if source.get("schema") != schema:
            raise VerificationError(f"source schema drift: {role}")
        boundary = source.get("claim_boundary")
        if (
            type(boundary) is not dict
            or not boundary
            or any(value is not False for value in boundary.values())
        ):
            raise VerificationError(f"source promotion boundary drift: {role}")

    policy_boundary = authorities["fixed_row_anti_vacuity_policy"]["claim_boundary"]
    if policy_boundary["policy_predecessor_order_independently_sealed"] is not False:
        raise VerificationError("policy predecessor-order drift")
    member_boundary = authorities["fixed_row_member_spec"]["claim_boundary"]
    if member_boundary["genuine_refinement_sequence_present"] is not False:
        raise VerificationError("historical member-spec refinement drift")

    dynamics = configuration["dynamics"]
    reference_bundle = authorities["reference_density"]["physical_parameter_bundle"]
    for name in (
        "ou_mean_binary64_hex",
        "ou_stiffness_binary64_hex",
        "particle_diffusion_binary64_hex",
        "transverse_period_exact",
    ):
        if dynamics[name] != reference_bundle[name]:
            raise VerificationError(f"parameter cross-source mismatch: {name}")


def expected_axis(
    coordinate: str,
    raw_axis: dict[str, Any],
    dynamics: dict[str, Any],
) -> tuple[dict[str, Any], Fraction, Fraction, int]:
    alignment = raw_axis.get("alignment")
    size = raw_axis.get("size")
    if type(size) is not int or size < 2 or type(alignment) is not str:
        raise VerificationError(f"bad anchor axis: {coordinate}")

    if alignment in REFLECTING:
        lower_hex = raw_axis.get("lower_binary64_hex")
        upper_hex = raw_axis.get("upper_binary64_hex")
        if type(lower_hex) is not str or type(upper_hex) is not str:
            raise VerificationError(f"missing reflecting endpoints: {coordinate}")
        lower = from_hex(lower_hex)
        upper = from_hex(upper_hex)
        if lower >= upper:
            raise VerificationError(f"nonpositive reflecting width: {coordinate}")
        width = upper - lower
        vertex = alignment == "vertex_centred_reflecting_dual"
        intervals = size - 1 if vertex else size
        spacing = width / intervals
        factor = Fraction(1, 2) if vertex else Fraction(1, 1)
        expected = {
            "alignment": alignment,
            "anchor_interval_count": intervals,
            "anchor_size": size,
            "cell_rule": (
                "dual endpoints have h(n)/2; interior dual cells have h(n)"
                if vertex
                else "all control volumes have length h(n)"
            ),
            "coordinate": coordinate,
            "domain": {
                "lower_binary64_hex": lower_hex,
                "lower_exact": rational(lower),
                "upper_binary64_hex": upper_hex,
                "upper_exact": rational(upper),
                "width_exact": rational(width),
            },
            "interval_count_formula": (
                "interval_count(n)=(size0-1)*2^n" if vertex else "interval_count(n)=size0*2^n"
            ),
            "maximum_cell_side_at_n": "h0_exact/2^n",
            "minimum_axis_volume_factor": rational(factor),
            "refinement_index_domain": "N_0",
            "size_formula": ("size(n)=(size0-1)*2^n+1" if vertex else "size(n)=size0*2^n"),
            "spacing_formula": "h(n)=h0_exact/2^n",
            "spacing_h0_exact": rational(spacing),
        }
        return expected, spacing, spacing * factor, int(vertex)

    if alignment not in PERIODIC:
        raise VerificationError(f"unknown alignment: {alignment}")
    start = from_rational(dynamics["transverse_domain_start_exact"])
    period = from_rational(dynamics["transverse_period_exact"])
    spacing = period / size
    shift = from_rational(raw_axis.get("periodic_shift_exact"))
    half_shift = alignment == "cell_centred_periodic_half_shift"
    required_shift = spacing / 2 if half_shift else Fraction(0)
    if shift != required_shift:
        raise VerificationError(f"periodic n=0 shift mismatch: {coordinate}")
    expected = {
        "alignment": alignment,
        "anchor_interval_count": size,
        "anchor_size": size,
        "cell_rule": ("uniform torus cells; a seam crossing is stored as two ordered segments"),
        "coordinate": coordinate,
        "domain": {
            "period_exact": rational(period),
            "start_exact": rational(start),
        },
        "interval_count_formula": "interval_count(n)=size0*2^n",
        "maximum_cell_side_at_n": "h0_exact/2^n",
        "minimum_axis_volume_factor": "1/1",
        "periodic_shift_at_n_formula": ("sigma(n)=h(n)/2" if half_shift else "sigma(n)=0"),
        "periodic_shift_n0_exact": rational(shift),
        "refinement_index_domain": "N_0",
        "size_formula": "size(n)=size0*2^n",
        "spacing_formula": "h(n)=h0_exact/2^n",
        "spacing_h0_exact": rational(spacing),
    }
    return expected, spacing, spacing, 0


def expected_sequences(
    configuration: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sequences: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    family_max: Fraction | None = None
    family_min: Fraction | None = None
    largest_aspect = Fraction(0)
    smallest_volume_factor = Fraction(1)

    for index, source_row in enumerate(configuration["configurations"]):
        expected_axes: list[dict[str, Any]] = []
        spacings: list[Fraction] = []
        minimum_sides: list[Fraction] = []
        dual_axes = 0
        for coordinate in AXIS_ORDER:
            raw_axis = source_row.get(coordinate)
            if type(raw_axis) is not dict:
                raise VerificationError(f"row {index} missing {coordinate}")
            axis, spacing, minimum_side, dual = expected_axis(
                coordinate, raw_axis, configuration["dynamics"]
            )
            expected_axes.append(axis)
            spacings.append(spacing)
            minimum_sides.append(minimum_side)
            dual_axes += dual
            alignment = axis["alignment"]
            counts[alignment] = counts.get(alignment, 0) + 1

        sizes = [source_row[axis]["size"] for axis in AXIS_ORDER]
        expected_states = sizes[0] * sizes[1] * sizes[2]
        if source_row.get("shape") != sizes:
            raise VerificationError(f"anchor shape mismatch: row {index}")
        if source_row.get("expected_states") != expected_states:
            raise VerificationError(f"anchor state-count mismatch: row {index}")

        maximum = max(spacings)
        minimum = min(minimum_sides)
        aspect = maximum / minimum
        volume_factor = Fraction(1, 2**dual_axes)
        family_max = maximum if family_max is None else max(family_max, maximum)
        family_min = minimum if family_min is None else min(family_min, minimum)
        largest_aspect = max(largest_aspect, aspect)
        smallest_volume_factor = min(smallest_volume_factor, volume_factor)

        sequences.append(
            {
                "anchor_expected_states": expected_states,
                "anchor_geometry_exactly_reproduced_at_n0": True,
                "anchor_shape": sizes,
                "axes": expected_axes,
                "fixed_box_and_alignment_at_every_n": True,
                "label": source_row["label"],
                "maximum_axis_spacing_at_n": "row_max_h0_exact/2^n",
                "minimum_tensor_volume_factor": rational(volume_factor),
                "physical_parameter_bundle_id": "encounter_control_free_physics_v2",
                "purpose": source_row["purpose"],
                "refinement_index_domain": "N_0",
                "row_cartesian_side_aspect_bound_exact": rational(aspect),
                "row_max_h0_exact": rational(maximum),
                "sequence_id": (f"encounter_c1_joint_refinement_v2:{index}:{source_row['label']}"),
                "source_row_canonical_sha256": digest(encode_canonical(source_row)),
                "source_row_index": index,
                "state_count_formula": ("product_over_axes_of_size(n); virtual definition only"),
            }
        )

    if family_max is None or family_min is None:
        raise VerificationError("empty configuration family")
    uniform = {
        "alignment_counts_across_36_axes": dict(sorted(counts.items())),
        "finite_family_cardinality": len(sequences),
        "global_cartesian_side_aspect_bound_exact": rational(largest_aspect),
        "global_max_axis_spacing_at_n": "global_max_h0_exact/2^n",
        "global_max_h0_exact": rational(family_max),
        "global_min_axis_cell_side_at_n": "global_min_side_h0_exact/2^n",
        "global_min_side_h0_exact": rational(family_min),
        "global_min_tensor_volume_factor": rational(smallest_volume_factor),
        "maximum_axis_spacing_tends_to_zero_uniformly_over_12": True,
        "periodic_geometry_metric": "torus_metric_not_storage_segment_length",
        "shape_regularity_uniform_over_12_and_n": True,
        "uniformity_scope": "exactly_the_12_declared_fixed_box_families_only",
    }
    return sequences, uniform


def expected_parameters(
    configuration: dict[str, Any],
    reference: dict[str, Any],
) -> dict[str, Any]:
    dynamics = configuration["dynamics"]
    expected = {
        "bundle_id": "encounter_control_free_physics_v2",
        "fixed_at_every_level_of_all_twelve_sequences": True,
        "ou_mean_binary64_hex": dynamics["ou_mean_binary64_hex"],
        "ou_mean_exact": rational(from_hex(dynamics["ou_mean_binary64_hex"])),
        "ou_stiffness_binary64_hex": dynamics["ou_stiffness_binary64_hex"],
        "ou_stiffness_exact": rational(from_hex(dynamics["ou_stiffness_binary64_hex"])),
        "particle_diffusion_binary64_hex": dynamics["particle_diffusion_binary64_hex"],
        "particle_diffusion_exact": rational(from_hex(dynamics["particle_diffusion_binary64_hex"])),
        "physical_dimension": configuration["physical_dimension"],
        "quotient_dimension": configuration["quotient_dimension"],
        "transverse_domain_start_exact": rational(
            from_rational(dynamics["transverse_domain_start_exact"])
        ),
        "transverse_period_exact": rational(from_rational(dynamics["transverse_period_exact"])),
    }
    if (
        expected["transverse_period_exact"]
        != reference["physical_parameter_bundle"]["transverse_period_exact"]
    ):
        raise VerificationError("reference period mismatch")
    return expected


def reconstruct_expected() -> dict[str, Any]:
    sources = load_authorities()
    verify_authority_scope(sources)
    configuration = sources["configuration_family"]
    reference = sources["reference_density"]
    formula = sources["ideal_formula"]
    factorization = sources["factorization"]
    sequences, uniformity = expected_sequences(configuration)
    builder = REPORT_ROOT / BUILDER_RELATIVE

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
            "builder_path": BUILDER_RELATIVE,
            "builder_sha256": digest(builder.read_bytes()),
            "canonical_json": "utf8_ascii_subset_indent2_sort_keys_newline",
            "dense_tensor_allocation_used": False,
            "network_access_used": False,
            "project_module_imports_used": False,
        },
        "claim_boundary": {
            "F0_complete": False,
            "F1_complete": False,
            "box_exhaustion_complete": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "concrete_control_specific_killing_constructed": False,
            "continuum_root_margin_certified": False,
            "control_values_present": False,
            "fixed_row_anti_vacuity_policy_retrospectively_seals_successor": False,
            "positive_budget_present": False,
            "production_n0_correlated_containment_receipt_present": False,
            "production_raw_acceptance": False,
            "production_same_member_bridge_accepted": False,
            "quantitative_cut_cell_or_evaluator_rate_proved": False,
            "release_eligible": False,
            "submission_eligible": False,
            "uniform_operator_or_mosco_constants_proved_for_12_families": False,
        },
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
        "physical_parameter_freeze": expected_parameters(configuration, reference),
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
        "schema": EXPECTED_SCHEMA,
        "sequence_count": len(sequences),
        "sequence_order": [item["label"] for item in sequences],
        "sequences": sequences,
        "source_inventory": {
            role: {"path": relative, "sha256": expected_digest}
            for role, (relative, expected_digest) in sorted(PINNED.items())
        },
        "source_policy": {
            "allowed_source_roles": sorted(PINNED),
            "concrete_control_or_budget_payload_opened": False,
            "embedded_paths_followed": False,
            "network_access_used": False,
            "production_raw_array_opened": False,
            "result_or_root_payload_opened": False,
            "source_count": len(PINNED),
        },
        "status": EXPECTED_STATUS,
        "uniform_geometry_certificate": uniformity,
    }


def validate_artifact(path: Path) -> dict[str, Any]:
    artifact_bytes = path.read_bytes()
    candidate = decode_json(artifact_bytes, path)
    expected = reconstruct_expected()
    if candidate != expected:
        candidate_keys = set(candidate)
        expected_keys = set(expected)
        if candidate_keys != expected_keys:
            detail = (
                f"top-level keys differ missing={sorted(expected_keys - candidate_keys)} "
                f"extra={sorted(candidate_keys - expected_keys)}"
            )
        else:
            differing = sorted(key for key in expected if candidate.get(key) != expected[key])
            detail = f"semantic sections differ: {differing}"
        raise VerificationError(detail)
    return candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args(argv)
    artifact = args.artifact.resolve()
    try:
        payload = validate_artifact(artifact)
        artifact_sha = digest(artifact.read_bytes())
    except (OSError, KeyError, TypeError, VerificationError) as exc:
        print(f"HOLD_C1_REFINEMENT_V2_VERIFY: {exc}", file=sys.stderr)
        return 1
    print(
        f"PASS_C1_REFINEMENT_V2_VERIFY artifact={artifact} "
        f"sha256={artifact_sha} sequences={payload['sequence_count']} "
        "genuine_refinement_sequences_defined=true complete_C1=false "
        "production_n0_correlated_containment_receipt_present=false "
        "release_eligible=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
