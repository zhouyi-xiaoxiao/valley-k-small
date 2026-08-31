from __future__ import annotations

import json
import shutil
from pathlib import Path

import build_manuscript_inputs as build
import pytest


def _isolated_source_tree(tmp_path: Path) -> tuple[Path, Path]:
    report = tmp_path / "report"
    release = build.load_object(build.NUMERICAL_SOURCE_MANIFEST)
    manifest = report / "artifacts" / "data" / build.NUMERICAL_SOURCE_MANIFEST.name
    manifest.parent.mkdir(parents=True)
    shutil.copy2(build.NUMERICAL_SOURCE_MANIFEST, manifest)
    copied: set[str] = set()
    for family in release["families"].values():
        for pin in family.values():
            relative = pin["path"]
            if relative in copied:
                continue
            copied.add(relative)
            target = report / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(build.REPORT / relative, target)
    return report, manifest


def _rewrite_json(path: Path, mutate: object) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert callable(mutate)
    mutate(payload)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_release(manifest: Path, release: dict[str, object]) -> str:
    manifest.write_text(
        json.dumps(release, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return build.sha256(manifest)


def _repin_family_result(
    report: Path,
    manifest: Path,
    family: str,
    mutate: object,
) -> str:
    release = build.load_object(manifest)
    result = report / release["families"][family]["result"]["path"]
    _rewrite_json(result, mutate)
    release["families"][family]["result"]["sha256"] = build.sha256(result)
    return _write_release(manifest, release)


def test_generated_macros_are_claim_gated_and_traceable() -> None:
    source = build.render_macros()
    for name in (
        "FourPatchCuspTime",
        "FourPatchSelectedWeights",
        "FourPatchValleyTwo",
        "DThreeCuspTime",
        "DThreeSelectedWeights",
        "DThreeValleyTwo",
        "DThreeRootDifference",
        "DThreeEligibleCount",
        "GOneCSeedCount",
        "GOneDFoldTime",
        "GOneDJacobianDeterminant",
        "BroadBZeroSelectedStep",
        "BroadBZeroCuspTime",
        "BroadBZeroSelectedWeights",
        "BroadBZeroFinestRootError",
    ):
        assert rf"\providecommand{{\{name}}}" in source
    for path in (
        build.FOUR_PATCH,
        build.FOUR_PATCH_D3,
        build.G1C,
        build.G1D,
        build.BROAD_B0,
    ):
        assert build.sha256(path) in source
    assert "13.3280319895" in source
    assert "0.83754" in source
    assert "10.5022583145" in source
    assert "12.8097399605" in source
    assert "0.84480" in source
    assert "0.06685" in source


def test_release_manifest_closes_all_five_numerical_families() -> None:
    verified = build.verify_numerical_sources()
    assert set(verified["families"]) == {"d2", "d3", "g1c", "g1d", "broad_b0"}
    assert len(verified["verified_files"]) == 38
    assert verified["manifest_sha256"] in build.render_macros()


@pytest.mark.parametrize(
    ("relative", "suffix"),
    (
        ("artifacts/data/continuum_observable_four_patch_result.json", b" "),
        ("artifacts/data/continuum_broad_patch_b0_bridge_result.json", b" "),
        ("code/continuum_broad_patch_b0_bridge.py", b"\n# isolated mutation\n"),
        ("code/continuum_weak_budget_design.py", b"\n# isolated mutation\n"),
    ),
)
def test_release_manifest_rejects_result_producer_and_dependency_mutations(
    tmp_path: Path,
    relative: str,
    suffix: bytes,
) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    target = report / relative
    target.write_bytes(target.read_bytes() + suffix)
    with pytest.raises(RuntimeError, match="hash mismatch"):
        build.verify_numerical_sources(report=report, manifest_path=manifest)


def test_g1d_nested_pin_rejects_a_repinned_mutated_g1c_result(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    g1c = report / "artifacts/data/continuum_g1c_simplex_result.json"
    _rewrite_json(g1c, lambda payload: payload["controls"].pop())
    changed_hash = build.sha256(g1c)
    release = build.load_object(manifest)
    release["families"]["g1c"]["result"]["sha256"] = changed_hash
    release["families"]["g1d"]["g1c_result_dependency"]["sha256"] = changed_hash
    manifest.write_text(
        json.dumps(release, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="G1d-to-G1c nested result hash"):
        build.verify_numerical_sources(
            report=report,
            manifest_path=manifest,
            expected_manifest_sha256=build.sha256(manifest),
        )


def test_duplicate_manifest_key_is_rejected_before_pin_use(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    raw = manifest.read_text(encoding="utf-8")
    manifest.write_text(raw.replace("{\n", '{\n  "schema_version": 1,\n', 1), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        build.verify_numerical_sources(
            report=report,
            manifest_path=manifest,
            expected_manifest_sha256=build.sha256(manifest),
        )


def test_duplicate_result_key_is_rejected_after_release_repin(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    release = build.load_object(manifest)
    result = report / release["families"]["d2"]["result"]["path"]
    raw = result.read_text(encoding="utf-8")
    result.write_text(raw.replace("{\n", '{\n  "schema_version": 1,\n', 1), encoding="utf-8")
    release["families"]["d2"]["result"]["sha256"] = build.sha256(result)
    expected = _write_release(manifest, release)
    with pytest.raises(ValueError, match="duplicate JSON key"):
        build.verify_numerical_sources(
            report=report, manifest_path=manifest, expected_manifest_sha256=expected
        )


def test_nonfinite_result_number_is_rejected_after_release_repin(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    release = build.load_object(manifest)
    result = report / release["families"]["d2"]["result"]["path"]
    _rewrite_json(result, lambda payload: payload["cusp"].__setitem__("time", float("nan")))
    release["families"]["d2"]["result"]["sha256"] = build.sha256(result)
    expected = _write_release(manifest, release)
    with pytest.raises(ValueError, match="nonfinite"):
        build.verify_numerical_sources(
            report=report, manifest_path=manifest, expected_manifest_sha256=expected
        )


def test_symlinked_result_is_rejected_even_when_target_bytes_match(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    release = build.load_object(manifest)
    result = report / release["families"]["d2"]["result"]["path"]
    backup = result.with_name(f"{result.name}.ordinary")
    result.replace(backup)
    result.symlink_to(backup.name)
    with pytest.raises(RuntimeError, match="ordinary nonsymlink"):
        build.verify_numerical_sources(report=report, manifest_path=manifest)


def test_release_manifest_rejects_schema_aliases_scope_aliases_and_extra_roles(
    tmp_path: Path,
) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    release = build.load_object(manifest)
    release["schema_version"] = True
    for family in release["release_scope_flags"].values():
        for key, value in list(family.items()):
            if type(value) is bool:
                family[key] = int(value)
    release["families"]["d2"]["extra_role"] = dict(
        release["families"]["d2"]["result"]
    )
    expected = _write_release(manifest, release)
    with pytest.raises(RuntimeError, match="schema or status|scope flags|incomplete"):
        build.verify_numerical_sources(
            report=report, manifest_path=manifest, expected_manifest_sha256=expected
        )


def test_g1d_boolean_integer_aliases_are_rejected_after_full_result_repin(
    tmp_path: Path,
) -> None:
    report, manifest = _isolated_source_tree(tmp_path)

    def mutate(result: dict[str, object]) -> None:
        result["finite_B_Doi_fold"] = 1
        result["finite_grid_fold_confirmed"] = 1
        result["continuum_verified"] = 0
        result["project_gate_passed"] = 0

    expected = _repin_family_result(report, manifest, "g1d", mutate)
    with pytest.raises(RuntimeError, match="G1d result identity or claim boundary changed"):
        build.verify_numerical_sources(
            report=report, manifest_path=manifest, expected_manifest_sha256=expected
        )


def test_broad_bridge_scope_and_limitations_cannot_be_promoted_after_repin(
    tmp_path: Path,
) -> None:
    report, manifest = _isolated_source_tree(tmp_path)

    def mutate(result: dict[str, object]) -> None:
        result["claim_scope"] = "continuum and publication ready"
        result["limitations"] = ["publication ready"]

    expected = _repin_family_result(report, manifest, "broad_b0", mutate)
    with pytest.raises(RuntimeError, match="broad B0 result identity or claim boundary changed"):
        build.verify_numerical_sources(
            report=report, manifest_path=manifest, expected_manifest_sha256=expected
        )


def test_nested_g1c_continuum_promotion_is_rejected_recursively() -> None:
    result = build.load_object(build.G1C)
    result["controls"][0]["continuum_verified"] = True
    with pytest.raises(RuntimeError, match="promotes dangerous claim key continuum_verified"):
        build._validate_family_result("g1c", result)


def test_verified_renderer_uses_snapshot_objects_not_later_path_bytes(tmp_path: Path) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    verified = build.verify_numerical_sources(report=report, manifest_path=manifest)
    release = build.load_object(manifest)
    result = report / release["families"]["d2"]["result"]["path"]
    _rewrite_json(result, lambda payload: payload["cusp"].__setitem__("time", 99.123456789))
    rendered = build.render_verified_macros(verified)
    assert r"\providecommand{\FourPatchCuspTime}{13.3280319895}" in rendered
    assert "99.123456789" not in rendered
    assert verified["families"]["d2"]["result"]["sha256"] in rendered


def test_verified_renderer_rehashes_snapshot_payload_instead_of_trusting_its_field(
    tmp_path: Path,
) -> None:
    report, manifest = _isolated_source_tree(tmp_path)
    verified = build.verify_numerical_sources(report=report, manifest_path=manifest)
    relative = verified["families"]["d2"]["result"]["path"]
    original = verified["snapshots"][relative]
    attacker = json.loads(original.payload)
    attacker["cusp"]["time"] = 99.123456789
    attacker_payload = json.dumps(attacker, sort_keys=True, allow_nan=False).encode()
    verified["snapshots"][relative] = build.FileSnapshot(
        path=original.path,
        sha256=original.sha256,
        payload=attacker_payload,
    )
    with pytest.raises(RuntimeError, match="snapshot identity changed"):
        build.render_verified_macros(verified)


def test_failed_preflight_does_not_overwrite_requested_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "numerical_results.tex"
    output.write_bytes(b"trusted-old-output\n")
    before = output.read_bytes()

    def reject(**_kwargs: object) -> dict[str, object]:
        raise RuntimeError("injected preflight failure")

    monkeypatch.setattr(build, "verify_numerical_sources", reject)
    with pytest.raises(RuntimeError, match="injected preflight failure"):
        build.main(("--output", str(output)))
    assert output.read_bytes() == before


def test_scientific_notation_is_valid_tex() -> None:
    assert build.tex_sci(1.0989e-12) == r"1.10\times10^{-12}"
    assert build.tex_sci(-2.8439e-15) == r"-2.84\times10^{-15}"
