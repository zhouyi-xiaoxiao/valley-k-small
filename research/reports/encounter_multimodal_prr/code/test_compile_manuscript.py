from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import compile_manuscript as build
import pytest


def _isolated_positive_figure_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, str]:
    report = tmp_path / "report"
    manuscript = report / "manuscript"
    figure_dir = report / "artifacts" / "figures"
    manuscript.mkdir(parents=True)
    figure_dir.mkdir(parents=True)
    figure = build.REPORT / "artifacts" / "figures" / "positive_b_broad_four_slab.pdf"
    metadata = figure.with_name("positive_b_broad_four_slab_metadata.json")
    shutil.copy2(figure, figure_dir / figure.name)
    shutil.copy2(metadata, figure_dir / metadata.name)
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    for label, value in payload["source_pins"].items():
        if label.endswith("_sha256"):
            continue
        source = build.REPORT / value
        target = report / value
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    monkeypatch.setattr(build, "REPORT", report)
    monkeypatch.setattr(build, "MANUSCRIPT", manuscript)
    source = (
        r"\graphicspath{{../artifacts/figures/}}"
        "\n"
        r"\includegraphics{positive_b_broad_four_slab}"
    )
    return report, source


def _isolated_d2_d3_figure_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, str]:
    report = tmp_path / "report"
    manuscript = report / "manuscript"
    figure_dir = report / "artifacts" / "figures"
    manuscript.mkdir(parents=True)
    figure_dir.mkdir(parents=True)
    figure = build.REPORT / "artifacts" / "figures" / "d2_d3_four_patch.pdf"
    metadata = figure.with_name("d2_d3_four_patch_metadata.json")
    shutil.copy2(figure, figure_dir / figure.name)
    shutil.copy2(metadata, figure_dir / metadata.name)
    payload = json.loads(metadata.read_text(encoding="utf-8"))

    def copy_pins(pins: dict[str, object]) -> None:
        for label, value in pins.items():
            if label.endswith("_sha256") or label == "claim_flags":
                continue
            expected = pins.get(f"{label}_sha256")
            if type(value) is dict and expected is None:
                copy_pins(value)
                continue
            assert isinstance(value, str)
            source_path = build.REPORT / value
            target = report / value
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(source_path, target)

    copy_pins(payload["source_pins"])
    monkeypatch.setattr(build, "REPORT", report)
    monkeypatch.setattr(build, "MANUSCRIPT", manuscript)
    source = r"\graphicspath{{../artifacts/figures/}}" "\n" r"\includegraphics{d2_d3_four_patch}"
    return report, source


def test_included_figures_close_metadata_and_source_pin_chain() -> None:
    source = build.TEX.read_text(encoding="utf-8")
    rows = build._figure_provenance(source)
    included = {
        match.removesuffix(".pdf")
        for match in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}", source)
    }
    assert {row["path"].rsplit("/", 1)[-1].removesuffix(".pdf") for row in rows} == included
    for row in rows:
        assert len(row["sha256"]) == 64
        assert len(row["metadata_sha256"]) == 64
        assert row["verified_source_pins"]
    comparison = next(row for row in rows if row["path"].endswith("d2_d3_four_patch.pdf"))
    roles = {pin["role"] for pin in comparison["verified_source_pins"]}
    assert {"d2.result", "d2.manifest", "d3.result", "d3.manifest"} <= roles


