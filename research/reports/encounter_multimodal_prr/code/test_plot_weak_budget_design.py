from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plot_weak_budget_design as plotter
import pytest


def test_barycentric_mapping_has_declared_vertices() -> None:
    x, y = plotter.barycentric_xy(np.eye(3))
    assert x == pytest.approx([0.0, 1.0, 0.5])
    assert y == pytest.approx([0.0, 0.0, np.sqrt(3.0) / 2.0])


def test_pinned_sources_pass_and_reject_tampered_result(tmp_path: Path) -> None:
    result, manifest = plotter.preflight_sources()
    assert result["simplex_screen"]["sampled_mode_count_histogram"] == {
        "1": 4696,
        "2": 455,
    }
    assert manifest["required_claim_flags"] == plotter.REQUIRED_FALSE_FLAGS

    tampered = json.loads(plotter.RESULT.read_text(encoding="utf-8"))
    tampered["continuum_verified"] = True
    tampered_path = tmp_path / "tampered.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned result hash mismatch"):
        plotter.preflight_sources(result_path=tampered_path)


def test_committed_metadata_is_bounded_and_pins_inputs() -> None:
    metadata = json.loads(plotter.OUTPUT_METADATA.read_text(encoding="utf-8"))
    assert metadata["status"] == "PASS_BOUNDED_FIGURE_REPRODUCTION"
    assert metadata["evidence_timing"] == (
        "RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY"
    )
    assert metadata["continuum_verified"] is False
    assert metadata["project_gate_passed"] is False
    assert metadata["finite_B_Doi_cusp_verified"] is False
    assert metadata["trimodality_verified"] is False
    assert metadata["source_pins"]["result_sha256"] == plotter.EXPECTED_RESULT_SHA256
    assert metadata["source_pins"]["manifest_sha256"] == plotter.EXPECTED_MANIFEST_SHA256
    assert metadata["source_pins"]["producer_sha256"] == plotter.EXPECTED_PRODUCER_SHA256
    assert metadata["recomputation"]["sampled_mode_count_histogram"] == {
        "1": 4696,
        "2": 455,
    }
    assert metadata["recomputation"]["maximum_sampled_mode_count"] == 2
    assert metadata["pdf_qa"] == {
        "raster_image_xobject_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "type3_font_tokens": 0,
    }
    assert plotter.OUTPUT_PDF.is_file()
    assert plotter.OUTPUT_PNG.is_file()
    assert plotter.verify_vector_pdf(plotter.OUTPUT_PDF) == metadata["pdf_qa"]
