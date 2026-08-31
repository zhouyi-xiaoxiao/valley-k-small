from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import os
import subprocess
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import f1_to_f2_common_observable_selector_v2 as selector
import pytest


def _hex(value: int | float | Fraction) -> str:
    return float(value).hex()


def _interval(lower: Fraction, upper: Fraction, precision: int) -> selector.MPInterval:
    return selector.MPInterval(
        selector._mpfr_fraction(lower, precision, selector.gmpy2.RoundDown),
        selector._mpfr_fraction(upper, precision, selector.gmpy2.RoundUp),
        precision,
    )


def _rows(control: str) -> dict[str, dict[str, tuple[str, str]]]:
    base = {
        "lp_m1": {"P1": (_hex(10), _hex(Fraction(101, 10)))},
        "lp_m2": {
            "P1": (_hex(1), _hex(Fraction(11, 10))),
            "Q1": (_hex(2), _hex(Fraction(21, 10))),
            "P2": (_hex(3), _hex(Fraction(31, 10))),
        },
        "lp_m3": {
            "P1": (_hex(1), _hex(Fraction(11, 10))),
            "Q1": (_hex(2), _hex(Fraction(21, 10))),
            "P2": (_hex(3), _hex(Fraction(31, 10))),
            "Q2": (_hex(4), _hex(Fraction(41, 10))),
            "P3": (_hex(5), _hex(Fraction(51, 10))),
        },
    }[control]
    return {
        configuration: {role: tuple(interval) for role, interval in base.items()}
        for configuration in selector.CONFIGURATION_ORDER
    }


def _dependencies() -> dict[str, str]:
    names = (
        "central_projection_spec_sha256",
        "f1_manifest_sha256",
        "f1a_result_sha256",
        "f1a_verifier_sha256",
        "philox_spec_sha256",
        "selector_design_sha256",
        "selector_implementation_sha256",
        "selector_runtime_sha256",
        "selector_schema_sha256",
        "selector_test_sha256",
        "test_key_set_sha256",
        "upstream_f0_audit_sha256",
        "upstream_f0_implementation_sha256",
    )
    result = {name: "0" * 64 for name in names}
    result.update(
        {
            "central_projection_spec_sha256": selector.EXPECTED_CENTRAL_PROJECTION_SHA256,
            "philox_spec_sha256": selector.EXPECTED_PHILOX_SPEC_SHA256,
            "selector_runtime_sha256": selector.EXPECTED_RUNTIME_SPEC_SHA256,
            "selector_schema_sha256": selector.sha256_file(selector.SCHEMA_PATH),
            "test_key_set_sha256": selector.EXPECTED_TEST_KEY_SET_SHA256,
        }
    )
    return result


def _role_positions(control: str) -> dict[str, int]:
    if control == "lp_m1":
        return {"P1": 3}
    return {role: 1 + 2 * index for index, role in enumerate(selector.ROLE_ORDER[control])}


def _named_intervals(control: str) -> list[dict[str, object]]:
    return [
        {
            "interval": [
                _hex(Fraction(position) + Fraction(1, 8)),
                _hex(Fraction(position) + Fraction(3, 8)),
            ],
            "role": role,
        }
        for role, position in _role_positions(control).items()
    ]


def _windows(control: str) -> list[dict[str, object]]:
    positions = {"L": 1, "P1": 3, "R": 5} if control == "lp_m1" else _role_positions(control)
    return [
        {
            "left_closed": True,
            "lower": str(position),
            "name": name,
            "right_open": True,
            "upper": selector.canonical_rational(Fraction(position) + Fraction(1, 2)),
        }
        for name, position in positions.items()
    ]


def _contrasts(pairs: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{"high": high, "low": low} for high, low in pairs]


def _cut(control: str, role: str) -> dict[str, str]:
    midpoint = Fraction(_role_positions(control)[role]) + Fraction(1, 4)
    return {
        "delta_v_binary64": _hex(Fraction(1, 8)),
        "exact_midpoint": selector.canonical_rational(midpoint),
        "role": role,
        "value_binary64": _hex(midpoint),
    }


def _cut_hulls(control: str) -> list[list[str]]:
    rows = {row["role"]: row["interval"] for row in _named_intervals(control)}
    return [rows[role] for role in selector.ROLE_ORDER[control] if role.startswith("Q")]


def _valid_selection() -> dict[str, object]:
    controls = {}
    for control in selector.CONTROL_ORDER:
        role_hulls = _named_intervals(control)
        hull_map = {row["role"]: tuple(row["interval"]) for row in role_hulls}
        geometry = selector.select_cuts_and_windows(control, hull_map)
        controls[control] = {
            "common_cuts": geometry["common_cuts"],
            "contrasts": _contrasts(selector.CONTRAST_PAIRS[control]),
            "cut_hulls": _cut_hulls(control),
            "role_hulls": role_hulls,
            "valley_roles": [role for role in selector.ROLE_ORDER[control] if role.startswith("Q")],
            "windows": geometry["windows"],
        }
    base_times = {
        Fraction(1, 2),
        Fraction(2),
        Fraction(5),
        Fraction(10),
        Fraction(20),
        Fraction(35),
        Fraction(50),
        Fraction(75),
        Fraction(100),
    }
    required_times = {}
    for control, payload in controls.items():
        times = set(base_times)
        times.update(
            selector.fraction_from_float_hex(cut["value_binary64"])
            for cut in payload["common_cuts"]
        )
        for lower, upper in payload["cut_hulls"]:
            times.update(
                (selector.fraction_from_float_hex(lower), selector.fraction_from_float_hex(upper))
            )
        for window in payload["windows"]:
            times.update(
                (
                    selector.parse_canonical_rational(window["lower"]),
                    selector.parse_canonical_rational(window["upper"]),
                )
            )
        required_times[control] = [selector.canonical_rational(value) for value in sorted(times)]
    return {"controls": controls, "required_times": required_times}


def _pass_core() -> dict[str, object]:
    return {
        "authorized_scientific_command": None,
        "dependencies": _dependencies(),
        "hold": None,
        "schema_version": 2,
        "selection": _valid_selection(),
        "stage": "f1_common_observable_selection_v2",
        "stage_rows": selector.selection_pass_stage_rows(),
        "status": "PASS_TO_F1B",
    }


