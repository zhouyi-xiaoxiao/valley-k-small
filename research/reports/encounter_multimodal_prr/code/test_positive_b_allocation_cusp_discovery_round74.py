"""Round-74 independent, result-blind pre-run attacks on the v3 freeze.

This file must never execute meshes 65 or 97 and must never invoke the
post-result auditor entrypoint.  Its only numerical execution is the permitted
seven-cell explicit-CSR algebra smoke test.  Strict xfails are open contracts,
not accepted behaviour.
"""

from __future__ import annotations

import copy
import math
from pathlib import Path
from typing import Any, Callable

import audit_positive_b_allocation_cusp_discovery_result as auditor
import numpy as np
import positive_b_allocation_cusp_discovery as discovery
import pytest
import test_audit_positive_b_allocation_cusp_discovery_result as auditor_tests
import test_positive_b_allocation_cusp_discovery as discovery_tests


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
    audit = auditor.audit_payload(
        manifest,
        result,
        evidence,
        result_bytes,
        evidence_bytes,
    )
    return audit["audit_integrity_passed"] is True


def _phase_with_shifted_centre(result: dict[str, Any], centre: np.ndarray) -> None:
    """Shift every phase record consistently without changing the mesh-97 cusp."""

    phase = result["bounded_phase_discovery"]
    phase["phase_centre_theta"] = centre.tolist()
    seen: set[int] = set()

    def update_control(control: dict[str, Any], theta: list[float], weights: list[float]) -> None:
        control["theta"] = list(theta)
        control["weights"] = list(weights)
        diagnostics = control["model_diagnostics"]
        diagnostics["minimum_weight"] = min(weights)
        diagnostics["weight_sum_error"] = abs(sum(weights) - 1.0)

    def walk(value: Any) -> None:
        if type(value) in (dict, list):
            identity = id(value)
            if identity in seen:
                return
            seen.add(identity)
        if type(value) is dict:
            if {
                "candidate_index",
                "radius",
                "direction",
                "theta",
                "weights",
            }.issubset(value):
                theta = (
                    centre + float(value["radius"]) * np.asarray(value["direction"], dtype=float)
                ).tolist()
                weights = discovery.weights_from_theta(np.asarray(theta, dtype=float)).tolist()
                value["theta"] = theta
                value["weights"] = weights
                value["eligible_geometry"] = bool(
                    discovery.point_in_trust_box(
                        discovery.REFERENCE_CUSP_TIME,
                        np.asarray(theta, dtype=float),
                    )[0]
                    and min(weights) >= discovery.SOLVER["minimum_simplex_weight"]
                )
                for key in ("mesh_65", "mesh_97"):
                    if type(value.get(key)) is dict:
                        update_control(value[key], theta, weights)
            for child in value.values():
                walk(child)
        elif type(value) is list:
            for child in value:
                walk(child)

    walk(phase)


def _replace_candidate_index_with_bool(value: Any, target: int) -> None:
    seen: set[int] = set()

    def walk(item: Any) -> None:
        if type(item) in (dict, list):
            identity = id(item)
            if identity in seen:
                return
            seen.add(identity)
        if type(item) is dict:
            if item.get("candidate_index") == target:
                item["candidate_index"] = bool(target)
            for child in item.values():
                walk(child)
        elif type(item) is list:
            for child in item:
                walk(child)

    walk(value)


def test_round74_never_starts_with_a_scientific_result_path() -> None:
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )


def test_manifest_rejects_budget_trust_chart_family_and_stale_pin_mutations() -> None:
    manifest, manifest_hash, _pins = _manifest_hash_pins()
    assert manifest_hash == auditor.EXPECTED_MANIFEST_SHA256

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value["budget_homotopy"]["schedule"].__setitem__(-1, 0.02),
        lambda value: value["solver"]["time_trust_box"].__setitem__(0, 8.0),
        lambda value: value["allocation_chart"]["reference_weights"].__setitem__(0, 0.29),
        lambda value: value["physical_parameters"].__setitem__("particle_diffusion", 0.003),
        lambda value: value["representative_gates"].__setitem__("minimum_density", -1.0),
        lambda value: value["pinned_files"]["runner"].__setitem__("sha256", "0" * 64),
    ]
    for mutate in mutations:
        changed = copy.deepcopy(manifest)
        mutate(changed)
        with pytest.raises(ValueError):
            discovery.validate_manifest(changed)


