from __future__ import annotations

import copy
import json
import shutil
from fractions import Fraction
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as producer
import pytest
import validate_continuum_c0_model_contract_candidate_v2 as verifier

REPORT = Path(__file__).resolve().parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"


def _load() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _encode(payload: dict[str, object]) -> bytes:
    # Deliberately independent of the verifier's encoder.
    return (json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode(
        "ascii"
    )


def _expect(payload: dict[str, object], code: str) -> None:
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(_encode(payload))
    assert caught.value.code == code


def _copy_allowed_report(tmp_path: Path) -> Path:
    report = tmp_path / "report"
    for descriptor in verifier.FROZEN_SOURCES.values():
        relative = Path(descriptor["path"])
        target = report / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPORT / relative, target)
    legacy = report / verifier.V1_RELATIVE
    legacy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPORT / verifier.V1_RELATIVE, legacy)
    return report


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("finite_volume_identification", "P_h", "denominator"), "M_i_pi"),
        (("finite_volume_identification", "A_h", "denominator"), "pi_h_i"),
        (("finite_volume_identification", "rho_i", "numerator"), "pi_h_i"),
        (("finite_volume_identification", "exact_identities", "P_h_J_h"), "I"),
        (
            (
                "finite_volume_identification",
                "nonclaims",
                "J_h_P_h_operator_norm_convergence_claimed",
            ),
            True,
        ),
        (("finite_volume_identification", "S_h", "defined_on_all_H_L"), True),
    ],
)
def test_map_denominator_identity_and_domain_mutations_hold(
    path: tuple[str, ...], value: object
) -> None:
    payload = _load()
    target: object = payload
    for key in path[:-1]:
        assert isinstance(target, dict)
        target = target[key]
    assert isinstance(target, dict)
    target[path[-1]] = value
    _expect(payload, verifier.HOLD_MAPS)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("conditional_renormalization_to_one", True),
        ("target", "unit_probability_mass"),
        ("scale_formula", "g_h_L=sum_i_tilde_pi_h_i/M_L"),
        ("global_mass_identity", "sum_i_pi_h_i=1"),
    ],
)
def test_global_gauge_mutations_hold(key: str, value: object) -> None:
    payload = _load()
    payload["stationary_mass_gauge"][key] = value
    _expect(payload, verifier.HOLD_GAUGE)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("raw_to_gauged_bridge_proved", True),
        ("gauge_enclosures_frozen_for_every_declared_configuration", True),
        ("common_conductance_intervals_constructed_for_every_declared_edge", True),
        ("gauged_ideal_member_containment_proved_for_every_declared_configuration", True),
        ("production_centres_accepted_as_exactly_reversible", True),
        ("production_centre_h_to_zero_theorem_claimed", True),
        ("production_interval_width_belongs_to", "E_space"),
        ("current_single_axis_diagnostic_generalized_to_all_configurations", True),
    ],
)
def test_production_bridge_promotions_hold(key: str, value: object) -> None:
    payload = _load()
    payload["production_gauge_bridge"][key] = value
    _expect(payload, verifier.HOLD_PRODUCTION)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("scalar_convention", "primary_scalar_field", "complex_bilinear"),
        ("scalar_convention", "complex_forms_conjugate_first_factor", False),
        ("discrete_operator_convention", "free_graph_connected", False),
        (
            "discrete_operator_convention",
            "probability_forward_equation",
            "p_prime=Q_c*p",
        ),
        ("discrete_operator_convention", "undirected_edge_has_extra_one_half", True),
        ("discrete_operator_convention", "free_offdiagonal_rates_nonnegative", False),
    ],
)
def test_scalar_row_column_and_edge_factor_mutations_hold(
    section: str, key: str, value: object
) -> None:
    payload = _load()
    payload[section][key] = value
    _expect(payload, verifier.HOLD_OPERATOR)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("meshwise_renormalization", True),
        ("initial_reference_mass", "p0_h_i"),
        ("unique_discrete_density_ratio", "u0_h_i=A_h[u0]_i"),
    ],
)
def test_initial_probability_reference_confusions_hold(key: str, value: object) -> None:
    payload = _load()
    payload["initial_law"][key] = value
    _expect(payload, verifier.HOLD_INITIAL)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("complete_c0_independently_accepted", True),
        ("positive_budget_scientific_values_read", True),
        ("production_raw_to_gauged_bridge_proved", True),
        ("control_values_committed_for_c0", True),
        ("release_eligible", True),
    ],
)
def test_claim_promotions_hold(key: str, value: object) -> None:
    payload = _load()
    payload["claim_boundary"][key] = value
    _expect(payload, verifier.HOLD_CLAIMS)