def _hold_core(*reasons: str) -> dict[str, object]:
    hold = selector.hold_payload(reasons)
    return {
        "authorized_scientific_command": None,
        "dependencies": _dependencies(),
        "hold": hold["hold"],
        "schema_version": 2,
        "selection": None,
        "stage": "f1_common_observable_selection_v2",
        "stage_rows": hold["stage_rows"],
        "status": hold["status"],
    }


def _registry(entries: list[dict[str, object]]) -> tuple[bytes, str]:
    states = [
        {
            "configuration": selector.REFERENCE_CONFIGURATION,
            "state_blob_sha256": hashlib.sha256(entry["state_blob"]).hexdigest(),
            "survival_interval": entry["survival_interval"],
            "time": entry["time"],
        }
        for entry in entries
    ]
    raw = selector.canonical_json_bytes({"schema_version": 1, "states": states})
    return raw, hashlib.sha256(raw).hexdigest()


def test_v1_and_round110_bytes_remain_unchanged() -> None:
    root = selector.HERE.parent
    expected = {
        root
        / "notes/f1_to_f2_common_observable_selector_v1.md": "9ab69dbd9662577aa72760bf003240ef0cd1edba167f03ceb72cd8335045c1af",
        root
        / "audits/round_110_f1_to_f2_selector_self_audit.md": "73306603dfa88a23bb9eff1514551640e811b1d1b55582790e55c04cf899915b",
    }
    for path, digest in expected.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_exact_constant_and_binary64_grammars_reject_alternates() -> None:
    assert selector.parse_canonical_float_hex("0x1.0000000000000p+0") == 1.0
    for text in ("0x1p+0", "0x1.0p+0", "1.0", "-0x0.0000000000000p+0"):
        with pytest.raises(selector.SelectorError, match="binary64") as error:
            selector.parse_canonical_float_hex(text)
        assert error.value.reason == "HOLD_NUMERIC_LEAF"
    assert selector.parse_canonical_rational("2/5") == Fraction(2, 5)
    assert selector.parse_canonical_rational("1/100") == Fraction(1, 100)
    assert selector.parse_canonical_rational("1/1000") == Fraction(1, 1000)
    assert selector.parse_canonical_rational("1/200") == Fraction(1, 200)
    for text in ("0.4", "2/10", "01", "-0"):
        with pytest.raises(selector.SelectorError) as error:
            selector.parse_canonical_rational(text)
        assert error.value.reason == "HOLD_NUMERIC_LEAF"
    assert Fraction.from_float(0.005) > Fraction(1, 200)


def test_strict_json_rejects_duplicate_keys_utf8_bom_and_noncanonical_bytes() -> None:
    with pytest.raises(selector.SelectorError) as duplicate:
        selector.strict_load_canonical_json(b'{"a": 1, "a": 2}\n')
    assert duplicate.value.reason == "HOLD_DUPLICATE_KEY"
    with pytest.raises(selector.SelectorError) as bom:
        selector.strict_load_canonical_json(b"\xef\xbb\xbf{}\n")
    assert bom.value.reason == "HOLD_DECODE_UTF8"
    with pytest.raises(selector.SelectorError) as whitespace:
        selector.strict_load_canonical_json(b"{}")
    assert whitespace.value.reason == "HOLD_CANONICAL_JSON"


@pytest.mark.parametrize(
    "raw",
    (
        b'{\n  "schema_version": 2.0\n}\n',
        b'{\n  "schema_version": 2e0\n}\n',
        b'{\n  "nested": [\n    0.0\n  ]\n}\n',
        b'{\n  "nested": {\n    "version": -0.0\n  }\n}\n',
    ),
)
def test_strict_json_recursively_rejects_every_float_token(raw: bytes) -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector.strict_load_canonical_json(raw)
    assert error.value.reason == "HOLD_CANONICAL_JSON"


def test_integer_zero_aliases_are_not_alternate_canonical_bytes() -> None:
    with pytest.raises(selector.SelectorError) as negative_zero:
        selector.strict_load_canonical_json(b'{\n  "value": -0\n}\n')
    assert negative_zero.value.reason == "HOLD_CANONICAL_JSON"
    with pytest.raises(selector.SelectorError) as positive_zero:
        selector.strict_load_canonical_json(b'{\n  "value": +0\n}\n')
    assert positive_zero.value.reason == "HOLD_DECODE_JSON"


def test_adjacent_binary64_midpoints_follow_ties_to_even() -> None:
    lower = 1.0
    middle = math.nextafter(lower, math.inf)
    upper = math.nextafter(middle, math.inf)
    assert selector.exact_midpoint_hex(lower.hex(), middle.hex())["rounded_binary64"] == lower.hex()
    assert selector.exact_midpoint_hex(middle.hex(), upper.hex())["rounded_binary64"] == upper.hex()
    assert round(Fraction(2049, 2)) == 1024
    assert round(Fraction(2051, 2)) == 1026


def test_all_12_grid_role_hull_and_global_overlap_mutation() -> None:
    rows = _rows("lp_m2")
    hulls = selector.build_role_hulls("lp_m2", rows)
    assert tuple(hulls) == selector.ROLE_ORDER["lp_m2"]

    missing = copy.deepcopy(rows)
    missing.pop("A_MRY")
    with pytest.raises(selector.SelectorError) as error:
        selector.build_role_hulls("lp_m2", missing)
    assert error.value.reason == "HOLD_SELECTOR_INPUT"

    early_reference = copy.deepcopy(rows)
    reference = early_reference.pop("MR+F")
    early_reference = {
        **dict(list(early_reference.items())[:2]),
        "MR+F": reference,
        **dict(list(early_reference.items())[2:]),
    }
    with pytest.raises(selector.SelectorError) as error:
        selector.build_role_hulls("lp_m2", early_reference)
    assert error.value.reason == "HOLD_SELECTOR_INPUT"

    overlap = _rows("lp_m2")
    overlap["O113/Base"]["P1"] = (_hex(1), _hex(Fraction(19, 10)))
    overlap["O113/Base"]["Q1"] = (_hex(2), _hex(Fraction(29, 10)))
    overlap["E128/Base"]["P1"] = (_hex(1), _hex(Fraction(5, 2)))
    overlap["E128/Base"]["Q1"] = (_hex(Fraction(13, 5)), _hex(Fraction(29, 10)))
    for configuration in selector.CONFIGURATION_ORDER[2:]:
        overlap[configuration]["P1"] = (_hex(1), _hex(Fraction(19, 10)))
        overlap[configuration]["Q1"] = (_hex(2), _hex(Fraction(29, 10)))
    with pytest.raises(selector.SelectorError) as error:
        selector.build_role_hulls("lp_m2", overlap)
    assert error.value.reason == "HOLD_ROLE_HULL_OVERLAP"


