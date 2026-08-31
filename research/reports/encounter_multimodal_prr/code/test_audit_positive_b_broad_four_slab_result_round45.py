"""Independent Round-45 closure attacks for the positive-B result auditor."""

from __future__ import annotations

import math
from pathlib import Path

import audit_positive_b_broad_four_slab_result as audit
import pytest
import test_audit_positive_b_broad_four_slab_result as fixtures

FROZEN_AUDITOR_SHA256 = "8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985"


@pytest.fixture(autouse=True)
def _frozen_resolution_snapshot() -> None:
    assert audit.sha256(audit.HERE) == FROZEN_AUDITOR_SHA256


def _rebind_evidence(result: Path, evidence: Path) -> None:
    result_hash = audit.sha256(result)
    payload = audit.load_canonical_object(evidence)
    payload["replica_result_sha256"] = [result_hash, result_hash]
    payload["canonical_result_sha256"] = result_hash
    fixtures._rewrite(evidence, payload)


def _make_hold(result: Path, evidence: Path) -> None:
    payload = audit.load_canonical_object(result)
    payload["status"] = "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
    payload["positive_B_event_mass_shape_confirmation"] = False
    payload["all_gates_passed"] = False
    fixtures._rewrite(result, payload)
    evidence_payload = audit.load_canonical_object(evidence)
    evidence_payload["replica_exit_codes"] = [2, 2]
    evidence_payload["result_status"] = payload["status"]
    evidence_payload["all_gates_passed"] = False
    fixtures._rewrite(evidence, evidence_payload)
    _rebind_evidence(result, evidence)


