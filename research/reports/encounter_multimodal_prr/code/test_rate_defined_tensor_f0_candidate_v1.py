from __future__ import annotations

import copy
import inspect
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
import rate_defined_tensor_f0_candidate_v1 as candidate


@pytest.fixture(scope="module")
def semantic() -> dict[str, object]:
    payload = candidate.build_semantic_candidate()
    candidate.validate_semantic_candidate(payload)
    return payload


def test_candidate_is_method_complete_but_cannot_promote(
    semantic: dict[str, object],
) -> None:
    assert semantic["schema"] == candidate.SCHEMA
    assert semantic["stage"] == candidate.STAGE
    assert semantic["status"] == (
        "PASS_F0_METHOD_CANDIDATE_AWAITING_RESOURCE_AND_INDEPENDENT_AUDIT"
    )
    assert semantic["integrated_compiled_fixture_status"] == (
        "PASS_FIXED_HETEROGENEOUS_COMPILED_TOPOLOGY_METHOD"
    )
    assert semantic["operator_fixtures"]["integrated_compiled_fixture_status"] == (
        "PASS_FIXED_HETEROGENEOUS_COMPILED_TOPOLOGY_METHOD"
    )
    assert semantic["claim_flags"] == {
        "authorizes_scientific_execution": False,
        "f0_accepted": False,
        "f0_pass": False,
        "f1_authorized": False,
        "independent_audit_complete": False,
        "measured_resource_evidence": False,
        "positive_budget_primary_controls_evaluated": False,
        "production_resource_gate": False,
        "scientific_execution": False,
    }


def test_public_builder_has_zero_arguments_and_cli_only_selects_output() -> None:
    assert tuple(inspect.signature(candidate.build_semantic_candidate).parameters) == ()
    assert tuple(
        inspect.signature(candidate.canonical_semantic_candidate_bytes).parameters
    ) == ()
    source = Path(candidate.__file__).read_text(encoding="utf-8")
    assert source.count("parser.add_argument(") == 1
    assert source.count('"--output"') == 1
    forbidden = (
        "--control",
        "--budget",
        "--root",
        "--time",
        "--threshold",
        "--precision",
        "--resource",
        "--oracle",
    )
    assert all(option not in source for option in forbidden)


def test_selector_is_parsed_from_selected_exact_entries_without_evaluation(
    semantic: dict[str, object],
) -> None:
    selector = semantic["selector_boundary"]
    assert [row["control_role"] for row in selector["controls"]] == [
        "lp_m1",
        "lp_m2",
        "lp_m3",
    ]
    assert [row["selected_entry_count"] for row in selector["controls"]] == [4, 4, 4]
    assert all(row["unit_sum_exact"] == "1/1" for row in selector["controls"])
    assert all(row["production_evaluation"] is False for row in selector["controls"])
    assert selector["positive_budget_production_evaluation"] is False
    assert selector["fixed_role_mapping"] == [
        {"control_role": "lp_m1", "selector_key": "m1"},
        {"control_role": "lp_m2", "selector_key": "m2"},
        {"control_role": "lp_m3", "selector_key": "m3"},
    ]
    assert selector["retired_source_kind_rejection"] == {
        "missing_selected_with_raw_fields_is_rejected": True,
        "rejected_source_kinds": ["raw", "S_c", "raw_hex"],
        "selected_entries_required_exactly": 4,
    }


def test_round111_one_ulp_fixture_comes_from_real_selector_paths(
    semantic: dict[str, object],
) -> None:
    fixture = semantic["selector_boundary"]["t_5_5_adjacent_binary64"]
    assert fixture["lower_decimal_source"] == "0.2674801474024188"
    assert fixture["upper_decimal_source"] == "0.2674801474024189"
    assert fixture["lower_binary64_hex"] == "0x1.11e650d5b0cabp-2"
    assert fixture["upper_binary64_hex"] == "0x1.11e650d5b0cacp-2"
    assert fixture["exact_difference"] == "1/18014398509481984"
    assert fixture["strictly_adjacent"] is True
    assert fixture["m1_source_path"].startswith(
        "selector_results.m1.frozen_coefficient_source"
    )
    assert fixture["m2_source_path"].startswith(
        "selector_results.m2.frozen_coefficient_source"
    )
    lower = float.fromhex(fixture["lower_binary64_hex"])
    upper = float.fromhex(fixture["upper_binary64_hex"])
    assert Fraction.from_float(upper) - Fraction.from_float(lower) == Fraction(
        1, 18_014_398_509_481_984
    )