def test_common_cut_window_and_contact_mutation() -> None:
    hulls = selector.build_role_hulls("lp_m2", _rows("lp_m2"))
    selected = selector.select_cuts_and_windows("lp_m2", hulls)
    assert [cut["role"] for cut in selected["common_cuts"]] == ["Q1"]
    assert [window["name"] for window in selected["windows"]] == ["P1", "Q1", "P2"]
    assert selected["n_h"] >= 1

    h = Fraction(409, 1024)
    contact = {"P1": (_hex(Fraction(10) - h), _hex(Fraction(10) + h))}
    with pytest.raises(selector.SelectorError) as error:
        selector.select_cuts_and_windows("lp_m1", contact)
    assert error.value.reason == "HOLD_ROLE_WINDOW"


def test_required_times_and_every_grid_direct_from_zero_coverage() -> None:
    hulls = selector.build_role_hulls("lp_m2", _rows("lp_m2"))
    selected = selector.select_cuts_and_windows("lp_m2", hulls)
    times = selector.required_common_times(selected, hulls)
    coverage = {
        configuration: [
            {"direct_from_zero": True, "time": selector.canonical_rational(time)} for time in times
        ]
        for configuration in selector.CONFIGURATION_ORDER
    }
    selector.validate_f1b_state_coverage(times, coverage)
    mutation = copy.deepcopy(coverage)
    mutation["A_MRY"].pop()
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_f1b_state_coverage(times, mutation)
    assert error.value.reason == "HOLD_F1B_STATE_COVERAGE"
    sequential = copy.deepcopy(coverage)
    sequential["MR+F"][0]["direct_from_zero"] = False
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_f1b_state_coverage(times, sequential)
    assert error.value.reason == "HOLD_F1B_STATE_COVERAGE"


def test_cut_robust_basin_uses_all_extreme_corners() -> None:
    l1, v1, u1 = Fraction(1), Fraction(3, 2), Fraction(2)
    l2, v2, u2 = Fraction(3), Fraction(7, 2), Fraction(4)
    survival = {
        l1: (Fraction(4, 5), Fraction(17, 20)),
        v1: (Fraction(19, 25), Fraction(79, 100)),
        u1: (Fraction(7, 10), Fraction(3, 4)),
        l2: (Fraction(3, 5), Fraction(13, 20)),
        v2: (Fraction(14, 25), Fraction(59, 100)),
        u2: (Fraction(1, 2), Fraction(11, 20)),
        Fraction(100): (Fraction(1, 10), Fraction(3, 25)),
    }
    result = selector.basin_intervals_with_cut_uncertainty(survival, (v1, v2), ((l1, u1), (l2, u2)))
    assert result["point"] == [
        (Fraction(21, 100), Fraction(6, 25)),
        (Fraction(17, 100), Fraction(23, 100)),
        (Fraction(11, 25), Fraction(49, 100)),
    ]
    assert result["robust"] == [
        (Fraction(3, 20), Fraction(3, 10)),
        (Fraction(1, 20), Fraction(7, 20)),
        (Fraction(19, 50), Fraction(11, 20)),
    ]
    assert result["promoted"][1] == (Fraction(1, 20), Fraction(7, 20))


def test_deterministic_envelope_includes_reference_self_width_and_all_grids() -> None:
    intervals = {
        configuration: (_hex(Fraction(2, 5)), _hex(Fraction(3, 5)))
        for configuration in selector.CONFIGURATION_ORDER
    }
    result = selector.deterministic_envelope(intervals, Fraction(1, 2))
    exact_width = selector.fraction_from_float_hex(
        _hex(Fraction(3, 5))
    ) - selector.fraction_from_float_hex(_hex(Fraction(2, 5)))
    assert selector.fraction_from_float_hex(result["e_det"]) == selector.fraction_from_float_hex(
        selector.up64(exact_width)
    )
    omitted = dict(intervals)
    omitted.pop("A_Y")
    with pytest.raises(selector.SelectorError) as error:
        selector.deterministic_envelope(omitted, Fraction(1, 2))
    assert error.value.reason == "HOLD_DETERMINISTIC_ENVELOPE"


def test_tau_quantization_boundaries_are_exact() -> None:
    for multiplier, expected in ((4, None), (8, selector.Q_TAU), (9, selector.Q_TAU)):
        budget = multiplier * selector.Q_TAU
        e_det = Fraction(1, 2) - budget
        if expected is None:
            with pytest.raises(selector.SelectorError) as error:
                selector.select_tau(Fraction(1, 2), e_det, "survival")
            assert error.value.reason == "HOLD_TAU_ZERO"
        else:
            observed = selector.select_tau(Fraction(1, 2), e_det, "survival")
            assert selector.parse_canonical_rational(observed["tau"]) == expected


