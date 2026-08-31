from __future__ import annotations

import json
import os
from pathlib import Path

import compile_theorem_first_working as build
import pytest


def test_paths_are_driver_relative_and_source_allowlist_is_closed() -> None:
    assert build.REPORT == build.HERE.parents[1]
    assert build.RELEASE_ELIGIBLE is False
    assert set(build._required_source_paths()) == {
        "manuscript/encounter_multimodal_prr_theorem_first_working.tex",
        "manuscript/encounter_multimodal_prr_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/references.bib",
        "code/compile_theorem_first_working.py",
    }
    assert all(
        "positive_b" not in relative and "numerical" not in relative
        for relative in build._required_source_paths()
    )
    supplement = build.SUPPLEMENT_TEX.read_text(encoding="utf-8")
    main = build.MAIN_TEX.read_text(encoding="utf-8")
    assert supplement.count(r"\input{exact_m_theorem_full_proof.tex}") == 1
    assert main.count(r"\input{exact_m_theorem_spine.tex}") == 1


def test_missing_full_proof_fails_before_any_canonical_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "exact_m_theorem_full_proof.tex"
    monkeypatch.setattr(build, "EXACT_M_FULL_PROOF_TEX", missing)

    targets = {
        "FINAL_MAIN_PDF": tmp_path / "canonical-main.pdf",
        "FINAL_SUPPLEMENT_PDF": tmp_path / "canonical-supplement.pdf",
        "MAIN_TEX_LOG": tmp_path / "canonical-main-tex.log",
        "MAIN_LATEXMK_LOG": tmp_path / "canonical-main-latexmk.log",
        "SUPPLEMENT_TEX_LOG": tmp_path / "canonical-supplement-tex.log",
        "SUPPLEMENT_LATEXMK_LOG": tmp_path / "canonical-supplement-latexmk.log",
        "MANIFEST": tmp_path / "canonical-manifest.json",
    }
    for index, (name, path) in enumerate(targets.items()):
        path.write_bytes(f"trusted-{index}\n".encode())
        monkeypatch.setattr(build, name, path)
    before = {path: path.read_bytes() for path in targets.values()}

    with pytest.raises(FileNotFoundError, match="exact_m_theorem_full_proof"):
        build._build_and_publish()
    assert {path: path.read_bytes() for path in targets.values()} == before


def test_manifest_freshness_detects_source_and_output_changes(tmp_path: Path) -> None:
    source = tmp_path / "source.tex"
    driver = tmp_path / "driver.py"
    output = tmp_path / "paper.pdf"
    source.write_bytes(b"source-v1\n")
    driver.write_bytes(b"driver-v1\n")
    output.write_bytes(b"output-v1\n")
    sources = {
        "manuscript/source.tex": source,
        "code/compile_theorem_first_working.py": driver,
    }
    outputs = {"output/pdf/paper.pdf": output}
    payload = {
        "build": {"driver_sha256": build._sha256(driver)},
        "inputs": {relative: build._sha256(path) for relative, path in sources.items()},
        "published_files": {relative: build._sha256(path) for relative, path in outputs.items()},
        "release_eligible": False,
    }
    assert not build._manifest_freshness_errors(
        payload,
        source_paths=sources,
        published_paths=outputs,
    )

    source.write_bytes(b"source-v2\n")
    output.write_bytes(b"output-v2\n")
    errors = build._manifest_freshness_errors(
        payload,
        source_paths=sources,
        published_paths=outputs,
    )
    assert "input hash mismatch: manuscript/source.tex" in errors
    assert "published output hash mismatch: output/pdf/paper.pdf" in errors


def test_manifest_freshness_rejects_release_eligible_true(tmp_path: Path) -> None:
    driver = tmp_path / "driver.py"
    driver.write_bytes(b"driver\n")
    sources = {"code/compile_theorem_first_working.py": driver}
    payload = {
        "build": {"driver_sha256": build._sha256(driver)},
        "inputs": {"code/compile_theorem_first_working.py": build._sha256(driver)},
        "published_files": {},
        "release_eligible": True,
    }
    errors = build._manifest_freshness_errors(
        payload,
        source_paths=sources,
        published_paths={},
    )
    assert "release_eligible is not fail-closed false" in errors


