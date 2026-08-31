#!/usr/bin/env python3
"""Independent verifier for the C0-v3 well-definedness repair layer."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import validate_continuum_c0_model_contract_candidate_v2 as base

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v3.json"
BASE_RELATIVE = Path("artifacts/data/continuum_c0_model_contract_candidate_v2.json")
BASE_SHA256 = "688ec0416e414737705631852bb5ecf44530c5fe93e3ca95f3dfdbe8807ead7e"
PRECONDITIONS_RELATIVE = Path(
    "artifacts/data/continuum_c0_measure_partition_preconditions_v1.json"
)
PRECONDITIONS_SHA256 = "652e0b1a1528eebff2f78ae4aae7854412da03ad8d5ad33887c77a072d439d15"
EXPECTED_CONTRACT_SHA256 = "5457f391ccfb59c5415302a4776219641305914b63c6933b222541cae746f239"

HOLD_ENCODING = "HOLD_C0_V3_ENCODING"
HOLD_SCHEMA = "HOLD_C0_V3_SCHEMA"
HOLD_BASE = "HOLD_C0_V3_BASE_CONTRACT"
HOLD_PRECONDITIONS = "HOLD_C0_V3_PRECONDITIONS"
HOLD_GEOMETRY = "HOLD_C0_V3_GEOMETRY"
HOLD_CLAIMS = "HOLD_C0_V3_CLAIMS"
HOLD_RESULT_BLINDNESS = "HOLD_C0_V3_RESULT_BLINDNESS"
PASS_STATUS = "PASS_C0_V3_SEMANTIC_AND_WELL_DEFINEDNESS_VERIFICATION_COMPLETE_C0_FALSE"


class C0V3Hold(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


EXPECTED_PRECONDITIONS = {
    "configuration_geometry_preconditions": {
        "actual_tensor_control_volumes_are_measurable": True,
        "actual_tensor_control_volumes_cover_Omega_L_up_to_null_sets": True,
        "actual_tensor_control_volumes_pairwise_disjoint_up_to_null_sets": True,
        "cell_centred_nonperiodic_cells_partition_each_interval": True,
        "declared_configuration_count": 12,
        "each_control_volume_has_finite_positive_physical_volume": True,
        "periodic_cells_include_wrapped_segments_and_partition_the_torus": True,
        "vertex_dual_nonperiodic_cells_include_positive_endpoint_half_volumes": True,
    },
    "continuum_measure_preconditions": {
        "M_L_finite_and_strictly_positive": True,
        "M_i_pi_formula": "M_i_pi=integral_C_i_pi_dx",
        "M_i_pi_strictly_positive_for_every_declared_cell": True,
        "pi_finite_and_strictly_positive_on_every_fixed_box": True,
    },
    "discrete_mass_preconditions": {
        "free_graph_connected": True,
        "g_h_L_finite_and_strictly_positive": True,
        "g_h_L_formula": "g_h_L=M_L/sum_i_tilde_pi_h_i",
        "pi_h_i_formula": "pi_h_i=g_h_L*tilde_pi_h_i",
        "pi_h_i_strictly_positive": True,
        "sum_i_tilde_pi_h_i_finite_and_strictly_positive": True,
        "tilde_pi_h_i_strictly_positive_for_every_declared_cell": True,
    },
    "map_well_definedness_consequences": {
        "A_h_denominator_nonzero": True,
        "H_h_is_a_positive_weight_Hilbert_space": True,
        "P_h_denominator_nonzero": True,
        "conditional_expectation_E_h_well_defined": True,
        "exact_adjoint_identity_well_defined": True,
        "rho_i_finite_and_strictly_positive": True,
    },
    "schema": "encounter_continuum_c0_measure_partition_preconditions_v1",
    "status": "FROZEN_C0_WELL_DEFINEDNESS_PRECONDITIONS_ONLY_COMPLETE_C0_FALSE",
    "verification_boundary": {
        "complete_c0": False,
        "geometry_checked_for_every_declared_configuration": True,
        "positive_budget_scientific_values_read": False,
        "production_raw_to_gauged_bridge_proved": False,
        "raw_mass_positivity_is_an_ideal_model_precondition_not_a_production_interval_claim": True,
        "release_eligible": False,
    },
}

EXPECTED_CLAIMS = {
    "complete_c0_independently_accepted": False,
    "configuration_geometry_checked_for_every_declared_configuration": True,
    "control_values_committed_for_c0": False,
    "map_and_gauge_well_definedness_preconditions_explicit": True,
    "positive_budget_scientific_values_read": False,
    "production_raw_to_gauged_bridge_proved": False,
    "raw_mass_positivity_is_ideal_model_precondition_only": True,
    "release_eligible": False,
}

EXPECTED_CONTRACT = {
    "base_contract": {
        "path": str(BASE_RELATIVE),
        "semantic_verification_required": True,
        "sha256": BASE_SHA256,
    },
    "claim_boundary": EXPECTED_CLAIMS,
    "frozen_sources": {
        "base_contract": {"path": str(BASE_RELATIVE), "sha256": BASE_SHA256},
        "measure_partition_preconditions": {
            "path": str(PRECONDITIONS_RELATIVE),
            "sha256": PRECONDITIONS_SHA256,
        },
    },
    "measure_and_partition_preconditions": EXPECTED_PRECONDITIONS,
    "schema": "encounter_continuum_c0_model_contract_candidate_v3",
    "source_policy": {
        "base_v2_verifier_must_pass": True,
        "embedded_paths_followed": False,
        "positive_budget_design_note_opened": False,
        "scratch_control_or_result_payload_opened": False,
        "v2_bytes_mutated": False,
    },
    "status": (
        "HOLD_C0_V3_CANDIDATE_WELL_DEFINEDNESS_EXPLICIT_"
        "COMPLETE_C0_AND_GAUGE_BRIDGE_OPEN"
    ),
    "supersession": {
        "finding": "v2_did_not_explicitly_freeze_partition_and_positive_mass_preconditions",
        "repair": "versioned_wrapper_adds_machine_checked_well_definedness_preconditions",
        "v2_retained_as_immutable_base": True,
    },
}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_exact(observed: Any, expected: Any, code: str, label: str) -> None:
    if observed != expected or type(observed) is not type(expected):
        raise C0V3Hold(code, f"{label} mismatch")


def _parse_candidate(payload: bytes) -> dict[str, Any]:
    try:
        return base._parse_json(payload, code=HOLD_ENCODING, canonical=True)
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_ENCODING, str(error)) from error


def _read_relative(report: Path, relative: Path, code: str) -> bytes:
    try:
        return base.read_relative_snapshot(report, relative, code=code)
    except base.C0V2Hold as error:
        raise C0V3Hold(code, str(error)) from error


def _nonperiodic_segments(record: dict[str, Any]) -> tuple[tuple[Fraction, Fraction], ...]:
    try:
        lower = base._fraction_from_hex(
            record.get("lower_binary64_hex"), HOLD_GEOMETRY, "lower"
        )
        upper = base._fraction_from_hex(
            record.get("upper_binary64_hex"), HOLD_GEOMETRY, "upper"
        )
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_GEOMETRY, str(error)) from error
    size = record.get("size")
    alignment = record.get("alignment")
    if type(size) is not int or size <= 0 or lower >= upper:
        raise C0V3Hold(HOLD_GEOMETRY, "invalid nonperiodic axis geometry")
    if alignment == "cell_centred_reflecting":
        step = (upper - lower) / size
        boundaries = [lower + index * step for index in range(size + 1)]
    elif alignment == "vertex_centred_reflecting_dual":
        if size < 2:
            raise C0V3Hold(HOLD_GEOMETRY, "vertex-dual axis needs at least two vertices")
        step = (upper - lower) / (size - 1)
        vertices = [lower + index * step for index in range(size)]
        boundaries = [lower]
        boundaries.extend((vertices[index] + vertices[index + 1]) / 2 for index in range(size - 1))
        boundaries.append(upper)
    else:
        raise C0V3Hold(HOLD_GEOMETRY, "unsupported nonperiodic alignment")
    segments = tuple(zip(boundaries, boundaries[1:]))
    if (
        len(segments) != size
        or segments[0][0] != lower
        or segments[-1][1] != upper
        or any(not left < right for left, right in segments)
        or any(a_right != b_left for (_, a_right), (b_left, _) in zip(segments, segments[1:]))
    ):
        raise C0V3Hold(HOLD_GEOMETRY, "nonperiodic control volumes do not partition interval")
    return segments


def _validate_all_geometry(family: dict[str, Any]) -> dict[str, int | bool]:
    rows = family.get("configurations")
    dynamics = family.get("dynamics")
    if type(rows) is not list or len(rows) != 12 or type(dynamics) is not dict:
        raise C0V3Hold(HOLD_GEOMETRY, "configuration family is incomplete")
    try:
        torus_start = base._fraction(
            dynamics.get("transverse_domain_start_exact"), HOLD_GEOMETRY, "torus start"
        )
        torus_period = base._fraction(
            dynamics.get("transverse_period_exact"), HOLD_GEOMETRY, "torus period"
        )
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_GEOMETRY, str(error)) from error
    axes_checked = 0
    total_tensor_cells = 0
    endpoint_half_volume_rows = 0
    wrapped_periodic_rows = 0
    for row in rows:
        if type(row) is not dict:
            raise C0V3Hold(HOLD_GEOMETRY, "configuration row is not an object")
        midpoint_record = row.get("midpoint")
        relative_record = row.get("relative_parallel")
        periodic = row.get("relative_perpendicular")
        if not all(type(record) is dict for record in (midpoint_record, relative_record, periodic)):
            raise C0V3Hold(HOLD_GEOMETRY, "configuration axis record is not an object")
        midpoint = _nonperiodic_segments(midpoint_record)
        relative = _nonperiodic_segments(relative_record)
        axes_checked += 2
        if midpoint_record["alignment"] == "vertex_centred_reflecting_dual":
            endpoint_half_volume_rows += 1
        if relative_record["alignment"] == "vertex_centred_reflecting_dual":
            endpoint_half_volume_rows += 1
        size = periodic.get("size")
        if type(size) is not int or size <= 0:
            raise C0V3Hold(HOLD_GEOMETRY, "invalid periodic axis size")
        try:
            shift = base._fraction(
                periodic.get("periodic_shift_exact"), HOLD_GEOMETRY, "shift"
            )
        except base.C0V2Hold as error:
            raise C0V3Hold(HOLD_GEOMETRY, str(error)) from error
        try:
            periodic_segments = base._periodic_cell_segments(
                torus_start,
                torus_period,
                size,
                shift,
            )
        except base.C0V2Hold as error:
            raise C0V3Hold(HOLD_GEOMETRY, str(error)) from error
        axes_checked += 1
        if len(periodic_segments) > size:
            wrapped_periodic_rows += 1
        shape = row.get("shape")
        if type(shape) is not list or any(type(entry) is not int or entry <= 0 for entry in shape):
            raise C0V3Hold(HOLD_GEOMETRY, "invalid tensor shape")
        tensor_cells = len(midpoint) * len(relative) * size
        if tensor_cells != row.get("expected_states") or tensor_cells != math.prod(shape):
            raise C0V3Hold(HOLD_GEOMETRY, "tensor cell count mismatch")
        total_tensor_cells += tensor_cells
    if total_tensor_cells != family.get("total_state_workload"):
        raise C0V3Hold(HOLD_GEOMETRY, "total tensor workload mismatch")
    return {
        "axis_partitions_checked": axes_checked,
        "configuration_count_checked": len(rows),
        "endpoint_half_volume_axes_checked": endpoint_half_volume_rows,
        "tensor_cells_accounted_for": total_tensor_cells,
        "wrapped_periodic_rows_represented": wrapped_periodic_rows,
        "all_declared_control_volumes_positive_and_partitioning": True,
    }


def verify_contract_bytes(payload: bytes, *, report: Path = REPORT) -> dict[str, Any]:
    contract = _parse_candidate(payload)
    try:
        base._scan_result_bearing(contract, code=HOLD_RESULT_BLINDNESS)
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_RESULT_BLINDNESS, str(error)) from error
    if set(contract) != set(EXPECTED_CONTRACT):
        raise C0V3Hold(HOLD_SCHEMA, "C0-v3 top-level key set mismatch")
    _require_exact(
        contract.get("base_contract"),
        EXPECTED_CONTRACT["base_contract"],
        HOLD_BASE,
        "base contract binding",
    )
    _require_exact(
        contract.get("claim_boundary"), EXPECTED_CLAIMS, HOLD_CLAIMS, "claim boundary"
    )
    _require_exact(
        contract.get("measure_and_partition_preconditions"),
        EXPECTED_PRECONDITIONS,
        HOLD_PRECONDITIONS,
        "measure and partition preconditions",
    )
    frozen_sources = contract.get("frozen_sources")
    if type(frozen_sources) is not dict or set(frozen_sources) != {
        "base_contract",
        "measure_partition_preconditions",
    }:
        raise C0V3Hold(HOLD_SCHEMA, "frozen source role set mismatch")
    _require_exact(
        frozen_sources.get("base_contract"),
        EXPECTED_CONTRACT["frozen_sources"]["base_contract"],
        HOLD_BASE,
        "frozen base binding",
    )
    _require_exact(
        frozen_sources.get("measure_partition_preconditions"),
        EXPECTED_CONTRACT["frozen_sources"]["measure_partition_preconditions"],
        HOLD_PRECONDITIONS,
        "frozen precondition binding",
    )
    for field in ("schema", "source_policy", "status", "supersession"):
        _require_exact(
            contract.get(field), EXPECTED_CONTRACT[field], HOLD_SCHEMA, field.replace("_", " ")
        )

    base_bytes = _read_relative(report, BASE_RELATIVE, HOLD_BASE)
    if _sha256(base_bytes) != BASE_SHA256:
        raise C0V3Hold(HOLD_BASE, "C0-v2 base hash mismatch")
    try:
        base_receipt = base.verify_contract_bytes(base_bytes, report=report)
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_BASE, str(error)) from error
    if base_receipt.get("status") != base.PASS_STATUS:
        raise C0V3Hold(HOLD_BASE, "C0-v2 semantic verifier did not pass")

    precondition_bytes = _read_relative(report, PRECONDITIONS_RELATIVE, HOLD_PRECONDITIONS)
    if _sha256(precondition_bytes) != PRECONDITIONS_SHA256:
        raise C0V3Hold(HOLD_PRECONDITIONS, "precondition source hash mismatch")
    try:
        preconditions = base._parse_json(
            precondition_bytes,
            code=HOLD_PRECONDITIONS,
            canonical=True,
        )
        base._scan_result_bearing(preconditions, code=HOLD_RESULT_BLINDNESS)
    except base.C0V2Hold as error:
        code = (
            HOLD_RESULT_BLINDNESS
            if error.code == HOLD_RESULT_BLINDNESS
            else HOLD_PRECONDITIONS
        )
        raise C0V3Hold(code, str(error)) from error
    _require_exact(preconditions, EXPECTED_PRECONDITIONS, HOLD_PRECONDITIONS, "preconditions")

    try:
        sources, source_hashes = base._load_sources(report)
    except base.C0V2Hold as error:
        raise C0V3Hold(HOLD_BASE, str(error)) from error
    geometry_receipt = _validate_all_geometry(sources["configuration_family"])
    if _sha256(payload) != EXPECTED_CONTRACT_SHA256:
        raise C0V3Hold(HOLD_SCHEMA, "C0-v3 candidate hash mismatch")
    return {
        "base_contract_sha256": _sha256(base_bytes),
        "base_verifier_status": base_receipt["status"],
        "complete_c0": False,
        "contract_sha256": _sha256(payload),
        "control_values_read": False,
        "geometry_receipt": geometry_receipt,
        "map_and_gauge_well_definedness_preconditions_explicit": True,
        "opened_auxiliary_paths": [str(BASE_RELATIVE), *base_receipt["opened_auxiliary_paths"]],
        "opened_source_paths": [
            str(PRECONDITIONS_RELATIVE),
            *base_receipt["opened_source_paths"],
        ],
        "positive_budget_scientific_values_read": False,
        "production_raw_to_gauged_bridge_proved": False,
        "release_eligible": False,
        "scratch_control_or_result_payload_read": False,
        "source_sha256s": {
            "measure_partition_preconditions": PRECONDITIONS_SHA256,
            **source_hashes,
        },
        "status": PASS_STATUS,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: validate_continuum_c0_model_contract_candidate_v3.py [contract.json]", file=sys.stderr)
        return 2
    path = DEFAULT_CONTRACT if not args else Path(args[0])
    try:
        payload = base.read_regular_snapshot(path, code=HOLD_ENCODING)
        receipt = verify_contract_bytes(payload)
    except (C0V3Hold, base.C0V2Hold) as error:
        code = error.code if hasattr(error, "code") else HOLD_ENCODING
        print(json.dumps({"status": code, "message": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