def test_canonical_state_ball_selects_path_a_only_and_reconciles() -> None:
    intervals = (
        (Fraction(13, 16), Fraction(15, 16)),
        (Fraction(9, 16), Fraction(11, 16)),
        (Fraction(1, 16), Fraction(3, 16)),
    )
    records = []
    for time, interval in zip(("1", "2", "100"), intervals, strict=True):
        blob = selector.encode_state_ball(((_hex(interval[0]), _hex(interval[1])),))
        records.append(
            {
                "state_blob": blob,
                "survival_interval": [_hex(interval[0]), _hex(interval[1])],
                "time": time,
            }
        )
    registry_raw, registry_sha256 = _registry(records)
    path_records = [{"state_blob": row["state_blob"], "time": row["time"]} for row in records]
    assert selector.validate_reference_path(path_records, registry_raw, registry_sha256) == (
        Fraction(28, 32),
        Fraction(20, 32),
        Fraction(4, 32),
    )

    path_b_blob = selector.encode_state_ball(((_hex(Fraction(28, 32)), _hex(Fraction(30, 32))),))
    path_b_records = copy.deepcopy(path_records)
    path_b_records[0]["state_blob"] = path_b_blob
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_reference_path(path_b_records, registry_raw, registry_sha256)
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"

    bad_scalar_entries = copy.deepcopy(records)
    bad_scalar_entries[0]["survival_interval"] = [_hex(0), _hex(Fraction(1, 10))]
    bad_registry_raw, bad_registry_sha256 = _registry(bad_scalar_entries)
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_reference_path(path_records, bad_registry_raw, bad_registry_sha256)
    assert error.value.reason == "HOLD_REFERENCE_POINT_LAW"


def test_reference_path_cannot_be_repaired_isotonically() -> None:
    records = []
    for time, value in (("1", Fraction(2, 5)), ("2", Fraction(1, 2))):
        blob = selector.encode_state_ball(((_hex(value), _hex(value)),))
        records.append(
            {
                "state_blob": blob,
                "survival_interval": [_hex(value), _hex(value)],
                "time": time,
            }
        )
    registry_raw, registry_sha256 = _registry(records)
    path_records = [{"state_blob": row["state_blob"], "time": row["time"]} for row in records]
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_reference_path(path_records, registry_raw, registry_sha256)
    assert error.value.reason == "HOLD_REFERENCE_POINT_LAW"


def test_state_ball_projection_hull_clips_box_overestimate_but_not_central_state() -> None:
    blob = selector.encode_state_ball(
        (
            (_hex(Fraction(2, 5)), _hex(Fraction(3, 5))),
            (_hex(Fraction(2, 5)), _hex(Fraction(3, 5))),
        )
    )
    result = selector._canonical_survival_from_state_ball(
        blob, hashlib.sha256(blob).hexdigest(), [_hex(Fraction(9, 10)), _hex(1)]
    )
    assert result["survival_binary64"] == _hex(1)
    assert result["projection_hull_exact"][1] == "1"


def test_state_registry_malformed_types_always_return_canonical_hold() -> None:
    blob = selector.encode_state_ball(((_hex(Fraction(1, 4)), _hex(Fraction(3, 4))),))
    entries = [
        {
            "state_blob": blob,
            "survival_interval": [_hex(Fraction(1, 4)), _hex(Fraction(3, 4))],
            "time": "1",
        }
    ]
    raw, digest = _registry(entries)
    payload = json.loads(raw)

    with pytest.raises(selector.SelectorError) as raw_type:
        selector.load_pinned_state_registry(bytearray(raw), digest)
    assert raw_type.value.reason == "HOLD_DEPENDENCY_HASH"
    with pytest.raises(selector.SelectorError) as digest_type:
        selector.load_pinned_state_registry(raw, None)
    assert digest_type.value.reason == "HOLD_DEPENDENCY_HASH"

    malformed_hash = copy.deepcopy(payload)
    malformed_hash["states"][0]["state_blob_sha256"] = 7
    malformed_hash_raw = selector.canonical_json_bytes(malformed_hash)
    with pytest.raises(selector.SelectorError) as hash_type:
        selector.load_pinned_state_registry(
            malformed_hash_raw, hashlib.sha256(malformed_hash_raw).hexdigest()
        )
    assert hash_type.value.reason == "HOLD_DEPENDENCY_HASH"

    malformed_interval = copy.deepcopy(payload)
    malformed_interval["states"][0]["survival_interval"] = None
    malformed_interval_raw = selector.canonical_json_bytes(malformed_interval)
    with pytest.raises(selector.SelectorError) as interval_type:
        selector.load_pinned_state_registry(
            malformed_interval_raw, hashlib.sha256(malformed_interval_raw).hexdigest()
        )
    assert interval_type.value.reason == "HOLD_REFERENCE_POINT_LAW"

    float_version = copy.deepcopy(payload)
    float_version["schema_version"] = 1.0
    float_version_raw = selector.canonical_json_bytes(float_version)
    with pytest.raises(selector.SelectorError) as version_alias:
        selector.load_pinned_state_registry(
            float_version_raw, hashlib.sha256(float_version_raw).hexdigest()
        )
    assert version_alias.value.reason == "HOLD_CANONICAL_JSON"

    with pytest.raises(selector.SelectorError) as blob_type:
        selector.validate_reference_path(
            [{"state_blob": memoryview(blob), "time": "1"}], raw, digest
        )
    assert blob_type.value.reason == "HOLD_REFERENCE_POINT_LAW"


def test_payload_core_digest_is_nonrecursive_and_mutations_fail_closed() -> None:
    core = _hold_core("HOLD_F1A")
    envelope = selector.build_selector_envelope(core)
    raw = selector.canonical_json_bytes(envelope)
    assert (
        selector.validate_selector_envelope_bytes(raw, expected_dependencies=core["dependencies"])
        == envelope
    )
    assert (
        envelope["canonical_payload_sha256"]
        == hashlib.sha256(selector.canonical_json_bytes(core)).hexdigest()
    )

    for replacement in (None, "", "canonical_payload_sha256"):
        mutation = copy.deepcopy(envelope)
        mutation["canonical_payload_sha256"] = replacement
        with pytest.raises(selector.SelectorError):
            selector.validate_selector_envelope_bytes(
                selector.canonical_json_bytes(mutation), expected_dependencies=core["dependencies"]
            )
    omitted = {"selector_payload_core": core}
    with pytest.raises(selector.SelectorError):
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(omitted), expected_dependencies=core["dependencies"]
        )
    wrong = copy.deepcopy(envelope)
    wrong["canonical_payload_sha256"] = "0" * 64
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(wrong), expected_dependencies=core["dependencies"]
        )
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"
    recursive = copy.deepcopy(core)
    recursive["canonical_payload_sha256"] = "0" * 64
    with pytest.raises(selector.SelectorError) as error:
        selector.build_selector_envelope(recursive)
    assert error.value.reason == "HOLD_SCHEMA"


