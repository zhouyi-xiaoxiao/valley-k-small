#!/usr/bin/env python3
"""Independent validator for the neutral symbolic-bridge contract fixture.

The validator does not import or invoke the builder.  It independently checks
the externally pinned operation model, bootstrap and payload bindings, strict
JSON/source semantics, native-record digest, four rational witnesses, and the
complete canonical artifact object.  Its stdout is an ephemeral validation
summary, never a symbolic acceptance receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OPERATION_MODEL = REPORT / "code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json"
DEFAULT_ARTIFACT = REPORT / "artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json"

OPERATION_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_operation_model_v1"
MANIFEST_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_outer_manifest_v1"
SOURCE_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_source_v1"
OUTPUT_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_fixture_v1"
OUTPUT_STATUS = "PASS_NEUTRAL_SYMBOLIC_CONTRACT_FIXTURE_ONLY_PRODUCTION_CANDIDATE_NOT_MATERIALIZED"
DESIGN_SHA256 = "d23c088f917832bb9d8078a046133556e8ee8547d8a062d3102a922881ba67e4"
NATIVE_DOMAIN = b"encounter-source-native-record-v1\x00"

REQUIRED_ROLES = [
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

FORMULAE = {
    "common_flux": "kappa_e=mu_i*q_ij=mu_j*q_ji",
    "discrete_killing_diagonal": "k=B*V",
    "global_gauge": "G=M_L/(S_z*S_r*S_y)",
    "map_ratio": "rho=M_pi/pi_h",
    "physical_weight_identity": "M_pi*K=pi_h*V",
    "reconstructed_killed_multiplier": "B*K",
    "reconstructed_multiplier": "K=V/rho",
    "tensor_conductance": "c_e=G*kappa_e*product_other_axis_masses",
}

SOURCE_CLAIM_KEYS = {
    "budget_present",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "control_specific_killing_constructed",
    "exact_controls_present",
    "one_correlated_distinguished_ideal_member_is_contained",
    "production_member_sources_complete",
    "record_is_production_authority",
    "release_submission_science_execution",
    "symbolic_bridge_accepted",
    "symbolic_machine_contract_complete",
}

OUTPUT_CLAIM_KEYS = {
    "budget_present",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "control_specific_killing_constructed",
    "end_to_end_evaluator_enclosure",
    "every_cartesian_interval_member_is_a_model",
    "exact_controls_present",
    "formal_symbolic_candidate_materialized",
    "one_correlated_distinguished_ideal_member_is_contained",
    "production_source_roles_1_through_11_bound",
    "release_submission_science_execution",
    "symbolic_acceptance_receipt_materialized",
    "symbolic_bridge_accepted",
    "symbolic_machine_contract_complete",
    "two_stage_production_open_policy_accepted",
}

EXPECTED_DESCRIPTOR_SHA256 = {
    "configuration_geometry": "0c560042ba4ece02b852583bd9fa5058e4a7302ad596cadb7807f7c5ee162ac7",
    "member_spec_manifest_descriptor": "a885b05b3154414554d18eb75c0dfc559bdd3d2514aa45c2bae5498b6b39a93d",
    "outward_method_registry_descriptor": "005265fcef08b7710d53c554ddea34c8eca3cdaf85949db0ec887950f96bfe42",
    "partition": "19678e150cbfb839852037adc6a51dc904bbe60ba5fb1527f256ad959a669801",
    "physical_parameter_bundle": "6e8b1258746c75e19c6d2200e63ccd43c8a419e984206c1afe74a732e20a45ca",
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


def _duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise ValueError("JSON floats forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        return
    if isinstance(value, list):
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or unicodedata.normalize("NFC", key) != key:
                raise ValueError("invalid JSON key")
            _strict_tree(item, depth + 1)
        return
    raise ValueError(f"forbidden JSON type: {type(value).__name__}")


def _exact(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(right, dict):
        return set(left) == set(right) and all(_exact(left[key], right[key]) for key in right)
    if isinstance(right, list):
        return len(left) == len(right) and all(_exact(a, b) for a, b in zip(left, right))
    return left == right


def _pretty(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _jcs(value: Any) -> bytes:
    _strict_tree(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _q(text: Any) -> Fraction:
    if not isinstance(text, str) or text.count("/") != 1:
        raise ValueError("canonical rational required")
    numerator, denominator = text.split("/")
    value = Fraction(int(numerator), int(denominator))
    if value.denominator <= 0 or f"{value.numerator}/{value.denominator}" != text:
        raise ValueError("noncanonical rational")
    return value


def _qs(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _relative(path: Path) -> str:
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(REPORT)
    except ValueError as error:
        raise ValueError("path must remain within report root") from error
    if ".." in relative.parts or not relative.parts:
        raise ValueError("unsafe path")
    banned = {
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
    if any(part.lower() in banned for part in relative.parts):
        raise ValueError("banned path component")
    return relative.as_posix()


def _snapshot(relative: str, cap: int = 131072) -> tuple[bytes, str]:
    parts = Path(relative).parts
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories = [os.open(REPORT, flags)]
    descriptor = -1
    try:
        for component in parts[:-1]:
            directories.append(os.open(component, flags, dir_fd=directories[-1]))
        descriptor = os.open(parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directories[-1])
        before = os.fstat(descriptor)
        named_before = os.stat(parts[-1], dir_fd=directories[-1], follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("ordinary single-link file required")
        if (before.st_dev, before.st_ino) != (named_before.st_dev, named_before.st_ino):
            raise ValueError("descriptor/name mismatch")
        if before.st_size > cap:
            raise ValueError("file cap exceeded")
        chunks: list[bytes] = []
        remaining = before.st_size + 1
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        named_after = os.stat(parts[-1], dir_fd=directories[-1], follow_symlinks=False)
        before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        named_id = (named_after.st_dev, named_after.st_ino, named_after.st_size, named_after.st_mtime_ns)
        if len(payload) != before.st_size or before_id != after_id or after_id != named_id:
            raise ValueError("unstable snapshot")
        for index, component in enumerate(parts[:-1]):
            held = os.fstat(directories[index + 1])
            named = os.stat(component, dir_fd=directories[index], follow_symlinks=False)
            if (held.st_dev, held.st_ino) != (named.st_dev, named.st_ino):
                raise ValueError("directory chain replaced")
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)
    return payload, hashlib.sha256(payload).hexdigest()


def _json_snapshot(relative: str, cap: int = 131072) -> tuple[dict[str, Any], bytes, str]:
    payload, digest = _snapshot(relative, cap)
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=_duplicates)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON object required")
    _strict_tree(value)
    if payload != _pretty(value):
        raise ValueError("canonical sorted JSON required")
    return value, payload, digest


def _claims_false(value: Any, keys: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != keys or any(value[key] is not False for key in keys):
        raise ValueError(f"{label} claims must be exact false booleans")


def _validate_operation(operation: dict[str, Any]) -> None:
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
    if operation["schema"] != OPERATION_SCHEMA or operation["stage"] != "symbolic_contract_neutral_fixture":
        raise ValueError("wrong operation schema/stage")
    if operation["status"] != "NEUTRAL_OPERATION_MODEL_EXTERNALLY_PINNED_NO_PRODUCTION_ACCEPTANCE":
        raise ValueError("wrong operation status")
    _claims_false(operation["claim_boundary"], {
        "complete_production_payload_roles_1_through_11",
        "control_or_budget_source_allowed",
        "symbolic_bridge_accepted",
    }, "operation")
    if not _exact(operation["payload_roles_allowed"], ["neutral_symbolic_witness_source"]):
        raise ValueError("wrong allowed payload role")
    if not _exact(operation["resource_caps"], {
        "maximum_file_bytes": 131072,
        "maximum_json_depth": 16,
        "maximum_report_file_opens": 6,
    }):
        raise ValueError("wrong resource caps")
    if not _exact(operation["two_repeat_snapshot_policy"], {
        "byte_identical_required": True,
        "snapshot_before_parse": True,
    }) or not _exact(operation["verifier_dependency_closure"], []):
        raise ValueError("wrong snapshot/dependency policy")
    bootstrap = operation["bootstrap_sources"]
    if not isinstance(bootstrap, list) or [entry.get("role") for entry in bootstrap if isinstance(entry, dict)] != [
        "builder_entry_source",
        "design_authority_source",
        "verifier_entry_source",
    ]:
        raise ValueError("wrong bootstrap roles/order")
    expected_paths = [
        "code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py",
        "notes/continuum_c1_production_gauge_killing_bridge_design_v1.md",
        "code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py",
    ]
    for entry, expected_path in zip(bootstrap, expected_paths):
        if not isinstance(entry, dict) or set(entry) != {"path", "role", "sha256"} or entry["path"] != expected_path:
            raise ValueError("malformed bootstrap binding")
        if re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None:
            raise ValueError("bad bootstrap digest")
    if bootstrap[1]["sha256"] != DESIGN_SHA256:
        raise ValueError("design authority digest changed")
    outer = operation["outer_manifest_source"]
    if not isinstance(outer, dict) or set(outer) != {"path", "schema", "sha256"} or outer["schema"] != MANIFEST_SCHEMA:
        raise ValueError("bad outer-manifest binding")


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    if set(manifest) != {
        "claim_boundary",
        "forbidden_selected_roles",
        "payload_sources",
        "schema",
        "source_dependency_dag",
        "stage",
        "status",
    }:
        raise ValueError("wrong outer manifest keys")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["stage"] != "symbolic_contract_neutral_fixture":
        raise ValueError("wrong outer manifest schema/stage")
    if manifest["status"] != "NEUTRAL_OUTER_MANIFEST_ONLY_PRODUCTION_ROLE_SET_INCOMPLETE":
        raise ValueError("wrong outer manifest status")
    _claims_false(manifest["claim_boundary"], {
        "complete_production_payload_roles_1_through_11",
        "control_or_budget_source_selected",
        "outer_manifest_authorizes_itself",
        "symbolic_bridge_accepted",
    }, "manifest")
    if not _exact(manifest["forbidden_selected_roles"], {
        "budget_value_sources": [],
        "control_value_sources": [],
        "result_or_scratch_sources": [],
    }) or not _exact(manifest["source_dependency_dag"], {
        "edges": [],
        "nodes": ["neutral_symbolic_witness_source"],
    }):
        raise ValueError("manifest forbidden roles/DAG changed")
    sources = manifest["payload_sources"]
    if not isinstance(sources, list) or len(sources) != 1:
        raise ValueError("one neutral payload required")
    source = sources[0]
    if not isinstance(source, dict) or set(source) != {"path", "role", "schema", "sha256"}:
        raise ValueError("malformed payload source")
    if source["role"] != "neutral_symbolic_witness_source" or source["schema"] != SOURCE_SCHEMA:
        raise ValueError("wrong payload role/schema")
    return source


def _validate_source(source: dict[str, Any], relative: str, digest: str) -> dict[str, Any]:
    if set(source) != {
        "claim_boundary",
        "contract_schema",
        "native_interval_records",
        "neutral_descriptors",
        "rational_sanity_witnesses",
        "schema",
        "status",
    }:
        raise ValueError("wrong neutral source keys")
    if source["schema"] != SOURCE_SCHEMA or source["status"] != "NEUTRAL_SYMBOLIC_CONTRACT_WITNESSES_ONLY_NO_PRODUCTION_NO_CONTROL_NO_BUDGET":
        raise ValueError("wrong neutral source schema/status")
    _claims_false(source["claim_boundary"], SOURCE_CLAIM_KEYS, "source")
    contract = source["contract_schema"]
    if set(contract) != {
        "application_policy_input_sources",
        "application_schema_name",
        "budget_value_sources",
        "control_value_sources",
        "native_record_digest_domain",
        "production_symbolic_schema_name",
        "required_production_payload_roles",
        "symbolic_formulae",
    }:
        raise ValueError("wrong contract keys")
    if contract["production_symbolic_schema_name"] != "encounter_c1_gauge_killing_symbolic_candidate_v1":
        raise ValueError("formal symbolic schema changed")
    if contract["application_schema_name"] != "encounter_c1_gauge_killing_control_budget_application_candidate_v1":
        raise ValueError("formal application schema changed")
    if contract["native_record_digest_domain"] != "encounter-source-native-record-v1":
        raise ValueError("record domain changed")
    if not _exact(contract["required_production_payload_roles"], REQUIRED_ROLES) or not _exact(contract["symbolic_formulae"], FORMULAE):
        raise ValueError("required roles/formulae changed")
    for key in ("application_policy_input_sources", "budget_value_sources", "control_value_sources"):
        if not _exact(contract[key], []):
            raise ValueError("neutral source selected application values")
    descriptors = source["neutral_descriptors"]
    if not isinstance(descriptors, dict) or set(descriptors) != set(EXPECTED_DESCRIPTOR_SHA256):
        raise ValueError("descriptor key set changed")
    observed_descriptor_sha = {key: hashlib.sha256(_jcs(value)).hexdigest() for key, value in descriptors.items()}
    if observed_descriptor_sha != EXPECTED_DESCRIPTOR_SHA256:
        raise ValueError("neutral descriptor bytes changed")
    if not _exact(source["rational_sanity_witnesses"], EXPECTED_WITNESSES):
        raise ValueError("rational witness source changed")
    records = source["native_interval_records"]
    if not isinstance(records, list) or len(records) != 1 or not isinstance(records[0], dict):
        raise ValueError("one native record required")
    record = records[0]
    expected_record_values = {
        "axis_or_factor_role": "neutral_common_flux",
        "cell_or_edge_id": "edge_i_j",
        "configuration_geometry_sha256": EXPECTED_DESCRIPTOR_SHA256["configuration_geometry"],
        "configuration_id": "neutral_symbolic_witnesses_v1",
        "coordinate_order": "z,r,y",
        "ideal_formula_id": "neutral_common_flux_formula",
        "ideal_formula_version": "v1",
        "ideal_quantity_id": "kappa_e",
        "lower_exact_p_over_q": "6/5",
        "member_spec_manifest_sha256": EXPECTED_DESCRIPTOR_SHA256["member_spec_manifest_descriptor"],
        "normalization_convention": "single_global_gauge",
        "outward_method_id": "neutral_exact_fraction_v1",
        "outward_method_registry_sha256": EXPECTED_DESCRIPTOR_SHA256["outward_method_registry_descriptor"],
        "partition_sha256": EXPECTED_DESCRIPTOR_SHA256["partition"],
        "physical_parameter_bundle_sha256": EXPECTED_DESCRIPTOR_SHA256["physical_parameter_bundle"],
        "refinement_family_id": "neutral_fixture_only",
        "refinement_member_id": "v1",
        "schema": "encounter_source_native_interval_record_v1",
        "unit": "dimensionless_neutral_fixture",
        "upper_exact_p_over_q": "6/5",
    }
    if not _exact(record, expected_record_values):
        raise ValueError("native record changed")
    _q(record["lower_exact_p_over_q"])
    _q(record["upper_exact_p_over_q"])
    strings: list[str] = []
    stack: list[Any] = [source]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            strings.append(item)
    if relative in strings or digest in strings:
        raise ValueError("source predicts its own path/hash")
    return record


def _identities(witnesses: dict[str, Any]) -> dict[str, Any]:
    gauge = witnesses["global_gauge"]
    product = _q(gauge["S_z"]) * _q(gauge["S_r"]) * _q(gauge["S_y"])
    global_gauge = _q(gauge["M_L"]) / product
    cells = [global_gauge * _q(value) for value in gauge["raw_tensor_cell_masses"]]
    if global_gauge != _q(gauge["expected_G"]) or [_qs(value) for value in cells] != gauge["expected_gauged_cell_masses"]:
        raise ValueError("gauge witness failed")
    if sum(cells, Fraction(0)) != _q(gauge["M_L"]):
        raise ValueError("mass closure failed")
    flux = witnesses["common_flux"]
    forward = _q(flux["mu_i"]) * _q(flux["q_ij"])
    reverse = _q(flux["mu_j"]) * _q(flux["q_ji"])
    conductance = _q(flux["G"]) * forward * _q(flux["spectator_axis_mass_product"])
    if forward != reverse or forward != _q(flux["expected_forward_flux"]) or reverse != _q(flux["expected_reverse_flux"]):
        raise ValueError("flux witness failed")
    if conductance != _q(flux["expected_tensor_conductance"]):
        raise ValueError("conductance witness failed")
    reconstruction = witnesses["reconstruction"]
    m_pi, pi_h, value_v = _q(reconstruction["M_pi"]), _q(reconstruction["pi_h"]), _q(reconstruction["V"])
    rho = m_pi / pi_h
    k_one, k_two = value_v / rho, value_v * pi_h / m_pi
    physical_left, physical_right = m_pi * k_one, pi_h * value_v
    if rho != _q(reconstruction["expected_rho"]) or k_one != k_two or k_one != _q(reconstruction["expected_K"]):
        raise ValueError("reconstruction witness failed")
    if physical_left != physical_right or physical_left != _q(reconstruction["expected_physical_weight_identity"]):
        raise ValueError("physical identity failed")
    division = witnesses["interval_division"]
    m_lo, m_hi = map(_q, division["M_pi_interval"])
    p_lo, p_hi = map(_q, division["pi_h_interval"])
    if not 0 < m_lo <= m_hi or not 0 < p_lo <= p_hi:
        raise ValueError("invalid positive intervals")
    interval = (m_lo / p_hi, m_hi / p_lo)
    if [_qs(value) for value in interval] != division["expected_rho_interval"]:
        raise ValueError("interval division failed")
    return {
        "all_four_neutral_witnesses_exact_pass": True,
        "common_flux_and_tensor_conductance": {
            "common_flux_exact": _qs(forward),
            "forward_flux_exact": _qs(forward),
            "forward_reverse_exactly_equal": True,
            "neutral_witness_exact_pass": True,
            "reverse_flux_exact": _qs(reverse),
            "tensor_conductance_exact": _qs(conductance),
        },
        "global_gauge": {
            "G_exact": _qs(global_gauge),
            "gauged_cell_masses": [_qs(value) for value in cells],
            "mass_residual_exact": _qs(sum(cells, Fraction(0)) - _q(gauge["M_L"])),
            "neutral_witness_exact_pass": True,
            "raw_axis_sum_product": _qs(product),
        },
        "interval_division": {
            "denominator_lower_strictly_positive": True,
            "neutral_witness_exact_pass": True,
            "rho_interval": [_qs(value) for value in interval],
        },
        "reconstruction": {
            "K_exact": _qs(k_one),
            "K_path_endpoints_exactly_equal": True,
            "neutral_witness_exact_pass": True,
            "physical_weight_identity_exact": _qs(physical_left),
            "rho_exact": _qs(rho),
        },
    }


def validate(operation_path: Path, expected_operation_sha: str, artifact_path: Path) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{64}", expected_operation_sha or "") is None:
        raise ValueError("external operation-model SHA-256 required")
    operation_relative = _relative(operation_path)
    operation, _operation_bytes, operation_sha = _json_snapshot(operation_relative)
    if operation_sha != expected_operation_sha:
        raise ValueError("external operation-model trust anchor mismatch")
    _validate_operation(operation)

    for entry in operation["bootstrap_sources"]:
        _payload, observed = _snapshot(entry["path"], operation["resource_caps"]["maximum_file_bytes"])
        if observed != entry["sha256"]:
            raise ValueError(f"stale bootstrap source: {entry['role']}")
    outer_binding = operation["outer_manifest_source"]
    manifest, _manifest_bytes, manifest_sha = _json_snapshot(outer_binding["path"])
    if manifest_sha != outer_binding["sha256"]:
        raise ValueError("stale outer manifest")
    payload_binding = _validate_manifest(manifest)
    if operation["payload_roles_allowed"] != [payload_binding["role"]]:
        raise ValueError("operation/manifest role mismatch")
    source, _source_bytes, source_sha = _json_snapshot(payload_binding["path"])
    if source_sha != payload_binding["sha256"]:
        raise ValueError("stale neutral source")
    record = _validate_source(source, payload_binding["path"], source_sha)

    bootstrap_counter = Counter({operation_relative: 1})
    bootstrap_counter.update({entry["path"]: 1 for entry in operation["bootstrap_sources"]})
    bootstrap_counter[outer_binding["path"]] += 1
    payload_counter = Counter({payload_binding["path"]: 1})
    all_counter = bootstrap_counter + payload_counter
    if set(bootstrap_counter) & set(payload_counter) or sum(all_counter.values()) != 6:
        raise ValueError("explicit snapshot ledger reconstruction failed")

    record_digest = hashlib.sha256(NATIVE_DOMAIN + _jcs(record)).hexdigest()
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
    expected_artifact = {
        "claim_boundary": {key: False for key in sorted(OUTPUT_CLAIM_KEYS)},
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
            "production_payload_roles_required": REQUIRED_ROLES,
        },
        "exact_identity_results": _identities(source["rational_sanity_witnesses"]),
        "member_semantics": {
            "every_cartesian_interval_member_is_a_model": False,
            "neutral_algebra_witnesses_do_not_construct_a_model": True,
            "one_correlated_distinguished_ideal_member_is_contained": False,
        },
        "native_record_receipts": [{
            "source_native_record_key": record_key,
            "source_native_record_schema": record["schema"],
            "source_native_record_sha256": record_digest,
            "source_path": payload_binding["path"],
            "source_role": payload_binding["role"],
            "source_sha256": source_sha,
        }],
        "open_ledger": {
            "bootstrap_explicit_snapshot_counter": dict(sorted(bootstrap_counter.items())),
            "bootstrap_payload_sets_disjoint": True,
            "complete_process_report_file_open_closure": False,
            "current_run_output_reopened_as_input": False,
            "explicit_construction_snapshot_counter": dict(sorted(all_counter.items())),
            "explicit_snapshot_counter_union_exact": True,
            "maximum_report_file_opens": 6,
            "payload_explicit_snapshot_counter": dict(sorted(payload_counter.items())),
            "prebootstrap_runtime_or_import_opens_traced": False,
        },
        "schema": OUTPUT_SCHEMA,
        "source_bindings": {
            "bootstrap_sources": [dict(entry) for entry in operation["bootstrap_sources"]],
            "operation_model_source": {
                "path": operation_relative,
                "schema": operation["schema"],
                "sha256": operation_sha,
            },
            "outer_manifest_source": {
                "path": outer_binding["path"],
                "schema": manifest["schema"],
                "sha256": manifest_sha,
            },
            "payload_sources": [dict(payload_binding)],
        },
        "status": OUTPUT_STATUS,
    }

    artifact_relative = _relative(artifact_path)
    artifact, artifact_bytes, artifact_sha = _json_snapshot(artifact_relative)
    if not _exact(artifact, expected_artifact):
        raise ValueError("artifact differs from independent reconstruction")
    _claims_false(artifact["claim_boundary"], OUTPUT_CLAIM_KEYS, "artifact")
    return {
        "artifact_sha256": artifact_sha,
        "explicit_construction_snapshot_count": sum(all_counter.values()),
        "native_record_sha256": record_digest,
        "status": "PASS_NEUTRAL_SYMBOLIC_BRIDGE_FIXTURE_INDEPENDENT_VALIDATION_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation-model", type=Path, default=DEFAULT_OPERATION_MODEL)
    parser.add_argument("--expected-operation-model-sha256", required=True)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    arguments = parser.parse_args()
    summary = validate(
        arguments.operation_model,
        arguments.expected_operation_model_sha256,
        arguments.artifact,
    )
    print("PASS " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
