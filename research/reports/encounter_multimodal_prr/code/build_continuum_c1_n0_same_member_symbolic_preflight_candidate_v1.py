#!/usr/bin/env python3
"""Build the non-promoting production n=0 same-member preflight package.

This builder performs only control-free, factorized metadata and exact-index
checks.  It does not construct the formal symbolic candidate reserved by the
Round-6 design, does not execute science, and cannot issue an acceptance
receipt.  In particular, the current stationary and raw-flux sources still
bind the legacy v1 member specification and predate no independently sealed
successor policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

SELF = Path(__file__).resolve()
REPORT = SELF.parents[1]

MEMBER_SPEC_PATH = "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json"
POLICY_PATH = "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json"
CONTROL_METHOD_PATH = "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json"
MANIFEST_PATH = "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json"
CANDIDATE_PATH = "artifacts/data/continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json"
VALIDATOR_PATH = "code/validate_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"

OUTPUT_PATHS = (
    MEMBER_SPEC_PATH,
    POLICY_PATH,
    CONTROL_METHOD_PATH,
    MANIFEST_PATH,
    CANDIDATE_PATH,
)

CORE_SOURCES: dict[str, tuple[str, str]] = {
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

JSON_SOURCE_ROLES = frozenset(
    role for role, (path, _) in CORE_SOURCES.items() if path.endswith(".json")
)
AXIS_ORDER = ["midpoint", "relative_parallel", "relative_perpendicular"]
PROFILE_ORDER = [0, 1, 2, 3]

CLAIM_KEYS = (
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
)

BLOCKERS = [
    {
        "blocker_id": "B01_current_roles_8_9_bind_legacy_member_spec_v1",
        "cleared": False,
        "required_future_action": (
            "regenerate stationary and raw-flux roles under a predecessor-sealed successor "
            "member specification"
        ),
    },
    {
        "blocker_id": "B02_policy_predecessor_order_not_independently_sealed",
        "cleared": False,
        "required_future_action": (
            "freeze an externally authenticated policy before any acceptance replay"
        ),
    },
    {
        "blocker_id": "B03_current_enclosures_predate_no_sealed_v2_policy",
        "cleared": False,
        "required_future_action": "perform a new ordered result-blind replay",
    },
    {
        "blocker_id": "B04_round172_has_no_partition_sha256",
        "cleared": False,
        "required_future_action": (
            "bind independently reconstructed n0 partition hashes in a future member identity"
        ),
    },
    {
        "blocker_id": "B05_killing_rows_lack_member_native_provenance",
        "cleared": False,
        "required_future_action": (
            "regenerate killing native records with refinement, member, partition, formula, "
            "method, normalization, unit, and record digests"
        ),
    },
    {
        "blocker_id": "B06_method_registry_missing_code_and_parameter_hashes",
        "cleared": False,
        "required_future_action": (
            "publish a successor registry with producer, verifier, and method-parameter hashes"
        ),
    },
    {
        "blocker_id": "B07_formal_outer_open_operation_model_and_complete_dag_absent",
        "cleared": False,
        "required_future_action": (
            "freeze an external operation model and a complete selected-source dependency DAG"
        ),
    },
    {
        "blocker_id": "B08_exact_dag_interval_replay_absent",
        "cleared": False,
        "required_future_action": (
            "stream and independently replay the exact gauge, flux, map, and killing DAG"
        ),
    },
    {
        "blocker_id": "B09_independent_symbolic_acceptance_receipt_absent",
        "cleared": False,
        "required_future_action": (
            "issue a distinct receipt only after the correlated replay passes"
        ),
    },
]

EXPRESSION_DAG = {
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def descriptor_snapshot(path: Path) -> bytes:
    """Read one stable regular-file snapshot without following a symlink."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("O_NOFOLLOW is required")
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
        named = os.stat(path, follow_symlinks=False)
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
        raise ValueError(f"file changed during snapshot: {path}")
    if (named.st_dev, named.st_ino) != (after.st_dev, after.st_ino):
        raise ValueError(f"path identity changed during snapshot: {path}")
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


def parse_json(data: bytes, path: Path, *, require_canonical: bool = False) -> dict[str, Any]:
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
    if require_canonical and canonical_bytes(value) != data:
        raise ValueError(f"canonical sorted JSON required: {path}")
    return value


def require_false_map(value: Any, context: str) -> None:
    if type(value) is not dict or not value or any(item is not False for item in value.values()):
        raise ValueError(f"exact false flag map required: {context}")