def test_schema_enforces_semantic_empty_arrays_not_null() -> None:
    core = _pass_core()
    envelope = selector.build_selector_envelope(core)
    assert selector.validate_selector_envelope_bytes(
        selector.canonical_json_bytes(envelope), expected_dependencies=core["dependencies"]
    )
    mutation = copy.deepcopy(envelope)
    mutation["selector_payload_core"]["selection"]["controls"]["lp_m1"]["valley_roles"] = None
    mutation = selector.build_selector_envelope(mutation["selector_payload_core"])
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(mutation), expected_dependencies=core["dependencies"]
        )
    assert error.value.reason == "HOLD_SCHEMA_NULLABILITY"


def test_total_hold_order_is_unique_for_all_pairs_and_selected_triple() -> None:
    for first, second in itertools.combinations(selector.HOLD_ORDER, 2):
        assert selector.ordered_hold_reasons((second, first, second)) == (first, second)
    triple = selector.hold_payload(
        ("HOLD_DEPENDENCY_HASH", "HOLD_NUMERIC_LEAF", "HOLD_SCHEMA_NULLABILITY")
    )
    assert triple["hold"] == {
        "primary": "HOLD_SCHEMA_NULLABILITY",
        "secondary": ["HOLD_DEPENDENCY_HASH", "HOLD_NUMERIC_LEAF"],
    }
    failure_index = selector.STAGE_ORDER.index("schema")
    for index, stage in enumerate(selector.STAGE_ORDER):
        if index > failure_index:
            assert triple["stage_rows"][stage] == "NOT_RUN_AFTER_HOLD"


def test_tagged_censor_event_at_100_and_endpoint_equality_are_distinct() -> None:
    cuts = (Fraction(1), Fraction(2))
    windows = {"W": (Fraction(1), Fraction(2))}
    event_100 = selector.classify_tagged_outcome(
        {"event_time": "100", "tag": "EVENT"}, cuts, windows
    )
    survivor = selector.classify_tagged_outcome(
        {"censor_time": "100", "tag": "RIGHT_CENSORED"}, cuts, windows
    )
    assert event_100["basin_index"] == 2 and not event_100["survives_horizon"]
    assert survivor["basin_index"] is None and survivor["survives_horizon"]
    at_lower = selector.classify_tagged_outcome({"event_time": "1", "tag": "EVENT"}, cuts, windows)
    at_upper = selector.classify_tagged_outcome({"event_time": "2", "tag": "EVENT"}, cuts, windows)
    assert at_lower["basin_index"] == 0 and at_lower["window_hits"]["W"]
    assert at_upper["basin_index"] == 1 and not at_upper["window_hits"]["W"]


def test_dkw_and_cp_contacts_use_strict_inequalities() -> None:
    delta = Fraction(1, 10)
    assert not selector.strict_dkw_contact(delta, delta)
    assert selector.strict_dkw_contact(delta - Fraction(1, 1000), delta)
    assert not selector.cp_lower_gt(1, 1, Fraction(1, 4), Fraction(1, 2))
    assert not selector.cp_upper_lt(1, 0, Fraction(3, 4), Fraction(1, 2))


def test_exact_binomial_cp_acceptance_and_probability() -> None:
    assert selector.exact_binomial_range(2, Fraction(1, 2), 1, 2) == Fraction(3, 4)
    n = 20
    alpha = Fraction(1, 10)
    lower_probability = Fraction(1, 10)
    upper_probability = Fraction(9, 10)
    accepted = selector.cp_acceptance_set(n, lower_probability, upper_probability, alpha)
    assert accepted is not None
    expected_lower = next(
        x
        for x in range(1, n + 1)
        if selector.exact_binomial_range(n, lower_probability, x, n) < alpha / 2
    )
    expected_upper = max(
        x for x in range(n) if selector.exact_binomial_range(n, upper_probability, 0, x) < alpha / 2
    )
    assert accepted == (expected_lower, expected_upper)


@pytest.mark.parametrize("bounds", ((0, 3), (7, 10), (3, 7)))
def test_mpfr_binomial_dag_contains_exact_reference_in_both_directions(
    bounds: tuple[int, int],
) -> None:
    lower, upper = bounds
    exact = selector.exact_binomial_range(10, Fraction(3, 10), lower, upper)
    interval, trace = selector._mp_binomial_range_in_process(10, Fraction(3, 10), lower, upper, 256)
    observed_lower, observed_upper = interval.exact_fraction_pair()
    assert observed_lower <= exact <= observed_upper
    assert trace["dag_id"] == "BINOMIAL_RANGE_V2"


def test_binomial_dag_precision_ladder_makes_strict_decision() -> None:
    exact = selector.exact_binomial_range(10, Fraction(1, 2), 0, 3)
    result = selector.binomial_precision_ladder_decision(
        10, Fraction(1, 2), 0, 3, exact + Fraction(1, 10_000), "lt"
    )
    assert result["decision"] == "PASS"
    assert result["precision_bits"] == 256


def test_large_n_binomial_tail_repair_contains_all_small_exact_ranges() -> None:
    directions = set()
    for n in range(1, 17):
        for probability in (Fraction(1, 7), Fraction(2, 5), Fraction(1, 2), Fraction(6, 7)):
            for lower in range(n + 1):
                for upper in range(lower, n + 1):
                    exact = selector.exact_binomial_range(n, probability, lower, upper)
                    interval, trace = selector._mp_binomial_range_in_process(
                        n, probability, lower, upper, 256
                    )
                    observed_lower, observed_upper = interval.exact_fraction_pair()
                    assert observed_lower <= exact <= observed_upper
                    directions.add(trace["direction"])
    assert {
        "complement_of_two_tails",
        "difference_of_lower_tails",
        "difference_of_upper_tails",
        "full_support",
        "lower_tail",
        "upper_tail",
    } <= directions


