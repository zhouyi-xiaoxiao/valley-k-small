"""Resolution tests for Round-42 post-result-auditor findings."""

from __future__ import annotations

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


@pytest.mark.parametrize("survival", [0.990000000002, 1.000000000002])
def test_rejects_root_survival_outside_frozen_tolerance(tmp_path: Path, survival: float) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]["survival"] = survival
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises(ValueError, match="survival"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_python_numeric_alias_in_manifest_copied_float(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    assert payload["physical_parameters"]["transverse_width"] == 1.0
    payload["physical_parameters"]["transverse_width"] = 1
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises(ValueError, match="physical parameters mismatch"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_audit_publication_snapshot_includes_auditor_source(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    audited = audit.audit(
        result_path=result,
        reproducibility_path=evidence,
        return_snapshots=True,
    )
    assert type(audited) is tuple
    payload, snapshots = audited
    assert snapshots[audit.HERE.resolve()] == audit.sha256(audit.HERE)
    assert payload["auditor_sha256"] == snapshots[audit.HERE.resolve()]


def test_atomic_publish_preserves_prior_output_if_file_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    prior = b"prior audit\n"
    output.write_bytes(prior)
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    def fail_fsync(_fd: int) -> None:
        raise OSError("injected file fsync failure")

    monkeypatch.setattr(audit.os, "fsync", fail_fsync)
    with pytest.raises(OSError, match="file fsync failure"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)

    assert output.read_bytes() == prior
    assert not output.with_name(f".{output.name}.staging").exists()


def test_atomic_publish_preserves_prior_output_if_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    prior = b"prior audit\n"
    output.write_bytes(prior)
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    def fail_replace(_source: Path, _target: Path) -> None:
        raise OSError("injected replace failure")

    monkeypatch.setattr(audit.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failure"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)

    assert output.read_bytes() == prior
    assert not output.with_name(f".{output.name}.staging").exists()


def test_atomic_publish_removes_new_output_if_directory_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    real_fsync = audit.os.fsync
    calls = 0

    def fail_second_fsync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(audit.os, "fsync", fail_second_fsync)
    with pytest.raises(OSError, match="directory fsync failure"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)

    assert not output.exists()
    assert not output.with_name(f".{output.name}.staging").exists()
