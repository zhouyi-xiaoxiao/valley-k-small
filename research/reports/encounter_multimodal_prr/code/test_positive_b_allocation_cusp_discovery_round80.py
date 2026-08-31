"""Round-80 attacks retained as ordinary regressions for the v6 repair.

This module never invokes either scientific entrypoint, never constructs a
mesh above seven cells, and never opens a scientific result.
"""

from __future__ import annotations

import copy
import os
import py_compile
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Callable

import audit_positive_b_allocation_cusp_discovery_result as auditor
import numpy as np
import positive_b_allocation_cusp_discovery as discovery
import pytest
import test_audit_positive_b_allocation_cusp_discovery_result as auditor_tests
import test_positive_b_allocation_cusp_discovery as discovery_tests
import test_positive_b_allocation_cusp_discovery_round74 as round74

EXPECTED_MANIFEST_SHA256 = auditor.EXPECTED_MANIFEST_SHA256


def _manifest_hash_pins() -> tuple[dict[str, Any], str, dict[str, str]]:
    manifest = discovery.load_json(discovery.MANIFEST)
    manifest_hash = discovery.sha256(discovery.MANIFEST)
    pins = {role: row["sha256"] for role, row in manifest["pinned_files"].items()}
    return manifest, manifest_hash, pins


def _producer_accepts(result: dict[str, Any], manifest_hash: str, pins: dict[str, str]) -> bool:
    try:
        discovery.validate_result_contract(result, manifest_hash, pins)
    except RuntimeError:
        return False
    return True


def _auditor_accepts(manifest: dict[str, Any], result: dict[str, Any]) -> bool:
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = auditor_tests._evidence(manifest, result, result_bytes)
    evidence_bytes = auditor.canonical_json_bytes(evidence)
    return bool(
        auditor.audit_payload(manifest, result, evidence, result_bytes, evidence_bytes)[
            "audit_integrity_passed"
        ]
    )


def _control_acceptance(
    control: dict[str, Any], manifest: dict[str, Any], cells: int = 65
) -> tuple[bool, bool]:
    return (
        discovery.validate_control_contract(control, cells),
        auditor.reconstruct_control(control, manifest),
    )


def test_round80_starts_result_blind_and_rehashes_every_direct_pin() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    assert manifest_hash == EXPECTED_MANIFEST_SHA256 == auditor.EXPECTED_MANIFEST_SHA256
    assert len(pins) == 27
    assert len({row["path"] for row in manifest["pinned_files"].values()}) == 27
    for role, row in manifest["pinned_files"].items():
        assert discovery.sha256(discovery.REPORT / row["path"]) == pins[role]
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )


def test_round74_absurd_factor_attack_is_closed_in_both_paths() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    control = auditor_tests._passing_control(manifest)
    factors = control["model_diagnostics"]["factor_diagnostics"]
    factors["spacings"] = {
        "midpoint": 9.0,
        "relative_parallel": 9.0,
        "relative_perp": 9.0,
    }
    factors["patch_integrals"] = [2.0, 2.0, 2.0, 2.0]
    factors["midpoint_initial_mass"] = 2.0
    factors["relative_initial_mass"] = 3.0
    factors["contact_area"] = 4.0
    for key in (
        "maximum_patch_quadrature_error_estimate",
        "maximum_initial_quadrature_error_estimate",
        "contact_area_error_estimate",
        "midpoint_generator_row_error",
        "relative_generator_row_error",
    ):
        factors[key] = 1.0e200
    assert _control_acceptance(control, manifest) == (False, False)


