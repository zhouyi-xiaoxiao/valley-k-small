"""Round-139 independent attack on the frozen Round-135 selector candidate.

All fixtures are synthetic and science-free.  Finding reproducers intentionally
assert current behaviour; a green reproducer is not an acceptance signal.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

import f1_to_f2_common_observable_selector_v2 as selector
import pytest

FROZEN_ROUND139_SELECTOR_SHA256 = "118d33446c986c1ca07c129886000a0812550a3976e0d7c7879b9f833fdda5b1"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry_payload() -> dict[str, object]:
    blob = selector.encode_state_ball((("0x1.0000000000000p-2", "0x1.8000000000000p-1"),))
    return {
        "schema_version": 1,
        "states": [
            {
                "configuration": selector.REFERENCE_CONFIGURATION,
                "state_blob_sha256": hashlib.sha256(blob).hexdigest(),
                "survival_interval": [
                    "0x1.0000000000000p-2",
                    "0x1.8000000000000p-1",
                ],
                "time": "1",
            }
        ],
    }


def _load_registry_payload(payload: object) -> object:
    raw = selector.canonical_json_bytes(payload)
    return selector.load_pinned_state_registry(raw, hashlib.sha256(raw).hexdigest())


def _canonical_worker_pass(request_raw: bytes) -> bytes:
    request = selector.strict_load_canonical_json(request_raw)
    n = request["n"]
    return selector.canonical_json_bytes(
        {
            "request_sha256": hashlib.sha256(request_raw).hexdigest(),
            "result": [0, n],
            "runtime_binary_sha256": request["runtime_binary_sha256"],
            "runtime_spec_sha256": request["runtime_spec_sha256"],
            "runtime_verified": True,
            "schema_version": 1,
            "selector_source_sha256": request["selector_source_sha256"],
            "status": "PASS",
            "worker_peak_rss_bytes": 1,
        }
    )


def test_round139_frozen_candidate_has_been_superseded() -> None:
    assert _digest(selector.HERE / "f1_to_f2_common_observable_selector_v2.py") != (
        FROZEN_ROUND139_SELECTOR_SHA256
    )


@pytest.mark.parametrize(
    "raw",
    (
        b'{\n  "x": 2.0\n}\n',
        b'{\n  "x": 2e0\n}\n',
        b'{\n  "x": [\n    {\n      "y": 0.0\n    }\n  ]\n}\n',
        b'{\n  "x": {\n    "y": -0.0\n  }\n}\n',
    ),
)
def test_round139_all_recursive_json_float_tokens_are_rejected(raw: bytes) -> None:
    with pytest.raises(selector.SelectorError) as error:
        selector.strict_load_canonical_json(raw)
    assert error.value.reason == "HOLD_CANONICAL_JSON"


def test_round139_registry_type_fuzz_is_total_over_selector_holds() -> None:
    base = _registry_payload()
    assert tuple(_load_registry_payload(base)) == (Fraction(1),)

    mutations: list[dict[str, object]] = []
    for value in (True, False, None, "1", [], {}):
        payload = copy.deepcopy(base)
        payload["schema_version"] = value
        mutations.append(payload)
    for value in (True, None, 1, {}, []):
        payload = copy.deepcopy(base)
        payload["states"] = value
        mutations.append(payload)
    for value in (None, 7, True, [], {}, "A" * 64, "0" * 63):
        payload = copy.deepcopy(base)
        payload["states"][0]["state_blob_sha256"] = value
        mutations.append(payload)
    for value in (None, 7, True, [], {}, "wrong"):
        payload = copy.deepcopy(base)
        payload["states"][0]["configuration"] = value
        mutations.append(payload)
    for value in (None, 7, True, [], {}, "01", "1.0"):
        payload = copy.deepcopy(base)
        payload["states"][0]["time"] = value
        mutations.append(payload)
    for value in (None, 7, True, {}, [], [None, "0x1.0000000000000p+0"]):
        payload = copy.deepcopy(base)
        payload["states"][0]["survival_interval"] = value
        mutations.append(payload)

    for payload in mutations:
        with pytest.raises(selector.SelectorError) as error:
            _load_registry_payload(payload)
        assert error.value.reason in selector.HOLD_RANK

    valid_raw = selector.canonical_json_bytes(base)
    valid_digest = hashlib.sha256(valid_raw).hexdigest()
    for malformed in (None, 7, b"0" * 64, bytearray(b"0" * 64), "A" * 64, "0" * 63):
        with pytest.raises(selector.SelectorError) as error:
            selector.load_pinned_state_registry(valid_raw, malformed)
        assert error.value.reason == "HOLD_DEPENDENCY_HASH"
    for malformed in (None, bytearray(valid_raw), memoryview(valid_raw), "not bytes"):
        with pytest.raises(selector.SelectorError) as error:
            selector.load_pinned_state_registry(malformed, valid_digest)
        assert error.value.reason == "HOLD_DEPENDENCY_HASH"


def test_round139_seed_type_fuzz_is_total_over_selector_holds() -> None:
    malformed_hashes = (
        None,
        7,
        True,
        b"0" * 64,
        bytearray(b"0" * 64),
        memoryview(b"0" * 64),
        "A" * 64,
        "0" * 63,
        "g" * 64,
        [],
        {},
    )
    for malformed in malformed_hashes:
        with pytest.raises(selector.SelectorError) as error:
            selector.derive_seed_basis(malformed, "0" * 64, "0" * 64)
        assert error.value.reason == "HOLD_DEPENDENCY_HASH"
    for malformed in (None, b"", bytearray(32), memoryview(bytes(32)), True, 7, "0" * 32):
        with pytest.raises(selector.SelectorError) as error:
            selector.derive_pool_keys(malformed)
        assert error.value.reason == "HOLD_RNG_SPEC"


def test_round139_test_keys_are_hash_order_and_identity_bound_at_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    basis = selector.derive_seed_basis("0" * 64, "1" * 64, "2" * 64)
    original = json.loads(selector.TEST_KEY_SET_PATH.read_bytes())
    mutations = []

    for key, value in (
        ("format", "drifted"),
        ("set_purpose", "drifted"),
        ("schema_version", True),
        ("schema_version", 1.0),
    ):
        payload = copy.deepcopy(original)
        payload[key] = value
        mutations.append(payload)
    for values in (
        [],
        original["ordered_keys_be_u64_hex"][:-1],
        [*original["ordered_keys_be_u64_hex"], "1111111111111111"],
        list(reversed(original["ordered_keys_be_u64_hex"])),
        [original["ordered_keys_be_u64_hex"][0]] * 8,
        ["A" * 16, *original["ordered_keys_be_u64_hex"][1:]],
        ["0", *original["ordered_keys_be_u64_hex"][1:]],
        [None, *original["ordered_keys_be_u64_hex"][1:]],
    ):
        payload = copy.deepcopy(original)
        payload["ordered_keys_be_u64_hex"] = values
        mutations.append(payload)

    for index, payload in enumerate(mutations):
        raw = selector.canonical_json_bytes(payload)
        path = tmp_path / f"keys_{index}.json"
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
            with pytest.raises(selector.SelectorError) as semantic:
                selector.load_test_keys()
            assert semantic.value.reason in {"HOLD_CANONICAL_JSON", "HOLD_TEST_KEY_SET"}


def test_round139_worker_request_and_response_are_canonical_and_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(selector, "_require_worker_authorization", lambda _authorization: None)
    identity = selector._cp_worker_identity()
    raw = selector._cp_worker_request_bytes(
        1000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800), identity
    )
    request = selector.strict_load_canonical_json(raw)
    assert selector.canonical_json_bytes(request) == raw
    response_raw = selector._run_internal_cp_worker(raw)
    response = selector.strict_load_canonical_json(response_raw)
    assert response["request_sha256"] == hashlib.sha256(raw).hexdigest()
    assert response["status"] == "PASS"
    # This helper is deliberately exercised in the long-lived pytest process,
    # so only an actual isolated child is entitled to enforce the 256 MiB cap.
    assert response["worker_peak_rss_bytes"] > 0


def test_round139_runtime_mismatch_holds_before_cp_evaluation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The repaired numerical worker makes runtime verification mandatory."""

    calls = 0

    def rejected_runtime() -> object:
        nonlocal calls
        calls += 1
        raise selector.SelectorError("HOLD_DEPENDENCY_HASH", "synthetic runtime mismatch")

    monkeypatch.setattr(selector, "verify_runtime_spec", rejected_runtime)
    monkeypatch.setattr(selector, "_require_worker_authorization", lambda _authorization: None)
    identity = selector._cp_worker_identity()
    raw = selector._cp_worker_request_bytes(
        1000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800), identity
    )
    response = selector.strict_load_canonical_json(selector._run_internal_cp_worker(raw))
    assert calls == 1
    assert response["status"] == "HOLD"
    assert response["reason"] == "HOLD_DEPENDENCY_HASH"