def test_control_values_or_sealed_source_promotion_holds() -> None:
    payload = _load()
    payload["control_contract"]["exclusions"]["actual_control_values_included"] = True
    _expect(payload, verifier.HOLD_CONTROL)

    payload = _load()
    payload["control_contract"]["future_source"]["required_before_complete_c0"] = False
    _expect(payload, verifier.HOLD_CONTROL)


def test_previous_contract_path_hash_or_mutation_claim_holds() -> None:
    for key, value in (
        ("path", "artifacts/data/continuum_c0_model_contract_candidate_v2.json"),
        ("sha256", "0" * 64),
        ("v1_bytes_mutated", True),
    ):
        payload = _load()
        payload["previous_contract"][key] = value
        _expect(payload, verifier.HOLD_LEGACY)


def test_source_role_swap_and_living_note_pin_hold() -> None:
    payload = _load()
    left = payload["frozen_sources"]["initial_source"]
    right = payload["frozen_sources"]["killing_geometry_source"]
    payload["frozen_sources"]["initial_source"] = right
    payload["frozen_sources"]["killing_geometry_source"] = left
    _expect(payload, verifier.HOLD_SOURCES)

    payload = _load()
    payload["source_policy"]["living_continuum_program_pinned"] = True
    _expect(payload, verifier.HOLD_SOURCES)


def test_result_key_and_forbidden_path_injection_hold_before_schema() -> None:
    payload = _load()
    payload["Peak-Time"] = "1/1"
    _expect(payload, verifier.HOLD_RESULT_BLINDNESS)

    payload = _load()
    payload["source_policy"]["extra"] = "scratch/opaque_result.json"
    _expect(payload, verifier.HOLD_RESULT_BLINDNESS)

    for attacked in (
        {"Peak-Time": "1/1"},
        {"harmless": "results/value.json"},
        {"harmless": "controls/value.json"},
        {"harmless": "result.json"},
        {"harmless": "control.json"},
        {"harmless": "nested/positive-result.json"},
        {"harmless": "nested/sealed_control.json"},
    ):
        with pytest.raises(producer.BuildHold):
            producer._scan_result_bearing(attacked)

    for injected in (
        "result.json",
        "control.json",
        "nested/positive_result.json",
        "nested/sealed-control.json",
    ):
        with pytest.raises(verifier.C0V2Hold) as caught:
            verifier._scan_result_bearing({"harmless": injected})
        assert caught.value.code == verifier.HOLD_RESULT_BLINDNESS


def test_deep_json_is_converted_to_a_stable_encoding_hold() -> None:
    deep = b'{"nested":' + b"[" * 2_000 + b"0" + b"]" * 2_000 + b"}\n"
    huge_integer = b'{"x":' + b"9" * 5_000 + b"}\n"
    for attacked in (deep, huge_integer):
        with pytest.raises(producer.BuildHold):
            producer.parse_source_json(attacked)
        with pytest.raises(verifier.C0V2Hold) as caught:
            verifier.verify_contract_bytes(attacked)
        assert caught.value.code == verifier.HOLD_ENCODING


def test_direct_bytes_entrypoints_enforce_the_size_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    attacked = b'{"x":"123456789"}\n'
    monkeypatch.setattr(producer, "MAX_FILE_BYTES", 8)
    with pytest.raises(producer.BuildHold):
        producer.parse_source_json(attacked)
    monkeypatch.setattr(verifier, "MAX_FILE_BYTES", 8)
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier._parse_json(attacked, code=verifier.HOLD_ENCODING, canonical=True)
    assert caught.value.code == verifier.HOLD_ENCODING