def safe_relative(path: str) -> str:
    if (
        type(path) is not str
        or not path
        or "\\" in path
        or Path(path).is_absolute()
        or ".." in Path(path).parts
        or "." in Path(path).parts
    ):
        raise ValueError(f"unsafe report-relative path: {path!r}")
    return Path(path).as_posix()


def load_core_sources() -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    parsed: dict[str, dict[str, Any]] = {}
    snapshots: dict[str, bytes] = {}
    for role, (relative, expected_digest) in CORE_SOURCES.items():
        path = REPORT / safe_relative(relative)
        data = descriptor_snapshot(path)
        actual_digest = sha256(data)
        if actual_digest != expected_digest:
            raise ValueError(f"source hash drift for {role}: {actual_digest} != {expected_digest}")
        snapshots[role] = data
        if role in JSON_SOURCE_ROLES:
            parsed[role] = parse_json(data, path)
    return parsed, snapshots


def source_pin(role: str) -> dict[str, str]:
    path, digest = CORE_SOURCES[role]
    return {"path": path, "sha256": digest}


def generated_pin(path: str, value: dict[str, Any]) -> dict[str, str]:
    return {"path": path, "sha256": sha256(canonical_bytes(value))}


def validate_core_semantics(sources: dict[str, dict[str, Any]]) -> None:
    configuration = sources["configuration_source"]
    legacy_member = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    stationary = sources["stationary_integral_source"]
    raw = sources["raw_flux_source"]
    killing = sources["killing_geometry_bundle"]

    if (
        configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or configuration.get("configuration_count") != 12
        or configuration.get("coordinate_order") != AXIS_ORDER
        or len(configuration.get("configurations", [])) != 12
    ):
        raise ValueError("configuration authority drift")
    if (
        legacy_member.get("schema") != "encounter_continuum_c1_c2_fixed_row_member_spec_v1"
        or legacy_member.get("configuration_order") != configuration.get("configuration_order")
        or len(legacy_member.get("configuration_semantic_ids", [])) != 12
    ):
        raise ValueError("legacy member specification drift")
    require_false_map(legacy_member.get("claim_boundary"), "legacy member specification")
    if (
        refinement.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2"
        or refinement.get("sequence_count") != 12
        or refinement.get("sequence_order") != configuration.get("configuration_order")
        or len(refinement.get("sequences", [])) != 12
    ):
        raise ValueError("joint refinement authority drift")
    require_false_map(refinement.get("claim_boundary"), "joint refinement family")
    if (
        stationary.get("schema") != "encounter_continuum_c1_stationary_integral_source_v1"
        or raw.get("schema") != "encounter_continuum_c1_fixed_row_raw_flux_source_v1"
        or len(stationary.get("rows", [])) != 12
        or len(raw.get("rows", [])) != 12
    ):
        raise ValueError("stationary/raw source drift")
    require_false_map(stationary.get("claim_boundary"), "stationary source")
    require_false_map(raw.get("claim_boundary"), "raw-flux source")
    if (
        killing.get("schema") != "encounter_control_free_production_killing_geometry_v1"
        or len(killing.get("rows", [])) != 12
    ):
        raise ValueError("killing bundle drift")
    factor_storage = killing.get("factorization_contract", {})
    if (
        factor_storage.get("contact_flat_index_formula") != "a*n_Y+b"
        or factor_storage.get("contact_logical_shape") != ["n_R", "n_Y"]
        or factor_storage.get("support_flat_index_formula") != "i_M"
        or factor_storage.get("support_logical_shape_each") != ["n_M"]
        or factor_storage.get("full_flat_index_formula") != "i=(i_M*n_R+i_R)*n_Y+i_Y"
        or factor_storage.get("full_logical_shape") != ["n_M", "n_R", "n_Y"]
        or factor_storage.get("tensor_storage_order")
        != "full:midpoint_outer_relative_parallel_middle_relative_perpendicular_inner"
    ):
        raise ValueError("killing factorization storage contract drift")

    policy = sources["legacy_policy"]
    if (
        policy.get("schema") != "encounter_continuum_c1_c2_fixed_row_anti_vacuity_policy_v1"
        or policy.get("claim_boundary", {}).get("policy_predecessor_order_independently_sealed")
        is not False
    ):
        raise ValueError("legacy policy ordering drift")
    method = sources["method_registry"]
    if (
        method.get("schema") != "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1"
        or len(method.get("methods", [])) != 4
    ):
        raise ValueError("method registry drift")
    missing = {
        "producer_code_sha256",
        "verifier_code_sha256",
        "method_parameter_sha256",
    }
    if any(not missing.isdisjoint(entry) for entry in method["methods"]):
        raise ValueError("method-registry gap unexpectedly changed")

    binding = sources["killing_binding_sidecar"]
    if (
        binding.get("schema") != "encounter_continuum_c2_killing_geometry_production_binding_v1"
        or binding.get("status")
        != "FROZEN_KILLING_GEOMETRY_SOURCE_BINDING_ONLY_NO_CONCRETE_KILLING_NO_SAME_MEMBER"
    ):
        raise ValueError("weak killing-binding sidecar drift")
    require_false_map(binding.get("claim_boundary"), "weak killing-binding sidecar")
    raw_binding = sources["raw_axis_binding"]
    if (
        raw_binding.get("schema") != "encounter_continuum_c1_raw_axis_production_binding_v1"
        or raw_binding.get("raw_role_binding", {}).get("tensor_storage_order")
        != "C:midpoint_outer_relative_parallel_middle_transverse_inner"
        or raw_binding.get("raw_role_binding", {}).get("saved_stationary_mass_role")
        != "ungauged_axis_primitive_mu_not_physical_cell_integral"
    ):
        raise ValueError("raw-axis storage/primitive semantics drift")
    require_false_map(raw_binding.get("claim_boundary"), "raw-axis binding")


