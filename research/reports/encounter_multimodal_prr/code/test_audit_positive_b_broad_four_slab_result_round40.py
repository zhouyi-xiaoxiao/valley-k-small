"""Round-40 adversarial closure tests for the independent positive-B auditor.

These tests encode rejection behavior that the pre-result frozen auditor did
not yet satisfy.  They intentionally remain separate from the original
four-test freeze snapshot so the historical hash is not rewritten.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import audit_positive_b_broad_four_slab_result as audit
import pytest
import test_audit_positive_b_broad_four_slab_result as fixtures


def _rebind_evidence(result: Path, evidence: Path) -> None:
    result_hash = audit.sha256(result)
    payload = audit.load_canonical_object(evidence)
    payload["replica_result_sha256"] = [result_hash, result_hash]
    payload["canonical_result_sha256"] = result_hash
    fixtures._rewrite(evidence, payload)


def test_rejects_root_trace_and_tangent_internal_contradictions(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    row = payload["heldout_mesh_rows"][0]
    root = row["stationary_structure"]["roots"][0]
    root["f_t"] = 123.0
    root["f_tt"] = -1.0e-300
    root["scaled_first_derivative_residual"] = 0.0
    root["scaled_second_derivative"] = -0.1
    row["scan"]["saved_trace"] = [{"time": 0.5, "f": -7.0, "f_t": -9.0, "survival": 2.0}]
    row["time_and_budget_control_jets"]["rows"] = [{"time": "garbage"} for _ in range(5)]
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_unpinned_claim_and_evidence_schema(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["claim_scope"] = "continuum and independent solver verified"
    payload["reproducibility_evidence"] = {}
    payload["mesh_agreement"]["mesh_pair"] = [[1, 1, 1], [2, 2, 2]]
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)
    evidence_payload = audit.load_canonical_object(evidence)
    evidence_payload["stage"] = "unrelated_stage"
    evidence_payload["unrecognized_promotion"] = True
    fixtures._rewrite(evidence, evidence_payload)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_audit_hashes_the_same_result_bytes_that_it_validates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    unsafe_payload = audit.load_canonical_object(result)
    unsafe_payload["independent_solver_verified"] = True
    unsafe_bytes = audit.canonical_bytes(unsafe_payload)
    unsafe_hash = hashlib.sha256(unsafe_bytes).hexdigest()

    evidence_payload = audit.load_canonical_object(evidence)
    evidence_payload["replica_result_sha256"] = [unsafe_hash, unsafe_hash]
    evidence_payload["canonical_result_sha256"] = unsafe_hash
    fixtures._rewrite(evidence, evidence_payload)

    original_loader = audit.load_canonical_object

    def swap_after_load(path: Path) -> dict[str, object]:
        value = original_loader(path)
        if Path(path) == result:
            result.write_bytes(unsafe_bytes)
        return value

    monkeypatch.setattr(audit, "load_canonical_object", swap_after_load)
    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_cli_refuses_to_overwrite_any_input(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    before = result.read_bytes()

    with pytest.raises((SystemExit, TypeError, ValueError)):
        audit.main(
            [
                "--result",
                str(result),
                "--reproducibility",
                str(evidence),
                "--output",
                str(result),
            ]
        )
    assert result.read_bytes() == before
