from __future__ import annotations

import ast
import copy
import json
import os
from pathlib import Path

import compile_manuscript as compiler
import plot_positive_b_broad_four_slab as plotter
import pytest


@pytest.fixture(scope="module")
def canonical_payloads() -> tuple[dict, dict, dict]:
    return plotter.read_pinned_payloads()


@pytest.fixture(scope="module")
def figure_data(canonical_payloads: tuple[dict, dict, dict]) -> plotter.FigureData:
    return plotter.validate_payloads(*canonical_payloads)


def test_preflight_is_bounded_to_the_two_pinned_meshes(
    figure_data: plotter.FigureData,
) -> None:
    assert tuple(mesh.mesh for mesh in figure_data.meshes) == (113, 129)
    for mesh in figure_data.meshes:
        assert tuple(root.topology for root in mesh.roots) == plotter.EXPECTED_TOPOLOGY
        assert len(mesh.trace_times) == 351
        assert mesh.trace_times[0] == 0.0
        assert mesh.trace_times[-1] == 35.0
        assert min(mesh.basin_masses) >= plotter.EVENT_MASS_FLOOR


def test_renderer_has_no_producer_solver_auditor_or_subprocess_import() -> None:
    tree = ast.parse(plotter.HERE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = {
        "positive_b_broad_four_slab",
        "audit_positive_b_broad_four_slab_result",
        "subprocess",
        "scipy",
        "vkcore",
    }
    assert imported.isdisjoint(forbidden)


def test_hard_pins_reject_a_byte_mutation(tmp_path: Path) -> None:
    tampered = tmp_path / "tampered_result.json"
    tampered.write_bytes(plotter.RESULT.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="pinned result hash mismatch"):
        plotter.preflight_sources(result_path=tampered)


def test_false_claim_flag_mutation_is_rejected(
    canonical_payloads: tuple[dict, dict, dict],
) -> None:
    result, reproducibility, audit = copy.deepcopy(canonical_payloads)
    result["continuum_interval_verified"] = True
    with pytest.raises(
        ValueError,
        match="negative claim flag continuum_interval_verified must remain false",
    ):
        plotter.validate_payloads(result, reproducibility, audit)


def test_five_root_topology_mutation_is_rejected(
    canonical_payloads: tuple[dict, dict, dict],
) -> None:
    result, reproducibility, audit = copy.deepcopy(canonical_payloads)
    result["heldout_mesh_rows"][0]["stationary_structure"]["topology"][0] = "minimum"
    with pytest.raises(ValueError, match="topology must remain max-min-max-min-max"):
        plotter.validate_payloads(result, reproducibility, audit)


def test_event_mass_floor_mutation_is_rejected(
    canonical_payloads: tuple[dict, dict, dict],
) -> None:
    result, reproducibility, audit = copy.deepcopy(canonical_payloads)
    result["heldout_mesh_rows"][0]["survival_and_event_mass"]["basin_reaction_masses"][
        0
    ] = 0.0049
    with pytest.raises(ValueError, match="event mass falls below frozen 0.005 floor"):
        plotter.validate_payloads(result, reproducibility, audit)


def test_reproducibility_result_hash_chain_mutation_is_rejected(
    canonical_payloads: tuple[dict, dict, dict],
) -> None:
    result, reproducibility, audit = copy.deepcopy(canonical_payloads)
    reproducibility["canonical_result_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="canonical-result hash chain is broken"):
        plotter.validate_payloads(result, reproducibility, audit)


def test_audit_evidence_hash_chain_mutation_is_rejected(
    canonical_payloads: tuple[dict, dict, dict],
) -> None:
    result, reproducibility, audit = copy.deepcopy(canonical_payloads)
    audit["reproducibility_evidence_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="reproducibility-evidence hash chain is broken"):
        plotter.validate_payloads(result, reproducibility, audit)


def test_validation_failure_does_not_overwrite_prior_pdf(tmp_path: Path) -> None:
    output = tmp_path / "figure.pdf"
    metadata = tmp_path / "figure_metadata.json"
    pdf_sentinel = b"prior-pdf-must-survive"
    metadata_sentinel = b"prior-metadata-must-survive"
    output.write_bytes(pdf_sentinel)
    metadata.write_bytes(metadata_sentinel)
    tampered = tmp_path / "tampered_result.json"
    tampered.write_bytes(plotter.RESULT.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="pinned result hash mismatch"):
        plotter.build_figure(
            result_path=tampered,
            output_path=output,
            metadata_path=metadata,
        )
    assert output.read_bytes() == pdf_sentinel
    assert metadata.read_bytes() == metadata_sentinel


def test_render_failure_does_not_overwrite_prior_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "figure.pdf"
    metadata = tmp_path / "figure_metadata.json"
    pdf_sentinel = b"prior-pdf-must-survive"
    metadata_sentinel = b"prior-metadata-must-survive"
    output.write_bytes(pdf_sentinel)
    metadata.write_bytes(metadata_sentinel)

    def fail_render(_data: plotter.FigureData) -> bytes:
        raise RuntimeError("injected render failure")

    monkeypatch.setattr(plotter, "render_pdf_bytes", fail_render)
    with pytest.raises(RuntimeError, match="injected render failure"):
        plotter.build_figure(output_path=output, metadata_path=metadata)
    assert output.read_bytes() == pdf_sentinel
    assert metadata.read_bytes() == metadata_sentinel


def test_metadata_mutation_does_not_overwrite_prior_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "figure.pdf"
    metadata = tmp_path / "figure_metadata.json"
    pdf_sentinel = b"prior-pdf-must-survive"
    metadata_sentinel = b"prior-metadata-must-survive"
    output.write_bytes(pdf_sentinel)
    metadata.write_bytes(metadata_sentinel)
    original_builder = plotter.build_metadata_payload

    def mutated_metadata(
        data: plotter.FigureData,
        pdf_bytes: bytes,
        pdf_qa: dict[str, int],
    ) -> dict:
        payload = original_builder(data, pdf_bytes, pdf_qa)
        payload["outputs"]["pdf_sha256"] = "0" * 64
        return payload

    monkeypatch.setattr(plotter, "build_metadata_payload", mutated_metadata)
    with pytest.raises(ValueError, match="metadata PDF output pin changed"):
        plotter.build_figure(output_path=output, metadata_path=metadata)
    assert output.read_bytes() == pdf_sentinel
    assert metadata.read_bytes() == metadata_sentinel


def test_pdf_bytes_are_deterministic_and_vector_safe(
    figure_data: plotter.FigureData,
) -> None:
    first = plotter.render_pdf_bytes(figure_data)
    second = plotter.render_pdf_bytes(figure_data)
    assert first == second
    assert plotter.sha256_bytes(first) == plotter.sha256_bytes(second)
    assert plotter.verify_vector_pdf_bytes(first) == {
        "type3_font_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "raster_image_xobject_tokens": 0,
    }


def test_committed_pdf_matches_fresh_render(figure_data: plotter.FigureData) -> None:
    expected = plotter.render_pdf_bytes(figure_data)
    assert plotter.OUTPUT_PDF.read_bytes() == expected
    assert plotter.verify_vector_pdf(plotter.OUTPUT_PDF) == {
        "type3_font_tokens": 0,
        "transparency_graphics_state_tokens": 0,
        "raster_image_xobject_tokens": 0,
    }


def test_metadata_is_canonical_bounded_and_free_of_runtime_paths(
    figure_data: plotter.FigureData,
) -> None:
    pdf_bytes = plotter.render_pdf_bytes(figure_data)
    pdf_qa = plotter.verify_vector_pdf_bytes(pdf_bytes)
    payload = plotter.build_metadata_payload(figure_data, pdf_bytes, pdf_qa)
    plotter.validate_metadata_payload(payload, figure_data, pdf_bytes)
    encoded = plotter.canonical_metadata_bytes(payload)
    assert json.loads(encoded) == payload
    assert encoded == (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False, ensure_ascii=True)
        + "\n"
    ).encode()
    assert payload["outputs"]["pdf_sha256"] == plotter.sha256_bytes(pdf_bytes)
    assert payload["source_pins"] == plotter.expected_source_pins()
    assert payload["claim_flags"] == plotter.METADATA_CLAIM_FLAGS
    assert payload["scope_constraints"] == plotter.METADATA_SCOPE_CONSTRAINTS
    assert b"generated_utc" not in encoded
    assert str(tmp_path_placeholder()).encode() not in encoded


def tmp_path_placeholder() -> Path:
    """A sentinel temporary path that must never leak into canonical metadata."""

    return Path("/tmp/positive-b-figure-runtime")


def test_metadata_pdf_hash_mutation_is_rejected(
    figure_data: plotter.FigureData,
) -> None:
    pdf_bytes = plotter.render_pdf_bytes(figure_data)
    payload = plotter.build_metadata_payload(
        figure_data,
        pdf_bytes,
        plotter.verify_vector_pdf_bytes(pdf_bytes),
    )
    payload["outputs"]["pdf_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="metadata PDF output pin changed"):
        plotter.validate_metadata_payload(payload, figure_data, pdf_bytes)


def test_metadata_source_pin_mutation_is_rejected(
    figure_data: plotter.FigureData,
) -> None:
    pdf_bytes = plotter.render_pdf_bytes(figure_data)
    payload = plotter.build_metadata_payload(
        figure_data,
        pdf_bytes,
        plotter.verify_vector_pdf_bytes(pdf_bytes),
    )
    payload["source_pins"]["plotter_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="metadata source pin changed"):
        plotter.validate_metadata_payload(payload, figure_data, pdf_bytes)


def test_paired_publication_rolls_back_after_second_replace_failure(tmp_path: Path) -> None:
    pdf = tmp_path / "figure.pdf"
    metadata = tmp_path / "figure_metadata.json"
    pdf.write_bytes(b"trusted-old-pdf")
    metadata.write_bytes(b"trusted-old-metadata")
    before = {pdf: pdf.read_bytes(), metadata: metadata.read_bytes()}
    calls = 0

    def fail_second_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second replace failure")
        os.replace(source, target)

    with pytest.raises(OSError, match="injected second replace failure"):
        plotter._publish_transaction(
            {pdf: b"new-pdf", metadata: b"new-metadata"},
            replace=fail_second_replace,
        )
    assert pdf.read_bytes() == before[pdf]
    assert metadata.read_bytes() == before[metadata]
    assert not list(tmp_path.glob(".*.incoming.*"))
    assert not list(tmp_path.glob(".*.backup.*"))


def test_paired_publication_rolls_back_after_directory_sync_failure(tmp_path: Path) -> None:
    pdf = tmp_path / "figure.pdf"
    metadata = tmp_path / "figure_metadata.json"
    pdf.write_bytes(b"trusted-old-pdf")
    metadata.write_bytes(b"trusted-old-metadata")
    before = {pdf: pdf.read_bytes(), metadata: metadata.read_bytes()}

    def fail_sync(_directory: Path) -> None:
        raise OSError("injected directory sync failure")

    with pytest.raises(OSError, match="injected directory sync failure"):
        plotter._publish_transaction(
            {pdf: b"new-pdf", metadata: b"new-metadata"},
            sync_directory=fail_sync,
        )
    assert pdf.read_bytes() == before[pdf]
    assert metadata.read_bytes() == before[metadata]


def test_two_paired_builds_have_identical_pdf_and_metadata_bytes(tmp_path: Path) -> None:
    first_pdf = tmp_path / "first.pdf"
    first_metadata = tmp_path / "first_metadata.json"
    second_pdf = tmp_path / "second.pdf"
    second_metadata = tmp_path / "second_metadata.json"
    first = plotter.build_figure(output_path=first_pdf, metadata_path=first_metadata)
    second = plotter.build_figure(output_path=second_pdf, metadata_path=second_metadata)
    assert first_pdf.read_bytes() == second_pdf.read_bytes()
    assert first_metadata.read_bytes() == second_metadata.read_bytes()
    assert first.sha256 == second.sha256
    assert first.metadata_sha256 == second.metadata_sha256


def test_committed_metadata_matches_fresh_payload(figure_data: plotter.FigureData) -> None:
    pdf_bytes = plotter.render_pdf_bytes(figure_data)
    payload = plotter.build_metadata_payload(
        figure_data,
        pdf_bytes,
        plotter.verify_vector_pdf_bytes(pdf_bytes),
    )
    expected = plotter.canonical_metadata_bytes(payload)
    assert plotter.OUTPUT_METADATA.read_bytes() == expected
    plotter.validate_metadata_payload(json.loads(expected), figure_data, pdf_bytes)


def test_metadata_is_compatible_with_compile_manuscript_provenance() -> None:
    source = (
        r"\graphicspath{{../artifacts/figures/}}"
        "\n"
        r"\includegraphics{positive_b_broad_four_slab.pdf}"
    )
    rows = compiler._figure_provenance(source)
    assert len(rows) == 1
    row = rows[0]
    assert row["sha256"] == plotter.sha256_file(plotter.OUTPUT_PDF)
    roles = {pin["role"] for pin in row["verified_source_pins"]}
    assert roles == {
        "canonical_result",
        "independent_audit",
        "plotter",
        "reproducibility_evidence",
        "test",
    }