def test_binomial_tail_degenerate_endpoints_and_invalid_mutations_fail_closed() -> None:
    for probability, atom in ((Fraction(0), 0), (Fraction(1), 9)):
        for lower, upper in ((0, 0), (0, 9), (9, 9)):
            interval, trace = selector._mp_binomial_range_in_process(
                9, probability, lower, upper, 256
            )
            exact = Fraction(int(lower <= atom <= upper))
            assert interval.exact_fraction_pair() == (exact, exact)
            assert trace["direction"] == "degenerate"
    interval, trace = selector._mp_binomial_range_in_process(0, Fraction(3, 7), 0, 0, 256)
    assert interval.exact_fraction_pair() == (Fraction(1), Fraction(1))
    assert trace["direction"] == "full_support"

    mutations = (
        (-1, Fraction(1, 2), 0, 0, 256),
        (10, Fraction(1, 2), 7, 6, 256),
        (10, Fraction(-1, 2), 0, 1, 256),
        (10, Fraction(3, 2), 0, 1, 256),
        (10, 0.5, 0, 1, 256),
        (10, Fraction(1, 2), 0, 1, 255),
    )
    for arguments in mutations:
        with pytest.raises(selector.SelectorError) as error:
            selector._mp_binomial_range_in_process(*arguments)
        assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"

    one = selector._mpfr_fraction(Fraction(1), 256, selector.gmpy2.RoundDown)
    zero = selector._mpfr_fraction(Fraction(0), 256, selector.gmpy2.RoundUp)
    with pytest.raises(selector.SelectorError) as reversed_error:
        selector.MPInterval(one, zero, 256)
    assert reversed_error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"
    with pytest.raises(selector.SelectorError) as nonfinite_error:
        selector.MPInterval(selector.gmpy2.mpfr("nan"), one, 256)
    assert nonfinite_error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_large_n_tail_uses_loggamma_recurrence_and_geometric_remainder() -> None:
    n = 100_000
    probability = Fraction(1, 200)
    boundary = selector._cp_transition_hint(n, probability, Fraction(1, 800), 1)
    interval, trace = selector._mp_binomial_range_in_process(n, probability, boundary, n, 256)
    lower, upper = interval.exact_fraction_pair()
    assert 0 < lower <= upper < Fraction(1, 100)
    assert trace["direction"] == "upper_tail"
    tail = trace["tail_traces"][0]
    assert not tail["exact_endpoint"]
    assert 0 < tail["terms_summed"] < n // 100
    assert tail["stop_target"] == "2^(-240)"
    remainder = tail["remainder_enclosure"]
    assert remainder["lower"]["mantissa_hex"] == "0"


@pytest.mark.parametrize(
    ("probability", "lower", "upper"),
    (
        (Fraction(1, 200), 80, 10_000),
        (Fraction(199, 200), 0, 9_920),
    ),
)
def test_geometrically_truncated_tail_contains_moderate_n_exact_fraction(
    probability: Fraction, lower: int, upper: int
) -> None:
    exact = selector.exact_binomial_range(10_000, probability, lower, upper)
    interval, trace = selector._mp_binomial_range_in_process(10_000, probability, lower, upper, 256)
    observed_lower, observed_upper = interval.exact_fraction_pair()
    assert observed_lower <= exact <= observed_upper
    assert not trace["tail_traces"][0]["exact_endpoint"]


def test_binomial_tail_higher_precision_nests_and_avoids_binary64_underflow() -> None:
    n = 100_000
    probability = Fraction(1, 200)
    boundary = selector._cp_transition_hint(n, probability, Fraction(1, 800), 1)
    outer, _ = selector._mp_binomial_range_in_process(n, probability, boundary, n, 256)
    inner, _ = selector._mp_binomial_range_in_process(n, probability, boundary, n, 512)
    outer_lower, outer_upper = outer.exact_fraction_pair()
    inner_lower, inner_upper = inner.exact_fraction_pair()
    assert outer_lower <= inner_lower <= inner_upper <= outer_upper

    tiny_probability = Fraction(1, 1 << 5000)
    tiny, _ = selector._mp_binomial_range_in_process(100, tiny_probability, 1, 100, 256)
    tiny_lower, tiny_upper = tiny.exact_fraction_pair()
    assert 0 < tiny_lower <= tiny_upper < Fraction(1, 1 << 4900)
    assert float(tiny_upper) == 0.0


def test_cp_acceptance_set_n8m_certified_tail_benchmark() -> None:
    started = perf_counter()
    accepted = selector.cp_acceptance_set(
        8_000_000,
        Fraction(1, 200),
        Fraction(3, 200),
        selector.ALPHA_BASIN_MEMBER,
    )
    elapsed = perf_counter() - started
    print(f"N=8,000,000 certified CP-tail benchmark: {elapsed:.6f} s")
    assert accepted is not None
    assert accepted[0] < accepted[1]
    # This is intentionally a broad regression ceiling, not a microbenchmark.
    assert elapsed < 20, f"certified N=8,000,000 CP tails took {elapsed:.3f} s"


def test_n8m_cp_worker_bounds_repeated_parent_and_child_memory() -> None:
    def rss_kib() -> int:
        return int(
            subprocess.check_output(["/bin/ps", "-o", "rss=", "-p", str(os.getpid())], text=True)
        )

    selector._isolated_cp_acceptance_set.cache_clear()
    lower = Fraction(1, 200)
    upper = Fraction(3, 200)
    alpha = Fraction(1, 800)
    before = rss_kib()
    expected = (40_646, 118_891)
    assert selector.cp_acceptance_set(8_000_000, lower, upper, alpha) == expected
    identity = selector._cp_worker_identity()
    cached_result, first_worker_peak = selector._isolated_cp_acceptance_set(
        8_000_000,
        lower.numerator,
        lower.denominator,
        upper.numerator,
        upper.denominator,
        alpha.numerator,
        alpha.denominator,
        *identity,
        os.getpid(),
    )
    assert cached_result == expected
    assert 0 < first_worker_peak <= selector.CP_WORKER_PEAK_RSS_CAP_BYTES
    for _index in range(99):
        assert selector.cp_acceptance_set(8_000_000, lower, upper, alpha) == expected
    for n in (7_999_996, 7_999_997, 7_999_998, 7_999_999):
        result = selector.cp_acceptance_set(n, lower, upper, alpha)
        assert result is not None and result[0] < result[1]
    after = rss_kib()
    cache = selector._isolated_cp_acceptance_set.cache_info()
    assert cache.hits >= 100 and cache.misses == 5
    assert after - before < 32_768


