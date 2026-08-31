from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plot_observable_four_patch as plotter
import pytest
from PIL import Image


@pytest.fixture(scope="module")
def frozen_sources() -> tuple[dict, dict]:
    return plotter.preflight_sources()


@pytest.fixture(scope="module")
def figure_data(frozen_sources: tuple[dict, dict]) -> plotter.FigureData:
    return plotter.recompute_figure_data(*frozen_sources)


def test_pinned_sources_pass_and_tampering_fails_closed(
    frozen_sources: tuple[dict, dict],
    tmp_path: Path,
) -> None:
    result, manifest = frozen_sources
    assert result["claim_flags"] == plotter.REQUIRED_CLAIM_FLAGS
    assert manifest["physical_model"]["patch_centres"] == [0.35, 0.6, 0.75, 0.9]

    tampered = json.loads(plotter.RESULT.read_text(encoding="utf-8"))
    tampered["claim_flags"]["continuum_verified"] = True
    tampered_path = tmp_path / "tampered_result.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned result hash mismatch"):
        plotter.preflight_sources(result_path=tampered_path)


def test_recomputed_curves_roots_and_relative_shape(
    figure_data: plotter.FigureData,
) -> None:
    assert figure_data.channels.shape == (2401, 4)
    assert figure_data.channel_derivatives.shape == (2401, 4)
    assert figure_data.mixture == pytest.approx(
        figure_data.channels @ figure_data.selected_weights,
        abs=2.0e-14,
    )
    assert [row["topology"] for row in figure_data.roots] == [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]
    assert figure_data.selected_step == pytest.approx(0.11)
    assert figure_data.relative_shape["peak_minimum_to_maximum_ratio"] == pytest.approx(
        0.8541266673541315,
        abs=2.0e-12,
    )
    assert figure_data.relative_shape["valley_to_smaller_adjacent_peak_ratios"] == (
        pytest.approx([0.6667854375339219, 0.8375426940831652], abs=2.0e-12)
    )
    assert figure_data.relative_shape["maximum_valley_ratio"] <= 0.85
    assert np.sum(figure_data.selected_weights) == pytest.approx(1.0, abs=2.0e-14)


def test_committed_outputs_are_vector_safe_and_bounded() -> None:
    metadata = json.loads(plotter.OUTPUT_METADATA.read_text(encoding="utf-8"))
    assert metadata["status"] == ("PASS_RESULT_INFORMED_FREE_EXPOSURE_RELATIVE_SHAPE_FIGURE")
    assert metadata["publication_scope_flags"] == plotter.PUBLICATION_SCOPE_FLAGS
    assert metadata["claim_flags"] == plotter.REQUIRED_CLAIM_FLAGS
    assert metadata["recomputation"]["maximum_valley_ratio"] <= 0.85
    assert metadata["recomputation"]["peak_minimum_to_maximum_ratio"] >= 0.10
    assert "relative-shape gate" in metadata["caption"]
    assert "not evidence of event-mass observability" in metadata["caption"]
    assert metadata["source_pins"]["result_sha256"] == plotter.EXPECTED_RESULT_SHA256
    assert metadata["source_pins"]["producer_sha256"] == plotter.EXPECTED_PRODUCER_SHA256
    assert metadata["pdf_qa"] == {
        "raster_image_xobject_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "type3_font_tokens": 0,
    }
    assert plotter.verify_vector_pdf(plotter.OUTPUT_PDF) == metadata["pdf_qa"]
    assert plotter.design.sha256(plotter.OUTPUT_PDF) == metadata["outputs"]["pdf_sha256"]
    assert plotter.design.sha256(plotter.OUTPUT_PNG) == metadata["outputs"]["png_sha256"]
    assert plotter.design.sha256(Path(plotter.HERE)) == metadata["provenance"]["plot_script_sha256"]
    with Image.open(plotter.OUTPUT_PNG) as preview:
        assert preview.size == (1728, 1476)
        assert preview.mode in {"RGB", "RGBA"}