def test_current_new_driver_manifest_is_fresh_when_present() -> None:
    if not build.MANIFEST.exists():
        pytest.skip("theorem-first compile manifest has not been published")
    payload = json.loads(build.MANIFEST.read_text(encoding="utf-8"))
    if payload.get("build", {}).get("driver") != "code/compile_theorem_first_working.py":
        pytest.skip("manifest predates the dedicated theorem-first build driver")
    assert not build._manifest_freshness_errors(payload)


def test_publication_transaction_replaces_complete_set(tmp_path: Path) -> None:
    staged_outputs: dict[Path, Path] = {}
    for index, name in enumerate(("first", "second"), start=1):
        target = tmp_path / f"{name}.txt"
        staged = tmp_path / f"staged-{name}.txt"
        target.write_bytes(f"trusted-{index}\n".encode())
        staged.write_bytes(f"new-{index}\n".encode())
        staged_outputs[target] = staged
    build._publish_transaction(staged_outputs)
    assert [path.read_bytes() for path in staged_outputs] == [b"new-1\n", b"new-2\n"]


def test_publication_failure_restores_every_canonical_output(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    absent = tmp_path / "previously-absent.txt"
    first.write_bytes(b"trusted-first\n")
    second.write_bytes(b"trusted-second\n")
    staged_outputs: dict[Path, Path] = {}
    for index, target in enumerate((first, second, absent), start=1):
        staged = tmp_path / f"staged-{index}.txt"
        staged.write_bytes(f"new-{index}\n".encode())
        staged_outputs[target] = staged
    before = {first: first.read_bytes(), second: second.read_bytes()}
    calls = 0

    def fail_second_replace(
        source: os.PathLike[str] | str,
        target: os.PathLike[str] | str,
    ) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected second replace failure")
        os.replace(source, target)

    with pytest.raises(OSError, match="injected second replace failure"):
        build._publish_transaction(staged_outputs, replace=fail_second_replace)
    assert first.read_bytes() == before[first]
    assert second.read_bytes() == before[second]
    assert not absent.exists()
    assert not list(tmp_path.glob(".*.incoming.*"))
    assert not list(tmp_path.glob(".*.backup.*"))


def test_published_log_normalization_removes_wrapped_random_temp_roots() -> None:
    root_a = Path("/var/folders/example/T/theorem-first-working-abcdefgh")
    root_b = Path("/var/folders/example/T/theorem-first-working-ijklmnop")

    def wrapped_payload(root: Path) -> bytes:
        raw = str(root).encode()
        basename = root.name.encode()
        return (
            b"open "
            + raw[:-1]
            + b"\n"
            + raw[-1:]
            + b"/main-1/source.tex\nrelative "
            + basename[:-1]
            + b"\n"
            + basename[-1:]
            + b"/main-2/output.pdf\n"
        )

    bundle_a = build._normalized_log_bundle(
        wrapped_payload(root_a),
        wrapped_payload(root_a),
        temporary_root=root_a,
    )
    bundle_b = build._normalized_log_bundle(
        wrapped_payload(root_b),
        wrapped_payload(root_b),
        temporary_root=root_b,
    )
    assert bundle_a == bundle_b
    assert bundle_a.count(b"<TEMP_BUILD_ROOT>") == 4
    assert b"theorem-first-working-" not in bundle_a


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"LaTeX Warning: Reference `missing' undefined.\n", "undefined reference"),
        (b"LaTeX Warning: Citation `missing' undefined.\n", "undefined citation"),
        (b"Overfull \\hbox (1.0pt too wide)\n", "overfull box"),
        (b"! Missing $ inserted.\n", "TeX error"),
    ],
)
def test_tex_log_gate_rejects_submission_defects(payload: bytes, message: str) -> None:
    with pytest.raises(RuntimeError, match=message):
        build._audit_tex_log(payload, label="test log")


def test_tex_log_gate_does_not_promote_underfull_box_to_failure() -> None:
    build._audit_tex_log(b"Underfull \\hbox (badness 1000)\n", label="test log")
