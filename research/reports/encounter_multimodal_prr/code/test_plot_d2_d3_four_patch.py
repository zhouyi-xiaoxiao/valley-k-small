from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plot_d2_d3_four_patch as plotter
import pytest
from PIL import Image


@pytest.fixture(scope="module")
def frozen_sources() -> tuple[dict, dict, dict, dict]:
    return plotter.preflight_sources()


@pytest.fixture(scope="module")
def figure_data(
    frozen_sources: tuple[dict, dict, dict, dict],
) -> plotter.FigureData:
    return plotter.recompute_figure_data(*frozen_sources)


def test_both_source_chains_are_pinned_and_fail_closed(
    frozen_sources: tuple[dict, dict, dict, dict],
    tmp_path: Path,
) -> None:
    d2_result, _d2_manifest, d3_result, _d3_manifest = frozen_sources
    assert d2_result["claim_flags"] == plotter.D2_REQUIRED_CLAIM_FLAGS
    assert d3_result["claim_flags"] == plotter.D3_REQUIRED_CLAIM_FLAGS
    assert d2_result["model"]["parameters"] == d3_result["model"]["parameters"]

    tampered = json.loads(plotter.D3_RESULT.read_text(encoding="utf-8"))
    tampered["claim_flags"]["finite_B_Doi_verified"] = True
    tampered_path = tmp_path / "tampered_d3_result.json"
    tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="pinned d3 result hash mismatch"):
        plotter.preflight_sources(d3_result_path=tampered_path)


def test_recomputed_curves_roots_and_shape_metrics(
    figure_data: plotter.FigureData,
) -> None:
    for dimension in (figure_data.d2, figure_data.d3):
        assert dimension.times.shape == (2401,)
        assert dimension.mixture.shape == (2401,)
        assert dimension.normalized_mixture.shape == (2401,)
        assert dimension.mixture_derivative.shape == (2401,)
        assert dimension.root_times.shape == (5,)
        assert dimension.normalized_root_density.shape == (5,)
        assert [row["topology"] for row in dimension.roots] == [
            "maximum",
            "minimum",
            "maximum",
            "minimum",
            "maximum",
        ]
        assert np.sum(dimension.selected_weights) == pytest.approx(1.0, abs=2.0e-14)
        assert np.max(dimension.normalized_mixture) == pytest.approx(1.0, abs=2.0e-5)
        assert dimension.peak_ratio >= 0.10
        assert max(dimension.valley_ratios) <= 0.85

    assert figure_data.d2.selected_step == pytest.approx(0.11)
    assert figure_data.d3.selected_step == pytest.approx(0.10)
    assert figure_data.d2.peak_ratio == pytest.approx(0.8541266673541315, abs=2.0e-12)
    assert figure_data.d2.valley_ratios == pytest.approx(
        (0.6667854375339219, 0.8375426940831652), abs=2.0e-12
    )
    assert figure_data.d3.peak_ratio == pytest.approx(0.6338081056472881, abs=2.0e-12)
    assert figure_data.d3.valley_ratios == pytest.approx(
        (0.7692448116396059, 0.8448001279484201), abs=2.0e-12
    )
    assert figure_data.d3.peak_ratio < figure_data.d2.peak_ratio
    assert 0.85 - figure_data.d3.valley_ratios[1] == pytest.approx(
        0.005199872051579901, abs=1.0e-12
    )


def test_render_is_byte_deterministic_and_vector_safe(
    figure_data: plotter.FigureData,
    tmp_path: Path,
) -> None:
    first_pdf = tmp_path / "first.pdf"
    first_png = tmp_path / "first.png"
    second_pdf = tmp_path / "second.pdf"
    second_png = tmp_path / "second.png"
    plotter.render_figure(figure_data, first_pdf, first_png)
    plotter.render_figure(figure_data, second_pdf, second_png)
    assert first_pdf.read_bytes() == second_pdf.read_bytes()
    assert first_png.read_bytes() == second_png.read_bytes()
    assert plotter.verify_vector_pdf(first_pdf) == {
        "type3_font_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "raster_image_xobject_tokens": 0,
    }


@pytest.mark.skipif(not plotter.OUTPUT_METADATA.exists(), reason="figure not generated yet")
def test_committed_outputs_metadata_scope_and_vector_integrity() -> None:
    metadata = json.loads(plotter.OUTPUT_METADATA.read_text(encoding="utf-8"))
    assert metadata["status"] == plotter.FIGURE_STATUS
    assert metadata["claim_flags"] == plotter.FIGURE_CLAIM_FLAGS
    assert metadata["chart_contract"] == plotter.CHART_CONTRACT
    assert metadata["recomputation"]["shape_gates"]["d2_pass"] is True
    assert metadata["recomputation"]["shape_gates"]["d3_pass"] is True
    assert metadata["recomputation"]["shape_gates"]["d3_second_valley_margin"] == (
        pytest.approx(0.005199872051579901, abs=1.0e-12)
    )
    for dimension in ("d2", "d3"):
        pins = metadata["source_pins"][dimension]
        assert pins["claim_flags"] in (
            plotter.D2_REQUIRED_CLAIM_FLAGS,
            plotter.D3_REQUIRED_CLAIM_FLAGS,
        )
        for member in ("result", "manifest", "producer", "test"):
            assert pins[f"{member}_sha256"] == plotter.EXPECTED_HASHES[dimension][member]
    assert metadata["pdf_qa"] == {
        "type3_font_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "raster_image_xobject_tokens": 0,
    }
    assert plotter.verify_vector_pdf(plotter.OUTPUT_PDF) == metadata["pdf_qa"]
    assert plotter.d2_design.sha256(plotter.OUTPUT_PDF) == metadata["outputs"]["pdf_sha256"]
    assert plotter.d2_design.sha256(plotter.OUTPUT_PNG) == metadata["outputs"]["png_sha256"]
    assert (
        plotter.d2_design.sha256(Path(plotter.HERE)) == metadata["provenance"]["plot_script_sha256"]
    )
    caption = metadata["caption"]
    for required in (
        "B=0",
        "result-informed",
        "relative-shape-only",
        "continuum_verified=false",
        "finite_B=false",
        "independent_PDE=false",
        "project=false",
        "no event-mass observability claim",
    ):
        assert required in caption
    with Image.open(plotter.OUTPUT_PNG) as preview:
        assert preview.size == (1728, 756)
        assert preview.mode in {"RGB", "RGBA"}