def test_compile_manifest_is_fail_closed_when_present() -> None:
    path = build.DATA / "manuscript_compile.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "tex_sha256" not in payload:
        return
    assert payload["release_eligible"] is False
    if payload.get("authority") == "ARCHIVED_HISTORICAL_WORKING_SET":
        assert payload["status"] == "PASS"
        assert payload["byte_identical_clean_rebuilds"] is True
        assert payload["tex_sha256"] == (
            "1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b"
        )
        assert payload["bibliography_sha256"] == (
            "f9564d51d9453e215ff3dc92744f325a7b3329603d99cfe06437963bd61b4fde"
        )
        assert payload["pdf_sha256"] == (
            "fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6"
        )
        assert payload["superseded_by"] == ("artifacts/data/theorem_first_working_compile.json")
        successor = build.DATA / "theorem_first_working_compile.json"
        assert successor.exists()
        successor_payload = json.loads(successor.read_text(encoding="utf-8"))
        assert successor_payload["status"] == ("PASS_INTERNAL_THEOREM_FIRST_WORKING_SET")
        assert successor_payload["release_eligible"] is False
        assert successor_payload["positive_budget_evaluated"] is False
        assert successor_payload["positive_budget_scientific_values_read"] is False
        return
    assert payload["tex_sha256"] == build._sha256(build.TEX)
    assert payload["bibliography_sha256"] == build._sha256(build.BIB)
    assert payload["numerical_input_sha256"] == build._sha256(build.NUMERICAL_INPUT)
    assert payload["positive_b_input_sha256"] == build._sha256(build.POSITIVE_B_INPUT)
    assert payload["build_driver_sha256"] == build._sha256(build.HERE)
    assert payload["numerical_input_builder_sha256"] == build._sha256(
        build.build_manuscript_inputs.HERE
    )
    assert payload["positive_b_input_builder_sha256"] == build._sha256(
        build.build_positive_b_manuscript_input.HERE
    )
    assert payload["positive_b_source_hashes"] == {
        "manifest": build.build_positive_b_manuscript_input.EXPECTED_MANIFEST_SHA256,
        "result": build.build_positive_b_manuscript_input.EXPECTED_RESULT_SHA256,
        "evidence": build.build_positive_b_manuscript_input.EXPECTED_EVIDENCE_SHA256,
        "audit": build.build_positive_b_manuscript_input.EXPECTED_AUDIT_SHA256,
    }
    assert payload["numerical_source_manifest"] == (
        "artifacts/data/manuscript_numerical_sources_manifest.json"
    )
    assert payload["numerical_source_manifest_sha256"] == (
        build.build_manuscript_inputs.EXPECTED_NUMERICAL_SOURCE_MANIFEST_SHA256
    )
    assert len(payload["verified_numerical_sources"]) == 38
    assert payload["publication_transaction"] == {
        "all_checks_before_publish": True,
        "preflight_before_canonical_writes": True,
        "published_outputs": [
            "manuscript/inputs/numerical_results.tex",
            "manuscript/inputs/positive_b_results.tex",
            "manuscript/encounter_multimodal_prr.pdf",
            "artifacts/logs/manuscript_tex.log",
            "artifacts/logs/manuscript_latexmk.log",
            "artifacts/data/manuscript_compile.json",
        ],
        "same_directory_atomic_replace_with_rollback": True,
        "temporary_source_snapshot": True,
    }
    assert payload["figure_inputs"] == build._figure_provenance(
        build.TEX.read_text(encoding="utf-8")
    )


def test_publication_transaction_replaces_the_complete_output_set(tmp_path: Path) -> None:
    targets = {
        tmp_path / "a.txt": tmp_path / "stage-a.txt",
        tmp_path / "b.txt": tmp_path / "stage-b.txt",
    }
    for index, (target, staged) in enumerate(targets.items()):
        target.write_text(f"old-{index}\n", encoding="utf-8")
        staged.write_text(f"new-{index}\n", encoding="utf-8")
    build._publish_transaction(targets)
    assert [path.read_text(encoding="utf-8") for path in targets] == ["new-0\n", "new-1\n"]