def test_missing_selected_cannot_fall_back_to_raw_or_s_c() -> None:
    path, digest = candidate._source_pin("exact_selector")
    selector = candidate._strict_json_source(path, digest)
    mutant = copy.deepcopy(selector)
    del mutant["selector_results"]["m1"]["selected"]
    mutant["selector_results"]["m1"]["raw"] = ["0.25"] * 4
    mutant["selector_results"]["m1"]["S_c"] = ["0.25"] * 4
    mutant["selector_results"]["m1"]["raw_hex"] = ["0x1.0p-2"] * 4
    with pytest.raises(
        candidate.CandidateFailure,
        match="lacks normative selected weights",
    ):
        candidate._selector_control_weights(mutant)


def test_all_twelve_control_free_axis_constructors_are_bound(
    semantic: dict[str, object],
) -> None:
    configurations = semantic["configuration_constructors"]
    assert configurations["configuration_order"] == [
        "O113/Base",
        "E128/Base",
        "O129/Base",
        "O161/Base",
        "M+",
        "R+",
        "MR+",
        "MR+F",
        "A_M",
        "A_R",
        "A_Y",
        "A_MRY",
    ]
    assert configurations["configuration_count"] == 12
    assert configurations["all_axis_constructors_built"] is True
    assert configurations["control_killing_allocated"] is False
    assert configurations["positive_budget_control_evaluated"] is False
    assert configurations["total_state_workload"] == 34_787_462
    assert [row["state_count"] for row in configurations["rows"]][-1] == 2_130_048
    mr_plus_f = configurations["rows"][7]
    assert mr_plus_f["shape"] == [207, 215, 161]
    assert mr_plus_f["state_count"] == 7_165_305
    assert [axis["periodic"] for axis in mr_plus_f["axes"]] == [
        False,
        False,
        True,
    ]
    assert configurations["rows"][8]["axes"][0]["has_half_boundary_volumes"] is True
    assert configurations["rows"][9]["axes"][1]["has_half_boundary_volumes"] is True
    assert configurations["rows"][10]["axes"][2]["periodic_shift_exact"] == "1/256"
    assert configurations["rows"][11]["axes"][2]["periodic_shift_exact"] == "1/256"


def test_closed_operator_fixtures_are_structural_only(
    semantic: dict[str, object],
) -> None:
    fixtures = semantic["operator_fixtures"]
    neutral = fixtures["fixed_neutral"]
    assert neutral["directed_rate_exact"] == "1/16"
    assert neutral["stationary_mass_exact"] == "1/1"
    assert neutral["killing_exact"] == "1/64"
    heterogeneous = fixtures["fixed_heterogeneous_two_state"]
    assert heterogeneous["dense_generator_exact"] == [
        ["-5/8", "1/2"],
        ["1/4", "-3/4"],
    ]
    assert heterogeneous["stationary_masses_exact"] == ["1/1", "2/1"]
    assert heterogeneous["killing_exact"] == ["1/8", "1/2"]
    assert heterogeneous["initial_state_exact"] == ["1/1", "0/1"]
    for fixture in (neutral, heterogeneous):
        receipt = fixture["structural_receipt"]
        assert receipt["diagonal_derived_not_supplied"] is True
        assert receipt["q_killed_row_identity_enclosed"] is True
        assert receipt["global_detailed_balance_witness"] is True
        assert receipt["primary_control_excluded_by_construction"] is True
        assert receipt["budget_excluded_by_construction"] is True
        assert receipt["topology_executed"] is False