def test_round74_scan_root_flags_reasons_duplicates_and_separation_are_closed() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    base = auditor_tests._passing_control(manifest, maximum_count=2)

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value["stationary_scan"].__setitem__("spacing", 1.0),
        lambda value: value["stationary_scan"].__setitem__("grid_point_count", 690),
        lambda value: value["stationary_scan"].__setitem__(
            "endpoint_first_derivatives_per_budget", [-1.0, 1.0]
        ),
        lambda value: value["roots"][0].__setitem__("type", "minimum"),
        lambda value: value["roots"][0].__setitem__("density_eligible", False),
        lambda value: value["roots"][0]["eligibility_reasons"].append("forged_reason"),
    ]
    for mutate in mutations:
        changed = copy.deepcopy(base)
        mutate(changed)
        assert _control_acceptance(changed, manifest) == (False, False)

    duplicate = copy.deepcopy(base["all_bracketed_roots"])
    duplicate[1]["time"] = duplicate[0]["time"] + 1.0e-9
    assert discovery.reconstruct_root_semantics(duplicate, 1.0) is False
    assert auditor.reconstruct_root_semantics(duplicate, 1.0, manifest) is False

    unseparated = copy.deepcopy(base["all_bracketed_roots"])
    unseparated[1]["time"] = unseparated[0]["time"] + 0.10
    assert discovery.reconstruct_root_semantics(unseparated, 1.0) is False
    assert auditor.reconstruct_root_semantics(unseparated, 1.0, manifest) is False


def test_round74_mesh97_phase_crosslink_and_honest_nonzero_centre_are_closed() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    result = copy.deepcopy(auditor_tests._passing_result(manifest))
    round74._phase_with_shifted_centre(result, np.asarray((2.0**-8, -(2.0**-8))))
    assert (_producer_accepts(result, manifest_hash, pins), _auditor_accepts(manifest, result)) == (
        False,
        False,
    )

    centre = np.asarray((0.01, -0.01))
    generated = discovery.candidate_controls(centre)
    missing = [row["candidate_index"] for row in generated if row["eligible_geometry"]]
    phase = {
        "phase_centre_theta": centre.tolist(),
        "candidate_generation": generated,
        "screened_mesh_65": [
            {
                **row,
                "mesh_65": None,
                "mesh_65_evaluation_status": (
                    "HOLD_CONTROL_EVALUATION"
                    if row["eligible_geometry"]
                    else "NOT_ELIGIBLE_GEOMETRY"
                ),
            }
            for row in generated
        ],
        "advanced_mesh_97": [],
        "representatives": {"1": None, "2": None, "3": None},
        "all_three_regions_found": False,
        "phase_complete": False,
        "hold_reasons": [f"missing_eligible_mesh_65_evaluations:{missing}"],
        "search_expanded": False,
    }
    assert discovery.validate_phase_contract(phase, centre.tolist()) is True
    assert auditor.reconstruct_phase(phase, manifest, centre.tolist()) == (True, False)
    forged = copy.deepcopy(phase)
    forged["phase_centre_theta"] = [0.0, 0.0]
    assert discovery.validate_phase_contract(forged, centre.tolist()) is False
    assert auditor.reconstruct_phase(forged, manifest, centre.tolist()) == (False, False)


def test_exact_native_bool_int_float_aliases_fail_closed() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("schema_version", True),
        lambda value: value["small_explicit_csr_preflight"].__setitem__("mesh", [7.0, 7.0, 7.0]),
        lambda value: value["small_explicit_csr_preflight"].__setitem__("state_count", 343.0),
        lambda value: value["small_explicit_csr_preflight"].__setitem__("passed", 0),
        lambda value: value.__setitem__("all_discovery_gates_passed", 0),
    ]
    for mutate in mutations:
        hold = discovery_tests.valid_preflight_hold_payload(manifest_hash, pins)
        mutate(hold)
        assert (_producer_accepts(hold, manifest_hash, pins), _auditor_accepts(manifest, hold)) == (
            False,
            False,
        )

    control = auditor_tests._passing_control(manifest)
    control["roots"][0]["bracket_index"] = False
    assert _control_acceptance(control, manifest) == (False, False)
    control = auditor_tests._passing_control(manifest)
    control["roots"][0]["time"] = 2
    assert _control_acceptance(control, manifest) == (False, False)


def test_direct_runtime_source_pin_and_snapshot_are_closed() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    runtime = manifest["pinned_files"]["continuum_runtime_dependency"]
    assert runtime["path"] == "code/continuum_observable_four_patch.py"
    assert discovery.sha256(discovery.REPORT / runtime["path"]) == runtime["sha256"]
    metadata, payloads = discovery.capture_complete_freeze_snapshot(discovery.MANIFEST, manifest)
    assert metadata["continuum_runtime_dependency"]["sha256"] == runtime["sha256"]
    changed = dict(payloads)
    changed["continuum_runtime_dependency"] += b"\n# round80 drift"
    with pytest.raises(RuntimeError, match="snapshot changed"):
        discovery.require_same_freeze_snapshot(metadata, payloads, metadata, changed)


