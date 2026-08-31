"""Science-free closure tests for the three Round-139 selector findings."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

import f1_to_f2_common_observable_selector_v2 as selector
import pytest


def _power_worker_pass(request_raw: bytes) -> bytes:
    request = selector.strict_load_canonical_json(request_raw)
    interval = selector._mp_interval_exact(Fraction(0), 256).canonical_payload()
    return selector.canonical_json_bytes(
        {
            "operation": request["operation"],
            "request_sha256": selector.sha256_bytes(request_raw),
            "result": {
                "attempts": [{"interval": interval, "precision_bits": 256}],
                "decision": "PASS",
                "precision_bits": 256,
            },
            "runtime_binary_sha256": request["runtime_binary_sha256"],
            "runtime_spec_sha256": request["runtime_spec_sha256"],
            "runtime_verified": True,
            "schema_version": 1,
            "selector_source_sha256": request["selector_source_sha256"],
            "status": "PASS",
            "worker_peak_rss_bytes": 1,
        }
    )


def test_round140_cp_worker_runtime_hold_precedes_numerical_evaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"evaluator": 0, "runtime": 0}

    def rejected_runtime() -> object:
        calls["runtime"] += 1
        raise selector.SelectorError("HOLD_DEPENDENCY_HASH", "synthetic runtime drift")

    def forbidden_evaluator(*_args: object) -> object:
        calls["evaluator"] += 1
        raise AssertionError("numerical evaluation ran after a runtime HOLD")

    monkeypatch.setattr(selector, "verify_runtime_spec", rejected_runtime)
    monkeypatch.setattr(selector, "_require_worker_authorization", lambda _authorization: None)
    monkeypatch.setattr(selector, "_cp_acceptance_set_in_process", forbidden_evaluator)
    identity = selector._cp_worker_identity()
    raw = selector._cp_worker_request_bytes(
        1000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800), identity
    )
    response = selector.strict_load_canonical_json(selector._run_internal_cp_worker(raw))
    assert calls == {"evaluator": 0, "runtime": 1}
    assert response["status"] == "HOLD"
    assert response["reason"] == "HOLD_DEPENDENCY_HASH"


def test_round140_power_worker_runtime_hold_precedes_numerical_evaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"evaluator": 0, "runtime": 0}

    def rejected_runtime() -> object:
        calls["runtime"] += 1
        raise selector.SelectorError("HOLD_DEPENDENCY_HASH", "synthetic runtime drift")

    def forbidden_evaluator(*_args: object) -> object:
        calls["evaluator"] += 1
        raise AssertionError("power evaluation ran after a runtime HOLD")

    monkeypatch.setattr(selector, "verify_runtime_spec", rejected_runtime)
    monkeypatch.setattr(selector, "_require_worker_authorization", lambda _authorization: None)
    monkeypatch.setattr(
        selector, "_binomial_precision_ladder_decision_in_process", forbidden_evaluator
    )
    parameters = selector._binomial_power_parameters(
        1000, Fraction(1, 10), 0, 120, Fraction(9, 10), "lt"
    )
    raw = selector._power_worker_request_bytes(
        "binomial_decision", parameters, selector._cp_worker_identity()
    )
    response = selector.strict_load_canonical_json(selector._run_internal_power_worker(raw))
    assert calls == {"evaluator": 0, "runtime": 1}
    assert response["status"] == "HOLD"
    assert response["reason"] == "HOLD_DEPENDENCY_HASH"


def test_round140_public_power_api_has_no_parent_process_dag_bypass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_parent_dag(*_args: object) -> object:
        raise AssertionError("public API evaluated the MPFR DAG in its parent")

    monkeypatch.setattr(
        selector, "_binomial_precision_ladder_decision_in_process", forbidden_parent_dag
    )
    result = selector.binomial_precision_ladder_decision(
        1000, Fraction(1, 10), 0, 120, Fraction(9, 10), "lt"
    )
    assert result["decision"] in {"FAIL", "PASS"}


def test_round140_all_worker_launches_are_serialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active = 0
    maximum_active = 0
    lock = threading.Lock()

    def worker(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        nonlocal active, maximum_active
        with lock:
            active += 1
            maximum_active = max(maximum_active, active)
        time.sleep(0.02)
        response = _power_worker_pass(kwargs["input"])
        with lock:
            active -= 1
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=response, stderr=b"")

    monkeypatch.setattr(selector.subprocess, "run", worker)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(
                selector.binomial_precision_ladder_decision,
                1000 + index,
                Fraction(1, 10),
                0,
                120,
                Fraction(9, 10),
                "lt",
            )
            for index in range(4)
        ]
        assert all(future.result()["decision"] == "PASS" for future in futures)
    assert maximum_active == selector.SPECIAL_WORKER_CONCURRENCY == 1


def test_round140_file_lock_serializes_independent_parent_processes() -> None:
    script = f"""
import json
import sys
import time
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector
with selector._special_worker_slot():
    start = time.monotonic_ns()
    time.sleep(0.20)
    end = time.monotonic_ns()
print(json.dumps({{'start': start, 'end': end}}))
"""
    processes = [
        subprocess.Popen(
            [sys.executable, "-I", "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(2)
    ]
    intervals = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 0, stderr
        intervals.append(json.loads(stdout))
    first, second = sorted(intervals, key=lambda row: row["start"])
    assert first["end"] <= second["start"]


def test_round140_complete_synthetic_68_assertion_schedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    def synthetic_worker(
        operation: str, parameters: dict[str, object], **bindings: object
    ) -> tuple[dict[str, object], int, dict[str, object]]:
        calls.append((operation, parameters))
        return (
            {
                "attempts": [
                    {
                        "interval": {
                            "endpoint_encoding": "mpfr-base16-mantissa-exponent-precision",
                            "precision_bits": 256,
                        },
                        "precision_bits": 256,
                    }
                ],
                "decision": "PASS",
                "precision_bits": 256,
            },
            1234,
            {"assertion_id": bindings["assertion_id"]},
        )

    monkeypatch.setattr(selector, "_isolated_power_decision", synthetic_worker)
    fixture = selector.synthetic_power_resource_fixture(100_000)
    expected_schedule_sha256 = selector.sha256_bytes(
        selector.powered_assertion_schedule_bytes(fixture)
    )
    result = selector.execute_powered_assertion_schedule(
        fixture, expected_schedule_sha256=expected_schedule_sha256
    )
    assert len(calls) == 68
    assert {operation for operation, _parameters in calls} == {
        "binomial_decision",
        "dkw_decision",
    }
    assert result["family_counts"] == selector.POWER_ASSERTION_COUNTS
    assert result["decision_counts"] == {"FAIL": 0, "PASS": 68}
    assert result["maximum_worker_peak_rss_bytes"] == 1234
    assert result["positive_budget_evaluated"] is False
    assert result["assertion_schedule_sha256"] == expected_schedule_sha256
    assert len(result["assertion_receipts"]) == 68


@pytest.mark.parametrize(
    "arguments",
    (
        (True, Fraction(1, 10), 0, 1, Fraction(1, 2), "lt"),
        (100, "1/10", 0, 1, Fraction(1, 2), "lt"),
        (100, Fraction(1, 10), 2, 1, Fraction(1, 2), "lt"),
        (100, Fraction(1, 10), 0, 1, 0.5, "lt"),
        (100, Fraction(1, 10), 0, 1, Fraction(1, 2), "wrong"),
    ),
)
def test_round140_malformed_public_power_inputs_hold(arguments: tuple[object, ...]) -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector.binomial_precision_ladder_decision(*arguments)
    assert error.value.reason == "HOLD_POWER_BOUNDARY"