def test_round139_parent_detects_post_worker_identity_toctou(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selector._isolated_cp_acceptance_set.cache_clear()
    identity = selector._cp_worker_identity()
    calls = 0

    def changing_identity() -> tuple[str, str, str]:
        nonlocal calls
        calls += 1
        if calls == 1:
            return identity
        return ("f" * 64, identity[1], identity[2])

    def worker(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=_canonical_worker_pass(kwargs["input"]),
            stderr=b"",
        )

    monkeypatch.setattr(selector, "_cp_worker_identity", changing_identity)
    monkeypatch.setattr(selector.subprocess, "run", worker)
    with pytest.raises(selector.SelectorError) as error:
        selector.cp_acceptance_set(1000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800))
    assert error.value.reason == "HOLD_DEPENDENCY_HASH"
    selector._isolated_cp_acceptance_set.cache_clear()


def test_round139_distinct_worker_concurrency_is_serialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The repaired launcher permits one aggregate child in a parent process."""

    selector._isolated_cp_acceptance_set.cache_clear()
    lock = threading.Lock()
    active = 0
    maximum_active = 0

    def worker(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        nonlocal active, maximum_active
        with lock:
            active += 1
            maximum_active = max(maximum_active, active)
        time.sleep(0.02)
        raw = _canonical_worker_pass(kwargs["input"])
        with lock:
            active -= 1
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=raw, stderr=b"")

    monkeypatch.setattr(selector.subprocess, "run", worker)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(
                selector.cp_acceptance_set,
                1000 + index,
                Fraction(1, 200),
                Fraction(3, 200),
                Fraction(1, 800),
            )
            for index in range(4)
        ]
        assert all(future.result()[0] == 0 for future in futures)
    assert maximum_active == selector.SPECIAL_WORKER_CONCURRENCY == 1
    print(f"Round139 synthetic simultaneous worker calls: {maximum_active}")
    selector._isolated_cp_acceptance_set.cache_clear()


def test_round139_two_real_concurrent_workers_bound_parent_rss() -> None:
    """Two real workers exercise concurrency while keeping aggregate use modest."""

    script = f"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector

def rss_kib():
    return int(subprocess.check_output(
        ['/bin/ps', '-o', 'rss=', '-p', str(os.getpid())], text=True
    ))

identity = selector._cp_worker_identity()
selector._isolated_cp_acceptance_set.cache_clear()
samples = [rss_kib()]
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = [
        pool.submit(
            selector._isolated_cp_acceptance_set,
            n, 1, 200, 3, 200, 1, 800, *identity, os.getpid()
        )
        for n in (1_000_000, 1_000_001)
    ]
    while not all(future.done() for future in futures):
        samples.append(rss_kib())
        time.sleep(0.02)
    rows = [future.result() for future in futures]
samples.append(rss_kib())
print(json.dumps({{'samples': samples, 'rows': rows}}))
"""
    completed = subprocess.run(
        [sys.executable, "-I", "-c", script],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    payload = json.loads(completed.stdout)
    assert max(payload["samples"]) - min(payload["samples"]) < 65_536
    for result, peak in payload["rows"]:
        assert result[0] < result[1]
        assert 0 < peak <= selector.CP_WORKER_PEAK_RSS_CAP_BYTES
    print(f"Round139 two-worker parent/child resource sample: {payload}")


def test_round139_isolated_power_helper_bounds_parent_rss() -> None:
    """The repaired public power helper returns MPFR pages with worker exit."""

    script = f"""
import gc
import os
import subprocess
import sys
from fractions import Fraction
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector

def rss_kib():
    return int(subprocess.check_output(
        ['/bin/ps', '-o', 'rss=', '-p', str(os.getpid())], text=True
    ))

values = [rss_kib()]
for _index in range(6):
    decision = selector.binomial_precision_ladder_decision(
        8_000_000,
        Fraction(1, 200),
        40_646,
        8_000_000,
        Fraction(1, 1600),
        'lt',
    )
    assert decision['decision'] == 'PASS'
    gc.collect()
    values.append(rss_kib())
print(' '.join(map(str, values)))
"""
    completed = subprocess.run(
        [sys.executable, "-I", "-c", script],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    values = tuple(int(value) for value in completed.stdout.split())
    assert len(values) == 7
    increments = tuple(right - left for left, right in zip(values, values[1:], strict=False))
    assert max(abs(increment) for increment in increments) < 8_192
    assert values[-1] - values[0] < 8_192
    print(f"Round139 direct power-helper RSS KiB: {values}")


def test_round139_large_n_threshold_has_not_drifted() -> None:
    assert selector.cp_acceptance_set(
        8_000_000, Fraction(1, 200), Fraction(3, 200), Fraction(1, 800)
    ) == (40_646, 118_891)
