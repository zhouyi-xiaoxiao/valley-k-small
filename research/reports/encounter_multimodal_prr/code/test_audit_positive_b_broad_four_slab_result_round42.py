"""Round-42 adversarial tests for the repaired positive-B result auditor.

The auditor still carries the pre-erratum manifest anchor.  These tests pin the
documented v2 operational-erratum manifest explicitly so downstream audit
logic can be attacked without weakening or editing the production auditor.
All result/evidence mutations occur under ``tmp_path``; no formal output is
read or written.
"""

from __future__ import annotations

from pathlib import Path

import audit_positive_b_broad_four_slab_result as audit
import pytest
import test_audit_positive_b_broad_four_slab_result as fixtures

V2_MANIFEST_SHA256 = "955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c"


@pytest.fixture(autouse=True)
def _exercise_v2_downstream_logic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the obsolete embedded pin visible while exercising v2 logic."""

    assert audit.sha256(audit.MANIFEST) == V2_MANIFEST_SHA256
    monkeypatch.setattr(audit, "EXPECTED_MANIFEST_SHA256", V2_MANIFEST_SHA256)


def _rebind_evidence(result: Path, evidence: Path) -> None:
    result_hash = audit.sha256(result)
    payload = audit.load_canonical_object(evidence)
    payload["replica_result_sha256"] = [result_hash, result_hash]
    payload["canonical_result_sha256"] = result_hash
    fixtures._rewrite(evidence, payload)


def test_v2_anchor_reaches_repaired_downstream_auditor(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.audit(result_path=result, reproducibility_path=evidence)
    assert payload["status"] == "PASS_INDEPENDENT_RECONSTRUCTION"


def test_rejects_bool_and_float_aliases_in_nested_reproducibility_contract(
    tmp_path: Path,
) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["reproducibility_evidence"]["independent_full_processes_required"] = 2.0
    payload["reproducibility_evidence"]["canonical_result_requires_external_byte_comparison"] = 1
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_unknown_claim_alias_inside_factor_diagnostics(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["diagnostics"]["factor_diagnostics"] = {
        "independent_solver_verified": True
    }
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_root_survival_outside_its_saved_trace_bracket(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    root = payload["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]
    root["survival"] = 2.0
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_one_mesh_structural_hold_is_reproduced(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    fixtures._convert_to_structural_hold(result, evidence)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][1] = fixtures._row(129)
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    audited = audit.audit(result_path=result, reproducibility_path=evidence)
    assert audited["status"] == "HOLD_REPRODUCED"
    assert audited["scientific_result_passed"] is False


@pytest.mark.parametrize("token", [b"NaN", b"Infinity", b"-Infinity"])
def test_rejects_nonfinite_raw_json_numbers(tmp_path: Path, token: bytes) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    raw = result.read_bytes()
    unsafe = raw.replace(b'"density": 1.0', b'"density": ' + token, 1)
    assert unsafe != raw
    result.write_bytes(unsafe)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_atomic_publish_rejects_a_protected_output_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protected = tmp_path / "input.json"
    protected.write_bytes(b"protected\n")
    before = protected.read_bytes()
    snapshots = {protected.resolve(): audit.sha256(protected)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", protected)

    with pytest.raises((TypeError, ValueError), match="aliases a protected input"):
        audit.atomic_publish(protected, {"status": "test"}, snapshots)
    assert protected.read_bytes() == before


def test_atomic_publish_preserves_prior_output_if_directory_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    prior = b"prior audit\n"
    output.write_bytes(prior)
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    real_fsync = audit.os.fsync
    calls = 0

    def fail_directory_fsync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(audit.os, "fsync", fail_directory_fsync)
    with pytest.raises(OSError, match="directory fsync failure"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)

    assert output.read_bytes() == prior
    assert not output.with_name(f".{output.name}.staging").exists()


def test_atomic_publish_detects_last_instant_input_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    real_replace = audit.os.replace

    def swap_then_replace(source: Path, target: Path) -> None:
        audited_input.write_bytes(b"swapped after final precheck\n")
        real_replace(source, target)

    monkeypatch.setattr(audit.os, "replace", swap_then_replace)
    with pytest.raises((TypeError, ValueError), match="changed"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)

    assert not output.exists()
