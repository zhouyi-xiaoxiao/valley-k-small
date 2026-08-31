from __future__ import annotations

import copy
import json

import pytest

import finalize_encounter_prr_terminal_branch_v1 as terminal


def test_build_receipt_selects_exact_fail_closed_branch() -> None:
    payload = terminal.build_receipt()
    assert payload["schema"] == terminal.SCHEMA
    assert payload["branch"] == terminal.BRANCH
    assert payload["execution"]["failure_class"] == "METHOD_OR_RESOURCE"
    assert payload["execution"]["stage_statuses"] == {
        "f0": "HOLD_F0",
        "f1": "NOT_RUN",
        "f2": "NOT_RUN",
        "f3": "NOT_RUN",
    }
    assert payload["execution"]["formal_f1_rows_executed"] == 0
    assert payload["execution"]["formal_f2_executed"] is False
    assert payload["execution"]["formal_f3_off_lattice_executed"] is False
    assert payload["claim_ceiling"][
        "strict_c0_c3_and_root_transfer"
    ] == "CONDITIONAL_NOT_ELECTED"


def test_published_receipt_is_current() -> None:
    published = json.loads(terminal.OUTPUT_RECEIPT.read_text(encoding="utf-8"))
    assert published == terminal.build_receipt()


def test_contract_cannot_permit_f1_on_selected_branch() -> None:
    contract = terminal._load_json(terminal.CONTRACT)
    mutated = copy.deepcopy(contract)
    mutated["terminal_branches"][terminal.BRANCH]["f1_permitted"] = True
    with pytest.raises(RuntimeError, match="unexpectedly permits"):
        terminal._validate_contract(mutated)


def test_semantic_replay_cannot_promote_f0() -> None:
    receipt = terminal._load_json(terminal.SEMANTIC_RECEIPT)
    mutated = copy.deepcopy(receipt)
    mutated["authority_flags"]["f0_pass"] = True
    with pytest.raises(RuntimeError, match="fail-closed"):
        terminal._validate_semantic_receipt(mutated)


def test_resource_replay_cannot_authorize_science() -> None:
    receipt = terminal._load_json(terminal.RESOURCE_RECEIPT)
    mutated = copy.deepcopy(receipt)
    mutated["promotion_flags"]["authorizes_scientific_execution"] = True
    with pytest.raises(RuntimeError, match="fail-closed"):
        terminal._validate_resource_receipt(mutated)


def test_reader_claim_scope_cannot_be_promoted() -> None:
    compile_manifest = terminal._load_json(terminal.COMPILE_MANIFEST)
    package_manifest = terminal._load_json(terminal.PACKAGE_MANIFEST)
    mutated = copy.deepcopy(compile_manifest)
    mutated["claim_scope"]["finite_parameter_physical_evidence"] = True
    with pytest.raises(RuntimeError, match="claim scope"):
        terminal._validate_reader_artifacts(mutated, package_manifest)
