"""Round-85 regressions for the two independent Round-84 provenance findings.

These tests never invoke either scientific entrypoint and never construct a
mesh above the already permitted seven-cell isolated algebra smoke.
"""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

import audit_positive_b_allocation_cusp_discovery_result as auditor
import positive_b_allocation_cusp_discovery as discovery
import pytest


def _manifest() -> dict[str, object]:
    return discovery.load_json(discovery.MANIFEST)


def test_v6_hash_contract_is_honest_and_keeps_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    reproducibility = manifest["reproducibility"]
    assert reproducibility["python_hash_mode"] == "isolated_randomized_per_process"
    assert reproducibility["python_ignore_environment_required"] is True
    assert reproducibility["python_hash_randomization_required"] is True
    assert reproducibility["unordered_boundary_rule"] == (
        "explicit_sort_before_numeric_or_serialized_use"
    )
    assert "PYTHONHASHSEED" not in reproducibility["subprocess_environment"]
    assert "PYTHONHASHSEED=0" not in discovery.PROTOCOL.read_text(encoding="utf-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    environment = discovery.subprocess_environment(manifest)
    assert "PYTHONHASHSEED" not in environment


def test_isolated_hashes_vary_but_set_derived_serialization_is_identical() -> None:
    site = discovery.repository_site_packages()
    code = Path(discovery.__file__).resolve().parent
    script = (
        "import sys; "
        f"sys.path.extend([{str(site)!r}, {str(code)!r}]); "
        "import positive_b_allocation_cusp_discovery as d; "
        "values={key:(key != 'm') for key in {'z','a','m'}}; "
        "print(sys.flags.ignore_environment,sys.flags.hash_randomization); "
        "print(hash('encounter')); "
        "print(d.canonical_json_bytes(d.sorted_bool_mapping(values)).decode(),end='')"
    )
    outputs: list[list[str]] = []
    for _index in range(3):
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-c", script],
            env={
                "HOME": os.environ["HOME"],
                "PATH": "/usr/bin:/bin",
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONHASHSEED": "0",
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "VECLIB_MAXIMUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
            },
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        outputs.append(completed.stdout.splitlines())
    assert all(rows[0] == "1 1" for rows in outputs)
    assert len({rows[1] for rows in outputs}) > 1
    assert len({"\n".join(rows[2:]) for rows in outputs}) == 1


def test_canonical_mapping_and_scientific_tie_breaks_ignore_insertion_order() -> None:
    first = {key: value for key, value in (("z", False), ("a", True), ("m", True))}
    second = {key: value for key, value in reversed(tuple(first.items()))}
    assert list(discovery.sorted_bool_mapping(first)) == ["a", "m", "z"]
    assert discovery.sorted_bool_mapping(first) == discovery.sorted_bool_mapping(second)
    assert discovery.canonical_json_bytes(first) == discovery.canonical_json_bytes(second)
    source = Path(discovery.__file__).read_text(encoding="utf-8")
    assert "for key, value in gates.items()" not in source
    assert "eligible.sort(" in source
    assert "passing.sort(" in source


def test_native_manifest_covers_exact_phases_and_external_homebrew_images() -> None:
    native = _manifest()["runtime_provenance"]["non_system_native"]
    assert native["contract"] == "bounded_non_system_macho_closure_v1"
    assert native["threat_boundary"] == (
        "reproducibility_witness_not_malicious_same_uid_prevention"
    )
    assert native["bootstrap_root_of_trust_includes_hash_primitive"] is True
    assert native["probe_induced_images_included"] == ["ctypes", "_ctypes"]
    assert set(native["phase_images"]) == set(discovery.NATIVE_IMAGE_PHASES)
    counts = [len(native["phase_images"][phase]) for phase in discovery.NATIVE_IMAGE_PHASES]
    assert counts == [13, 93, 94, 98]
    transition = native["phase_transition_causes"]["post_manifest_validation"]
    assert transition["operation"] == "signed_dyld_cache_provenance.platform.mac_ver"
    assert transition["added_images"] == [
        row
        for row in native["phase_images"]["post_manifest_validation"]
        if row not in native["phase_images"]["runner_post_import"]
    ]
    assert len(transition["added_images"]) == 1
    assert Path(transition["added_images"][0]["resolved_path"]).name.startswith("pyexpat.")
    assert native["closure_image_count"] == len(native["images"])
    resolved = {row["resolved_path"] for row in native["images"]}
    assert any("/openssl@3/" in path and path.endswith("/libcrypto.3.dylib") for path in resolved)
    assert any("/xz/" in path and path.endswith("/liblzma.5.dylib") for path in resolved)
    assert any("/mpdecimal/" in path and "libmpdec" in path for path in resolved)
    for row in native["images"]:
        assert row["lexical_paths"] == sorted(set(row["lexical_paths"]))
        assert os.path.realpath(row["resolved_path"]) == row["resolved_path"]
        assert row["size"] > 0
        assert len(row["sha256"]) == 64
        for dependency in row["dependencies"]:
            assert dependency["classification"] in {"non_system", "system_dyld_cache"}
            if dependency["classification"] == "non_system":
                assert dependency["resolved_path"] in resolved
            else:
                assert dependency["resolved_path"] is None


def test_producer_and_independent_auditor_rebuild_identical_native_witness() -> None:
    expected = _manifest()["runtime_provenance"]["non_system_native"]
    producer = discovery.bounded_non_system_native_provenance()
    independent = auditor.bounded_non_system_native_provenance()
    assert producer == expected
    assert independent == expected
    assert producer == independent


def test_native_witness_mutations_fail_both_reconstruction_paths() -> None:
    manifest = _manifest()
    changed = copy.deepcopy(manifest)
    changed["runtime_provenance"]["non_system_native"]["images"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="runtime_provenance"):
        discovery.validate_manifest(changed)
    assert (
        changed["runtime_provenance"]["non_system_native"]
        != auditor.current_runtime_provenance()["non_system_native"]
    )


def test_macho_token_resolution_is_closed_in_both_implementations(tmp_path: Path) -> None:
    executable = tmp_path / "app" / "python"
    loader = tmp_path / "pkg" / "module.so"
    libraries = tmp_path / "pkg" / "libs"
    executable.parent.mkdir()
    loader.parent.mkdir()
    libraries.mkdir()
    executable.write_bytes(b"executable")
    loader.write_bytes(b"loader")
    target = libraries / "libtarget.dylib"
    target.write_bytes(b"target")
    arguments = ("@rpath/libtarget.dylib", loader, executable, ["@loader_path/libs"])
    producer = discovery._resolve_macho_dependency(*arguments)
    independent = auditor._resolve_macho_dependency(*arguments)
    assert producer == independent == ("non_system", str(target), str(target.resolve()))
    system_arguments = ("/usr/lib/libSystem.B.dylib", loader, executable, [])
    assert discovery._resolve_macho_dependency(*system_arguments) == (
        "system_dyld_cache",
        "/usr/lib/libSystem.B.dylib",
        None,
    )
    assert auditor._resolve_macho_dependency(*system_arguments) == (
        "system_dyld_cache",
        "/usr/lib/libSystem.B.dylib",
        None,
    )


def test_protocol_embeds_native_verifier_and_exact_formal_bootstrap() -> None:
    protocol = discovery.PROTOCOL.read_text(encoding="utf-8")
    embedded = protocol.split("BOOTSTRAP='", 1)[1].split("'\nenv -i", 1)[0]
    assert embedded == discovery.ISOLATED_RUNNER_BOOTSTRAP
    assert "formal bootstrap pre-third-party native image set changed" in embedded
    assert "formal bootstrap native closure contains unreachable rows" in embedded
    assert '"$PY" -I -S -B -c "$BOOTSTRAP" "$RUNNER" "$SITE"' in protocol
    assert "PYTHONHASHSEED=0" not in protocol


def test_round85_finishes_result_blind() -> None:
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )
    assert all(
        not discovery.lexical_path_exists(path)
        for path in discovery.promotion_staging_paths(
            discovery.OUTPUT, discovery.REPRODUCIBILITY_OUTPUT
        )
    )
