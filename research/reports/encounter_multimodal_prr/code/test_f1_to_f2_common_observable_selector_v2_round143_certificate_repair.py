"""Round-143 focused tests for parent-side power certificates and schedule pins."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import f1_to_f2_common_observable_selector_v2 as selector
import pytest


def _interval_payload(lower: Fraction, upper: Fraction, precision: int) -> dict[str, object]:
    interval = selector.MPInterval(
        selector._mpfr_fraction(lower, precision, selector.gmpy2.RoundDown),
        selector._mpfr_fraction(upper, precision, selector.gmpy2.RoundUp),
        precision,
    )
    return interval.canonical_payload()


def _decision_payload(
    intervals: list[tuple[Fraction, Fraction]], decision: str
) -> dict[str, object]:
    attempts = []
    for precision, (lower, upper) in zip(
        selector.PRECISION_LADDER[: len(intervals)], intervals, strict=True
    ):
        attempts.append(
            {
                "interval": _interval_payload(lower, upper, precision),
                "precision_bits": precision,
            }
        )
    return {
        "attempts": attempts,
        "decision": decision,
        "precision_bits": attempts[-1]["precision_bits"],
    }


def test_round143_parent_recomputes_pass_and_fail_from_exact_endpoints() -> None:
    passed = _decision_payload([(Fraction(3, 4), Fraction(4, 5))], "PASS")
    failed = _decision_payload([(Fraction(1, 4), Fraction(2, 5))], "FAIL")
    assert selector._validate_power_decision_result(passed, Fraction(1, 2), "gt") is passed
    assert selector._validate_power_decision_result(failed, Fraction(1, 2), "gt") is failed


@pytest.mark.parametrize(
    ("interval", "decision"),
    (
        ((Fraction(2, 5), Fraction(3, 5)), "PASS"),
        ((Fraction(3, 4), Fraction(4, 5)), "FAIL"),
    ),
)
def test_round143_parent_rejects_decision_not_implied_by_endpoints(
    interval: tuple[Fraction, Fraction], decision: str
) -> None:
    forged = _decision_payload([interval], decision)
    with pytest.raises(selector.SelectorError) as error:
        selector._validate_power_decision_result(forged, Fraction(1, 2), "gt")
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_round143_parent_rejects_nonfirst_decisive_ladder() -> None:
    delayed = _decision_payload(
        [
            (Fraction(3, 4), Fraction(4, 5)),
            (Fraction(3, 4), Fraction(4, 5)),
        ],
        "PASS",
    )
    with pytest.raises(selector.SelectorError) as error:
        selector._validate_power_decision_result(delayed, Fraction(1, 2), "gt")
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


@pytest.mark.parametrize(
    "mutation",
    (
        lambda endpoint: {**endpoint, "extra": 1},
        lambda endpoint: {**endpoint, "mantissa_hex": "00"},
        lambda endpoint: {**endpoint, "mantissa_hex": "-0"},
        lambda endpoint: {**endpoint, "precision_bits": 512},
        lambda endpoint: {**endpoint, "exponent_base16": selector.MPFR_SERIALIZED_EMAX + 1},
    ),
)
def test_round143_parent_rejects_malformed_endpoint_payloads(mutation) -> None:
    result = _decision_payload([(Fraction(3, 4), Fraction(4, 5))], "PASS")
    interval = result["attempts"][0]["interval"]
    interval["lower"] = mutation(interval["lower"])
    with pytest.raises(selector.SelectorError) as error:
        selector._validate_power_decision_result(result, Fraction(1, 2), "gt")
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_round145_parent_rejects_nonrepresentable_low_mantissa_bits() -> None:
    result = _decision_payload([(Fraction(3, 4), Fraction(3, 4))], "PASS")
    interval = result["attempts"][0]["interval"]
    for endpoint_name in ("lower", "upper"):
        endpoint = interval[endpoint_name]
        assert endpoint["mantissa_hex"].endswith("0")
        endpoint["mantissa_hex"] = endpoint["mantissa_hex"][:-1] + "1"
    with pytest.raises(selector.SelectorError) as error:
        selector._validate_power_decision_result(result, Fraction(3, 4), "gt")
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_round143_public_workers_survive_parent_endpoint_validation() -> None:
    binomial = selector.binomial_precision_ladder_decision(
        100,
        Fraction(1, 2),
        0,
        100,
        Fraction(9, 10),
        "gt",
    )
    dkw = selector.dkw_precision_ladder_decision(
        Fraction(1, 2),
        Fraction(1, 20),
        1_000,
        Fraction(9, 10),
        "ge",
    )
    assert binomial["decision"] == "PASS"
    assert dkw["decision"] == "PASS"


def test_round143_schedule_has_exact_family_type_order_and_unique_ids() -> None:
    fixture = selector.synthetic_power_resource_fixture(100_000)
    assert len(fixture) == 68
    assert tuple((row.family, row.assertion_id) for row in fixture) == tuple(
        (family, assertion_id)
        for family, assertion_id, _operation in selector.POWER_ASSERTION_LAYOUT
    )
    assert len({row.assertion_id for row in fixture}) == 68
    assert all(
        type(row) is selector.DKWPowerAssertion
        for row in fixture[: selector.POWER_ASSERTION_COUNTS["survival_compatibility"]]
    )
    assert all(
        type(row) is selector.BinomialPowerAssertion
        for row in fixture[selector.POWER_ASSERTION_COUNTS["survival_compatibility"] :]
    )


def test_round143_parameter_mutation_misses_pinned_schedule_before_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = selector.synthetic_power_resource_fixture(100_000)
    expected = selector.sha256_bytes(selector.powered_assertion_schedule_bytes(fixture))
    mutated = list(fixture)
    mutated[-1] = replace(mutated[-1], boundary=Fraction(1, 1_599))
    monkeypatch.setattr(
        selector,
        "_isolated_power_decision",
        lambda *_args, **_kwargs: pytest.fail("a worker ran before schedule validation"),
    )
    with pytest.raises(selector.SelectorError) as error:
        selector.execute_powered_assertion_schedule(
            tuple(mutated), expected_schedule_sha256=expected
        )
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"


def test_round143_reorder_and_duplicate_identity_hold_before_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = list(selector.synthetic_power_resource_fixture(100_000))
    fixture[0], fixture[1] = fixture[1], fixture[0]
    monkeypatch.setattr(
        selector,
        "_isolated_power_decision",
        lambda *_args, **_kwargs: pytest.fail("a worker ran before schedule validation"),
    )
    with pytest.raises(selector.SelectorError) as error:
        selector.execute_powered_assertion_schedule(
            tuple(fixture), expected_schedule_sha256="0" * 64
        )
    assert error.value.reason == "HOLD_POWER_BOUNDARY"


def test_round143_wrong_family_type_holds_before_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = list(selector.synthetic_power_resource_fixture(100_000))
    first = fixture[0]
    fixture[0] = selector.BinomialPowerAssertion(
        assertion_id=first.assertion_id,
        family=first.family,
        n=100_000,
        p_value=Fraction(1, 2),
        lower=0,
        upper=100_000,
        boundary=Fraction(1, 2),
        relation="ge",
    )
    monkeypatch.setattr(
        selector,
        "_isolated_power_decision",
        lambda *_args, **_kwargs: pytest.fail("a worker ran before schedule validation"),
    )
    with pytest.raises(selector.SelectorError) as error:
        selector.execute_powered_assertion_schedule(
            tuple(fixture), expected_schedule_sha256="0" * 64
        )
    assert error.value.reason == "HOLD_POWER_BOUNDARY"


def test_round143_invalid_final_record_holds_before_first_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = list(selector.synthetic_power_resource_fixture(100_000))
    fixture[-1] = replace(fixture[-1], boundary=Fraction(2))
    monkeypatch.setattr(
        selector,
        "_isolated_power_decision",
        lambda *_args, **_kwargs: pytest.fail("a worker ran before schedule validation"),
    )
    with pytest.raises(selector.SelectorError) as error:
        selector.powered_assertion_schedule_bytes(tuple(fixture))
    assert error.value.reason == "HOLD_POWER_BOUNDARY"


def test_round143_pinned_complete_schedule_executes_both_worker_families(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = selector.synthetic_power_resource_fixture(100_000)
    expected = selector.sha256_bytes(selector.powered_assertion_schedule_bytes(fixture))
    calls = []

    def fake_worker(operation: str, parameters: dict[str, object], **bindings: object):
        calls.append((operation, parameters))
        return (
            {"decision": "PASS"},
            4_096,
            {"assertion_id": bindings["assertion_id"]},
        )

    monkeypatch.setattr(selector, "_isolated_power_decision", fake_worker)
    result = selector.execute_powered_assertion_schedule(fixture, expected_schedule_sha256=expected)
    assert len(calls) == 68
    assert {operation for operation, _parameters in calls} == {
        "binomial_decision",
        "dkw_decision",
    }
    assert result["assertion_schedule_sha256"] == expected
    assert result["family_counts"] == selector.POWER_ASSERTION_COUNTS
    assert len(result["assertion_receipts"]) == 68
