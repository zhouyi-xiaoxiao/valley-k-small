"""Round-131 independent attacks, inverted after the selector-v2 repair.

The original defect-reproducing bytes remain frozen under ``audits/frozen_tests``.
No test in this module executes F1, a positive-budget semigroup, or Monte Carlo.
"""

from __future__ import annotations

import copy
import hashlib
import math
import random
import struct
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import f1_to_f2_common_observable_selector_v2 as selector
import pytest

EXPECTED_HOLD_ORDER = (
    "HOLD_DECODE_UTF8",
    "HOLD_DECODE_JSON",
    "HOLD_DUPLICATE_KEY",
    "HOLD_CANONICAL_JSON",
    "HOLD_SCHEMA",
    "HOLD_SCHEMA_NULLABILITY",
    "HOLD_DEPENDENCY_HASH",
    "HOLD_NUMERIC_LEAF",
    "HOLD_F1A",
    "HOLD_SELECTOR_INPUT",
    "HOLD_ROLE_HULL_OVERLAP",
    "HOLD_COMMON_CUT",
    "HOLD_ROLE_WINDOW",
    "HOLD_F1B_STATE_COVERAGE",
    "HOLD_REFERENCE_POINT_LAW",
    "HOLD_CUT_UNCERTAINTY",
    "HOLD_COMMON_OBSERVABLE",
    "HOLD_DETERMINISTIC_ENVELOPE",
    "HOLD_TAU_ZERO",
    "HOLD_BASIN_FLOOR",
    "HOLD_CONTRAST_NONPOSITIVE",
    "HOLD_CONTRAST_PLANNING_INCOHERENT",
    "HOLD_CONTRAST_SPLIT",
    "HOLD_SPECIAL_FUNCTION_DAG",
    "HOLD_SPECIAL_FUNCTION_AMBIGUOUS",
    "HOLD_POWER_BOUNDARY",
    "HOLD_N_CAP",
    "HOLD_RNG_SPEC",
    "HOLD_TEST_KEY_SET",
    "HOLD_SEED_COLLISION",
    "HOLD_NO_REFIT_VIOLATION",
    "HOLD_APPEND_ONLY",
    "HOLD_SELECTOR_REPLICA_MISMATCH",
)

