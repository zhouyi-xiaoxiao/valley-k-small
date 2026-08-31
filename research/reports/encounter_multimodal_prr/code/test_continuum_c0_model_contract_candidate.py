from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_hex(record: dict[str, str]) -> Fraction:
    encoded = Fraction(record["exact"])
    assert encoded == Fraction.from_float(float.fromhex(record["binary64_hex"]))
    return encoded


def test_contract_is_result_blind_fail_closed_and_dimensionally_explicit() -> None:
    contract = _load(CONTRACT)
    assert contract["schema"] == "encounter_continuum_c0_model_contract_candidate_v1"
    assert contract["status"] == (
        "HOLD_C0_CANDIDATE_RESULT_BLIND_PENDING_INDEPENDENT_THEORY_AND_HASH_AUDIT"
    )
    assert contract["physical_dimension"] == 2
    assert contract["quotient_dimension"] == 3
    boundary = contract["claim_boundary"]
    assert boundary == {
        "c0a_operator_realization_proved": True,
        "complete_c0_independently_accepted": False,
        "c1_fixed_box_convergence_proved": False,
        "c2_quantitative_spatial_error_proved": False,
        "c3_derivative_box_error_proved": False,
        "continuum_stationary_topology_proved": False,
        "f0_complete": False,
        "positive_budget_scientific_values_read": False,
        "release_eligible": False,
    }
    units = {record["unit"] for record in contract["physical_parameters"].values()}
    assert units == {
        "length",
        "length_squared_per_time",
        "inverse_time",
        "inverse_time_times_longitudinal_measure",
    }


def test_frozen_sources_are_exact_and_controls_remain_opaque() -> None:
    contract = _load(CONTRACT)
    for record in contract["frozen_sources"].values():
        path = REPORT / record["path"]
        assert path.is_file()
        assert _sha256(path) == record["sha256"]
    controls = contract["control_contract"]
    control_path = REPORT / controls["opaque_result_blind_source_path"]
    assert _sha256(control_path) == controls["opaque_result_blind_source_sha256"]
    raw = CONTRACT.read_text(encoding="utf-8").lower()
    for forbidden in ("peak_time", "root_interval", "positive_budget_result", "basin_mass"):
        assert forbidden not in raw


def test_exact_parameters_satisfy_c0_geometry_and_reversible_identity() -> None:
    pars = _load(CONTRACT)["physical_parameters"]
    budget = _exact_hex(pars["B"])
    diffusion = _exact_hex(pars["D"])
    period = _exact_hex(pars["W"])
    radius = _exact_hex(pars["contact_radius_a"])
    stiffness = _exact_hex(pars["gamma"])
    _exact_hex(pars["zbar"])
    assert min(budget, diffusion, period, radius, stiffness) > 0
    assert 2 * radius < period
    # Dmat * grad(log pi) = b, coefficient by coefficient.
    assert diffusion / 2 * (-2 * stiffness / diffusion) == -stiffness
    assert 2 * diffusion * (-stiffness / (2 * diffusion)) == -stiffness
    assert 2 * diffusion * 0 == 0
    normalizer_without_pi = 2 * diffusion * period / stiffness
    assert normalizer_without_pi > 0
    assert math.isfinite(float(normalizer_without_pi))


def test_initial_and_killing_sources_match_the_continuum_contract() -> None:
    contract = _load(CONTRACT)
    initial = _load(REPORT / contract["initial_law"]["source_path"])
    killing = _load(REPORT / contract["frozen_sources"]["killing_geometry_source"]["path"])
    assert initial["physical_dimension"] == contract["physical_dimension"]
    assert initial["quotient_dimension"] == contract["quotient_dimension"]
    assert initial["analytic_total_mass_exact"] == "1/1"
    assert initial["scope"] == "physical_initial_law_only_no_control_no_budget"
    assert killing["physical_dimension"] == contract["physical_dimension"]
    assert killing["quotient_dimension"] == contract["quotient_dimension"]
    assert killing["support_basis"]["profile_count"] == 4
    assert killing["support_basis"]["analytic_integral_each"] == "1/1"
    assert killing["flags"]["contains_budget_value"] is False
    assert killing["flags"]["contains_control_values"] is False
    assert killing["flags"]["positive_budget_executed"] is False


def test_mesh_classes_order_box_nesting_and_identification_maps_are_fixed() -> None:
    contract = _load(CONTRACT)
    family = _load(REPORT / contract["mesh_contract"]["source_path"])
    assert family["configuration_count"] == contract["mesh_contract"]["configuration_count"]
    assert family["configuration_order"] == contract["mesh_contract"]["configuration_order"]
    assert set(family["axis_construction_contracts"]) == set(
        contract["mesh_contract"]["alignment_classes"]
    )
    rows = {row["label"]: row for row in family["configurations"]}

    def bounds(label: str, axis: str) -> tuple[float, float]:
        record = rows[label][axis]
        return (
            float.fromhex(record["lower_binary64_hex"]),
            float.fromhex(record["upper_binary64_hex"]),
        )

    base_m = bounds("O129/Base", "midpoint")
    plus_m = bounds("M+", "midpoint")
    base_r = bounds("O129/Base", "relative_parallel")
    plus_r = bounds("R+", "relative_parallel")
    assert plus_m[0] <= base_m[0] < base_m[1] <= plus_m[1]
    assert plus_r[0] <= base_r[0] < base_r[1] <= plus_r[1]
    assert bounds("MR+", "midpoint") == plus_m
    assert bounds("MR+", "relative_parallel") == plus_r
    assert bounds("MR+F", "midpoint") == plus_m
    assert bounds("MR+F", "relative_parallel") == plus_r
    maps = contract["finite_volume_identification"]
    assert maps["stationary_mass_gauge"] == "sum_i_pi_h_i=integral_Omega_L_pi_dx"
    assert "physical_volume_cell_average" in maps["killing_projection"]


def test_equation_and_boundary_contracts_exclude_reflecting_target_confusion() -> None:
    contract = _load(CONTRACT)
    assert contract["equation_contract"] == [
        "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.6a",
        "2.7", "2.7a", "2.8", "2.8a", "2.9", "2.10", "2.11", "2.12",
        "2.13", "2.14", "2.15", "2.16", "2.17",
    ]
    boundary = contract["boundary_conditions"]
    assert boundary["target_midpoint"].startswith("natural_decay")
    assert boundary["target_relative_parallel"].startswith("natural_decay")
    assert boundary["finite_box_midpoint"].endswith("approximant_only")
    assert boundary["finite_box_relative_parallel"].endswith("approximant_only")

