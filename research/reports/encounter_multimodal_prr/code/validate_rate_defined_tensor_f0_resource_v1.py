#!/usr/bin/env python3
"""Independent stdlib-only replay of the formal F0 resource evidence.

This module deliberately does not import the resource runner, the compiled
backend, the batched scalar evaluator, the semantic candidate, NumPy, or
gmpy2.  It reconstructs the persistence contracts from canonical JSON,
recomputes every available nested binding, rehashes the frozen source tree,
and checks the identity fixture directly.

Two terminal receipts are possible:

* ``PASS_F0_RESOURCE_INDEPENDENT_REPLAY_NOT_F0`` when the formal resource
  observation satisfies every frozen cap; and
* ``INDEPENDENTLY_CONFIRMED_HOLD_F0_METHOD_OR_RESOURCE`` when the numerical
  payload is sound but the immutable resource observation records exactly the
  frozen resource-cap failure.

Neither receipt accepts F0, authorizes F1, or authorizes scientific execution.
The stricter ``require_formal_resource_pass`` API always fails closed on the
HOLD branch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import struct
import sys
from fractions import Fraction
from pathlib import Path
from typing import Final, Sequence


class IndependentReplayFailure(RuntimeError):
    """Fail-closed independent replay error."""


REPLAY_SCHEMA: Final = "rate_defined_tensor_f0_resource_independent_replay_v1"
PASS_REPLAY_STATUS: Final = "PASS_F0_RESOURCE_INDEPENDENT_REPLAY_NOT_F0"
HOLD_REPLAY_STATUS: Final = (
    "INDEPENDENTLY_CONFIRMED_HOLD_F0_METHOD_OR_RESOURCE"
)

CANONICAL_SCHEMA: Final = "rate_defined_tensor_f0_resource_canonical_v1"
CANONICAL_STATUS: Final = (
    "CANONICAL_METHOD_EVIDENCE_AWAITING_RESOURCE_EVALUATION"
)
OBSERVATION_SCHEMA: Final = "rate_defined_tensor_f0_resource_observation_v1"
PASS_OBSERVATION_STATUS: Final = "PASS_RESOURCE_CANDIDATE_NOT_F0"
HOLD_OBSERVATION_STATUS: Final = "HOLD_F0_METHOD_OR_RESOURCE"

SCHEDULE_SCHEMA: Final = "rate_defined_tensor_f0_topology_schedule_v1"
SCHEDULE_STATUS: Final = "PASS_F0_TOPOLOGY_SCHEDULE_FROZEN_NOT_F0"
SCHEDULE_STAGE: Final = "F0_SCIENCE_FREE_COMPLETE_QUERY_SCHEDULE"
SCHEDULE_ARTIFACT_SHA256: Final = (
    "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344"
)
SCHEDULE_PAYLOAD_BINDING_SHA256: Final = (
    "0621f2db5d8df0fe6e09ef16c60496c631364c01df5200f9aed8ecb05ef2758d"
)
SCHEDULE_HASHES: Final = {
    "analytic_times_sha256": (
        "de5841874cd971bb731df76215efd044d94f496ab17a9dbd433ed28c9189a3e2"
    ),
    "heterogeneous_times_sha256": (
        "87ee412ba94dbeb3bdb0b8aa8770ca66ee31f222e73c13b9846db9c2aa74a943"
    ),
    "required_union_sha256": (
        "e7ba95950573919b9ef462c6afb24e560357920cb7c07db9df9ec4f91a1bea1f"
    ),
    "padding_times_sha256": (
        "dd84e3003f3d839ddf3123db121ddc686dc97743846ff814c136de1d7aa1eaa7"
    ),
    "topology_times_sha256": (
        "77b42d12721f3508eb128e2f3866181b372b34fa0d06a8ad7ec9b1ed8f581561"
    ),
}

FORMAL_SHAPE: Final = (207, 215, 161)
FORMAL_PERIODIC: Final = (False, False, True)
FORMAL_STATES: Final = 7_165_305
FORMAL_RATE: Final = Fraction(256)
FORMAL_KILLING: Final = Fraction(1, 64)
FORMAL_HORIZON: Final = Fraction(100)
FORMAL_TAIL_TOLERANCE: Final = Fraction(1, 10**18)
FORMAL_PRECISION_BITS: Final = 192
FORMAL_MAXIMUM_TERMS: Final = 200_000
FORMAL_BLOCK_SIZE: Final = 65_536
FORMAL_TOPOLOGY_COUNT: Final = 512
FORMAL_TAIL_TIMES: Final = (
    Fraction(35),
    Fraction(50),
    Fraction(75),
    Fraction(100),
)
FORMAL_UNION_COUNT: Final = 515
FORMAL_MAXIMUM_POWER: Final = 27_018
FORMAL_SCALAR_RECORD_COUNT: Final = 27_019
FORMAL_HORIZON_MODE: Final = 25_600
FORMAL_HORIZON_RIGHT_INDEX: Final = 27_014
FORMAL_MAXIMUM_WALL_SECONDS: Final = 3_600.0
FORMAL_MAXIMUM_RSS_BYTES: Final = 4_294_967_296
FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES: Final = 8_589_934_592
FORMAL_MAXIMUM_SWAP_DELTA: Final = 0
FORMAL_MAXIMUM_STATE_RADIUS: Final = Fraction(1, 100_000_000)

MAXIMUM_CANONICAL_BYTES: Final = 768_000_000
MAXIMUM_SIDECAR_BYTES: Final = 2_000_000
MAXIMUM_SCHEDULE_BYTES: Final = 2_000_000
MAXIMUM_SOURCE_BYTES: Final = 64_000_000
SHA256_ZERO: Final = "0" * 64

METHOD_INPUT_PROVENANCE: Final = (
    "CALLER_SUPPLIED_UNCLASSIFIED_NO_CONTROL_OR_BUDGET_EXCLUSION_PROOF"
)
COMPILED_INPUT_PROVENANCE: Final = "CALLER_SUPPLIED_UNCLASSIFIED"
COMPILED_METHOD_STATUS: Final = "COMPILED_METHOD_BACKEND_ONLY_NOT_F0"
COMPILED_BATCH_STATUS: Final = "COMPILED_BATCH_METHOD_COMPLETE_NOT_F0"
MAGNITUDE_FORMULA: Final = (
    "Kmax*(2*lambda)^r*initial_mass_upper_by_submarkov_contraction_v1"
)

PROMOTION_FLAGS: Final = {
    "authorizes_f1": False,
    "authorizes_scientific_execution": False,
    "control_exclusion_proved": False,
    "f0_pass": False,
    "independent_audit_complete": False,
    "production_resource_gate": False,
    "production_scale_execution_classified": False,
    "resource_pass": False,
    "science_executed": False,
    "science_free_proved": False,
}
SCHEDULE_PROMOTION_FLAGS: Final = {
    "authorizes_f1": False,
    "authorizes_scientific_execution": False,
    "f0_accepted": False,
    "f0_pass": False,
    "positive_budget_primary_controls_evaluated": False,
    "production_resource_gate": False,
    "science_executed": False,
}
REPLAY_PROMOTION_FLAGS: Final = {
    "authorizes_f1": False,
    "authorizes_scientific_execution": False,
    "f0_accepted": False,
    "f0_pass": False,
    "production_resource_gate": False,
    "resource_pass": False,
    "science_executed": False,
}

EXPECTED_DEPENDENCY_SHA256: Final = {
    "batched_scalar_source": (
        "56b783f073528146e6cdd3321f078a89978b5e5453b8fdfcabfe35412614b280"
    ),
    "batched_scalar_test": (
        "ddddb839f3b50c1dc2ca05fbce2ddad1b5e025d08f549665585b7a866159dac1"
    ),
    "candidate_freeze": (
        "0f282f7227220c4a0dc6ae13996ee650759d0cf6679a6d360897929386796d9b"
    ),
    "compiled_batch_source": (
        "798d605d5cfc79319a633a5f9e487b4da34a55638b534f35804b3636cb402aa7"
    ),
    "compiled_batch_test": (
        "c1a378aa9851335391d3dfd016be8cf7943abfc388754eb9fb5d59c49d941e4e"
    ),
    "compiled_power_c_source": (
        "9db8c672a04732b23dedb332854c4f4259911cfac32ec130d1d16b64db274917"
    ),
    "compiled_power_python_source": (
        "13c7fabd4118c3858b03d839dcfea037eb15eb6b64b08f7fb69f0757342eae55"
    ),
    "compiled_power_test": (
        "513c0ce06b4424c4a8c3cf6cfea3bb21cd588fc389af8a9e760e451fb9b6dd51"
    ),
    "topology_schedule_artifact": SCHEDULE_ARTIFACT_SHA256,
    "topology_schedule_source": (
        "f188cbbf7c9e6c31e90ab01c21c9effd334e4ab449102c5501271f83723d2ca7"
    ),
    "topology_schedule_test": (
        "0deed13b23eec298047e290513232094c4ba3ca18db1c8177c6e7e0d7607fcaf"
    ),
}
DEPENDENCY_RELATIVE_PATHS: Final = {
    "batched_scalar_source": (
        "code/rate_defined_tensor_f0_batched_scalar_uniformization_v1.py"
    ),
    "batched_scalar_test": (
        "code/test_rate_defined_tensor_f0_batched_scalar_uniformization_v1.py"
    ),
    "candidate_freeze": "notes/rate_defined_tensor_f0_candidate_v1_freeze.md",
    "compiled_batch_source": "code/rate_defined_tensor_f0_compiled_batch_v1.py",
    "compiled_batch_test": "code/test_rate_defined_tensor_f0_compiled_batch_v1.py",
    "compiled_power_c_source": (
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.c"
    ),
    "compiled_power_python_source": (
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.py"
    ),
    "compiled_power_test": (
        "code/test_rate_defined_tensor_f0_compiled_power_stream_v1.py"
    ),
    "topology_schedule_artifact": (
        "artifacts/data/rate_defined_tensor_f0_topology_schedule_v1.json"
    ),
    "topology_schedule_source": (
        "code/rate_defined_tensor_f0_topology_schedule_v1.py"
    ),
    "topology_schedule_test": (
        "code/test_rate_defined_tensor_f0_topology_schedule_v1.py"
    ),
}
EXPECTED_CANDIDATE_SOURCE_SHA256: Final = (
    "acf32cc3babd269d4dec26081ab2e5f5b616a537c7d2989a38c47b72f1d64aba"
)
EXPECTED_CANDIDATE_TEST_SHA256: Final = (
    "f4259eb7cc00d262894ff61554621c14acff18c41106eb713d07bd59629116da"
)
EXPECTED_CANONICAL_CANDIDATE_SHA256: Final = (
    "f3c294fbc6323845b530b986197ee43d3f0b3fb8a690aa9f5bb71e4f343889dd"
)
EXPECTED_RUNNER_SOURCE_SHA256: Final = (
    "12adb131e416f52579773c11e364d126cd24b4fa3ffed1ed0cc1a97f54051181"
)


def _canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise IndependentReplayFailure("canonical JSON encoding failed") from error


def _pretty_json_bytes(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            ).encode("ascii")
            + b"\n"
        )
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise IndependentReplayFailure("pretty JSON encoding failed") from error


def _strict_json_loads(payload: bytes, *, label: str, maximum_bytes: int) -> object:
    if type(payload) is not bytes or not payload or len(payload) > maximum_bytes:
        raise IndependentReplayFailure(f"{label} byte envelope is invalid")
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise IndependentReplayFailure(f"{label} is not ASCII") from error

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise IndependentReplayFailure(
                    f"{label} has a duplicate or non-string key"
                )
            result[key] = value
        return result

    try:
        return json.loads(
            text,
            object_pairs_hook=object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"nonfinite JSON token {token}")
            ),
        )
    except IndependentReplayFailure:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise IndependentReplayFailure(f"{label} JSON is invalid") from error


def _require_exact_dict(
    value: object,
    keys: set[str] | frozenset[str],
    *,
    label: str,
) -> dict[str, object]:
    if type(value) is not dict or set(value) != set(keys):
        raise IndependentReplayFailure(f"{label} has a noncanonical key set")
    return value


def _require_int(value: object, *, label: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise IndependentReplayFailure(f"{label} is not a valid exact integer")
    return value


def _require_sha256(value: object, *, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise IndependentReplayFailure(f"{label} is not canonical SHA-256")
    return value


def _require_fraction(value: object, *, label: str) -> Fraction:
    row = _require_exact_dict(
        value,
        {"denominator", "numerator"},
        label=label,
    )
    numerator = _require_int(row["numerator"], label=f"{label} numerator")
    denominator = _require_int(
        row["denominator"],
        label=f"{label} denominator",
        minimum=1,
    )
    result = Fraction(numerator, denominator)
    if result.numerator != numerator or result.denominator != denominator:
        raise IndependentReplayFailure(f"{label} rational is not reduced")
    return result


def _fraction_payload(value: Fraction) -> dict[str, int]:
    return {"denominator": value.denominator, "numerator": value.numerator}


def _fraction_from_fields(
    row: dict[str, object],
    numerator_key: str,
    denominator_key: str,
    *,
    label: str,
) -> Fraction:
    numerator = _require_int(row[numerator_key], label=f"{label} numerator")
    denominator = _require_int(
        row[denominator_key],
        label=f"{label} denominator",
        minimum=1,
    )
    result = Fraction(numerator, denominator)
    if result.numerator != numerator or result.denominator != denominator:
        raise IndependentReplayFailure(f"{label} rational is not reduced")
    return result


def _parse_hex(
    value: object,
    *,
    label: str,
    nonnegative: bool = False,
) -> float:
    if type(value) is not str:
        raise IndependentReplayFailure(f"{label} is not binary64 hex")
    try:
        result = float.fromhex(value)
    except ValueError as error:
        raise IndependentReplayFailure(f"{label} is not binary64 hex") from error
    if (
        not math.isfinite(result)
        or result.hex() != value
        or (result == 0.0 and math.copysign(1.0, result) < 0.0)
        or (nonnegative and result < 0.0)
    ):
        raise IndependentReplayFailure(f"{label} is not canonical binary64")
    return result


def _binding_with_zero(row: dict[str, object], field: str) -> str:
    if field not in row:
        raise IndependentReplayFailure(f"binding field {field} is absent")
    provisional = dict(row)
    provisional[field] = SHA256_ZERO
    return hashlib.sha256(_canonical_json_bytes(provisional)).hexdigest()


def _binding_without(row: dict[str, object], field: str) -> str:
    if field not in row:
        raise IndependentReplayFailure(f"binding field {field} is absent")
    provisional = {key: value for key, value in row.items() if key != field}
    return hashlib.sha256(_canonical_json_bytes(provisional)).hexdigest()


def _stable_read(path: Path, *, label: str, maximum_bytes: int) -> bytes:
    if not isinstance(path, Path) or not path.is_absolute():
        raise IndependentReplayFailure(f"{label} path must be absolute")
    try:
        before = path.stat(follow_symlinks=False)
        payload = path.read_bytes()
        after = path.stat(follow_symlinks=False)
    except OSError as error:
        raise IndependentReplayFailure(f"{label} cannot be read") from error
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_mode,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_mode,
    )
    if (
        identity_before != identity_after
        or before.st_size != len(payload)
        or not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or len(payload) > maximum_bytes
    ):
        raise IndependentReplayFailure(f"{label} changed or is not a regular file")
    return payload


def _stable_sha256(path: Path, *, label: str) -> str:
    return hashlib.sha256(
        _stable_read(path, label=label, maximum_bytes=MAXIMUM_SOURCE_BYTES)
    ).hexdigest()


def _write_exclusive(path: Path, payload: bytes) -> None:
    if not isinstance(path, Path) or not path.is_absolute():
        raise IndependentReplayFailure("output path must be absolute")
    if not path.parent.is_dir() or path.name in {"", ".", ".."}:
        raise IndependentReplayFailure("output parent or filename is invalid")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise IndependentReplayFailure("output reservation failed") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise IndependentReplayFailure("output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    except BaseException:
        os.close(descriptor)
        path.unlink(missing_ok=True)
        raise
    os.close(descriptor)


def _times_sha256(values: Sequence[Fraction]) -> str:
    return hashlib.sha256(
        _canonical_json_bytes([_fraction_payload(value) for value in values])
    ).hexdigest()


def _parse_fraction_list(
    value: object,
    *,
    label: str,
    expected_count: int | None = None,
) -> tuple[Fraction, ...]:
    if type(value) is not list:
        raise IndependentReplayFailure(f"{label} is not a list")
    result = tuple(
        _require_fraction(row, label=f"{label}[{index}]")
        for index, row in enumerate(value)
    )
    if expected_count is not None and len(result) != expected_count:
        raise IndependentReplayFailure(f"{label} count drifted")
    return result


def _validate_schedule(
    payload: bytes,
    *,
    report_root: Path,
) -> tuple[dict[str, object], tuple[Fraction, ...]]:
    if hashlib.sha256(payload).hexdigest() != SCHEDULE_ARTIFACT_SHA256:
        raise IndependentReplayFailure("frozen schedule artifact hash drifted")
    parsed = _strict_json_loads(
        payload,
        label="frozen schedule",
        maximum_bytes=MAXIMUM_SCHEDULE_BYTES,
    )
    row = _require_exact_dict(
        parsed,
        {
            "candidate_binding",
            "counts",
            "hashes",
            "mandatory_tail_times",
            "padding_recipe",
            "padding_times",
            "payload_binding_sha256",
            "promotion_flags",
            "query_sets",
            "schema",
            "stage",
            "status",
            "topology_times",
        },
        label="frozen schedule",
    )
    if _canonical_json_bytes(row) != payload:
        raise IndependentReplayFailure("frozen schedule bytes are not canonical")
    if (
        row["schema"] != SCHEDULE_SCHEMA
        or row["stage"] != SCHEDULE_STAGE
        or row["status"] != SCHEDULE_STATUS
        or row["promotion_flags"] != SCHEDULE_PROMOTION_FLAGS
        or row["hashes"] != SCHEDULE_HASHES
        or row["payload_binding_sha256"] != SCHEDULE_PAYLOAD_BINDING_SHA256
        or row["payload_binding_sha256"]
        != _binding_with_zero(row, "payload_binding_sha256")
    ):
        raise IndependentReplayFailure("frozen schedule header drifted")

    candidate = _require_exact_dict(
        row["candidate_binding"],
        {
            "candidate_schema",
            "candidate_source_sha256",
            "candidate_test_sha256",
            "canonical_candidate_sha256",
        },
        label="schedule candidate binding",
    )
    if candidate != {
        "candidate_schema": "rate_defined_tensor_f0_candidate_v1_method_complete",
        "candidate_source_sha256": EXPECTED_CANDIDATE_SOURCE_SHA256,
        "candidate_test_sha256": EXPECTED_CANDIDATE_TEST_SHA256,
        "canonical_candidate_sha256": EXPECTED_CANONICAL_CANDIDATE_SHA256,
    }:
        raise IndependentReplayFailure("schedule candidate binding drifted")

    counts = _require_exact_dict(
        row["counts"],
        {
            "analytic",
            "combined_with_tail",
            "heterogeneous",
            "padding",
            "required_union",
            "topology",
        },
        label="schedule counts",
    )
    if counts != {
        "analytic": 211,
        "combined_with_tail": 515,
        "heterogeneous": 26,
        "padding": 281,
        "required_union": 231,
        "topology": 512,
    }:
        raise IndependentReplayFailure("schedule counts drifted")

    query_sets = _require_exact_dict(
        row["query_sets"],
        {"analytic", "heterogeneous", "required_union"},
        label="schedule query sets",
    )
    analytic = _parse_fraction_list(
        query_sets["analytic"],
        label="analytic schedule times",
        expected_count=211,
    )
    heterogeneous = _parse_fraction_list(
        query_sets["heterogeneous"],
        label="heterogeneous schedule times",
        expected_count=26,
    )
    required_union = _parse_fraction_list(
        query_sets["required_union"],
        label="required schedule union",
        expected_count=231,
    )
    padding = _parse_fraction_list(
        row["padding_times"],
        label="schedule padding times",
        expected_count=281,
    )
    topology = _parse_fraction_list(
        row["topology_times"],
        label="topology schedule times",
        expected_count=FORMAL_TOPOLOGY_COUNT,
    )
    tails = _parse_fraction_list(
        row["mandatory_tail_times"],
        label="schedule mandatory tail times",
        expected_count=4,
    )
    if (
        tuple(sorted(set(analytic))) != analytic
        or tuple(sorted(set(heterogeneous))) != heterogeneous
        or tuple(sorted(set(required_union))) != required_union
        or tuple(sorted(set(padding))) != padding
        or tuple(sorted(set(topology))) != topology
        or required_union != tuple(sorted(set(analytic) | set(heterogeneous)))
        or topology != tuple(sorted(set(required_union) | set(padding)))
        or topology[0] != Fraction(1, 2)
        or topology[-1] != Fraction(35)
        or tails != FORMAL_TAIL_TIMES
        or len(set(topology) | set(tails)) != FORMAL_UNION_COUNT
        or _times_sha256(analytic) != SCHEDULE_HASHES["analytic_times_sha256"]
        or _times_sha256(heterogeneous)
        != SCHEDULE_HASHES["heterogeneous_times_sha256"]
        or _times_sha256(required_union)
        != SCHEDULE_HASHES["required_union_sha256"]
        or _times_sha256(padding) != SCHEDULE_HASHES["padding_times_sha256"]
        or _times_sha256(topology) != SCHEDULE_HASHES["topology_times_sha256"]
    ):
        raise IndependentReplayFailure("frozen schedule time ledger failed replay")

    padding_recipe = _require_exact_dict(
        row["padding_recipe"],
        {
            "enumeration",
            "first_denominator",
            "padding_count",
            "result_order",
            "window",
        },
        label="schedule padding recipe",
    )
    if padding_recipe != {
        "enumeration": (
            "absolute_dyadic_grids_left_to_right_skip_required_and_seen"
        ),
        "first_denominator": 4,
        "padding_count": 281,
        "result_order": "strict_fraction_ascending",
        "window": [_fraction_payload(Fraction(1, 2)), _fraction_payload(Fraction(35))],
    }:
        raise IndependentReplayFailure("schedule padding recipe drifted")

    candidate_source = report_root / "code/rate_defined_tensor_f0_candidate_v1.py"
    candidate_test = report_root / "code/test_rate_defined_tensor_f0_candidate_v1.py"
    if (
        _stable_sha256(candidate_source, label="candidate source")
        != EXPECTED_CANDIDATE_SOURCE_SHA256
        or _stable_sha256(candidate_test, label="candidate test")
        != EXPECTED_CANDIDATE_TEST_SHA256
    ):
        raise IndependentReplayFailure("live candidate source binding drifted")
    return row, topology


def _expected_fixture() -> dict[str, object]:
    return {
        "identity_initial_flat_index": 0,
        "identity_kernel": True,
        "killing": _fraction_payload(FORMAL_KILLING),
        "maximum_peak_footprint_bytes": FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES,
        "maximum_poisson_terms": FORMAL_MAXIMUM_TERMS,
        "maximum_process_swap_delta": FORMAL_MAXIMUM_SWAP_DELTA,
        "maximum_rss_bytes": FORMAL_MAXIMUM_RSS_BYTES,
        "maximum_state_radius": _fraction_payload(FORMAL_MAXIMUM_STATE_RADIUS),
        "maximum_wall_seconds": _fraction_payload(
            Fraction(int(FORMAL_MAXIMUM_WALL_SECONDS))
        ),
        "mpfr_precision_bits": FORMAL_PRECISION_BITS,
        "name": "largest_shape_identity_control_free_v1",
        "periodic": list(FORMAL_PERIODIC),
        "production_scale": True,
        "reduction_block_size": FORMAL_BLOCK_SIZE,
        "series_horizon": _fraction_payload(FORMAL_HORIZON),
        "shape": list(FORMAL_SHAPE),
        "state_count": FORMAL_STATES,
        "tail_tolerance": _fraction_payload(FORMAL_TAIL_TOLERANCE),
        "uniformization_rate": _fraction_payload(FORMAL_RATE),
    }


def _expected_schedule_projection(
    topology: tuple[Fraction, ...],
) -> dict[str, object]:
    return {
        "artifact_sha256": SCHEDULE_ARTIFACT_SHA256,
        "combined_union_count": FORMAL_UNION_COUNT,
        "generator": "rate_defined_tensor_f0_topology_schedule_v1",
        "integrated_query_set_frozen": True,
        "mandatory_tail_times": [
            _fraction_payload(value) for value in FORMAL_TAIL_TIMES
        ],
        "maximum_union_time_count": FORMAL_UNION_COUNT,
        "provisional": False,
        "status": "FIXED_COMPLETE_CONTROL_FREE_SCHEDULE",
        "topology_time_count": FORMAL_TOPOLOGY_COUNT,
        "topology_times": [_fraction_payload(value) for value in topology],
    }


def _expected_dependencies() -> dict[str, dict[str, object]]:
    return {
        name: {
            "accepted": True,
            "expected_sha256": digest,
            "observed_sha256": digest,
        }
        for name, digest in sorted(EXPECTED_DEPENDENCY_SHA256.items())
    }


def _rehash_dependencies(report_root: Path) -> dict[str, str]:
    if (
        not isinstance(report_root, Path)
        or not report_root.is_absolute()
        or not report_root.is_dir()
    ):
        raise IndependentReplayFailure("report root must be an absolute directory")
    if set(DEPENDENCY_RELATIVE_PATHS) != set(EXPECTED_DEPENDENCY_SHA256):
        raise IndependentReplayFailure("dependency registry key set drifted")
    observed: dict[str, str] = {}
    for name in sorted(DEPENDENCY_RELATIVE_PATHS):
        digest = _stable_sha256(
            report_root / DEPENDENCY_RELATIVE_PATHS[name],
            label=f"dependency {name}",
        )
        if digest != EXPECTED_DEPENDENCY_SHA256[name]:
            raise IndependentReplayFailure(f"dependency hash mismatch: {name}")
        observed[name] = digest
    runner_digest = _stable_sha256(
        report_root / "code/run_rate_defined_tensor_f0_resource_v1.py",
        label="resource runner source",
    )
    if runner_digest != EXPECTED_RUNNER_SOURCE_SHA256:
        raise IndependentReplayFailure("resource runner source hash drifted")
    return observed


SERIES_KEYS: Final = {
    "canonical_scalar_records_retained",
    "control_exclusion_proved",
    "f0_pass",
    "horizon_denominator",
    "horizon_numerator",
    "initial_mass_upper_denominator",
    "initial_mass_upper_numerator",
    "input_provenance_classification",
    "maximum_killing_upper_denominator",
    "maximum_killing_upper_numerator",
    "maximum_power_index",
    "records",
    "scalar_stream_sha256",
    "schema",
    "science_free_proved",
    "series_binding_sha256",
    "state_arrays_retained",
    "uniformization_rate_denominator",
    "uniformization_rate_numerator",
}
POWER_RECORD_KEYS: Final = {
    "binding_sha256",
    "index",
    "lower_hex",
    "schema",
    "upper_hex",
}
JET_KEYS: Final = {"binding_sha256", "lower_hex", "order", "schema", "upper_hex"}
MAGNITUDE_KEYS: Final = {
    "binding_sha256",
    "formula",
    "order",
    "schema",
    "upper_hex",
}
POISSON_KEYS: Final = {
    "binding_sha256",
    "forward_weight_recurrence_steps",
    "mean_denominator",
    "mean_numerator",
    "mode",
    "mode_initialization_count",
    "mode_initialized",
    "p0_back_recurrence_steps",
    "p0_derived_from_mode",
    "planning_recurrence_steps",
    "precision_bits",
    "requested_tail_denominator",
    "requested_tail_numerator",
    "right_index",
    "right_tail_geometric",
    "right_tail_planning_steps",
    "schema",
    "starts_at_zero",
    "tail_upper_hex",
    "terms",
}
TIME_ROW_KEYS: Final = {
    "absolute_time_from_initial",
    "binding_sha256",
    "jets",
    "magnitudes",
    "poisson",
    "schema",
    "state_chaining_used",
    "time_denominator",
    "time_numerator",
}
PLAN_KEYS: Final = {
    "binding_sha256",
    "maximum_required_power_index",
    "maximum_terms",
    "mean_denominator",
    "mean_numerator",
    "mode",
    "p0_back_recurrence_steps",
    "positive_mean_has_positive_tail",
    "precision_bits",
    "purpose",
    "requested_tail_denominator",
    "requested_tail_numerator",
    "right_index",
    "right_tail_planning_steps",
    "schema",
    "tail_upper_hex",
    "time_denominator",
    "time_numerator",
}


def _validate_series(value: object) -> dict[str, object]:
    series = _require_exact_dict(value, SERIES_KEYS, label="canonical scalar series")
    records = series["records"]
    if type(records) is not list or len(records) != FORMAL_SCALAR_RECORD_COUNT:
        raise IndependentReplayFailure("canonical scalar record count drifted")
    if (
        series["schema"]
        != "rate_defined_tensor_f0_canonical_scalar_power_series_v1"
        or _fraction_from_fields(
            series,
            "horizon_numerator",
            "horizon_denominator",
            label="series horizon",
        )
        != FORMAL_HORIZON
        or _fraction_from_fields(
            series,
            "uniformization_rate_numerator",
            "uniformization_rate_denominator",
            label="series rate",
        )
        != FORMAL_RATE
        or _fraction_from_fields(
            series,
            "maximum_killing_upper_numerator",
            "maximum_killing_upper_denominator",
            label="series killing",
        )
        != FORMAL_KILLING
        or _fraction_from_fields(
            series,
            "initial_mass_upper_numerator",
            "initial_mass_upper_denominator",
            label="series initial mass",
        )
        != 1
        or series["maximum_power_index"] != FORMAL_MAXIMUM_POWER
        or series["state_arrays_retained"] is not False
        or series["canonical_scalar_records_retained"] is not True
        or series["input_provenance_classification"] != METHOD_INPUT_PROVENANCE
        or series["control_exclusion_proved"] is not False
        or series["science_free_proved"] is not False
        or series["f0_pass"] is not False
    ):
        raise IndependentReplayFailure("canonical scalar series header drifted")
    record_bindings: list[str] = []
    exact_identity = float(FORMAL_KILLING)
    for index, raw in enumerate(records):
        row = _require_exact_dict(
            raw,
            POWER_RECORD_KEYS,
            label=f"scalar record {index}",
        )
        lower = _parse_hex(
            row["lower_hex"],
            label=f"scalar record {index} lower",
            nonnegative=True,
        )
        upper = _parse_hex(
            row["upper_hex"],
            label=f"scalar record {index} upper",
            nonnegative=True,
        )
        binding = _require_sha256(
            row["binding_sha256"],
            label=f"scalar record {index} binding",
        )
        if (
            row["schema"] != "rate_defined_tensor_f0_scalar_power_record_v1"
            or type(row["index"]) is not int
            or row["index"] != index
            or not lower <= exact_identity <= upper
            or binding != _binding_without(row, "binding_sha256")
        ):
            raise IndependentReplayFailure(
                f"scalar record {index} identity enclosure or binding failed"
            )
        record_bindings.append(binding)
    scalar_stream = _require_sha256(
        series["scalar_stream_sha256"],
        label="scalar stream SHA-256",
    )
    expected_series_payload = {
        key: value
        for key, value in series.items()
        if key not in {"records", "series_binding_sha256"}
    }
    expected_series_payload["record_bindings"] = record_bindings
    expected_binding = hashlib.sha256(
        _canonical_json_bytes(expected_series_payload)
    ).hexdigest()
    if (
        _require_sha256(
            series["series_binding_sha256"],
            label="series binding",
        )
        != expected_binding
    ):
        raise IndependentReplayFailure("canonical scalar series binding failed")
    return series


def _geometric_poisson_tail(mean: Fraction, right_index: int) -> float:
    mean_float = float(mean)
    if mean_float <= 0.0 or right_index < math.floor(mean_float):
        raise IndependentReplayFailure("Poisson tail inputs are invalid")
    first_omitted = right_index + 1
    log_probability = (
        -mean_float
        + first_omitted * math.log(mean_float)
        - math.lgamma(first_omitted + 1)
    )
    ratio = mean_float / (right_index + 2)
    if not 0.0 <= ratio < 1.0:
        raise IndependentReplayFailure("Poisson geometric ratio is invalid")
    return math.exp(log_probability) / (1.0 - ratio)


def _validate_poisson(
    value: object,
    *,
    expected_time: Fraction,
    label: str,
) -> dict[str, object]:
    row = _require_exact_dict(value, POISSON_KEYS, label=label)
    mean = _fraction_from_fields(
        row,
        "mean_numerator",
        "mean_denominator",
        label=f"{label} mean",
    )
    requested_tail = _fraction_from_fields(
        row,
        "requested_tail_numerator",
        "requested_tail_denominator",
        label=f"{label} requested tail",
    )
    integer_names = (
        "mode",
        "right_index",
        "terms",
        "precision_bits",
        "mode_initialization_count",
        "p0_back_recurrence_steps",
        "right_tail_planning_steps",
        "planning_recurrence_steps",
        "forward_weight_recurrence_steps",
    )
    for name in integer_names:
        _require_int(row[name], label=f"{label} {name}", minimum=0)
    expected_mean = FORMAL_RATE * expected_time
    right_index = row["right_index"]
    mode = row["mode"]
    tail_upper = _parse_hex(
        row["tail_upper_hex"],
        label=f"{label} tail upper",
        nonnegative=True,
    )
    independent_tail = _geometric_poisson_tail(expected_mean, right_index)
    previous_tail = _geometric_poisson_tail(expected_mean, right_index - 1)
    if (
        row["schema"] != "rate_defined_tensor_f0_centered_poisson_v1"
        or mean != expected_mean
        or mode != expected_mean.numerator // expected_mean.denominator
        or right_index < mode
        or row["terms"] != right_index + 1
        or requested_tail != FORMAL_TAIL_TOLERANCE
        or row["precision_bits"] != FORMAL_PRECISION_BITS
        or row["terms"] > FORMAL_MAXIMUM_TERMS
        or row["mode_initialization_count"] != 1
        or row["p0_back_recurrence_steps"] != mode
        or row["right_tail_planning_steps"] != right_index - mode + 1
        or row["planning_recurrence_steps"]
        != row["p0_back_recurrence_steps"] + row["right_tail_planning_steps"]
        or row["forward_weight_recurrence_steps"] != right_index
        or row["mode_initialized"] is not True
        or row["p0_derived_from_mode"] is not True
        or row["right_tail_geometric"] is not True
        or row["starts_at_zero"] is not True
        or right_index + 4 > FORMAL_MAXIMUM_POWER
        or not independent_tail * (1.0 - 1e-10)
        <= tail_upper
        <= independent_tail * (1.0 + 1e-8)
        or tail_upper > float(FORMAL_TAIL_TOLERANCE) * (1.0 + 1e-12)
        or previous_tail <= float(FORMAL_TAIL_TOLERANCE) * (1.0 - 1e-10)
        or row["binding_sha256"] != _binding_without(row, "binding_sha256")
    ):
        raise IndependentReplayFailure(f"{label} plan or binding failed")
    return row


def _validate_time_row(
    value: object,
    *,
    expected_time: Fraction,
    label: str,
) -> dict[str, object]:
    row = _require_exact_dict(value, TIME_ROW_KEYS, label=label)
    time = _fraction_from_fields(
        row,
        "time_numerator",
        "time_denominator",
        label=f"{label} time",
    )
    if (
        row["schema"] != "rate_defined_tensor_f0_batched_scalar_time_v1"
        or time != expected_time
        or row["absolute_time_from_initial"] is not True
        or row["state_chaining_used"] is not False
    ):
        raise IndependentReplayFailure(f"{label} absolute-time semantics failed")
    _validate_poisson(row["poisson"], expected_time=expected_time, label=f"{label} Poisson")
    jets = row["jets"]
    if type(jets) is not list or len(jets) != 4:
        raise IndependentReplayFailure(f"{label} jet count drifted")
    identity = float(FORMAL_KILLING)
    for order, raw in enumerate(jets):
        jet = _require_exact_dict(raw, JET_KEYS, label=f"{label} J{order}")
        lower = _parse_hex(jet["lower_hex"], label=f"{label} J{order} lower")
        upper = _parse_hex(jet["upper_hex"], label=f"{label} J{order} upper")
        target = identity if order == 0 else 0.0
        if (
            jet["schema"] != "rate_defined_tensor_f0_scalar_jet_interval_v1"
            or jet["order"] != order
            or not lower <= target <= upper
            or jet["binding_sha256"] != _binding_without(jet, "binding_sha256")
        ):
            raise IndependentReplayFailure(f"{label} J{order} enclosure failed")
    magnitudes = row["magnitudes"]
    expected_magnitudes = {
        2: float(2**12).hex(),
        3: float(2**21).hex(),
        4: float(2**30).hex(),
    }
    if type(magnitudes) is not list or len(magnitudes) != 3:
        raise IndependentReplayFailure(f"{label} magnitude count drifted")
    for order, raw in zip((2, 3, 4), magnitudes, strict=True):
        bound = _require_exact_dict(
            raw,
            MAGNITUDE_KEYS,
            label=f"{label} M{order}",
        )
        _parse_hex(
            bound["upper_hex"],
            label=f"{label} M{order} upper",
            nonnegative=True,
        )
        if (
            bound["schema"] != "rate_defined_tensor_f0_scalar_magnitude_v1"
            or bound["order"] != order
            or bound["formula"] != MAGNITUDE_FORMULA
            or bound["upper_hex"] != expected_magnitudes[order]
            or bound["binding_sha256"]
            != _binding_without(bound, "binding_sha256")
        ):
            raise IndependentReplayFailure(f"{label} M{order} bound failed")
    if row["binding_sha256"] != _binding_without(row, "binding_sha256"):
        raise IndependentReplayFailure(f"{label} binding failed")
    return row


def _validate_plan(
    value: object,
    *,
    expected_time: Fraction,
    purpose: str,
    poisson: dict[str, object] | None = None,
) -> dict[str, object]:
    plan = _require_exact_dict(value, PLAN_KEYS, label=f"Poisson plan {purpose}")
    time = _fraction_from_fields(
        plan,
        "time_numerator",
        "time_denominator",
        label=f"Poisson plan {purpose} time",
    )
    mean = _fraction_from_fields(
        plan,
        "mean_numerator",
        "mean_denominator",
        label=f"Poisson plan {purpose} mean",
    )
    requested_tail = _fraction_from_fields(
        plan,
        "requested_tail_numerator",
        "requested_tail_denominator",
        label=f"Poisson plan {purpose} requested tail",
    )
    right_index = _require_int(
        plan["right_index"],
        label=f"Poisson plan {purpose} right index",
        minimum=0,
    )
    mode = _require_int(
        plan["mode"],
        label=f"Poisson plan {purpose} mode",
        minimum=0,
    )
    tail_upper = _parse_hex(
        plan["tail_upper_hex"],
        label=f"Poisson plan {purpose} tail",
        nonnegative=True,
    )
    expected_mean = FORMAL_RATE * expected_time
    if (
        plan["schema"] != "rate_defined_tensor_f0_compiled_batch_poisson_plan_v1"
        or plan["purpose"] != purpose
        or time != expected_time
        or mean != expected_mean
        or mode != expected_mean.numerator // expected_mean.denominator
        or plan["maximum_required_power_index"] != right_index + 4
        or right_index + 4 > FORMAL_MAXIMUM_POWER
        or requested_tail != FORMAL_TAIL_TOLERANCE
        or plan["precision_bits"] != FORMAL_PRECISION_BITS
        or plan["maximum_terms"] != FORMAL_MAXIMUM_TERMS
        or plan["p0_back_recurrence_steps"] != mode
        or plan["right_tail_planning_steps"] != right_index - mode + 1
        or plan["positive_mean_has_positive_tail"] is not True
        or tail_upper > float(FORMAL_TAIL_TOLERANCE) * (1.0 + 1e-12)
        or plan["binding_sha256"] != _binding_without(plan, "binding_sha256")
    ):
        raise IndependentReplayFailure(f"Poisson plan {purpose} failed")
    if poisson is not None and any(
        plan[key] != poisson[key]
        for key in (
            "mean_denominator",
            "mean_numerator",
            "mode",
            "p0_back_recurrence_steps",
            "precision_bits",
            "requested_tail_denominator",
            "requested_tail_numerator",
            "right_index",
            "right_tail_planning_steps",
            "tail_upper_hex",
        )
    ):
        raise IndependentReplayFailure(f"Poisson plan {purpose} cross-binding failed")
    return plan


BUILD_KEYS: Final = {
    "authorizes_scientific_execution",
    "c_source_sha256",
    "compiled_binary_sha256",
    "compiler_binary_sha256",
    "compiler_identity_sha256",
    "f0_pass",
    "fast_math_enabled",
    "fp_contraction_enabled",
    "input_provenance_classification",
    "normalized_compile_command_sha256",
    "optimization_level",
    "post_link_normalization_sha256",
    "python_wrapper_sha256",
    "resource_pass",
    "runtime_probe",
    "schema",
    "science_executed",
    "status",
    "target_identity_sha256",
    "unsafe_fp_optimizations_enabled",
}
RUNTIME_PROBE_KEYS: Final = {
    "abi_version",
    "binary64_layout",
    "dbl_mant_dig",
    "dbl_max_exp",
    "dbl_min_exp",
    "fe_tonearest_value",
    "flt_eval_method",
    "flt_radix",
    "rounding_mode",
    "sizeof_double",
    "smallest_subnormal_preserved",
    "subnormal_arithmetic_preserved",
    "tonearest_active",
}
ACTION_KEYS: Final = {
    "accumulation_order",
    "accumulator_addition_count",
    "actual_arithmetic_operation_count",
    "changes_upstream_enclosure",
    "conservative_arithmetic_operation_budget",
    "dimensions",
    "maximum_dependency_operation_count",
    "present_incoming_edge_count",
    "present_incoming_multiplication_count",
    "relative_error_model",
    "schema",
    "self_multiplication_count",
    "states",
    "underflow_error_model",
    "underflow_event_operation_budget",
    "underflow_unit_hex",
}
REDUCTION_KEYS: Final = {
    "accumulation_order",
    "actual_arithmetic_operation_count",
    "addition_count",
    "block_count",
    "block_size",
    "changes_upstream_enclosure",
    "maximum_dependency_operation_count",
    "multiplication_count",
    "reduction",
    "schema",
    "states",
    "underflow_event_operation_budget",
    "underflow_unit_hex",
    "upstream_enclosure_operation_count",
}
BACKEND_KEYS: Final = {
    "action_operations",
    "authorizes_scientific_execution",
    "build",
    "control_exclusion_proved",
    "dimensions",
    "f0_pass",
    "input_binding_sha256",
    "input_provenance_classification",
    "killing_dot_operations",
    "killing_sha256",
    "mass_reduction_operations",
    "owned_native_readonly_inputs",
    "p_backward_sha256",
    "p_forward_sha256",
    "p_self_sha256",
    "periodic",
    "receipt_sha256",
    "reduction_block_size",
    "resource_pass",
    "schema",
    "science_executed",
    "science_free_proved",
    "states",
    "status",
    "tensor_shape",
}
STREAM_KEYS: Final = {
    "authorizes_scientific_execution",
    "backend_receipt_sha256",
    "control_exclusion_proved",
    "f0_pass",
    "final_power_raw_sha256",
    "final_power_retained",
    "full_power_arrays_retained",
    "initial_raw_sha256",
    "input_provenance_classification",
    "killing_dot_call_count",
    "killing_dot_stream_raw_sha256",
    "mass_reduction_call_count",
    "mass_stream_raw_sha256",
    "maximum_power_index",
    "p_action_call_count",
    "private_owned_readonly_outputs",
    "resource_pass",
    "scalar_streams_retained",
    "schema",
    "science_executed",
    "science_free_proved",
    "status",
    "stream_binding_sha256",
}
RESOURCE_KEYS: Final = {
    "canonical_scalar_endpoint_payload_bytes",
    "canonical_scalar_record_count",
    "compiled_final_state_float64_payload_bytes",
    "compiled_power_stream_run_count",
    "compiled_scalar_stream_float64_payload_bytes",
    "complete_numeric_payload_ledger",
    "complete_process_peak_measured",
    "declared_compiled_peak_float64_payload_bytes_excluding_backend_and_caller",
    "dimensions",
    "evaluation_count",
    "evaluation_float_endpoint_payload_bytes",
    "evaluation_jet_count",
    "evaluation_magnitude_count",
    "f0_pass",
    "float64_stream_payload_formula_complete",
    "killing_dot_call_count",
    "mass_reduction_call_count",
    "maximum_evaluation_count",
    "maximum_power_index",
    "maximum_simultaneous_float64_full_state_vectors_excluding_backend_and_caller",
    "mpfr_payload_bytes_measured",
    "p_action_call_count",
    "production_scale_execution_classified",
    "python_object_overhead_measured",
    "resource_pass",
    "retained_final_full_state_vector_count",
    "retained_full_power_history_count",
    "schema",
    "states",
    "validation_temporary_payload_bytes_measured",
}


def _repeated_float64_sha256(value: float, count: int) -> str:
    unit = struct.pack("<d", value)
    block_count = min(count, 8_192)
    block = unit * block_count
    digest = hashlib.sha256()
    remaining = count
    while remaining >= block_count and block_count:
        digest.update(block)
        remaining -= block_count
    if remaining:
        digest.update(unit * remaining)
    return digest.hexdigest()


def _identity_vector_sha256() -> str:
    digest = hashlib.sha256()
    digest.update(struct.pack("<d", 1.0))
    unit = struct.pack("<d", 0.0)
    block = unit * 8_192
    remaining = FORMAL_STATES - 1
    while remaining >= 8_192:
        digest.update(block)
        remaining -= 8_192
    if remaining:
        digest.update(unit * remaining)
    return digest.hexdigest()


def _validate_build(value: object) -> dict[str, object]:
    build = _require_exact_dict(value, BUILD_KEYS, label="compiled build receipt")
    probe = _require_exact_dict(
        build["runtime_probe"],
        RUNTIME_PROBE_KEYS,
        label="compiled runtime probe",
    )
    expected_probe = {
        "abi_version": 1,
        "binary64_layout": True,
        "dbl_mant_dig": 53,
        "dbl_max_exp": 1024,
        "dbl_min_exp": -1021,
        "fe_tonearest_value": 0,
        "flt_eval_method": 0,
        "flt_radix": 2,
        "rounding_mode": 0,
        "sizeof_double": 8,
        "smallest_subnormal_preserved": True,
        "subnormal_arithmetic_preserved": True,
        "tonearest_active": True,
    }
    for name in (
        "compiled_binary_sha256",
        "compiler_binary_sha256",
        "compiler_identity_sha256",
        "normalized_compile_command_sha256",
        "post_link_normalization_sha256",
        "target_identity_sha256",
    ):
        _require_sha256(build[name], label=f"compiled build {name}")
    if (
        probe != expected_probe
        or build["schema"] != "rate_defined_tensor_f0_compiled_build_receipt_v1"
        or build["status"] != COMPILED_METHOD_STATUS
        or build["python_wrapper_sha256"]
        != EXPECTED_DEPENDENCY_SHA256["compiled_power_python_source"]
        or build["c_source_sha256"]
        != EXPECTED_DEPENDENCY_SHA256["compiled_power_c_source"]
        or build["optimization_level"] != "O3"
        or build["input_provenance_classification"] != COMPILED_INPUT_PROVENANCE
        or any(
            build[name] is not False
            for name in (
                "authorizes_scientific_execution",
                "f0_pass",
                "fast_math_enabled",
                "fp_contraction_enabled",
                "resource_pass",
                "science_executed",
                "unsafe_fp_optimizations_enabled",
            )
        )
    ):
        raise IndependentReplayFailure("compiled build safety receipt failed")
    return build


def _expected_action_ledger() -> dict[str, object]:
    present_edges = (
        sum(
            FORMAL_STATES
            if periodic
            else FORMAL_STATES - FORMAL_STATES // size
            for size, periodic in zip(FORMAL_SHAPE, FORMAL_PERIODIC, strict=True)
        )
        * 2
    )
    additions = 2 * len(FORMAL_SHAPE) * FORMAL_STATES
    conservative = FORMAL_STATES * (4 * len(FORMAL_SHAPE) + 1)
    return {
        "accumulation_order": (
            "self_then_each_dimension_increasing_incoming_forward_then_"
            "incoming_backward_v1"
        ),
        "accumulator_addition_count": additions,
        "actual_arithmetic_operation_count": FORMAL_STATES + present_edges + additions,
        "changes_upstream_enclosure": False,
        "conservative_arithmetic_operation_budget": conservative,
        "dimensions": 3,
        "maximum_dependency_operation_count": 7,
        "present_incoming_edge_count": present_edges,
        "present_incoming_multiplication_count": present_edges,
        "relative_error_model": (
            "gamma_(2*d+1)_per_nonnegative_contribution_path_v1"
        ),
        "schema": "rate_defined_tensor_f0_compiled_action_ledger_v1",
        "self_multiplication_count": FORMAL_STATES,
        "states": FORMAL_STATES,
        "underflow_error_model": "N*(4*d+1)*2^-1074_v1",
        "underflow_event_operation_budget": conservative,
        "underflow_unit_hex": "0x0.0000000000001p-1022",
    }


def _expected_reduction_ledger(*, killing: bool) -> dict[str, object]:
    blocks = (FORMAL_STATES + FORMAL_BLOCK_SIZE - 1) // FORMAL_BLOCK_SIZE
    operations = (2 if killing else 1) * FORMAL_STATES + blocks
    return {
        "accumulation_order": (
            "strict_flat_index_multiply_then_left_to_right_add_v1"
            if killing
            else "strict_flat_index_left_to_right_v1"
        ),
        "actual_arithmetic_operation_count": (
            2 * FORMAL_STATES if killing else FORMAL_STATES
        ),
        "addition_count": FORMAL_STATES,
        "block_count": blocks,
        "block_size": FORMAL_BLOCK_SIZE,
        "changes_upstream_enclosure": False,
        "maximum_dependency_operation_count": (
            FORMAL_STATES + 1 if killing else FORMAL_STATES
        ),
        "multiplication_count": FORMAL_STATES if killing else 0,
        "reduction": "positive_killing_dot" if killing else "positive_mass",
        "schema": "rate_defined_tensor_f0_compiled_reduction_ledger_v1",
        "states": FORMAL_STATES,
        "underflow_event_operation_budget": operations,
        "underflow_unit_hex": "0x0.0000000000001p-1022",
        "upstream_enclosure_operation_count": operations,
    }


def _validate_backend(
    value: object,
    *,
    build: dict[str, object],
) -> dict[str, object]:
    backend = _require_exact_dict(value, BACKEND_KEYS, label="compiled backend receipt")
    _require_exact_dict(backend["action_operations"], ACTION_KEYS, label="action ledger")
    _require_exact_dict(
        backend["mass_reduction_operations"],
        REDUCTION_KEYS,
        label="mass reduction ledger",
    )
    _require_exact_dict(
        backend["killing_dot_operations"],
        REDUCTION_KEYS,
        label="killing reduction ledger",
    )
    p_self = _repeated_float64_sha256(1.0, FORMAL_STATES)
    killing = _repeated_float64_sha256(float(FORMAL_KILLING), FORMAL_STATES)
    axis_zero_hashes = [
        _repeated_float64_sha256(0.0, size) for size in FORMAL_SHAPE
    ]
    input_payload = {
        "killing_sha256": killing,
        "p_backward_sha256": axis_zero_hashes,
        "p_forward_sha256": axis_zero_hashes,
        "p_self_sha256": p_self,
        "periodic": list(FORMAL_PERIODIC),
        "reduction_block_size": FORMAL_BLOCK_SIZE,
        "tensor_shape": list(FORMAL_SHAPE),
    }
    if (
        backend["schema"] != "rate_defined_tensor_f0_compiled_backend_receipt_v1"
        or backend["status"] != COMPILED_METHOD_STATUS
        or backend["tensor_shape"] != list(FORMAL_SHAPE)
        or backend["periodic"] != list(FORMAL_PERIODIC)
        or backend["states"] != FORMAL_STATES
        or backend["dimensions"] != 3
        or backend["reduction_block_size"] != FORMAL_BLOCK_SIZE
        or backend["p_self_sha256"] != p_self
        or backend["p_forward_sha256"] != axis_zero_hashes
        or backend["p_backward_sha256"] != axis_zero_hashes
        or backend["killing_sha256"] != killing
        or backend["input_binding_sha256"]
        != hashlib.sha256(_canonical_json_bytes(input_payload)).hexdigest()
        or backend["owned_native_readonly_inputs"] is not True
        or backend["input_provenance_classification"]
        != COMPILED_INPUT_PROVENANCE
        or backend["build"] != build
        or backend["action_operations"] != _expected_action_ledger()
        or backend["mass_reduction_operations"]
        != _expected_reduction_ledger(killing=False)
        or backend["killing_dot_operations"]
        != _expected_reduction_ledger(killing=True)
        or any(
            backend[name] is not False
            for name in (
                "authorizes_scientific_execution",
                "control_exclusion_proved",
                "f0_pass",
                "resource_pass",
                "science_executed",
                "science_free_proved",
            )
        )
        or backend["receipt_sha256"] != _binding_with_zero(backend, "receipt_sha256")
    ):
        raise IndependentReplayFailure("compiled backend identity replay failed")
    return backend


def _validate_stream(
    value: object,
    *,
    backend: dict[str, object],
) -> dict[str, object]:
    stream = _require_exact_dict(value, STREAM_KEYS, label="compiled stream receipt")
    identity_vector = _identity_vector_sha256()
    expected_mass_stream = _repeated_float64_sha256(
        1.0,
        FORMAL_SCALAR_RECORD_COUNT,
    )
    expected_killing_stream = _repeated_float64_sha256(
        float(FORMAL_KILLING),
        FORMAL_SCALAR_RECORD_COUNT,
    )
    if (
        stream["schema"] != "rate_defined_tensor_f0_compiled_stream_receipt_v1"
        or stream["status"] != COMPILED_METHOD_STATUS
        or stream["backend_receipt_sha256"] != backend["receipt_sha256"]
        or stream["initial_raw_sha256"] != identity_vector
        or stream["final_power_raw_sha256"] != identity_vector
        or stream["mass_stream_raw_sha256"] != expected_mass_stream
        or stream["killing_dot_stream_raw_sha256"] != expected_killing_stream
        or stream["maximum_power_index"] != FORMAL_MAXIMUM_POWER
        or stream["p_action_call_count"] != FORMAL_MAXIMUM_POWER
        or stream["mass_reduction_call_count"] != FORMAL_SCALAR_RECORD_COUNT
        or stream["killing_dot_call_count"] != FORMAL_SCALAR_RECORD_COUNT
        or stream["final_power_retained"] is not True
        or stream["full_power_arrays_retained"] != 1
        or stream["private_owned_readonly_outputs"] is not True
        or stream["scalar_streams_retained"] is not True
        or stream["input_provenance_classification"]
        != COMPILED_INPUT_PROVENANCE
        or any(
            stream[name] is not False
            for name in (
                "authorizes_scientific_execution",
                "control_exclusion_proved",
                "f0_pass",
                "resource_pass",
                "science_executed",
                "science_free_proved",
            )
        )
        or stream["stream_binding_sha256"]
        != _binding_with_zero(stream, "stream_binding_sha256")
    ):
        raise IndependentReplayFailure("compiled identity power stream replay failed")
    return stream


def _validate_resources(value: object) -> dict[str, object]:
    resources = _require_exact_dict(value, RESOURCE_KEYS, label="resource ledger")
    final_bytes = FORMAL_STATES * 8
    scalar_bytes = FORMAL_SCALAR_RECORD_COUNT * 16
    expected = {
        "canonical_scalar_endpoint_payload_bytes": scalar_bytes,
        "canonical_scalar_record_count": FORMAL_SCALAR_RECORD_COUNT,
        "compiled_final_state_float64_payload_bytes": final_bytes,
        "compiled_power_stream_run_count": 1,
        "compiled_scalar_stream_float64_payload_bytes": scalar_bytes,
        "complete_numeric_payload_ledger": False,
        "complete_process_peak_measured": False,
        "declared_compiled_peak_float64_payload_bytes_excluding_backend_and_caller": (
            4 * final_bytes + scalar_bytes
        ),
        "dimensions": 3,
        "evaluation_count": FORMAL_TOPOLOGY_COUNT,
        "evaluation_float_endpoint_payload_bytes": 45_056,
        "evaluation_jet_count": 2_048,
        "evaluation_magnitude_count": 1_536,
        "f0_pass": False,
        "float64_stream_payload_formula_complete": True,
        "killing_dot_call_count": FORMAL_SCALAR_RECORD_COUNT,
        "mass_reduction_call_count": FORMAL_SCALAR_RECORD_COUNT,
        "maximum_evaluation_count": FORMAL_TOPOLOGY_COUNT,
        "maximum_power_index": FORMAL_MAXIMUM_POWER,
        "maximum_simultaneous_float64_full_state_vectors_excluding_backend_and_caller": 4,
        "mpfr_payload_bytes_measured": False,
        "p_action_call_count": FORMAL_MAXIMUM_POWER,
        "production_scale_execution_classified": False,
        "python_object_overhead_measured": False,
        "resource_pass": False,
        "retained_final_full_state_vector_count": 1,
        "retained_full_power_history_count": 0,
        "schema": "rate_defined_tensor_f0_compiled_batch_resources_v1",
        "states": FORMAL_STATES,
        "validation_temporary_payload_bytes_measured": False,
    }
    if resources != expected:
        raise IndependentReplayFailure("compiled resource ledger drifted")
    return resources


METADATA_KEYS: Final = {
    "coefficient_l1_uncertainty_upper",
    "evaluation_times",
    "initial_l1_radius_upper",
    "initial_mass_cap",
    "maximum_center_row_sum",
    "maximum_killing_uncertainty",
    "maximum_killing_upper",
    "maximum_poisson_terms",
    "mpfr_precision_bits",
    "schema",
    "series_horizon",
    "tail_tolerance",
    "uniformization_rate",
}
EVIDENCE_KEYS: Final = {
    "evaluations",
    "evidence_binding_sha256",
    "metadata",
    "receipt",
    "schema",
    "series",
}
RECEIPT_KEYS: Final = {
    "absolute_time_reevaluation_used",
    "authorizes_scientific_execution",
    "batched_scalar_runtime_identity",
    "batched_scalar_source_sha256",
    "canonical_series_binding_sha256",
    "canonical_series_bytes_sha256",
    "compiled_backend_receipt",
    "compiled_backend_receipt_sha256",
    "compiled_build_receipt",
    "compiled_power_stream_run_count",
    "compiled_stream_receipt",
    "control_exclusion_proved",
    "evaluation_plans",
    "external_stream_replay_complete",
    "f0_pass",
    "final_power_raw_sha256",
    "horizon_plan",
    "independent_source_audit_complete",
    "initial_mass_cap_independently_proved",
    "initial_raw_sha256",
    "input_provenance_classification",
    "integration_source_observation_authoritative",
    "integration_source_sha256",
    "maximum_finite_difference_order",
    "maximum_state_radius_upper_hex",
    "metadata_binding_sha256",
    "method_metadata_preconditions_proved",
    "production_scale_execution_classified",
    "receipt_sha256",
    "repeated_p_actions_during_reevaluation",
    "resource_pass",
    "resources",
    "returned_jet_orders",
    "scalar_stream_sha256",
    "schema",
    "science_executed",
    "science_free_proved",
    "status",
    "topology_pass",
}


def _validate_metadata(
    value: object,
    *,
    topology: tuple[Fraction, ...],
) -> dict[str, object]:
    metadata = _require_exact_dict(value, METADATA_KEYS, label="compiled metadata")
    times = _parse_fraction_list(
        metadata["evaluation_times"],
        label="metadata evaluation times",
        expected_count=FORMAL_TOPOLOGY_COUNT,
    )
    if (
        metadata["schema"] != "rate_defined_tensor_f0_compiled_batch_metadata_v1"
        or times != topology
        or _require_fraction(
            metadata["coefficient_l1_uncertainty_upper"],
            label="coefficient uncertainty",
        )
        != 0
        or _require_fraction(
            metadata["initial_l1_radius_upper"],
            label="initial radius",
        )
        != 0
        or _require_fraction(metadata["initial_mass_cap"], label="initial mass cap")
        != 1
        or _require_fraction(
            metadata["maximum_center_row_sum"],
            label="maximum centre row sum",
        )
        != 1
        or _require_fraction(
            metadata["maximum_killing_uncertainty"],
            label="maximum killing uncertainty",
        )
        != 0
        or _require_fraction(
            metadata["maximum_killing_upper"],
            label="maximum killing upper",
        )
        != FORMAL_KILLING
        or metadata["maximum_poisson_terms"] != FORMAL_MAXIMUM_TERMS
        or metadata["mpfr_precision_bits"] != FORMAL_PRECISION_BITS
        or _require_fraction(metadata["series_horizon"], label="series horizon")
        != FORMAL_HORIZON
        or _require_fraction(metadata["tail_tolerance"], label="tail tolerance")
        != FORMAL_TAIL_TOLERANCE
        or _require_fraction(metadata["uniformization_rate"], label="rate")
        != FORMAL_RATE
    ):
        raise IndependentReplayFailure("compiled method metadata drifted")
    return metadata


def _validate_compiled_evidence(
    value: object,
    *,
    topology: tuple[Fraction, ...],
) -> dict[str, object]:
    evidence = _require_exact_dict(value, EVIDENCE_KEYS, label="compiled evidence")
    if evidence["schema"] != "rate_defined_tensor_f0_compiled_batch_evidence_v1":
        raise IndependentReplayFailure("compiled evidence schema drifted")
    metadata = _validate_metadata(evidence["metadata"], topology=topology)
    series = _validate_series(evidence["series"])
    evaluations = evidence["evaluations"]
    if type(evaluations) is not list or len(evaluations) != FORMAL_TOPOLOGY_COUNT:
        raise IndependentReplayFailure("compiled evaluation count drifted")
    validated_evaluations: list[dict[str, object]] = []
    for index, (raw, expected_time) in enumerate(
        zip(evaluations, topology, strict=True)
    ):
        validated_evaluations.append(
            _validate_time_row(
                raw,
                expected_time=expected_time,
                label=f"topology evaluation {index}",
            )
        )

    receipt = _require_exact_dict(
        evidence["receipt"],
        RECEIPT_KEYS,
        label="compiled batch receipt",
    )
    build = _validate_build(receipt["compiled_build_receipt"])
    backend = _validate_backend(receipt["compiled_backend_receipt"], build=build)
    stream = _validate_stream(receipt["compiled_stream_receipt"], backend=backend)
    resources = _validate_resources(receipt["resources"])
    horizon = _validate_plan(
        receipt["horizon_plan"],
        expected_time=FORMAL_HORIZON,
        purpose="series_horizon",
    )
    if (
        horizon["mode"] != FORMAL_HORIZON_MODE
        or horizon["right_index"] != FORMAL_HORIZON_RIGHT_INDEX
        or horizon["maximum_required_power_index"] != FORMAL_MAXIMUM_POWER
    ):
        raise IndependentReplayFailure("formal horizon Poisson plan drifted")
    plans = receipt["evaluation_plans"]
    if type(plans) is not list or len(plans) != FORMAL_TOPOLOGY_COUNT:
        raise IndependentReplayFailure("evaluation Poisson plan count drifted")
    for index, (raw_plan, expected_time, evaluation) in enumerate(
        zip(plans, topology, validated_evaluations, strict=True)
    ):
        _validate_plan(
            raw_plan,
            expected_time=expected_time,
            purpose=f"evaluation_{index}",
            poisson=evaluation["poisson"],
        )

    maximum_state_radius = _parse_hex(
        receipt["maximum_state_radius_upper_hex"],
        label="maximum state radius",
        nonnegative=True,
    )
    identity_vector = _identity_vector_sha256()
    canonical_series_bytes = _canonical_json_bytes(series)
    for name in (
        "final_power_raw_sha256",
        "initial_raw_sha256",
        "receipt_sha256",
        "scalar_stream_sha256",
    ):
        _require_sha256(receipt[name], label=f"compiled receipt {name}")
    if (
        receipt["schema"] != "rate_defined_tensor_f0_compiled_batch_receipt_v1"
        or receipt["status"] != COMPILED_BATCH_STATUS
        or receipt["integration_source_sha256"]
        != EXPECTED_DEPENDENCY_SHA256["compiled_batch_source"]
        or receipt["batched_scalar_source_sha256"]
        != EXPECTED_DEPENDENCY_SHA256["batched_scalar_source"]
        or receipt["metadata_binding_sha256"]
        != hashlib.sha256(_canonical_json_bytes(metadata)).hexdigest()
        or receipt["canonical_series_binding_sha256"]
        != series["series_binding_sha256"]
        or receipt["canonical_series_bytes_sha256"]
        != hashlib.sha256(canonical_series_bytes).hexdigest()
        or receipt["scalar_stream_sha256"] != series["scalar_stream_sha256"]
        or receipt["compiled_backend_receipt_sha256"] != backend["receipt_sha256"]
        or receipt["compiled_power_stream_run_count"] != 1
        or receipt["initial_raw_sha256"] != identity_vector
        or receipt["final_power_raw_sha256"] != identity_vector
        or receipt["maximum_finite_difference_order"] != 4
        or receipt["returned_jet_orders"] != [0, 1, 2, 3]
        or receipt["repeated_p_actions_during_reevaluation"] != 0
        or receipt["absolute_time_reevaluation_used"] is not True
        or receipt["input_provenance_classification"] != METHOD_INPUT_PROVENANCE
        or maximum_state_radius > float(FORMAL_MAXIMUM_STATE_RADIUS)
        or resources["p_action_call_count"] != stream["p_action_call_count"]
        or any(
            receipt[name] is not False
            for name in (
                "authorizes_scientific_execution",
                "control_exclusion_proved",
                "external_stream_replay_complete",
                "f0_pass",
                "independent_source_audit_complete",
                "initial_mass_cap_independently_proved",
                "integration_source_observation_authoritative",
                "method_metadata_preconditions_proved",
                "production_scale_execution_classified",
                "resource_pass",
                "science_executed",
                "science_free_proved",
                "topology_pass",
            )
        )
        or receipt["receipt_sha256"] != _binding_without(receipt, "receipt_sha256")
    ):
        raise IndependentReplayFailure("compiled batch receipt replay failed")
    if evidence["evidence_binding_sha256"] != _binding_with_zero(
        evidence,
        "evidence_binding_sha256",
    ):
        raise IndependentReplayFailure("compiled evidence binding failed")
    return evidence


CANONICAL_KEYS: Final = {
    "compiled_batch_evidence",
    "dependencies",
    "fixture",
    "mandatory_tail_evaluations",
    "payload_binding_sha256",
    "promotion_flags",
    "schedule",
    "schema",
    "status",
}


def validate_canonical_artifact_bytes(
    payload: bytes,
    *,
    topology: tuple[Fraction, ...],
) -> dict[str, object]:
    """Validate the formal canonical method payload without runner imports."""

    parsed = _strict_json_loads(
        payload,
        label="canonical resource artifact",
        maximum_bytes=MAXIMUM_CANONICAL_BYTES,
    )
    row = _require_exact_dict(parsed, CANONICAL_KEYS, label="canonical resource")
    if (
        _canonical_json_bytes(row) != payload
        or row["schema"] != CANONICAL_SCHEMA
        or row["status"] != CANONICAL_STATUS
        or row["promotion_flags"] != PROMOTION_FLAGS
        or row["fixture"] != _expected_fixture()
        or row["schedule"] != _expected_schedule_projection(topology)
        or row["dependencies"] != _expected_dependencies()
    ):
        raise IndependentReplayFailure("canonical resource header drifted")
    _validate_compiled_evidence(
        row["compiled_batch_evidence"],
        topology=topology,
    )
    tails = row["mandatory_tail_evaluations"]
    if type(tails) is not list or len(tails) != len(FORMAL_TAIL_TIMES):
        raise IndependentReplayFailure("mandatory tail evaluation count drifted")
    validated_tails = [
        _validate_time_row(
            raw,
            expected_time=time,
            label=f"mandatory tail evaluation {index}",
        )
        for index, (raw, time) in enumerate(zip(tails, FORMAL_TAIL_TIMES, strict=True))
    ]
    horizon = row["compiled_batch_evidence"]["receipt"]["horizon_plan"]
    final_tail_poisson = validated_tails[-1]["poisson"]
    if any(
        horizon[key] != final_tail_poisson[key]
        for key in (
            "mean_denominator",
            "mean_numerator",
            "mode",
            "p0_back_recurrence_steps",
            "precision_bits",
            "requested_tail_denominator",
            "requested_tail_numerator",
            "right_index",
            "right_tail_planning_steps",
            "tail_upper_hex",
        )
    ):
        raise IndependentReplayFailure("horizon/tail Poisson cross-binding failed")
    if row["payload_binding_sha256"] != _binding_with_zero(
        row,
        "payload_binding_sha256",
    ):
        raise IndependentReplayFailure("canonical resource payload binding failed")
    return row


SIDECAR_KEYS: Final = {
    "canonical_artifact",
    "dependencies_after",
    "dependencies_before",
    "failure_reasons",
    "fixture",
    "measurement",
    "method_counts",
    "promotion_flags",
    "resource_caps_satisfied",
    "runner_source_sha256_same_process_observation",
    "runner_source_sha256_same_process_observation_authoritative",
    "schedule",
    "schema",
    "status",
}
MEASUREMENT_KEYS: Final = {
    "host_peak_footprint_bytes",
    "host_peak_footprint_method",
    "peak_rss_bytes",
    "process_swap_count_after",
    "process_swap_count_before",
    "process_swap_delta",
    "wall_seconds_hex",
}
METHOD_COUNT_KEYS: Final = {
    "canonical_scalar_record_count",
    "compiled_power_stream_run_count",
    "mandatory_tail_evaluation_count",
    "maximum_power_index",
    "p_action_call_count",
    "repeated_p_actions_during_reevaluation",
    "topology_evaluation_count",
}


def _validate_sidecar(
    payload: bytes,
    *,
    canonical_path: Path,
    canonical_payload: bytes,
    topology: tuple[Fraction, ...],
) -> tuple[dict[str, object], str, list[str]]:
    parsed = _strict_json_loads(
        payload,
        label="resource observation sidecar",
        maximum_bytes=MAXIMUM_SIDECAR_BYTES,
    )
    row = _require_exact_dict(parsed, SIDECAR_KEYS, label="resource sidecar")
    if _pretty_json_bytes(row) != payload:
        raise IndependentReplayFailure("resource sidecar bytes are not canonical pretty JSON")
    artifact = _require_exact_dict(
        row["canonical_artifact"],
        {"absolute_path", "byte_count", "sha256"},
        label="sidecar canonical artifact binding",
    )
    measurement = _require_exact_dict(
        row["measurement"],
        MEASUREMENT_KEYS,
        label="resource measurement",
    )
    counts = _require_exact_dict(
        row["method_counts"],
        METHOD_COUNT_KEYS,
        label="resource method counts",
    )
    wall_seconds = _parse_hex(
        measurement["wall_seconds_hex"],
        label="resource wall seconds",
        nonnegative=True,
    )
    footprint = _require_int(
        measurement["host_peak_footprint_bytes"],
        label="host peak footprint",
        minimum=0,
    )
    peak_rss = _require_int(
        measurement["peak_rss_bytes"],
        label="peak RSS",
        minimum=0,
    )
    swaps_before = _require_int(
        measurement["process_swap_count_before"],
        label="swap count before",
        minimum=0,
    )
    swaps_after = _require_int(
        measurement["process_swap_count_after"],
        label="swap count after",
        minimum=0,
    )
    swap_delta = _require_int(
        measurement["process_swap_delta"],
        label="swap delta",
        minimum=0,
    )
    failures: list[str] = []
    if wall_seconds > FORMAL_MAXIMUM_WALL_SECONDS:
        failures.append("wall_cap_exceeded")
    if peak_rss > FORMAL_MAXIMUM_RSS_BYTES:
        failures.append("rss_cap_exceeded")
    if footprint > FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES:
        failures.append("peak_footprint_cap_exceeded")
    if swap_delta > FORMAL_MAXIMUM_SWAP_DELTA:
        failures.append("process_swap_cap_exceeded")
    expected_counts = {
        "canonical_scalar_record_count": FORMAL_SCALAR_RECORD_COUNT,
        "compiled_power_stream_run_count": 1,
        "mandatory_tail_evaluation_count": 4,
        "maximum_power_index": FORMAL_MAXIMUM_POWER,
        "p_action_call_count": FORMAL_MAXIMUM_POWER,
        "repeated_p_actions_during_reevaluation": 0,
        "topology_evaluation_count": FORMAL_TOPOLOGY_COUNT,
    }
    if (
        artifact["absolute_path"] != str(canonical_path)
        or artifact["byte_count"] != len(canonical_payload)
        or artifact["sha256"] != hashlib.sha256(canonical_payload).hexdigest()
        or row["dependencies_before"] != _expected_dependencies()
        or row["dependencies_after"] != _expected_dependencies()
        or row["fixture"] != _expected_fixture()
        or row["schedule"] != _expected_schedule_projection(topology)
        or counts != expected_counts
        or measurement["host_peak_footprint_method"]
        != "darwin_phys_footprint_peak"
        or swaps_after - swaps_before != swap_delta
        or swap_delta != 0
        or row["promotion_flags"] != PROMOTION_FLAGS
        or row["runner_source_sha256_same_process_observation"]
        != EXPECTED_RUNNER_SOURCE_SHA256
        or row["runner_source_sha256_same_process_observation_authoritative"]
        is not False
        or row["schema"] != OBSERVATION_SCHEMA
    ):
        raise IndependentReplayFailure("resource sidecar binding or counts failed")
    if row["failure_reasons"] != failures:
        raise IndependentReplayFailure("resource sidecar failure reasons failed replay")
    if not failures:
        if (
            row["status"] != PASS_OBSERVATION_STATUS
            or row["resource_caps_satisfied"] is not True
        ):
            raise IndependentReplayFailure("passing resource sidecar status drifted")
        terminal_status = PASS_REPLAY_STATUS
    else:
        if (
            row["status"] != HOLD_OBSERVATION_STATUS
            or row["resource_caps_satisfied"] is not False
        ):
            raise IndependentReplayFailure("held resource sidecar status drifted")
        terminal_status = HOLD_REPLAY_STATUS
    return row, terminal_status, failures


def build_independent_replay_receipt(
    *,
    canonical_artifact: Path,
    resource_sidecar: Path,
    topology_schedule: Path,
    report_root: Path,
) -> dict[str, object]:
    """Replay the formal evidence and return a canonical terminal receipt."""

    for label, path in (
        ("canonical artifact", canonical_artifact),
        ("resource sidecar", resource_sidecar),
        ("topology schedule", topology_schedule),
    ):
        if not isinstance(path, Path) or not path.is_absolute():
            raise IndependentReplayFailure(f"{label} path must be absolute")
    schedule_bytes = _stable_read(
        topology_schedule,
        label="topology schedule",
        maximum_bytes=MAXIMUM_SCHEDULE_BYTES,
    )
    schedule, topology = _validate_schedule(schedule_bytes, report_root=report_root)
    _rehash_dependencies(report_root)
    canonical_bytes = _stable_read(
        canonical_artifact,
        label="canonical artifact",
        maximum_bytes=MAXIMUM_CANONICAL_BYTES,
    )
    canonical = validate_canonical_artifact_bytes(
        canonical_bytes,
        topology=topology,
    )
    sidecar_bytes = _stable_read(
        resource_sidecar,
        label="resource sidecar",
        maximum_bytes=MAXIMUM_SIDECAR_BYTES,
    )
    sidecar, terminal_status, failures = _validate_sidecar(
        sidecar_bytes,
        canonical_path=canonical_artifact,
        canonical_payload=canonical_bytes,
        topology=topology,
    )
    validator_sha256 = _stable_sha256(
        Path(__file__).resolve(strict=True),
        label="independent validator source",
    )
    receipt = {
        "artifacts": {
            "canonical_resource": {
                "absolute_path": str(canonical_artifact),
                "byte_count": len(canonical_bytes),
                "sha256": hashlib.sha256(canonical_bytes).hexdigest(),
            },
            "resource_sidecar": {
                "absolute_path": str(resource_sidecar),
                "byte_count": len(sidecar_bytes),
                "sha256": hashlib.sha256(sidecar_bytes).hexdigest(),
            },
            "topology_schedule": {
                "absolute_path": str(topology_schedule),
                "byte_count": len(schedule_bytes),
                "sha256": hashlib.sha256(schedule_bytes).hexdigest(),
            },
        },
        "checks": {
            "absolute_time_rows_validated": 516,
            "canonical_ascii_and_key_sets_validated": True,
            "canonical_scalar_records_validated": FORMAL_SCALAR_RECORD_COUNT,
            "dependency_files_rehashed": len(EXPECTED_DEPENDENCY_SHA256) + 3,
            "formal_schedule_union_count": FORMAL_UNION_COUNT,
            "identity_fixture_reconstructed": True,
            "nested_sha_bindings_replayed": True,
            "poisson_plans_independently_checked": 517,
            "resource_caps_satisfied": not failures,
            "sidecar_failure_reasons_replayed": True,
        },
        "failure_reasons": failures,
        "frozen_caps": {
            "maximum_peak_footprint_bytes": FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES,
            "maximum_process_swap_delta": FORMAL_MAXIMUM_SWAP_DELTA,
            "maximum_rss_bytes": FORMAL_MAXIMUM_RSS_BYTES,
            "maximum_wall_seconds": int(FORMAL_MAXIMUM_WALL_SECONDS),
        },
        "input_bindings": {
            "canonical_payload_binding_sha256": canonical[
                "payload_binding_sha256"
            ],
            "compiled_evidence_binding_sha256": canonical[
                "compiled_batch_evidence"
            ]["evidence_binding_sha256"],
            "resource_observation_runner_source_sha256": sidecar[
                "runner_source_sha256_same_process_observation"
            ],
            "schedule_payload_binding_sha256": schedule[
                "payload_binding_sha256"
            ],
            "series_binding_sha256": canonical["compiled_batch_evidence"][
                "series"
            ]["series_binding_sha256"],
            "validator_source_sha256": validator_sha256,
        },
        "observed_measurements": dict(sidecar["measurement"]),
        "promotion_flags": dict(REPLAY_PROMOTION_FLAGS),
        "receipt_binding_sha256": SHA256_ZERO,
        "schema": REPLAY_SCHEMA,
        "status": terminal_status,
    }
    receipt["receipt_binding_sha256"] = _binding_with_zero(
        receipt,
        "receipt_binding_sha256",
    )
    return receipt


def require_formal_resource_pass(receipt: dict[str, object]) -> None:
    """Fail closed unless an independently replayed formal PASS was obtained."""

    if (
        type(receipt) is not dict
        or receipt.get("schema") != REPLAY_SCHEMA
        or receipt.get("status") != PASS_REPLAY_STATUS
        or receipt.get("failure_reasons") != []
        or receipt.get("promotion_flags") != REPLAY_PROMOTION_FLAGS
        or receipt.get("receipt_binding_sha256")
        != _binding_with_zero(receipt, "receipt_binding_sha256")
    ):
        raise IndependentReplayFailure(
            "formal resource PASS required; independent replay is HOLD"
        )


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Independently replay the formal F0 resource artifacts."
    )
    parser.add_argument("--canonical-artifact", required=True, type=Path)
    parser.add_argument("--resource-sidecar", required=True, type=Path)
    parser.add_argument("--topology-schedule", required=True, type=Path)
    parser.add_argument("--report-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    try:
        receipt = build_independent_replay_receipt(
            canonical_artifact=arguments.canonical_artifact,
            resource_sidecar=arguments.resource_sidecar,
            topology_schedule=arguments.topology_schedule,
            report_root=arguments.report_root,
        )
        payload = _canonical_json_bytes(receipt)
        _write_exclusive(arguments.output, payload)
    except IndependentReplayFailure as error:
        print(f"{HOLD_REPLAY_STATUS}: {error}", file=sys.stderr)
        return 2
    print(str(arguments.output))
    print(receipt["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
