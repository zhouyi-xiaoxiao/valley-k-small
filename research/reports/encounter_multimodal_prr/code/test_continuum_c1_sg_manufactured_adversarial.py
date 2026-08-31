from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import continuum_c1_sg_manufactured as fixture
import gmpy2

REPORT = Path(__file__).resolve().parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c1_sg_manufactured_v2.json"


def _load() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _continuum_terms() -> tuple[gmpy2.mpfr, gmpy2.mpfr, gmpy2.mpfr, gmpy2.mpfr]:
    alpha = fixture._mp(fixture.STIFFNESS / fixture.DIFFUSION)
    mean = fixture._mp(fixture.MEAN)
    lower = fixture._mp(fixture.LOWER)
    upper = fixture._mp(fixture.UPPER)
    normalization = gmpy2.sqrt(alpha / gmpy2.const_pi())
    box_mass = normalization * fixture._gaussian_moments(
        lower - mean,
        upper - mean,
        alpha,
        0,
    )[0]
    return alpha, mean, normalization, box_mass


def _centre_density_error_for_potential_scale(scale: Fraction) -> gmpy2.mpfr:
    alpha, mean, normalization, box_mass = _continuum_terms()
    cells = 65
    step_fraction = (fixture.UPPER - fixture.LOWER) / cells
    step = fixture._mp(step_fraction)
    positions = [
        fixture._mp(fixture.LOWER + (index + Fraction(1, 2)) * step_fraction)
        for index in range(cells)
    ]
    raw_masses = [
        step * gmpy2.exp(-fixture._mp(scale) * alpha * (position - mean) ** 2)
        for position in positions
    ]
    gauge = box_mass / sum(raw_masses, gmpy2.mpfr(0))
    return max(
        abs(
            (gauge * mass / step)
            / (normalization * gmpy2.exp(-alpha * (position - mean) ** 2))
            - 1
        )
        for mass, position in zip(raw_masses, positions, strict=True)
    )


def test_wrong_potential_sign_and_scale_are_not_hidden_by_mass_gauge() -> None:
    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        sign_reversed = _centre_density_error_for_potential_scale(Fraction(-1))
        half_scaled = _centre_density_error_for_potential_scale(Fraction(1, 2))
        double_scaled = _centre_density_error_for_potential_scale(Fraction(2))
    assert sign_reversed > gmpy2.mpfr("1e20")
    assert half_scaled > gmpy2.mpfr("1e10")
    assert double_scaled > gmpy2.mpfr("0.9")


def test_swapped_bernoulli_directions_break_exact_detailed_balance() -> None:
    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        cells = 17
        alpha, mean, _normalization, _box_mass = _continuum_terms()
        step = fixture._mp((fixture.UPPER - fixture.LOWER) / cells)
        diffusion_axis = fixture._mp(fixture.DIFFUSION / 2)
        positions = [
            fixture._mp(
                fixture.LOWER
                + (index + Fraction(1, 2)) * (fixture.UPPER - fixture.LOWER) / cells
            )
            for index in range(cells)
        ]
        potentials = [alpha * (position - mean) ** 2 for position in positions]
        left = 7
        delta = potentials[left + 1] - potentials[left]
        left_mass = step * gmpy2.exp(-potentials[left])
        right_mass = step * gmpy2.exp(-potentials[left + 1])
        wrong_forward = diffusion_axis / step**2 * fixture._bernoulli(-delta)
        wrong_backward = diffusion_axis / step**2 * fixture._bernoulli(delta)
        lhs = left_mass * wrong_forward
        rhs = right_mass * wrong_backward
        relative_gap = abs(lhs - rhs) / max(abs(lhs), abs(rhs))
    assert relative_gap > gmpy2.mpfr("0.9")