def test_terminal_budget_trust_weight_density_and_nonfinite_mutations_fail_closed() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    base = auditor_tests._passing_result(manifest)

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value["discovery_mesh_rows"][0]["homotopy"]["rows"][-1].__setitem__(
            "budget", 0.009
        ),
        lambda value: value["discovery_mesh_rows"][0]["cusp"].__setitem__("time", 18.1),
        lambda value: value["bounded_phase_discovery"]["advanced_mesh_97"][0]["mesh_65"][
            "weights"
        ].__setitem__(0, 0.29),
        lambda value: value["bounded_phase_discovery"]["advanced_mesh_97"][0]["mesh_65"][
            "tail_trace"
        ][0].__setitem__("density_per_budget", 2.0),
    ]
    for mutate in mutations:
        changed = copy.deepcopy(base)
        mutate(changed)
        assert not _producer_accepts(changed, manifest_hash, pins)
        assert not _auditor_accepts(manifest, changed)

    for nonfinite in (math.nan, math.inf, -math.inf):
        changed = copy.deepcopy(base)
        changed["small_explicit_csr_preflight"]["maximum_error"] = nonfinite
        with pytest.raises(ValueError):
            discovery.require_finite_json(changed)
        with pytest.raises(ValueError):
            auditor.require_finite_json(changed)


def test_signed_zero_cannot_satisfy_a_strict_positive_density_gate() -> None:
    diagnostics = {
        "generator_killing_identity_error": 0.0,
        "initial_mass_error": 0.0,
        "physical_installed_budget_absolute_error": 0.0,
    }
    row = {
        "density": -0.0,
        "survival": 1.0,
        "minimum_state_component": -0.0,
        "survival_density_identity_error": 0.0,
        "differential_mass_balance_error": 0.0,
    }
    gates = discovery.law_gate_results(diagnostics, [row])
    assert gates["positive_density_and_survival"] is False
    discovery.require_finite_json({"signed_zero": -0.0})


def test_symlink_toctou_stale_staging_and_once_only_helpers_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target.json"
    target.write_bytes(b"{}\n")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(RuntimeError, match="non-symlink"):
        discovery.stable_regular_file_bytes(link)
    with pytest.raises(RuntimeError, match="lexical regular"):
        auditor.stable_regular_file_bytes(link)

    changing = tmp_path / "changing.bin"
    changing.write_bytes(b"frozen bytes")
    backup = tmp_path / "changing.old"
    original_read = discovery.os.read
    attacked = False

    def replace_after_open(descriptor: int, count: int) -> bytes:
        nonlocal attacked
        if not attacked:
            attacked = True
            changing.replace(backup)
            changing.write_bytes(b"replacement")
        return original_read(descriptor, count)

    monkeypatch.setattr(discovery.os, "read", replace_after_open)
    with pytest.raises(RuntimeError, match="changed during stable capture"):
        discovery.stable_regular_file_bytes(changing)
    monkeypatch.setattr(discovery.os, "read", original_read)

    foreign = tmp_path / "foreign-result.json"
    foreign.write_bytes(b"do not delete\n")
    with pytest.raises(RuntimeError, match="must be lexically absent"):
        discovery.require_lexically_absent([foreign], "round74")
    assert foreign.read_bytes() == b"do not delete\n"

    audit_output = tmp_path / "audit.json"
    first = b'{"first": true}\n'
    auditor.write_append_only(audit_output, first)
    with pytest.raises(RuntimeError, match="append-only"):
        auditor.write_append_only(audit_output, b'{"second": true}\n')
    assert audit_output.read_bytes() == first


def test_cells7_algebra_smoke_is_byte_identical_and_science_free() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    first = discovery.canonical_json_bytes(discovery.run_algebra_dry_run(manifest, 7))
    second = discovery.canonical_json_bytes(discovery.run_algebra_dry_run(manifest, 7))
    assert first == second
    payload = discovery.parse_json_object_bytes(first, "round74 cells7 smoke")
    assert payload["status"] == "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE"
    assert payload["scientific_meshes_executed"] == []
    assert payload["all_discovery_gates_passed"] is False
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )


def test_large_factor_errors_must_block_control_and_audit_pass() -> None:
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
        factors[key] = 1.0e9
    assert discovery.validate_control_contract(control, 65) is False
    assert auditor.reconstruct_control(control, manifest) is False


def test_scan_and_root_semantics_must_not_trust_self_reported_flags() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    accepted: list[tuple[bool, bool]] = []

    wrong_type = auditor_tests._passing_control(manifest)
    wrong_type["roots"][0]["scaled_curvature"] = 1.0
    accepted.append(
        (
            discovery.validate_control_contract(wrong_type, 65),
            auditor.reconstruct_control(wrong_type, manifest),
        )
    )

    wrong_endpoints = auditor_tests._passing_control(manifest)
    wrong_endpoints["stationary_scan"]["endpoint_first_derivatives_per_budget"] = [
        -1.0,
        1.0,
    ]
    accepted.append(
        (
            discovery.validate_control_contract(wrong_endpoints, 65),
            auditor.reconstruct_control(wrong_endpoints, manifest),
        )
    )

    wrong_spacing = auditor_tests._passing_control(manifest)
    wrong_spacing["stationary_scan"]["spacing"] = 1.0
    accepted.append(
        (
            discovery.validate_control_contract(wrong_spacing, 65),
            auditor.reconstruct_control(wrong_spacing, manifest),
        )
    )
    assert accepted == [(False, False), (False, False), (False, False)]


