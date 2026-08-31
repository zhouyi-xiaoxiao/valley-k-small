#!/usr/bin/env python3
"""Build the result-blind neutral symbolic-bridge contract fixture v1.

This is not the formal production symbolic candidate.  It opens exactly one
externally selected operation model, its three hash-pinned bootstrap sources,
one hash-pinned outer manifest, and one neutral payload source.  The four
exact-rational witnesses exercise algebra and provenance only.

``--check`` deliberately does not open the existing output: it validates the
six construction inputs and prints the expected fixture digest.  Artifact
currentness belongs to the independent validator and currentness gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OPERATION_MODEL = REPORT / "code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json"
DEFAULT_OUTPUT = REPORT / "artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json"

OPERATION_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_operation_model_v1"
MANIFEST_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_outer_manifest_v1"
SOURCE_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_source_v1"
OUTPUT_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_fixture_v1"
OUTPUT_STATUS = "PASS_NEUTRAL_SYMBOLIC_CONTRACT_FIXTURE_ONLY_PRODUCTION_CANDIDATE_NOT_MATERIALIZED"
OPERATION_STATUS = "NEUTRAL_OPERATION_MODEL_EXTERNALLY_PINNED_NO_PRODUCTION_ACCEPTANCE"
MANIFEST_STATUS = "NEUTRAL_OUTER_MANIFEST_ONLY_PRODUCTION_ROLE_SET_INCOMPLETE"
SOURCE_STATUS = "NEUTRAL_SYMBOLIC_CONTRACT_WITNESSES_ONLY_NO_PRODUCTION_NO_CONTROL_NO_BUDGET"
DESIGN_SHA256 = "d23c088f917832bb9d8078a046133556e8ee8547d8a062d3102a922881ba67e4"
NATIVE_RECORD_DOMAIN = b"encounter-source-native-record-v1\x00"

EXPECTED_ROLES = [
    "reference_density_source",
    "ideal_formula_source",
    "factorization_source",
    "configuration_source",
    "member_spec_manifest",
    "outward_method_registry_source",
    "anti_vacuity_policy_source",
    "raw_axis_enclosure_source",
    "stationary_integral_source",
    "killing_geometry_source",
    "symbolic_control_method_source",
]

EXPECTED_FORMULAE = {
    "common_flux": "kappa_e=mu_i*q_ij=mu_j*q_ji",
    "discrete_killing_diagonal": "k=B*V",
    "global_gauge": "G=M_L/(S_z*S_r*S_y)",
    "map_ratio": "rho=M_pi/pi_h",
    "physical_weight_identity": "M_pi*K=pi_h*V",
    "reconstructed_killed_multiplier": "B*K",
    "reconstructed_multiplier": "K=V/rho",
    "tensor_conductance": "c_e=G*kappa_e*product_other_axis_masses",
}

EXPECTED_SOURCE_CLAIMS = {
    "budget_present": False,
    "complete_C0": False,
    "complete_C1": False,
    "complete_C2": False,
    "complete_C3": False,
    "control_specific_killing_constructed": False,
    "exact_controls_present": False,
    "one_correlated_distinguished_ideal_member_is_contained": False,
    "production_member_sources_complete": False,
    "record_is_production_authority": False,
    "release_submission_science_execution": False,
    "symbolic_bridge_accepted": False,
    "symbolic_machine_contract_complete": False,
}

EXPECTED_OUTPUT_CLAIMS = {
    "budget_present": False,
    "complete_C0": False,
    "complete_C1": False,
    "complete_C2": False,
    "complete_C3": False,
    "control_specific_killing_constructed": False,
    "end_to_end_evaluator_enclosure": False,
    "every_cartesian_interval_member_is_a_model": False,
    "exact_controls_present": False,
    "formal_symbolic_candidate_materialized": False,
    "one_correlated_distinguished_ideal_member_is_contained": False,
    "production_source_roles_1_through_11_bound": False,
    "release_submission_science_execution": False,
    "symbolic_acceptance_receipt_materialized": False,
    "symbolic_bridge_accepted": False,
    "symbolic_machine_contract_complete": False,
    "two_stage_production_open_policy_accepted": False,
}

EXPECTED_DESCRIPTORS = {
    "configuration_geometry": {
        "axis_roles": ["z", "r", "y"],
        "configuration_id": "neutral_symbolic_witnesses_v1",
        "shape": [1, 1, 2],
    },
    "member_spec_manifest_descriptor": {
        "configuration_id": "neutral_symbolic_witnesses_v1",
        "production_member_source_complete": False,
        "refinement_family_id": "neutral_fixture_only",
        "refinement_member_id": "v1",
    },
    "outward_method_registry_descriptor": {
        "analytic_remainder_rule": "exact_rational_only",
        "method_id": "neutral_exact_fraction_v1",
        "precision_bits": "unbounded_integer_fraction",
        "rounding_mode": "exact",
        "special_function_backend_and_version": "none",
    },
    "partition": {
        "raw_axis_masses": {
            "r": ["1/1"],
            "y": ["1/1", "1/1"],
            "z": ["1/1"],
        }
    },
    "physical_parameter_bundle": {
        "M_L": "1/2",
        "W": "2/1",
        "coordinate_order": ["z", "r", "y"],
        "unit": "dimensionless_neutral_fixture",
    },
}

EXPECTED_WITNESSES = {
    "common_flux": {
        "G": "1/7",
        "expected_forward_flux": "6/5",
        "expected_reverse_flux": "6/5",
        "expected_tensor_conductance": "6/7",
        "mu_i": "2/1",
        "mu_j": "3/1",
        "q_ij": "3/5",
        "q_ji": "2/5",
        "spectator_axis_mass_product": "5/1",
    },
    "global_gauge": {
        "M_L": "1/2",
        "S_r": "1/1",
        "S_y": "2/1",
        "S_z": "1/1",
        "expected_G": "1/4",
        "expected_gauged_cell_masses": ["1/4", "1/4"],
        "raw_tensor_cell_masses": ["1/1", "1/1"],
    },
    "interval_division": {
        "M_pi_interval": ["3/10", "31/100"],
        "expected_rho_interval": ["15/13", "31/25"],
        "pi_h_interval": ["1/4", "13/50"],
    },
    "reconstruction": {
        "M_pi": "3/10",
        "V": "2/5",
        "expected_K": "1/3",
        "expected_physical_weight_identity": "1/10",
        "expected_rho": "6/5",
        "pi_h": "1/4",
    },
}


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_exact_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _json_exact_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _json_exact_equal(left, right) for left, right in zip(actual, expected)
        )
    return actual == expected


def _validate_json_tree(value: Any, depth: int = 0, maximum_depth: int = 16) -> None:
    if depth > maximum_depth:
        raise ValueError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise ValueError("JSON floats are forbidden")
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC JSON string")
        return
    if value is None or type(value) in (bool, int):
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_tree(item, depth + 1, maximum_depth)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or unicodedata.normalize("NFC", key) != key:
                raise ValueError("non-NFC or non-string JSON key")
            _validate_json_tree(item, depth + 1, maximum_depth)
        return
    raise ValueError(f"unsupported JSON value type: {type(value).__name__}")


def _canonical_pretty(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _jcs_subset(value: Any) -> bytes:
    _validate_json_tree(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fraction(text: Any) -> Fraction:
    if not isinstance(text, str) or text.count("/") != 1:
        raise ValueError(f"canonical p/q string required: {text!r}")
    numerator_text, denominator_text = text.split("/")
    if not numerator_text or not denominator_text:
        raise ValueError(f"malformed rational: {text!r}")
    value = Fraction(int(numerator_text), int(denominator_text))
    if value.denominator <= 0 or f"{value.numerator}/{value.denominator}" != text:
        raise ValueError(f"noncanonical rational: {text!r}")
    return value


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _safe_relative(text: Any) -> tuple[str, Path]:
    if not isinstance(text, str) or not text or "\\" in text:
        raise ValueError("safe report-relative POSIX path required")
    relative = Path(text)
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        raise ValueError(f"unsafe path: {text!r}")
    banned_components = {
        "budget",
        "control",
        "positive-budget-result",
        "positive_budget_result",
        "propagation",
        "result",
        "results",
        "root",
        "scratch",
        "topology",
    }
    if any(component.lower() in banned_components for component in relative.parts):
        raise ValueError(f"banned path component: {text!r}")
    path = REPORT / relative
    return relative.as_posix(), path


def _open_parent_chain(relative: str) -> tuple[list[int], str]:
    parts = Path(relative).parts
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors = [os.open(REPORT, directory_flags)]
    try:
        for component in parts[:-1]:
            descriptors.append(
                os.open(component, directory_flags, dir_fd=descriptors[-1])
            )
    except BaseException:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise
    return descriptors, parts[-1]


def _verify_parent_chain(relative: str, descriptors: list[int]) -> None:
    parts = Path(relative).parts
    for index, component in enumerate(parts[:-1]):
        held = os.fstat(descriptors[index + 1])
        named = os.stat(component, dir_fd=descriptors[index], follow_symlinks=False)
        if not stat.S_ISDIR(held.st_mode) or (held.st_dev, held.st_ino) != (named.st_dev, named.st_ino):
            raise ValueError(f"directory path replaced while open: {relative}")


def _snapshot(relative_text: Any, counter: Counter[str], maximum_bytes: int) -> tuple[bytes, str]:
    relative, _ = _safe_relative(relative_text)
    directory_descriptors, final_name = _open_parent_chain(relative)
    directory_descriptor = directory_descriptors[-1]
    descriptor = -1
    try:
        descriptor = os.open(
            final_name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_descriptor,
        )
        before = os.fstat(descriptor)
        named_before = os.stat(final_name, dir_fd=directory_descriptor, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError(f"ordinary single-link file required: {relative}")
        if (before.st_dev, before.st_ino) != (named_before.st_dev, named_before.st_ino):
            raise ValueError(f"named file/descriptor mismatch: {relative}")
        if before.st_size > maximum_bytes:
            raise ValueError(f"file size cap exceeded: {relative}")
        chunks: list[bytes] = []
        remaining = before.st_size + 1
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) != before.st_size:
            raise ValueError(f"short or growing read: {relative}")
        after = os.fstat(descriptor)
        named_after = os.stat(final_name, dir_fd=directory_descriptor, follow_symlinks=False)
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after:
            raise ValueError(f"TOCTOU drift while reading: {relative}")
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            named_after.st_dev,
            named_after.st_ino,
            named_after.st_size,
            named_after.st_mtime_ns,
        ):
            raise ValueError(f"named path replaced while reading: {relative}")
        _verify_parent_chain(relative, directory_descriptors)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        for parent_descriptor in reversed(directory_descriptors):
            os.close(parent_descriptor)
    counter[relative] += 1
    return payload, hashlib.sha256(payload).hexdigest()


def _parse_canonical_json(payload: bytes, relative: str, maximum_depth: int) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON object required: {relative}")
    _validate_json_tree(value, maximum_depth=maximum_depth)
    if payload != _canonical_pretty(value):
        raise ValueError(f"canonical sorted JSON required: {relative}")
    return value


def _validate_operation_model(operation: dict[str, Any]) -> tuple[int, int]:
    if set(operation) != {
        "bootstrap_sources",
        "claim_boundary",
        "outer_manifest_source",
        "payload_roles_allowed",
        "resource_caps",
        "schema",
        "stage",
        "status",
        "two_repeat_snapshot_policy",
        "verifier_dependency_closure",
    }:
        raise ValueError("wrong operation-model key set")
    if operation.get("schema") != OPERATION_SCHEMA or operation.get("status") != OPERATION_STATUS:
        raise ValueError("wrong operation-model schema/status")
    if operation.get("stage") != "symbolic_contract_neutral_fixture":
        raise ValueError("wrong operation-model stage")
    if not _json_exact_equal(operation.get("claim_boundary"), {
        "complete_production_payload_roles_1_through_11": False,
        "control_or_budget_source_allowed": False,
        "symbolic_bridge_accepted": False,
    }):
        raise ValueError("operation-model claim boundary changed")
    if not _json_exact_equal(operation.get("payload_roles_allowed"), ["neutral_symbolic_witness_source"]):
        raise ValueError("operation-model payload role changed")
    if not _json_exact_equal(operation.get("resource_caps"), {
        "maximum_file_bytes": 131072,
        "maximum_json_depth": 16,
        "maximum_report_file_opens": 6,
    }):
        raise ValueError("operation-model resource caps changed")
    if not _json_exact_equal(operation.get("two_repeat_snapshot_policy"), {
        "byte_identical_required": True,
        "snapshot_before_parse": True,
    }):
        raise ValueError("operation-model snapshot policy changed")
    if not _json_exact_equal(operation.get("verifier_dependency_closure"), []):
        raise ValueError("v1 verifier dependency closure must be exactly empty")
    bootstrap = operation.get("bootstrap_sources")
    if not isinstance(bootstrap, list) or [entry.get("role") for entry in bootstrap if isinstance(entry, dict)] != [
        "builder_entry_source",
        "design_authority_source",
        "verifier_entry_source",
    ]:
        raise ValueError("wrong ordered bootstrap-source roles")
    for entry in bootstrap:
        if not isinstance(entry, dict) or set(entry) != {"path", "role", "sha256"}:
            raise ValueError("malformed bootstrap-source binding")
        if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64:
            raise ValueError("malformed bootstrap-source digest")
    if bootstrap[0]["path"] != HERE.relative_to(REPORT).as_posix():
        raise ValueError("builder entry does not name this builder")
    if bootstrap[1]["path"] != "notes/continuum_c1_production_gauge_killing_bridge_design_v1.md":
        raise ValueError("wrong design authority path")
    if bootstrap[1]["sha256"] != DESIGN_SHA256:
        raise ValueError("wrong design authority digest")
    if bootstrap[2]["path"] != "code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py":
        raise ValueError("wrong verifier entry path")
    outer = operation.get("outer_manifest_source")
    if not isinstance(outer, dict) or set(outer) != {"path", "schema", "sha256"}:
        raise ValueError("malformed outer-manifest binding")
    if outer["schema"] != MANIFEST_SCHEMA:
        raise ValueError("wrong outer-manifest schema binding")
    return operation["resource_caps"]["maximum_file_bytes"], operation["resource_caps"]["maximum_json_depth"]


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if set(manifest) != {
        "claim_boundary",
        "forbidden_selected_roles",
        "payload_sources",
        "schema",
        "source_dependency_dag",
        "stage",
        "status",
    }:
        raise ValueError("wrong outer-manifest key set")
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != MANIFEST_STATUS:
        raise ValueError("wrong outer-manifest schema/status")
    if manifest.get("stage") != "symbolic_contract_neutral_fixture":
        raise ValueError("wrong outer-manifest stage")
    if not _json_exact_equal(manifest.get("claim_boundary"), {
        "complete_production_payload_roles_1_through_11": False,
        "control_or_budget_source_selected": False,
        "outer_manifest_authorizes_itself": False,
        "symbolic_bridge_accepted": False,
    }):
        raise ValueError("outer-manifest claim boundary changed")
    if not _json_exact_equal(manifest.get("forbidden_selected_roles"), {
        "budget_value_sources": [],
        "control_value_sources": [],
        "result_or_scratch_sources": [],
    }):
        raise ValueError("forbidden role set changed")
    payloads = manifest.get("payload_sources")
    if not isinstance(payloads, list) or len(payloads) != 1:
        raise ValueError("exactly one neutral payload required")
    payload = payloads[0]
    if not isinstance(payload, dict) or set(payload) != {"path", "role", "schema", "sha256"}:
        raise ValueError("malformed neutral payload binding")
    if payload["role"] != "neutral_symbolic_witness_source" or payload["schema"] != SOURCE_SCHEMA:
        raise ValueError("wrong neutral payload role/schema")
    banned_parts = {"results", "result", "scratch", "control", "budget", "positive-budget"}
    if any(part.lower() in banned_parts for part in Path(payload["path"]).parts):
        raise ValueError("banned payload path component")
    if not _json_exact_equal(manifest.get("source_dependency_dag"), {
        "edges": [],
        "nodes": ["neutral_symbolic_witness_source"],
    }):
        raise ValueError("neutral source DAG changed")
    return payload


def _expected_record() -> dict[str, Any]:
    descriptor_hashes = {
        name: hashlib.sha256(_jcs_subset(value)).hexdigest()
        for name, value in EXPECTED_DESCRIPTORS.items()
    }
    return {
        "axis_or_factor_role": "neutral_common_flux",
        "cell_or_edge_id": "edge_i_j",
        "configuration_geometry_sha256": descriptor_hashes["configuration_geometry"],
        "configuration_id": "neutral_symbolic_witnesses_v1",
        "coordinate_order": "z,r,y",
        "ideal_formula_id": "neutral_common_flux_formula",
        "ideal_formula_version": "v1",
        "ideal_quantity_id": "kappa_e",
        "lower_exact_p_over_q": "6/5",
        "member_spec_manifest_sha256": descriptor_hashes["member_spec_manifest_descriptor"],
        "normalization_convention": "single_global_gauge",
        "outward_method_id": "neutral_exact_fraction_v1",
        "outward_method_registry_sha256": descriptor_hashes["outward_method_registry_descriptor"],
        "partition_sha256": descriptor_hashes["partition"],
        "physical_parameter_bundle_sha256": descriptor_hashes["physical_parameter_bundle"],
        "refinement_family_id": "neutral_fixture_only",
        "refinement_member_id": "v1",
        "schema": "encounter_source_native_interval_record_v1",
        "unit": "dimensionless_neutral_fixture",
        "upper_exact_p_over_q": "6/5",
    }


def _validate_source(source: dict[str, Any], source_relative: str, source_sha256: str) -> dict[str, Any]:
    if set(source) != {
        "claim_boundary",
        "contract_schema",
        "native_interval_records",
        "neutral_descriptors",
        "rational_sanity_witnesses",
        "schema",
        "status",
    }:
        raise ValueError("wrong neutral-source key set")
    if source.get("schema") != SOURCE_SCHEMA or source.get("status") != SOURCE_STATUS:
        raise ValueError("wrong neutral-source schema/status")
    if not _json_exact_equal(source.get("claim_boundary"), EXPECTED_SOURCE_CLAIMS):
        raise ValueError("neutral-source claim boundary changed")
    contract = source.get("contract_schema")
    if not isinstance(contract, dict) or set(contract) != {
        "application_policy_input_sources",
        "application_schema_name",
        "budget_value_sources",
        "control_value_sources",
        "native_record_digest_domain",
        "production_symbolic_schema_name",
        "required_production_payload_roles",
        "symbolic_formulae",
    }:
        raise ValueError("wrong neutral contract-schema keys")
    if not _json_exact_equal(contract["required_production_payload_roles"], EXPECTED_ROLES):
        raise ValueError("required production role list changed")
    if not _json_exact_equal(contract["symbolic_formulae"], EXPECTED_FORMULAE):
        raise ValueError("symbolic formula contract changed")
    if contract["production_symbolic_schema_name"] != "encounter_c1_gauge_killing_symbolic_candidate_v1":
        raise ValueError("formal production schema name changed")
    if contract["application_schema_name"] != "encounter_c1_gauge_killing_control_budget_application_candidate_v1":
        raise ValueError("formal application schema name changed")
    if contract["native_record_digest_domain"] != "encounter-source-native-record-v1":
        raise ValueError("native-record digest domain changed")
    for empty_key in ("application_policy_input_sources", "budget_value_sources", "control_value_sources"):
        if not _json_exact_equal(contract[empty_key], []):
            raise ValueError(f"neutral source must keep {empty_key} empty")
    if not _json_exact_equal(source.get("neutral_descriptors"), EXPECTED_DESCRIPTORS):
        raise ValueError("neutral descriptor set changed")
    if not _json_exact_equal(source.get("rational_sanity_witnesses"), EXPECTED_WITNESSES):
        raise ValueError("frozen rational witnesses changed")
    records = source.get("native_interval_records")
    expected_record = _expected_record()
    if not isinstance(records, list) or len(records) != 1 or not _json_exact_equal(records[0], expected_record):
        raise ValueError("neutral native-record fixture changed")
    _fraction(records[0]["lower_exact_p_over_q"])
    _fraction(records[0]["upper_exact_p_over_q"])
    strings: list[str] = []
    stack: list[Any] = [source]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
        elif isinstance(value, str):
            strings.append(value)
    if source_relative in strings or source_sha256 in strings:
        raise ValueError("neutral source predicts its own path or digest")
    return expected_record


def _identity_results(witnesses: dict[str, Any]) -> dict[str, Any]:
    gauge = witnesses["global_gauge"]
    product = _fraction(gauge["S_z"]) * _fraction(gauge["S_r"]) * _fraction(gauge["S_y"])
    global_gauge = _fraction(gauge["M_L"]) / product
    raw_cells = [_fraction(value) for value in gauge["raw_tensor_cell_masses"]]
    gauged_cells = [global_gauge * value for value in raw_cells]
    if global_gauge != _fraction(gauge["expected_G"]):
        raise ValueError("global-gauge witness failed")
    if [_f(value) for value in gauged_cells] != gauge["expected_gauged_cell_masses"]:
        raise ValueError("gauged-cell witness failed")
    if sum(gauged_cells, Fraction(0)) != _fraction(gauge["M_L"]):
        raise ValueError("exact symbolic mass closure failed")

    flux = witnesses["common_flux"]
    forward = _fraction(flux["mu_i"]) * _fraction(flux["q_ij"])
    reverse = _fraction(flux["mu_j"]) * _fraction(flux["q_ji"])
    conductance = _fraction(flux["G"]) * forward * _fraction(flux["spectator_axis_mass_product"])
    if (
        forward != reverse
        or forward != _fraction(flux["expected_forward_flux"])
        or reverse != _fraction(flux["expected_reverse_flux"])
    ):
        raise ValueError("common-flux witness failed")
    if conductance != _fraction(flux["expected_tensor_conductance"]):
        raise ValueError("tensor-conductance witness failed")

    reconstruction = witnesses["reconstruction"]
    m_pi = _fraction(reconstruction["M_pi"])
    pi_h = _fraction(reconstruction["pi_h"])
    value_v = _fraction(reconstruction["V"])
    rho = m_pi / pi_h
    value_k_path_one = value_v / rho
    value_k_path_two = value_v * pi_h / m_pi
    identity_left = m_pi * value_k_path_one
    identity_right = pi_h * value_v
    if rho != _fraction(reconstruction["expected_rho"]):
        raise ValueError("rho witness failed")
    if value_k_path_one != value_k_path_two or value_k_path_one != _fraction(reconstruction["expected_K"]):
        raise ValueError("K reconstruction witness failed")
    if identity_left != identity_right or identity_left != _fraction(reconstruction["expected_physical_weight_identity"]):
        raise ValueError("physical-weight identity failed")

    division = witnesses["interval_division"]
    m_lower, m_upper = map(_fraction, division["M_pi_interval"])
    p_lower, p_upper = map(_fraction, division["pi_h_interval"])
    if not 0 < m_lower <= m_upper or not 0 < p_lower <= p_upper:
        raise ValueError("positive ordered intervals required")
    rho_interval = (m_lower / p_upper, m_upper / p_lower)
    if [_f(value) for value in rho_interval] != division["expected_rho_interval"]:
        raise ValueError("interval-division witness failed")

    return {
        "all_four_neutral_witnesses_exact_pass": True,
        "common_flux_and_tensor_conductance": {
            "common_flux_exact": _f(forward),
            "forward_flux_exact": _f(forward),
            "forward_reverse_exactly_equal": True,
            "neutral_witness_exact_pass": True,
            "reverse_flux_exact": _f(reverse),
            "tensor_conductance_exact": _f(conductance),
        },
        "global_gauge": {
            "G_exact": _f(global_gauge),
            "gauged_cell_masses": [_f(value) for value in gauged_cells],
            "mass_residual_exact": _f(sum(gauged_cells, Fraction(0)) - _fraction(gauge["M_L"])),
            "neutral_witness_exact_pass": True,
            "raw_axis_sum_product": _f(product),
        },
        "interval_division": {
            "denominator_lower_strictly_positive": True,
            "neutral_witness_exact_pass": True,
            "rho_interval": [_f(value) for value in rho_interval],
        },
        "reconstruction": {
            "K_exact": _f(value_k_path_one),
            "K_path_endpoints_exactly_equal": True,
            "neutral_witness_exact_pass": True,
            "physical_weight_identity_exact": _f(identity_left),
            "rho_exact": _f(rho),
        },
    }


def build(
    operation_model_path: Path = DEFAULT_OPERATION_MODEL,
    expected_operation_model_sha256: str | None = None,
) -> dict[str, Any]:
    operation_model_path = Path(os.path.abspath(operation_model_path))
    try:
        operation_relative = operation_model_path.relative_to(REPORT).as_posix()
    except ValueError as error:
        raise ValueError("operation model must be report-relative") from error

    all_reads: Counter[str] = Counter()
    bootstrap_reads: Counter[str] = Counter()
    payload_reads: Counter[str] = Counter()
    operation_bytes, operation_sha = _snapshot(operation_relative, all_reads, 131072)
    bootstrap_reads[operation_relative] += 1
    if (
        not isinstance(expected_operation_model_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_operation_model_sha256) is None
    ):
        raise ValueError("external expected operation-model SHA-256 is required")
    if operation_sha != expected_operation_model_sha256:
        raise ValueError("external operation-model trust anchor mismatch")
    operation = _parse_canonical_json(operation_bytes, operation_relative, 16)
    maximum_bytes, maximum_depth = _validate_operation_model(operation)

    bootstrap_bindings: list[dict[str, str]] = []
    for entry in operation["bootstrap_sources"]:
        payload, observed_sha = _snapshot(entry["path"], all_reads, maximum_bytes)
        bootstrap_reads[entry["path"]] += 1
        if observed_sha != entry["sha256"]:
            raise ValueError(f"stale bootstrap binding: {entry['role']}")
        if entry["role"] == "builder_entry_source" and Path(entry["path"]) != HERE.relative_to(REPORT):
            raise ValueError("builder role path drift")
        if entry["role"] == "design_authority_source" and observed_sha != DESIGN_SHA256:
            raise ValueError("design authority drift")
        bootstrap_bindings.append(dict(entry))

    outer_binding = operation["outer_manifest_source"]
    outer_bytes, outer_sha = _snapshot(outer_binding["path"], all_reads, maximum_bytes)
    bootstrap_reads[outer_binding["path"]] += 1
    if outer_sha != outer_binding["sha256"]:
        raise ValueError("stale outer-manifest binding")
    manifest = _parse_canonical_json(outer_bytes, outer_binding["path"], maximum_depth)
    payload_binding = _validate_manifest(manifest)
    if [payload_binding["role"]] != operation["payload_roles_allowed"]:
        raise ValueError("operation-model/manifest payload-role mismatch")
    if outer_binding["path"] == payload_binding["path"]:
        raise ValueError("outer manifest may not authorize itself")

    source_bytes, source_sha = _snapshot(payload_binding["path"], all_reads, maximum_bytes)
    payload_reads[payload_binding["path"]] += 1
    if source_sha != payload_binding["sha256"]:
        raise ValueError("stale neutral-source binding")
    source = _parse_canonical_json(source_bytes, payload_binding["path"], maximum_depth)
    record = _validate_source(source, payload_binding["path"], source_sha)

    if set(bootstrap_reads) & set(payload_reads):
        raise ValueError("bootstrap and payload open sets overlap")
    combined = bootstrap_reads + payload_reads
    if combined != all_reads:
        raise ValueError("open Counter union is incomplete")
    if sum(all_reads.values()) != operation["resource_caps"]["maximum_report_file_opens"]:
        raise ValueError("report-file open count differs from frozen cap")
    if any(count != 1 for count in all_reads.values()):
        raise ValueError("every report construction input must be opened exactly once")

    record_digest = hashlib.sha256(NATIVE_RECORD_DOMAIN + _jcs_subset(record)).hexdigest()
    identity_results = _identity_results(source["rational_sanity_witnesses"])
    record_key = [
        payload_binding["role"],
        record["member_spec_manifest_sha256"],
        record["partition_sha256"],
        record["refinement_family_id"],
        record["refinement_member_id"],
        record["configuration_id"],
        record["axis_or_factor_role"],
        record["cell_or_edge_id"],
        record["ideal_quantity_id"],
    ]

    return {
        "claim_boundary": EXPECTED_OUTPUT_CLAIMS,
        "contract_scope": {
            "acceptance_receipt_deferred": True,
            "application_policy_input_sources": [],
            "budget_value_sources": [],
            "control_value_sources": [],
            "error_ledger": {
                "E_eval_owner": "future_production_enclosure_and_centre_vs_ideal",
                "E_space_E_eval_double_count_forbidden": True,
                "E_space_owner": "ideal_discretization_vs_continuum",
            },
            "external_operation_model_trust_anchor_verified": True,
            "formal_application_schema_name": source["contract_schema"]["application_schema_name"],
            "formal_production_schema_name": source["contract_schema"]["production_symbolic_schema_name"],
            "neutral_contract_fixture_pass": True,
            "outer_manifest_is_neutral_only": True,
            "production_payload_roles_bound": [],
            "production_payload_roles_required": EXPECTED_ROLES,
        },
        "exact_identity_results": identity_results,
        "member_semantics": {
            "every_cartesian_interval_member_is_a_model": False,
            "neutral_algebra_witnesses_do_not_construct_a_model": True,
            "one_correlated_distinguished_ideal_member_is_contained": False,
        },
        "native_record_receipts": [
            {
                "source_native_record_key": record_key,
                "source_native_record_schema": record["schema"],
                "source_native_record_sha256": record_digest,
                "source_path": payload_binding["path"],
                "source_role": payload_binding["role"],
                "source_sha256": source_sha,
            }
        ],
        "open_ledger": {
            "bootstrap_explicit_snapshot_counter": dict(sorted(bootstrap_reads.items())),
            "bootstrap_payload_sets_disjoint": True,
            "complete_process_report_file_open_closure": False,
            "current_run_output_reopened_as_input": False,
            "explicit_construction_snapshot_counter": dict(sorted(all_reads.items())),
            "explicit_snapshot_counter_union_exact": True,
            "maximum_report_file_opens": operation["resource_caps"]["maximum_report_file_opens"],
            "payload_explicit_snapshot_counter": dict(sorted(payload_reads.items())),
            "prebootstrap_runtime_or_import_opens_traced": False,
        },
        "schema": OUTPUT_SCHEMA,
        "source_bindings": {
            "bootstrap_sources": bootstrap_bindings,
            "operation_model_source": {
                "path": operation_relative,
                "schema": operation["schema"],
                "sha256": operation_sha,
            },
            "outer_manifest_source": {
                "path": outer_binding["path"],
                "schema": manifest["schema"],
                "sha256": outer_sha,
            },
            "payload_sources": [dict(payload_binding)],
        },
        "status": OUTPUT_STATUS,
    }


def _write_exclusive(relative: str, payload: bytes) -> None:
    _safe_relative(relative)
    directory_descriptors, final_name = _open_parent_chain(relative)
    directory_descriptor = directory_descriptors[-1]
    temporary_name = f".{final_name}.{secrets.token_hex(12)}.tmp"
    descriptor = -1
    temporary_exists = False
    try:
        try:
            os.stat(final_name, dir_fd=directory_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise FileExistsError(f"refusing to overwrite existing output: {relative}")
        descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o644,
            dir_fd=directory_descriptor,
        )
        temporary_exists = True
        handle = os.fdopen(descriptor, "wb")
        descriptor = -1
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _verify_parent_chain(relative, directory_descriptors)
        os.link(
            temporary_name,
            final_name,
            src_dir_fd=directory_descriptor,
            dst_dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
        os.unlink(temporary_name, dir_fd=directory_descriptor)
        temporary_exists = False
        os.fsync(directory_descriptor)
        _verify_parent_chain(relative, directory_descriptors)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_exists:
            try:
                os.unlink(temporary_name, dir_fd=directory_descriptor)
            except FileNotFoundError:
                pass
        for parent_descriptor in reversed(directory_descriptors):
            os.close(parent_descriptor)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation-model", type=Path, default=DEFAULT_OPERATION_MODEL)
    parser.add_argument("--expected-operation-model-sha256", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate six inputs and print expected SHA; do not open the output",
    )
    arguments = parser.parse_args()
    payload = _canonical_pretty(
        build(arguments.operation_model, arguments.expected_operation_model_sha256)
    )
    digest = hashlib.sha256(payload).hexdigest()
    if arguments.check:
        print(f"PASS_INPUTS_EXPECTED_FIXTURE_SHA {digest} OUTPUT_NOT_OPENED")
        return 0
    output = Path(os.path.abspath(arguments.output))
    try:
        output_relative = output.relative_to(REPORT).as_posix()
    except ValueError as error:
        raise SystemExit("output must remain under report root") from error
    relative_output_path = Path(output_relative)
    if relative_output_path.name != DEFAULT_OUTPUT.name:
        raise SystemExit("v1 output basename must remain the neutral fixture basename")
    if output_relative != DEFAULT_OUTPUT.relative_to(REPORT).as_posix() and (
        not relative_output_path.parts or relative_output_path.parts[0] != "tmp"
    ):
        raise SystemExit("nondefault v1 outputs are allowed only below report/tmp")
    _write_exclusive(output_relative, payload)
    print(f"WROTE {output} SHA256 {digest} OUTPUT_NOT_REOPENED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