def test_raw_or_unit_mass_normalization_is_not_the_declared_gauge() -> None:
    payload = _load()
    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        _alpha, _mean, _normalization, box_mass = _continuum_terms()
        assert box_mass < 1
    first = payload["rows"][0]
    gauge = float.fromhex(first["gauge_scale_hex"])
    exported_box_mass = float.fromhex(first["box_mass_hex"])
    assert gauge > 3.0
    assert exported_box_mass == 1.0
    assert exported_box_mass / gauge < 0.3


def test_point_sampling_is_not_the_weighted_cell_projection() -> None:
    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        cells = 65
        axis = fixture._axis(cells)
        alpha, mean, _normalization, _box_mass = _continuum_terms()
        index = 10
        cell_lower, cell_upper = axis.cell_segments[index][0]
        moments = fixture._gaussian_moments(
            fixture._mp(cell_lower) - mean,
            fixture._mp(cell_upper) - mean,
            alpha,
            2,
        )
        weighted_average_y_squared = moments[2] / moments[0]
        centre_sample_y_squared = (fixture._mp(axis.positions[index]) - mean) ** 2
    assert abs(weighted_average_y_squared - centre_sample_y_squared) > gmpy2.mpfr("1e-3")


def test_projection_denominators_are_numerically_distinguishable() -> None:
    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        cells = 65
        axis = fixture._axis(cells)
        alpha, mean, normalization, box_mass = _continuum_terms()
        step = fixture._mp((fixture.UPPER - fixture.LOWER) / cells)
        raw_masses = [
            step * gmpy2.exp(-alpha * (fixture._mp(position) - mean) ** 2)
            for position in axis.positions
        ]
        gauge = box_mass / sum(raw_masses, gmpy2.mpfr(0))
        index = 10
        cell_lower, cell_upper = axis.cell_segments[index][0]
        cell_mass = normalization * fixture._gaussian_moments(
            fixture._mp(cell_lower) - mean,
            fixture._mp(cell_upper) - mean,
            alpha,
            0,
        )[0]
        discrete_mass = gauge * raw_masses[index]
        adjoint_projection_of_one = cell_mass / discrete_mass
        cell_mass_residual = abs(discrete_mass * adjoint_projection_of_one - cell_mass)
    assert abs(adjoint_projection_of_one - 1) > gmpy2.mpfr("0.1")
    assert cell_mass_residual < gmpy2.mpfr(2) ** -200
    assert _load()["fixture_projection_map"]["denominator"] == "integral_C_i_pi"


def test_axis_diffusion_factor_two_mutation_is_visible() -> None:
    row = _load()["rows"][-1]
    observed = float.fromhex(row["functions"]["linear"]["continuum_energy_hex"])
    box_mass = float.fromhex(row["box_mass_hex"])
    correct = float(fixture.DIFFUSION / 2) * box_mass
    wrong = float(fixture.DIFFUSION) * box_mass
    assert observed == correct
    assert wrong == 2 * observed


def test_edge_factor_and_reflecting_wrap_mutations_fail_flat_exact_value() -> None:
    row = _load()["flat_boundary_order_sentinel"]["rows"][1]
    expected = Fraction(row["discrete_energy_exact"])
    step = Fraction(row["h_exact"])
    conductance = Fraction(row["gauged_conductance_exact"])
    assert expected == Fraction(7, 8)
    assert 2 * expected != expected
    assert expected / 2 != expected
    left_centre = Fraction(-1) + step / 2
    right_centre = Fraction(1) - step / 2
    erroneous_wrap_energy = conductance * (right_centre - left_centre) ** 2
    assert expected + erroneous_wrap_energy != expected


def test_attack_layer_cannot_promote_scope_or_function_coverage() -> None:
    payload = _load()
    assert len(fixture.POLYNOMIALS) >= 5
    assert any(max(polynomial) >= 2 for polynomial in fixture.POLYNOMIALS.values())
    assert payload["alignment_scope"]["tensor_alignment_vector_frozen"] is False
    assert payload["claim_boundary"]["c1_mosco_proved"] is False
    assert payload["claim_boundary"]["production_centre_mosco_proved"] is False
    assert payload["theory_boundary"]["complete_c1_from_finite_tables"] is False