def test_heterogeneous_operator_compiled_stream_and_topology_are_integrated(
    semantic: dict[str, object],
) -> None:
    fixture = semantic["integrated_compiled_fixture"]
    assert fixture["status"] == (
        "PASS_FIXED_HETEROGENEOUS_COMPILED_TOPOLOGY_METHOD"
    )
    assert fixture["initial_state_exact"] == ["1/1", "0/1"]
    assert fixture["window"] == ["1/2", "2/1"]
    assert fixture["control_path_evaluated"] is False
    assert fixture["positive_budget_primary_control_evaluated"] is False
    assert fixture["compiled_power_stream_run_count"] == 1
    assert fixture["frozen_evaluation_count"] == 26
    assert fixture["maximum_power_index"] == 26
    assert fixture["p_action_call_count"] == 26
    assert fixture["repeated_p_actions_during_reevaluation"] == 0
    assert fixture["tile_count"] == 20
    assert fixture["oracle_call_count"] == 104
    assert fixture["unique_call_count"] == 26
    assert len(fixture["unique_query_times"]) == 26
    assert fixture["maximum_depth"] == 4
    evidence = fixture["compiled_batch_evidence"]
    assert len(evidence["evaluations"]) == 26
    assert evidence["receipt"]["resources"]["evaluation_count"] == 26
    assert evidence["receipt"]["compiled_power_stream_run_count"] == 1
    assert evidence["receipt"]["repeated_p_actions_during_reevaluation"] == 0
    assert len(fixture["compiled_batch_evidence_sha256"]) == 64
    assert fixture["root"]["role"] == "P1"
    assert fixture["root"]["kind"] == "maximum"
    assert fixture["root"]["inclusion_observed"] is True
    assert len(fixture["root"]["newton_steps"]) == 12
    assert Fraction(fixture["root"]["final_width"]) <= Fraction(1, 20)
    assert fixture["method_metadata"] == {
        "coefficient_l1_uncertainty_upper": "5/108086391056891904",
        "initial_l1_radius_upper": "0/1",
        "initial_mass_cap": "1/1",
        "maximum_center_row_sum": (
            "30023997515803305/36028797018963968"
        ),
        "maximum_killing_uncertainty": "0/1",
        "maximum_killing_upper": "1/2",
        "maximum_poisson_terms": 200_000,
        "mpfr_precision_bits": 192,
        "series_horizon": "2/1",
        "tail_tolerance": "1/1000000000000000000",
        "uniformization_rate": "3/4",
    }
    assert all(
        len(fixture[field]) == 64
        for field in (
            "compiled_backend_receipt_sha256",
            "compiled_build_c_source_sha256",
            "compiled_build_python_wrapper_sha256",
            "compiled_stream_binding_sha256",
            "scalar_series_binding_sha256",
            "scalar_series_bytes_sha256",
            "scalar_stream_sha256",
        )
    )


def test_analytic_topology_has_frozen_ledgers_and_query_union(
    semantic: dict[str, object],
) -> None:
    topology = semantic["analytic_topology_fixtures"]
    assert topology["fixed_role_order"] == ["lp_m1", "lp_m2", "lp_m3"]
    assert topology["private_adapter_exact_type_required"] is True
    assert topology["legacy_oracle_publicly_injectable"] is False
    assert topology["valid_forward_radius"] == "1/4"
    assert topology["union_unique_call_count"] == 211
    assert len(topology["union_unique_query_times"]) == 211
    expected = {
        "lp_m1": (146, 350, 147, 4, ["maximum"]),
        "lp_m2": (162, 498, 168, 4, ["maximum", "minimum", "maximum"]),
        "lp_m3": (
            178,
            646,
            188,
            4,
            ["maximum", "minimum", "maximum", "minimum", "maximum"],
        ),
    }
    for fixture in topology["fixtures"]:
        tiles, calls, unique, depth, kinds = expected[fixture["role"]]
        assert fixture["tile_count"] == tiles
        assert fixture["oracle_call_count"] == calls
        assert fixture["unique_call_count"] == unique
        assert len(fixture["unique_query_times"]) == unique
        assert fixture["maximum_depth"] == depth
        assert fixture["control_path_evaluated"] is False
        assert fixture["legacy_science_free_fields_used_as_authority"] is False
        assert [root["kind"] for root in fixture["roots"]] == kinds
        assert all(len(root["newton_steps"]) == 12 for root in fixture["roots"])
        assert all(root["inclusion_observed"] is True for root in fixture["roots"])
        assert all(
            Fraction(root["final_width"]) <= Fraction(1, 20)
            for root in fixture["roots"]
        )
        assert max(tile["depth"] for tile in fixture["tiles"]) == depth
        assert all(
            Fraction(tile["valid_forward_span"]) <= Fraction(1, 4)
            for tile in fixture["tiles"]
        )
        assert all(
            Fraction(step["valid_forward_span"]) <= Fraction(1, 4)
            for root in fixture["roots"]
            for step in root["newton_steps"]
        )


def test_private_legacy_adapter_rejects_subclasses_and_public_injection() -> None:
    class OracleSubclass(candidate._FixedAnalyticTopologyOracle):
        pass

    injected = OracleSubclass("lp_m1")
    with pytest.raises(candidate.CandidateFailure, match="exact type violated"):
        injected(Fraction(1))
    assert tuple(
        inspect.signature(candidate._run_fixed_analytic_topology).parameters
    ) == ("role",)
    assert "oracle" not in inspect.signature(
        candidate.build_semantic_candidate
    ).parameters


