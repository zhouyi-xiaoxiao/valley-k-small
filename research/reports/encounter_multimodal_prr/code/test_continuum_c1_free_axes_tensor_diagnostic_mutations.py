from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import continuum_c1_free_axes_tensor_diagnostic as fixture
import gmpy2
import rate_defined_tensor_f0 as f0

REPORT = Path(__file__).resolve().parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c1_free_axes_tensor_diagnostic_v1.json"


def _load() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_deleting_vertex_half_volume_loses_the_exact_factor_two_endpoint_rate() -> None:
    spec = fixture.VERTEX_SPEC
    intervals = 16
    step = (spec["upper"] - spec["lower"]) / intervals
    positions = tuple(spec["lower"] + index * step for index in range(intervals + 1))
    delta = fixture._mp(
        fixture._potential(spec, positions[1]) - fixture._potential(spec, positions[0])
    )
    reference_equal_volume_rate = (
        fixture._mp(spec["diffusion"]) / fixture._mp(step) ** 2 * fixture._bernoulli(delta)
    )
    correct_half_volume_rate = (
        fixture._mp(spec["diffusion"])
        / (fixture._mp(step / 2) * fixture._mp(step))
        * fixture._bernoulli(delta)
    )
    mutated_full_volume_rate = (
        fixture._mp(spec["diffusion"])
        / (fixture._mp(step) * fixture._mp(step))
        * fixture._bernoulli(delta)
    )
    assert correct_half_volume_rate / reference_equal_volume_rate == 2
    assert mutated_full_volume_rate / reference_equal_volume_rate == 1
    published = _load()["vertex_dual_ou"]["rows"][0]
    assert float.fromhex(published["endpoint_outgoing_rate_factor_left_hex"]) == 2.0


def test_full_endpoint_volume_mutation_breaks_flat_vertex_cell_mass_map() -> None:
    width = Fraction(3)
    intervals = 12
    step = width / intervals
    correct_volumes = (step / 2, *(step for _ in range(intervals - 1)), step / 2)
    mutated_volumes = (step,) * (intervals + 1)
    correct_gauge = width / sum(correct_volumes, Fraction(0))
    mutated_gauge = width / sum(mutated_volumes, Fraction(0))
    physical_dual_masses = correct_volumes
    correct_rhos = [
        physical / (correct_gauge * raw)
        for physical, raw in zip(physical_dual_masses, correct_volumes, strict=True)
    ]
    mutated_rhos = [
        physical / (mutated_gauge * raw)
        for physical, raw in zip(physical_dual_masses, mutated_volumes, strict=True)
    ]
    assert correct_gauge == 1
    assert all(rho == 1 for rho in correct_rhos)
    assert abs(mutated_rhos[0] - 1) > Fraction(2, 5)
    assert abs(mutated_rhos[-1] - 1) > Fraction(2, 5)


def test_swapping_vertex_bernoulli_directions_breaks_detailed_balance() -> None:
    spec = fixture.VERTEX_SPEC
    intervals = 16
    step = (spec["upper"] - spec["lower"]) / intervals
    positions = tuple(spec["lower"] + index * step for index in range(intervals + 1))
    left = 1
    right = left + 1
    potentials = [fixture._mp(fixture._potential(spec, position)) for position in positions]
    volumes = [step / 2, *(step for _ in range(intervals - 1)), step / 2]
    left_mass = fixture._mp(volumes[left]) * gmpy2.exp(-potentials[left])
    right_mass = fixture._mp(volumes[right]) * gmpy2.exp(-potentials[right])
    delta = potentials[right] - potentials[left]
    wrong_forward = (
        fixture._mp(spec["diffusion"])
        / (fixture._mp(volumes[left]) * fixture._mp(step))
        * fixture._bernoulli(-delta)
    )
    wrong_backward = (
        fixture._mp(spec["diffusion"])
        / (fixture._mp(volumes[right]) * fixture._mp(step))
        * fixture._bernoulli(delta)
    )
    lhs = left_mass * wrong_forward
    rhs = right_mass * wrong_backward
    assert abs(lhs - rhs) / max(abs(lhs), abs(rhs)) > gmpy2.mpfr("0.05")


def test_omitting_one_vertex_edge_turns_smooth_form_recovery_first_order() -> None:
    spec = fixture.VERTEX_SPEC

    def mutated_error(intervals: int) -> gmpy2.mpfr:
        row = fixture._reflecting_row(spec, intervals, vertex_dual=True)
        correct = fixture._mp(Fraction.from_float(float.fromhex(row["probe_discrete_form_hex"])))
        continuum = fixture._mp(
            Fraction.from_float(float.fromhex(row["probe_continuum_form_hex"]))
        )
        step = (spec["upper"] - spec["lower"]) / intervals
        positions = tuple(spec["lower"] + index * step for index in range(intervals + 1))
        axis = f0.build_reflecting_sg_axis(
            "mutated_missing_edge",
            positions,
            tuple(fixture._potential(spec, position) for position in positions),
            spec["diffusion"],
            precision_bits=fixture.PRECISION_BITS,
        )
        alpha = fixture._mp(spec["gamma"] / (2 * spec["diffusion"]))
        mean = fixture._mp(spec["mean"])
        raw = [
            fixture._mp(volume)
            * gmpy2.exp(-fixture._mp(fixture._potential(spec, position)))
            for volume, position in zip(axis.cell_volumes, axis.positions, strict=True)
        ]
        box_mass = fixture._gaussian_moments(
            fixture._mp(spec["lower"]) - mean,
            fixture._mp(spec["upper"]) - mean,
            alpha,
            0,
        )[0]
        gauge = box_mass / sum(raw, gmpy2.mpfr(0))
        left = intervals // 2
        delta = fixture._mp(
            fixture._potential(spec, positions[left + 1])
            - fixture._potential(spec, positions[left])
        )
        omitted_rate = (
            fixture._mp(spec["diffusion"])
            / (fixture._mp(axis.cell_volumes[left]) * fixture._mp(step))
            * fixture._bernoulli(delta)
        )
        omitted_conductance = gauge * raw[left] * omitted_rate
        omitted_jump = fixture._mp(
            fixture._vertex_probe_value(positions[left + 1])
            - fixture._vertex_probe_value(positions[left])
        )
        mutated = correct - omitted_conductance * omitted_jump**2
        return abs(mutated - continuum) / continuum

    with gmpy2.context(gmpy2.get_context(), precision=fixture.PRECISION_BITS):
        coarse = mutated_error(256)
        fine = mutated_error(512)
    observed = gmpy2.log(coarse / fine) / gmpy2.log(2)
    assert gmpy2.mpfr("0.9") < observed < gmpy2.mpfr("1.1")


