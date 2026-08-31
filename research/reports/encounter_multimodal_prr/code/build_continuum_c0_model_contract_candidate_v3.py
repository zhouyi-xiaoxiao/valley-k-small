#!/usr/bin/env python3
"""Build the versioned C0-v3 well-definedness repair over immutable C0-v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import build_continuum_c0_model_contract_candidate_v2 as base

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v3.json"
BASE_RELATIVE = Path("artifacts/data/continuum_c0_model_contract_candidate_v2.json")
BASE_SHA256 = "688ec0416e414737705631852bb5ecf44530c5fe93e3ca95f3dfdbe8807ead7e"
PRECONDITIONS_RELATIVE = Path(
    "artifacts/data/continuum_c0_measure_partition_preconditions_v1.json"
)
PRECONDITIONS_SHA256 = "652e0b1a1528eebff2f78ae4aae7854412da03ad8d5ad33887c77a072d439d15"
SCHEMA = "encounter_continuum_c0_model_contract_candidate_v3"
STATUS = "HOLD_C0_V3_CANDIDATE_WELL_DEFINEDNESS_EXPLICIT_COMPLETE_C0_AND_GAUGE_BRIDGE_OPEN"
PASS_STATUS = "PASS_C0_V3_REPRODUCIBLE_LAYER_BUILD_COMPLETE_C0_FALSE"


def _load_inputs(*, report: Path = REPORT) -> tuple[bytes, dict[str, Any]]:
    base_bytes = base.read_relative_snapshot(report, BASE_RELATIVE)
    if base.sha256_bytes(base_bytes) != BASE_SHA256:
        raise base.BuildHold("immutable C0-v2 base hash mismatch")
    if base.build_bytes(report=report) != base_bytes:
        raise base.BuildHold("C0-v2 base no longer reproduces from its frozen sources")
    precondition_bytes = base.read_relative_snapshot(report, PRECONDITIONS_RELATIVE)
    if base.sha256_bytes(precondition_bytes) != PRECONDITIONS_SHA256:
        raise base.BuildHold("well-definedness precondition source hash mismatch")
    preconditions = base.parse_source_json(precondition_bytes)
    base._scan_result_bearing(preconditions)
    if precondition_bytes != base.canonical_json_bytes(preconditions):
        raise base.BuildHold("well-definedness precondition source is not canonical")
    if set(preconditions) != {
        "configuration_geometry_preconditions",
        "continuum_measure_preconditions",
        "discrete_mass_preconditions",
        "map_well_definedness_consequences",
        "schema",
        "status",
        "verification_boundary",
    }:
        raise base.BuildHold("well-definedness precondition schema mismatch")
    return base_bytes, preconditions


def build_payload(*, report: Path = REPORT) -> dict[str, Any]:
    _base_bytes, preconditions = _load_inputs(report=report)
    return {
        "base_contract": {
            "path": str(BASE_RELATIVE),
            "semantic_verification_required": True,
            "sha256": BASE_SHA256,
        },
        "claim_boundary": {
            "complete_c0_independently_accepted": False,
            "configuration_geometry_checked_for_every_declared_configuration": True,
            "control_values_committed_for_c0": False,
            "map_and_gauge_well_definedness_preconditions_explicit": True,
            "positive_budget_scientific_values_read": False,
            "production_raw_to_gauged_bridge_proved": False,
            "raw_mass_positivity_is_ideal_model_precondition_only": True,
            "release_eligible": False,
        },
        "frozen_sources": {
            "base_contract": {
                "path": str(BASE_RELATIVE),
                "sha256": BASE_SHA256,
            },
            "measure_partition_preconditions": {
                "path": str(PRECONDITIONS_RELATIVE),
                "sha256": PRECONDITIONS_SHA256,
            },
        },
        "measure_and_partition_preconditions": preconditions,
        "schema": SCHEMA,
        "source_policy": {
            "base_v2_verifier_must_pass": True,
            "embedded_paths_followed": False,
            "positive_budget_design_note_opened": False,
            "scratch_control_or_result_payload_opened": False,
            "v2_bytes_mutated": False,
        },
        "status": STATUS,
        "supersession": {
            "finding": (
                "v2_did_not_explicitly_freeze_partition_and_positive_mass_preconditions"
            ),
            "repair": "versioned_wrapper_adds_machine_checked_well_definedness_preconditions",
            "v2_retained_as_immutable_base": True,
        },
    }


def build_bytes(*, report: Path = REPORT) -> bytes:
    return base.canonical_json_bytes(build_payload(report=report))


def _receipt(payload: bytes, action: str) -> dict[str, Any]:
    return {
        "action": action,
        "base_contract_sha256": BASE_SHA256,
        "complete_c0": False,
        "contract_sha256": base.sha256_bytes(payload),
        "opened_auxiliary_paths": [
            str(BASE_RELATIVE),
            str(base.V1_PATH.relative_to(REPORT)),
        ],
        "opened_source_paths": [
            str(PRECONDITIONS_RELATIVE),
            *[base.FROZEN_SOURCES[role]["path"] for role in sorted(base.FROZEN_SOURCES)],
        ],
        "positive_budget_scientific_values_read": False,
        "production_raw_to_gauged_bridge_proved": False,
        "release_eligible": False,
        "scratch_control_or_result_payload_read": False,
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
                raise base.BuildHold("C0-v3 output exists; never overwrite, use --check")
            base._exclusive_publish(OUTPUT, expected)
        observed = base.read_regular_snapshot(OUTPUT)
        if observed != expected:
            raise base.BuildHold("published C0-v3 bytes differ from deterministic build")
        if base.sha256_bytes(base.read_relative_snapshot(REPORT, BASE_RELATIVE)) != BASE_SHA256:
            raise base.BuildHold("C0-v2 base changed during C0-v3 build")
    except (base.BuildHold, FileExistsError, OSError) as error:
        print(json.dumps({"status": "HOLD_C0_V3_BUILD", "message": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(_receipt(observed, action), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