def test_runtime_dependency_order_and_preloaded_sys_modules_fail_closed() -> None:
    assert discovery.RUNTIME_MODULE_PINS == (
        ("continuum_g1_smoke", "grid_dependency"),
        ("continuum_observable_four_patch", "continuum_runtime_dependency"),
        ("continuum_weak_budget_design", "finite_volume_dependency"),
        ("continuum_broad_patch_b0_bridge", "B0_bridge_producer"),
    )
    module_names = [name for name, _role in discovery.RUNTIME_MODULE_PINS]
    saved_bridge = discovery._BRIDGE_MODULE
    saved_bound = discovery._BOUND_RUNTIME_MODULES
    saved_modules = {name: sys.modules.get(name) for name in module_names}
    try:
        discovery._BRIDGE_MODULE = None
        discovery._BOUND_RUNTIME_MODULES = {}
        for name in module_names:
            sys.modules.pop(name, None)
        sys.modules[module_names[0]] = types.ModuleType(module_names[0])
        with pytest.raises(RuntimeError, match="preloaded runtime module is forbidden"):
            discovery.bridge_module()
    finally:
        for name in module_names:
            sys.modules.pop(name, None)
            if saved_modules[name] is not None:
                sys.modules[name] = saved_modules[name]
        discovery._BOUND_RUNTIME_MODULES = saved_bound
        discovery._BRIDGE_MODULE = saved_bridge
    module_names = [name for name, _role in discovery.RUNTIME_MODULE_PINS]
    code_directory = Path(discovery.__file__).resolve().parent
    site_packages = discovery.repository_site_packages()
    script = (
        "import sys; "
        f"sys.path.append({str(site_packages)!r}); "
        f"sys.path.insert(0, {str(code_directory)!r}); "
        "import positive_b_allocation_cusp_stage_a; "
        f"print([name for name in {module_names!r} if name in sys.modules])"
    )
    completed = subprocess.run(
        [sys.executable, "-I", "-S", "-B", "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "[]"


@pytest.mark.parametrize("staging_role", ("canonical", "evidence"))
def test_preexisting_promotion_stage_aborts_before_zero_replica_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, staging_role: str
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"
    stages = discovery.promotion_staging_paths(canonical, evidence)
    stage = stages[0 if staging_role == "canonical" else 1]
    stage.write_bytes(b"foreign stage\n")
    calls = 0

    def fake_run(_command: list[str], **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        return type("Completed", (), {"returncode": 2})()

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="staging boundary"):
        discovery.run_replica_commands(
            (("replica-one",), ("replica-two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            canonical,
            evidence,
        )
    assert calls == 0
    assert stage.read_bytes() == b"foreign stage\n"


def test_no_cycle_and_scientific_output_collision_helpers_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = Path(auditor.__file__).read_text(encoding="utf-8")
    assert "import positive_b_allocation_cusp_discovery" not in source
    assert "from positive_b_allocation_cusp_discovery" not in source
    assert auditor.EXPECTED_MANIFEST_SHA256 == EXPECTED_MANIFEST_SHA256

    paths = tuple(tmp_path / f"science-{index}.json" for index in range(5))
    paths[2].write_bytes(b"declared replica\n")
    paths[0].write_bytes(b"foreign canonical collision\n")
    monkeypatch.setattr(discovery, "scientific_output_paths", lambda: paths)
    with pytest.raises(RuntimeError, match="path boundary changed"):
        discovery.require_exact_present_science_paths([paths[2]])
    assert paths[0].read_bytes() == b"foreign canonical collision\n"


def test_preexisting_canonical_collision_aborts_before_zero_replica_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"
    canonical.write_bytes(b"foreign canonical\n")
    calls = 0

    def fake_run(_command: list[str], **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        return type("Completed", (), {"returncode": 2})()

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="must be lexically absent"):
        discovery.run_replica_commands(
            (("replica-one",), ("replica-two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            canonical,
            evidence,
        )
    assert calls == 0
    assert canonical.read_bytes() == b"foreign canonical\n"


def test_outer_model_diagnostics_must_reject_absurd_killing_trace_and_negative_error() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    control = auditor_tests._passing_control(manifest)
    diagnostics = control["model_diagnostics"]
    diagnostics["minimum_killing_per_budget"] = -1.0e200
    diagnostics["maximum_killing_per_budget"] = 1.0e200
    diagnostics["analytic_column_operator_trace"] = 1.0e200
    diagnostics["generator_killing_identity_error"] = -1.0e200
    assert _control_acceptance(control, manifest) == (False, False)


def test_full_scan_reference_maximum_and_saved_trace_cardinality_must_be_exact() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    control = auditor_tests._passing_control(manifest)
    scan = control["stationary_scan"]
    expected_saved_count = (
        int(
            round(
                (scan["time_window"][1] - scan["time_window"][0])
                / manifest["root_search"]["saved_trace_spacing"]
            )
        )
        + 1
    )
    assert expected_saved_count == 70
    assert len(scan["saved_trace"]) == 70
    scan["reference_maximum_density_per_budget"] = 1.0e7
    assert _control_acceptance(control, manifest) == (False, False)


def test_root_residual_and_scan_errors_must_be_nonnegative() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    control = auditor_tests._passing_control(manifest)
    control["roots"][0]["scaled_root_residual"] = -1.0e200
    assert _control_acceptance(control, manifest) == (False, False)

    control = auditor_tests._passing_control(manifest)
    for row in control["stationary_scan"]["full_scan_trace"]:
        row["differential_mass_balance_error"] = -1.0e200
    for row in control["stationary_scan"]["saved_trace"]:
        row["differential_mass_balance_error"] = -1.0e200
    control["stationary_scan"]["maximum_sampled_differential_mass_balance_error"] = -1.0e200
    assert _control_acceptance(control, manifest) == (False, False)


def test_negative_cusp_fold_tail_comparison_and_preflight_norms_fail_closed() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    cusp, cusp_diagnostics = auditor_tests._cusp(65, manifest)
    cusp_diagnostics["maximum_dimensionless_residual"] = -1.0
    assert (
        discovery.validate_cusp_diagnostics_contract(
            cusp_diagnostics,
            65,
            cusp,
            cusp_diagnostics["model_diagnostics"],
        )
        is False
    )
    assert (
        auditor.reconstruct_cusp_diagnostics(
            cusp_diagnostics,
            cusp,
            cusp_diagnostics["model_diagnostics"],
            65,
            manifest,
        )
        is False
    )

    fold = auditor_tests._fold_node(65, 0, 12.0)
    fold["normalized_fold_residual"] = -1.0
    assert discovery.validate_fold_node_contract(fold, 65) is False
    assert auditor.validate_fold_node(fold, 65, manifest) is False

    comparison = auditor_tests._fold_node(65, 0, 12.0)
    comparison.update(
        {
            "signed_time_offset": 1.0,
            "target_signed_time_offset": 1.0,
            "absolute_time_offset_mismatch": -1.0,
        }
    )
    assert discovery.validate_fold_node_contract(comparison, 65, comparison=True) is False
    assert auditor.validate_fold_node(comparison, 65, manifest, comparison=True) is False

    control = auditor_tests._passing_control(manifest)
    control["tail_trace"][0]["differential_mass_balance_error"] = -1.0
    control["tail_trace"][0]["survival_density_identity_error"] = -1.0
    assert _control_acceptance(control, manifest) == (False, False)

    result = discovery_tests.valid_preflight_hold_payload(manifest_hash, pins)
    result["small_explicit_csr_preflight"]["errors"]["column_action"] = -1.0
    assert (_producer_accepts(result, manifest_hash, pins), _auditor_accepts(manifest, result)) == (
        False,
        False,
    )


def test_formal_subprocess_environment_must_not_allow_import_substitution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    sitecustomize = tmp_path / "sitecustomize.py"
    sitecustomize.write_text(
        "import sys, types\n"
        "fake = types.ModuleType('continuum_broad_patch_b0_bridge')\n"
        "fake.ROUND80_UNPINNED_IMPORT = True\n"
        "sys.modules['continuum_broad_patch_b0_bridge'] = fake\n",
        encoding="utf-8",
    )
    hostile_pythonpath = os.pathsep.join(
        (str(tmp_path), str(Path(discovery.__file__).resolve().parent))
    )
    monkeypatch.setenv("PYTHONPATH", hostile_pythonpath)
    monkeypatch.setenv("DYLD_INSERT_LIBRARIES", str(tmp_path / "hostile.dylib"))
    monkeypatch.setenv("LD_PRELOAD", str(tmp_path / "hostile.so"))
    environment = discovery.subprocess_environment(manifest)
    assert "PYTHONPATH" not in environment
    assert "PYTHONHOME" not in environment
    assert not any(key.startswith(("DYLD_", "LD_")) for key in environment)
    command = discovery.isolated_runner_command(
        [
            "--algebra-dry-run",
            "--cells",
            "7",
            "--expected-manifest-sha256",
            discovery.sha256(discovery.MANIFEST),
        ]
    )
    assert command[1:4] == ["-I", "-S", "-B"]
    completed = subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (completed.stdout, completed.stderr)


def test_protocol_contains_the_exact_stdlib_only_formal_bootstrap() -> None:
    protocol = discovery.PROTOCOL.read_text(encoding="utf-8")
    embedded = protocol.split("BOOTSTRAP='", 1)[1].split("'\nenv -i", 1)[0]
    assert embedded == discovery.ISOLATED_RUNNER_BOOTSTRAP
    assert '"$PY" -I -S -B -c "$BOOTSTRAP" "$RUNNER" "$SITE"' in protocol
    assert "import numpy" not in embedded
    assert "stable_bytes(manifest_path)" in embedded
    assert "stable_bytes(runner)" in embedded
    assert "sys.dont_write_bytecode" in embedded
    assert "import_tree_closures" in embedded
    assert "tree_closure(expected_stdlib)" in embedded
    assert embedded.index("tree_closure(expected_stdlib)") < embedded.index("sys.path.append")


def test_unchecked_hash_forged_pyc_is_executable_under_B_but_exactly_bound(
    tmp_path: Path,
) -> None:
    import_root = tmp_path / "import-root"
    import_root.mkdir()
    source = import_root / "forged_target.py"
    source.write_text("FORGED = False\n", encoding="utf-8")
    pyc_path = Path(
        py_compile.compile(
            str(source),
            doraise=True,
            invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
        )
    )
    producer_before = discovery.exact_import_tree_closure(import_root)
    auditor_before = auditor.exact_import_tree_closure(import_root)
    assert producer_before == auditor_before
    assert producer_before["pyc_file_count"] == 1

    malicious_source = tmp_path / "malicious_payload.py"
    malicious_source.write_text("FORGED = True\n", encoding="utf-8")
    py_compile.compile(
        str(malicious_source),
        cfile=str(pyc_path),
        doraise=True,
        invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-B",
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, {str(import_root)!r}); "
                "import forged_target; print(forged_target.FORGED)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "True"
    producer_after = discovery.exact_import_tree_closure(import_root)
    auditor_after = auditor.exact_import_tree_closure(import_root)
    assert producer_after == auditor_after
    assert producer_after != producer_before


def test_stage_created_by_first_child_must_abort_before_second_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"
    result_stage, _evidence_stage = discovery.promotion_staging_paths(canonical, evidence)
    payload = discovery_tests.valid_preflight_hold_payload(manifest_hash)
    payload_bytes = discovery.canonical_json_bytes(payload)
    calls = 0

    def fake_run(_command: list[str], **_kwargs: Any) -> Any:
        nonlocal calls
        replicas[calls].write_bytes(payload_bytes)
        calls += 1
        if calls == 1:
            result_stage.write_bytes(b"foreign stage after child one\n")
        return type("Completed", (), {"returncode": 2})()

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="staging boundary"):
        discovery.run_replica_commands(
            (("replica-one",), ("replica-two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            canonical,
            evidence,
        )
    assert calls == 1
    assert result_stage.read_bytes() == b"foreign stage after child one\n"


def test_operationally_failed_child_replica_is_removed_by_owned_inode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")

    def fake_run(_command: list[str], **_kwargs: Any) -> Any:
        replicas[0].write_bytes(b"owned failed replica\n")
        return type("Completed", (), {"returncode": 1})()

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="failed operationally"):
        discovery.run_replica_commands(
            (("replica-one",), ("replica-two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            tmp_path / "canonical.json",
            tmp_path / "evidence.json",
        )
    assert not replicas[0].exists()


def test_promotion_rollback_preserves_a_replaced_unowned_inode(tmp_path: Path) -> None:
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"

    def replace_then_fail() -> None:
        canonical.unlink()
        canonical.write_bytes(b"foreign replacement\n")
        raise RuntimeError("injected replacement")

    with pytest.raises(RuntimeError, match="injected replacement"):
        discovery.promote_replica_bytes(
            discovery.canonical_json_bytes({"result": True}),
            discovery.canonical_json_bytes({"evidence": True}),
            canonical,
            evidence,
            post_promotion_check=replace_then_fail,
        )
    assert canonical.read_bytes() == b"foreign replacement\n"
    assert not evidence.exists()


def test_full_scan_rows_projection_aggregates_and_brackets_are_reconstructed() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value["stationary_scan"]["full_scan_trace"].pop(11),
        lambda value: value["stationary_scan"]["saved_trace"].pop(4),
        lambda value: value["stationary_scan"]["full_scan_trace"][20].__setitem__("time", 123.0),
        lambda value: value["stationary_scan"].__setitem__("minimum_sampled_density", 0.5),
        lambda value: value["stationary_scan"]["all_bracketed_roots"][0].__setitem__(
            "bracket", [1.90, 1.95]
        ),
    ]
    for mutate in mutations:
        control = auditor_tests._passing_control(manifest)
        mutate(control)
        assert _control_acceptance(control, manifest) == (False, False)


def test_generator_diagonal_primitives_are_independently_rebuilt() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    control = auditor_tests._passing_control(manifest)
    diagnostics = control["model_diagnostics"]
    diagnostics["midpoint_generator_diagonal_sum"] = -1.0e200
    cells = diagnostics["mesh"][0]
    killing_sum = (
        diagnostics["midpoint_killing_profile_sum"]
        * diagnostics["contact_killing_profile_sum"]
        / manifest["physical_parameters"]["transverse_width"]
    )
    diagnostics["analytic_column_operator_trace"] = (
        cells**2 * diagnostics["midpoint_generator_diagonal_sum"]
        + cells * diagnostics["relative_generator_diagonal_sum"]
        - diagnostics["installed_budget"] * killing_sum
    )
    assert _control_acceptance(control, manifest) == (False, False)


def test_independent_auditor_never_rolls_back_an_unowned_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "audit.json"
    monkeypatch.setattr(auditor, "REPORT", tmp_path)
    monkeypatch.setattr(auditor, "OUTPUT", output)
    monkeypatch.setattr(
        auditor,
        "EXPECTED_FIVE_PATH_ABSENCE",
        ["result.json", "evidence.json", "replica-1.json", "replica-2.json", "audit.json"],
    )
    monkeypatch.setattr(
        auditor,
        "_capture_audit_input_snapshot",
        lambda: (
            {"manifest": b"manifest", "result": b"result", "evidence": b"evidence"},
            {},
            {},
        ),
    )
    monkeypatch.setattr(auditor, "sha256_bytes", lambda _payload: auditor.EXPECTED_MANIFEST_SHA256)
    monkeypatch.setattr(auditor, "parse_json_object_bytes", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        auditor,
        "audit_payload",
        lambda *_args, **_kwargs: {
            "release_status": "HOLD_AUDIT",
            "audit_integrity_passed": False,
            "scientific_result_passed": False,
        },
    )

    def foreign_collision(path: Path, _payload: bytes) -> tuple[int, int]:
        path.write_bytes(b"foreign audit output\n")
        raise RuntimeError("injected writer failure")

    monkeypatch.setattr(auditor, "write_append_only", foreign_collision)
    with pytest.raises(RuntimeError, match="injected writer failure"):
        auditor.main()
    assert output.read_bytes() == b"foreign audit output\n"


def test_round80_finishes_result_blind() -> None:
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )
