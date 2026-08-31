from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable

import build_positive_b_manuscript_input as build
import pytest


def _write_canonical(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(build.canonical_json_bytes(value))


def _isolated_tree(tmp_path: Path) -> Path:
    report = tmp_path / "report"
    data = report / "artifacts" / "data"
    data.mkdir(parents=True)
    for name in (
        build.MANIFEST_NAME,
        build.RESULT_NAME,
        build.EVIDENCE_NAME,
        build.AUDIT_NAME,
    ):
        shutil.copy2(build.DATA / name, data / name)
    manifest = build.load_object(data / build.MANIFEST_NAME, require_canonical=False)
    for pin in manifest["pinned_files"].values():
        source = build.REPORT / pin["path"]
        target = report / pin["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    auditor_relative = Path("code/audit_positive_b_broad_four_slab_result.py")
    auditor_target = report / auditor_relative
    auditor_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(build.REPORT / auditor_relative, auditor_target)
    return report


def _repin_mutated_result_chain(
    report: Path,
    mutate_result: Callable[[dict[str, Any]], None] | None = None,
    mutate_evidence: Callable[[dict[str, Any]], None] | None = None,
    mutate_audit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, str]:
    data = report / "artifacts" / "data"
    result_path = data / build.RESULT_NAME
    evidence_path = data / build.EVIDENCE_NAME
    audit_path = data / build.AUDIT_NAME
    result = build.load_object(result_path, require_canonical=True)
    if mutate_result is not None:
        mutate_result(result)
    _write_canonical(result_path, result)
    result_hash = build.sha256(result_path)
    evidence = build.load_object(evidence_path, require_canonical=True)
    evidence["canonical_result_sha256"] = result_hash
    evidence["replica_result_sha256"] = [result_hash, result_hash]
    evidence["result_status"] = result["status"]
    evidence["all_gates_passed"] = result["all_gates_passed"]
    if mutate_evidence is not None:
        mutate_evidence(evidence)
    _write_canonical(evidence_path, evidence)
    evidence_hash = build.sha256(evidence_path)
    audit = build.load_object(audit_path, require_canonical=True)
    audit["canonical_result_sha256"] = result_hash
    audit["reproducibility_evidence_sha256"] = evidence_hash
    if mutate_audit is not None:
        mutate_audit(audit)
    _write_canonical(audit_path, audit)
    return {
        "expected_result_sha256": result_hash,
        "expected_evidence_sha256": evidence_hash,
        "expected_audit_sha256": build.sha256(audit_path),
    }


def _repin_mutated_manifest_chain(
    report: Path,
    mutate_manifest: Callable[[dict[str, Any]], None],
) -> dict[str, str]:
    data = report / "artifacts" / "data"
    manifest_path = data / build.MANIFEST_NAME
    result_path = data / build.RESULT_NAME
    evidence_path = data / build.EVIDENCE_NAME
    audit_path = data / build.AUDIT_NAME
    manifest = build.load_object(manifest_path, require_canonical=False)
    mutate_manifest(manifest)
    _write_canonical(manifest_path, manifest)
    manifest_hash = build.sha256(manifest_path)
    result = build.load_object(result_path, require_canonical=True)
    result["manifest_sha256"] = manifest_hash
    _write_canonical(result_path, result)
    result_hash = build.sha256(result_path)
    evidence = build.load_object(evidence_path, require_canonical=True)
    evidence["manifest_sha256"] = manifest_hash
    evidence["canonical_result_sha256"] = result_hash
    evidence["replica_result_sha256"] = [result_hash, result_hash]
    _write_canonical(evidence_path, evidence)
    evidence_hash = build.sha256(evidence_path)
    audit = build.load_object(audit_path, require_canonical=True)
    audit["manifest_sha256"] = manifest_hash
    audit["canonical_result_sha256"] = result_hash
    audit["reproducibility_evidence_sha256"] = evidence_hash
    _write_canonical(audit_path, audit)
    return {
        "expected_manifest_sha256": manifest_hash,
        "expected_result_sha256": result_hash,
        "expected_evidence_sha256": evidence_hash,
        "expected_audit_sha256": build.sha256(audit_path),
    }


def test_live_sources_render_claim_gated_traceable_macros() -> None:
    source = build.render_macros()
    for name in (
        "PositiveBBudget",
        "PositiveBWeights",
        "PositiveBRootTimesOne",
        "PositiveBRootTimesTwo",
        "PositiveBBasinMassesOne",
        "PositiveBBasinMassesTwo",
        "PositiveBBasinOneRange",
        "PositiveBValleyTwoRange",
        "PositiveBFinalSurvivalRange",
        "PositiveBMinimumBasinMass",
        "PositiveBWorstValleyRatio",
        "PositiveBMaximumRootDifference",
    ):
        assert rf"\providecommand{{\{name}}}" in source
    for digest in (
        build.EXPECTED_MANIFEST_SHA256,
        build.EXPECTED_RESULT_SHA256,
        build.EXPECTED_EVIDENCE_SHA256,
        build.EXPECTED_AUDIT_SHA256,
    ):
        assert digest in source
    assert "3.33676,5.09431,8.62228,13.56147,22.54890" in source
    assert "0.00521143,0.01662829,0.14837901" in source
    assert "Forbidden: allocation cusp, continuum/unbounded" in source


def test_false_scope_is_rejected_even_when_the_hash_chain_is_repinned(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["claim_scope"] = "continuum cusp and independent solver verified"

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="claim boundary changed"):
        build.verify_sources(report=report, **hashes)


def test_false_claim_flag_is_rejected_even_when_the_hash_chain_is_repinned(
    tmp_path: Path,
) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["continuum_interval_verified"] = True
        result["required_claim_flags"]["continuum_interval_verified"] = True

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="claim boundary changed"):
        build.verify_sources(report=report, **hashes)


def test_two_process_contract_is_reconstructed_not_only_hash_checked(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(evidence: dict[str, Any]) -> None:
        evidence["independent_process_count"] = 1

    hashes = _repin_mutated_result_chain(report, mutate_evidence=mutate)
    with pytest.raises(RuntimeError, match="two-process evidence contract changed"):
        build.verify_sources(report=report, **hashes)


def test_peak_ratio_failure_is_rejected_after_a_full_core_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        for row in result["heldout_mesh_rows"]:
            row["stationary_structure"]["peak_minimum_to_maximum_ratio"] = 0.01

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="peak ratio does not reconstruct"):
        build.verify_sources(report=report, **hashes)


def test_root_residual_and_curvature_failure_is_rejected_after_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        root = result["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]
        root["f_t"] = root["density"] / root["time"]
        root["scaled_first_derivative_residual"] = 1.0
        root["f_tt"] = abs(root["f_tt"])
        root["scaled_second_derivative"] = root["time"] ** 2 * root["f_tt"] / root["density"]

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError):
        build.verify_sources(report=report, **hashes)


def test_result_final_time_must_equal_the_manifest_after_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        for row in result["heldout_mesh_rows"]:
            row["survival_and_event_mass"]["final_time"] = 50.0

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="final time changed"):
        build.verify_sources(report=report, **hashes)