def test_cp_worker_has_no_silent_in_process_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selector._isolated_cp_acceptance_set.cache_clear()

    def cannot_start(*_args: object, **_kwargs: object) -> object:
        raise OSError("synthetic worker-start failure")

    monkeypatch.setattr(selector.subprocess, "run", cannot_start)
    with pytest.raises(selector.SelectorError) as error:
        selector.cp_acceptance_set(8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800))
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"
    selector._isolated_cp_acceptance_set.cache_clear()


def test_cp_worker_rejects_unbound_canonical_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selector._isolated_cp_acceptance_set.cache_clear()

    def forged_response(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        request = selector.strict_load_canonical_json(kwargs["input"])
        response = {
            "request_sha256": "0" * 64,
            "result": [40_646, 118_891],
            "runtime_binary_sha256": request["runtime_binary_sha256"],
            "runtime_spec_sha256": request["runtime_spec_sha256"],
            "runtime_verified": True,
            "schema_version": 1,
            "selector_source_sha256": request["selector_source_sha256"],
            "status": "PASS",
            "worker_peak_rss_bytes": 1,
        }
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout=selector.canonical_json_bytes(response), stderr=b""
        )

    monkeypatch.setattr(selector.subprocess, "run", forged_response)
    with pytest.raises(selector.SelectorError) as error:
        selector.cp_acceptance_set(8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800))
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"
    selector._isolated_cp_acceptance_set.cache_clear()


def test_cp_worker_timeout_nonzero_and_stderr_are_canonical_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout(*args: object, **_kwargs: object) -> object:
        raise subprocess.TimeoutExpired(args[0], selector.CP_WORKER_TIMEOUT_SECONDS)

    selector._isolated_cp_acceptance_set.cache_clear()
    monkeypatch.setattr(selector.subprocess, "run", timeout)
    with pytest.raises(selector.SelectorError) as timed_out:
        selector.cp_acceptance_set(8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800))
    assert timed_out.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"

    with monkeypatch.context() as scoped:
        scoped.setattr(
            selector.subprocess,
            "run",
            lambda *args, **_kwargs: subprocess.CompletedProcess(
                args=args, returncode=0, stdout=b"{}\n", stderr=b"synthetic stderr"
            ),
        )
        selector._isolated_cp_acceptance_set.cache_clear()
        with pytest.raises(selector.SelectorError) as stderr_error:
            selector.cp_acceptance_set(
                8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800)
            )
        assert stderr_error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"
    selector._isolated_cp_acceptance_set.cache_clear()


def test_internal_cp_worker_rejects_source_runtime_identity_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(selector, "_require_worker_authorization", lambda _authorization: None)
    identity = selector._cp_worker_identity()
    mutated_identity = ("0" * 64, identity[1], identity[2])
    raw = selector._cp_worker_request_bytes(
        8_000_000,
        Fraction(1, 200),
        Fraction(3, 200),
        Fraction(1, 800),
        mutated_identity,
    )
    response = selector.strict_load_canonical_json(selector._run_internal_cp_worker(raw))
    assert response["status"] == "HOLD"
    assert response["reason"] == "HOLD_DEPENDENCY_HASH"


def test_special_function_dag_and_independent_containment_contract() -> None:
    producer, trace = selector._dkw_power_interval_in_process(
        Fraction(1, 5), selector.ALPHA_SURVIVAL_MEMBER, 10_000, 256
    )
    verifier, _ = selector._dkw_power_interval_in_process(
        Fraction(1, 5), selector.ALPHA_SURVIVAL_MEMBER, 10_000, 512
    )
    assert trace["dag_id"] == "DKW_POWER_V2"
    assert selector.verify_special_certificate(producer, verifier, Fraction(9, 10), "gt")
    assert producer.canonical_payload() != verifier.canonical_payload()


@pytest.mark.parametrize("first_success", selector.PRECISION_LADDER)
def test_every_special_precision_step_is_reachable(first_success: int) -> None:
    def evaluator(precision: int) -> selector.MPInterval:
        if precision < first_success:
            return _interval(Fraction(-1), Fraction(1), precision)
        return _interval(Fraction(1), Fraction(2), precision)

    result = selector._precision_ladder_decision_in_process(evaluator, Fraction(0), "gt")
    assert result["precision_bits"] == first_success
    assert result["decision"] == "PASS"


def test_special_4096_contact_is_ambiguous_hold() -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector._precision_ladder_decision_in_process(
            lambda precision: _interval(Fraction(-1), Fraction(1), precision),
            Fraction(0),
            "gt",
        )
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_AMBIGUOUS"


def test_independent_verifier_may_differ_but_must_be_contained() -> None:
    producer = _interval(Fraction(1), Fraction(3), 256)
    verifier = _interval(Fraction(2), Fraction(5, 2), 512)
    assert selector.verify_special_certificate(producer, verifier, Fraction(0), "gt")
    outside = _interval(Fraction(2), Fraction(4), 512)
    assert not selector.verify_special_certificate(producer, outside, Fraction(0), "gt")


def test_contrast_planning_uses_two_marginal_failures_as_one_assertion() -> None:
    result = selector.contrast_planning_values(
        Fraction(3, 10),
        Fraction(1, 10),
        Fraction(1, 100),
        Fraction(1, 100),
        Fraction(1, 1000),
        Fraction(1, 1000),
        Fraction(1, 5),
    )
    assert selector.parse_canonical_rational(result["difference_low"]) > 0
    assert (
        selector.parse_canonical_rational(result["p_b_high"])
        < selector.parse_canonical_rational(result["theta"])
        < selector.parse_canonical_rational(result["p_a_low"])
    )
    selector.validate_family_ledger(selector.POWER_ASSERTION_COUNTS)
    mutation = dict(selector.POWER_ASSERTION_COUNTS)
    mutation["positive_contrast"] += 16
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_family_ledger(mutation)
    assert error.value.reason == "HOLD_POWER_BOUNDARY"


