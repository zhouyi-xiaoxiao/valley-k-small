from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import validate_continuum_c0_model_contract_candidate as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"


def test_v1_contract_fails_closed_after_living_program_map_and_gauge_repairs() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    program_record = contract["frozen_sources"]["continuum_program"]
    program = REPORT / program_record["path"]
    current_sha256 = hashlib.sha256(program.read_bytes()).hexdigest()

    assert current_sha256 != program_record["sha256"]
    assert contract["claim_boundary"]["complete_c0_independently_accepted"] is False
    with pytest.raises(verifier.C0ContractHold) as caught:
        verifier.verify_contract_bytes(CONTRACT.read_bytes())
    assert caught.value.code == verifier.HOLD_SOURCES