def test_unnormalized_periodic_mass_mutation_sums_to_width_not_one() -> None:
    intervals = 32
    step = fixture.PERIODIC_WIDTH / intervals
    correct_mass = step / fixture.PERIODIC_WIDTH
    mutated_mass = step
    assert intervals * correct_mass == 1
    assert intervals * mutated_mass == fixture.PERIODIC_WIDTH
    assert intervals * mutated_mass != 1


def test_dropping_periodic_wrap_edge_changes_fourier_form() -> None:
    intervals = 32
    axis = f0.build_periodic_diffusion_axis(
        "wrap_edge_attack",
        intervals,
        fixture.PERIODIC_WIDTH,
        fixture.PERIODIC_DIFFUSION,
    )
    step = fixture.PERIODIC_WIDTH / intervals
    conductance = fixture._mp(
        (step / fixture.PERIODIC_WIDTH) * fixture.PERIODIC_DIFFUSION / step**2
    )
    angle = 2 * gmpy2.const_pi() * fixture.PERIODIC_MODE / fixture._mp(
        fixture.PERIODIC_WIDTH
    )
    cosine = [gmpy2.cos(angle * fixture._mp(position)) for position in axis.positions]
    sine = [gmpy2.sin(angle * fixture._mp(position)) for position in axis.positions]

    def energy(values: list[gmpy2.mpfr], edges: int) -> gmpy2.mpfr:
        return sum(
            (
                conductance * (values[(left + 1) % intervals] - values[left]) ** 2
                for left in range(edges)
            ),
            gmpy2.mpfr(0),
        )

    correct = energy(cosine, intervals) + energy(sine, intervals)
    mutated = energy(cosine, intervals - 1) + energy(sine, intervals - 1)
    observed_missing_fraction = abs(correct - mutated) / correct
    assert abs(observed_missing_fraction - gmpy2.mpfr(1) / intervals) < gmpy2.mpfr(
        "1e-14"
    )


def test_erasing_half_shift_removes_the_required_wrapped_cell() -> None:
    shifted = f0.build_periodic_diffusion_axis(
        "correct_half_shift",
        16,
        fixture.PERIODIC_WIDTH,
        fixture.PERIODIC_DIFFUSION,
        half_cell_shift=True,
    )
    mutated = f0.build_periodic_diffusion_axis(
        "mutated_shift_erased",
        16,
        fixture.PERIODIC_WIDTH,
        fixture.PERIODIC_DIFFUSION,
        half_cell_shift=False,
    )
    assert sum(len(segments) == 2 for segments in shifted.cell_segments) == 1
    assert sum(len(segments) == 2 for segments in mutated.cell_segments) == 0
    assert shifted.periodic_shift != mutated.periodic_shift


def test_extra_half_in_periodic_conductance_halves_fourier_form() -> None:
    row = _load()["periodic"]["rows"][-2]
    correct = float.fromhex(row["combined_fourier_discrete_form_hex"])
    mutated = correct / 2
    continuum = float.fromhex(row["combined_fourier_continuum_form_hex"])
    assert abs(correct / continuum - 1) < 0.01
    assert abs(mutated / continuum - 1) > 0.49


def test_missing_tensor_cross_mass_factors_is_detected_exactly() -> None:
    sentinel = _load()["tensor_factorization"]["small_exact_streaming_sentinel"]
    norms = [Fraction(value) for value in sentinel["axis_norms_exact"]]
    energies = [Fraction(value) for value in sentinel["axis_energies_exact"]]
    correct_norm, correct_energy = fixture.factorized_tensor_quantities(norms, energies)
    mutated_energy = sum(energies, Fraction(0))
    assert correct_norm == Fraction(sentinel["direct_streaming_norm_exact"])
    assert correct_energy == Fraction(sentinel["direct_streaming_energy_exact"])
    assert mutated_energy != correct_energy


def test_factorization_rejects_non_three_axis_inputs() -> None:
    try:
        fixture.factorized_tensor_quantities((Fraction(1), Fraction(1)), (Fraction(1),) * 2)
    except ValueError as error:
        assert "three axis" in str(error)
    else:
        raise AssertionError("two-axis mutation was silently accepted")
