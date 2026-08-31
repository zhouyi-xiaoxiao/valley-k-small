from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
import rate_defined_tensor_f0_candidate_v1 as candidate
import rate_defined_tensor_f0_topology_schedule_v1 as schedule


def _fraction(row: object) -> Fraction:
    assert type(row) is dict
    return Fraction(row["numerator"], row["denominator"])


def test_complete_schedule_counts_hashes_and_query_containment() -> None:
    payload = schedule.canonical_topology_schedule_payload()
    times = tuple(_fraction(row) for row in payload["topology_times"])
    tails = tuple(_fraction(row) for row in payload["mandatory_tail_times"])
    assert payload["schema"] == schedule.SCHEMA
    assert payload["status"] == schedule.STATUS
    assert payload["promotion_flags"] == schedule.PROMOTION_FLAGS
    assert payload["counts"] == {
        "analytic": 211,
        "combined_with_tail": 515,
        "heterogeneous": 26,
        "padding": 281,
        "required_union": 231,
        "topology": 512,
    }
    assert payload["hashes"] == schedule.EXPECTED_HASHES
    assert len(times) == 512
    assert times == tuple(sorted(set(times)))
    assert times[0] == Fraction(1, 2)
    assert times[-1] == Fraction(35)
    assert tails == (
        Fraction(35),
        Fraction(50),
        Fraction(75),
        Fraction(100),
    )
    assert len(set(times) | set(tails)) == 515
    required = {
        _fraction(row)
        for row in payload["query_sets"]["required_union"]
    }
    assert len(required) == 231
    assert required.issubset(times)
    assert Fraction(35) not in required
    assert Fraction(35) in {
        _fraction(row) for row in payload["padding_times"]
    }


def test_candidate_exact_query_sets_are_the_only_required_sources() -> None:
    semantic = candidate.build_semantic_candidate()
    analytic = {
        Fraction(value)
        for value in semantic["analytic_topology_fixtures"][
            "union_unique_query_times"
        ]
    }
    heterogeneous = {
        Fraction(value)
        for value in semantic["integrated_compiled_fixture"][
            "unique_query_times"
        ]
    }
    payload = schedule.canonical_topology_schedule_payload()
    frozen_analytic = {
        _fraction(row) for row in payload["query_sets"]["analytic"]
    }
    frozen_heterogeneous = {
        _fraction(row) for row in payload["query_sets"]["heterogeneous"]
    }
    assert analytic == frozen_analytic
    assert heterogeneous == frozen_heterogeneous
    assert len(analytic | heterogeneous) == 231


def test_payload_binding_and_canonical_round_trip() -> None:
    payload = schedule.canonical_topology_schedule_bytes()
    parsed = schedule.load_and_validate_canonical_topology_schedule_bytes(
        payload
    )
    provisional = copy.deepcopy(parsed)
    observed = provisional["payload_binding_sha256"]
    provisional["payload_binding_sha256"] = "0" * 64
    assert observed == hashlib.sha256(
        json.dumps(
            provisional,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    ).hexdigest()
    assert payload.decode("ascii").encode("ascii") == payload


@pytest.mark.parametrize(
    "mutator",
    (
        lambda row: row["topology_times"].pop(),
        lambda row: row["topology_times"].reverse(),
        lambda row: row["query_sets"]["analytic"].pop(),
        lambda row: row["promotion_flags"].__setitem__("f0_pass", True),
        lambda row: row["counts"].__setitem__("topology", 511),
        lambda row: row.__setitem__("unknown", False),
    ),
)
def test_semantic_mutations_fail_closed(mutator: object) -> None:
    payload = schedule.canonical_topology_schedule_payload()
    mutator(payload)
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    with pytest.raises(schedule.TopologyScheduleFailure):
        schedule.load_and_validate_canonical_topology_schedule_bytes(encoded)


@pytest.mark.parametrize(
    "payload",
    (
        b'{"a":1,"a":2}',
        b'{"value":NaN}',
        '{"value":"é"}'.encode(),
    ),
)
def test_strict_parser_rejects_duplicate_nonfinite_and_nonascii(
    payload: bytes,
) -> None:
    with pytest.raises(schedule.TopologyScheduleFailure):
        schedule.load_and_validate_canonical_topology_schedule_bytes(payload)


def test_public_surface_has_only_output_path_and_no_science_knobs() -> None:
    assert tuple(inspect.signature(schedule.topology_schedule_times).parameters) == ()
    assert tuple(
        inspect.signature(schedule.canonical_topology_schedule_bytes).parameters
    ) == ()
    source = Path(schedule.__file__).read_text(encoding="utf-8")
    assert source.count("parser.add_argument(") == 1
    assert '"--output"' in source
    assert all(
        option not in source
        for option in (
            "--control",
            "--budget",
            "--root",
            "--time",
            "--precision",
            "--threshold",
            "--resource",
        )
    )


def test_two_isolated_replicas_are_identical_and_output_is_exclusive(
    tmp_path: Path,
) -> None:
    source = Path(schedule.__file__).resolve()
    first = tmp_path / "schedule_one.json"
    second = tmp_path / "schedule_two.json"
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
    assert first.read_bytes() == second.read_bytes()
    schedule.load_and_validate_canonical_topology_schedule_bytes(
        first.read_bytes()
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(source),
            "--output",
            str(first),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode != 0
    assert first.read_bytes() == second.read_bytes()