def test_publication_transaction_rolls_back_after_injected_replace_failure(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    third = tmp_path / "third.txt"
    first.write_bytes(b"trusted-first\n")
    second.write_bytes(b"trusted-second\n")
    staged = {}
    for index, target in enumerate((first, second, third), start=1):
        source = tmp_path / f"staged-{index}.txt"
        source.write_bytes(f"new-{index}\n".encode())
        staged[target] = source
    before = {first: first.read_bytes(), second: second.read_bytes()}
    calls = 0

    def fail_second_replace(source: os.PathLike[str] | str, target: os.PathLike[str] | str) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second replace failure")
        os.replace(source, target)

    with pytest.raises(OSError, match="injected second replace failure"):
        build._publish_transaction(staged, replace=fail_second_replace)
    assert first.read_bytes() == before[first]
    assert second.read_bytes() == before[second]
    assert not third.exists()
    assert not list(tmp_path.glob(".*.incoming.*"))
    assert not list(tmp_path.glob(".*.backup.*"))


def test_numerical_preflight_failure_precedes_all_canonical_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manuscript = tmp_path / "manuscript"
    data = tmp_path / "data"
    logs = tmp_path / "logs"
    manuscript.mkdir()
    data.mkdir()
    logs.mkdir()
    numerical = manuscript / "numerical.tex"
    positive_b = manuscript / "positive_b.tex"
    pdf = manuscript / "paper.pdf"
    tex_log = logs / "manuscript_tex.log"
    latexmk_log = logs / "manuscript_latexmk.log"
    compile_manifest = data / "manuscript_compile.json"
    targets = (numerical, positive_b, pdf, tex_log, latexmk_log, compile_manifest)
    for index, target in enumerate(targets):
        target.write_bytes(f"trusted-{index}\n".encode())
    before = {target: target.read_bytes() for target in targets}
    monkeypatch.setattr(build, "NUMERICAL_INPUT", numerical)
    monkeypatch.setattr(build, "POSITIVE_B_INPUT", positive_b)
    monkeypatch.setattr(build, "FINAL_PDF", pdf)
    monkeypatch.setattr(build, "LOGS", logs)
    monkeypatch.setattr(build, "DATA", data)

    def reject() -> dict[str, object]:
        raise RuntimeError("injected numerical provenance failure")

    monkeypatch.setattr(build.build_manuscript_inputs, "verify_numerical_sources", reject)
    with pytest.raises(RuntimeError, match="injected numerical provenance failure"):
        build.main()
    assert {target: target.read_bytes() for target in targets} == before


def test_duplicate_figure_metadata_key_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_positive_figure_tree(tmp_path, monkeypatch)
    metadata = report / "artifacts" / "figures" / "positive_b_broad_four_slab_metadata.json"
    raw = metadata.read_text(encoding="utf-8")
    metadata.write_text(raw.replace("{\n", '{\n  "schema_version": 1,\n', 1), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        build._figure_provenance(source)


def test_symlinked_figure_source_pin_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_positive_figure_tree(tmp_path, monkeypatch)
    metadata = json.loads(
        (report / "artifacts" / "figures" / "positive_b_broad_four_slab_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    pinned = report / metadata["source_pins"]["canonical_result"]
    ordinary = pinned.with_name(f"{pinned.name}.ordinary")
    pinned.replace(ordinary)
    pinned.symlink_to(ordinary.name)
    with pytest.raises(RuntimeError, match="ordinary nonsymlink"):
        build._figure_provenance(source)


def test_positive_publication_or_continuum_claim_flag_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_positive_figure_tree(tmp_path, monkeypatch)
    metadata = report / "artifacts" / "figures" / "positive_b_broad_four_slab_metadata.json"
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    payload["claim_flags"]["publication_gate_passed"] = True
    payload["claim_flags"]["continuum_interval_verified"] = True
    metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="claim flags changed"):
        build._figure_provenance(source)


def test_positive_figure_claim_scope_text_cannot_promote_the_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_positive_figure_tree(tmp_path, monkeypatch)
    metadata = report / "artifacts" / "figures" / "positive_b_broad_four_slab_metadata.json"
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    payload["claim_scope"] = (
        "continuum interval, unbounded-domain FV limit, and publication gate verified"
    )
    metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="claim scope changed"):
        build._figure_provenance(source)


def test_staging_uses_attested_figure_snapshot_during_verify_copy_restore_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_positive_figure_tree(tmp_path, monkeypatch)
    rows, snapshots = build._figure_provenance_with_snapshots(source)
    row = rows[0]
    snapshot = snapshots[row["path"]]
    live = report / row["path"]
    original = live.read_bytes()
    replacement = build.REPORT.parent / "does-not-matter.pdf"
    live.write_bytes(b"%PDF-1.4\n% attacker replacement\n")
    staged = tmp_path / "staged.pdf"
    build._write_staged_bytes(staged, snapshot.payload)
    live.write_bytes(original)
    assert build._sha256(staged) == row["sha256"]
    assert staged.read_bytes() == original
    assert not replacement.exists()


def test_nested_d3_positive_claim_flag_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_d2_d3_figure_tree(tmp_path, monkeypatch)
    metadata = report / "artifacts" / "figures" / "d2_d3_four_patch_metadata.json"
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    payload["source_pins"]["d3"]["claim_flags"]["physical_d3_verified"] = True
    metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="nested figure source claim"):
        build._figure_provenance(source)


def test_flat_and_nested_duplicate_source_role_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report, source = _isolated_d2_d3_figure_tree(tmp_path, monkeypatch)
    metadata = report / "artifacts" / "figures" / "d2_d3_four_patch_metadata.json"
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    payload["source_pins"]["d2.manifest"] = payload["source_pins"]["d2"]["manifest"]
    payload["source_pins"]["d2.manifest_sha256"] = payload["source_pins"]["d2"]["manifest_sha256"]
    metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="source-role set changed"):
        build._figure_provenance(source)