def rational(text: Any) -> Fraction:
    if type(text) is not str or text.count("/") != 1:
        raise ValueError(f"canonical rational required: {text!r}")
    value = Fraction(text)
    if f"{value.numerator}/{value.denominator}" != text:
        raise ValueError(f"noncanonical rational: {text!r}")
    return value


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def expected_partition_geometry(sequence_axis: dict[str, Any]) -> dict[str, Any]:
    domain = sequence_axis["domain"]
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = rational(start_text)
    width = rational(width_text)
    end = start + width
    size = sequence_axis["anchor_size"]
    alignment = sequence_axis["alignment"]
    shift_text = sequence_axis.get("periodic_shift_n0_exact", "0/1")
    shift = rational(shift_text)

    if alignment == "cell_centred_reflecting":
        construction = "cell_centred_reflecting_scharfetter_gummel"
        periodic = False
        spacing = width / size
        positions = [start + (index * 2 + 1) * spacing / 2 for index in range(size)]
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
        raise ValueError(f"unknown Round172 alignment: {alignment}")

    if (
        sequence_axis["anchor_interval_count"] != interval_count
        or rational(sequence_axis["spacing_h0_exact"]) != spacing
    ):
        raise ValueError("Round172 spacing/interval-count drift")
    return {
        "cell_segments_exact": [
            [[rational_text(left), rational_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [rational_text(value) for value in volumes],
        "construction": construction,
        "coordinate": sequence_axis["coordinate"],
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [rational_text(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def partition_geometry_matches(sequence_axis: dict[str, Any], partition: dict[str, Any]) -> bool:
    return partition == expected_partition_geometry(sequence_axis)


def subordinate_snapshot(
    report_relative: str,
    expected_digest: str,
    snapshots: dict[str, bytes],
) -> dict[str, Any]:
    relative = safe_relative(report_relative)
    data = descriptor_snapshot(REPORT / relative)
    digest = sha256(data)
    if digest != expected_digest:
        raise ValueError(f"subordinate source drift for {relative}: {digest} != {expected_digest}")
    snapshots[relative] = data
    return parse_json(data, REPORT / relative)


def build_join_rows(
    sources: dict[str, dict[str, Any]],
    subordinate_snapshots: dict[str, bytes],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    configuration = sources["configuration_source"]
    legacy_member = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    stationary = sources["stationary_integral_source"]
    raw = sources["raw_flux_source"]
    killing_bundle = sources["killing_geometry_bundle"]

    rows: list[dict[str, Any]] = []
    subordinate_inventory: list[dict[str, str]] = []
    stationary_cell_count = 0
    raw_cell_count = 0
    raw_edge_count = 0
    periodic_seam_count = 0

    for index in range(12):
        config = configuration["configurations"][index]
        semantic = legacy_member["configuration_semantic_ids"][index]
        sequence = refinement["sequences"][index]
        stationary_row = stationary["rows"][index]
        raw_row = raw["rows"][index]
        killing_index = killing_bundle["rows"][index]

        label = config["label"]
        shape = config["shape"]
        states = config["expected_states"]
        if (
            index != stationary_row.get("configuration_index")
            or index != raw_row.get("configuration_index")
            or index != killing_index.get("configuration_index")
            or index != sequence.get("source_row_index")
            or label != semantic.get("authority_label")
            or label != sequence.get("label")
            or label != stationary_row.get("configuration_label")
            or label != raw_row.get("configuration_label")
            or label != killing_index.get("configuration_label")
        ):
            raise ValueError(f"configuration join failure at row {index}")
        if (
            shape != sequence.get("anchor_shape")
            or shape != killing_index.get("shape")
            or states != sequence.get("anchor_expected_states")
            or states != stationary_row.get("tensor_state_count")
            or states != raw_row.get("tensor_state_count")
            or states != killing_index.get("expected_states")
        ):
            raise ValueError(f"shape/state join failure at row {index}")

        family = semantic["refinement_family_id"]
        member = semantic["refinement_member_id"]
        stationary_member = (
            stationary_row["refinement_family_id"],
            stationary_row["refinement_member_id"],
            stationary_row["member_digest_sha256"],
        )
        raw_member = (
            raw_row["refinement_family_id"],
            raw_row["refinement_member_id"],
            raw_row["member_digest_sha256"],
        )
        if stationary_member != raw_member or stationary_member[:2] != (family, member):
            raise ValueError(f"legacy member tuple join failure at row {index}")

        killing_manifest = killing_index["row_manifest"]
        killing_relative = (
            "artifacts/data/physical_production_killing_geometry_v1/" + killing_manifest["path"]
        )
        killing_row = subordinate_snapshot(
            killing_relative,
            killing_manifest["sha256"],
            subordinate_snapshots,
        )
        subordinate_inventory.append(
            {
                "path": killing_relative,
                "role": f"killing_row_{index:02d}",
                "sha256": killing_manifest["sha256"],
            }
        )
        if (
            killing_row.get("configuration_index") != index
            or killing_row.get("configuration_label") != label
            or killing_row.get("shape") != shape
            or killing_row.get("expected_states") != states
            or killing_row.get("row_relation_sha256") != killing_index.get("row_relation_sha256")
        ):
            raise ValueError(f"killing row join failure at row {index}")
        profile_indices = [entry.get("profile_index") for entry in killing_row["support_densities"]]
        if profile_indices != PROFILE_ORDER:
            raise ValueError(f"killing profile order failure at row {index}")
        contact_manifest = killing_row["contact_fraction_relative"]["manifest"]
        support_manifests = [entry["manifest"] for entry in killing_row["support_densities"]]
        if (
            contact_manifest.get("logical_shape") != shape[1:]
            or contact_manifest.get("record_count") != shape[1] * shape[2]
            or any(
                manifest.get("logical_shape") != [shape[0]]
                or manifest.get("record_count") != shape[0]
                for manifest in support_manifests
            )
        ):
            raise ValueError(f"killing factor storage-shape failure at row {index}")

        stationary_axes = stationary_row["axes"]
        raw_axes = raw_row["axes"]
        sequence_axes = sequence["axes"]
        killing_partitions = killing_row["partition_source"]["partitions"]
        if not (
            len(stationary_axes)
            == len(raw_axes)
            == len(sequence_axes)
            == len(killing_partitions)
            == 3
        ):
            raise ValueError(f"axis cardinality failure at row {index}")

        axis_receipts: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(AXIS_ORDER):
            stationary_axis = stationary_axes[axis_index]
            raw_axis = raw_axes[axis_index]
            sequence_axis = sequence_axes[axis_index]
            killing_axis = killing_partitions[axis_index]
            partition_path = stationary_axis["partition_path"]
            partition_sha = stationary_axis["partition_sha256"]
            partition_file = killing_axis["file"]
            if (
                stationary_axis["coordinate"] != coordinate
                or raw_axis["coordinate"] != coordinate
                or sequence_axis["coordinate"] != coordinate
                or killing_axis["coordinate"] != coordinate
                or raw_axis["partition_path"] != partition_path
                or raw_axis["partition_sha256"] != partition_sha
                or partition_file["path"] != partition_path
                or partition_file["sha256"] != partition_sha
                or stationary_axis["cell_count"] != raw_axis["cell_count"]
                or stationary_axis["cell_count"] != sequence_axis["anchor_size"]
            ):
                raise ValueError(f"axis partition join failure at row {index}, {coordinate}")

            partition_relative = (
                "artifacts/data/physical_production_initial_stream_v1/" + partition_path
            )
            partition = subordinate_snapshot(
                partition_relative,
                partition_sha,
                subordinate_snapshots,
            )
            subordinate_inventory.append(
                {
                    "path": partition_relative,
                    "role": f"initial_partition_{index:02d}_{coordinate}",
                    "sha256": partition_sha,
                }
            )
            if not partition_geometry_matches(sequence_axis, partition):
                raise ValueError(
                    f"n0 partition reconstruction failure at row {index}, {coordinate}"
                )

            stationary_cells = stationary_axis["cell_mass_intervals"]
            raw_cells = raw_axis["cell_records"]
            edges = raw_axis["edge_records"]
            cell_count = stationary_axis["cell_count"]
            if [entry.get("cell_index") for entry in stationary_cells] != list(
                range(cell_count)
            ) or [entry.get("cell_index") for entry in raw_cells] != list(range(cell_count)):
                raise ValueError(f"cell identity failure at row {index}, {coordinate}")
            expected_edges = [
                (edge_index, edge_index, edge_index + 1) for edge_index in range(cell_count - 1)
            ]
            if raw_axis["periodic"]:
                expected_edges.append((cell_count - 1, cell_count - 1, 0))
                periodic_seam_count += 1
            observed_edges = [
                (
                    entry.get("edge_index"),
                    entry.get("left_cell_index"),
                    entry.get("right_cell_index"),
                )
                for entry in edges
            ]
            if observed_edges != expected_edges:
                raise ValueError(f"edge identity failure at row {index}, {coordinate}")

            stationary_cell_count += len(stationary_cells)
            raw_cell_count += len(raw_cells)
            raw_edge_count += len(edges)
            axis_receipts.append(
                {
                    "alignment": sequence_axis["alignment"],
                    "cell_count": cell_count,
                    "cell_indices_contiguous_and_unique": True,
                    "coordinate": coordinate,
                    "edge_keys_contiguous_unique_and_oriented": True,
                    "n0_geometry_independently_matches_partition_bytes": True,
                    "partition_bundle_relative_path": partition_path,
                    "partition_report_relative_path": partition_relative,
                    "partition_sha256": partition_sha,
                    "periodic": raw_axis["periodic"],
                    "raw_stationary_partition_tuple_equal": True,
                }
            )

        rows.append(
            {
                "configuration_index": index,
                "configuration_label": label,
                "killing_configuration_shape_state_join_visible": True,
                "killing_partition_join_reconstructed": True,
                "killing_profile_index_order": PROFILE_ORDER,
                "killing_row_manifest_path": killing_relative,
                "killing_row_manifest_sha256": killing_manifest["sha256"],
                "legacy_member_digests_equal": True,
                "legacy_raw_flux_member_digest_sha256": raw_member[2],
                "legacy_stationary_member_digest_sha256": stationary_member[2],
                "n0_axes": axis_receipts,
                "n0_shape": shape,
                "n0_state_count": states,
                "refinement_family_id": family,
                "refinement_member_id": member,
                "same_member_contained": False,
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": sequence["source_row_canonical_sha256"],
                "v2_ordered_replay_present": False,
            }
        )

    counts = {
        "axis_join_count": sum(len(row["n0_axes"]) for row in rows),
        "configuration_join_count": len(rows),
        "killing_profile_join_count": 12 * 4,
        "periodic_seam_edge_count": periodic_seam_count,
        "raw_axis_cell_record_count": raw_cell_count,
        "raw_axis_edge_record_count": raw_edge_count,
        "stationary_axis_cell_record_count": stationary_cell_count,
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
        raise ValueError(f"joined record-count drift: {counts} != {expected_counts}")
    subordinate_inventory.sort(key=lambda item: item["role"])
    if len(subordinate_inventory) != 48:
        raise ValueError("subordinate inventory must contain 36 partitions and 12 killing rows")
    return rows, subordinate_inventory, counts


def build_control_method_source(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    commitment = sources["control_method_commitment"]
    geometry = sources["killing_geometry_authority"]
    basis = geometry["support_basis"]
    if (
        commitment.get("control_ids") != ["m1", "m2", "m3"]
        or basis.get("profile_count") != 4
        or len(basis.get("centres_exact", [])) != 4
    ):
        raise ValueError("control/profile authority drift")
    payload = {
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
            "control_ids": commitment["control_ids"],
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
            "profile_index_order": PROFILE_ORDER,
            "profile_ids_in_order": ["phi_0", "phi_1", "phi_2", "phi_3"],
        },
        "schema": "encounter_continuum_c1_symbolic_control_method_source_v1",
        "source_pins": {
            "control_method_commitment": source_pin("control_method_commitment"),
            "factorization_source": source_pin("factorization_source"),
            "killing_geometry_authority": source_pin("killing_geometry_authority"),
        },
        "status": ("FROZEN_SYMBOLIC_CONTROL_METHOD_ROLE11_ONLY_NO_VALUES_NO_BUDGET_NO_COMPLETE_C0"),
        "symbolic_formula": "V_c_mab=W^-1*C_ab*sum_j(w_j^(c)*Phi_jm)",
    }
    require_false_map(payload["claim_boundary"], "symbolic control method")
    return payload


def build_member_spec(
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    legacy = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    configurations = sources["configuration_source"]["configurations"]
    bindings: list[dict[str, Any]] = []
    for index, sequence in enumerate(refinement["sequences"]):
        semantic = legacy["configuration_semantic_ids"][index]
        config = configurations[index]
        axes: list[dict[str, Any]] = []
        for axis in sequence["axes"]:
            record = {
                "alignment": axis["alignment"],
                "anchor_size": axis["anchor_size"],
                "coordinate": axis["coordinate"],
            }
            if "periodic_shift_n0_exact" in axis:
                record["periodic_shift_n0_exact"] = axis["periodic_shift_n0_exact"]
            axes.append(record)
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
    payload = {
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
            "coordinate_order": AXIS_ORDER,
            "joint_refinement_sequence_bound": True,
            "legacy_member_digest_is_not_v2_acceptance_identity": True,
            "n0_geometry_match_is_not_correlated_containment": True,
            "physical_dimension": 2,
            "quotient_dimension": 3,
        },
        "n0_sequence_bindings": bindings,
        "schema": "encounter_continuum_c1_c2_n0_member_spec_v2",
        "source_pins": {
            "configuration_source": source_pin("configuration_source"),
            "factorization_source": source_pin("factorization_source"),
            "ideal_formula_source": source_pin("ideal_formula_source"),
            "joint_refinement_family": source_pin("joint_refinement_family"),
            "legacy_member_spec": source_pin("legacy_member_spec"),
            "reference_density_source": source_pin("reference_density_source"),
        },
        "status": ("FROZEN_N0_SEQUENCE_BINDING_ONLY_NO_PARTITION_HASH_IDENTITY_NO_ORDERED_REPLAY"),
    }
    require_false_map(payload["claim_boundary"], "n0 member specification")
    return payload


def build_policy(
    sources: dict[str, dict[str, Any]],
    member_spec: dict[str, Any],
) -> dict[str, Any]:
    legacy = sources["legacy_policy"]
    payload = {
        "claim_boundary": {
            "complete_C1": False,
            "complete_C2": False,
            "formal_production_bridge_accepted": False,
            "release_eligible": False,
        },
        "join_requirements": {
            "axis_order_exact": AXIS_ORDER,
            "axis_partition_path_sha_cell_count_equal": True,
            "cell_indices_contiguous_and_unique": True,
            "configuration_count_exactly_12": True,
            "configuration_index_and_label_unique": True,
            "edge_key": ["edge_index", "left_cell_index", "right_cell_index"],
            "edge_keys_unique": True,
            "killing_partition_path_sha_equal": True,
            "profile_index_order_exact": PROFILE_ORDER,
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
        "requirements": legacy["requirements"],
        "schema": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v2",
        "source_pins": {
            "legacy_policy": source_pin("legacy_policy"),
            "member_spec_v2": generated_pin(MEMBER_SPEC_PATH, member_spec),
        },
        "status": (
            "FROZEN_PREFLIGHT_JOIN_POLICY_NOT_PREDECESSOR_SEALED_CURRENT_SOURCES_INELIGIBLE"
        ),
    }
    require_false_map(payload["claim_boundary"], "n0 anti-vacuity policy")
    return payload


def source_schema(source: dict[str, Any]) -> str:
    schema = source.get("schema")
    if type(schema) is not str:
        raise ValueError("source schema required")
    return schema


def build_manifest(
    sources: dict[str, dict[str, Any]],
    member_spec: dict[str, Any],
    policy: dict[str, Any],
    control_method: dict[str, Any],
    subordinate_inventory: list[dict[str, str]],
) -> dict[str, Any]:
    generated = {
        "member_spec_manifest": (MEMBER_SPEC_PATH, member_spec),
        "anti_vacuity_policy_source": (POLICY_PATH, policy),
        "symbolic_control_method_source": (CONTROL_METHOD_PATH, control_method),
    }
    primitive_map: list[tuple[str, str]] = [
        ("reference_density_source", "reference_density_source"),
        ("ideal_formula_source", "ideal_formula_source"),
        ("factorization_source", "factorization_source"),
        ("configuration_source", "configuration_source"),
        ("member_spec_manifest", "member_spec_manifest"),
        ("outward_method_registry_source", "method_registry"),
        ("anti_vacuity_policy_source", "anti_vacuity_policy_source"),
        ("raw_axis_enclosure_source", "raw_flux_source"),
        ("stationary_integral_source", "stationary_integral_source"),
        ("killing_geometry_source", "killing_geometry_bundle"),
        ("symbolic_control_method_source", "symbolic_control_method_source"),
    ]
    primitive_sources: list[dict[str, str]] = []
    for role, source_role in primitive_map:
        if source_role in generated:
            path, value = generated[source_role]
            primitive_sources.append(
                {
                    "path": path,
                    "role": role,
                    "schema": source_schema(value),
                    "sha256": sha256(canonical_bytes(value)),
                }
            )
        else:
            path, digest = CORE_SOURCES[source_role]
            primitive_sources.append(
                {
                    "path": path,
                    "role": role,
                    "schema": source_schema(sources[source_role]),
                    "sha256": digest,
                }
            )

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
    supporting_evidence = [
        {
            "path": CORE_SOURCES[role][0],
            "role": role,
            "sha256": CORE_SOURCES[role][1],
        }
        for role in support_roles
    ]

    nodes = [entry["role"] for entry in primitive_sources]
    edges = [
        ["reference_density_source", "member_spec_manifest"],
        ["ideal_formula_source", "member_spec_manifest"],
        ["factorization_source", "member_spec_manifest"],
        ["configuration_source", "member_spec_manifest"],
        ["member_spec_manifest", "anti_vacuity_policy_source"],
        ["factorization_source", "symbolic_control_method_source"],
    ]
    payload = {
        "claim_boundary": {
            "complete_process_report_file_open_closure": False,
            "formal_outer_open_operation_model_present": False,
            "outer_manifest_authorizes_itself": False,
            "production_payload_roles_1_through_11_formally_bound": False,
            "source_dependency_dag_complete": False,
            "symbolic_bridge_accepted": False,
        },
        "forbidden_selected_roles": {
            "budget_value_sources": [],
            "control_value_sources": [],
            "result_or_scratch_sources": [],
        },
        "preflight_role_catalog": {
            "preflight_role_catalog_cardinality_11": True,
            "primitive_sources": primitive_sources,
        },
        "preflight_subordinate_inventory": subordinate_inventory,
        "schema": "encounter_continuum_c1_n0_same_member_preflight_outer_manifest_v1",
        "source_dependency_dag": {
            "edges": edges,
            "nodes": nodes,
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
        },
        "stage": "production_n0_same_member_symbolic_preflight_only",
        "status": ("PREFLIGHT_CATALOG_ONLY_NO_FORMAL_OUTER_OPEN_AUTHORITY_NO_ACCEPTANCE"),
        "supporting_evidence": supporting_evidence,
    }
    require_false_map(payload["claim_boundary"], "preflight outer manifest")
    if len(primitive_sources) != 11 or len({item["role"] for item in primitive_sources}) != 11:
        raise ValueError("primitive role catalog must contain 11 unique roles")
    return payload


def build_candidate(
    rows: list[dict[str, Any]],
    counts: dict[str, Any],
    member_spec: dict[str, Any],
    policy: dict[str, Any],
    control_method: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    method_missing = [
        "method_parameter_sha256",
        "producer_code_sha256",
        "verifier_code_sha256",
    ]
    payload = {
        "blocking_conditions": BLOCKERS,
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "configuration_join_rows": rows,
        "expression_dag_contract": {
            "selected_required_symbolic_identities_declared": True,
            "all_identities_interval_replayed": False,
            "discrete_and_reconstructed_killing_are_distinct": True,
            "expressions": EXPRESSION_DAG,
        },
        "member_semantics": {
            "every_cartesian_interval_member_is_a_model": False,
            "geometric_n0_equality_is_not_correlated_containment": True,
            "legacy_marginal_member_tuple_joined": True,
            "one_correlated_distinguished_ideal_member_is_contained": False,
            "retrospective_join_cannot_repair_predecessor_order": True,
        },
        "role_binding_summary": {
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
            "method_registry_missing_required_fields": method_missing,
            "preflight_role_catalog_cardinality": 11,
            "production_payload_roles_1_through_11_formally_bound": False,
            "round172_contains_partition_sha256": False,
            "support_factor_storage": {
                "flat_index_formula": "i_M",
                "logical_shape_each": ["n_M"],
            },
        },
        "schema": "encounter_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1",
        "source_bindings": {
            "builder_source": {
                "path": str(SELF.relative_to(REPORT)),
                "sha256": sha256(descriptor_snapshot(SELF)),
            },
            "control_method_source": generated_pin(CONTROL_METHOD_PATH, control_method),
            "member_spec_v2": generated_pin(MEMBER_SPEC_PATH, member_spec),
            "outer_manifest": generated_pin(MANIFEST_PATH, manifest),
            "policy_v2": generated_pin(POLICY_PATH, policy),
            "validator_source": {
                "path": VALIDATOR_PATH,
                "sha256": sha256(descriptor_snapshot(REPORT / VALIDATOR_PATH)),
            },
        },
        "status": (
            "PASS_METADATA_PREFLIGHT_ONLY_CORRELATED_MEMBER_AND_FORMAL_CANDIDATE_ACCEPTANCE_FALSE"
        ),
        "validation_scope": {
            "authenticated_execution_attested": False,
            "complete_process_open_closure": False,
            "hostile_writer_atomicity_claimed": False,
            "independent_numerical_backend": False,
            "largest_tensor_materialized": False,
            "network_access_used": False,
            "positive_budget_or_result_payload_read": False,
            "python_stdlib_only": True,
            "join_subordinate_json_files_preflight_catalogued": True,
        },
    }
    require_false_map(payload["claim_boundary"], "preflight candidate")
    if any(item["cleared"] is not False for item in payload["blocking_conditions"]):
        raise ValueError("every preflight blocker must remain uncleared")
    return payload


def build_outputs() -> dict[str, dict[str, Any]]:
    sources, _ = load_core_sources()
    validate_core_semantics(sources)
    subordinate_snapshots: dict[str, bytes] = {}
    rows, subordinate_inventory, counts = build_join_rows(
        sources,
        subordinate_snapshots,
    )
    member_spec = build_member_spec(sources)
    policy = build_policy(sources, member_spec)
    control_method = build_control_method_source(sources)
    manifest = build_manifest(
        sources,
        member_spec,
        policy,
        control_method,
        subordinate_inventory,
    )
    candidate = build_candidate(
        rows,
        counts,
        member_spec,
        policy,
        control_method,
        manifest,
    )
    return {
        MEMBER_SPEC_PATH: member_spec,
        POLICY_PATH: policy,
        CONTROL_METHOD_PATH: control_method,
        MANIFEST_PATH: manifest,
        CANDIDATE_PATH: candidate,
    }


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPORT,
        help="root under which canonical report-relative output paths are written",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify canonical live outputs without writing",
    )
    arguments = parser.parse_args()
    try:
        outputs = build_outputs()
        for relative in OUTPUT_PATHS:
            expected = canonical_bytes(outputs[relative])
            destination = arguments.output_root / relative
            if arguments.check:
                actual = descriptor_snapshot(destination)
                if actual != expected:
                    raise ValueError(
                        f"output drift for {relative}: {sha256(actual)} != {sha256(expected)}"
                    )
            else:
                atomic_write(destination, expected)
        candidate_bytes = canonical_bytes(outputs[CANDIDATE_PATH])
        print(
            "PASS_N0_SAME_MEMBER_PREFLIGHT_BUILD "
            f"candidate_sha256={sha256(candidate_bytes)} outputs={len(outputs)} "
            "configuration_joins=12 axis_joins=36 blockers=9 "
            "correlated_member=false formal_candidate=false release=false"
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR N0SameMemberPreflightBuild: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
