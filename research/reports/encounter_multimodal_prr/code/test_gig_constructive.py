from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import validate_gig_constructive as pilot


@pytest.fixture(scope="module")
def payload() -> dict:
    return pilot.build_payload(scan_points=pilot.SCAN_POINTS)


def test_normalized_channels_and_analytic_derivatives_through_fourth() -> None:
    spec = pilot.make_gig_specification(
        pilot.CUSP_TARGET_MODES,
        b=pilot.CUSP_B,
        p=pilot.CUSP_P,
        weights=(1.0, 1.0, 1.0),
    )
    normalization = pilot._normalization_audit(spec)
    crosscheck = pilot._derivative_crosscheck(spec)

    assert normalization["passed"]
    assert normalization["maximum_absolute_normalization_error"] < 2.0e-12
    assert crosscheck["passed"]
    assert crosscheck["orders"] == [0, 1, 2, 3, 4]
    assert crosscheck["maximum_error"] < 1.0e-10


def test_d2_three_channel_cusp_candidate(payload: dict) -> None:
    cusp = payload["cusp_candidate"]
    transversality = cusp["unfolding_transversality"]

    assert cusp["status"] == "PASS"
    assert cusp["fixture_role"] == "canonical_preliminary_result"
    assert cusp["b"] == pytest.approx(0.01, abs=0.0)
    assert cusp["target_isolated_modes"] == [0.35, 1.0, 1.5]
    assert cusp["cusp_time"] == pytest.approx(
        0.5728883706366298,
        abs=2.0e-9,
    )
    assert cusp["weights"] == pytest.approx(
        [0.2769343322238386, 0.3200588141402115, 0.4030068536359499],
        abs=2.0e-9,
    )
    assert np.all(np.asarray(cusp["weights"]) > 0.0)
    assert sum(cusp["weights"]) == pytest.approx(1.0, abs=2.0e-14)
    assert max(cusp["scaled_derivative_residuals"].values()) < 1.0e-10
    assert cusp["scaled_fourth_derivative"] == pytest.approx(
        -13.6105363,
        abs=2.0e-7,
    )
    assert transversality["rank"] == 2
    assert transversality["row_angle_normalized_determinant"] == pytest.approx(
        0.9632674,
        abs=2.0e-7,
    )
    assert transversality["row_angle_sine_magnitude"] == pytest.approx(
        0.9632674,
        abs=2.0e-7,
    )
    assert transversality["dimensionless_raw_matrix_svd_ratio"] > 0.5
    assert "scaled_unfolding_determinant" not in cusp
    assert all(cusp["gates"].values())


def test_b01_is_canonical_and_b1_is_only_a_robustness_case(payload: dict) -> None:
    canonical = payload["cusp_candidate"]
    robustness_cases = payload["cusp_robustness_cases"]

    assert canonical["b"] == pytest.approx(0.01, abs=0.0)
    assert len(robustness_cases) == 1
    robustness = robustness_cases[0]
    assert robustness["fixture_role"] == "robustness_case_not_canonical"
    assert robustness["b"] == pytest.approx(0.1, abs=0.0)
    assert robustness["cusp_time"] == pytest.approx(
        0.5688427124927922,
        abs=2.0e-9,
    )
    assert robustness["status"] == "PASS"
    assert all(robustness["gates"].values())


def test_well_separated_constructions_have_requested_extrema(
    payload: dict,
) -> None:
    cases = payload["well_separated_constructions"]

    assert [case["mode_count"] for case in cases] == [2, 3, 4, 5, 6]
    for case in cases:
        mode_count = case["mode_count"]
        kinds = [row["kind"] for row in case["roots"]]
        assert case["status"] == "PASS"
        assert len(kinds) == 2 * mode_count - 1
        assert kinds.count("maximum") == mode_count
        assert kinds.count("minimum") == mode_count - 1
        assert kinds == [
            "maximum" if index % 2 == 0 else "minimum" for index in range(2 * mode_count - 1)
        ]
        assert case["minimum_peak_to_adjacent_valley_ratio"] >= 1.5
        assert case["minimum_absolute_dimensionless_curvature"] >= 0.1
        assert case["maximum_scaled_root_residual"] <= 1.0e-7
        assert all(case["gates"].values())


def test_payload_is_fail_closed_and_does_not_overclaim(
    payload: dict,
    tmp_path: Path,
) -> None:
    output = tmp_path / "pilot.json"
    pilot._write_payload(output, payload)
    restored = json.loads(output.read_text(encoding="utf-8"))

    assert restored["status"] == "PASS"
    assert restored["summary"]["canonical_cusp_b"] == pytest.approx(0.01)
    assert restored["summary"]["robustness_cusp_cases_passed"]
    assert restored["summary"]["maximum_verified_mode_count"] == 6
    claim = restored["claim_scope"].lower()
    assert "screening only" in claim
    assert "not bounded-domain" in claim
    assert "continuum doi/robin" in claim
    assert restored["limitations"]
