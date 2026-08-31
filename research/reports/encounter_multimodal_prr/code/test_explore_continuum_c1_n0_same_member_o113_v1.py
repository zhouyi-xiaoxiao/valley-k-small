"""Focused tests for the bounded O113 exploratory composition receipt."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

CODE_ROOT = Path(__file__).resolve().parent
REPORT_ROOT = CODE_ROOT.parent
SCRIPT = CODE_ROOT / "explore_continuum_c1_n0_same_member_o113_v1.py"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import explore_continuum_c1_n0_same_member_o113_v1 as explorer  # noqa: E402


@pytest.fixture(scope="module")
def clean_replays(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[
    dict[str, object],
    dict[str, object],
    bytes,
]:
    root = tmp_path_factory.mktemp("o113_exploratory_replays")
    observations: list[dict[str, object]] = []
    payloads: list[bytes] = []
    for index in range(2):
        output = root / f"receipt_{index}.json"
        completed = subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPT), "--output", str(output)],
            cwd=REPORT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=explorer.MAX_WALL_SECONDS + 10,
        )
        assert completed.returncode == 0, completed.stderr
        assert completed.stderr == ""
        observation = json.loads(completed.stdout)
        payload = output.read_bytes()
        assert observation["receipt_sha256"] == hashlib.sha256(payload).hexdigest()
        assert observation["receipt_byte_length"] == len(payload)
        assert len(payload) <= explorer.MAX_OUTPUT_BYTES
        observations.append(observation)
        payloads.append(payload)
    assert payloads[0] == payloads[1]
    return observations[0], json.loads(payloads[0]), payloads[0]


def test_exact_formal_lane_and_mutation_sentinels() -> None:
    lane = explorer.build_formal_lane()
    assert lane["all_identities_passed"] is True
    assert all(lane["mutation_sentinels"].values())
    assert lane["interval_midpoint_or_rational_selector_used"] is False


def test_interval_lane_has_no_member_selector_and_is_outward() -> None:
    value = explorer.Interval(Fraction(1, 3), Fraction(2, 3))
    denominator = explorer.Interval(Fraction(2), Fraction(3))
    quotient = value.divide(denominator)
    assert quotient == explorer.Interval(Fraction(1, 9), Fraction(1, 3))
    assert not hasattr(value, "midpoint")


def test_small_tensor_stream_counts_and_periodic_seam_mutation() -> None:
    result = explorer.stream_tensor_topology((3, 4, 5))
    assert result["state_count"] == 60
    assert result["undirected_edge_count"] == 145
    assert result["directed_off_diagonal_count"] == 290
    with pytest.raises(explorer.ExploratoryReceiptError, match="periodic seam"):
        explorer.stream_tensor_topology(
            (3, 4, 5),
            include_periodic_seam=False,
            require_periodic_seam=True,
        )


def test_report_tree_output_is_rejected_before_write() -> None:
    forbidden = REPORT_ROOT / "artifacts/data/forbidden_o113_exploratory_receipt.json"
    assert not forbidden.exists()
    with pytest.raises(explorer.ExploratoryReceiptError, match="report tree"):
        explorer._output_path(str(forbidden))
    assert not forbidden.exists()


def test_two_clean_replays_are_byte_deterministic(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    observation, receipt, _ = clean_replays
    assert observation["status"] == explorer.STATUS
    assert receipt["status"] == explorer.STATUS
    assert observation["peak_rss_bytes"] <= explorer.MAX_RSS_BYTES
    assert observation["elapsed_seconds"] <= explorer.MAX_WALL_SECONDS


def test_receipt_keeps_every_material_promotion_false(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    claims = receipt["claims"]
    disclosed_exploratory_claims = {
        "exploratory_same_process_formula_composition_completed",
        "actual_exploratory_control_values_present",
        "exploratory_barycentre_control_witness_present",
    }
    for key, value in claims.items():
        if key in disclosed_exploratory_claims:
            assert value is True, key
        else:
            assert value is False, key


def test_o113_science_counts_and_streamed_topology(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    outward = receipt["outward_interval_lane"]
    primitive = outward["primitive_summary"]
    role10 = outward["role10_summary"]
    stream = receipt["streamed_tensor"]
    assert primitive["raw_cell_count"] == 339
    assert primitive["physical_cell_count"] == 339
    assert primitive["axis_edge_count"] == 337
    assert primitive["positive_directed_axis_rate_count"] == 674
    assert primitive["reflecting_boundary_zero_rate_count"] == 4
    assert role10["contact_record_count"] == 12_769
    assert role10["active_contact_cell_count"] == 335
    assert role10["full_contact_cell_count"] == 243
    assert role10["profile_record_count"] == 452
    assert stream["state_count"] == 1_442_897
    assert stream["undirected_edge_count"] == 4_303_153
    assert stream["logical_Q_entry_count_with_diagonal"] == 10_049_203
    assert stream["topology_only_no_rates_conductances_or_diagonals_streamed"] is True
    assert receipt["all_science_gates_passed"] is True


def test_barycentre_is_predeclared_numerical_witness_only(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    composition = receipt["outward_interval_lane"]["composition"]
    barycentre = composition["barycentre_contract"]
    assert barycentre["weights_exact"] == ["1/4"] * 4
    assert barycentre["predeclared_not_result_selected"] is True
    assert barycentre["numerical_exploratory_witness_only"] is True
    assert barycentre["actual_exploratory_control_values_present"] is True
    assert barycentre["source_control_authority_contains_these_values"] is False
    assert barycentre["concrete_production_control"] is False
    assert barycentre["budget_used"] is False
    records = composition["control_free_basis_and_barycentre"]
    assert records[-1]["label"] == "barycentre_1_4_each"
    assert records[-1]["nonnegative"] is True
    assert records[-1]["hull_endpoints_are_not_claimed_attained_extrema"] is True


def test_frozen_outputs_are_regression_only_and_all_cross_checks_pass(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    regression = receipt["non_authoritative_regression_cross_checks"]
    assert regression["role"] == "post_computation_regression_only_not_scientific_input"
    assert regression["independent_oracle_claimed"] is False
    assert regression["same_backend_outputs_used"] is True
    assert regression["raw_oracle"]["member_digest_sha256"] == (
        "fa2b5008aaa8ec4a636f8797cf29174e9512e25cc5719a9b026ab748a6f91b80"
    )
    assert regression["raw_oracle"]["raw_file_pin_checks"] == 9
    assert regression["raw_oracle"]["raw_file_pin_total"] == 9
    assert regression["checks"]["global_gauge_oracle_overlap"] is True
    assert regression["checks"]["rho_enclosure_hull_oracle_overlap"] is True
    assert regression["checks"]["role10_contact_exact_replay"] is True
    assert regression["checks"]["role10_profiles_exact_replay"] is True
    assert regression["all_passed"] is True


def test_receipt_is_compact_and_contains_no_dense_tensor_payload(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, payload = clean_replays
    assert len(payload) < 100_000
    assert receipt["scope"]["factorized_no_dense_tensor"] is True
    assert "killing_intervals" not in payload.decode("ascii")
    assert "stationary_mass_tensor" not in payload.decode("ascii")


def test_all_primary_sources_partitions_and_oracles_use_literal_sha_pins(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    assert receipt["method"]["all_primary_and_oracle_literal_sha256_pins_checked"] is True
    assert receipt["method"]["cross_source_semantic_joins_checked"] is True
    assert receipt["method"]["imported_scientific_kernel_source_hashes_checked"] is True
    assert receipt["source_inputs"]["factorization"]["sha256"] == (
        "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca"
    )
    assert receipt["source_inputs"]["symbolic_control"]["sha256"] == (
        "fd6edf9046956d311366ff51f229523ab605d80073515b9768d5fa5cafa8904f"
    )
    assert all(
        receipt["source_inputs"][role]["sha256"] == expected
        for role, expected in explorer.KERNEL_SHA256.items()
    )
    assert all(
        source["literal_current_sha256_pin_checked"] is True
        for source in receipt["source_inputs"].values()
    )
    regression = receipt["non_authoritative_regression_cross_checks"]
    assert regression["raw_oracle"]["sha256"] == explorer.ORACLE_SHA256["raw"]
    assert regression["stationary_oracle"]["sha256"] == explorer.ORACLE_SHA256["stationary"]
    assert regression["role10_oracle"]["sha256"] == explorer.ORACLE_SHA256["role10_row"]


def test_semantic_source_joins_are_explicit_and_complete(
    clean_replays: tuple[dict[str, object], dict[str, object], bytes],
) -> None:
    _, receipt, _ = clean_replays
    joins = receipt["semantic_source_joins"]
    assert joins == {
        "authority_hash_edges_equal": True,
        "configuration_partition_geometry_equal": True,
        "configuration_reference_parameters_equal": True,
        "contact_radius_period_equal": True,
        "coordinate_order_equal": True,
        "profile_basis_equal": True,
        "symbolic_control_source_contains_no_values_or_budget": True,
    }