def test_resource_constants_bind_repaired_preexecution_freeze(
    semantic: dict[str, object],
) -> None:
    resource = semantic["resource_contract_declared_not_executed"]
    assert resource == {
        "expected_maximum_power": 27018,
        "expected_poisson_mode": 25600,
        "expected_right_index": 27014,
        "mandatory_tail_times": ["35/1", "50/1", "75/1", "100/1"],
        "maximum_distinct_query_count": 515,
        "maximum_peak_footprint_bytes": 8_589_934_592,
        "maximum_poisson_terms": 200_000,
        "maximum_process_swaps": 0,
        "maximum_rss_bytes": 4_294_967_296,
        "maximum_state_radius_upper": "1/100000000",
        "maximum_time_query_count": 512,
        "maximum_wall_seconds": 3600,
        "mpfr_precision_bits": 192,
        "poisson_tail_tolerance": "1/1000000000000000000",
        "reduction_block_size": 65_536,
        "series_horizon": "100/1",
        "shape": [207, 215, 161],
        "state_count": 7_165_305,
        "uniformization_rate": "256/1",
    }
    assert semantic["claim_flags"]["measured_resource_evidence"] is False
    assert semantic["claim_flags"]["production_resource_gate"] is False


def test_source_hashes_are_explicitly_non_authoritative(
    semantic: dict[str, object],
) -> None:
    bindings = semantic["source_bindings"]
    assert (
        bindings["observation_scope"]
        == "SAME_PROCESS_SELF_OBSERVED_NON_AUTHORITATIVE"
    )
    assert bindings["source_hashes_authoritative"] is False
    assert bindings["external_exact_byte_audit_required"] is True
    assert bindings["external_exact_byte_audit_complete"] is False
    pinned = {row["label"]: row["sha256"] for row in bindings["pinned_sources"]}
    assert pinned["candidate_freeze"] == (
        "0f282f7227220c4a0dc6ae13996ee650759d0cf6679a6d360897929386796d9b"
    )
    assert pinned["legacy_topology_engine"] == (
        "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
    )


@pytest.mark.parametrize(
    "payload",
    (
        b'{"a":1,"a":2}',
        b'{"value":NaN}',
        b'{"value":Infinity}',
        b'{"value":-0.0}',
        '{"value":"é"}'.encode(),
    ),
)
def test_strict_parser_rejects_duplicate_nonfinite_signed_zero_and_nonascii(
    payload: bytes,
) -> None:
    with pytest.raises(candidate.CandidateFailure):
        candidate._strict_json_load_bytes(payload)


def test_strict_parser_requires_exact_bytes_and_builtin_tree_types(
    semantic: dict[str, object],
) -> None:
    with pytest.raises(candidate.CandidateFailure):
        candidate._strict_json_load_bytes(bytearray(b"{}"))  # type: ignore[arg-type]

    class DictSubclass(dict):
        pass

    with pytest.raises(candidate.CandidateFailure):
        candidate.validate_semantic_candidate(DictSubclass(semantic))

    mutant = copy.deepcopy(semantic)
    mutant["claim_flags"]["f0_pass"] = 0
    with pytest.raises(candidate.CandidateFailure):
        candidate.validate_semantic_candidate(mutant)


def _mutate_controls_missing(payload: dict[str, object]) -> None:
    del payload["selector_boundary"]["controls"][0]


def _mutate_controls_extra(payload: dict[str, object]) -> None:
    payload["selector_boundary"]["controls"].append(
        copy.deepcopy(payload["selector_boundary"]["controls"][0])
    )


def _mutate_controls_reordered(payload: dict[str, object]) -> None:
    payload["selector_boundary"]["controls"].reverse()


def _mutate_configurations_missing(payload: dict[str, object]) -> None:
    del payload["configuration_constructors"]["rows"][-1]


def _mutate_configurations_extra(payload: dict[str, object]) -> None:
    payload["configuration_constructors"]["rows"].append(
        copy.deepcopy(payload["configuration_constructors"]["rows"][0])
    )


def _mutate_configurations_reordered(payload: dict[str, object]) -> None:
    payload["configuration_constructors"]["rows"].reverse()


def _mutate_roles_reordered(payload: dict[str, object]) -> None:
    payload["analytic_topology_fixtures"]["fixtures"].reverse()