def test_result_weights_must_equal_the_frozen_manifest_after_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["fixed_absolute_weights"] = [0.25, 0.25, 0.25, 0.25]

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="claim boundary changed"):
        build.verify_sources(report=report, **hashes)


def test_mesh_agreement_ceiling_is_reconstructed_after_manifest_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(manifest: dict[str, Any]) -> None:
        manifest["mesh_agreement"]["maximum_paired_root_time_difference"] = 0.01

    hashes = _repin_mutated_manifest_chain(report, mutate)
    with pytest.raises(RuntimeError, match="mesh-agreement thresholds changed"):
        build.verify_sources(report=report, **hashes)


@pytest.mark.parametrize(
    ("field", "mutated_value", "message"),
    (
        ("f", -1.0, "sampled minimum contradicts"),
        ("boundary_layer_fraction", 0.5, "boundary maximum contradicts"),
        ("differential_mass_balance_residual", 1.0, "mass residual contradicts"),
        ("survival", 0.999, "survival-increase summary contradicts"),
    ),
)
def test_saved_trace_cannot_hide_an_extreme_behind_unchanged_scan_summaries(
    tmp_path: Path,
    field: str,
    mutated_value: float,
    message: str,
) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["heldout_mesh_rows"][0]["scan"]["saved_trace"][100][field] = mutated_value

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match=message):
        build.verify_sources(report=report, **hashes)


def test_scan_tail_junction_reconstructs_density_as_well_as_survival(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        row = result["heldout_mesh_rows"][0]
        row["tail_35_to_100"]["trace"][0]["density"] += 1.0e-4

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="scan/tail junction changed"):
        build.verify_sources(report=report, **hashes)


def test_negative_error_cannot_pass_an_upper_bound_gate_after_full_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["heldout_mesh_rows"][0]["diagnostics"]["initial_mass_error"] = -1.0

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="must be nonnegative"):
        build.verify_sources(report=report, **hashes)


@pytest.mark.parametrize(
    ("field", "mutated_value", "message"),
    (
        ("survival", 1.5, "must lie in"),
        ("differential_mass_balance_residual", -1.0, "must be nonnegative"),
        ("boundary_layer_fraction", 2.0, "must lie in"),
    ),
)
def test_root_probability_and_residual_domains_are_fail_closed(
    tmp_path: Path,
    field: str,
    mutated_value: float,
    message: str,
) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0][field] = (
            mutated_value
        )

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match=message):
        build.verify_sources(report=report, **hashes)


def test_negative_tangent_norm_cannot_pass_an_upper_bound_gate(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        row = result["heldout_mesh_rows"][0]["time_and_budget_control_jets"]["rows"][0]
        row["direct_vs_tangent_state_relative_l1"] = -1.0

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="must be nonnegative"):
        build.verify_sources(report=report, **hashes)


def test_each_reported_root_requires_a_saved_trace_sign_bracket(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        mesh = result["heldout_mesh_rows"][0]
        root_time = mesh["stationary_structure"]["roots"][0]["time"]
        trace = mesh["scan"]["saved_trace"]
        index = next(
            i
            for i, (left, right) in enumerate(zip(trace[:-1], trace[1:], strict=True))
            if left["time"] <= root_time <= right["time"]
        )
        trace[index]["f_t"] = abs(trace[index]["f_t"])
        trace[index + 1]["f_t"] = abs(trace[index + 1]["f_t"])

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="lacks a saved-trace sign bracket"):
        build.verify_sources(report=report, **hashes)


def test_root_survival_must_lie_inside_its_saved_time_bracket(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["heldout_mesh_rows"][0]["stationary_structure"]["roots"][0]["survival"] = (
            0.996
        )

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="survival lies outside its saved-trace bracket"):
        build.verify_sources(report=report, **hashes)


def test_manifest_repin_cannot_weaken_the_process_count_contract(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(manifest: dict[str, Any]) -> None:
        manifest["numerical_reproducibility"]["independent_full_processes_required"] = 1

    hashes = _repin_mutated_manifest_chain(report, mutate)
    with pytest.raises(RuntimeError, match="manifest identity or claim boundary changed"):
        build.verify_sources(report=report, **hashes)


def test_nested_publication_claim_and_positive_limitation_text_are_rejected(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["numerical_reproducibility"]["publication_gate_passed"] = True
        result["limitations"] = ["continuum and publication ready"]

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="unauthorized location"):
        build.verify_sources(report=report, **hashes)


def test_empty_software_versions_are_rejected_after_full_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["software"] = {"python": "", "numpy": "", "scipy": ""}

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="software versions must be nonempty"):
        build.verify_sources(report=report, **hashes)


def test_reproducibility_evidence_rejects_python_bool_integer_aliases(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(evidence: dict[str, Any]) -> None:
        evidence["schema_version"] = 1.0
        evidence["independent_process_count"] = 2.0
        evidence["replica_exit_codes"] = [False, False]
        evidence["byte_identical"] = 1
        evidence["canonical_promotion_after_comparison"] = 1
        evidence["all_gates_passed"] = 1

    hashes = _repin_mutated_result_chain(report, mutate_evidence=mutate)
    with pytest.raises(RuntimeError, match="two-process evidence contract changed"):
        build.verify_sources(report=report, **hashes)


def test_result_agreement_gate_map_rejects_integer_aliases(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["mesh_agreement"]["gates"] = {
            key: 1 for key in result["mesh_agreement"]["gates"]
        }

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="non-Boolean"):
        build.verify_sources(report=report, **hashes)


def test_audit_source_hash_and_extrema_contract_are_reconstructed(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(audit: dict[str, Any]) -> None:
        audit["auditor_sha256"] = "0" * 64
        for mesh in audit["mesh_reconstructions"]:
            mesh["producer_reported_full_scan_extrema_used"] = []

    hashes = _repin_mutated_result_chain(report, mutate_audit=mutate)
    with pytest.raises(RuntimeError, match="independent-audit contract changed"):
        build.verify_sources(report=report, **hashes)


def test_audit_gate_maps_reject_python_integer_aliases(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(audit: dict[str, Any]) -> None:
        for key, value in list(audit["claim_boundary"].items()):
            if type(value) is bool:
                audit["claim_boundary"][key] = int(value)
        audit["agreement_reconstruction"]["gates"] = {
            key: 1 for key in audit["agreement_reconstruction"]["gates"]
        }
        for mesh in audit["mesh_reconstructions"]:
            mesh["independently_algebraically_reconstructed_gates"] = {
                key: 1 for key in mesh["independently_algebraically_reconstructed_gates"]
            }

    hashes = _repin_mutated_result_chain(report, mutate_audit=mutate)
    with pytest.raises(RuntimeError, match="non-Boolean"):
        build.verify_sources(report=report, **hashes)


def test_stationary_root_count_requires_an_integer_after_full_repin(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        result["heldout_mesh_rows"][0]["stationary_structure"]["stationary_root_count"] = 5.0

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match="exactly five retained roots"):
        build.verify_sources(report=report, **hashes)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("spacing", "spacings contradict"),
        ("contact_exact", "exact contact area contradicts"),
        ("contact_actual", "factor normalization fails"),
        ("initial_mass", "factor normalization fails"),
        ("patch_integrals", "factor normalization fails"),
        ("row_error", "factor normalization fails"),
        ("zero_trace", "trace must be negative"),
        ("augmented_trace", "not twice the base trace"),
    ),
)
def test_fixed_geometry_factor_and_trace_diagnostics_are_reconstructed(
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(result: dict[str, Any]) -> None:
        row = result["heldout_mesh_rows"][0]
        factor = row["diagnostics"]["factor_diagnostics"]
        if mutation == "spacing":
            factor["spacings"]["midpoint"] = 999.0
        elif mutation == "contact_exact":
            factor["contact_area_exact"] = 1.0
        elif mutation == "contact_actual":
            factor["contact_area"] = 2.0
        elif mutation == "initial_mass":
            factor["midpoint_initial_mass"] = 2.0
        elif mutation == "patch_integrals":
            weights = result["fixed_absolute_weights"]
            factor["patch_integrals"][0] += 0.2
            factor["patch_integrals"][1] -= 0.2 * weights[0] / weights[1]
        elif mutation == "row_error":
            factor["relative_generator_row_error"] = 1.0e6
        elif mutation == "zero_trace":
            row["diagnostics"]["analytic_column_operator_trace"] = 0.0
            row["time_and_budget_control_jets"]["analytic_augmented_operator_trace"] = 0.0
        elif mutation == "augmented_trace":
            row["time_and_budget_control_jets"]["analytic_augmented_operator_trace"] = -1.0
        else:  # pragma: no cover - the parameter table is closed above
            raise AssertionError(mutation)

    hashes = _repin_mutated_result_chain(report, mutate_result=mutate)
    with pytest.raises(RuntimeError, match=message):
        build.verify_sources(report=report, **hashes)


def test_audit_mesh_identity_requires_an_integer(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)

    def mutate(audit: dict[str, Any]) -> None:
        audit["mesh_reconstructions"][0]["mesh"] = 113.0

    hashes = _repin_mutated_result_chain(report, mutate_audit=mutate)
    with pytest.raises(RuntimeError, match="identity must be an integer"):
        build.verify_sources(report=report, **hashes)


def test_render_uses_the_verified_snapshot_not_a_later_path_read(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)
    verified = build.verify_sources(report=report)
    result_path = report / "artifacts" / "data" / build.RESULT_NAME
    result = build.load_object(result_path, require_canonical=True)
    result["fixed_absolute_weights"] = [0.25, 0.25, 0.25, 0.25]
    _write_canonical(result_path, result)
    rendered = build.render_verified_macros(verified)
    assert "0.28000000,0.27736690,0.08571723,0.35691587" in rendered
    assert "0.25000000,0.25000000,0.25000000,0.25000000" not in rendered


def test_manifest_pin_content_mutation_is_rejected(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)
    manifest = build.load_object(
        report / "artifacts" / "data" / build.MANIFEST_NAME,
        require_canonical=False,
    )
    relative = manifest["pinned_files"]["protocol"]["path"]
    target = report / relative
    target.write_bytes(target.read_bytes() + b"\nmutation\n")
    with pytest.raises(RuntimeError, match="pin protocol SHA-256 mismatch"):
        build.verify_sources(report=report)


def test_symlinked_pin_is_rejected_even_when_target_bytes_match(tmp_path: Path) -> None:
    report = _isolated_tree(tmp_path)
    manifest = build.load_object(
        report / "artifacts" / "data" / build.MANIFEST_NAME,
        require_canonical=False,
    )
    relative = manifest["pinned_files"]["protocol"]["path"]
    target = report / relative
    backup = target.with_name(f"{target.name}.ordinary")
    target.replace(backup)
    target.symlink_to(backup.name)
    with pytest.raises(RuntimeError, match="ordinary nonsymlink"):
        build.verify_sources(report=report)


def test_failed_preflight_does_not_overwrite_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "positive_b_results.tex"
    output.write_bytes(b"trusted-old-output\n")

    def reject(**_kwargs: Any) -> str:
        raise RuntimeError("injected source-chain failure")

    monkeypatch.setattr(build, "render_macros", reject)
    with pytest.raises(RuntimeError, match="injected source-chain failure"):
        build.main(("--output", str(output)))
    assert output.read_bytes() == b"trusted-old-output\n"


def test_scientific_notation_is_valid_tex() -> None:
    assert build.tex_sci(1.0255676151960103e-4) == r"1.03\times10^{-4}"