def test_philox4x32_10_full_spec_kats_and_round_mutations() -> None:
    evidence = selector.verify_rng_specs()
    assert evidence["algorithm"] == "Philox4x32-10"
    zero_7 = selector.philox4x32((0, 0, 0, 0), (0, 0), 7)
    zero_8 = selector.philox4x32((0, 0, 0, 0), (0, 0), 8)
    zero_10 = selector.philox4x32_10((0, 0, 0, 0), (0, 0))
    assert zero_7 == (0x5F6FB709, 0x0D893F64, 0x4F121F81, 0x4F730A48)
    assert zero_8 == (0x618F177A, 0x9920C1D7, 0x1EC12DC0, 0xC43B6EEB)
    assert zero_10 == (0x6627E8D5, 0xE169C58D, 0xBC57AC4C, 0x9B00DBD8)
    assert len({zero_7, zero_8, zero_10}) == 3


def test_test_key_set_is_prehashed_ordered_and_big_endian_uint64() -> None:
    raw = selector.TEST_KEY_SET_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == selector.EXPECTED_TEST_KEY_SET_SHA256
    payload = json.loads(raw)
    expected = tuple(
        int.from_bytes(bytes.fromhex(text), "big") for text in payload["ordered_keys_be_u64_hex"]
    )
    assert selector.load_test_keys() == expected
    assert len(expected) == len(set(expected)) == 8


def test_test_key_set_is_hash_and_identity_bound_at_point_of_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    basis = selector.derive_seed_basis(*("0" * 64 for _ in range(3)))
    original = json.loads(selector.TEST_KEY_SET_PATH.read_bytes())
    mutations = []
    empty = copy.deepcopy(original)
    empty["ordered_keys_be_u64_hex"] = []
    mutations.append(empty)
    reordered = copy.deepcopy(original)
    reordered["ordered_keys_be_u64_hex"] = list(reversed(reordered["ordered_keys_be_u64_hex"]))
    mutations.append(reordered)
    malformed_width = copy.deepcopy(original)
    malformed_width["ordered_keys_be_u64_hex"][0] = "00"
    mutations.append(malformed_width)
    collision = copy.deepcopy(original)
    derived = int.from_bytes(
        hashlib.sha256(b"philox-pool-v2\0" + basis + bytes((0, 0))).digest()[:8], "big"
    )
    collision["ordered_keys_be_u64_hex"][0] = f"{derived:016x}"
    mutations.append(collision)

    root = tmp_path
    for index, mutation in enumerate(mutations):
        path = root / f"test_keys_{index}.json"
        raw = selector.canonical_json_bytes(mutation)
        path.write_bytes(raw)
        with monkeypatch.context() as scoped:
            scoped.setattr(selector, "TEST_KEY_SET_PATH", path)
            with pytest.raises(selector.SelectorError) as stale:
                selector.derive_pool_keys(basis)
            assert stale.value.reason == "HOLD_TEST_KEY_SET"
        with monkeypatch.context() as scoped:
            scoped.setattr(selector, "TEST_KEY_SET_PATH", path)
            scoped.setattr(
                selector, "EXPECTED_TEST_KEY_SET_SHA256", hashlib.sha256(raw).hexdigest()
            )
            with pytest.raises(selector.SelectorError) as identity:
                selector.load_test_keys()
            assert identity.value.reason == "HOLD_TEST_KEY_SET"


@pytest.mark.parametrize(
    "malformed",
    (None, 7, b"0" * 64, "A" * 64, "0" * 63, "g" * 64),
)
def test_seed_dependencies_fail_as_canonical_dependency_hold(malformed: object) -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector.derive_seed_basis(malformed, "0" * 64, "0" * 64)
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"


@pytest.mark.parametrize("malformed", (None, b"", bytearray(32), memoryview(bytes(32))))
def test_pool_seed_basis_type_failures_are_canonical_rng_holds(malformed: object) -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector.derive_pool_keys(malformed)
    assert error.value.reason == "HOLD_RNG_SPEC"


def test_seed_pool_counter_and_chunk_domains_are_injective_on_fixture() -> None:
    seed_basis = selector.derive_seed_basis(*("0" * 64 for _ in range(3)))
    keys = selector.derive_pool_keys(seed_basis)
    assert len(keys) == len(set(keys.values())) == 6
    counter, key = selector.counter_and_key_words(
        0x0123456789ABCDEF, 0xFEDCBA9876543210, 0xC001D00D0BADF00D
    )
    assert counter == (0x89ABCDEF, 0x01234567, 0x76543210, 0xFEDCBA98)
    assert key == (0x0BADF00D, 0xC001D00D)
    chunks = {
        selector.chunk_id(seed_basis, control, pool, chunk, chunk * 100_000, (chunk + 1) * 100_000)
        for control in range(3)
        for pool in range(2)
        for chunk in range(3)
    }
    assert len(chunks) == 18
    block_0 = selector.philox4x32_10(*selector.counter_and_key_words(0, 3, keys[(0, 0)]))
    block_1 = selector.philox4x32_10(*selector.counter_and_key_words(1, 3, keys[(0, 0)]))
    assert block_0 != block_1


def test_candidate_grid_prunes_only_impossible_249_and_250_and_cap_is_exact() -> None:
    assert len(selector.CANDIDATE_GRID) == 248
    assert selector.CANDIDATE_GRID[-1] == 24_800_000
    thresholds = {"lp_m1": 8_000_000, "lp_m2": 8_000_000, "lp_m3": 9_000_000}
    assert (
        selector.first_passing_schedule(lambda control, n: n >= thresholds[control]) == thresholds
    )
    thresholds["lp_m1"] = 8_100_000
    with pytest.raises(selector.SelectorError) as error:
        selector.first_passing_schedule(lambda control, n: n >= thresholds[control])
    assert error.value.reason == "HOLD_N_CAP"


def test_no_refit_echo_is_exact_hash_equality() -> None:
    selector.require_no_refit("a" * 64, "a" * 64)
    with pytest.raises(selector.SelectorError) as error:
        selector.require_no_refit("a" * 64, "b" * 64)
    assert error.value.reason == "HOLD_NO_REFIT_VIOLATION"


def test_science_free_self_check_has_no_execution_authority() -> None:
    result = selector.run_science_free_self_check()
    assert result["status"] == "PASS_SCIENCE_FREE_SELF_CHECK"
    assert result["authorized_scientific_command"] is None
    assert not result["f1_executed"]
    assert not result["positive_budget_evaluated"]
    assert not result["monte_carlo_executed"]
    assert result["runtime"]["runtime_verified"]