def _mutate_roles_missing(payload: dict[str, object]) -> None:
    del payload["analytic_topology_fixtures"]["fixtures"][0]


def _mutate_roles_extra(payload: dict[str, object]) -> None:
    payload["analytic_topology_fixtures"]["fixtures"].append(
        copy.deepcopy(payload["analytic_topology_fixtures"]["fixtures"][0])
    )


def _mutate_claim_promotion(payload: dict[str, object]) -> None:
    payload["claim_flags"]["f0_pass"] = True


def _mutate_status_promotion(payload: dict[str, object]) -> None:
    payload["status"] = "PASS_F0_IMPLEMENTATION"


def _mutate_unknown_field(payload: dict[str, object]) -> None:
    payload["authorized_scientific_command"] = "run_f1"


def _mutate_topology_interval(payload: dict[str, object]) -> None:
    tile = payload["analytic_topology_fixtures"]["fixtures"][0]["tiles"][0]
    tile["derivative"]["lower_binary64_hex"] = tile["derivative"][
        "upper_binary64_hex"
    ]


def _mutate_root_width(payload: dict[str, object]) -> None:
    root = payload["analytic_topology_fixtures"]["fixtures"][0]["roots"][0]
    root["final_width"] = "1/10"


def _mutate_newton_step(payload: dict[str, object]) -> None:
    steps = payload["analytic_topology_fixtures"]["fixtures"][0]["roots"][0][
        "newton_steps"
    ]
    del steps[-1]


@pytest.mark.parametrize(
    "mutator",
    (
        _mutate_controls_missing,
        _mutate_controls_extra,
        _mutate_controls_reordered,
        _mutate_configurations_missing,
        _mutate_configurations_extra,
        _mutate_configurations_reordered,
        _mutate_roles_reordered,
        _mutate_roles_missing,
        _mutate_roles_extra,
        _mutate_claim_promotion,
        _mutate_status_promotion,
        _mutate_unknown_field,
        _mutate_topology_interval,
        _mutate_root_width,
        _mutate_newton_step,
    ),
)
def test_semantic_mutations_fail_closed(
    semantic: dict[str, object],
    mutator: object,
) -> None:
    mutant = copy.deepcopy(semantic)
    mutator(mutant)
    with pytest.raises(candidate.CandidateFailure):
        candidate.validate_semantic_candidate(mutant)


def test_same_process_source_drift_is_rejected(
    semantic: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(candidate, "_SOURCE_SHA256_AT_IMPORT", "0" * 64)
    with pytest.raises(candidate.CandidateFailure, match="changed after import"):
        candidate.validate_semantic_candidate(semantic)


def test_canonical_bytes_round_trip_and_are_ascii(
    semantic: dict[str, object],
) -> None:
    payload = candidate.canonical_semantic_candidate_bytes()
    assert payload.decode("ascii").encode("ascii") == payload
    assert not payload.endswith(b"\n")
    assert candidate.parse_and_validate_semantic_candidate_bytes(payload) == semantic
    with pytest.raises(candidate.CandidateFailure, match="not canonical"):
        candidate.parse_and_validate_semantic_candidate_bytes(b" " + payload)


def test_two_clean_isolated_processes_emit_identical_method_candidate_bytes(
    tmp_path: Path,
) -> None:
    source = Path(candidate.__file__).resolve()
    first = tmp_path / "replica_one.json"
    second = tmp_path / "replica_two.json"
    for output in (first, second):
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                str(source),
                "--output",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout == ""
    assert first.read_bytes() == second.read_bytes()
    replica = candidate.parse_and_validate_semantic_candidate_bytes(
        first.read_bytes()
    )
    assert replica["status"] == (
        "PASS_F0_METHOD_CANDIDATE_AWAITING_RESOURCE_AND_INDEPENDENT_AUDIT"
    )
    assert replica["claim_flags"]["f0_pass"] is False


def test_candidate_output_is_absolute_fresh_and_nonoverwriting(
    tmp_path: Path,
) -> None:
    payload = candidate.canonical_semantic_candidate_bytes()
    output = tmp_path / "candidate.json"
    candidate._write_output(str(output), payload)
    before = output.read_bytes()
    with pytest.raises(
        candidate.CandidateFailure,
        match="reserved exclusively",
    ):
        candidate._write_output(str(output), payload)
    assert output.read_bytes() == before
    with pytest.raises(candidate.CandidateFailure, match="absolute"):
        candidate._write_output("relative.json", payload)
