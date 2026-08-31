#!/usr/bin/env python3
"""Fail-closed validator for the frozen manuscript-completion contract v1."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

REPORT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPORT / "artifacts/data/manuscript_completion_contract_v1.json"

EXPECTED_CLAIM_CEILING = {
    "forbidden_numerical_claims": [
        "allocation_cusp",
        "phase_diagram",
        "strict_numerical_continuum_limit",
        "unbounded_time_topology",
        "finite_parameter_arbitrary_dimension",
        "positive_budget_physical_d3",
    ],
    "numerical_claim": "finite_window_continuum_consistent_physical_d2_evidence",
    "numerical_tail_checks_end": "100/1",
    "numerical_topology_window": ["1/2", "35/1"],
    "strict_continuum_claimed": False,
    "strict_continuum_gate": (
        "CONDITIONAL_ONLY_IF_STRICT_NUMERICAL_CONTINUUM_CLAIMED"
    ),
    "theorem_claim": (
        "accepted_exact_m_doi_theorem_at_frozen_hypotheses_and_sequential_limits"
    ),
}

EXPECTED_CONFIGURATIONS = [
    "O113/Base",
    "E128/Base",
    "O129/Base",
    "O161/Base",
    "M+",
    "R+",
    "MR+",
    "MR+F",
    "A_M",
    "A_R",
    "A_Y",
    "A_MRY",
]

EXPECTED_NO_REFIT_FIELDS = [
    "control",
    "budget",
    "geometry",
    "supports",
    "initial_law",
    "contact_rule",
    "configuration",
    "grid",
    "box",
    "alignment",
    "reference_grid",
    "root_band",
    "time_window",
    "checkpoints",
    "metric_definitions",
    "threshold",
    "interval_method",
    "bisection_limits",
    "newton_limits",
    "schema",
    "hard_stop_semantics",
    "precision",
    "solver_tolerance",
    "resource_cap",
    "selector_logic",
    "sample_size",
    "power_rule",
    "multiplicity_rule",
    "pool_separation",
    "chunk_rule",
    "seed_domain",
]

EXPECTED_F0_CAPABILITIES = [
    "exact_rational_parser_without_production_evaluation",
    "retired_selector_v1_rejection",
    "t_5_5_one_ulp_fixture",
    "all_12_configuration_constructors",
    "half_volume_and_periodic_alignment_semantics",
    "canonical_packed_owned_readonly_inputs",
    "derived_diagonal_only",
    "sub_markov_detailed_balance_killing_witnesses",
    "directed_p_and_q_action_roundoff",
    "absolute_time_uniformization_no_state_chaining",
    "directed_poisson_tail_enclosure",
    "scalar_j0_to_j3_and_m2_to_m4",
    "complete_window_tiles_and_root_roles",
    "twelve_step_interval_newton",
    "canonical_schema_and_claim_field_mutations",
    "two_clean_replicas",
    "independent_semantic_replay",
    "actual_mr_plus_f_resource_schedule",
]

EXPECTED_IMMUTABLE_SOURCES = {
    "configuration_contract": {
        "path": "artifacts/data/physical_configuration_family_control_free_v1.json",
        "sha256": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    },
    "continuum_scope_at_freeze": {
        "path": "notes/continuum_next_stage_path.md",
        "sha256": "65caeb28baffdf45e6675e10a522f9fbd5b5d724ad3899f63928be5f62175782",
    },
    "exact_control_selector_result": {
        "path": "scratch/modal_certificate_exact_selector_method_only_result.json",
        "sha256": "77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98",
    },
    "exact_m_full_proof": {
        "path": "manuscript/exact_m_theorem_full_proof.tex",
        "sha256": "a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b",
    },
    "exact_m_spine": {
        "path": "manuscript/exact_m_theorem_spine.tex",
        "sha256": "79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e",
    },
    "fixed_control_design": {
        "path": "notes/positive_b_fixed_control_robustness_design_v2.md",
        "sha256": "264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd",
    },
    "round149_independent_audit": {
        "path": "audits/round_149_exact_m_supplement_migration_independent_attack.md",
        "sha256": "f689002b01b1fff3549ed446c9b05efe3fbe3cfc4aa1a3b64c859bbb18dfea78",
    },
    "selector_design": {
        "path": "notes/f1_to_f2_common_observable_selector_v1.md",
        "sha256": "9ab69dbd9662577aa72760bf003240ef0cd1edba167f03ceb72cd8335045c1af",
    },
    "selector_implementation": {
        "path": "code/f1_to_f2_common_observable_selector_v2.py",
        "sha256": "b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6",
    },
}

EXPECTED_LIMITATIONS = [
    "This pre-F0 freeze is not an F0 record or an independent F0 acceptance.",
    "No F1, F2, or F3 scientific result exists at this freeze.",
    (
        "Strict C0-C3 and root transfer remain available only for a separately "
        "elected strict numerical continuum claim."
    ),
    (
        "Author metadata, overlap identifiers, archive identifiers, and final "
        "release audits remain separate gates."
    ),
]

EXPECTED_ROOT_KEYS = {
    "authorized_scientific_command",
    "claim_ceiling",
    "current_state",
    "exact_controls",
    "f0_acceptance",
    "f1_contract",
    "immutable_sources",
    "limitations",
    "no_refit",
    "schema_version",
    "stage",
    "status",
    "terminal_branches",
}

EXPECTED_BRANCHES = {
    "HOLD_F0_METHOD_OR_RESOURCE": {
        "failure": "METHOD_OR_RESOURCE",
        "statuses": {
            "f0": "HOLD_F0",
            "f1": "NOT_RUN",
            "f2": "NOT_RUN",
            "f3": "NOT_RUN",
        },
        "permissions": {
            "f1_permitted": False,
            "f2_permitted": False,
            "f3_permitted": False,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "complete_honest_theorem_first_pre_science_limit_and_reassess_fit"
        ),
    },
    "HOLD_F1_METHOD_OR_RESOURCE": {
        "failure": "METHOD_OR_RESOURCE",
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "HOLD_F1",
            "f2": "NOT_RUN",
            "f3": "NOT_RUN",
        },
        "permissions": {
            "f2_permitted": False,
            "f3_permitted": False,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "report_unresolved_computational_boundary_without_physical_failure_claim"
        ),
    },
    "HOLD_F1_SCIENCE": {
        "failure": "SCIENCE",
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "HOLD_F1",
            "f2": "NOT_RUN",
            "f3": "NOT_RUN",
        },
        "permissions": {
            "f2_permitted": False,
            "f3_permitted": False,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "report_frozen_negative_result_without_refit_or_remove_finite_parameter_headline"
        ),
    },
    "HOLD_F2_PLAN_OR_RESOURCE": {
        "failure": "METHOD_OR_RESOURCE",
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "PASS_F1_ALL_ROWS",
            "f2": "HOLD_F2",
            "f3": "NOT_RUN",
        },
        "permissions": {
            "deterministic_f1_claim_permitted_at_exact_scope": True,
            "f3_permitted": False,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "retain_f1_at_exact_scope_and_report_selector_or_feasibility_boundary"
        ),
    },
    "HOLD_F3_METHOD_OR_RESOURCE": {
        "failure": "METHOD_OR_RESOURCE",
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "PASS_F1_ALL_ROWS",
            "f2": "PASS_F2_PLAN",
            "f3": "HOLD_F3",
        },
        "permissions": {
            "deterministic_f1_claim_permitted_at_exact_scope": True,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "retain_deterministic_finite_window_result_and_report_unresolved_"
            "independent_method_boundary"
        ),
    },
    "HOLD_F3_SCIENCE": {
        "failure": "SCIENCE",
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "PASS_F1_ALL_ROWS",
            "f2": "PASS_F2_PLAN",
            "f3": "HOLD_F3",
        },
        "permissions": {
            "deterministic_f1_claim_permitted_at_exact_scope": True,
            "independent_validation_claim_permitted": False,
        },
        "action": (
            "retain_deterministic_finite_window_result_and_report_cross_method_"
            "disagreement"
        ),
    },
    "PASS_VALIDATED_D2": {
        "failure": None,
        "statuses": {
            "f0": "PASS_F0_ACCEPTED",
            "f1": "PASS_F1_ALL_ROWS",
            "f2": "PASS_F2_PLAN",
            "f3": "PASS_F3_ALL_ASSERTIONS",
        },
        "permissions": {
            "independent_validation_claim_permitted": True,
            "submission_still_requires_editorial_and_final_audits": True,
        },
        "action": (
            "write_theorem_first_finite_window_continuum_consistent_physical_d2_result"
        ),
    },
}


class ContractValidationError(RuntimeError):
    """A claim-bearing field or frozen source failed closed."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_strict_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ContractValidationError(f"contract JSON is unreadable: {error}") from error
    if type(payload) is not dict:
        raise ContractValidationError("contract root must be an exact object")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_exact_dict(value: object, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ContractValidationError(f"{label} must be an exact object")
    return value


def _selector_exact_weights(source: Path) -> dict[str, list[str]]:
    selector = _load_strict_json(source)
    results = _require_exact_dict(selector.get("selector_results"), "selector_results")
    exact: dict[str, list[str]] = {}
    for source_id, contract_id in (("m1", "lp_m1"), ("m2", "lp_m2"), ("m3", "lp_m3")):
        row = _require_exact_dict(results.get(source_id), f"selector {source_id}")
        selected = _require_exact_dict(row.get("selected"), f"selector {source_id}.selected")
        weights = selected.get("weights")
        if type(weights) is not list or len(weights) != 4:
            raise ContractValidationError(f"selector {source_id} weights are malformed")
        exact[contract_id] = [
            _require_exact_dict(weight, f"selector {source_id} weight").get("exact")
            for weight in weights
        ]
        if any(type(value) is not str for value in exact[contract_id]):
            raise ContractValidationError(f"selector {source_id} exact weights are malformed")
    return exact


def validate_contract_payload(
    contract: dict[str, Any],
    *,
    report: Path = REPORT,
) -> None:
    """Validate every claim-bearing value against the frozen external sources."""

    if type(contract) is not dict:
        raise ContractValidationError("contract must be an exact object")
    if set(contract) != EXPECTED_ROOT_KEYS:
        raise ContractValidationError("contract root contains extra or missing fields")
    if (
        contract.get("schema_version") != "encounter_manuscript_completion_contract_v1"
        or contract.get("stage") != "pre_f0_claim_and_terminal_branch_freeze"
        or contract.get("status") != "FROZEN_PRE_F0_NO_SCIENTIFIC_EXECUTION"
        or contract.get("authorized_scientific_command") is not None
    ):
        raise ContractValidationError("pre-F0 contract header was promoted or mutated")

    if contract.get("claim_ceiling") != EXPECTED_CLAIM_CEILING:
        raise ContractValidationError("claim ceiling differs from the frozen ceiling")
    if contract.get("current_state") != {
        "f0_independently_accepted": False,
        "f1_authorized": False,
        "manuscript_complete": False,
        "science_branch_selected": False,
        "submission_eligible": False,
    }:
        raise ContractValidationError("pre-F0 current state was promoted or mutated")
    if contract.get("limitations") != EXPECTED_LIMITATIONS:
        raise ContractValidationError("pre-F0 limitations were weakened or mutated")

    f0 = _require_exact_dict(contract.get("f0_acceptance"), "f0_acceptance")
    expected_f0 = {
        "actual_largest_shape": [207, 215, 161],
        "actual_largest_states": 7_165_305,
        "clean_canonical_replicas": 2,
        "independent_semantic_replay_required": True,
        "positive_budget_primary_controls_evaluated": False,
        "production_resource_measurement_required": True,
        "required_capabilities": EXPECTED_F0_CAPABILITIES,
        "science_free": True,
    }
    if f0 != expected_f0:
        raise ContractValidationError("F0 acceptance capability set was weakened")

    f1 = _require_exact_dict(contract.get("f1_contract"), "f1_contract")
    if f1 != {
        "configuration_order": EXPECTED_CONFIGURATIONS,
        "control_order": ["lp_m1", "lp_m2", "lp_m3"],
        "no_refit": True,
        "ordered_rows": 36,
        "replicas": 2,
        "stop_after_first_hold": True,
    }:
        raise ContractValidationError("F1 order or stop/no-refit semantics changed")

    no_refit = _require_exact_dict(contract.get("no_refit"), "no_refit")
    if no_refit != {
        "after_independent_f0_acceptance": True,
        "forbidden_changes": EXPECTED_NO_REFIT_FIELDS,
    }:
        raise ContractValidationError("no-refit field set was weakened or reordered")

    sources = _require_exact_dict(contract.get("immutable_sources"), "immutable_sources")
    if sources != EXPECTED_IMMUTABLE_SOURCES:
        raise ContractValidationError("immutable source mapping differs from the freeze")
    for label, record_value in sources.items():
        record = _require_exact_dict(record_value, f"immutable source {label}")
        if set(record) != {"path", "sha256"}:
            raise ContractValidationError(f"immutable source {label} has extra/missing fields")
        relative = record["path"]
        expected = record["sha256"]
        if (
            type(relative) is not str
            or not relative
            or relative.startswith("/")
            or ".." in Path(relative).parts
            or type(expected) is not str
            or len(expected) != 64
        ):
            raise ContractValidationError(f"immutable source {label} is malformed")
        source = report / relative
        if not source.is_file() or _sha256(source) != expected:
            raise ContractValidationError(f"immutable source drifted: {relative}")

    exact_controls = _require_exact_dict(contract.get("exact_controls"), "exact_controls")
    if (
        exact_controls.get("budget_binary64_hex")
        != float.fromhex("0x1.47ae147ae147bp-7").hex()
        or exact_controls.get("budget_human_label") != "0.01"
        or set(exact_controls)
        != {"budget_binary64_hex", "budget_human_label", "lp_m1", "lp_m2", "lp_m3"}
    ):
        raise ContractValidationError("budget/control header changed")
    selector_record = _require_exact_dict(
        sources.get("exact_control_selector_result"),
        "exact selector source",
    )
    selector_weights = _selector_exact_weights(report / selector_record["path"])
    for control_id in ("lp_m1", "lp_m2", "lp_m3"):
        weights = exact_controls.get(control_id)
        if weights != selector_weights[control_id]:
            raise ContractValidationError(f"{control_id} differs from exact selector order")
        fractions = tuple(Fraction(value) for value in weights)
        if not all(value > 0 for value in fractions) or sum(fractions, Fraction(0)) != 1:
            raise ContractValidationError(f"{control_id} is not a positive exact simplex point")

    branches = _require_exact_dict(contract.get("terminal_branches"), "terminal_branches")
    if set(branches) != set(EXPECTED_BRANCHES):
        raise ContractValidationError("terminal branch set is incomplete")
    state_keys: set[tuple[tuple[tuple[str, str], ...], str | None]] = set()
    for name, expected in EXPECTED_BRANCHES.items():
        branch = _require_exact_dict(branches.get(name), f"branch {name}")
        if branch.get("required_statuses") != expected["statuses"]:
            raise ContractValidationError(f"branch {name} upstream statuses changed")
        if branch.get("required_failure_class") != expected["failure"]:
            raise ContractValidationError(f"branch {name} failure class changed")
        if branch.get("manuscript_action") != expected["action"]:
            raise ContractValidationError(f"branch {name} manuscript action changed")
        for field, value in expected["permissions"].items():
            if branch.get(field) is not value:
                raise ContractValidationError(f"branch {name} permission changed: {field}")
        expected_fields = {
            "manuscript_action",
            "required_failure_class",
            "required_statuses",
            *expected["permissions"],
        }
        if set(branch) != expected_fields:
            raise ContractValidationError(f"branch {name} contains extra/missing fields")
        state_key = (
            tuple(sorted(expected["statuses"].items())),
            expected["failure"],
        )
        if state_key in state_keys:
            raise ContractValidationError("two terminal branches have the same predicate")
        state_keys.add(state_key)


def load_and_validate_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    contract = _load_strict_json(path)
    canonical = (json.dumps(contract, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ContractValidationError(f"contract bytes are unreadable: {error}") from error
    if raw != canonical:
        raise ContractValidationError("contract bytes are not canonical sorted JSON")
    validate_contract_payload(contract)
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    arguments = parser.parse_args()
    contract = load_and_validate_contract(arguments.contract.resolve())
    print(
        json.dumps(
            {
                "contract_sha256": _sha256(arguments.contract.resolve()),
                "schema_version": contract["schema_version"],
                "status": "PASS_CONTRACT_V1_VALIDATION",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