def test_noncanonical_duplicate_nonfinite_float_bom_and_extra_newline_hold() -> None:
    raw = ARTIFACT.read_bytes()
    duplicate = b'{\n  "schema": "evil",' + raw[1:]
    nonfinite = raw.replace(b'"physical_dimension": 2', b'"physical_dimension": NaN', 1)
    floating = raw.replace(b'"physical_dimension": 2', b'"physical_dimension": 2.0', 1)
    compact = json.dumps(_load(), sort_keys=True).encode("ascii") + b"\n"
    for attacked in (duplicate, nonfinite, floating, b"\xef\xbb\xbf" + raw, raw + b"\n", compact):
        with pytest.raises(verifier.C0V2Hold) as caught:
            verifier.verify_contract_bytes(attacked)
        assert caught.value.code == verifier.HOLD_ENCODING


def test_map_gauge_row_and_complex_witness_mutations_hold() -> None:
    mutations = [
        ("map_denominators", "inner_v_Pu", "1/2"),
        ("global_gauge", "correct_gauge", "1/2"),
        ("row_column", "transpose_Q_p_total_derivative", "1/1"),
        ("complex_positivity", "sesquilinear_edge_square_correct", "-1/1"),
    ]
    for section, key, value in mutations:
        payload = _load()
        payload["witnesses"][section][key] = value
        _expect(payload, verifier.HOLD_WITNESSES)

    payload = _load()
    payload["witnesses"]["map_denominators"]["pi_h_i"][0] = "0/1"
    _expect(payload, verifier.HOLD_WITNESSES)

    payload = _load()
    payload["witnesses"]["map_denominators"] = []
    _expect(payload, verifier.HOLD_WITNESSES)


def test_source_byte_drift_duplicate_nonfinite_and_result_injection_hold(tmp_path: Path) -> None:
    report = _copy_allowed_report(tmp_path)
    initial = report / verifier.FROZEN_SOURCES["initial_source"]["path"]

    data = json.loads(initial.read_text(encoding="utf-8"))
    data["scope"] = "drift"
    initial.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES

    report = _copy_allowed_report(tmp_path / "duplicate")
    source = report / verifier.FROZEN_SOURCES["control_method_commitment"]["path"]
    source.write_bytes(b'{"schema":"a","schema":"b"}\n')
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES

    report = _copy_allowed_report(tmp_path / "nonfinite")
    source = report / verifier.FROZEN_SOURCES["control_method_commitment"]["path"]
    source.write_bytes(b'{"x":NaN}\n')
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES

    report = _copy_allowed_report(tmp_path / "result")
    source = report / verifier.FROZEN_SOURCES["control_method_commitment"]["path"]
    source.write_bytes(b'{"peakTime":"1/1"}\n')
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES

    for index, injected_path in enumerate(("result/x.json", "results/x.json", "control/x.json")):
        report = _copy_allowed_report(tmp_path / f"path-{index}")
        source = report / verifier.FROZEN_SOURCES["control_method_commitment"]["path"]
        data = json.loads(source.read_text(encoding="utf-8"))
        data["status"] = injected_path
        source.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        with pytest.raises(verifier.C0V2Hold) as caught:
            verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
        assert caught.value.code == verifier.HOLD_SOURCES

    for index, encoding in enumerate(("compact", "extra-newline", "reverse-keys")):
        report = _copy_allowed_report(tmp_path / f"canonical-{index}")
        source = report / verifier.FROZEN_SOURCES["control_method_commitment"]["path"]
        data = json.loads(source.read_text(encoding="utf-8"))
        if encoding == "compact":
            attacked = json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"
        elif encoding == "extra-newline":
            attacked = json.dumps(data, sort_keys=True, indent=2) + "\n\n"
        else:
            attacked = json.dumps(
                {key: data[key] for key in reversed(list(data))}, indent=2
            ) + "\n"
        source.write_text(attacked, encoding="utf-8")
        with pytest.raises(verifier.C0V2Hold) as caught:
            verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
        assert caught.value.code == verifier.HOLD_SOURCES


def test_symlink_source_is_rejected(tmp_path: Path) -> None:
    report = _copy_allowed_report(tmp_path)
    source = report / verifier.FROZEN_SOURCES["mathematical_source"]["path"]
    target = source.with_suffix(".target")
    source.rename(target)
    source.symlink_to(target.name)
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES


def test_symlink_parent_directory_is_rejected_without_following(tmp_path: Path) -> None:
    report = _copy_allowed_report(tmp_path)
    artifacts = report / "artifacts"
    target = report / "artifacts-real"
    artifacts.rename(target)
    artifacts.symlink_to(target.name, target_is_directory=True)
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_SOURCES


def test_duplicate_configuration_label_and_support_boundary_equality_fail_helpers() -> None:
    contract = _load()
    family = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["configuration_family"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    initial = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["initial_source"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    duplicated = copy.deepcopy(family)
    duplicated["configurations"][-1]["label"] = duplicated["configurations"][0]["label"]
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier._validate_initial_and_mesh(contract, duplicated, initial)
    assert caught.value.code == verifier.HOLD_MESH

    equality = copy.deepcopy(family)
    centre = verifier._fraction_from_hex(
        initial["starts_binary64_hex"]["midpoint"], verifier.HOLD_INITIAL, "centre"
    )
    half = verifier._fraction_from_hex(
        initial["half_width_binary64_hex"], verifier.HOLD_INITIAL, "half"
    )
    equality["configurations"][0]["midpoint"]["lower_binary64_hex"] = float(
        centre - half
    ).hex()
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier._validate_initial_and_mesh(contract, equality, initial)
    assert caught.value.code == verifier.HOLD_INITIAL


def test_periodic_support_wrap_and_cell_partitions_are_checked_exactly() -> None:
    start = Fraction(-1, 2)
    period = Fraction(1)
    half = verifier._fraction_from_hex(
        "0x1.47ae147ae147bp-6", verifier.HOLD_INITIAL, "half"
    )
    crossing_centre = verifier._fraction_from_hex(
        "0x1.f5c28f5c28f5cp-2", verifier.HOLD_INITIAL, "crossing centre"
    )
    arc = verifier._wrapped_arc_segments(start, period, crossing_centre, half)
    assert len(arc) == 2
    assert sum((right - left for left, right in arc), Fraction(0)) == 2 * half

    for shift in (Fraction(0), Fraction(1, 256)):
        cells = verifier._periodic_cell_segments(start, period, 128, shift)
        assert cells[0][0] == start
        assert cells[-1][1] == start + period
        assert sum((right - left for left, right in cells), Fraction(0)) == period

    contract = _load()
    family = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["configuration_family"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    initial = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["initial_source"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    initial["transverse_period_exact"] = "2/1"
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier._validate_initial_and_mesh(contract, family, initial)
    assert caught.value.code == verifier.HOLD_INITIAL


def test_killing_support_uses_exact_bounds_from_every_configuration() -> None:
    family = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["configuration_family"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    killing = json.loads(
        (REPORT / verifier.FROZEN_SOURCES["killing_geometry_source"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    exact = verifier._validate_parameters(verifier.EXPECTED_PARAMETERS)
    verifier._validate_killing(killing, family, exact)

    attacked = copy.deepcopy(killing)
    attacked["support_basis"]["centres_exact"][-1] = "46/25"
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier._validate_killing(attacked, family, exact)
    assert caught.value.code == verifier.HOLD_KILLING


def test_legacy_v1_byte_mutation_holds_without_following_its_embedded_path(tmp_path: Path) -> None:
    report = _copy_allowed_report(tmp_path)
    legacy = report / verifier.V1_RELATIVE
    raw = bytearray(legacy.read_bytes())
    raw[-2] = ord(" ")
    legacy.write_bytes(bytes(raw))
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.verify_contract_bytes(ARTIFACT.read_bytes(), report=report)
    assert caught.value.code == verifier.HOLD_LEGACY
    assert not (report / "scratch").exists()