def test_rejects_float_aliases_in_integer_mesh_triplets(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    mesh_pair: list[list[float]] = []
    for row in payload["heldout_mesh_rows"]:
        cells = float(row["mesh"][0])
        row["mesh"] = [cells, cells, cells]
        row["diagnostics"]["mesh"] = [cells, cells, cells]
        mesh_pair.append([cells, cells, cells])
    payload["mesh_agreement"]["mesh_pair"] = mesh_pair
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_gross_root_trace_mismatch_even_on_survival_hold(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    row = payload["heldout_mesh_rows"][0]
    row["stationary_structure"]["roots"][0]["survival"] = 0.999
    row["scan"]["maximum_sampled_survival_increase"] = 1.0
    row["gates"]["survival_monotone_through_final_time"] = False
    row["all_mesh_gates_passed"] = False
    fixtures._rewrite(result, payload)
    _make_hold(result, evidence)

    with pytest.raises((TypeError, ValueError), match="survival"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_root_survival_bracket_uses_the_frozen_tolerance_boundary(tmp_path: Path) -> None:
    manifest = audit.load_object(audit.MANIFEST)
    tolerance = float(manifest["root_gates"]["maximum_negative_state_tolerance"])
    bracket_upper = 0.99

    at_boundary = tmp_path / "at_boundary"
    at_boundary.mkdir()
    result, evidence = fixtures._write_bundle(at_boundary)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]["survival"] = (
        bracket_upper + tolerance
    )
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)
    assert audit.audit(result_path=result, reproducibility_path=evidence)[
        "scientific_result_passed"
    ]

    past_boundary = tmp_path / "past_boundary"
    past_boundary.mkdir()
    result, evidence = fixtures._write_bundle(past_boundary)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]["survival"] = (
        math.nextafter(bracket_upper + tolerance, math.inf)
    )
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)
    with pytest.raises(ValueError, match="survival"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_forbidden_claim_key_inside_a_nested_list(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["time_and_budget_control_jets"]["rows"][0][
        "budget_control_jets"
    ]["allocation_cusp_verified"] = False
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises(ValueError, match="claim key allocation_cusp_verified"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_post_replace_auditor_source_swap_is_rolled_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    fake_auditor = tmp_path / "auditor.py"
    fake_auditor.write_bytes(b"frozen auditor\n")
    monkeypatch.setattr(audit, "HERE", fake_auditor)
    audited = audit.audit(
        result_path=result,
        reproducibility_path=evidence,
        return_snapshots=True,
    )
    assert type(audited) is tuple
    payload, snapshots = audited

    output = tmp_path / "audit.json"
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)
    real_replace = audit.os.replace

    def swap_source_then_replace(source: Path, target: Path) -> None:
        fake_auditor.write_bytes(b"changed auditor\n")
        real_replace(source, target)

    monkeypatch.setattr(audit.os, "replace", swap_source_then_replace)
    with pytest.raises(ValueError, match="audited input changed"):
        audit.atomic_publish(output, payload, snapshots)
    assert not output.exists()


def test_post_replace_input_swap_restores_prior_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audited_input = tmp_path / "input.json"
    audited_input.write_bytes(b"input\n")
    output = tmp_path / "audit.json"
    prior = b"prior audit\n"
    output.write_bytes(prior)
    snapshots = {audited_input.resolve(): audit.sha256(audited_input)}
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)
    real_replace = audit.os.replace
    replace_calls = 0

    def swap_after_precheck(source: Path, target: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 1:
            audited_input.write_bytes(b"changed input\n")
        real_replace(source, target)

    monkeypatch.setattr(audit.os, "replace", swap_after_precheck)
    with pytest.raises(ValueError, match="audited input changed"):
        audit.atomic_publish(output, {"status": "new"}, snapshots)
    assert output.read_bytes() == prior


def test_rejects_near_synonym_for_exact_producer_limitation(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["limitations"][-1] = "no physical d3 or project/publication gate"
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises(ValueError, match="limitations changed"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_negative_absolute_errors_and_mass_balance_residuals(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    row = payload["heldout_mesh_rows"][0]
    diagnostics = row["diagnostics"]
    diagnostics["initial_mass_error"] = -1.0
    diagnostics["killed_mass_balance_operator_error"] = -1.0
    factors = diagnostics["factor_diagnostics"]
    for key in (
        "contact_area_error_estimate",
        "maximum_initial_quadrature_error_estimate",
        "maximum_patch_quadrature_error_estimate",
        "midpoint_generator_row_error",
        "relative_generator_row_error",
    ):
        factors[key] = -1.0
    for root in row["stationary_structure"]["roots"]:
        root["differential_mass_balance_residual"] = -1.0
    tail_trace = row["tail_35_to_100"]["trace"]
    for tail_row in tail_trace[1:]:
        tail_row["differential_mass_balance_residual"] = -1.0
    row["survival_and_event_mass"]["final_differential_mass_balance_residual"] = -1.0
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_out_of_range_boundary_layer_fraction(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0][
        "boundary_layer_fraction"
    ] = 2.0
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError), match="boundary"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_integer_alias_for_conditional_float_ratio(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    for row in payload["heldout_mesh_rows"]:
        roots = row["stationary_structure"]["roots"]
        controls = row["time_and_budget_control_jets"]["rows"]
        for index in (2, 4):
            roots[index]["density"] = 1.0
            roots[index]["scaled_second_derivative"] = (
                roots[index]["time"] ** 2 * roots[index]["f_tt"] / roots[index]["density"]
            )
            controls[index]["time_jets_f_f_t_f_tt_f_ttt"][0] = 1.0
        row["stationary_structure"]["peak_minimum_to_maximum_ratio"] = 1
        row["stationary_structure"]["valley_to_smaller_adjacent_peak_ratios"] = [0.5, 0.4]
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_negative_reported_absolute_agreement_difference(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["mesh_agreement"]["peak_ratio_absolute_difference"] = -1.0e-15
    fixtures._rewrite(result, payload)
    _rebind_evidence(result, evidence)

    with pytest.raises((TypeError, ValueError)):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_audit_rejects_an_initial_input_symlink(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    result_link = tmp_path / "result-link.json"
    result_link.symlink_to(result.name)

    with pytest.raises((TypeError, ValueError), match="non-symlink regular file"):
        audit.audit(result_path=result_link, reproducibility_path=evidence)


def test_publication_rejects_regular_input_replaced_by_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    audited = audit.audit(result_path=result, reproducibility_path=evidence, return_snapshots=True)
    assert type(audited) is tuple
    payload, snapshots = audited

    unsafe = tmp_path / "unsafe-result.json"
    unsafe.write_bytes(b'{"unsafe":true}\n')
    result.unlink()
    result.symlink_to(unsafe.name)
    output = tmp_path / "audit.json"
    monkeypatch.setattr(audit, "AUDIT_OUTPUT", output)

    with pytest.raises((TypeError, ValueError), match="symlink|changed"):
        audit.atomic_publish(output, payload, snapshots)
    assert not output.exists()


def test_audit_rejects_initial_evidence_and_manifest_symlinks(tmp_path: Path) -> None:
    result, evidence = fixtures._write_bundle(tmp_path)
    evidence_link = tmp_path / "evidence-link.json"
    evidence_link.symlink_to(evidence.name)
    with pytest.raises((TypeError, ValueError), match="non-symlink regular file"):
        audit.audit(result_path=result, reproducibility_path=evidence_link)

    manifest_link = tmp_path / "manifest-link.json"
    manifest_link.symlink_to(audit.MANIFEST)
    with pytest.raises((TypeError, ValueError), match="non-symlink regular file"):
        audit.audit(
            result_path=result,
            reproducibility_path=evidence,
            manifest_path=manifest_link,
        )


def test_manifest_validation_rejects_a_symlinked_pinned_file(tmp_path: Path) -> None:
    report = tmp_path / "report"
    code = report / "code"
    code.mkdir(parents=True)
    producer = code / "positive_b_broad_four_slab.py"
    producer.symlink_to(audit.REPORT / "code" / producer.name)

    with pytest.raises((TypeError, ValueError), match="pinned input producer.*non-symlink"):
        audit.validate_manifest(audit.MANIFEST, report)
