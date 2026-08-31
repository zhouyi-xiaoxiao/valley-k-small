"""Hostile mutations for the Round-176 n=0 same-member preflight."""

from __future__ import annotations

import copy
import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
VALIDATOR = REPORT / "code/validate_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"
MEMBER = REPORT / "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json"
POLICY = REPORT / "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json"
CONTROL = REPORT / "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json"
MANIFEST = REPORT / "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json"
CANDIDATE = (
    REPORT / "artifacts/data/continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("round176_mutation_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATION = load_validator()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    assert isinstance(value, dict)
    return value


def write_mutation(
    tmp_path: Path,
    source: Path,
    mutate: Callable[[dict[str, Any]], None],
) -> Path:
    value = copy.deepcopy(load(source))
    mutate(value)
    destination = tmp_path / source.name
    destination.write_bytes(canonical(value))
    return destination


@pytest.mark.parametrize("claim", sorted(VALIDATION.CLAIM_KEYS))
def test_rejects_every_promoted_claim_flag(tmp_path: Path, claim: str) -> None:
    mutated = write_mutation(
        tmp_path,
        CANDIDATE,
        lambda value: value["claim_boundary"].__setitem__(claim, True),
    )
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(candidate_path=mutated)


@pytest.mark.parametrize("blocker_index", range(9))
def test_rejects_clearing_any_named_blocker(tmp_path: Path, blocker_index: int) -> None:
    mutated = write_mutation(
        tmp_path,
        CANDIDATE,
        lambda value: value["blocking_conditions"][blocker_index].__setitem__("cleared", True),
    )
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(candidate_path=mutated)


def set_nested(path: tuple[Any, ...], replacement: Any) -> Callable[[dict[str, Any]], None]:
    def mutate(value: dict[str, Any]) -> None:
        cursor: Any = value
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement

    return mutate


CANDIDATE_ATTACKS: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
    (
        "false_replaced_by_integer_zero",
        set_nested(("claim_boundary", "complete_C1"), 0),
    ),
    (
        "preflight_schema_relabelled_as_formal_candidate",
        set_nested(("schema",), "encounter_c1_gauge_killing_symbolic_candidate_v1"),
    ),
    (
        "status_relabelled_as_acceptance",
        set_nested(("status",), "PASS_SYMBOLIC_BRIDGE_ACCEPTED"),
    ),
    (
        "row_dropped",
        lambda value: value["configuration_join_rows"].pop(),
    ),
    (
        "row_duplicated",
        lambda value: value["configuration_join_rows"].__setitem__(
            1, copy.deepcopy(value["configuration_join_rows"][0])
        ),
    ),
    (
        "row_index_mutated",
        set_nested(("configuration_join_rows", 0, "configuration_index"), 1),
    ),
    (
        "row_index_zero_replaced_by_false",
        set_nested(("configuration_join_rows", 0, "configuration_index"), False),
    ),
    (
        "row_label_mutated",
        set_nested(("configuration_join_rows", 0, "configuration_label"), "E128/Base"),
    ),
    (
        "refinement_family_mutated",
        set_nested(
            ("configuration_join_rows", 0, "refinement_family_id"),
            "invented_family",
        ),
    ),
    (
        "member_digest_mutated",
        set_nested(
            (
                "configuration_join_rows",
                0,
                "legacy_stationary_member_digest_sha256",
            ),
            "0" * 64,
        ),
    ),
    (
        "sequence_source_hash_mutated",
        set_nested(
            (
                "configuration_join_rows",
                0,
                "sequence_source_row_canonical_sha256",
            ),
            "0" * 64,
        ),
    ),
    (
        "partition_sha_mutated",
        set_nested(
            ("configuration_join_rows", 0, "n0_axes", 0, "partition_sha256"),
            "0" * 64,
        ),
    ),
    (
        "same_member_smuggled_true",
        set_nested(("configuration_join_rows", 0, "same_member_contained"), True),
    ),
    (
        "same_member_false_replaced_by_zero",
        set_nested(("configuration_join_rows", 0, "same_member_contained"), 0),
    ),
    (
        "ordered_replay_smuggled_true",
        set_nested(("configuration_join_rows", 0, "v2_ordered_replay_present"), True),
    ),
    (
        "global_gauge_denominator_axis_deleted",
        set_nested(
            ("expression_dag_contract", "expressions", "global_gauge"),
            "G=M_L/(S_midpoint*S_relative_parallel)",
        ),
    ),
    (
        "rho_inverted",
        set_nested(
            ("expression_dag_contract", "expressions", "map_ratio"),
            "rho=pi_h/M_pi",
        ),
    ),
    (
        "map_composition_replaced_by_identity",
        set_nested(
            ("expression_dag_contract", "expressions", "map_composition"),
            "P_h*J_h=I",
        ),
    ),
    (
        "reconstruction_replaced_by_V",
        set_nested(
            (
                "expression_dag_contract",
                "expressions",
                "reconstructed_multiplier_via_ratio",
            ),
            "K=V",
        ),
    ),
    (
        "declared_true_replaced_by_one",
        set_nested(
            (
                "expression_dag_contract",
                "selected_required_symbolic_identities_declared",
            ),
            1,
        ),
    ),
    (
        "discrete_killing_conflated_with_reconstruction",
        set_nested(
            ("expression_dag_contract", "expressions", "discrete_killing_diagonal"),
            "B*K",
        ),
    ),
    (
        "round172_partition_sha_claim_smuggled_true",
        set_nested(
            ("role_binding_summary", "round172_contains_partition_sha256"),
            True,
        ),
    ),
    (
        "weak_killing_sidecar_promoted",
        set_nested(
            (
                "role_binding_summary",
                "killing_binding_sidecar_is_receipt_or_candidate",
            ),
            True,
        ),
    ),
    (
        "method_registry_gap_hidden",
        set_nested(
            ("role_binding_summary", "method_registry_complete_for_formal_bridge"),
            True,
        ),
    ),
    (
        "builder_hash_substituted",
        set_nested(("source_bindings", "builder_source", "sha256"), "0" * 64),
    ),
    (
        "largest_tensor_claim_mutated",
        set_nested(("validation_scope", "largest_tensor_materialized"), True),
    ),
    (
        "unknown_top_level_key",
        lambda value: value.__setitem__("acceptance_receipt", {}),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "mutate"),
    CANDIDATE_ATTACKS,
    ids=[name for name, _ in CANDIDATE_ATTACKS],
)
def test_rejects_candidate_semantic_mutations(
    tmp_path: Path,
    attack_name: str,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    assert attack_name
    mutated = write_mutation(tmp_path, CANDIDATE, mutate)
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(candidate_path=mutated)


SOURCE_ATTACKS: list[tuple[str, Path, str, Callable[[dict[str, Any]], None]]] = [
    (
        "member_current_sources_bind_v2",
        MEMBER,
        "member_spec_path",
        set_nested(("claim_boundary", "current_enclosure_sources_bind_this_v2_spec"), True),
    ),
    (
        "member_partition_hashes_claimed_bound",
        MEMBER,
        "member_spec_path",
        set_nested(("claim_boundary", "n0_partition_sha256s_bound"), True),
    ),
    (
        "member_sequence_id_mutated",
        MEMBER,
        "member_spec_path",
        set_nested(("n0_sequence_bindings", 0, "sequence_id"), "invented"),
    ),
    (
        "member_index_zero_replaced_by_false",
        MEMBER,
        "member_spec_path",
        set_nested(("n0_sequence_bindings", 0, "configuration_index"), False),
    ),
    (
        "policy_predecessor_sealed_retroactively",
        POLICY,
        "policy_path",
        set_nested(("ordering", "policy_predecessor_order_independently_sealed"), True),
    ),
    (
        "policy_current_sources_eligible",
        POLICY,
        "policy_path",
        set_nested(("ordering", "current_enclosure_sources_eligible_for_acceptance"), True),
    ),
    (
        "policy_future_replay_removed",
        POLICY,
        "policy_path",
        set_nested(("ordering", "future_replay_required"), False),
    ),
    (
        "policy_threshold_changed_after_results",
        POLICY,
        "policy_path",
        set_nested(("requirements", "maximum_map_anchor_constant"), "2000000/1"),
    ),
    (
        "policy_true_replaced_by_one",
        POLICY,
        "policy_path",
        set_nested(("join_requirements", "configuration_count_exactly_12"), 1),
    ),
    (
        "control_values_inserted",
        CONTROL,
        "control_path",
        set_nested(
            ("no_value_contract", "actual_weight_rows"),
            [["1/4", "1/4", "1/4", "1/4"]],
        ),
    ),
    (
        "control_profile_order_swapped",
        CONTROL,
        "control_path",
        set_nested(("profile_basis_contract", "profile_index_order"), [1, 0, 2, 3]),
    ),
    (
        "control_true_replaced_by_one",
        CONTROL,
        "control_path",
        set_nested(("control_contract", "exact_sum_one_required"), 1),
    ),
    (
        "manifest_formal_roles_claimed_bound",
        MANIFEST,
        "manifest_path",
        set_nested(
            (
                "claim_boundary",
                "production_payload_roles_1_through_11_formally_bound",
            ),
            True,
        ),
    ),
    (
        "manifest_self_authorizes",
        MANIFEST,
        "manifest_path",
        set_nested(("claim_boundary", "outer_manifest_authorizes_itself"), True),
    ),
    (
        "manifest_partition_entry_removed",
        MANIFEST,
        "manifest_path",
        lambda value: value["preflight_subordinate_inventory"].pop(),
    ),
    (
        "manifest_subordinate_hash_mutated",
        MANIFEST,
        "manifest_path",
        set_nested(("preflight_subordinate_inventory", 0, "sha256"), "0" * 64),
    ),
    (
        "manifest_path_escape",
        MANIFEST,
        "manifest_path",
        set_nested(
            ("preflight_role_catalog", "primitive_sources", 0, "path"),
            "../outside.json",
        ),
    ),
    (
        "manifest_invents_v2_to_current_enclosure_edge",
        MANIFEST,
        "manifest_path",
        lambda value: value["source_dependency_dag"]["edges"].append(
            ["member_spec_manifest", "raw_axis_enclosure_source"]
        ),
    ),
    (
        "manifest_true_replaced_by_one",
        MANIFEST,
        "manifest_path",
        set_nested(
            (
                "preflight_role_catalog",
                "preflight_role_catalog_cardinality_11",
            ),
            1,
        ),
    ),
]


@pytest.mark.parametrize(
    ("attack_name", "source", "argument", "mutate"),
    SOURCE_ATTACKS,
    ids=[name for name, *_ in SOURCE_ATTACKS],
)
def test_rejects_generated_source_and_manifest_mutations(
    tmp_path: Path,
    attack_name: str,
    source: Path,
    argument: str,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    assert attack_name
    mutated = write_mutation(tmp_path, source, mutate)
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(**{argument: mutated})


def raw_candidate_mutations(original: bytes) -> list[tuple[str, bytes]]:
    duplicate_schema = original.replace(
        b"{\n",
        (
            b'{\n  "schema": '
            b'"encounter_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1",\n'
        ),
        1,
    )
    float_value = original.replace(
        b'"preflight_role_catalog_cardinality": 11',
        b'"preflight_role_catalog_cardinality": 11.0',
        1,
    )
    nan_value = original.replace(
        b'"preflight_role_catalog_cardinality": 11',
        b'"preflight_role_catalog_cardinality": NaN',
        1,
    )
    return [
        ("duplicate_key", duplicate_schema),
        ("float", float_value),
        ("nan", nan_value),
        ("missing_terminal_newline", original.rstrip(b"\n")),
        ("truncated", original[: len(original) // 2]),
        ("non_ascii", original.replace(b"PREFLIGHT", "PRÉFLIGHT".encode(), 1)),
    ]


@pytest.mark.parametrize(
    ("attack_name", "payload"),
    raw_candidate_mutations(CANDIDATE.read_bytes()),
    ids=[name for name, _ in raw_candidate_mutations(CANDIDATE.read_bytes())],
)
def test_rejects_noncanonical_or_malformed_candidate_bytes(
    tmp_path: Path,
    attack_name: str,
    payload: bytes,
) -> None:
    assert attack_name
    mutated = tmp_path / "candidate.json"
    mutated.write_bytes(payload)
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(candidate_path=mutated)