def test_phase_centre_must_equal_the_mesh97_cusp_theta() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()
    result = copy.deepcopy(auditor_tests._passing_result(manifest))
    mesh97_cusp = result["discovery_mesh_rows"][1]["cusp"]["theta"]
    shifted = np.asarray((2.0**-8, -(2.0**-8)))
    _phase_with_shifted_centre(result, shifted)
    first = result["bounded_phase_discovery"]["candidate_generation"][0]
    observed_centre = np.asarray(first["theta"], dtype=float) - float(first["radius"]) * np.asarray(
        first["direction"], dtype=float
    )
    assert not np.array_equal(observed_centre, np.asarray(mesh97_cusp, dtype=float))
    assert _producer_accepts(result, manifest_hash, pins) is False
    assert _auditor_accepts(manifest, result) is False


def test_honest_nonzero_phase_centre_must_survive_round_trip_roundoff() -> None:
    centre = np.asarray((0.01, -0.01))
    generated = discovery.candidate_controls(centre)
    screened = []
    missing = []
    for candidate in generated:
        row = {
            **candidate,
            "mesh_65": None,
            "mesh_65_evaluation_status": "NOT_ELIGIBLE_GEOMETRY",
        }
        if candidate["eligible_geometry"]:
            row["mesh_65_evaluation_status"] = "HOLD_CONTROL_EVALUATION"
            missing.append(candidate["candidate_index"])
        screened.append(row)
    phase = {
        "phase_centre_theta": centre.tolist(),
        "candidate_generation": generated,
        "screened_mesh_65": screened,
        "advanced_mesh_97": [],
        "representatives": {"1": None, "2": None, "3": None},
        "all_three_regions_found": False,
        "phase_complete": False,
        "hold_reasons": [f"missing_eligible_mesh_65_evaluations:{missing}"],
        "search_expanded": False,
    }
    assert discovery.validate_phase_contract(phase) is True

    forged = copy.deepcopy(phase)
    forged["phase_centre_theta"] = [0.0, 0.0]
    assert discovery.validate_phase_contract(forged, centre.tolist()) is False


def test_native_number_types_must_be_exact_in_preflight_and_candidate_indices() -> None:
    manifest, manifest_hash, pins = _manifest_hash_pins()

    hold = discovery_tests.valid_preflight_hold_payload(manifest_hash, pins)
    hold["small_explicit_csr_preflight"]["mesh"] = [7.0, 7.0, 7.0]
    hold["small_explicit_csr_preflight"]["state_count"] = 343.0
    preflight_accepted = (
        _producer_accepts(hold, manifest_hash, pins),
        _auditor_accepts(manifest, hold),
    )

    passed = copy.deepcopy(auditor_tests._passing_result(manifest))
    _replace_candidate_index_with_bool(passed["bounded_phase_discovery"], 1)
    candidate_accepted = (
        _producer_accepts(passed, manifest_hash, pins),
        _auditor_accepts(manifest, passed),
    )
    assert preflight_accepted == (False, False)
    assert candidate_accepted == (False, False)


def test_complete_runtime_local_import_graph_must_be_directly_pinned() -> None:
    manifest, _manifest_hash, _pins = _manifest_hash_pins()
    bridge_manifest = discovery.load_json(
        discovery.REPORT / "artifacts/data/continuum_broad_patch_b0_bridge_manifest.json"
    )
    nested = bridge_manifest["pinned_files"]["exact_continuum_dependency"]
    assert nested["path"] == "code/continuum_observable_four_patch.py"
    assert discovery.sha256(discovery.REPORT / nested["path"]) == nested["sha256"]
    directly_snapshotted = {row["path"] for row in manifest["pinned_files"].values()}
    assert nested["path"] in directly_snapshotted

    metadata, payloads = discovery.capture_complete_freeze_snapshot(discovery.MANIFEST, manifest)
    role = "continuum_runtime_dependency"
    assert metadata[role]["sha256"] == nested["sha256"]
    assert discovery.sha256_bytes(payloads[role]) == nested["sha256"]
    attacked_metadata = copy.deepcopy(metadata)
    attacked_payloads = dict(payloads)
    attacked_payloads[role] = payloads[role] + b"\n# drift"
    with pytest.raises(RuntimeError, match="snapshot changed"):
        discovery.require_same_freeze_snapshot(
            metadata,
            payloads,
            attacked_metadata,
            attacked_payloads,
        )


@pytest.mark.parametrize("staging_role", ("canonical", "evidence"))
def test_stale_promotion_staging_must_abort_before_any_replica(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, staging_role: str
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"
    stale_stage = tmp_path / f".{staging_role}.json.staging"
    stale_stage.write_bytes(b"foreign stage\n")
    payload = discovery_tests.valid_preflight_hold_payload(manifest_hash)
    payload_bytes = discovery.canonical_json_bytes(payload)
    calls = 0

    def fake_run(_command: list[str], **_kwargs: Any) -> Any:
        nonlocal calls
        replicas[calls].write_bytes(payload_bytes)
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
    assert stale_stage.read_bytes() == b"foreign stage\n"


def test_round74_finishes_without_a_scientific_result_path() -> None:
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )
