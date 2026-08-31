#!/usr/bin/env python3
"""Independently validate the production n=0 same-member preflight package.

This module deliberately does not import or invoke the builder.  It reconstructs
the 12 configuration joins, 36 axis/partition joins, 5,037 cell identities,
5,013 oriented edge identities, and 48 killing-profile identities from the
hash-pinned retained sources.  The validated object is a preflight only: every
promotion flag and every named blocker must remain false/uncleared.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

SELF = Path(__file__).resolve()
REPORT = SELF.parents[1]

MEMBER_SPEC_RELATIVE = "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json"
POLICY_RELATIVE = "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json"
CONTROL_RELATIVE = "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json"
MANIFEST_RELATIVE = "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json"
CANDIDATE_RELATIVE = (
    "artifacts/data/continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json"
)
BUILDER_RELATIVE = "code/build_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"

DEFAULT_MEMBER_SPEC = REPORT / MEMBER_SPEC_RELATIVE
DEFAULT_POLICY = REPORT / POLICY_RELATIVE
DEFAULT_CONTROL = REPORT / CONTROL_RELATIVE
DEFAULT_MANIFEST = REPORT / MANIFEST_RELATIVE
DEFAULT_CANDIDATE = REPORT / CANDIDATE_RELATIVE

SOURCE_PINS: dict[str, tuple[str, str]] = {
    "reference_density_source": (
        "artifacts/data/continuum_c1_reference_density_source_v1.json",
        "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    ),
    "ideal_formula_source": (
        "artifacts/data/continuum_c1_ideal_formula_source_v1.json",
        "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    ),
    "factorization_source": (
        "artifacts/data/continuum_c1_factorization_source_v1.json",
        "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
    ),
    "configuration_source": (
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    "legacy_member_spec": (
        "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json",
        "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef",
    ),
    "method_registry": (
        "artifacts/data/continuum_c1_c2_fixed_row_outward_method_registry_v1.json",
        "ac00450edf826029b157a98ad2835592630c07b2a75334c25d8d1232a4fe69c3",
    ),
    "legacy_policy": (
        "artifacts/data/continuum_c1_c2_fixed_row_anti_vacuity_policy_v1.json",
        "c8b9f3aca2b3a516935eeb1fdfb2bf542ba0da2d12ae4c11581f6f1ee607f628",
    ),
    "raw_axis_binding": (
        "artifacts/data/continuum_c1_raw_axis_production_binding_v1.json",
        "7028fecf4538abb1df56f03d8cea01d0ed208a43356cb9b1e24c67fb54d47480",
    ),
    "stationary_integral_source": (
        "artifacts/data/continuum_c1_stationary_integral_source_v1.json",
        "03db61b4aa9c2b7a4ab2fd78c86fbbf90dd1548657c615d91c1526ae3ed77212",
    ),
    "stationary_integral_receipt": (
        "artifacts/data/"
        "continuum_c1_stationary_integral_validator_authenticated_outer_receipt_v1.json",
        "26d2b9a3fd49f7f8d4cf893431b1f134c2ae2efae3bf15e1615ca28766603571",
    ),
    "raw_flux_source": (
        "artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json",
        "04fee91f8708d90febc23e1f1ee4cfc1cb4800b9e35980eb99006fad327b40f3",
    ),
    "raw_flux_receipt": (
        "artifacts/data/"
        "continuum_c1_fixed_row_raw_flux_validator_authenticated_outer_receipt_v1.json",
        "44af008a9a86cbb249209dd806fbb2633f4976aae5e5fbf234d55dfa36bad0e2",
    ),
    "joint_refinement_family": (
        "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9",
    ),
    "control_method_commitment": (
        "artifacts/data/continuum_c0_control_method_commitment_v2.json",
        "288ad85d5992446a8f3b58416e445a88f1c15a4c71114ba008939d8fbd9a4a97",
    ),
    "killing_geometry_authority": (
        "artifacts/data/physical_killing_geometry_source_v1.json",
        "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    ),
    "killing_binding_sidecar": (
        "artifacts/data/continuum_c2_killing_geometry_production_binding_v1.json",
        "fc03f0934defbc515ab2940705abc4c020199dc238b576aca5703bb31287ec27",
    ),
    "initial_bundle": (
        "artifacts/data/physical_production_initial_stream_v1/bundle.json",
        "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
    ),
    "initial_independent_receipt": (
        "artifacts/data/physical_production_initial_stream_v1_independent_receipt.json",
        "2fb16af6545281f988ddf7527b5e88b46e98ec7e5a05fcbe1bb5bf457c6f9136",
    ),
    "initial_geometry_receipt": (
        "artifacts/data/physical_production_initial_stream_v1_geometry_receipt.json",
        "3b23c641ce82cb30a2f150d9956b235bca918948a40f57365f866e6aa54959fb",
    ),
    "initial_clean_replay": (
        "artifacts/data/physical_production_initial_clean_process_replay_v1.json",
        "e1b25ab5221434e26749e9b2103c04c36e27539a810e2a15c236c1806b333891",
    ),
    "killing_geometry_bundle": (
        "artifacts/data/physical_production_killing_geometry_v1/bundle.json",
        "f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684",
    ),
    "killing_geometry_receipt": (
        "artifacts/data/physical_production_killing_geometry_two_repeat_outer_receipt_v1.json",
        "d635dfb7dd24fc15731dfd69e20264a5515c3bf82b92569a58cd2bed3264fcd9",
    ),
    "bridge_design": (
        "notes/continuum_c1_production_gauge_killing_bridge_design_v1.md",
        "d23c088f917832bb9d8078a046133556e8ee8547d8a062d3102a922881ba67e4",
    ),
    "round170_audit": (
        "audits/round_170_production_killing_geometry_two_repeat_outer_replay.md",
        "a794bbf15b8c46aa1bae69a520a8b641b903ee416dfe2da24facdbfbe0808935",
    ),
    "round171_audit": (
        "audits/round_171_fixed_row_stationary_raw_flux_authenticated_source_audit.md",
        "4f906b099778ffa4e676d742189df332931edd31c561957d65bfeac4aaeed2d4",
    ),
    "round172_audit": (
        "audits/round_172_genuine_joint_refinement_family_v2.md",
        "90415181c06e94e6dd451b3c9c2a8abb32c4127cc0703976b003e26afd10cad0",
    ),
}

JSON_ROLES = frozenset(role for role, (path, _) in SOURCE_PINS.items() if path.endswith(".json"))
AXES = ["midpoint", "relative_parallel", "relative_perpendicular"]
PROFILES = [0, 1, 2, 3]

CLAIM_KEYS = {
    "backend_independence_claimed",
    "box_exhaustion_complete",
    "budget_present",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "computable_C2_certificate",
    "continuum_root_margin_certified",
    "control_specific_killing_constructed",
    "end_to_end_evaluator_enclosure",
    "exact_controls_present",
    "F0",
    "F1",
    "F2",
    "F3",
    "formal_symbolic_candidate_materialized",
    "numerically_evaluated_theorem_constants",
    "one_correlated_distinguished_ideal_member_is_contained",
    "production_n0_correlated_containment_receipt_present",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "root_transfer_complete",
    "science_executed",
    "submission_eligible",
    "symbolic_acceptance_receipt_materialized",
    "symbolic_bridge_accepted",
}

EXPECTED_BLOCKER_IDS = [
    "B01_current_roles_8_9_bind_legacy_member_spec_v1",
    "B02_policy_predecessor_order_not_independently_sealed",
    "B03_current_enclosures_predate_no_sealed_v2_policy",
    "B04_round172_has_no_partition_sha256",
    "B05_killing_rows_lack_member_native_provenance",
    "B06_method_registry_missing_code_and_parameter_hashes",
    "B07_formal_outer_open_operation_model_and_complete_dag_absent",
    "B08_exact_dag_interval_replay_absent",
    "B09_independent_symbolic_acceptance_receipt_absent",
]
EXPECTED_BLOCKER_ACTIONS = [
    (
        "regenerate stationary and raw-flux roles under a predecessor-sealed successor "
        "member specification"
    ),
    "freeze an externally authenticated policy before any acceptance replay",
    "perform a new ordered result-blind replay",
    "bind independently reconstructed n0 partition hashes in a future member identity",
    (
        "regenerate killing native records with refinement, member, partition, formula, "
        "method, normalization, unit, and record digests"
    ),
    ("publish a successor registry with producer, verifier, and method-parameter hashes"),
    "freeze an external operation model and a complete selected-source dependency DAG",
    "stream and independently replay the exact gauge, flux, map, and killing DAG",
    "issue a distinct receipt only after the correlated replay passes",
]

EXPECTED_DAG = {
    "adjoint_map": "P_h=J_h_star",
    "axis_mass_sums": "S_axis=sum_axis_cells(mu_axis)",
    "common_flux": "kappa_e=mu_i*q_ij=mu_j*q_ji",
    "discrete_killing_diagonal": "k=B*V",
    "gauged_cell_mass": "pi_h=G*mu_midpoint*mu_relative_parallel*mu_relative_perpendicular",
    "gauged_mass_closure": "sum_cells(pi_h)=M_L",
    "generator_diagonal": "q_CC=-sum_Cprime_not_equal_C(q_C_Cprime)",
    "global_gauge": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
    "global_gauge_mass_identity": ("G*S_midpoint*S_relative_parallel*S_relative_perpendicular=M_L"),
    "map_composition": "P_h*J_h=diag(rho)",
    "map_ratio": "rho=M_pi/pi_h",
    "physical_mass_closure": "sum_cells(M_pi)=M_L",
    "physical_weight_identity": "M_pi*K=pi_h*V",
    "raw_axis_product_mass_identity": (
        "sum_cells(mu_midpoint*mu_relative_parallel*mu_relative_perpendicular)="
        "S_midpoint*S_relative_parallel*S_relative_perpendicular"
    ),
    "reconstructed_killed_multiplier": "B*K",
    "reconstructed_multiplier_direct": "K=V*pi_h/M_pi",
    "reconstructed_multiplier_via_ratio": "K=V/rho",
    "symbolic_killing_average": "V=W^-1*C_ab*sum_j(w_j*Phi_jm)",
    "tensor_conductance": "c_e=G*kappa_e*product_spectator_axis_mu",
    "tensor_rate": "q_tensor=c_e/pi_h",
}


class PreflightValidationError(ValueError):
    """Raised when a preflight invariant is violated."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(path: Path) -> bytes:
    """Retain one stable regular-file snapshot and reject symlinks."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise PreflightValidationError("O_NOFOLLOW is required")
    try:
        descriptor = os.open(path, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0))
    except OSError as exc:
        raise PreflightValidationError(
            f"cannot open regular file without following: {path}"
        ) from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise PreflightValidationError(f"regular file required: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        named = os.stat(path, follow_symlinks=False)
    finally:
        os.close(descriptor)
    signatures = (
        (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ),
        (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ),
    )
    if signatures[0] != signatures[1]:
        raise PreflightValidationError(f"file changed during snapshot: {path}")
    if (named.st_dev, named.st_ino) != (after.st_dev, after.st_ino):
        raise PreflightValidationError(f"path identity changed during snapshot: {path}")
    data = b"".join(chunks)
    if len(data) != after.st_size:
        raise PreflightValidationError(f"snapshot size mismatch: {path}")
    return data


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def type_exact_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON trees without Python's bool/int equality aliases."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            type_exact_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            type_exact_equal(left, right) for left, right in zip(actual, expected)
        )
    return actual == expected


def reject_number(token: str) -> None:
    raise PreflightValidationError(f"non-integer JSON number forbidden: {token}")


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PreflightValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(data: bytes, path: Path, *, require_canonical: bool) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=unique_pairs,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PreflightValidationError(f"strict JSON failure for {path}: {exc}") from exc
    if type(value) is not dict:
        raise PreflightValidationError(f"top-level object required: {path}")
    if require_canonical and canonical(value) != data:
        raise PreflightValidationError(f"canonical sorted JSON required: {path}")
    return value


def load_json(path: Path, *, require_canonical: bool = False) -> tuple[dict[str, Any], bytes]:
    data = snapshot(path)
    return decode(data, path, require_canonical=require_canonical), data


def safe_relative(text: Any) -> str:
    if (
        type(text) is not str
        or not text
        or "\\" in text
        or Path(text).is_absolute()
        or ".." in Path(text).parts
        or "." in Path(text).parts
    ):
        raise PreflightValidationError(f"unsafe report-relative path: {text!r}")
    return Path(text).as_posix()


def exact_false_map(value: Any, keys: set[str] | None, context: str) -> None:
    if type(value) is not dict or not value:
        raise PreflightValidationError(f"nonempty false map required: {context}")
    if keys is not None and set(value) != keys:
        raise PreflightValidationError(f"wrong false-map key set: {context}")
    if any(item is not False for item in value.values()):
        raise PreflightValidationError(f"promotion drift: {context}")


def pinned(role: str) -> dict[str, str]:
    path, sha = SOURCE_PINS[role]
    return {"path": path, "sha256": sha}


def generated(path: str, data: bytes) -> dict[str, str]:
    return {"path": path, "sha256": digest(data)}


def load_sources() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_sha) in SOURCE_PINS.items():
        path = REPORT / safe_relative(relative)
        data = snapshot(path)
        actual_sha = digest(data)
        if actual_sha != expected_sha:
            raise PreflightValidationError(
                f"source hash drift for {role}: {actual_sha} != {expected_sha}"
            )
        if role in JSON_ROLES:
            values[role] = decode(data, path, require_canonical=False)
    return values


def validate_source_semantics(sources: dict[str, dict[str, Any]]) -> None:
    configuration = sources["configuration_source"]
    legacy_member = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    stationary = sources["stationary_integral_source"]
    raw = sources["raw_flux_source"]
    killing = sources["killing_geometry_bundle"]
    if (
        configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or configuration.get("configuration_count") != 12
        or configuration.get("coordinate_order") != AXES
        or len(configuration.get("configurations", [])) != 12
    ):
        raise PreflightValidationError("configuration authority drift")
    if legacy_member.get(
        "schema"
    ) != "encounter_continuum_c1_c2_fixed_row_member_spec_v1" or legacy_member.get(
        "configuration_order"
    ) != configuration.get("configuration_order"):
        raise PreflightValidationError("legacy member specification drift")
    exact_false_map(legacy_member.get("claim_boundary"), None, "legacy member specification")
    if (
        refinement.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2"
        or refinement.get("sequence_count") != 12
        or refinement.get("sequence_order") != configuration.get("configuration_order")
    ):
        raise PreflightValidationError("joint refinement authority drift")
    exact_false_map(refinement.get("claim_boundary"), None, "joint refinement family")
    exact_false_map(stationary.get("claim_boundary"), None, "stationary source")
    exact_false_map(raw.get("claim_boundary"), None, "raw-flux source")
    if (
        killing.get("schema") != "encounter_control_free_production_killing_geometry_v1"
        or len(killing.get("rows", [])) != 12
    ):
        raise PreflightValidationError("killing bundle drift")

    factor_storage = killing.get("factorization_contract", {})
    expected_factor_storage = {
        "contact_flat_index_formula": "a*n_Y+b",
        "contact_logical_shape": ["n_R", "n_Y"],
        "full_flat_index_formula": "i=(i_M*n_R+i_R)*n_Y+i_Y",
        "full_logical_shape": ["n_M", "n_R", "n_Y"],
        "support_flat_index_formula": "i_M",
        "support_logical_shape_each": ["n_M"],
        "tensor_storage_order": (
            "full:midpoint_outer_relative_parallel_middle_relative_perpendicular_inner"
        ),
    }
    for key, expected in expected_factor_storage.items():
        if not type_exact_equal(factor_storage.get(key), expected):
            raise PreflightValidationError(f"killing factor storage drift: {key}")

    method = sources["method_registry"]
    missing = {
        "method_parameter_sha256",
        "producer_code_sha256",
        "verifier_code_sha256",
    }
    if (
        method.get("schema") != "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1"
        or len(method.get("methods", [])) != 4
        or any(not missing.isdisjoint(entry) for entry in method["methods"])
    ):
        raise PreflightValidationError("method registry gap/status drift")
    raw_binding = sources["raw_axis_binding"]
    if (
        raw_binding.get("schema") != "encounter_continuum_c1_raw_axis_production_binding_v1"
        or raw_binding.get("raw_role_binding", {}).get("tensor_storage_order")
        != "C:midpoint_outer_relative_parallel_middle_transverse_inner"
        or raw_binding.get("raw_role_binding", {}).get("saved_stationary_mass_role")
        != "ungauged_axis_primitive_mu_not_physical_cell_integral"
    ):
        raise PreflightValidationError("raw-axis storage/primitive semantics drift")
    exact_false_map(raw_binding.get("claim_boundary"), None, "raw-axis binding")
    sidecar = sources["killing_binding_sidecar"]
    if (
        sidecar.get("schema") != "encounter_continuum_c2_killing_geometry_production_binding_v1"
        or sidecar.get("status")
        != "FROZEN_KILLING_GEOMETRY_SOURCE_BINDING_ONLY_NO_CONCRETE_KILLING_NO_SAME_MEMBER"
    ):
        raise PreflightValidationError("weak killing sidecar drift")
    exact_false_map(sidecar.get("claim_boundary"), None, "weak killing sidecar")


def expected_member_spec(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    legacy = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    configuration = sources["configuration_source"]
    bindings: list[dict[str, Any]] = []
    for index, (semantic, sequence, config) in enumerate(
        zip(
            legacy["configuration_semantic_ids"],
            refinement["sequences"],
            configuration["configurations"],
        )
    ):
        axes: list[dict[str, Any]] = []
        for axis in sequence["axes"]:
            item = {
                "alignment": axis["alignment"],
                "anchor_size": axis["anchor_size"],
                "coordinate": axis["coordinate"],
            }
            if "periodic_shift_n0_exact" in axis:
                item["periodic_shift_n0_exact"] = axis["periodic_shift_n0_exact"]
            axes.append(item)
        bindings.append(
            {
                "authority_label": semantic["authority_label"],
                "configuration_index": index,
                "n0_anchor_expected_states": config["expected_states"],
                "n0_anchor_shape": config["shape"],
                "n0_axes": axes,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": sequence["source_row_canonical_sha256"],
                "sequence_source_row_index": sequence["source_row_index"],
            }
        )
    return {
        "claim_boundary": {
            "current_enclosure_sources_bind_this_v2_spec": False,
            "n0_partition_sha256s_bound": False,
            "one_correlated_distinguished_ideal_member_is_contained": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "configuration_order": legacy["configuration_order"],
        "configuration_semantic_ids": legacy["configuration_semantic_ids"],
        "member_semantics": {
            "configuration_count": 12,
            "coordinate_order": AXES,
            "joint_refinement_sequence_bound": True,
            "legacy_member_digest_is_not_v2_acceptance_identity": True,
            "n0_geometry_match_is_not_correlated_containment": True,
            "physical_dimension": 2,
            "quotient_dimension": 3,
        },
        "n0_sequence_bindings": bindings,
        "schema": "encounter_continuum_c1_c2_n0_member_spec_v2",
        "source_pins": {
            "configuration_source": pinned("configuration_source"),
            "factorization_source": pinned("factorization_source"),
            "ideal_formula_source": pinned("ideal_formula_source"),
            "joint_refinement_family": pinned("joint_refinement_family"),
            "legacy_member_spec": pinned("legacy_member_spec"),
            "reference_density_source": pinned("reference_density_source"),
        },
        "status": ("FROZEN_N0_SEQUENCE_BINDING_ONLY_NO_PARTITION_HASH_IDENTITY_NO_ORDERED_REPLAY"),
    }


def expected_policy(
    sources: dict[str, dict[str, Any]],
    member_bytes: bytes,
) -> dict[str, Any]:
    return {
        "claim_boundary": {
            "complete_C1": False,
            "complete_C2": False,
            "formal_production_bridge_accepted": False,
            "release_eligible": False,
        },
        "join_requirements": {
            "axis_order_exact": AXES,
            "axis_partition_path_sha_cell_count_equal": True,
            "cell_indices_contiguous_and_unique": True,
            "configuration_count_exactly_12": True,
            "configuration_index_and_label_unique": True,
            "edge_key": ["edge_index", "left_cell_index", "right_cell_index"],
            "edge_keys_unique": True,
            "killing_partition_path_sha_equal": True,
            "profile_index_order_exact": PROFILES,
            "raw_stationary_member_tuple_equal": True,
        },
        "ordering": {
            "current_enclosure_sources_eligible_for_acceptance": False,
            "future_replay_must_pin_this_exact_policy_sha256": True,
            "future_replay_required": True,
            "policy_predecessor_order_independently_sealed": False,
            "retroactive_acceptance_authorized": False,
            "this_policy_externally_sealed_before_current_enclosures": False,
            "timestamp_ordering_is_sufficient": False,
        },
        "requirements": sources["legacy_policy"]["requirements"],
        "schema": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v2",
        "source_pins": {
            "legacy_policy": pinned("legacy_policy"),
            "member_spec_v2": generated(MEMBER_SPEC_RELATIVE, member_bytes),
        },
        "status": (
            "FROZEN_PREFLIGHT_JOIN_POLICY_NOT_PREDECESSOR_SEALED_CURRENT_SOURCES_INELIGIBLE"
        ),
    }


def expected_control(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    basis = sources["killing_geometry_authority"]["support_basis"]
    return {
        "claim_boundary": {
            "actual_control_values_present": False,
            "budget_present": False,
            "complete_C0": False,
            "control_specific_killing_constructed": False,
            "exact_controls_present": False,
            "release_eligible": False,
            "science_executed": False,
        },
        "control_contract": {
            "control_count": 3,
            "control_ids": ["m1", "m2", "m3"],
            "each_weight_nonnegative": True,
            "exact_sum_one_required": True,
            "first_application_v1_strict_positivity_is_a_later_requirement": True,
            "finite_control_ids_only": True,
            "future_weight_representation": "reduced_exact_p_over_q",
            "future_weight_vector_length": 4,
        },
        "no_value_contract": {
            "actual_weight_rows": [],
            "budget_sources": [],
            "control_payload_paths": [],
            "result_or_positive_budget_sources": [],
        },
        "profile_basis_contract": {
            "profile_centres_exact_in_order": basis["centres_exact"],
            "profile_count": 4,
            "profile_index_order": PROFILES,
            "profile_ids_in_order": ["phi_0", "phi_1", "phi_2", "phi_3"],
        },
        "schema": "encounter_continuum_c1_symbolic_control_method_source_v1",
        "source_pins": {
            "control_method_commitment": pinned("control_method_commitment"),
            "factorization_source": pinned("factorization_source"),
            "killing_geometry_authority": pinned("killing_geometry_authority"),
        },
        "status": ("FROZEN_SYMBOLIC_CONTROL_METHOD_ROLE11_ONLY_NO_VALUES_NO_BUDGET_NO_COMPLETE_C0"),
        "symbolic_formula": "V_c_mab=W^-1*C_ab*sum_j(w_j^(c)*Phi_jm)",
    }


def primitive_manifest_sources(
    sources: dict[str, dict[str, Any]],
    member_bytes: bytes,
    policy_bytes: bytes,
    control_bytes: bytes,
) -> list[dict[str, str]]:
    return [
        {
            "path": SOURCE_PINS["reference_density_source"][0],
            "role": "reference_density_source",
            "schema": sources["reference_density_source"]["schema"],
            "sha256": SOURCE_PINS["reference_density_source"][1],
        },
        {
            "path": SOURCE_PINS["ideal_formula_source"][0],
            "role": "ideal_formula_source",
            "schema": sources["ideal_formula_source"]["schema"],
            "sha256": SOURCE_PINS["ideal_formula_source"][1],
        },
        {
            "path": SOURCE_PINS["factorization_source"][0],
            "role": "factorization_source",
            "schema": sources["factorization_source"]["schema"],
            "sha256": SOURCE_PINS["factorization_source"][1],
        },
        {
            "path": SOURCE_PINS["configuration_source"][0],
            "role": "configuration_source",
            "schema": sources["configuration_source"]["schema"],
            "sha256": SOURCE_PINS["configuration_source"][1],
        },
        {
            "path": MEMBER_SPEC_RELATIVE,
            "role": "member_spec_manifest",
            "schema": "encounter_continuum_c1_c2_n0_member_spec_v2",
            "sha256": digest(member_bytes),
        },
        {
            "path": SOURCE_PINS["method_registry"][0],
            "role": "outward_method_registry_source",
            "schema": sources["method_registry"]["schema"],
            "sha256": SOURCE_PINS["method_registry"][1],
        },
        {
            "path": POLICY_RELATIVE,
            "role": "anti_vacuity_policy_source",
            "schema": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v2",
            "sha256": digest(policy_bytes),
        },
        {
            "path": SOURCE_PINS["raw_flux_source"][0],
            "role": "raw_axis_enclosure_source",
            "schema": sources["raw_flux_source"]["schema"],
            "sha256": SOURCE_PINS["raw_flux_source"][1],
        },
        {
            "path": SOURCE_PINS["stationary_integral_source"][0],
            "role": "stationary_integral_source",
            "schema": sources["stationary_integral_source"]["schema"],
            "sha256": SOURCE_PINS["stationary_integral_source"][1],
        },
        {
            "path": SOURCE_PINS["killing_geometry_bundle"][0],
            "role": "killing_geometry_source",
            "schema": sources["killing_geometry_bundle"]["schema"],
            "sha256": SOURCE_PINS["killing_geometry_bundle"][1],
        },
        {
            "path": CONTROL_RELATIVE,
            "role": "symbolic_control_method_source",
            "schema": "encounter_continuum_c1_symbolic_control_method_source_v1",
            "sha256": digest(control_bytes),
        },
    ]


def validate_manifest_static(
    manifest: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    member_bytes: bytes,
    policy_bytes: bytes,
    control_bytes: bytes,
) -> dict[str, dict[str, str]]:
    expected_keys = {
        "claim_boundary",
        "forbidden_selected_roles",
        "preflight_role_catalog",
        "preflight_subordinate_inventory",
        "schema",
        "source_dependency_dag",
        "stage",
        "status",
        "supporting_evidence",
    }
    if set(manifest) != expected_keys:
        raise PreflightValidationError("preflight manifest top-level key drift")
    expected_claim_boundary = {
        "complete_process_report_file_open_closure": False,
        "formal_outer_open_operation_model_present": False,
        "outer_manifest_authorizes_itself": False,
        "production_payload_roles_1_through_11_formally_bound": False,
        "source_dependency_dag_complete": False,
        "symbolic_bridge_accepted": False,
    }
    if not type_exact_equal(manifest["claim_boundary"], expected_claim_boundary):
        raise PreflightValidationError("preflight manifest claim-boundary drift")
    exact_false_map(manifest["claim_boundary"], set(expected_claim_boundary), "preflight manifest")
    if (
        manifest["schema"] != "encounter_continuum_c1_n0_same_member_preflight_outer_manifest_v1"
        or manifest["stage"] != "production_n0_same_member_symbolic_preflight_only"
        or manifest["status"]
        != "PREFLIGHT_CATALOG_ONLY_NO_FORMAL_OUTER_OPEN_AUTHORITY_NO_ACCEPTANCE"
    ):
        raise PreflightValidationError("preflight manifest identity drift")
    if not type_exact_equal(
        manifest["forbidden_selected_roles"],
        {
            "budget_value_sources": [],
            "control_value_sources": [],
            "result_or_scratch_sources": [],
        },
    ):
        raise PreflightValidationError("forbidden source role drift")

    expected_primitives = primitive_manifest_sources(
        sources,
        member_bytes,
        policy_bytes,
        control_bytes,
    )
    catalog = manifest["preflight_role_catalog"]
    if not type_exact_equal(
        catalog,
        {
            "preflight_role_catalog_cardinality_11": True,
            "primitive_sources": expected_primitives,
        },
    ):
        raise PreflightValidationError("primitive role catalog drift")

    support_roles = [
        "legacy_member_spec",
        "legacy_policy",
        "raw_axis_binding",
        "stationary_integral_receipt",
        "raw_flux_receipt",
        "joint_refinement_family",
        "control_method_commitment",
        "killing_geometry_authority",
        "killing_binding_sidecar",
        "initial_bundle",
        "initial_independent_receipt",
        "initial_geometry_receipt",
        "initial_clean_replay",
        "killing_geometry_receipt",
        "bridge_design",
        "round170_audit",
        "round171_audit",
        "round172_audit",
    ]
    expected_support = [
        {
            "path": SOURCE_PINS[role][0],
            "role": role,
            "sha256": SOURCE_PINS[role][1],
        }
        for role in support_roles
    ]
    if not type_exact_equal(manifest["supporting_evidence"], expected_support):
        raise PreflightValidationError("supporting evidence catalog drift")

    expected_dag = {
        "edges": [
            ["reference_density_source", "member_spec_manifest"],
            ["ideal_formula_source", "member_spec_manifest"],
            ["factorization_source", "member_spec_manifest"],
            ["configuration_source", "member_spec_manifest"],
            ["member_spec_manifest", "anti_vacuity_policy_source"],
            ["factorization_source", "symbolic_control_method_source"],
        ],
        "nodes": [entry["role"] for entry in expected_primitives],
        "projection_complete_for_generated_preflight_sources": True,
        "projection_scope": "generated_member_policy_control_sources_only",
        "semantic_note": (
            "current roles 8 and 9 bind legacy member spec v1; no invented v2-to-current "
            "enclosure dependency edge"
        ),
        "support_dependencies_outside_projection": [
            ["control_method_commitment", "symbolic_control_method_source"],
            ["joint_refinement_family", "member_spec_manifest"],
            ["killing_geometry_authority", "symbolic_control_method_source"],
            ["legacy_member_spec", "member_spec_manifest"],
            ["legacy_policy", "anti_vacuity_policy_source"],
        ],
    }
    if not type_exact_equal(manifest["source_dependency_dag"], expected_dag):
        raise PreflightValidationError("source dependency DAG drift")
    if any(left == right for left, right in expected_dag["edges"]):
        raise PreflightValidationError("self-edge in source DAG")

    inventory = manifest["preflight_subordinate_inventory"]
    if type(inventory) is not list or len(inventory) != 48:
        raise PreflightValidationError("subordinate inventory must contain exactly 48 files")
    roles: dict[str, dict[str, str]] = {}
    paths: set[str] = set()
    for entry in inventory:
        if (
            type(entry) is not dict
            or set(entry) != {"path", "role", "sha256"}
            or type(entry["role"]) is not str
            or type(entry["sha256"]) is not str
            or len(entry["sha256"]) != 64
        ):
            raise PreflightValidationError("malformed subordinate inventory entry")
        safe_relative(entry["path"])
        if entry["role"] in roles or entry["path"] in paths:
            raise PreflightValidationError("duplicate subordinate role/path")
        roles[entry["role"]] = entry
        paths.add(entry["path"])
    if [entry["role"] for entry in inventory] != sorted(roles):
        raise PreflightValidationError("subordinate inventory order drift")
    return roles


def rational(text: Any) -> Fraction:
    if type(text) is not str or text.count("/") != 1:
        raise PreflightValidationError(f"canonical rational required: {text!r}")
    value = Fraction(text)
    if f"{value.numerator}/{value.denominator}" != text:
        raise PreflightValidationError(f"noncanonical rational: {text!r}")
    return value


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def independently_reconstructed_partition(axis: dict[str, Any]) -> dict[str, Any]:
    domain = axis["domain"]
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = rational(start_text)
    width = rational(width_text)
    end = start + width
    size = axis["anchor_size"]
    alignment = axis["alignment"]
    shift_text = axis.get("periodic_shift_n0_exact", "0/1")
    shift = rational(shift_text)

    if alignment == "cell_centred_reflecting":
        construction = "cell_centred_reflecting_scharfetter_gummel"
        periodic = False
        spacing = width / size
        positions = [start + (2 * index + 1) * spacing / 2 for index in range(size)]
        boundaries = [start + index * spacing for index in range(size + 1)]
        segments = [[[boundaries[index], boundaries[index + 1]]] for index in range(size)]
        volumes = [spacing] * size
        interval_count = size
    elif alignment == "vertex_centred_reflecting_dual":
        construction = "vertex_centred_reflecting_scharfetter_gummel"
        periodic = False
        spacing = width / (size - 1)
        positions = [start + index * spacing for index in range(size)]
        boundaries = [start]
        boundaries.extend((positions[index - 1] + positions[index]) / 2 for index in range(1, size))
        boundaries.append(end)
        segments = [[[boundaries[index], boundaries[index + 1]]] for index in range(size)]
        volumes = [boundaries[index + 1] - boundaries[index] for index in range(size)]
        interval_count = size - 1
    elif alignment in {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    }:
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment == "cell_centred_periodic_base"
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
        spacing = width / size
        positions = [
            start + ((index * spacing + spacing / 2 + shift) % width) for index in range(size)
        ]
        segments = []
        for position in positions:
            lower = position - spacing / 2
            upper = position + spacing / 2
            if lower < start:
                segments.append([[lower + width, end], [start, upper]])
            elif upper > end:
                segments.append([[lower, end], [start, upper - width]])
            else:
                segments.append([[lower, upper]])
        volumes = [spacing] * size
        interval_count = size
    else:
        raise PreflightValidationError(f"unknown Round172 alignment: {alignment}")

    if (
        axis["anchor_interval_count"] != interval_count
        or rational(axis["spacing_h0_exact"]) != spacing
    ):
        raise PreflightValidationError("Round172 spacing/interval-count drift")
    return {
        "cell_segments_exact": [
            [[rational_text(left), rational_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [rational_text(value) for value in volumes],
        "construction": construction,
        "coordinate": axis["coordinate"],
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [rational_text(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def partition_matches(axis: dict[str, Any], partition: dict[str, Any]) -> bool:
    return type_exact_equal(partition, independently_reconstructed_partition(axis))


def reconstruct_join_rows(
    sources: dict[str, dict[str, Any]],
    inventory: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    configs = sources["configuration_source"]["configurations"]
    semantics = sources["legacy_member_spec"]["configuration_semantic_ids"]
    sequences = sources["joint_refinement_family"]["sequences"]
    stationary_rows = sources["stationary_integral_source"]["rows"]
    raw_rows = sources["raw_flux_source"]["rows"]
    killing_rows = sources["killing_geometry_bundle"]["rows"]

    rows: list[dict[str, Any]] = []
    stationary_cells_total = 0
    raw_cells_total = 0
    edges_total = 0
    seam_total = 0
    used_inventory_roles: set[str] = set()

    for index, (config, semantic, sequence, stationary, raw, killing_index) in enumerate(
        zip(configs, semantics, sequences, stationary_rows, raw_rows, killing_rows)
    ):
        label = config["label"]
        if (
            stationary["configuration_index"] != index
            or raw["configuration_index"] != index
            or killing_index["configuration_index"] != index
            or sequence["source_row_index"] != index
            or semantic["authority_label"] != label
            or stationary["configuration_label"] != label
            or raw["configuration_label"] != label
            or killing_index["configuration_label"] != label
            or sequence["label"] != label
        ):
            raise PreflightValidationError(f"row identity mismatch at {index}")
        if (
            sequence["anchor_shape"] != config["shape"]
            or killing_index["shape"] != config["shape"]
            or sequence["anchor_expected_states"] != config["expected_states"]
            or killing_index["expected_states"] != config["expected_states"]
            or stationary["tensor_state_count"] != config["expected_states"]
            or raw["tensor_state_count"] != config["expected_states"]
        ):
            raise PreflightValidationError(f"row shape/state mismatch at {index}")

        stationary_member = (
            stationary["refinement_family_id"],
            stationary["refinement_member_id"],
            stationary["member_digest_sha256"],
        )
        raw_member = (
            raw["refinement_family_id"],
            raw["refinement_member_id"],
            raw["member_digest_sha256"],
        )
        if stationary_member != raw_member or stationary_member[:2] != (
            semantic["refinement_family_id"],
            semantic["refinement_member_id"],
        ):
            raise PreflightValidationError(f"legacy member mismatch at {index}")

        killing_role = f"killing_row_{index:02d}"
        killing_entry = inventory.get(killing_role)
        expected_killing_path = (
            "artifacts/data/physical_production_killing_geometry_v1/"
            + killing_index["row_manifest"]["path"]
        )
        if killing_entry != {
            "path": expected_killing_path,
            "role": killing_role,
            "sha256": killing_index["row_manifest"]["sha256"],
        }:
            raise PreflightValidationError(f"killing inventory mismatch at {index}")
        killing_data = snapshot(REPORT / safe_relative(killing_entry["path"]))
        if digest(killing_data) != killing_entry["sha256"]:
            raise PreflightValidationError(f"killing row digest mismatch at {index}")
        killing = decode(
            killing_data,
            REPORT / killing_entry["path"],
            require_canonical=False,
        )
        used_inventory_roles.add(killing_role)
        if (
            killing["configuration_index"] != index
            or killing["configuration_label"] != label
            or killing["shape"] != config["shape"]
            or killing["expected_states"] != config["expected_states"]
            or killing["row_relation_sha256"] != killing_index["row_relation_sha256"]
            or [item["profile_index"] for item in killing["support_densities"]] != PROFILES
        ):
            raise PreflightValidationError(f"killing row semantics mismatch at {index}")
        contact_manifest = killing["contact_fraction_relative"]["manifest"]
        support_manifests = [entry["manifest"] for entry in killing["support_densities"]]
        if (
            contact_manifest.get("logical_shape") != config["shape"][1:]
            or contact_manifest.get("record_count") != config["shape"][1] * config["shape"][2]
            or any(
                manifest.get("logical_shape") != [config["shape"][0]]
                or manifest.get("record_count") != config["shape"][0]
                for manifest in support_manifests
            )
        ):
            raise PreflightValidationError(f"killing factor shape mismatch at {index}")

        axes: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(AXES):
            s_axis = stationary["axes"][axis_index]
            r_axis = raw["axes"][axis_index]
            sequence_axis = sequence["axes"][axis_index]
            killing_axis = killing["partition_source"]["partitions"][axis_index]
            partition_path = s_axis["partition_path"]
            partition_sha = s_axis["partition_sha256"]
            if (
                s_axis["coordinate"] != coordinate
                or r_axis["coordinate"] != coordinate
                or sequence_axis["coordinate"] != coordinate
                or killing_axis["coordinate"] != coordinate
                or r_axis["partition_path"] != partition_path
                or r_axis["partition_sha256"] != partition_sha
                or killing_axis["file"]["path"] != partition_path
                or killing_axis["file"]["sha256"] != partition_sha
                or s_axis["cell_count"] != r_axis["cell_count"]
                or s_axis["cell_count"] != sequence_axis["anchor_size"]
            ):
                raise PreflightValidationError(f"axis tuple mismatch at {index}:{coordinate}")

            role = f"initial_partition_{index:02d}_{coordinate}"
            entry = inventory.get(role)
            expected_path = "artifacts/data/physical_production_initial_stream_v1/" + partition_path
            if entry != {
                "path": expected_path,
                "role": role,
                "sha256": partition_sha,
            }:
                raise PreflightValidationError(
                    f"partition inventory mismatch at {index}:{coordinate}"
                )
            partition_data = snapshot(REPORT / safe_relative(entry["path"]))
            if digest(partition_data) != entry["sha256"]:
                raise PreflightValidationError(f"partition digest mismatch at {index}:{coordinate}")
            partition = decode(
                partition_data,
                REPORT / entry["path"],
                require_canonical=False,
            )
            used_inventory_roles.add(role)
            if not partition_matches(sequence_axis, partition):
                raise PreflightValidationError(
                    f"independent n0 geometry mismatch at {index}:{coordinate}"
                )

            cell_count = s_axis["cell_count"]
            stationary_indices = [item.get("cell_index") for item in s_axis["cell_mass_intervals"]]
            raw_indices = [item.get("cell_index") for item in r_axis["cell_records"]]
            if stationary_indices != list(range(cell_count)) or raw_indices != list(
                range(cell_count)
            ):
                raise PreflightValidationError(f"cell identity mismatch at {index}:{coordinate}")
            expected_edges = [(edge, edge, edge + 1) for edge in range(cell_count - 1)]
            if r_axis["periodic"]:
                expected_edges.append((cell_count - 1, cell_count - 1, 0))
                seam_total += 1
            observed_edges = [
                (
                    item.get("edge_index"),
                    item.get("left_cell_index"),
                    item.get("right_cell_index"),
                )
                for item in r_axis["edge_records"]
            ]
            if observed_edges != expected_edges:
                raise PreflightValidationError(f"edge identity mismatch at {index}:{coordinate}")

            stationary_cells_total += len(stationary_indices)
            raw_cells_total += len(raw_indices)
            edges_total += len(observed_edges)
            axes.append(
                {
                    "alignment": sequence_axis["alignment"],
                    "cell_count": cell_count,
                    "cell_indices_contiguous_and_unique": True,
                    "coordinate": coordinate,
                    "edge_keys_contiguous_unique_and_oriented": True,
                    "n0_geometry_independently_matches_partition_bytes": True,
                    "partition_bundle_relative_path": partition_path,
                    "partition_report_relative_path": expected_path,
                    "partition_sha256": partition_sha,
                    "periodic": r_axis["periodic"],
                    "raw_stationary_partition_tuple_equal": True,
                }
            )

        rows.append(
            {
                "configuration_index": index,
                "configuration_label": label,
                "killing_configuration_shape_state_join_visible": True,
                "killing_partition_join_reconstructed": True,
                "killing_profile_index_order": PROFILES,
                "killing_row_manifest_path": expected_killing_path,
                "killing_row_manifest_sha256": killing_index["row_manifest"]["sha256"],
                "legacy_member_digests_equal": True,
                "legacy_raw_flux_member_digest_sha256": raw_member[2],
                "legacy_stationary_member_digest_sha256": stationary_member[2],
                "n0_axes": axes,
                "n0_shape": config["shape"],
                "n0_state_count": config["expected_states"],
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "same_member_contained": False,
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": sequence["source_row_canonical_sha256"],
                "v2_ordered_replay_present": False,
            }
        )

    if used_inventory_roles != set(inventory):
        raise PreflightValidationError("subordinate inventory has unused or missing roles")
    counts = {
        "axis_join_count": 36,
        "configuration_join_count": 12,
        "killing_profile_join_count": 48,
        "periodic_seam_edge_count": seam_total,
        "raw_axis_cell_record_count": raw_cells_total,
        "raw_axis_edge_record_count": edges_total,
        "stationary_axis_cell_record_count": stationary_cells_total,
    }
    expected_counts = {
        "axis_join_count": 36,
        "configuration_join_count": 12,
        "killing_profile_join_count": 48,
        "periodic_seam_edge_count": 12,
        "raw_axis_cell_record_count": 5037,
        "raw_axis_edge_record_count": 5013,
        "stationary_axis_cell_record_count": 5037,
    }
    if counts != expected_counts:
        raise PreflightValidationError(f"record-count drift: {counts}")
    return rows, counts


def validate_candidate(
    candidate: dict[str, Any],
    candidate_bytes: bytes,
    rows: list[dict[str, Any]],
    counts: dict[str, int],
    member_bytes: bytes,
    policy_bytes: bytes,
    control_bytes: bytes,
    manifest_bytes: bytes,
) -> None:
    expected_keys = {
        "blocking_conditions",
        "claim_boundary",
        "configuration_join_rows",
        "expression_dag_contract",
        "member_semantics",
        "role_binding_summary",
        "schema",
        "source_bindings",
        "status",
        "validation_scope",
    }
    if set(candidate) != expected_keys:
        raise PreflightValidationError("candidate top-level key drift")
    if candidate[
        "schema"
    ] != "encounter_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1" or candidate[
        "status"
    ] != ("PASS_METADATA_PREFLIGHT_ONLY_CORRELATED_MEMBER_AND_FORMAL_CANDIDATE_ACCEPTANCE_FALSE"):
        raise PreflightValidationError("candidate identity/status drift")
    exact_false_map(candidate["claim_boundary"], CLAIM_KEYS, "candidate claim boundary")
    if not type_exact_equal(candidate["configuration_join_rows"], rows):
        raise PreflightValidationError("candidate configuration join rows drift")

    blockers = candidate["blocking_conditions"]
    if (
        type(blockers) is not list
        or len(blockers) != 9
        or [item.get("blocker_id") for item in blockers] != EXPECTED_BLOCKER_IDS
        or [item.get("required_future_action") for item in blockers] != EXPECTED_BLOCKER_ACTIONS
        or any(
            type(item) is not dict
            or set(item) != {"blocker_id", "cleared", "required_future_action"}
            or item["cleared"] is not False
            or type(item["required_future_action"]) is not str
            or not item["required_future_action"]
            for item in blockers
        )
    ):
        raise PreflightValidationError("candidate blocker ledger drift")

    if not type_exact_equal(
        candidate["expression_dag_contract"],
        {
            "all_identities_interval_replayed": False,
            "discrete_and_reconstructed_killing_are_distinct": True,
            "expressions": EXPECTED_DAG,
            "selected_required_symbolic_identities_declared": True,
        },
    ):
        raise PreflightValidationError("expression DAG contract drift")
    if (
        candidate["expression_dag_contract"]["expressions"]["discrete_killing_diagonal"]
        == candidate["expression_dag_contract"]["expressions"]["reconstructed_killed_multiplier"]
    ):
        raise PreflightValidationError("discrete and reconstructed killing were conflated")

    expected_member_semantics = {
        "every_cartesian_interval_member_is_a_model": False,
        "geometric_n0_equality_is_not_correlated_containment": True,
        "legacy_marginal_member_tuple_joined": True,
        "one_correlated_distinguished_ideal_member_is_contained": False,
        "retrospective_join_cannot_repair_predecessor_order": True,
    }
    if not type_exact_equal(candidate["member_semantics"], expected_member_semantics):
        raise PreflightValidationError("candidate member semantics drift")

    expected_summary = {
        "all_12_configuration_index_label_shape_state_joins_visible": True,
        "all_36_raw_stationary_partition_tuple_joins_visible": True,
        "all_36_round172_n0_geometries_reconstructed_from_partition_bytes": True,
        "all_48_killing_profile_indices_in_frozen_order": True,
        "all_cell_and_edge_keys_contiguous_unique_and_oriented": True,
        "contact_factor_storage": {
            "flat_index_formula": "a*n_Y+b",
            "logical_shape": ["n_R", "n_Y"],
        },
        "counts": counts,
        "full_tensor_storage": {
            "flat_index_formula": "i=(i_M*n_R+i_R)*n_Y+i_Y",
            "logical_shape": ["n_M", "n_R", "n_Y"],
            "storage_order": (
                "full:midpoint_outer_relative_parallel_middle_relative_perpendicular_inner"
            ),
        },
        "killing_binding_sidecar_is_receipt_or_candidate": False,
        "killing_factor_array_shapes_visible": True,
        "method_registry_complete_for_formal_bridge": False,
        "method_registry_missing_required_fields": [
            "method_parameter_sha256",
            "producer_code_sha256",
            "verifier_code_sha256",
        ],
        "preflight_role_catalog_cardinality": 11,
        "production_payload_roles_1_through_11_formally_bound": False,
        "round172_contains_partition_sha256": False,
        "support_factor_storage": {
            "flat_index_formula": "i_M",
            "logical_shape_each": ["n_M"],
        },
    }
    if not type_exact_equal(candidate["role_binding_summary"], expected_summary):
        raise PreflightValidationError("candidate role-binding summary drift")

    expected_bindings = {
        "builder_source": {
            "path": BUILDER_RELATIVE,
            "sha256": digest(snapshot(REPORT / BUILDER_RELATIVE)),
        },
        "control_method_source": generated(CONTROL_RELATIVE, control_bytes),
        "member_spec_v2": generated(MEMBER_SPEC_RELATIVE, member_bytes),
        "outer_manifest": generated(MANIFEST_RELATIVE, manifest_bytes),
        "policy_v2": generated(POLICY_RELATIVE, policy_bytes),
        "validator_source": {
            "path": str(SELF.relative_to(REPORT)),
            "sha256": digest(snapshot(SELF)),
        },
    }
    if not type_exact_equal(candidate["source_bindings"], expected_bindings):
        raise PreflightValidationError("candidate source binding drift")
    if not type_exact_equal(
        candidate["validation_scope"],
        {
            "authenticated_execution_attested": False,
            "complete_process_open_closure": False,
            "hostile_writer_atomicity_claimed": False,
            "independent_numerical_backend": False,
            "join_subordinate_json_files_preflight_catalogued": True,
            "largest_tensor_materialized": False,
            "network_access_used": False,
            "positive_budget_or_result_payload_read": False,
            "python_stdlib_only": True,
        },
    ):
        raise PreflightValidationError("candidate validation-scope drift")
    if canonical(candidate) != candidate_bytes:
        raise PreflightValidationError("candidate snapshot was not canonical")


def validate_package(
    *,
    member_spec_path: Path = DEFAULT_MEMBER_SPEC,
    policy_path: Path = DEFAULT_POLICY,
    control_path: Path = DEFAULT_CONTROL,
    manifest_path: Path = DEFAULT_MANIFEST,
    candidate_path: Path = DEFAULT_CANDIDATE,
) -> tuple[str, dict[str, int]]:
    sources = load_sources()
    validate_source_semantics(sources)
    member, member_bytes = load_json(member_spec_path, require_canonical=True)
    policy, policy_bytes = load_json(policy_path, require_canonical=True)
    control, control_bytes = load_json(control_path, require_canonical=True)
    manifest, manifest_bytes = load_json(manifest_path, require_canonical=True)
    candidate, candidate_bytes = load_json(candidate_path, require_canonical=True)

    expected_member = expected_member_spec(sources)
    if not type_exact_equal(member, expected_member):
        raise PreflightValidationError("member specification does not reconstruct exactly")
    exact_false_map(member["claim_boundary"], None, "member specification")
    expected_policy_value = expected_policy(sources, member_bytes)
    if not type_exact_equal(policy, expected_policy_value):
        raise PreflightValidationError("anti-vacuity policy does not reconstruct exactly")
    exact_false_map(policy["claim_boundary"], None, "anti-vacuity policy")
    if any(
        policy["ordering"][key] is not False
        for key in (
            "current_enclosure_sources_eligible_for_acceptance",
            "policy_predecessor_order_independently_sealed",
            "retroactive_acceptance_authorized",
            "this_policy_externally_sealed_before_current_enclosures",
            "timestamp_ordering_is_sufficient",
        )
    ) or any(
        policy["ordering"][key] is not True
        for key in (
            "future_replay_must_pin_this_exact_policy_sha256",
            "future_replay_required",
        )
    ):
        raise PreflightValidationError("anti-vacuity ordering drift")

    expected_control_value = expected_control(sources)
    if not type_exact_equal(control, expected_control_value):
        raise PreflightValidationError("symbolic control method does not reconstruct exactly")
    exact_false_map(control["claim_boundary"], None, "symbolic control method")
    if any(control["no_value_contract"].values()):
        raise PreflightValidationError("symbolic control method contains values or payload paths")

    inventory = validate_manifest_static(
        manifest,
        sources,
        member_bytes,
        policy_bytes,
        control_bytes,
    )
    rows, counts = reconstruct_join_rows(sources, inventory)
    validate_candidate(
        candidate,
        candidate_bytes,
        rows,
        counts,
        member_bytes,
        policy_bytes,
        control_bytes,
        manifest_bytes,
    )
    return digest(candidate_bytes), counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--member-spec", type=Path, default=DEFAULT_MEMBER_SPEC)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--control", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    arguments = parser.parse_args()
    try:
        candidate_sha, counts = validate_package(
            member_spec_path=arguments.member_spec,
            policy_path=arguments.policy,
            control_path=arguments.control,
            manifest_path=arguments.manifest,
            candidate_path=arguments.candidate,
        )
        print(
            "PASS_N0_SAME_MEMBER_PREFLIGHT_VALIDATION "
            f"candidate_sha256={candidate_sha} "
            f"configuration_joins={counts['configuration_join_count']} "
            f"axis_joins={counts['axis_join_count']} "
            f"cell_records={counts['raw_axis_cell_record_count']} "
            f"edge_records={counts['raw_axis_edge_record_count']} "
            "blockers=9 correlated_member=false formal_candidate=false release=false"
        )
        return 0
    except (OSError, KeyError, TypeError, PreflightValidationError) as exc:
        print(f"ERROR N0SameMemberPreflightValidation: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
