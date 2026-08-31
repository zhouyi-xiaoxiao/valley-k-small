from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plot_g1d_fold as plotter
import pytest


def test_barycentric_mapping_has_declared_vertices() -> None:
    x, y = plotter.barycentric_xy(np.eye(3))
    assert x == pytest.approx([0.0, 1.0, 0.5])
    assert y == pytest.approx([0.0, 0.0, np.sqrt(3.0) / 2.0])


def test_pinned_sources_pass_and_reject_tampered_result(tmp_path: Path) -> None:
    result, manifest = plotter.preflight_sources()
    assert result["status"] == "PASS_FINITE_GRID_FOLD_ONLY"
    assert result["finite_grid_fold_confirmed"] is True
    assert result["finite_B_Doi_fold"] is True
    assert result["continuum_verified"] is False
    assert result["project_gate_passed"] is False
    assert manifest["pinned_inputs"]["runner_sha256"] == plotter.EXPECTED_RUNNER_SHA256

    tampered = json.loads(plotter.RESULT.read_text(encoding="utf-8"))
    tampered["continuum_verified"] = True
    tampered_path = tmp_path / "tampered.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned result hash mismatch"):
        plotter.preflight_sources(result_path=tampered_path)


def test_local_normal_form_opens_to_lambda_minus_side() -> None:
    result, _manifest = plotter.preflight_sources()
    offsets = np.asarray((-0.4, 0.0, 0.4))
    controls = plotter.normal_form_control_offsets(result, offsets)
    assert controls[0] == pytest.approx(controls[2], abs=1.0e-15)
    assert controls[0] < 0.0
    assert controls[1] == pytest.approx(0.0, abs=1.0e-18)

    predicted = plotter.predicted_time_offset_magnitude(result, -0.02)
    f_tlambda = float(result["fold"]["control_jets_orders_0_to_3"][1])
    f_ttt = float(result["fold"]["time_jets_orders_0_to_3"][3])
    artifact_formula = float(np.sqrt(-2.0 * f_tlambda * -0.02 / f_ttt))
    assert predicted == pytest.approx(artifact_formula, rel=0.0, abs=1.0e-15)
    assert predicted == pytest.approx(0.4269048074, rel=0.0, abs=1.0e-10)
    fold_time = float(result["fold"]["time"])
    local_roots = result["side_topology"][0]["roots"][1:]
    observed = [float(row["time"]) - fold_time for row in local_roots]
    assert observed[0] == pytest.approx(-predicted, abs=0.035)
    assert observed[1] == pytest.approx(predicted, abs=0.035)


def test_committed_metadata_is_bounded_and_pins_inputs() -> None:
    metadata = json.loads(plotter.OUTPUT_METADATA.read_text(encoding="utf-8"))
    assert metadata["status"] == "PASS_BOUNDED_FIGURE_REPRODUCTION"
    assert metadata["claim_scope"] == "one 65x65x49 finite-grid B=0.6 fold only"
    assert metadata["finite_grid_fold_confirmed"] is True
    assert metadata["finite_B_Doi_fold"] is True
    assert metadata["continuum_verified"] is False
    assert metadata["project_gate_passed"] is False
    assert metadata["observable_trimodality_verified"] is False
    assert metadata["interval_global_root_proof"] is False
    assert metadata["source_pins"]["result_sha256"] == plotter.EXPECTED_RESULT_SHA256
    assert metadata["source_pins"]["manifest_sha256"] == plotter.EXPECTED_MANIFEST_SHA256
    assert metadata["recomputation"]["retained_side_root_counts"] == [3, 1]
    assert metadata["recomputation"]["strict_sign_change_bracket_counts_all_three_controls"] == [
        3,
        1,
        1,
    ]
    caption = metadata["caption"]
    assert "one 65x65x49 finite-grid B=0.6 fold only" in caption
    assert "retained sign-changing roots" in caption
    assert "not an interval-global root proof" in caption
    assert "continuum_verified and project_gate_passed flags are false" in caption
    assert plotter.OUTPUT_PDF.is_file()
    assert plotter.OUTPUT_PNG.is_file()
    assert plotter.verify_vector_pdf(plotter.OUTPUT_PDF) == metadata["pdf_qa"]