DEPENDENCY_NAMES = (
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


def _dependencies() -> dict[str, str]:
    dependencies = {name: "0" * 64 for name in DEPENDENCY_NAMES}
    dependencies.update(
        {
            "central_projection_spec_sha256": selector.EXPECTED_CENTRAL_PROJECTION_SHA256,
            "philox_spec_sha256": selector.EXPECTED_PHILOX_SPEC_SHA256,
            "selector_runtime_sha256": selector.EXPECTED_RUNTIME_SPEC_SHA256,
            "selector_schema_sha256": selector.sha256_file(selector.SCHEMA_PATH),
            "test_key_set_sha256": selector.EXPECTED_TEST_KEY_SET_SHA256,
        }
    )
    return dependencies


def _hold_core(*reasons: str, schema_version: int | float = 2) -> dict[str, object]:
    hold = selector.hold_payload(reasons)
    return {
        "authorized_scientific_command": None,
        "dependencies": _dependencies(),
        "hold": hold["hold"],
        "schema_version": schema_version,
        "selection": None,
        "stage": "f1_common_observable_selection_v2",
        "stage_rows": hold["stage_rows"],
        "status": hold["status"],
    }


def _exact_pmf_integer_prefix(n: int, probability: Fraction) -> tuple[list[int], int]:
    """Return exact binomial prefix numerators over one common denominator."""

    numerator = probability.numerator
    denominator_base = probability.denominator
    complement = denominator_base - numerator
    assert 0 < numerator < denominator_base
    denominator = denominator_base**n
    term = complement**n
    prefix = [0, term]
    for k in range(n):
        dividend = term * (n - k) * numerator
        divisor = (k + 1) * complement
        quotient, remainder = divmod(dividend, divisor)
        assert remainder == 0
        term = quotient
        prefix.append(prefix[-1] + term)
    assert prefix[-1] == denominator
    return prefix, denominator


def _exact_range_from_prefix(
    prefix: list[int], denominator: int, lower: int, upper: int
) -> Fraction:
    return Fraction(prefix[upper + 1] - prefix[lower], denominator)


def _decode_mpfr_endpoint(payload: dict[str, object]) -> Fraction:
    mantissa_text = str(payload["mantissa_hex"])
    if mantissa_text == "0":
        return Fraction(0)
    sign = -1 if mantissa_text.startswith("-") else 1
    digits = mantissa_text.removeprefix("-")
    mantissa = sign * int(digits, 16)
    exponent = int(payload["exponent_base16"]) - len(digits)
    if exponent >= 0:
        return Fraction(mantissa * 16**exponent)
    return Fraction(mantissa, 16 ** (-exponent))


def _independent_high_precision_tail(
    n: int,
    probability: Fraction,
    boundary: int,
    side: str,
    *,
    precision: int = 512,
) -> selector.gmpy2.mpfr:
    """Independent noncertifying oracle: exact comb + MPFR power recurrence.

    This deliberately does not use the selector's log-gamma boundary PMF,
    interval operations, range decomposition, or geometric remainder routine.
    The 2^-400 cutoff is far below the roughly 1e-5 neighbour separation in
    the N=8,000,000 threshold fixture.
    """

    gmpy2 = selector.gmpy2
    with gmpy2.context(precision=precision, round=gmpy2.RoundToNearest):
        p_value = gmpy2.mpfr(probability.numerator) / probability.denominator
        q_value = 1 - p_value
        term = gmpy2.mpfr(gmpy2.comb(n, boundary)) * p_value**boundary * q_value ** (n - boundary)
        total = +term
        k = boundary
        cutoff = gmpy2.exp2(-400)
        while (side == "upper" and k < n) or (side == "lower" and k > 0):
            if side == "upper":
                ratio = (gmpy2.mpfr(n - k) * p_value) / (gmpy2.mpfr(k + 1) * q_value)
                k += 1
            elif side == "lower":
                ratio = (gmpy2.mpfr(k) * q_value) / (gmpy2.mpfr(n - k + 1) * p_value)
                k -= 1
            else:
                raise ValueError("unknown tail side")
            term *= ratio
            total += term
            if ratio < 1 and term < cutoff:
                break
        return +total


def _state_blob(intervals: tuple[tuple[float, float], ...]) -> bytes:
    payload = bytearray(selector.STATE_BALL_MAGIC)
    payload.extend(struct.pack(">I", len(intervals)))
    for lower, upper in intervals:
        payload.extend(struct.pack(">d", lower))
        payload.extend(struct.pack(">d", upper))
    return bytes(payload)


def _registry_bytes(
    rows: list[dict[str, object]], *, schema_version: int | float = 1
) -> tuple[bytes, str]:
    payload = {"schema_version": schema_version, "states": rows}
    raw = selector.canonical_json_bytes(payload)
    return raw, hashlib.sha256(raw).hexdigest()


def _registry_row(time: str, blob: bytes, lower: float, upper: float) -> dict[str, object]:
    return {
        "configuration": selector.REFERENCE_CONFIGURATION,
        "state_blob_sha256": hashlib.sha256(blob).hexdigest(),
        "survival_interval": [lower.hex(), upper.hex()],
        "time": time,
    }


def test_round131_loggamma_and_boundary_pmf_against_independent_oracles() -> None:
    gmpy2 = selector.gmpy2
    for integer in (1, 2, 3, 4, 7, 17, 64, 127, 200, 1000):
        interval = selector._mp_lgamma_integer(integer, 256)
        with gmpy2.context(precision=2048, round=gmpy2.RoundToNearest):
            alternate = gmpy2.log(gmpy2.mpz(gmpy2.fac(integer - 1)))
        assert interval.lower <= alternate <= interval.upper

    fixtures = (
        (3, Fraction(1, 7), 1),
        (17, Fraction(2, 5), 8),
        (127, Fraction(1, 17), 11),
        (1000, Fraction(16, 17), 970),
        (2000, Fraction(1, 257), 50),
        (2000, Fraction(128, 257), 999),
    )
    for n, probability, k in fixtures:
        interval = selector._mp_binomial_boundary_pmf(n, probability, k, 256)
        exact = Fraction(math.comb(n, k)) * probability**k * (1 - probability) ** (n - k)
        lower, upper = interval.exact_fraction_pair()
        assert lower <= exact <= upper

    with pytest.raises(selector.SelectorError) as too_wide:
        selector._mp_lgamma_integer((1 << 256) + 1, 256)
    assert too_wide.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


@pytest.mark.parametrize(
    ("n", "probability", "boundary", "side"),
    (
        (1000, Fraction(1, 200), 40, "upper"),
        (1000, Fraction(199, 200), 960, "lower"),
        (600, Fraction(1, 20), 85, "upper"),
        (600, Fraction(19, 20), 515, "lower"),
    ),
)
def test_round131_ratio_monotonicity_and_geometric_remainder(
    n: int, probability: Fraction, boundary: int, side: str
) -> None:
    prefix, denominator = _exact_pmf_integer_prefix(n, probability)
    interval, trace = selector._mp_binomial_tail(n, probability, boundary, side, 256)
    assert not trace["exact_endpoint"]
    terms_summed = int(trace["terms_summed"])

    if side == "upper":
        exact_tail = _exact_range_from_prefix(prefix, denominator, boundary, n)
        last_included = boundary + terms_summed - 1
        exact_remainder = _exact_range_from_prefix(prefix, denominator, last_included + 1, n)
        ratios = [
            Fraction(
                (n - k) * probability.numerator,
                (k + 1) * (probability.denominator - probability.numerator),
            )
            for k in range(boundary, last_included + 1)
            if k < n
        ]
        next_ratio = ratios[-1]
    else:
        exact_tail = _exact_range_from_prefix(prefix, denominator, 0, boundary)
        last_included = boundary - terms_summed + 1
        exact_remainder = (
            _exact_range_from_prefix(prefix, denominator, 0, last_included - 1)
            if last_included > 0
            else Fraction(0)
        )
        ratios = [
            Fraction(
                k * (probability.denominator - probability.numerator),
                (n - k + 1) * probability.numerator,
            )
            for k in range(boundary, last_included - 1, -1)
            if k > 0
        ]
        next_ratio = ratios[-1]

    assert all(right <= left for left, right in zip(ratios, ratios[1:], strict=False))
    assert next_ratio < 1
    last_term = Fraction(prefix[last_included + 1] - prefix[last_included], denominator)
    independent_geometric_bound = last_term * next_ratio / (1 - next_ratio)
    assert exact_remainder <= independent_geometric_bound

    remainder_payload = trace["remainder_enclosure"]
    traced_lower = _decode_mpfr_endpoint(remainder_payload["lower"])
    traced_upper = _decode_mpfr_endpoint(remainder_payload["upper"])
    assert traced_lower == 0
    assert exact_remainder <= traced_upper
    assert independent_geometric_bound <= traced_upper

    observed_lower, observed_upper = interval.exact_fraction_pair()
    assert observed_lower <= exact_tail <= observed_upper


def test_round131_exhaustive_small_n_range_decomposition() -> None:
    directions = set()
    cases = 0
    probabilities = (
        Fraction(1, 17),
        Fraction(1, 7),
        Fraction(2, 5),
        Fraction(1, 2),
        Fraction(6, 7),
        Fraction(16, 17),
    )
    for n in range(20):
        for probability in probabilities:
            prefix, denominator = _exact_pmf_integer_prefix(n, probability)
            for lower in range(n + 1):
                for upper in range(lower, n + 1):
                    exact = _exact_range_from_prefix(prefix, denominator, lower, upper)
                    interval, trace = selector._mp_binomial_range_in_process(
                        n, probability, lower, upper, 256
                    )
                    observed_lower, observed_upper = interval.exact_fraction_pair()
                    assert observed_lower <= exact <= observed_upper
                    directions.add(trace["direction"])
                    cases += 1
    assert cases == 9240
    assert directions == {
        "complement_of_two_tails",
        "difference_of_lower_tails",
        "difference_of_upper_tails",
        "full_support",
        "lower_tail",
        "upper_tail",
    }


def test_round131_seeded_random_medium_n_exact_ranges_and_precision_nesting() -> None:
    rng = random.Random(0x131)
    directions = set()
    for _case in range(72):
        n = rng.randint(75, 2500)
        denominator_base = rng.choice((7, 11, 17, 31, 101, 257))
        probability = Fraction(rng.randint(1, denominator_base - 1), denominator_base)
        lower = rng.randint(0, n)
        upper = rng.randint(lower, n)
        prefix, denominator = _exact_pmf_integer_prefix(n, probability)
        exact = _exact_range_from_prefix(prefix, denominator, lower, upper)
        outer, trace = selector._mp_binomial_range_in_process(n, probability, lower, upper, 256)
        inner, _ = selector._mp_binomial_range_in_process(n, probability, lower, upper, 512)
        outer_lower, outer_upper = outer.exact_fraction_pair()
        inner_lower, inner_upper = inner.exact_fraction_pair()
        assert outer_lower <= exact <= outer_upper
        assert inner_lower <= exact <= inner_upper
        assert outer_lower <= inner_lower <= inner_upper <= outer_upper
        directions.add(trace["direction"])
    assert {
        "complement_of_two_tails",
        "difference_of_lower_tails",
        "difference_of_upper_tails",
    } <= directions


def test_round131_n8m_cp_performance_and_independent_neighbour_oracle() -> None:
    n = 8_000_000
    alpha = Fraction(1, 800)
    selector_started = perf_counter()
    accepted = selector.cp_acceptance_set(n, Fraction(1, 200), Fraction(3, 200), alpha)
    selector_elapsed = perf_counter() - selector_started
    assert accepted == (40_646, 118_891)
    assert selector_elapsed < 20

    oracle_started = perf_counter()
    lower_left = _independent_high_precision_tail(n, Fraction(1, 200), accepted[0] - 1, "upper")
    lower_right = _independent_high_precision_tail(n, Fraction(1, 200), accepted[0], "upper")
    upper_left = _independent_high_precision_tail(n, Fraction(3, 200), accepted[1], "lower")
    upper_right = _independent_high_precision_tail(n, Fraction(3, 200), accepted[1] + 1, "lower")
    oracle_elapsed = perf_counter() - oracle_started
    with selector.gmpy2.context(precision=512, round=selector.gmpy2.RoundToNearest):
        contact = selector.gmpy2.mpfr((alpha / 2).numerator) / (alpha / 2).denominator
    assert lower_left > contact > lower_right
    assert upper_left < contact < upper_right
    assert oracle_elapsed < 20
    print(
        "Round131 N=8,000,000: "
        f"selector={selector_elapsed:.6f}s independent_oracle={oracle_elapsed:.6f}s"
    )


def test_round131_repaired_n8m_repeated_call_rss_is_bounded() -> None:
    """One hundred identical calls plus distinct requests keep parent RSS bounded."""

    script = f"""
from fractions import Fraction
import os
import subprocess
import sys
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector

def rss_kib():
    return int(subprocess.check_output(
        ['/bin/ps', '-o', 'rss=', '-p', str(os.getpid())], text=True
    ))

selector._isolated_cp_acceptance_set.cache_clear()
values = [rss_kib()]
for _index in range(100):
    assert selector.cp_acceptance_set(
        8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800)
    ) == (40_646, 118_891)
values.append(rss_kib())
for n in (7_999_996, 7_999_997, 7_999_998, 7_999_999):
    result = selector.cp_acceptance_set(
        n, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800)
    )
    assert result is not None and result[0] < result[1]
    values.append(rss_kib())
identity = selector._cp_worker_identity()
_result, peak = selector._isolated_cp_acceptance_set(
    8_000_000, 1, 200, 3, 200, 1, 800, *identity, os.getpid()
)
print(' '.join(map(str, (*values, peak))))
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    values = tuple(int(value) for value in completed.stdout.split())
    assert len(values) == 7
    rss_kib, worker_peak = values[:-1], values[-1]
    assert max(rss_kib) - min(rss_kib) < 32_768
    assert 0 < worker_peak <= selector.CP_WORKER_PEAK_RSS_CAP_BYTES
    print(f"Round131 repaired parent RSS KiB: {rss_kib}; child peak bytes: {worker_peak}")


def test_round131_schema_dependency_digest_and_precedence_contract() -> None:
    dependencies = _dependencies()
    core = _hold_core("HOLD_F1A")
    envelope = selector.build_selector_envelope(core)
    raw = selector.canonical_json_bytes(envelope)
    assert (
        selector.validate_selector_envelope_bytes(raw, expected_dependencies=dependencies)
        == envelope
    )
    assert (
        envelope["canonical_payload_sha256"]
        == hashlib.sha256(selector.canonical_json_bytes(core)).hexdigest()
    )

    stale = copy.deepcopy(core)
    stale["dependencies"]["f1_manifest_sha256"] = "1" * 64
    stale_envelope = selector.build_selector_envelope(stale)
    with pytest.raises(selector.SelectorError) as stale_error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(stale_envelope),
            expected_dependencies=dependencies,
        )
    assert stale_error.value.reason == "HOLD_DEPENDENCY_HASH"

    # Even if an untrusted caller changes its expected mapping too, package
    # edges remain tied to their local pinned bytes.
    forged = copy.deepcopy(core)
    forged["dependencies"]["philox_spec_sha256"] = "2" * 64
    forged_expected = dict(dependencies)
    forged_expected["philox_spec_sha256"] = "2" * 64
    with pytest.raises(selector.SelectorError) as package_error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(selector.build_selector_envelope(forged)),
            expected_dependencies=forged_expected,
        )
    assert package_error.value.reason == "HOLD_DEPENDENCY_HASH"

    schema_first = copy.deepcopy(stale)
    schema_first["authorized_scientific_command"] = "forbidden"
    with pytest.raises(selector.SelectorError) as schema_error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(selector.build_selector_envelope(schema_first)),
            expected_dependencies=dependencies,
        )
    assert schema_error.value.reason == "HOLD_SCHEMA"

    dependency_first = copy.deepcopy(stale)
    dependency_first["stage_rows"]["f1a"] = "PASS"
    with pytest.raises(selector.SelectorError) as dependency_error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(selector.build_selector_envelope(dependency_first)),
            expected_dependencies=dependencies,
        )
    assert dependency_error.value.reason == "HOLD_DEPENDENCY_HASH"


def test_round131_repaired_p0_integer_float_alias_is_rejected() -> None:
    """Byte-distinct 2.0 is rejected before schema or dependency semantics."""

    dependencies = _dependencies()
    integer_envelope = selector.build_selector_envelope(_hold_core("HOLD_F1A", schema_version=2))
    float_envelope = selector.build_selector_envelope(_hold_core("HOLD_F1A", schema_version=2.0))
    integer_raw = selector.canonical_json_bytes(integer_envelope)
    float_raw = selector.canonical_json_bytes(float_envelope)
    assert integer_raw != float_raw
    assert (
        integer_envelope["canonical_payload_sha256"] != float_envelope["canonical_payload_sha256"]
    )
    with pytest.raises(selector.SelectorError) as error:
        selector.validate_selector_envelope_bytes(float_raw, expected_dependencies=dependencies)
    assert error.value.reason == "HOLD_CANONICAL_JSON"


def test_round131_state_registry_blob_binding_and_canonical_path() -> None:
    blobs = (
        _state_blob(((0.375, 0.5), (0.25, 0.375))),
        _state_blob(((0.25, 0.375), (0.1875, 0.3125))),
        _state_blob(((0.03125, 0.09375), (0.0, 0.0625))),
    )
    rows = [
        _registry_row("1", blobs[0], 0.625, 0.875),
        _registry_row("2", blobs[1], 0.4375, 0.6875),
        _registry_row("100", blobs[2], 0.03125, 0.15625),
    ]
    registry_raw, registry_sha256 = _registry_bytes(rows)
    records = [
        {"state_blob": blob, "time": time}
        for blob, time in zip(blobs, ("1", "2", "100"), strict=True)
    ]
    path = selector.validate_reference_path(records, registry_raw, registry_sha256)
    assert path == (Fraction(3, 4), Fraction(9, 16), Fraction(3, 32))

    swapped = copy.deepcopy(records)
    swapped[0]["state_blob"] = blobs[1]
    with pytest.raises(selector.SelectorError) as swapped_error:
        selector.validate_reference_path(swapped, registry_raw, registry_sha256)
    assert swapped_error.value.reason == "HOLD_DEPENDENCY_HASH"

    self_reported = copy.deepcopy(records)
    self_reported[0]["state_blob_sha256"] = hashlib.sha256(blobs[0]).hexdigest()
    with pytest.raises(selector.SelectorError) as self_reported_error:
        selector.validate_reference_path(self_reported, registry_raw, registry_sha256)
    assert self_reported_error.value.reason == "HOLD_REFERENCE_POINT_LAW"

    reversed_blob = _state_blob(((0.75, 0.25),))
    reversed_rows = [_registry_row("1", reversed_blob, 0.0, 1.0)]
    reversed_raw, reversed_sha256 = _registry_bytes(reversed_rows)
    with pytest.raises(selector.SelectorError) as reversed_error:
        selector.validate_reference_path(
            [{"state_blob": reversed_blob, "time": "1"}],
            reversed_raw,
            reversed_sha256,
        )
    assert reversed_error.value.reason == "HOLD_REFERENCE_POINT_LAW"

    duplicate_rows = [rows[0], {**rows[1], "time": "1"}]
    duplicate_raw, duplicate_sha256 = _registry_bytes(duplicate_rows)
    with pytest.raises(selector.SelectorError) as duplicate_error:
        selector.load_pinned_state_registry(duplicate_raw, duplicate_sha256)
    assert duplicate_error.value.reason == "HOLD_F1B_STATE_COVERAGE"


def test_round131_repaired_registry_alias_and_type_return_holds() -> None:
    """Registry aliases and malformed hash leaves return declared HOLD reasons."""

    blob = _state_blob(((0.25, 0.75),))
    rows = [_registry_row("1", blob, 0.25, 0.75)]
    integer_raw, integer_sha256 = _registry_bytes(rows, schema_version=1)
    float_raw, float_sha256 = _registry_bytes(rows, schema_version=1.0)
    assert integer_raw != float_raw and integer_sha256 != float_sha256
    integer_registry = selector.load_pinned_state_registry(integer_raw, integer_sha256)
    assert tuple(integer_registry) == (Fraction(1),)
    with pytest.raises(selector.SelectorError) as float_error:
        selector.load_pinned_state_registry(float_raw, float_sha256)
    assert float_error.value.reason == "HOLD_CANONICAL_JSON"

    malformed_rows = copy.deepcopy(rows)
    malformed_rows[0]["state_blob_sha256"] = 7
    malformed_raw, malformed_sha256 = _registry_bytes(malformed_rows)
    with pytest.raises(selector.SelectorError) as hash_error:
        selector.load_pinned_state_registry(malformed_raw, malformed_sha256)
    assert hash_error.value.reason == "HOLD_DEPENDENCY_HASH"


def test_round131_seed_basis_pool_domains_and_point_of_use_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    accepted_hashes = ("0" * 64, "1" * 64, "2" * 64)
    fields = (
        *accepted_hashes,
        selector.EXPECTED_PHILOX_SPEC_SHA256,
        selector.EXPECTED_TEST_KEY_SET_SHA256,
        selector.EXPECTED_CENTRAL_PROJECTION_SHA256,
        selector.EXPECTED_RUNTIME_SPEC_SHA256,
    )
    independent_basis = hashlib.sha256(
        b"encounter-f2-common-observable-v2\0" + b"".join(bytes.fromhex(value) for value in fields)
    ).digest()
    basis = selector.derive_seed_basis(*accepted_hashes)
    assert basis == independent_basis

    keys = selector.derive_pool_keys(basis)
    independently_derived = {
        (control, pool): int.from_bytes(
            hashlib.sha256(b"philox-pool-v2\0" + basis + bytes((control, pool))).digest()[:8],
            "big",
        )
        for control in range(3)
        for pool in range(2)
    }
    assert keys == independently_derived
    assert len(set(keys.values())) == 6
    assert set(keys.values()).isdisjoint(selector.load_test_keys())

    with pytest.raises(selector.SelectorError) as collision:
        monkeypatch.setattr(selector, "load_test_keys", lambda: (keys[(0, 0)],))
        selector.derive_pool_keys(basis)
    assert collision.value.reason == "HOLD_SEED_COLLISION"
    monkeypatch.undo()

    # Point-of-use verification rejects drift before it can affect collisions.
    drifted_path = tmp_path / "drifted_test_keys.json"
    drifted_path.write_bytes(
        selector.canonical_json_bytes(
            {
                "format": "unsigned-64-bit-big-endian-lowercase-hex",
                "ordered_keys_be_u64_hex": [],
                "schema_version": 1,
                "set_purpose": "drifted",
            }
        )
    )
    assert hashlib.sha256(drifted_path.read_bytes()).hexdigest() != (
        selector.EXPECTED_TEST_KEY_SET_SHA256
    )
    monkeypatch.setattr(selector, "TEST_KEY_SET_PATH", drifted_path)
    with pytest.raises(selector.SelectorError) as drifted:
        selector.derive_pool_keys(basis)
    assert drifted.value.reason == "HOLD_TEST_KEY_SET"


def test_round131_hold_order_schema_enum_and_stage_rows_are_exact() -> None:
    assert selector.HOLD_ORDER == EXPECTED_HOLD_ORDER
    assert len(EXPECTED_HOLD_ORDER) == len(set(EXPECTED_HOLD_ORDER))
    assert set(selector.REASON_STAGE) == set(EXPECTED_HOLD_ORDER)
    assert set(selector.REASON_STAGE.values()) <= set(selector.STAGE_ORDER)
    schema = selector.strict_load_canonical_json(selector.SCHEMA_PATH.read_bytes())
    assert tuple(schema["$defs"]["hold_reason"]["enum"]) == EXPECTED_HOLD_ORDER

    reasons = (
        "HOLD_SEED_COLLISION",
        "HOLD_DEPENDENCY_HASH",
        "HOLD_SCHEMA_NULLABILITY",
        "HOLD_REFERENCE_POINT_LAW",
    )
    payload = selector.hold_payload(reversed(reasons))
    assert payload["hold"] == {
        "primary": "HOLD_SCHEMA_NULLABILITY",
        "secondary": [
            "HOLD_DEPENDENCY_HASH",
            "HOLD_REFERENCE_POINT_LAW",
            "HOLD_SEED_COLLISION",
        ],
    }
    failure_index = selector.STAGE_ORDER.index("schema")
    assert all(
        payload["stage_rows"][stage] == "NOT_RUN_AFTER_HOLD"
        for stage in selector.STAGE_ORDER[failure_index + 1 :]
    )

    lying = _hold_core("HOLD_DEPENDENCY_HASH", "HOLD_F1A")
    lying["hold"]["primary"], lying["hold"]["secondary"] = (
        "HOLD_F1A",
        ["HOLD_DEPENDENCY_HASH"],
    )
    with pytest.raises(selector.SelectorError) as lying_error:
        selector.validate_selector_envelope_bytes(
            selector.canonical_json_bytes(selector.build_selector_envelope(lying)),
            expected_dependencies=_dependencies(),
        )
    assert lying_error.value.reason == "HOLD_SCHEMA"


def test_round131_repaired_nonstring_seed_dependencies_return_hold() -> None:
    """Malformed seed dependencies are total over the canonical HOLD algebra."""

    for malformed in (None, 7, b"0" * 64):
        with pytest.raises(selector.SelectorError) as error:
            selector.derive_seed_basis(malformed, "0" * 64, "0" * 64)
        assert error.value.reason == "HOLD_DEPENDENCY_HASH"


def test_round131_runtime_rng_and_science_free_boundary() -> None:
    assert selector.verify_runtime_spec() == {
        "runtime_spec_sha256": selector.EXPECTED_RUNTIME_SPEC_SHA256,
        "runtime_verified": True,
    }
    rng = selector.verify_rng_specs()
    assert rng["philox_spec_sha256"] == selector.EXPECTED_PHILOX_SPEC_SHA256
    result = selector.run_science_free_self_check()
    assert result["authorized_scientific_command"] is None
    assert not result["f1_executed"]
    assert not result["monte_carlo_executed"]
    assert not result["positive_budget_evaluated"]
