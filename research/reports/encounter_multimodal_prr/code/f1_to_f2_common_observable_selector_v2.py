"""Science-free F1-to-F2 common-observable selector contract, version 2.

This module contains only deterministic geometry, canonical-byte, exact-count,
central-state, special-function-contract, and counter-RNG machinery.  Importing
or executing it cannot run F1, positive-budget semigroups, or Monte Carlo.

The process boundary is a cooperative public-API and resource-isolation
contract.  It rejects ordinary in-process and direct-CLI bypasses, but active
same-UID mutation or a hostile importer deliberately invoking private names is
outside its threat model; Python private objects are not security capabilities.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import re
import resource
import stat
import struct
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable, Iterable, Mapping, Sequence

import gmpy2
import jsonschema

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "f1_to_f2_common_observable_selector_v2.schema.json"
PHILOX_SPEC_PATH = HERE / "f1_to_f2_philox4x32_10_spec_v1.json"
TEST_KEY_SET_PATH = HERE / "f1_to_f2_selector_test_keys_v1.json"
CENTRAL_PROJECTION_SPEC_PATH = HERE / "f1_to_f2_central_projection_v1.json"
RUNTIME_SPEC_PATH = HERE / "f1_to_f2_common_observable_selector_v2_runtime.json"

EXPECTED_PHILOX_SPEC_SHA256 = "822a8aa14973227516669372a65ad55e12e63b84151bc51e593b61a2ef45a8d5"
EXPECTED_TEST_KEY_SET_SHA256 = "cb273018dbca49cf09399e1504ffe5282eec84513891e2ddc4e79d3995dc185d"
EXPECTED_CENTRAL_PROJECTION_SHA256 = (
    "ca55da389ac6b72b3359d5000249b52cd836db4ab8eacf19397a3b5d73f4c5d5"
)
EXPECTED_RUNTIME_SPEC_SHA256 = "3ddd0fda64a6cb739776b78056050089dfb20662735356189ac0237fe18ba86c"
EXPECTED_TEST_KEYS = (
    0x0000000000000000,
    0xFFFFFFFFFFFFFFFF,
    0x0123456789ABCDEF,
    0xFEDCBA9876543210,
    0x9E3779B9BB67AE85,
    0xD2511F53CD9E8D57,
    0x0000000100000000,
    0x0000000000000001,
)
CP_WORKER_TIMEOUT_SECONDS = 30
CP_WORKER_PEAK_RSS_CAP_BYTES = 256 * 1024 * 1024
SPECIAL_WORKER_RESPONSE_CAP_BYTES = 65_536
SPECIAL_WORKER_CONCURRENCY = 1
SPECIAL_WORKER_LOCK_DIRECTORY = Path("/tmp").resolve() / (
    f"encounter-selector-v2-special-worker-{os.getuid()}"
)
SPECIAL_WORKER_LOCK_PATH = SPECIAL_WORKER_LOCK_DIRECTORY / "worker.lock"
SPECIAL_WORKER_CAPABILITY_FD_ENV = "ENCOUNTER_SELECTOR_V2_CAPABILITY_FD"
SPECIAL_WORKER_CAPABILITY_SHA_ENV = "ENCOUNTER_SELECTOR_V2_CAPABILITY_SHA256"
SPECIAL_WORKER_LOCK_FD_ENV = "ENCOUNTER_SELECTOR_V2_LOCK_FD"
SPECIAL_WORKER_PARENT_PID_ENV = "ENCOUNTER_SELECTOR_V2_PARENT_PID"
SPECIAL_WORKER_DEADLINE_NS_ENV = "ENCOUNTER_SELECTOR_V2_DEADLINE_MONOTONIC_NS"
_SPECIAL_WORKER_THREAD_SLOT = threading.BoundedSemaphore(SPECIAL_WORKER_CONCURRENCY)
_SPECIAL_WORKER_OPEN_DESCRIPTORS: set[int] = set()
_SPECIAL_WORKER_DESCRIPTOR_GUARD = threading.Lock()
LOADED_SELECTOR_SOURCE_SHA256: str
LOADED_RUNTIME_BINARY_SHA256: str

CONFIGURATION_ORDER = (
    "O113/Base",
    "E128/Base",
    "O129/Base",
    "O161/Base",
    "M+",
    "R+",
    "MR+",
    "MR+F",
    "A_M",
    "A_R",
    "A_Y",
    "A_MRY",
)
REFERENCE_CONFIGURATION = "MR+F"
CONTROL_ORDER = ("lp_m1", "lp_m2", "lp_m3")
ROLE_ORDER = {
    "lp_m1": ("P1",),
    "lp_m2": ("P1", "Q1", "P2"),
    "lp_m3": ("P1", "Q1", "P2", "Q2", "P3"),
}
WINDOW_ORDER = {
    "lp_m1": ("L", "P1", "R"),
    "lp_m2": ROLE_ORDER["lp_m2"],
    "lp_m3": ROLE_ORDER["lp_m3"],
}
CONTRAST_PAIRS = {
    "lp_m1": (("P1", "L"), ("P1", "R")),
    "lp_m2": (("P1", "Q1"), ("P2", "Q1")),
    "lp_m3": (("P1", "Q1"), ("P2", "Q1"), ("P2", "Q2"), ("P3", "Q2")),
}

Q_TIME = Fraction(1, 1 << 10)
H_CAP = Fraction(2, 5)
Q_TAU = Fraction(1, 1 << 40)
TAU_CAPS = {
    "survival": Fraction(1, 100),
    "basin": Fraction(1, 1000),
    "window": Fraction(1, 1000),
}
BASIN_FLOOR = Fraction(1, 200)
ALPHA_SURVIVAL_MEMBER = Fraction(1, 600)
ALPHA_BASIN_MEMBER = Fraction(1, 800)
ALPHA_WINDOW_MEMBER = Fraction(1, 880)
BETA_MEMBER = Fraction(1, 680)
PRECISION_LADDER = (256, 512, 1024, 2048, 4096)
CANDIDATE_GRID = tuple(100_000 * k for k in range(1, 249))
WHOLE_CAMPAIGN_CAP = 50_000_000
POWER_ASSERTION_COUNTS = {
    "basin_compatibility": 12,
    "basin_floor": 12,
    "positive_contrast": 16,
    "survival_compatibility": 6,
    "window_compatibility": 22,
}
POWER_ASSERTION_FAMILY_LAYOUT = (
    ("survival_compatibility", 6, "dkw_decision"),
    ("basin_floor", 12, "binomial_decision"),
    ("basin_compatibility", 12, "binomial_decision"),
    ("window_compatibility", 22, "binomial_decision"),
    ("positive_contrast", 16, "binomial_decision"),
)
POWER_ASSERTION_LAYOUT = tuple(
    (family, f"{family}:{index:02d}", operation)
    for family, count, operation in POWER_ASSERTION_FAMILY_LAYOUT
    for index in range(1, count + 1)
)
MPFR_SERIALIZED_EMIN = -1_073_741_823
MPFR_SERIALIZED_EMAX = 1_073_741_823

MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
PHILOX_M0 = 0xD2511F53
PHILOX_M1 = 0xCD9E8D57
PHILOX_W0 = 0x9E3779B9
PHILOX_W1 = 0xBB67AE85

STATE_BALL_MAGIC = b"F1SBV2\0"


class SelectorError(ValueError):
    """A deterministic fail-closed selector error with one canonical reason."""

    def __init__(self, reason: str, detail: str) -> None:
        if reason not in HOLD_RANK:
            raise ValueError(f"unknown HOLD reason {reason!r}")
        super().__init__(detail)
        self.reason = reason
        self.detail = detail


HOLD_ORDER = (
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
HOLD_RANK = {reason: index for index, reason in enumerate(HOLD_ORDER)}

STAGE_ORDER = (
    "decode",
    "schema",
    "dependencies",
    "numeric_leaves",
    "f1a",
    "geometry",
    "f1b_coverage",
    "reference_point_law",
    "common_observables",
    "power",
    "rng",
    "append_only",
    "replica",
)
REASON_STAGE = {
    **{reason: "decode" for reason in HOLD_ORDER[:4]},
    "HOLD_SCHEMA": "schema",
    "HOLD_SCHEMA_NULLABILITY": "schema",
    "HOLD_DEPENDENCY_HASH": "dependencies",
    "HOLD_NUMERIC_LEAF": "numeric_leaves",
    "HOLD_F1A": "f1a",
    "HOLD_SELECTOR_INPUT": "f1a",
    "HOLD_ROLE_HULL_OVERLAP": "geometry",
    "HOLD_COMMON_CUT": "geometry",
    "HOLD_ROLE_WINDOW": "geometry",
    "HOLD_F1B_STATE_COVERAGE": "f1b_coverage",
    "HOLD_REFERENCE_POINT_LAW": "reference_point_law",
    "HOLD_CUT_UNCERTAINTY": "common_observables",
    "HOLD_COMMON_OBSERVABLE": "common_observables",
    "HOLD_DETERMINISTIC_ENVELOPE": "common_observables",
    "HOLD_TAU_ZERO": "common_observables",
    "HOLD_BASIN_FLOOR": "common_observables",
    "HOLD_CONTRAST_NONPOSITIVE": "common_observables",
    "HOLD_CONTRAST_PLANNING_INCOHERENT": "common_observables",
    "HOLD_CONTRAST_SPLIT": "common_observables",
    "HOLD_SPECIAL_FUNCTION_DAG": "power",
    "HOLD_SPECIAL_FUNCTION_AMBIGUOUS": "power",
    "HOLD_POWER_BOUNDARY": "power",
    "HOLD_N_CAP": "power",
    "HOLD_RNG_SPEC": "rng",
    "HOLD_TEST_KEY_SET": "rng",
    "HOLD_SEED_COLLISION": "rng",
    "HOLD_NO_REFIT_VIOLATION": "append_only",
    "HOLD_APPEND_ONLY": "append_only",
    "HOLD_SELECTOR_REPLICA_MISMATCH": "replica",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(
        _read_ordinary_file_snapshot(
            path.resolve(strict=True), f"ordinary-file snapshot changed: {path.name}"
        )
    )


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    ).encode("ascii")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SelectorError("HOLD_DUPLICATE_KEY", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(value: str) -> None:
    raise SelectorError("HOLD_DECODE_JSON", f"forbidden JSON constant {value}")


def _reject_json_float_token(value: str) -> None:
    raise SelectorError(
        "HOLD_CANONICAL_JSON",
        f"JSON floating-point token {value!r} is forbidden; use a canonical string",
    )


def _require_ascii_tree(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        try:
            value.encode("ascii")
        except UnicodeEncodeError as exc:
            raise SelectorError("HOLD_SCHEMA", f"non-ASCII string at {path}") from exc
    elif isinstance(value, list):
        for index, member in enumerate(value):
            _require_ascii_tree(member, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, member in value.items():
            _require_ascii_tree(key, f"{path}.<key>")
            _require_ascii_tree(member, f"{path}.{key}")


def strict_load_canonical_json(raw: bytes) -> Any:
    if type(raw) is not bytes:
        raise SelectorError("HOLD_DECODE_UTF8", "canonical JSON input must be bytes")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SelectorError("HOLD_DECODE_UTF8", "input is not strict UTF-8") from exc
    if text.startswith("\ufeff"):
        raise SelectorError("HOLD_DECODE_UTF8", "UTF-8 BOM is forbidden")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite_json_constant,
            parse_float=_reject_json_float_token,
        )
    except SelectorError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise SelectorError("HOLD_DECODE_JSON", "input is not JSON") from exc
    _require_ascii_tree(value)
    if canonical_json_bytes(value) != raw:
        raise SelectorError(
            "HOLD_CANONICAL_JSON", "input is not sorted, indented canonical JSON plus newline"
        )
    return value


def canonical_rational(value: Fraction) -> str:
    return (
        str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    )


_RATIONAL_RE = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


def parse_canonical_rational(text: str) -> Fraction:
    if not isinstance(text, str) or _RATIONAL_RE.fullmatch(text) is None:
        raise SelectorError("HOLD_NUMERIC_LEAF", f"noncanonical rational {text!r}")
    value = Fraction(text)
    if canonical_rational(value) != text:
        raise SelectorError("HOLD_NUMERIC_LEAF", f"unreduced rational {text!r}")
    return value


def parse_canonical_float_hex(text: str) -> float:
    if not isinstance(text, str):
        raise SelectorError("HOLD_NUMERIC_LEAF", "binary64 leaf is not a string")
    try:
        value = float.fromhex(text)
    except ValueError as exc:
        raise SelectorError("HOLD_NUMERIC_LEAF", f"invalid binary64 hex {text!r}") from exc
    if not math.isfinite(value) or value == 0.0 and text.startswith("-"):
        raise SelectorError("HOLD_NUMERIC_LEAF", f"forbidden binary64 value {text!r}")
    if value.hex() != text:
        raise SelectorError("HOLD_NUMERIC_LEAF", f"alternate binary64 spelling {text!r}")
    return value


def fraction_from_float_hex(text: str) -> Fraction:
    return Fraction.from_float(parse_canonical_float_hex(text))


def rn64(value: Fraction) -> str:
    rounded = float(value)
    if not math.isfinite(rounded):
        raise SelectorError("HOLD_NUMERIC_LEAF", "exact value overflows binary64")
    if rounded == 0.0 and value < 0:
        raise SelectorError("HOLD_NUMERIC_LEAF", "rounding would produce negative zero")
    return rounded.hex()


def up64(value: Fraction) -> str:
    rounded = float(value)
    if not math.isfinite(rounded):
        raise SelectorError("HOLD_NUMERIC_LEAF", "exact value overflows binary64")
    if Fraction.from_float(rounded) < value:
        rounded = math.nextafter(rounded, math.inf)
    return rounded.hex()


def down64(value: Fraction) -> str:
    rounded = float(value)
    if not math.isfinite(rounded):
        raise SelectorError("HOLD_NUMERIC_LEAF", "exact value overflows binary64")
    if Fraction.from_float(rounded) > value:
        rounded = math.nextafter(rounded, -math.inf)
    if rounded == 0.0 and value < 0:
        raise SelectorError("HOLD_NUMERIC_LEAF", "directed rounding would produce negative zero")
    return rounded.hex()


def exact_midpoint_hex(lower: str, upper: str) -> dict[str, str]:
    lo = fraction_from_float_hex(lower)
    hi = fraction_from_float_hex(upper)
    if lo > hi:
        raise SelectorError("HOLD_NUMERIC_LEAF", "interval endpoints are reversed")
    midpoint = (lo + hi) / 2
    rounded = rn64(midpoint)
    return {
        "exact_midpoint": canonical_rational(midpoint),
        "rounded_binary64": rounded,
        "tie_rule": "roundTiesToEven",
    }


def ordered_hold_reasons(reasons: Iterable[str]) -> tuple[str, ...]:
    unique = set(reasons)
    unknown = unique.difference(HOLD_RANK)
    if unknown:
        raise ValueError(f"unknown HOLD reasons: {sorted(unknown)!r}")
    return tuple(sorted(unique, key=HOLD_RANK.__getitem__))


def hold_payload(reasons: Iterable[str]) -> dict[str, Any]:
    ordered = ordered_hold_reasons(reasons)
    if not ordered:
        raise ValueError("at least one HOLD reason is required")
    primary = ordered[0]
    failure_index = STAGE_ORDER.index(REASON_STAGE[primary])
    stage_rows = {
        stage: (
            "PASS_BEFORE_HOLD"
            if index < failure_index
            else "HOLD"
            if index == failure_index
            else "NOT_RUN_AFTER_HOLD"
        )
        for index, stage in enumerate(STAGE_ORDER)
    }
    return {
        "hold": {"primary": primary, "secondary": list(ordered[1:])},
        "stage_rows": stage_rows,
        "status": "HOLD_SELECTION",
    }


def selection_pass_stage_rows() -> dict[str, str]:
    geometry_index = STAGE_ORDER.index("geometry")
    return {
        stage: "PASS" if index <= geometry_index else "NOT_RUN_NOT_YET"
        for index, stage in enumerate(STAGE_ORDER)
    }


def selector_payload_core_bytes(core: Mapping[str, Any]) -> bytes:
    if "canonical_payload_sha256" in core:
        raise SelectorError(
            "HOLD_SCHEMA", "selector_payload_core must exclude its own digest field"
        )
    return canonical_json_bytes(dict(core))


def build_selector_envelope(core: Mapping[str, Any]) -> dict[str, Any]:
    core_copy = dict(core)
    digest = sha256_bytes(selector_payload_core_bytes(core_copy))
    return {"canonical_payload_sha256": digest, "selector_payload_core": core_copy}


def _validate_core_semantics(
    core: Mapping[str, Any], expected_dependencies: Mapping[str, str]
) -> None:
    if type(core.get("schema_version")) is not int or core["schema_version"] != 2:
        raise SelectorError("HOLD_SCHEMA", "selector schema version must be the integer 2")
    dependencies = core["dependencies"]
    if set(expected_dependencies) != set(dependencies):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "expected dependency key set changed")
    for name, value in dependencies.items():
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise SelectorError("HOLD_DEPENDENCY_HASH", f"dependency {name} is not SHA-256")
        if value != expected_dependencies[name]:
            raise SelectorError("HOLD_DEPENDENCY_HASH", f"dependency {name} is stale")
    pinned_package_edges = {
        "central_projection_spec_sha256": EXPECTED_CENTRAL_PROJECTION_SHA256,
        "philox_spec_sha256": EXPECTED_PHILOX_SPEC_SHA256,
        "selector_runtime_sha256": EXPECTED_RUNTIME_SPEC_SHA256,
        "selector_schema_sha256": sha256_file(SCHEMA_PATH),
        "test_key_set_sha256": EXPECTED_TEST_KEY_SET_SHA256,
    }
    for name, expected in pinned_package_edges.items():
        if dependencies[name] != expected:
            raise SelectorError("HOLD_DEPENDENCY_HASH", f"package dependency {name} changed")

    if core["status"] == "HOLD_SELECTION":
        hold = core["hold"]
        recomputed = hold_payload((hold["primary"], *hold["secondary"]))
        if hold != recomputed["hold"] or core["stage_rows"] != recomputed["stage_rows"]:
            raise SelectorError("HOLD_SCHEMA", "HOLD reason order or NOT_RUN stubs are false")
        return
    if core["hold"] is not None or core["stage_rows"] != selection_pass_stage_rows():
        raise SelectorError("HOLD_SCHEMA", "PASS payload contains a lying stage row")

    selection = core["selection"]
    for control in CONTROL_ORDER:
        payload = selection["controls"][control]
        roles = ROLE_ORDER[control]
        if tuple(row["role"] for row in payload["role_hulls"]) != roles:
            raise SelectorError("HOLD_SELECTOR_INPUT", f"{control} role order changed")
        parsed_hulls = {}
        previous_upper = None
        for row in payload["role_hulls"]:
            lower, upper = _parse_interval(row["interval"], "HOLD_NUMERIC_LEAF")
            if not Fraction(1, 2) < lower <= upper < 35:
                raise SelectorError("HOLD_SELECTOR_INPUT", f"{control} role hull left its domain")
            if previous_upper is not None and previous_upper >= lower:
                raise SelectorError("HOLD_ROLE_HULL_OVERLAP", f"{control} role hulls overlap")
            previous_upper = upper
            parsed_hulls[row["role"]] = (lower, upper)
        expected_valleys = tuple(role for role in roles if role.startswith("Q"))
        if tuple(payload["valley_roles"]) != expected_valleys:
            raise SelectorError("HOLD_SCHEMA_NULLABILITY", f"{control} valley-role array changed")
        if tuple(cut["role"] for cut in payload["common_cuts"]) != expected_valleys:
            raise SelectorError("HOLD_COMMON_CUT", f"{control} common-cut roles changed")
        if len(payload["cut_hulls"]) != len(expected_valleys):
            raise SelectorError("HOLD_COMMON_CUT", f"{control} cut-hull count changed")
        parsed_cut_hulls = []
        for role, interval in zip(expected_valleys, payload["cut_hulls"], strict=True):
            parsed = _parse_interval(interval, "HOLD_NUMERIC_LEAF")
            if parsed != parsed_hulls[role]:
                raise SelectorError("HOLD_COMMON_CUT", f"{control} cut hull differs from Q hull")
            parsed_cut_hulls.append(parsed)
        for cut in payload["common_cuts"]:
            lower, upper = parsed_hulls[cut["role"]]
            midpoint = (lower + upper) / 2
            if parse_canonical_rational(cut["exact_midpoint"]) != midpoint or cut[
                "value_binary64"
            ] != rn64(midpoint):
                raise SelectorError("HOLD_COMMON_CUT", f"{control} common cut is noncanonical")
            fraction_from_float_hex(cut["delta_v_binary64"])
        canonical_geometry = select_cuts_and_windows(
            control,
            {
                role: tuple(row["interval"])
                for role, row in zip(roles, payload["role_hulls"], strict=True)
            },
        )
        if payload["common_cuts"] != canonical_geometry["common_cuts"]:
            raise SelectorError("HOLD_COMMON_CUT", f"{control} common-cut bytes are not canonical")
        if tuple(window["name"] for window in payload["windows"]) != WINDOW_ORDER[control]:
            raise SelectorError("HOLD_ROLE_WINDOW", f"{control} window order changed")
        if payload["windows"] != canonical_geometry["windows"]:
            raise SelectorError("HOLD_ROLE_WINDOW", f"{control} window bytes are not canonical")
        windows = []
        widths = set()
        for window in payload["windows"]:
            lower = parse_canonical_rational(window["lower"])
            upper = parse_canonical_rational(window["upper"])
            if not Fraction(1, 2) <= lower < upper <= 35:
                raise SelectorError("HOLD_ROLE_WINDOW", f"{control} window is invalid")
            windows.append((lower, upper))
            widths.add(upper - lower)
        if len(widths) != 1 or any(
            left[1] >= right[0] for left, right in zip(windows, windows[1:], strict=False)
        ):
            raise SelectorError("HOLD_ROLE_WINDOW", f"{control} windows touch or differ in width")
        window_map = {
            window["name"]: (
                parse_canonical_rational(window["lower"]),
                parse_canonical_rational(window["upper"]),
            )
            for window in payload["windows"]
        }
        for role, (hull_lower, hull_upper) in parsed_hulls.items():
            window_lower, window_upper = window_map[role]
            if not window_lower < hull_lower <= hull_upper < window_upper:
                raise SelectorError(
                    "HOLD_ROLE_WINDOW", f"{control} role hull is not window-interior"
                )
        observed_contrasts = tuple(
            (contrast["high"], contrast["low"]) for contrast in payload["contrasts"]
        )
        if observed_contrasts != CONTRAST_PAIRS[control]:
            raise SelectorError("HOLD_CONTRAST_PLANNING_INCOHERENT", f"{control} contrasts changed")
        required_times = tuple(
            parse_canonical_rational(value) for value in selection["required_times"][control]
        )
        expected_times = {
            Fraction(1, 2),
            Fraction(2),
            Fraction(5),
            Fraction(10),
            Fraction(20),
            Fraction(35),
            Fraction(50),
            Fraction(75),
            Fraction(100),
        }
        expected_times.update(
            fraction_from_float_hex(cut["value_binary64"]) for cut in payload["common_cuts"]
        )
        for lower, upper in parsed_cut_hulls:
            expected_times.update((lower, upper))
        for lower, upper in windows:
            expected_times.update((lower, upper))
        if tuple(sorted(expected_times)) != required_times:
            raise SelectorError("HOLD_F1B_STATE_COVERAGE", f"{control} required times changed")


def validate_selector_envelope_bytes(
    raw: bytes, *, expected_dependencies: Mapping[str, str]
) -> dict[str, Any]:
    if not isinstance(expected_dependencies, Mapping):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "expected dependencies must be a mapping")
    envelope = strict_load_canonical_json(raw)
    if not isinstance(envelope, dict):
        raise SelectorError("HOLD_SCHEMA", "selector envelope must be an object")
    try:
        schema = strict_load_canonical_json(SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(schema).validate(envelope)
    except jsonschema.ValidationError as exc:
        pending = [exc]
        saw_null = False
        while pending:
            current = pending.pop()
            saw_null = saw_null or current.instance is None
            pending.extend(current.context)
        reason = "HOLD_SCHEMA_NULLABILITY" if saw_null else "HOLD_SCHEMA"
        raise SelectorError(reason, f"selector envelope schema failure: {exc.message}") from exc
    core = envelope["selector_payload_core"]
    observed = sha256_bytes(selector_payload_core_bytes(core))
    if envelope["canonical_payload_sha256"] != observed:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "selector core digest mismatch")
    _validate_core_semantics(core, expected_dependencies)
    return envelope


def _parse_interval(
    value: Sequence[str],
    reason: str,
    *,
    minimum: Fraction | None = None,
    maximum: Fraction | None = None,
) -> tuple[Fraction, Fraction]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise SelectorError(reason, "interval must have exactly two endpoints")
    if not all(isinstance(endpoint, str) for endpoint in value):
        raise SelectorError(reason, "interval endpoints must be canonical strings")
    lower = fraction_from_float_hex(value[0])
    upper = fraction_from_float_hex(value[1])
    if lower > upper:
        raise SelectorError(reason, "interval endpoints are reversed")
    if minimum is not None and lower < minimum:
        raise SelectorError(reason, "interval is below its allowed domain")
    if maximum is not None and upper > maximum:
        raise SelectorError(reason, "interval is above its allowed domain")
    return lower, upper


def build_role_hulls(
    control: str, rows: Mapping[str, Mapping[str, Sequence[str]]]
) -> dict[str, tuple[str, str]]:
    if control not in ROLE_ORDER or tuple(rows) != CONFIGURATION_ORDER:
        raise SelectorError("HOLD_SELECTOR_INPUT", "control or configuration order changed")
    expected_roles = ROLE_ORDER[control]
    parsed: dict[str, list[tuple[Fraction, Fraction]]] = {role: [] for role in expected_roles}
    for configuration in CONFIGURATION_ORDER:
        role_map = rows[configuration]
        if tuple(role_map) != expected_roles:
            raise SelectorError("HOLD_SELECTOR_INPUT", "stationary role order changed")
        previous_upper: Fraction | None = None
        for role in expected_roles:
            lower, upper = _parse_interval(role_map[role], "HOLD_SELECTOR_INPUT")
            if lower <= Fraction(1, 2) or upper >= 35:
                raise SelectorError("HOLD_SELECTOR_INPUT", "role interval left the frozen band")
            if previous_upper is not None and previous_upper >= lower:
                raise SelectorError("HOLD_SELECTOR_INPUT", "one grid is not strictly ordered")
            previous_upper = upper
            parsed[role].append((lower, upper))
    hulls: dict[str, tuple[str, str]] = {}
    previous_upper = None
    for role in expected_roles:
        lower = min(item[0] for item in parsed[role])
        upper = max(item[1] for item in parsed[role])
        if previous_upper is not None and previous_upper >= lower:
            raise SelectorError(
                "HOLD_ROLE_HULL_OVERLAP", "global 12-grid role hulls touch or overlap"
            )
        previous_upper = upper
        hulls[role] = (rn64(lower), rn64(upper))
    return hulls


def select_cuts_and_windows(control: str, hulls: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    roles = ROLE_ORDER.get(control)
    if roles is None or tuple(hulls) != roles:
        raise SelectorError("HOLD_SELECTOR_INPUT", "role hull order changed")
    exact_hulls = {role: _parse_interval(hulls[role], "HOLD_SELECTOR_INPUT") for role in roles}
    cuts = []
    for role in roles:
        if role.startswith("Q"):
            lower, upper = exact_hulls[role]
            midpoint = (lower + upper) / 2
            cut = fraction_from_float_hex(rn64(midpoint))
            if not lower <= cut <= upper:
                raise SelectorError("HOLD_COMMON_CUT", "rounded cut escaped its role hull")
            cuts.append(
                {
                    "delta_v_binary64": up64(max(cut - lower, upper - cut)),
                    "exact_midpoint": canonical_rational(midpoint),
                    "role": role,
                    "value_binary64": rn64(midpoint),
                }
            )
    if any(
        fraction_from_float_hex(cuts[index]["value_binary64"])
        >= fraction_from_float_hex(cuts[index + 1]["value_binary64"])
        for index in range(len(cuts) - 1)
    ):
        raise SelectorError("HOLD_COMMON_CUT", "common cuts are not strictly ordered")

    centres: dict[str, Fraction] = {}
    centre_indices: dict[str, int] = {}
    for role in roles:
        lower, upper = exact_hulls[role]
        scaled = ((lower + upper) / 2) / Q_TIME
        index = round(scaled)
        centre_indices[role] = index
        centres[role] = index * Q_TIME
    centre_values = [centres[role] for role in roles]
    if any(left >= right for left, right in zip(centre_values, centre_values[1:], strict=False)):
        raise SelectorError("HOLD_ROLE_WINDOW", "lattice role centres are not ordered")
    candidates = [
        H_CAP,
        (centre_values[0] - Fraction(1, 2)) / 4,
        (Fraction(35) - centre_values[-1]) / 4,
    ]
    candidates.extend(
        (right - left) / 4 for left, right in zip(centre_values, centre_values[1:], strict=False)
    )
    h_raw = min(candidates)
    n_h = math.floor(h_raw / Q_TIME)
    if n_h < 1:
        raise SelectorError("HOLD_ROLE_WINDOW", "selected lattice half-width is zero")
    h = n_h * Q_TIME
    windows: dict[str, tuple[Fraction, Fraction]] = {
        role: (centres[role] - h, centres[role] + h) for role in roles
    }
    if control == "lp_m1":
        centre = centres["P1"]
        windows = {
            "L": (centre - 4 * h, centre - 2 * h),
            "P1": windows["P1"],
            "R": (centre + 2 * h, centre + 4 * h),
        }
    ordered_windows = [windows[name] for name in WINDOW_ORDER[control]]
    for name, (lower, upper) in windows.items():
        if not Fraction(1, 2) <= lower < upper <= 35:
            raise SelectorError("HOLD_ROLE_WINDOW", f"window {name} left [0.5,35]")
        if name in exact_hulls:
            hull_lower, hull_upper = exact_hulls[name]
            if not lower < hull_lower <= hull_upper < upper:
                raise SelectorError("HOLD_ROLE_WINDOW", f"hull {name} is not strictly interior")
    if any(
        left[1] >= right[0]
        for left, right in zip(ordered_windows, ordered_windows[1:], strict=False)
    ):
        raise SelectorError("HOLD_ROLE_WINDOW", "window closures touch or overlap")
    return {
        "centres": {
            role: {
                "lattice_index": centre_indices[role],
                "value": canonical_rational(centres[role]),
            }
            for role in roles
        },
        "common_cuts": cuts,
        "contrasts": [list(pair) for pair in CONTRAST_PAIRS[control]],
        "h": canonical_rational(h),
        "h_raw": canonical_rational(h_raw),
        "n_h": n_h,
        "windows": [
            {
                "left_closed": True,
                "lower": canonical_rational(windows[name][0]),
                "name": name,
                "right_open": True,
                "upper": canonical_rational(windows[name][1]),
            }
            for name in WINDOW_ORDER[control]
        ],
    }


def required_common_times(
    selection: Mapping[str, Any], hulls: Mapping[str, Sequence[str]]
) -> tuple[Fraction, ...]:
    times = {
        Fraction(1, 2),
        Fraction(2),
        Fraction(5),
        Fraction(10),
        Fraction(20),
        Fraction(35),
        Fraction(50),
        Fraction(75),
        Fraction(100),
    }
    for cut in selection["common_cuts"]:
        times.add(fraction_from_float_hex(cut["value_binary64"]))
        lower, upper = _parse_interval(hulls[cut["role"]], "HOLD_COMMON_CUT")
        times.update((lower, upper))
    for window in selection["windows"]:
        times.update(
            (parse_canonical_rational(window["lower"]), parse_canonical_rational(window["upper"]))
        )
    return tuple(sorted(times))


def validate_f1b_state_coverage(
    required_times: Sequence[Fraction],
    coverage: Mapping[str, Sequence[Mapping[str, Any]]],
) -> None:
    if tuple(coverage) != CONFIGURATION_ORDER:
        raise SelectorError("HOLD_F1B_STATE_COVERAGE", "F1-B coverage does not contain 12 grids")
    expected = tuple(required_times)
    for configuration in CONFIGURATION_ORDER:
        rows = coverage[configuration]
        observed = tuple(parse_canonical_rational(row["time"]) for row in rows)
        if observed != expected:
            raise SelectorError(
                "HOLD_F1B_STATE_COVERAGE", f"{configuration} required-time coverage changed"
            )
        if any(row.get("direct_from_zero") is not True for row in rows):
            raise SelectorError(
                "HOLD_F1B_STATE_COVERAGE", f"{configuration} contains sequential propagation"
            )


def _probability_interval(lower: Fraction, upper: Fraction) -> tuple[Fraction, Fraction]:
    lower = max(Fraction(0), lower)
    upper = min(Fraction(1), upper)
    if lower > upper:
        raise SelectorError("HOLD_CUT_UNCERTAINTY", "probability intersection with [0,1] is empty")
    return lower, upper


def _subtract_intervals(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return _probability_interval(left[0] - right[1], left[1] - right[0])


def basin_intervals_with_cut_uncertainty(
    survival_at: Mapping[Fraction, tuple[Fraction, Fraction]],
    point_cuts: Sequence[Fraction],
    cut_hulls: Sequence[tuple[Fraction, Fraction]],
) -> dict[str, list[tuple[Fraction, Fraction]]]:
    if len(point_cuts) != len(cut_hulls):
        raise SelectorError("HOLD_CUT_UNCERTAINTY", "cut and cut-hull counts differ")

    def survival(time: Fraction) -> tuple[Fraction, Fraction]:
        try:
            lower, upper = survival_at[time]
        except KeyError as exc:
            raise SelectorError("HOLD_F1B_STATE_COVERAGE", f"missing survival at {time}") from exc
        if not 0 <= lower <= upper <= 1:
            raise SelectorError("HOLD_COMMON_OBSERVABLE", "invalid survival interval")
        return lower, upper

    def event_cdf(time: Fraction) -> tuple[Fraction, Fraction]:
        lower, upper = survival(time)
        return 1 - upper, 1 - lower

    horizon = Fraction(100)
    if not point_cuts:
        interval = event_cdf(horizon)
        return {"point": [interval], "promoted": [interval], "robust": [interval]}

    point = [event_cdf(point_cuts[0])]
    for previous, current in zip(point_cuts, point_cuts[1:], strict=False):
        point.append(_subtract_intervals(event_cdf(current), event_cdf(previous)))
    point.append(_subtract_intervals(survival(point_cuts[-1]), survival(horizon)))

    robust = []
    first_lower, first_upper = cut_hulls[0]
    robust.append(_probability_interval(event_cdf(first_lower)[0], event_cdf(first_upper)[1]))
    for previous, current in zip(cut_hulls, cut_hulls[1:], strict=False):
        previous_lower, previous_upper = previous
        current_lower, current_upper = current
        robust.append(
            _probability_interval(
                event_cdf(current_lower)[0] - event_cdf(previous_upper)[1],
                event_cdf(current_upper)[1] - event_cdf(previous_lower)[0],
            )
        )
    last_lower, last_upper = cut_hulls[-1]
    robust.append(
        _probability_interval(
            survival(last_upper)[0] - survival(horizon)[1],
            survival(last_lower)[1] - survival(horizon)[0],
        )
    )
    promoted = [
        (min(point_iv[0], robust_iv[0]), max(point_iv[1], robust_iv[1]))
        for point_iv, robust_iv in zip(point, robust, strict=True)
    ]
    return {"point": point, "promoted": promoted, "robust": robust}


def deterministic_envelope(
    grid_intervals: Mapping[str, Sequence[str]], reference_value: Fraction
) -> dict[str, str]:
    if tuple(grid_intervals) != CONFIGURATION_ORDER:
        raise SelectorError("HOLD_DETERMINISTIC_ENVELOPE", "not all 12 grids were supplied")
    parsed = {
        grid: _parse_interval(
            interval,
            "HOLD_DETERMINISTIC_ENVELOPE",
            minimum=Fraction(0),
            maximum=Fraction(1),
        )
        for grid, interval in grid_intervals.items()
    }
    reference_interval = parsed[REFERENCE_CONFIGURATION]
    if not reference_interval[0] <= reference_value <= reference_interval[1]:
        raise SelectorError(
            "HOLD_DETERMINISTIC_ENVELOPE", "reference point is outside its own interval"
        )
    ref_lower, ref_upper = reference_interval
    error = max(
        max(abs(lower - ref_upper), abs(upper - ref_lower)) for lower, upper in parsed.values()
    )
    return {
        "compatibility_lower": down64(reference_value - error),
        "compatibility_upper": up64(reference_value + error),
        "e_det": up64(error),
        "reference_value": canonical_rational(reference_value),
    }


def select_tau(reference_value: Fraction, e_det: Fraction, observable_class: str) -> dict[str, str]:
    if observable_class not in TAU_CAPS:
        raise ValueError("unknown observable class")
    floor = BASIN_FLOOR if observable_class == "basin" else Fraction(0)
    budget = min(reference_value - e_det - floor, 1 - (reference_value + e_det))
    if budget <= 0:
        reason = "HOLD_BASIN_FLOOR" if observable_class == "basin" else "HOLD_TAU_ZERO"
        raise SelectorError(reason, "deterministic envelope leaves no allowance budget")
    raw = min(TAU_CAPS[observable_class], budget / 8)
    tau = math.floor(raw / Q_TAU) * Q_TAU
    if tau <= 0:
        raise SelectorError("HOLD_TAU_ZERO", "quantized cross-method allowance is zero")
    return {"budget": canonical_rational(budget), "tau": canonical_rational(tau)}


def contrast_planning_values(
    p_a_reference: Fraction,
    p_b_reference: Fraction,
    e_a: Fraction,
    e_b: Fraction,
    tau_a: Fraction,
    tau_b: Fraction,
    window_width: Fraction,
) -> dict[str, str]:
    p_a_low = fraction_from_float_hex(down64(p_a_reference - e_a - tau_a))
    p_b_high = fraction_from_float_hex(up64(p_b_reference + e_b + tau_b))
    if not 0 <= p_a_low <= 1 or not 0 <= p_b_high <= 1 or window_width <= 0:
        raise SelectorError("HOLD_CONTRAST_NONPOSITIVE", "contrast inputs left their domains")
    if p_a_low + p_b_high > 1:
        raise SelectorError(
            "HOLD_CONTRAST_PLANNING_INCOHERENT", "disjoint-window marginals exceed one"
        )
    difference = fraction_from_float_hex(down64(p_a_low - p_b_high))
    density = fraction_from_float_hex(down64(difference / window_width))
    if difference <= 0 or density <= 0:
        raise SelectorError("HOLD_CONTRAST_NONPOSITIVE", "subtracted contrast is not positive")
    theta = fraction_from_float_hex(rn64((p_a_low + p_b_high) / 2))
    if not p_b_high < theta < p_a_low:
        raise SelectorError("HOLD_CONTRAST_SPLIT", "canonical contrast split is not strict")
    return {
        "density_low": canonical_rational(density),
        "difference_low": canonical_rational(difference),
        "p_a_low": canonical_rational(p_a_low),
        "p_b_high": canonical_rational(p_b_high),
        "theta": canonical_rational(theta),
    }


def validate_family_ledger(counts: Mapping[str, int]) -> None:
    if dict(counts) != POWER_ASSERTION_COUNTS or sum(counts.values()) != 68:
        raise SelectorError("HOLD_POWER_BOUNDARY", "powered assertion family is not the frozen 68")


def encode_state_ball(intervals: Sequence[Sequence[str]]) -> bytes:
    if not intervals:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state ball is empty")
    payload = bytearray(STATE_BALL_MAGIC + struct.pack(">I", len(intervals)))
    for interval in intervals:
        lower, upper = _parse_interval(
            interval,
            "HOLD_REFERENCE_POINT_LAW",
            minimum=Fraction(0),
            maximum=Fraction(1),
        )
        payload.extend(struct.pack(">d", float(lower)))
        payload.extend(struct.pack(">d", float(upper)))
    return bytes(payload)


def decode_state_ball(payload: bytes) -> tuple[tuple[str, str], ...]:
    if type(payload) is not bytes:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state ball must be immutable bytes")
    if len(payload) < len(STATE_BALL_MAGIC) + 4 or not payload.startswith(STATE_BALL_MAGIC):
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state-ball magic mismatch")
    offset = len(STATE_BALL_MAGIC)
    dimension = struct.unpack(">I", payload[offset : offset + 4])[0]
    offset += 4
    if dimension == 0 or len(payload) != offset + 16 * dimension:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state-ball length mismatch")
    intervals = []
    for _index in range(dimension):
        lower = struct.unpack(">d", payload[offset : offset + 8])[0]
        upper = struct.unpack(">d", payload[offset + 8 : offset + 16])[0]
        offset += 16
        pair = (lower.hex(), upper.hex())
        _parse_interval(
            pair,
            "HOLD_REFERENCE_POINT_LAW",
            minimum=Fraction(0),
            maximum=Fraction(1),
        )
        intervals.append(pair)
    return tuple(intervals)


def _canonical_survival_from_state_ball(
    payload: bytes, expected_sha256: str, scalar_survival_interval: Sequence[str]
) -> dict[str, Any]:
    if type(payload) is not bytes:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state ball must be immutable bytes")
    if type(expected_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "state-ball SHA-256 binding is invalid")
    if sha256_bytes(payload) != expected_sha256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "pinned state-ball SHA-256 mismatch")
    intervals = decode_state_ball(payload)
    central_components = []
    lower_sum = Fraction(0)
    upper_sum = Fraction(0)
    central_sum = Fraction(0)
    for lower_hex, upper_hex in intervals:
        lower = fraction_from_float_hex(lower_hex)
        upper = fraction_from_float_hex(upper_hex)
        central_hex = rn64((lower + upper) / 2)
        central = fraction_from_float_hex(central_hex)
        lower_sum += lower
        upper_sum += upper
        central_sum += central
        central_components.append(central_hex)
    if not 0 <= lower_sum <= upper_sum or not 0 <= central_sum <= 1:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state-ball projection is not in [0,1]")
    projection_lower = max(Fraction(0), lower_sum)
    projection_upper = min(Fraction(1), upper_sum)
    if projection_lower > projection_upper:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state-ball projection misses [0,1]")
    survival_hex = rn64(central_sum)
    survival = fraction_from_float_hex(survival_hex)
    scalar_lower, scalar_upper = _parse_interval(
        scalar_survival_interval,
        "HOLD_REFERENCE_POINT_LAW",
        minimum=Fraction(0),
        maximum=Fraction(1),
    )
    if (
        not projection_lower <= survival <= projection_upper
        or not scalar_lower <= survival <= scalar_upper
    ):
        raise SelectorError(
            "HOLD_REFERENCE_POINT_LAW", "canonical state projection fails reconciliation"
        )
    if max(projection_lower, scalar_lower) > min(projection_upper, scalar_upper):
        raise SelectorError(
            "HOLD_REFERENCE_POINT_LAW", "state and scalar enclosures have empty intersection"
        )
    return {
        "central_components_binary64": central_components,
        "projection_exact_before_final_round": canonical_rational(central_sum),
        "projection_hull_exact": [
            canonical_rational(projection_lower),
            canonical_rational(projection_upper),
        ],
        "state_ball_sha256": expected_sha256,
        "survival_binary64": survival_hex,
    }


def load_pinned_state_registry(
    raw: bytes, expected_registry_sha256: str
) -> dict[Fraction, Mapping[str, Any]]:
    if type(raw) is not bytes:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "state registry must be immutable bytes")
    if (
        type(expected_registry_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", expected_registry_sha256) is None
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "state registry SHA-256 is invalid")
    if sha256_bytes(raw) != expected_registry_sha256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "F1-B state registry SHA-256 mismatch")
    registry = strict_load_canonical_json(raw)
    if not isinstance(registry, dict) or set(registry) != {"schema_version", "states"}:
        raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state registry shape changed")
    if (
        type(registry["schema_version"]) is not int
        or registry["schema_version"] != 1
        or not isinstance(registry["states"], list)
    ):
        raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state registry version changed")
    result = {}
    previous_time = None
    for row in registry["states"]:
        if not isinstance(row, dict) or set(row) != {
            "configuration",
            "state_blob_sha256",
            "survival_interval",
            "time",
        }:
            raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state registry row shape changed")
        if type(row["configuration"]) is not str or row["configuration"] != REFERENCE_CONFIGURATION:
            raise SelectorError("HOLD_REFERENCE_POINT_LAW", "state registry is not MR+F")
        time = parse_canonical_rational(row["time"])
        if previous_time is not None and time <= previous_time:
            raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state registry times are not ordered")
        if (
            type(row["state_blob_sha256"]) is not str
            or re.fullmatch(r"[0-9a-f]{64}", row["state_blob_sha256"]) is None
        ):
            raise SelectorError("HOLD_DEPENDENCY_HASH", "state blob SHA-256 is invalid")
        _parse_interval(
            row["survival_interval"],
            "HOLD_REFERENCE_POINT_LAW",
            minimum=Fraction(0),
            maximum=Fraction(1),
        )
        result[time] = row
        previous_time = time
    if not result:
        raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state registry is empty")
    return result


def validate_reference_path(
    records: Sequence[Mapping[str, Any]],
    registry_raw: bytes,
    expected_registry_sha256: str,
) -> tuple[Fraction, ...]:
    if not isinstance(records, (list, tuple)) or not records:
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "reference path is empty")
    registry = load_pinned_state_registry(registry_raw, expected_registry_sha256)
    if len(records) != len(registry):
        raise SelectorError("HOLD_F1B_STATE_COVERAGE", "state blobs do not cover the registry")
    previous_time: Fraction | None = None
    previous_survival = Fraction(1)
    path = []
    for record in records:
        if not isinstance(record, Mapping) or set(record) != {"state_blob", "time"}:
            raise SelectorError(
                "HOLD_REFERENCE_POINT_LAW", "caller supplied an alternate point path"
            )
        time = parse_canonical_rational(record["time"])
        if previous_time is not None and time <= previous_time:
            raise SelectorError("HOLD_REFERENCE_POINT_LAW", "reference times are not increasing")
        try:
            binding = registry[time]
        except KeyError as exc:
            raise SelectorError(
                "HOLD_F1B_STATE_COVERAGE", "state time is absent from registry"
            ) from exc
        projection = _canonical_survival_from_state_ball(
            record["state_blob"],
            binding["state_blob_sha256"],
            binding["survival_interval"],
        )
        survival = fraction_from_float_hex(projection["survival_binary64"])
        if survival > previous_survival:
            raise SelectorError("HOLD_REFERENCE_POINT_LAW", "canonical reference path increases")
        path.append(survival)
        previous_time = time
        previous_survival = survival
    if (
        sum(
            (left - right for left, right in zip((Fraction(1), *path[:-1]), path, strict=True)),
            Fraction(0),
        )
        + path[-1]
        != 1
    ):
        raise SelectorError("HOLD_REFERENCE_POINT_LAW", "reference probabilities do not close")
    return tuple(path)


def classify_tagged_outcome(
    outcome: Mapping[str, str],
    cuts: Sequence[Fraction],
    windows: Mapping[str, tuple[Fraction, Fraction]],
) -> dict[str, Any]:
    horizon = Fraction(100)
    tag = outcome.get("tag")
    event_time: Fraction | None
    if tag == "EVENT":
        event_time = parse_canonical_rational(outcome.get("event_time", ""))
        if not 0 <= event_time <= horizon or "censor_time" in outcome:
            raise SelectorError("HOLD_SELECTOR_INPUT", "invalid tagged event record")
    elif tag == "RIGHT_CENSORED":
        if outcome.get("censor_time") != "100" or "event_time" in outcome:
            raise SelectorError("HOLD_SELECTOR_INPUT", "invalid tagged survivor record")
        event_time = None
    else:
        raise SelectorError("HOLD_SELECTOR_INPUT", "unknown outcome tag")
    basin = None
    if event_time is not None:
        basin = sum(event_time > cut for cut in cuts)
    window_hits = {
        name: event_time is not None and lower <= event_time < upper
        for name, (lower, upper) in windows.items()
    }
    return {
        "basin_index": basin,
        "survives_horizon": event_time is None,
        "window_hits": window_hits,
    }


def strict_dkw_contact(empirical_sup_error: Fraction, delta: Fraction) -> bool:
    return empirical_sup_error < delta


def exact_binomial_range(n: int, p: Fraction, lower: int, upper: int) -> Fraction:
    if not 0 <= lower <= upper <= n or not 0 <= p <= 1:
        raise ValueError("invalid binomial range")
    if p == 0:
        return Fraction(int(lower == 0), 1)
    if p == 1:
        return Fraction(int(upper == n), 1)
    q = 1 - p

    def forward_sum(first: int, last: int) -> Fraction:
        if first > last:
            return Fraction(0)
        term = q**n
        total = Fraction(0)
        for k in range(0, last + 1):
            if k >= first:
                total += term
            if k != last:
                term = term * (n - k) * p / ((k + 1) * q)
        return total

    def reverse_sum(first: int, last: int) -> Fraction:
        if first > last:
            return Fraction(0)
        term = p**n
        total = Fraction(0)
        for k in range(n, first - 1, -1):
            if k <= last:
                total += term
            if k != first:
                term = term * k * q / ((n - k + 1) * p)
        return total

    strategies = (
        (upper + 1, 0, "forward"),
        (n - lower + 1, 1, "reverse"),
        (lower + n - upper, 2, "complement"),
    )
    strategy = min(strategies)[2]
    if strategy == "forward":
        return forward_sum(lower, upper)
    if strategy == "reverse":
        return reverse_sum(lower, upper)
    return 1 - forward_sum(0, lower - 1) - reverse_sum(upper + 1, n)


def cp_lower_gt(n: int, x: int, q: Fraction, alpha: Fraction) -> bool:
    if x == 0:
        return False
    return binomial_precision_ladder_decision(n, q, x, n, alpha / 2, "lt")["decision"] == "PASS"


def cp_upper_lt(n: int, x: int, q: Fraction, alpha: Fraction) -> bool:
    if x == n:
        return False
    return binomial_precision_ladder_decision(n, q, 0, x, alpha / 2, "lt")["decision"] == "PASS"


def _cp_lower_gt_in_process(n: int, x: int, q: Fraction, alpha: Fraction) -> bool:
    if x == 0:
        return False
    return (
        _binomial_precision_ladder_decision_in_process(n, q, x, n, alpha / 2, "lt")["decision"]
        == "PASS"
    )


def _cp_upper_lt_in_process(n: int, x: int, q: Fraction, alpha: Fraction) -> bool:
    if x == n:
        return False
    return (
        _binomial_precision_ladder_decision_in_process(n, q, 0, x, alpha / 2, "lt")["decision"]
        == "PASS"
    )


def _first_true(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    if not predicate(high):
        return None
    while low < high:
        middle = (low + high) // 2
        if predicate(middle):
            high = middle
        else:
            low = middle + 1
    return low


def _last_true(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    if not predicate(low):
        return None
    while low < high:
        middle = (low + high + 1) // 2
        if predicate(middle):
            low = middle
        else:
            high = middle - 1
    return low


def _cp_transition_hint(n: int, probability: Fraction, alpha: Fraction, sign: int) -> int:
    """Return a noncertifying binary64 search hint; MPFR rechecks every candidate."""

    z_value = NormalDist().inv_cdf(1 - float(alpha / 2))
    p_float = float(probability)
    mean = n * p_float
    deviation = z_value * math.sqrt(n * p_float * (1 - p_float))
    return min(n, max(0, round(mean + sign * deviation)))


def _cp_lower_threshold_in_process(n: int, boundary: Fraction, alpha: Fraction) -> int | None:
    lower = _cp_transition_hint(n, boundary, alpha, 1)
    if _cp_lower_gt_in_process(n, lower, boundary, alpha):
        while lower > 0 and _cp_lower_gt_in_process(n, lower - 1, boundary, alpha):
            lower -= 1
    else:
        while lower <= n and not _cp_lower_gt_in_process(n, lower, boundary, alpha):
            lower += 1
        if lower > n:
            return None
    return lower


def _cp_upper_threshold_in_process(n: int, boundary: Fraction, alpha: Fraction) -> int | None:
    upper = _cp_transition_hint(n, boundary, alpha, -1)
    if _cp_upper_lt_in_process(n, upper, boundary, alpha):
        while upper < n and _cp_upper_lt_in_process(n, upper + 1, boundary, alpha):
            upper += 1
    else:
        while upper >= 0 and not _cp_upper_lt_in_process(n, upper, boundary, alpha):
            upper -= 1
        if upper < 0:
            return None
    return upper


def _validate_cp_acceptance_input(
    n: int, lower_boundary: Fraction, upper_boundary: Fraction, alpha: Fraction
) -> None:
    if (
        type(n) is not int
        or type(lower_boundary) is not Fraction
        or type(upper_boundary) is not Fraction
        or type(alpha) is not Fraction
        or n < 0
        or not 0 < alpha < 1
        or not 0 <= lower_boundary < upper_boundary <= 1
    ):
        raise SelectorError("HOLD_POWER_BOUNDARY", "invalid CP acceptance-set input")


def _cp_acceptance_set_in_process(
    n: int, lower_boundary: Fraction, upper_boundary: Fraction, alpha: Fraction
) -> tuple[int, int] | None:
    """Evaluate one CP set inside a process that the public API must terminate."""

    _validate_cp_acceptance_input(n, lower_boundary, upper_boundary, alpha)
    lower = _cp_lower_threshold_in_process(n, lower_boundary, alpha)
    upper = _cp_upper_threshold_in_process(n, upper_boundary, alpha)
    if lower is None or upper is None or lower > upper:
        return None
    return lower, upper


def _read_ordinary_file_snapshot(
    path: Path, detail: str, *, maximum_bytes: int = 512 * 1024 * 1024
) -> bytes:
    """Read one ordinary file once and bind the bytes to stable descriptor metadata."""

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(path, flags)
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size < 0
            or before.st_size > maximum_bytes
        ):
            raise SelectorError("HOLD_DEPENDENCY_HASH", detail)
        chunks = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1 << 20, maximum_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum_bytes:
                raise SelectorError("HOLD_DEPENDENCY_HASH", detail)
        after = os.fstat(descriptor)
        path_after = os.stat(path, follow_symlinks=False)
        frozen_fields = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_nlink",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if (
            any(getattr(before, field) != getattr(after, field) for field in frozen_fields)
            or any(getattr(after, field) != getattr(path_after, field) for field in frozen_fields)
            or total != after.st_size
        ):
            raise SelectorError("HOLD_DEPENDENCY_HASH", detail)
        return b"".join(chunks)
    except OSError as exc:
        raise SelectorError("HOLD_DEPENDENCY_HASH", detail) from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _sha256_file_or_hold(path: Path, detail: str) -> str:
    return sha256_bytes(_read_ordinary_file_snapshot(path, detail))


LOADED_SELECTOR_SOURCE_SHA256 = _sha256_file_or_hold(
    Path(__file__).resolve(), "loaded selector source cannot be snapshotted"
)
LOADED_RUNTIME_BINARY_SHA256 = _sha256_file_or_hold(
    Path(sys.executable).resolve(), "loaded selector runtime cannot be snapshotted"
)


def _cp_worker_identity() -> tuple[str, str, str]:
    source_sha256 = _sha256_file_or_hold(
        Path(__file__).resolve(), "selector worker source cannot be hashed"
    )
    runtime_binary_sha256 = _sha256_file_or_hold(
        Path(sys.executable).resolve(), "selector worker runtime cannot be hashed"
    )
    runtime_spec_sha256 = _sha256_file_or_hold(
        RUNTIME_SPEC_PATH, "selector worker runtime spec cannot be hashed"
    )
    if source_sha256 != LOADED_SELECTOR_SOURCE_SHA256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "loaded selector worker source changed")
    if runtime_binary_sha256 != LOADED_RUNTIME_BINARY_SHA256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "loaded selector worker runtime changed")
    if runtime_spec_sha256 != EXPECTED_RUNTIME_SPEC_SHA256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "selector worker runtime spec changed")
    return source_sha256, runtime_binary_sha256, runtime_spec_sha256


def _cp_worker_request_bytes(
    n: int,
    lower_boundary: Fraction,
    upper_boundary: Fraction,
    alpha: Fraction,
    identity: tuple[str, str, str],
) -> bytes:
    _validate_cp_acceptance_input(n, lower_boundary, upper_boundary, alpha)
    source_sha256, runtime_binary_sha256, runtime_spec_sha256 = identity
    return canonical_json_bytes(
        {
            "alpha": canonical_rational(alpha),
            "lower_boundary": canonical_rational(lower_boundary),
            "n": n,
            "runtime_binary_sha256": runtime_binary_sha256,
            "runtime_spec_sha256": runtime_spec_sha256,
            "schema_version": 1,
            "selector_source_sha256": source_sha256,
            "upper_boundary": canonical_rational(upper_boundary),
        }
    )


def _parse_cp_worker_request(
    raw: bytes,
) -> tuple[dict[str, Any], tuple[int, Fraction, Fraction, Fraction]]:
    request = strict_load_canonical_json(raw)
    expected_keys = {
        "alpha",
        "lower_boundary",
        "n",
        "runtime_binary_sha256",
        "runtime_spec_sha256",
        "schema_version",
        "selector_source_sha256",
        "upper_boundary",
    }
    if not isinstance(request, dict) or set(request) != expected_keys:
        raise SelectorError("HOLD_SCHEMA", "CP worker request shape changed")
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise SelectorError("HOLD_SCHEMA", "CP worker request version changed")
    identity = _cp_worker_identity()
    observed_identity = (
        request["selector_source_sha256"],
        request["runtime_binary_sha256"],
        request["runtime_spec_sha256"],
    )
    if (
        any(
            type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in observed_identity
        )
        or observed_identity != identity
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "CP worker identity mismatch")
    n = request["n"]
    lower_boundary = parse_canonical_rational(request["lower_boundary"])
    upper_boundary = parse_canonical_rational(request["upper_boundary"])
    alpha = parse_canonical_rational(request["alpha"])
    _validate_cp_acceptance_input(n, lower_boundary, upper_boundary, alpha)
    return request, (n, lower_boundary, upper_boundary, alpha)


def _worker_peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


_WORKER_AUTHORIZATION_FACTORY_KEY = object()


class _WorkerAuthorization:
    __slots__ = (
        "capability_sha256",
        "deadline_monotonic_ns",
        "lock_descriptor",
        "parent_pid",
        "worker_pid",
    )

    def __init__(
        self,
        factory_key: object,
        capability_sha256: str,
        deadline_monotonic_ns: int,
        lock_descriptor: int,
        parent_pid: int,
        worker_pid: int,
    ) -> None:
        if factory_key is not _WORKER_AUTHORIZATION_FACTORY_KEY:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "worker authorization is not minted")
        self.capability_sha256 = capability_sha256
        self.deadline_monotonic_ns = deadline_monotonic_ns
        self.lock_descriptor = lock_descriptor
        self.parent_pid = parent_pid
        self.worker_pid = worker_pid


def _validate_inherited_worker_lock(descriptor: int) -> None:
    """Require the worker to retain the parent's already-held global lock."""

    try:
        metadata = os.fstat(descriptor)
        path_metadata = os.stat(SPECIAL_WORKER_LOCK_PATH, follow_symlinks=False)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.getuid()
            or metadata.st_nlink != 1
            or (metadata.st_dev, metadata.st_ino) != (path_metadata.st_dev, path_metadata.st_ino)
        ):
            raise SelectorError(
                "HOLD_SPECIAL_FUNCTION_DAG", "worker did not inherit the global lock"
            )
        # An inherited descriptor refers to the same open file description, so
        # reasserting LOCK_EX is a no-op when the parent already holds it.  It
        # also guarantees that the worker itself retains the lock if the parent
        # exits before the worker does.
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except SelectorError:
        raise
    except OSError as exc:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "worker inherited lock is invalid"
        ) from exc


def _worker_authorization_from_inherited_descriptor() -> _WorkerAuthorization:
    fd_text = os.environ.pop(SPECIAL_WORKER_CAPABILITY_FD_ENV, None)
    expected_sha256 = os.environ.pop(SPECIAL_WORKER_CAPABILITY_SHA_ENV, None)
    lock_fd_text = os.environ.pop(SPECIAL_WORKER_LOCK_FD_ENV, None)
    parent_pid_text = os.environ.pop(SPECIAL_WORKER_PARENT_PID_ENV, None)
    deadline_text = os.environ.pop(SPECIAL_WORKER_DEADLINE_NS_ENV, None)
    if (
        type(fd_text) is not str
        or re.fullmatch(r"[1-9][0-9]*", fd_text) is None
        or int(fd_text) < 3
        or type(expected_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
        or type(lock_fd_text) is not str
        or re.fullmatch(r"[1-9][0-9]*", lock_fd_text) is None
        or int(lock_fd_text) < 3
        or int(lock_fd_text) == int(fd_text)
        or type(parent_pid_text) is not str
        or re.fullmatch(r"[1-9][0-9]*", parent_pid_text) is None
        or type(deadline_text) is not str
        or re.fullmatch(r"[1-9][0-9]*", deadline_text) is None
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "worker launch capability is absent")
    descriptor = int(fd_text)
    lock_descriptor = int(lock_fd_text)
    parent_pid = int(parent_pid_text)
    deadline_monotonic_ns = int(deadline_text)
    lock_is_retained = False
    try:
        _validate_inherited_worker_lock(lock_descriptor)
        with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
            _SPECIAL_WORKER_OPEN_DESCRIPTORS.add(lock_descriptor)
        lock_is_retained = True
        capability = os.read(descriptor, 33)
        trailing = os.read(descriptor, 1)
    except OSError as exc:
        if lock_is_retained:
            with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                _SPECIAL_WORKER_OPEN_DESCRIPTORS.discard(lock_descriptor)
            try:
                os.close(lock_descriptor)
            except OSError:
                pass
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "worker launch capability cannot be read"
        ) from exc
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
    if (
        len(capability) != 32
        or trailing
        or sha256_bytes(capability) != expected_sha256
        or parent_pid != os.getppid()
        or parent_pid == os.getpid()
        or deadline_monotonic_ns <= time.monotonic_ns()
        or deadline_monotonic_ns > time.monotonic_ns() + CP_WORKER_TIMEOUT_SECONDS * 1_000_000_000
    ):
        if lock_is_retained:
            with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                _SPECIAL_WORKER_OPEN_DESCRIPTORS.discard(lock_descriptor)
            try:
                os.close(lock_descriptor)
            except OSError:
                pass
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "worker launch capability is invalid")
    return _WorkerAuthorization(
        _WORKER_AUTHORIZATION_FACTORY_KEY,
        expected_sha256,
        deadline_monotonic_ns,
        lock_descriptor,
        parent_pid,
        os.getpid(),
    )


def _require_worker_authorization(authorization: Any) -> None:
    if (
        type(authorization) is not _WorkerAuthorization
        or authorization.worker_pid != os.getpid()
        or authorization.parent_pid != os.getppid()
        or type(authorization.deadline_monotonic_ns) is not int
        or authorization.deadline_monotonic_ns <= time.monotonic_ns()
        or type(authorization.lock_descriptor) is not int
        or type(authorization.capability_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", authorization.capability_sha256) is None
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "internal worker called outside child")
    _validate_inherited_worker_lock(authorization.lock_descriptor)


def _seconds_until(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


@contextmanager
def _special_worker_thread_slot(deadline: float) -> Iterable[None]:
    remaining = _seconds_until(deadline)
    if remaining <= 0 or not _SPECIAL_WORKER_THREAD_SLOT.acquire(timeout=remaining):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "special-function worker queue timed out")
    try:
        yield
    finally:
        _SPECIAL_WORKER_THREAD_SLOT.release()


def _ensure_special_worker_lock_directory() -> None:
    try:
        os.mkdir(SPECIAL_WORKER_LOCK_DIRECTORY, 0o700)
    except FileExistsError:
        pass
    except OSError as exc:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "special-function lock directory cannot be created"
        ) from exc
    try:
        metadata = os.lstat(SPECIAL_WORKER_LOCK_DIRECTORY)
    except OSError as exc:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "special-function lock directory cannot be inspected"
        ) from exc
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "special-function lock directory is unsafe"
        )


@contextmanager
def _special_worker_slot(deadline: float | None = None) -> Iterable[int]:
    """Enforce one resident special-function child across all cooperating parents."""

    if deadline is None:
        deadline = time.monotonic() + CP_WORKER_TIMEOUT_SECONDS
    with _special_worker_thread_slot(deadline):
        _ensure_special_worker_lock_directory()
        flags = os.O_RDWR | os.O_CREAT
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(SPECIAL_WORKER_LOCK_PATH, flags, 0o600)
        except OSError as exc:
            raise SelectorError(
                "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker lock cannot be opened"
            ) from exc
        with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
            _SPECIAL_WORKER_OPEN_DESCRIPTORS.add(descriptor)
        locked = False
        try:
            metadata = os.fstat(descriptor)
            if (
                not stat.S_ISREG(metadata.st_mode)
                or metadata.st_uid != os.getuid()
                or metadata.st_nlink != 1
            ):
                raise SelectorError(
                    "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker lock is not private"
                )
            while not locked:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    locked = True
                except OSError as exc:
                    if exc.errno not in {errno.EACCES, errno.EAGAIN}:
                        raise
                    remaining = _seconds_until(deadline)
                    if remaining <= 0:
                        raise SelectorError(
                            "HOLD_SPECIAL_FUNCTION_DAG",
                            "special-function worker lock timed out",
                        ) from exc
                    time.sleep(min(0.01, remaining))
            path_metadata = os.stat(SPECIAL_WORKER_LOCK_PATH, follow_symlinks=False)
            if (metadata.st_dev, metadata.st_ino) != (path_metadata.st_dev, path_metadata.st_ino):
                raise SelectorError(
                    "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker lock was replaced"
                )
            yield descriptor
            path_metadata = os.stat(SPECIAL_WORKER_LOCK_PATH, follow_symlinks=False)
            if (metadata.st_dev, metadata.st_ino) != (path_metadata.st_dev, path_metadata.st_ino):
                raise SelectorError(
                    "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker lock changed while held"
                )
        except OSError as exc:
            raise SelectorError(
                "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker lock failed"
            ) from exc
        finally:
            # Do not issue LOCK_UN: the worker inherits this same open file
            # description, and an explicit unlock here would also release the
            # worker's lock.  Closing the parent's descriptor releases the lock
            # normally, while a surviving worker keeps it after parent failure.
            os.close(descriptor)
            with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                _SPECIAL_WORKER_OPEN_DESCRIPTORS.discard(descriptor)


def _run_special_worker_subprocess(
    mode: str, request_raw: bytes
) -> subprocess.CompletedProcess[bytes]:
    if mode not in {"--internal-cp-worker", "--internal-power-worker"}:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "unknown worker mode")
    deadline = time.monotonic() + CP_WORKER_TIMEOUT_SECONDS
    read_descriptor = -1
    write_descriptor = -1
    try:
        with _special_worker_slot(deadline) as lock_descriptor:
            read_descriptor, write_descriptor = os.pipe()
            with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                _SPECIAL_WORKER_OPEN_DESCRIPTORS.update({read_descriptor, write_descriptor})
            capability = os.urandom(32)
            if os.write(write_descriptor, capability) != len(capability):
                raise OSError("short capability write")
            os.close(write_descriptor)
            with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                _SPECIAL_WORKER_OPEN_DESCRIPTORS.discard(write_descriptor)
            write_descriptor = -1
            environment = os.environ.copy()
            environment[SPECIAL_WORKER_CAPABILITY_FD_ENV] = str(read_descriptor)
            environment[SPECIAL_WORKER_CAPABILITY_SHA_ENV] = sha256_bytes(capability)
            environment[SPECIAL_WORKER_LOCK_FD_ENV] = str(lock_descriptor)
            environment[SPECIAL_WORKER_PARENT_PID_ENV] = str(os.getpid())
            environment[SPECIAL_WORKER_DEADLINE_NS_ENV] = str(int(deadline * 1_000_000_000))
            remaining = _seconds_until(deadline)
            if remaining <= 0:
                raise SelectorError(
                    "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker queue timed out"
                )
            return subprocess.run(
                [sys.executable, "-I", str(Path(__file__).resolve()), mode],
                input=request_raw,
                capture_output=True,
                check=False,
                timeout=remaining,
                env=environment,
                pass_fds=(read_descriptor, lock_descriptor),
            )
    except subprocess.TimeoutExpired as exc:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker exceeded its fixed timeout"
        ) from exc
    except OSError as exc:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "special-function worker could not start"
        ) from exc
    finally:
        for descriptor in (read_descriptor, write_descriptor):
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                with _SPECIAL_WORKER_DESCRIPTOR_GUARD:
                    _SPECIAL_WORKER_OPEN_DESCRIPTORS.discard(descriptor)


def _run_internal_cp_worker(raw: bytes, authorization: Any = None) -> bytes:
    _require_worker_authorization(authorization)
    request_sha256 = sha256_bytes(raw)
    try:
        request, arguments = _parse_cp_worker_request(raw)
        runtime = verify_runtime_spec()
        if runtime != {
            "runtime_spec_sha256": EXPECTED_RUNTIME_SPEC_SHA256,
            "runtime_verified": True,
        }:
            raise SelectorError(
                "HOLD_DEPENDENCY_HASH", "CP worker runtime verification payload changed"
            )
        result = _cp_acceptance_set_in_process(*arguments)
        response = {
            "request_sha256": request_sha256,
            "result": None if result is None else list(result),
            "runtime_binary_sha256": request["runtime_binary_sha256"],
            "runtime_spec_sha256": runtime["runtime_spec_sha256"],
            "runtime_verified": True,
            "schema_version": 1,
            "selector_source_sha256": request["selector_source_sha256"],
            "status": "PASS",
            "worker_peak_rss_bytes": _worker_peak_rss_bytes(),
        }
    except SelectorError as exc:
        response = {
            "detail": exc.detail,
            "reason": exc.reason,
            "request_sha256": request_sha256,
            "schema_version": 1,
            "status": "HOLD",
            "worker_peak_rss_bytes": _worker_peak_rss_bytes(),
        }
    return canonical_json_bytes(response)


@lru_cache(maxsize=128)
def _isolated_cp_acceptance_set(
    n: int,
    lower_numerator: int,
    lower_denominator: int,
    upper_numerator: int,
    upper_denominator: int,
    alpha_numerator: int,
    alpha_denominator: int,
    source_sha256: str,
    runtime_binary_sha256: str,
    runtime_spec_sha256: str,
    process_id: int,
) -> tuple[tuple[int, int] | None, int]:
    if type(process_id) is not int or process_id != os.getpid():
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP cache crossed a process boundary")
    lower_boundary = Fraction(lower_numerator, lower_denominator)
    upper_boundary = Fraction(upper_numerator, upper_denominator)
    alpha = Fraction(alpha_numerator, alpha_denominator)
    identity = (source_sha256, runtime_binary_sha256, runtime_spec_sha256)
    request_raw = _cp_worker_request_bytes(n, lower_boundary, upper_boundary, alpha, identity)
    completed = _run_special_worker_subprocess("--internal-cp-worker", request_raw)
    if completed.returncode != 0 or completed.stderr:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "CP worker exited nonzero or wrote to stderr"
        )
    if not 0 < len(completed.stdout) <= 4096:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker response size is invalid")
    response = strict_load_canonical_json(completed.stdout)
    if not isinstance(response, dict) or type(response.get("schema_version")) is not int:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker response is not typed")
    if response.get("schema_version") != 1 or response.get("request_sha256") != sha256_bytes(
        request_raw
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "CP worker response binding changed")
    peak_rss = response.get("worker_peak_rss_bytes")
    if type(peak_rss) is not int or not 0 < peak_rss <= CP_WORKER_PEAK_RSS_CAP_BYTES:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker peak RSS exceeded its cap")
    if response.get("status") == "HOLD":
        if set(response) != {
            "detail",
            "reason",
            "request_sha256",
            "schema_version",
            "status",
            "worker_peak_rss_bytes",
        }:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker HOLD shape changed")
        reason = response.get("reason")
        detail = response.get("detail")
        if not isinstance(reason, str) or reason not in HOLD_RANK or not isinstance(detail, str):
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker HOLD is untyped")
        raise SelectorError(reason, detail)
    if (
        set(response)
        != {
            "request_sha256",
            "result",
            "runtime_binary_sha256",
            "runtime_spec_sha256",
            "runtime_verified",
            "schema_version",
            "selector_source_sha256",
            "status",
            "worker_peak_rss_bytes",
        }
        or response.get("status") != "PASS"
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker PASS shape changed")
    if (
        response["selector_source_sha256"] != source_sha256
        or response["runtime_binary_sha256"] != runtime_binary_sha256
        or response["runtime_spec_sha256"] != runtime_spec_sha256
        or response["runtime_verified"] is not True
        or _cp_worker_identity() != identity
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "CP worker identity changed during execution")
    raw_result = response["result"]
    if raw_result is None:
        result = None
    elif (
        isinstance(raw_result, list)
        and len(raw_result) == 2
        and all(type(value) is int for value in raw_result)
        and 0 <= raw_result[0] <= raw_result[1] <= n
    ):
        result = (raw_result[0], raw_result[1])
    else:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "CP worker result is invalid")
    return result, peak_rss


def _reset_special_worker_state_after_fork() -> None:
    global _SPECIAL_WORKER_DESCRIPTOR_GUARD
    global _SPECIAL_WORKER_OPEN_DESCRIPTORS
    global _SPECIAL_WORKER_THREAD_SLOT

    inherited_descriptors = tuple(_SPECIAL_WORKER_OPEN_DESCRIPTORS)
    _SPECIAL_WORKER_THREAD_SLOT = threading.BoundedSemaphore(SPECIAL_WORKER_CONCURRENCY)
    _SPECIAL_WORKER_DESCRIPTOR_GUARD = threading.Lock()
    _SPECIAL_WORKER_OPEN_DESCRIPTORS = set()
    for descriptor in inherited_descriptors:
        try:
            os.close(descriptor)
        except OSError:
            pass
    _isolated_cp_acceptance_set.cache_clear()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_reset_special_worker_state_after_fork)


def cp_acceptance_set(
    n: int, lower_boundary: Fraction, upper_boundary: Fraction, alpha: Fraction
) -> tuple[int, int] | None:
    """Return a certified CP set using a mandatory fail-closed process boundary.

    The pinned gmpy2/MPFR runtime retains allocator pages after a large number
    of immutable MPFR operations.  A fresh interpreter per distinct request is
    therefore part of the resource contract; there is no in-process fallback.
    """

    _validate_cp_acceptance_input(n, lower_boundary, upper_boundary, alpha)
    identity = _cp_worker_identity()
    result, _peak_rss = _isolated_cp_acceptance_set(
        n,
        lower_boundary.numerator,
        lower_boundary.denominator,
        upper_boundary.numerator,
        upper_boundary.denominator,
        alpha.numerator,
        alpha.denominator,
        *identity,
        os.getpid(),
    )
    return result


@dataclass(frozen=True)
class MPInterval:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    precision: int

    def __post_init__(self) -> None:
        if (
            self.precision not in PRECISION_LADDER
            or not gmpy2.is_finite(self.lower)
            or not gmpy2.is_finite(self.upper)
            or self.lower > self.upper
        ):
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid or reversed MPFR interval")

    def exact_fraction_pair(self) -> tuple[Fraction, Fraction]:
        def convert(value: gmpy2.mpfr) -> Fraction:
            numerator, denominator = value.as_integer_ratio()
            return Fraction(int(numerator), int(denominator))

        return convert(self.lower), convert(self.upper)

    def canonical_payload(self) -> dict[str, Any]:
        def encode(value: gmpy2.mpfr) -> dict[str, Any]:
            mantissa, exponent, precision = value.digits(16)
            return {
                "exponent_base16": exponent,
                "mantissa_hex": mantissa.lower(),
                "precision_bits": precision,
            }

        return {
            "endpoint_encoding": "mpfr-base16-mantissa-exponent-precision",
            "lower": encode(self.lower),
            "precision_bits": self.precision,
            "upper": encode(self.upper),
        }


def _mpfr_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(precision=precision, round=rounding):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mp_interval_exact(value: Fraction, precision: int) -> MPInterval:
    return MPInterval(
        _mpfr_fraction(value, precision, gmpy2.RoundDown),
        _mpfr_fraction(value, precision, gmpy2.RoundUp),
        precision,
    )


def _mp_binary(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    precision: int,
    rounding: int,
    operation: Callable[[gmpy2.mpfr, gmpy2.mpfr], gmpy2.mpfr],
) -> gmpy2.mpfr:
    with gmpy2.context(precision=precision, round=rounding):
        return +operation(left, right)


def _mp_add(left: MPInterval, right: MPInterval) -> MPInterval:
    p = left.precision
    if right.precision != p:
        raise ValueError("precision mismatch")
    return MPInterval(
        _mp_binary(left.lower, right.lower, p, gmpy2.RoundDown, lambda a, b: a + b),
        _mp_binary(left.upper, right.upper, p, gmpy2.RoundUp, lambda a, b: a + b),
        p,
    )


def _mp_sub(left: MPInterval, right: MPInterval) -> MPInterval:
    p = left.precision
    if right.precision != p:
        raise ValueError("precision mismatch")
    return MPInterval(
        _mp_binary(left.lower, right.upper, p, gmpy2.RoundDown, lambda a, b: a - b),
        _mp_binary(left.upper, right.lower, p, gmpy2.RoundUp, lambda a, b: a - b),
        p,
    )


def _mp_mul(left: MPInterval, right: MPInterval) -> MPInterval:
    p = left.precision
    if right.precision != p:
        raise ValueError("precision mismatch")
    pairs = tuple((a, b) for a in (left.lower, left.upper) for b in (right.lower, right.upper))
    lows = [_mp_binary(a, b, p, gmpy2.RoundDown, lambda x, y: x * y) for a, b in pairs]
    highs = [_mp_binary(a, b, p, gmpy2.RoundUp, lambda x, y: x * y) for a, b in pairs]
    return MPInterval(min(lows), max(highs), p)


def _mp_div(left: MPInterval, right: MPInterval) -> MPInterval:
    if right.lower <= 0 <= right.upper:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "interval division by zero")
    p = left.precision
    pairs = tuple((a, b) for a in (left.lower, left.upper) for b in (right.lower, right.upper))
    lows = [_mp_binary(a, b, p, gmpy2.RoundDown, lambda x, y: x / y) for a, b in pairs]
    highs = [_mp_binary(a, b, p, gmpy2.RoundUp, lambda x, y: x / y) for a, b in pairs]
    return MPInterval(min(lows), max(highs), p)


def _mp_monotone_unary(
    interval: MPInterval, function: Callable[[gmpy2.mpfr], gmpy2.mpfr]
) -> MPInterval:
    p = interval.precision
    with gmpy2.context(precision=p, round=gmpy2.RoundDown):
        lower = +function(interval.lower)
    with gmpy2.context(precision=p, round=gmpy2.RoundUp):
        upper = +function(interval.upper)
    return MPInterval(lower, upper, p)


def _mp_pow_nonnegative(base: MPInterval, exponent: int) -> MPInterval:
    if exponent < 0 or base.lower < 0:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid nonnegative integer power")
    result = _mp_interval_exact(Fraction(1), base.precision)
    factor = base
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = _mp_mul(result, factor)
        remaining >>= 1
        if remaining:
            factor = _mp_mul(factor, factor)
    return result


def _mp_probability_clip(interval: MPInterval) -> MPInterval:
    """Intersect an outward enclosure with the exact probability range [0, 1]."""

    zero = _mpfr_fraction(Fraction(0), interval.precision, gmpy2.RoundDown)
    one = _mpfr_fraction(Fraction(1), interval.precision, gmpy2.RoundUp)
    return MPInterval(max(zero, interval.lower), min(one, interval.upper), interval.precision)


def _mp_lgamma_integer(value: int, precision: int) -> MPInterval:
    """Directed MPFR enclosure of log(Gamma(value)) for a positive integer."""

    if value <= 0 or value.bit_length() > precision:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG",
            "log-gamma integer input is nonpositive or not exactly representable",
        )
    with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
        lower = +gmpy2.lngamma(gmpy2.mpfr(value))
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        upper = +gmpy2.lngamma(gmpy2.mpfr(value))
    return MPInterval(lower, upper, precision)


def _mp_binomial_boundary_pmf(n: int, p_value: Fraction, k: int, precision: int) -> MPInterval:
    """Enclose one binomial PMF using a directed integer log-gamma DAG."""

    if not 0 <= k <= n or not 0 < p_value < 1:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid boundary-PMF input")
    if k == 0:
        return _mp_pow_nonnegative(_mp_interval_exact(1 - p_value, precision), n)
    if k == n:
        return _mp_pow_nonnegative(_mp_interval_exact(p_value, precision), n)
    log_coefficient = _mp_sub(
        _mp_sub(
            _mp_lgamma_integer(n + 1, precision),
            _mp_lgamma_integer(k + 1, precision),
        ),
        _mp_lgamma_integer(n - k + 1, precision),
    )
    log_p = _mp_monotone_unary(_mp_interval_exact(p_value, precision), gmpy2.log)
    log_q = _mp_monotone_unary(_mp_interval_exact(1 - p_value, precision), gmpy2.log)
    log_pmf = _mp_add(
        log_coefficient,
        _mp_add(
            _mp_mul(_mp_interval_exact(Fraction(k), precision), log_p),
            _mp_mul(_mp_interval_exact(Fraction(n - k), precision), log_q),
        ),
    )
    result = _mp_monotone_unary(log_pmf, gmpy2.exp)
    if result.upper == 0:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "boundary PMF underflowed MPFR")
    return result


def _mp_exact_positive_ratio(numerator: int, denominator: int, precision: int) -> MPInterval:
    """Enclose a positive rational recurrence ratio without binary64."""

    if numerator < 0 or denominator <= 0:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid PMF recurrence ratio")
    return _mp_interval_exact(Fraction(numerator, denominator), precision)


def _mp_tail_stop_threshold(precision: int) -> gmpy2.mpfr:
    """Absolute tail remainder target; the returned value is rounded upward."""

    # Sixteen guard bits leave the rigorous truncation enclosure appreciably
    # wider than a single rounding ulp, while every precision-ladder step still
    # tightens the target exponentially.
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        return +gmpy2.exp2(gmpy2.mpfr(-precision + 16))


def _mp_binomial_tail(
    n: int,
    p_value: Fraction,
    boundary: int,
    side: str,
    precision: int,
) -> tuple[MPInterval, dict[str, Any]]:
    """Enclose one binomial tail by outward recurrence from its boundary.

    ``side == "lower"`` returns P[X <= boundary] and recurs toward zero;
    ``side == "upper"`` returns P[X >= boundary] and recurs toward ``n``.
    The caller only supplies boundaries on the corresponding side of a mode.
    Once the outward PMF ratio is below one, its exact monotonicity bounds all
    later ratios and hence the unsummed finite tail by a geometric series.
    """

    if side not in {"lower", "upper"}:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "unknown binomial-tail side")
    zero_remainder = _mp_interval_exact(Fraction(0), precision).canonical_payload()
    stop_target = f"2^(-{precision - 16})"
    monotonicity = (
        "k*q/((n-k+1)*p) decreases toward k=0"
        if side == "lower"
        else "(n-k)*p/((k+1)*q) decreases toward k=n"
    )
    if (side == "lower" and boundary < 0) or (side == "upper" and boundary > n):
        return _mp_interval_exact(Fraction(0), precision), {
            "boundary": boundary,
            "exact_endpoint": True,
            "geometric_ratio_monotonicity": monotonicity,
            "remainder_enclosure": zero_remainder,
            "side": side,
            "stop_target": stop_target,
            "terms_summed": 0,
        }
    if (side == "lower" and boundary >= n) or (side == "upper" and boundary <= 0):
        return _mp_interval_exact(Fraction(1), precision), {
            "boundary": boundary,
            "exact_endpoint": True,
            "geometric_ratio_monotonicity": monotonicity,
            "remainder_enclosure": zero_remainder,
            "side": side,
            "stop_target": stop_target,
            "terms_summed": 0,
        }

    if not 0 <= boundary <= n:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "tail boundary is outside support")
    center = Fraction(n + 1) * p_value
    if side == "lower" and boundary > center:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "lower-tail boundary is right of mode")
    if side == "upper" and boundary + 1 < center:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "upper-tail boundary is left of mode")

    p_numerator = p_value.numerator
    p_denominator = p_value.denominator
    q_numerator = p_denominator - p_numerator
    term = _mp_binomial_boundary_pmf(n, p_value, boundary, precision)
    total = term
    k = boundary
    terms_summed = 1
    remainder = _mp_interval_exact(Fraction(0), precision)
    stopped_geometrically = False
    threshold = _mp_tail_stop_threshold(precision)

    while (side == "lower" and k > 0) or (side == "upper" and k < n):
        if side == "lower":
            # P[X=k-1] / P[X=k] = k(1-p) / ((n-k+1)p).
            ratio = _mp_exact_positive_ratio(
                k * q_numerator,
                (n - k + 1) * p_numerator,
                precision,
            )
        else:
            # P[X=k+1] / P[X=k] = (n-k)p / ((k+1)(1-p)).
            ratio = _mp_exact_positive_ratio(
                (n - k) * p_numerator,
                (k + 1) * q_numerator,
                precision,
            )

        # The exact ratios decrease monotonically as recurrence moves away
        # from the mode.  Thus term*r/(1-r) encloses every unsummed term.
        if ratio.upper < 1:
            denominator = _mp_sub(_mp_interval_exact(Fraction(1), precision), ratio)
            geometric_upper = _mp_div(_mp_mul(term, ratio), denominator)
            zero = _mpfr_fraction(Fraction(0), precision, gmpy2.RoundDown)
            remainder = MPInterval(zero, geometric_upper.upper, precision)
            if remainder.upper <= threshold:
                total = _mp_add(total, remainder)
                stopped_geometrically = True
                break

        term = _mp_mul(term, ratio)
        if term.upper == 0:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "PMF recurrence underflowed MPFR")
        total = _mp_add(total, term)
        terms_summed += 1
        k = k - 1 if side == "lower" else k + 1

    if not stopped_geometrically:
        remainder = _mp_interval_exact(Fraction(0), precision)
    result = _mp_probability_clip(total)
    return result, {
        "boundary": boundary,
        "exact_endpoint": not stopped_geometrically,
        "geometric_ratio_monotonicity": monotonicity,
        "remainder_enclosure": remainder.canonical_payload(),
        "side": side,
        "stop_target": stop_target,
        "terms_summed": terms_summed,
    }


def _mp_binomial_range_in_process(
    n: int, p_value: Fraction, lower: int, upper: int, precision: int
) -> tuple[MPInterval, dict[str, Any]]:
    if (
        precision not in PRECISION_LADDER
        or not isinstance(n, int)
        or isinstance(n, bool)
        or not isinstance(lower, int)
        or isinstance(lower, bool)
        or not isinstance(upper, int)
        or isinstance(upper, bool)
        or not isinstance(p_value, Fraction)
        or n < 0
        or not 0 <= lower <= upper <= n
        or not 0 <= p_value <= 1
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid binomial DAG input")
    if p_value in (0, 1):
        atom = 0 if p_value == 0 else n
        value = Fraction(int(lower <= atom <= upper))
        return _mp_interval_exact(value, precision), {
            "dag_id": "BINOMIAL_RANGE_V2",
            "direction": "degenerate",
            "rounding_contract": "exact atom",
        }
    if lower == 0 and upper == n:
        total = _mp_interval_exact(Fraction(1), precision)
        direction = "full_support"
        tail_traces: list[dict[str, Any]] = []
    else:
        center = Fraction(n + 1) * p_value
        left_eligible = Fraction(upper) <= center
        right_eligible = Fraction(lower + 1) >= center
        if left_eligible and (not right_eligible or upper + 1 <= n - lower + 1):
            upper_tail, upper_trace = _mp_binomial_tail(n, p_value, upper, "lower", precision)
            tail_traces = [upper_trace]
            if lower == 0:
                total = upper_tail
                direction = "lower_tail"
            else:
                excluded, excluded_trace = _mp_binomial_tail(
                    n, p_value, lower - 1, "lower", precision
                )
                tail_traces.append(excluded_trace)
                total = _mp_probability_clip(_mp_sub(upper_tail, excluded))
                direction = "difference_of_lower_tails"
        elif right_eligible:
            lower_tail, lower_trace = _mp_binomial_tail(n, p_value, lower, "upper", precision)
            tail_traces = [lower_trace]
            if upper == n:
                total = lower_tail
                direction = "upper_tail"
            else:
                excluded, excluded_trace = _mp_binomial_tail(
                    n, p_value, upper + 1, "upper", precision
                )
                tail_traces.append(excluded_trace)
                total = _mp_probability_clip(_mp_sub(lower_tail, excluded))
                direction = "difference_of_upper_tails"
        else:
            left, left_trace = _mp_binomial_tail(n, p_value, lower - 1, "lower", precision)
            right, right_trace = _mp_binomial_tail(n, p_value, upper + 1, "upper", precision)
            tail_traces = [left_trace, right_trace]
            total = _mp_probability_clip(
                _mp_sub(_mp_sub(_mp_interval_exact(Fraction(1), precision), left), right)
            )
            direction = "complement_of_two_tails"
    return total, {
        "dag_id": "BINOMIAL_RANGE_V2",
        "direction": direction,
        "operation_order": (
            "integer log-gamma boundary PMF; outward rational recurrence; "
            "monotone geometric remainder; tail difference or complement"
        ),
        "rounding_contract": "MPFR RNDD lower and RNDU upper at every node",
        "tail_traces": tail_traces,
    }


def _binomial_precision_ladder_decision_in_process(
    n: int,
    p_value: Fraction,
    lower: int,
    upper: int,
    boundary: Fraction,
    relation: str,
) -> dict[str, Any]:
    return _precision_ladder_decision_in_process(
        lambda precision: _mp_binomial_range_in_process(n, p_value, lower, upper, precision)[0],
        boundary,
        relation,
    )


def _dkw_power_interval_in_process(
    a_min: Fraction, alpha: Fraction, n: int, precision: int
) -> tuple[MPInterval, dict[str, Any]]:
    if precision not in PRECISION_LADDER or a_min <= 0 or not 0 < alpha < 1 or n <= 0:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "invalid DKW DAG input")
    two = _mp_interval_exact(Fraction(2), precision)
    one = _mp_interval_exact(Fraction(1), precision)
    alpha_i = _mp_interval_exact(alpha, precision)
    log_arg = _mp_div(two, alpha_i)
    log_value = _mp_monotone_unary(log_arg, gmpy2.log)
    epsilon_square = _mp_div(log_value, _mp_interval_exact(Fraction(2 * n), precision))
    epsilon = _mp_monotone_unary(epsilon_square, gmpy2.sqrt)
    delta = _mp_sub(_mp_interval_exact(a_min, precision), epsilon)
    if delta.lower <= 0:
        if delta.upper <= 0:
            exact_zero = _mp_interval_exact(Fraction(0), precision)
            return exact_zero, {
                "dag_id": "DKW_POWER_V2",
                "delta": delta.canonical_payload(),
                "strict_event": "D_N < delta is impossible when delta<=0",
            }
        zero_one = MPInterval(
            _mpfr_fraction(Fraction(0), precision, gmpy2.RoundDown),
            _mpfr_fraction(Fraction(1), precision, gmpy2.RoundUp),
            precision,
        )
        return zero_one, {"dag_id": "DKW_POWER_V2", "delta": delta.canonical_payload()}
    delta_square = _mp_mul(delta, delta)
    exponent_magnitude = _mp_mul(_mp_interval_exact(Fraction(2 * n), precision), delta_square)
    exponent = MPInterval(-exponent_magnitude.upper, -exponent_magnitude.lower, precision)
    exponential = _mp_monotone_unary(exponent, gmpy2.exp)
    failure = _mp_mul(two, exponential)
    power = _mp_sub(one, failure)
    zero = _mpfr_fraction(Fraction(0), precision, gmpy2.RoundDown)
    one_up = _mpfr_fraction(Fraction(1), precision, gmpy2.RoundUp)
    clipped = MPInterval(
        max(zero, min(one_up, power.lower)),
        max(zero, min(one_up, power.upper)),
        precision,
    )
    return clipped, {
        "dag_id": "DKW_POWER_V2",
        "delta": delta.canonical_payload(),
        "epsilon": epsilon.canonical_payload(),
        "rounding_contract": "RNDD lower and RNDU upper at every listed node",
    }


def _precision_ladder_decision_in_process(
    evaluator: Callable[[int], MPInterval], boundary: Fraction, relation: str
) -> dict[str, Any]:
    if relation not in {"ge", "gt", "le", "lt"}:
        raise ValueError("relation must be ge, gt, le, or lt")
    attempts = []
    for precision in PRECISION_LADDER:
        interval = evaluator(precision)
        lower, upper = interval.exact_fraction_pair()
        if relation == "gt":
            decision = "PASS" if lower > boundary else "FAIL" if upper <= boundary else None
        elif relation == "lt":
            decision = "PASS" if upper < boundary else "FAIL" if lower >= boundary else None
        elif relation == "ge":
            decision = "PASS" if lower >= boundary else "FAIL" if upper < boundary else None
        else:
            decision = "PASS" if upper <= boundary else "FAIL" if lower > boundary else None
        attempts.append({"interval": interval.canonical_payload(), "precision_bits": precision})
        if decision is not None:
            return {"attempts": attempts, "decision": decision, "precision_bits": precision}
    raise SelectorError(
        "HOLD_SPECIAL_FUNCTION_AMBIGUOUS", "4096-bit outward interval still contacts boundary"
    )


def _power_worker_request_bytes(
    operation: str,
    parameters: dict[str, Any],
    identity: tuple[str, str, str],
    *,
    assertion_id: str | None = None,
    schedule_sha256: str | None = None,
) -> bytes:
    if operation not in {"binomial_decision", "dkw_decision"} or type(parameters) is not dict:
        raise SelectorError("HOLD_POWER_BOUNDARY", "invalid powered-assertion worker request")
    if (assertion_id is None) != (schedule_sha256 is None):
        raise SelectorError("HOLD_POWER_BOUNDARY", "partial powered-assertion binding")
    if assertion_id is not None and (
        type(assertion_id) is not str
        or re.fullmatch(
            r"(?:survival_compatibility|basin_floor|basin_compatibility|window_compatibility|positive_contrast):[0-9]{2}",
            assertion_id,
        )
        is None
        or type(schedule_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", schedule_sha256) is None
    ):
        raise SelectorError("HOLD_POWER_BOUNDARY", "invalid powered-assertion binding")
    source_sha256, runtime_binary_sha256, runtime_spec_sha256 = identity
    return canonical_json_bytes(
        {
            "assertion_id": assertion_id,
            "operation": operation,
            "parameters": parameters,
            "runtime_binary_sha256": runtime_binary_sha256,
            "runtime_spec_sha256": runtime_spec_sha256,
            "schedule_sha256": schedule_sha256,
            "schema_version": 1,
            "selector_source_sha256": source_sha256,
        }
    )


def _parse_power_worker_request(raw: bytes) -> tuple[dict[str, Any], str, tuple[Any, ...]]:
    request = strict_load_canonical_json(raw)
    expected_keys = {
        "assertion_id",
        "operation",
        "parameters",
        "runtime_binary_sha256",
        "runtime_spec_sha256",
        "schedule_sha256",
        "schema_version",
        "selector_source_sha256",
    }
    if type(request) is not dict or set(request) != expected_keys:
        raise SelectorError("HOLD_SCHEMA", "power worker request shape changed")
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise SelectorError("HOLD_SCHEMA", "power worker request version changed")
    identity = _cp_worker_identity()
    observed_identity = (
        request["selector_source_sha256"],
        request["runtime_binary_sha256"],
        request["runtime_spec_sha256"],
    )
    if (
        any(
            type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in observed_identity
        )
        or observed_identity != identity
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "power worker identity mismatch")
    operation = request["operation"]
    parameters = request["parameters"]
    assertion_id = request["assertion_id"]
    schedule_sha256 = request["schedule_sha256"]
    if type(operation) is not str or type(parameters) is not dict:
        raise SelectorError("HOLD_POWER_BOUNDARY", "power worker operation is untyped")
    if (
        (assertion_id is None) != (schedule_sha256 is None)
        or assertion_id is not None
        and (
            type(assertion_id) is not str
            or re.fullmatch(
                r"(?:survival_compatibility|basin_floor|basin_compatibility|window_compatibility|positive_contrast):[0-9]{2}",
                assertion_id,
            )
            is None
            or type(schedule_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", schedule_sha256) is None
        )
    ):
        raise SelectorError("HOLD_POWER_BOUNDARY", "power worker schedule binding is invalid")
    relation = parameters.get("relation")
    if type(relation) is not str or relation not in {"ge", "gt", "le", "lt"}:
        raise SelectorError("HOLD_POWER_BOUNDARY", "power worker relation is invalid")
    if operation == "binomial_decision":
        if set(parameters) != {"boundary", "lower", "n", "p_value", "relation", "upper"}:
            raise SelectorError("HOLD_POWER_BOUNDARY", "binomial worker shape changed")
        n = parameters["n"]
        lower = parameters["lower"]
        upper = parameters["upper"]
        p_value = parse_canonical_rational(parameters["p_value"])
        boundary = parse_canonical_rational(parameters["boundary"])
        if (
            type(n) is not int
            or type(lower) is not int
            or type(upper) is not int
            or n < 0
            or not 0 <= lower <= upper <= n
            or not 0 <= p_value <= 1
            or not 0 <= boundary <= 1
        ):
            raise SelectorError("HOLD_POWER_BOUNDARY", "binomial worker input is invalid")
        arguments = (n, p_value, lower, upper, boundary, relation)
    elif operation == "dkw_decision":
        if set(parameters) != {"a_min", "alpha", "boundary", "n", "relation"}:
            raise SelectorError("HOLD_POWER_BOUNDARY", "DKW worker shape changed")
        a_min = parse_canonical_rational(parameters["a_min"])
        alpha = parse_canonical_rational(parameters["alpha"])
        boundary = parse_canonical_rational(parameters["boundary"])
        n = parameters["n"]
        if (
            type(n) is not int
            or n <= 0
            or a_min <= 0
            or not 0 < alpha < 1
            or not 0 <= boundary <= 1
        ):
            raise SelectorError("HOLD_POWER_BOUNDARY", "DKW worker input is invalid")
        arguments = (a_min, alpha, n, boundary, relation)
    else:
        raise SelectorError("HOLD_POWER_BOUNDARY", "unknown power worker operation")
    return request, operation, arguments


def _run_internal_power_worker(raw: bytes, authorization: Any = None) -> bytes:
    _require_worker_authorization(authorization)
    request_sha256 = sha256_bytes(raw)
    try:
        request, operation, arguments = _parse_power_worker_request(raw)
        runtime = verify_runtime_spec()
        if runtime != {
            "runtime_spec_sha256": EXPECTED_RUNTIME_SPEC_SHA256,
            "runtime_verified": True,
        }:
            raise SelectorError(
                "HOLD_DEPENDENCY_HASH", "power worker runtime verification payload changed"
            )
        if operation == "binomial_decision":
            result = _binomial_precision_ladder_decision_in_process(*arguments)
        else:
            a_min, alpha, n, boundary, relation = arguments
            result = _precision_ladder_decision_in_process(
                lambda precision: _dkw_power_interval_in_process(a_min, alpha, n, precision)[0],
                boundary,
                relation,
            )
        response = {
            "operation": operation,
            "request_sha256": request_sha256,
            "result": result,
            "runtime_binary_sha256": request["runtime_binary_sha256"],
            "runtime_spec_sha256": runtime["runtime_spec_sha256"],
            "runtime_verified": True,
            "schema_version": 1,
            "selector_source_sha256": request["selector_source_sha256"],
            "status": "PASS",
            "worker_peak_rss_bytes": _worker_peak_rss_bytes(),
        }
    except SelectorError as exc:
        response = {
            "detail": exc.detail,
            "reason": exc.reason,
            "request_sha256": request_sha256,
            "schema_version": 1,
            "status": "HOLD",
            "worker_peak_rss_bytes": _worker_peak_rss_bytes(),
        }
    return canonical_json_bytes(response)


def _decode_canonical_probability_endpoint(
    payload: Any, expected_precision: int
) -> tuple[int, int]:
    """Decode one MPFR endpoint as ``mantissa * 16**exponent`` without MPFR.

    Comparisons below stay in integer arithmetic and avoid expanding a
    maliciously remote exponent into an enormous ``Fraction`` denominator.
    """

    if type(payload) is not dict or set(payload) != {
        "exponent_base16",
        "mantissa_hex",
        "precision_bits",
    }:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power endpoint shape changed")
    mantissa_text = payload["mantissa_hex"]
    exponent = payload["exponent_base16"]
    precision = payload["precision_bits"]
    if (
        type(mantissa_text) is not str
        or re.fullmatch(r"(?:0|[1-9a-f][0-9a-f]*)", mantissa_text) is None
        or type(exponent) is not int
        or not MPFR_SERIALIZED_EMIN <= exponent <= MPFR_SERIALIZED_EMAX
        or type(precision) is not int
        or precision != expected_precision
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power endpoint is not canonical")
    if mantissa_text == "0":
        if exponent != 0:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "zero endpoint exponent changed")
        return 0, 0
    if len(mantissa_text) != expected_precision // 4 + 1:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power endpoint precision changed")
    mantissa = int(mantissa_text, 16)
    leading_bit_count = int(mantissa_text[0], 16).bit_length()
    if mantissa & ((1 << leading_bit_count) - 1):
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG",
            "power endpoint has nonzero bits below its claimed MPFR precision",
        )
    return mantissa, exponent - len(mantissa_text)


def _compare_scaled_hex(left: tuple[int, int], right: tuple[int, int]) -> int:
    """Compare nonnegative exact values ``mantissa * 16**exponent``."""

    left_mantissa, left_exponent = left
    right_mantissa, right_exponent = right
    if left_mantissa == 0 or right_mantissa == 0:
        return (left_mantissa > right_mantissa) - (left_mantissa < right_mantissa)
    left_magnitude = left_mantissa.bit_length() + 4 * left_exponent
    right_magnitude = right_mantissa.bit_length() + 4 * right_exponent
    if left_magnitude != right_magnitude:
        return (left_magnitude > right_magnitude) - (left_magnitude < right_magnitude)
    if left_exponent >= right_exponent:
        left_integer = left_mantissa << (4 * (left_exponent - right_exponent))
        right_integer = right_mantissa
    else:
        left_integer = left_mantissa
        right_integer = right_mantissa << (4 * (right_exponent - left_exponent))
    return (left_integer > right_integer) - (left_integer < right_integer)


def _compare_scaled_hex_to_fraction(value: tuple[int, int], boundary: Fraction) -> int:
    """Compare one decoded endpoint with a nonnegative exact rational."""

    if type(boundary) is not Fraction or boundary < 0:
        raise SelectorError("HOLD_POWER_BOUNDARY", "power comparison boundary is invalid")
    mantissa, exponent = value
    if mantissa == 0 or boundary == 0:
        return (mantissa > boundary.numerator) - (mantissa < boundary.numerator)
    scaled_mantissa = mantissa * boundary.denominator
    numerator = boundary.numerator
    left_magnitude = scaled_mantissa.bit_length() + 4 * exponent
    right_magnitude = numerator.bit_length()
    if left_magnitude != right_magnitude:
        return (left_magnitude > right_magnitude) - (left_magnitude < right_magnitude)
    if exponent >= 0:
        left_integer = scaled_mantissa << (4 * exponent)
        right_integer = numerator
    else:
        left_integer = scaled_mantissa
        right_integer = numerator << (-4 * exponent)
    return (left_integer > right_integer) - (left_integer < right_integer)


def _decision_from_endpoint_comparisons(
    lower_comparison: int, upper_comparison: int, relation: str
) -> str | None:
    if relation == "gt":
        return "PASS" if lower_comparison > 0 else "FAIL" if upper_comparison <= 0 else None
    if relation == "lt":
        return "PASS" if upper_comparison < 0 else "FAIL" if lower_comparison >= 0 else None
    if relation == "ge":
        return "PASS" if lower_comparison >= 0 else "FAIL" if upper_comparison < 0 else None
    if relation == "le":
        return "PASS" if upper_comparison <= 0 else "FAIL" if lower_comparison > 0 else None
    raise SelectorError("HOLD_POWER_BOUNDARY", "power comparison relation is invalid")


def _validate_power_decision_result(
    result: Any, boundary: Fraction, relation: str
) -> dict[str, Any]:
    if type(result) is not dict or set(result) != {"attempts", "decision", "precision_bits"}:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker result shape changed")
    attempts = result["attempts"]
    precision = result["precision_bits"]
    if (
        type(result["decision"]) is not str
        or result["decision"] not in {"PASS", "FAIL"}
        or type(precision) is not int
        or precision not in PRECISION_LADDER
        or type(attempts) is not list
        or not 1 <= len(attempts) <= len(PRECISION_LADDER)
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker decision is invalid")
    observed_precisions = []
    observed_decisions: list[str | None] = []
    for attempt in attempts:
        if type(attempt) is not dict or set(attempt) != {"interval", "precision_bits"}:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker attempt shape changed")
        attempt_precision = attempt["precision_bits"]
        interval = attempt["interval"]
        if (
            type(attempt_precision) is not int
            or attempt_precision not in PRECISION_LADDER
            or type(interval) is not dict
            or set(interval) != {"endpoint_encoding", "lower", "precision_bits", "upper"}
            or type(interval.get("precision_bits")) is not int
            or interval.get("precision_bits") != attempt_precision
            or interval.get("endpoint_encoding") != "mpfr-base16-mantissa-exponent-precision"
        ):
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker interval is invalid")
        lower = _decode_canonical_probability_endpoint(interval["lower"], attempt_precision)
        upper = _decode_canonical_probability_endpoint(interval["upper"], attempt_precision)
        if (
            _compare_scaled_hex(lower, upper) > 0
            or _compare_scaled_hex_to_fraction(lower, Fraction(0)) < 0
            or _compare_scaled_hex_to_fraction(upper, Fraction(1)) > 0
        ):
            raise SelectorError(
                "HOLD_SPECIAL_FUNCTION_DAG", "power worker probability interval is invalid"
            )
        observed_decisions.append(
            _decision_from_endpoint_comparisons(
                _compare_scaled_hex_to_fraction(lower, boundary),
                _compare_scaled_hex_to_fraction(upper, boundary),
                relation,
            )
        )
        observed_precisions.append(attempt_precision)
    if (
        observed_precisions != list(PRECISION_LADDER[: len(attempts)])
        or precision != attempts[-1]["precision_bits"]
    ):
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power precision ladder changed")
    if any(decision is not None for decision in observed_decisions[:-1]):
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "power worker did not stop at first decisive precision"
        )
    if observed_decisions[-1] != result["decision"]:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "power decision is not certified by its endpoints"
        )
    return result


def _isolated_power_decision(
    operation: str,
    parameters: dict[str, Any],
    *,
    assertion_id: str | None = None,
    schedule_sha256: str | None = None,
) -> tuple[dict[str, Any], int, dict[str, Any]]:
    identity = _cp_worker_identity()
    request_raw = _power_worker_request_bytes(
        operation,
        parameters,
        identity,
        assertion_id=assertion_id,
        schedule_sha256=schedule_sha256,
    )
    completed = _run_special_worker_subprocess("--internal-power-worker", request_raw)
    if completed.returncode != 0 or completed.stderr:
        raise SelectorError(
            "HOLD_SPECIAL_FUNCTION_DAG", "power worker exited nonzero or wrote to stderr"
        )
    if not 0 < len(completed.stdout) <= SPECIAL_WORKER_RESPONSE_CAP_BYTES:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker response size is invalid")
    response = strict_load_canonical_json(completed.stdout)
    if type(response) is not dict or type(response.get("schema_version")) is not int:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker response is not typed")
    if response.get("schema_version") != 1 or response.get("request_sha256") != sha256_bytes(
        request_raw
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "power worker response binding changed")
    peak_rss = response.get("worker_peak_rss_bytes")
    if type(peak_rss) is not int or not 0 < peak_rss <= CP_WORKER_PEAK_RSS_CAP_BYTES:
        raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker peak RSS exceeded its cap")
    if response.get("status") == "HOLD":
        if set(response) != {
            "detail",
            "reason",
            "request_sha256",
            "schema_version",
            "status",
            "worker_peak_rss_bytes",
        }:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker HOLD shape changed")
        reason = response.get("reason")
        detail = response.get("detail")
        if type(reason) is not str or reason not in HOLD_RANK or type(detail) is not str:
            raise SelectorError("HOLD_SPECIAL_FUNCTION_DAG", "power worker HOLD is untyped")
        raise SelectorError(reason, detail)
    if (
        set(response)
        != {
            "operation",
            "request_sha256",
            "result",
            "runtime_binary_sha256",
            "runtime_spec_sha256",
            "runtime_verified",
            "schema_version",
            "selector_source_sha256",
            "status",
            "worker_peak_rss_bytes",
        }
        or response.get("status") != "PASS"
        or response.get("operation") != operation
        or response.get("selector_source_sha256") != identity[0]
        or response.get("runtime_binary_sha256") != identity[1]
        or response.get("runtime_spec_sha256") != identity[2]
        or response.get("runtime_verified") is not True
        or _cp_worker_identity() != identity
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "power worker identity changed")
    boundary = parse_canonical_rational(parameters["boundary"])
    relation = parameters["relation"]
    result = _validate_power_decision_result(response["result"], boundary, relation)
    receipt = {
        "assertion_id": assertion_id,
        "decision": result["decision"],
        "operation": operation,
        "request_sha256": sha256_bytes(request_raw),
        "response_sha256": sha256_bytes(completed.stdout),
        "runtime_binary_sha256": identity[1],
        "runtime_spec_sha256": identity[2],
        "schedule_sha256": schedule_sha256,
        "selector_source_sha256": identity[0],
        "worker_peak_rss_bytes": peak_rss,
    }
    return result, peak_rss, receipt


def _binomial_power_parameters(
    n: int,
    p_value: Fraction,
    lower: int,
    upper: int,
    boundary: Fraction,
    relation: str,
) -> dict[str, Any]:
    if (
        type(n) is not int
        or type(p_value) is not Fraction
        or type(lower) is not int
        or type(upper) is not int
        or type(boundary) is not Fraction
        or type(relation) is not str
        or relation not in {"ge", "gt", "le", "lt"}
        or n < 0
        or not 0 <= lower <= upper <= n
        or not 0 <= p_value <= 1
        or not 0 <= boundary <= 1
    ):
        raise SelectorError("HOLD_POWER_BOUNDARY", "binomial power input is invalid")
    return {
        "boundary": canonical_rational(boundary),
        "lower": lower,
        "n": n,
        "p_value": canonical_rational(p_value),
        "relation": relation,
        "upper": upper,
    }


def binomial_precision_ladder_decision(
    n: int,
    p_value: Fraction,
    lower: int,
    upper: int,
    boundary: Fraction,
    relation: str,
) -> dict[str, Any]:
    """Evaluate a binomial power decision only in a terminating verified worker."""

    parameters = _binomial_power_parameters(n, p_value, lower, upper, boundary, relation)
    result, _peak_rss, _receipt = _isolated_power_decision("binomial_decision", parameters)
    return result


def _dkw_power_parameters(
    a_min: Fraction,
    alpha: Fraction,
    n: int,
    boundary: Fraction,
    relation: str,
) -> dict[str, Any]:
    if (
        type(a_min) is not Fraction
        or type(alpha) is not Fraction
        or type(n) is not int
        or type(boundary) is not Fraction
        or type(relation) is not str
        or relation not in {"ge", "gt", "le", "lt"}
        or a_min <= 0
        or not 0 < alpha < 1
        or n <= 0
        or not 0 <= boundary <= 1
    ):
        raise SelectorError("HOLD_POWER_BOUNDARY", "DKW power input is invalid")
    return {
        "a_min": canonical_rational(a_min),
        "alpha": canonical_rational(alpha),
        "boundary": canonical_rational(boundary),
        "n": n,
        "relation": relation,
    }


def dkw_precision_ladder_decision(
    a_min: Fraction,
    alpha: Fraction,
    n: int,
    boundary: Fraction,
    relation: str,
) -> dict[str, Any]:
    """Evaluate a DKW power decision only in a terminating verified worker."""

    parameters = _dkw_power_parameters(a_min, alpha, n, boundary, relation)
    result, _peak_rss, _receipt = _isolated_power_decision("dkw_decision", parameters)
    return result


@dataclass(frozen=True)
class BinomialPowerAssertion:
    assertion_id: str
    family: str
    n: int
    p_value: Fraction
    lower: int
    upper: int
    boundary: Fraction
    relation: str


@dataclass(frozen=True)
class DKWPowerAssertion:
    assertion_id: str
    family: str
    a_min: Fraction
    alpha: Fraction
    n: int
    boundary: Fraction
    relation: str


def _validated_powered_assertion_schedule(
    assertions: tuple[BinomialPowerAssertion | DKWPowerAssertion, ...],
) -> tuple[
    bytes,
    tuple[tuple[str, str, str, dict[str, Any]], ...],
    dict[str, int],
]:
    if type(assertions) is not tuple or len(assertions) != 68:
        raise SelectorError("HOLD_POWER_BOUNDARY", "powered assertion schedule is not length 68")
    counts = {family: 0 for family in POWER_ASSERTION_COUNTS}
    prepared: list[tuple[str, str, str, dict[str, Any]]] = []
    payloads = []
    for assertion, (expected_family, expected_id, expected_operation) in zip(
        assertions, POWER_ASSERTION_LAYOUT, strict=True
    ):
        if type(assertion) not in {BinomialPowerAssertion, DKWPowerAssertion}:
            raise SelectorError("HOLD_POWER_BOUNDARY", "powered assertion record is untyped")
        if (
            type(assertion.assertion_id) is not str
            or assertion.assertion_id != expected_id
            or type(assertion.family) is not str
            or assertion.family != expected_family
        ):
            raise SelectorError(
                "HOLD_POWER_BOUNDARY", "powered assertion identity or order changed"
            )
        counts[assertion.family] += 1
        if expected_operation == "binomial_decision" and type(assertion) is BinomialPowerAssertion:
            parameters = _binomial_power_parameters(
                assertion.n,
                assertion.p_value,
                assertion.lower,
                assertion.upper,
                assertion.boundary,
                assertion.relation,
            )
        elif expected_operation == "dkw_decision" and type(assertion) is DKWPowerAssertion:
            parameters = _dkw_power_parameters(
                assertion.a_min,
                assertion.alpha,
                assertion.n,
                assertion.boundary,
                assertion.relation,
            )
        else:
            raise SelectorError("HOLD_POWER_BOUNDARY", "powered assertion family type changed")
        prepared.append((assertion.assertion_id, assertion.family, expected_operation, parameters))
        payloads.append(
            {
                "assertion_id": assertion.assertion_id,
                "family": assertion.family,
                "operation": expected_operation,
                "parameters": parameters,
            }
        )
    validate_family_ledger(counts)
    schedule_raw = canonical_json_bytes({"assertions": payloads, "schema_version": 1})
    return schedule_raw, tuple(prepared), counts


def powered_assertion_schedule_bytes(
    assertions: tuple[BinomialPowerAssertion | DKWPowerAssertion, ...],
) -> bytes:
    """Return the complete canonical parameter contract after full prevalidation."""

    schedule_raw, _prepared, _counts = _validated_powered_assertion_schedule(assertions)
    return schedule_raw


def execute_powered_assertion_schedule(
    assertions: tuple[BinomialPowerAssertion | DKWPowerAssertion, ...],
    *,
    expected_schedule_sha256: str,
) -> dict[str, Any]:
    """Execute one prevalidated, content-pinned 68-assertion schedule serially."""

    schedule_raw, prepared, counts = _validated_powered_assertion_schedule(assertions)
    observed_schedule_sha256 = sha256_bytes(schedule_raw)
    if (
        type(expected_schedule_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", expected_schedule_sha256) is None
        or observed_schedule_sha256 != expected_schedule_sha256
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "powered assertion schedule hash changed")
    decision_counts = {"FAIL": 0, "PASS": 0}
    maximum_worker_peak = 0
    receipts = []
    for assertion_id, family, operation, parameters in prepared:
        result, peak, receipt = _isolated_power_decision(
            operation,
            parameters,
            assertion_id=assertion_id,
            schedule_sha256=observed_schedule_sha256,
        )
        decision_counts[result["decision"]] += 1
        maximum_worker_peak = max(maximum_worker_peak, peak)
        receipts.append({**receipt, "family": family})
        if result["decision"] != "PASS":
            raise SelectorError("HOLD_POWER_BOUNDARY", f"powered assertion {assertion_id} failed")
    return {
        "assertion_count": len(assertions),
        "assertion_receipts": receipts,
        "assertion_schedule_sha256": observed_schedule_sha256,
        "decision_counts": decision_counts,
        "family_counts": counts,
        "maximum_worker_peak_rss_bytes": maximum_worker_peak,
        "positive_budget_evaluated": False,
        "schedule_kind": "CALLER_SUPPLIED_UNCLASSIFIED",
        "schema_version": 1,
        "status": "PASS_POWERED_ASSERTION_EXECUTION",
    }


def run_synthetic_power_resource_gate(n: int = 8_000_000) -> dict[str, Any]:
    """Run the frozen synthetic fixture without claiming an accepted science schedule."""

    fixture = synthetic_power_resource_fixture(n)
    schedule_sha256 = sha256_bytes(powered_assertion_schedule_bytes(fixture))
    result = execute_powered_assertion_schedule(fixture, expected_schedule_sha256=schedule_sha256)
    return {
        **result,
        "schedule_kind": "SYNTHETIC_RESOURCE_FIXTURE",
        "status": "PASS_SYNTHETIC_SCIENCE_FREE_POWER_RESOURCE_GATE",
    }


def synthetic_power_resource_fixture(
    n: int = 8_000_000,
) -> tuple[BinomialPowerAssertion | DKWPowerAssertion, ...]:
    if type(n) is not int or n < 100_000:
        raise SelectorError("HOLD_POWER_BOUNDARY", "synthetic resource N is invalid")
    records = []
    for family, count, operation in POWER_ASSERTION_FAMILY_LAYOUT:
        for index in range(1, count + 1):
            assertion_id = f"{family}:{index:02d}"
            if operation == "dkw_decision":
                records.append(
                    DKWPowerAssertion(
                        assertion_id=assertion_id,
                        family=family,
                        a_min=Fraction(1, 20),
                        alpha=ALPHA_SURVIVAL_MEMBER,
                        n=n,
                        boundary=1 - BETA_MEMBER,
                        relation="ge",
                    )
                )
            else:
                records.append(
                    BinomialPowerAssertion(
                        assertion_id=assertion_id,
                        family=family,
                        n=n,
                        p_value=Fraction(1, 200),
                        lower=40_646,
                        upper=n,
                        boundary=Fraction(1, 1_600),
                        relation="lt",
                    )
                )
    return tuple(records)


def verify_special_certificate(
    producer: MPInterval,
    verifier: MPInterval,
    boundary: Fraction,
    relation: str,
) -> bool:
    producer_lower, producer_upper = producer.exact_fraction_pair()
    verifier_lower, verifier_upper = verifier.exact_fraction_pair()
    if not producer_lower <= verifier_lower <= verifier_upper <= producer_upper:
        return False
    if relation == "gt":
        return producer_lower > boundary and verifier_lower > boundary
    if relation == "lt":
        return producer_upper < boundary and verifier_upper < boundary
    raise ValueError("unknown relation")


def philox4x32(counter: Sequence[int], key: Sequence[int], rounds: int = 10) -> tuple[int, ...]:
    if len(counter) != 4 or len(key) != 2 or not 1 <= rounds <= 16:
        raise ValueError("invalid Philox shape or round count")
    words = tuple(int(value) & MASK32 for value in counter)
    key_words = [int(value) & MASK32 for value in key]
    for round_index in range(rounds):
        product0 = PHILOX_M0 * words[0]
        product1 = PHILOX_M1 * words[2]
        words = (
            ((product1 >> 32) ^ words[1] ^ key_words[0]) & MASK32,
            product1 & MASK32,
            ((product0 >> 32) ^ words[3] ^ key_words[1]) & MASK32,
            product0 & MASK32,
        )
        if round_index != rounds - 1:
            key_words[0] = (key_words[0] + PHILOX_W0) & MASK32
            key_words[1] = (key_words[1] + PHILOX_W1) & MASK32
    return words


def philox4x32_10(counter: Sequence[int], key: Sequence[int]) -> tuple[int, ...]:
    return philox4x32(counter, key, rounds=10)


def verify_rng_specs() -> dict[str, Any]:
    if sha256_file(PHILOX_SPEC_PATH) != EXPECTED_PHILOX_SPEC_SHA256:
        raise SelectorError("HOLD_RNG_SPEC", "Philox spec hash changed")
    if sha256_file(TEST_KEY_SET_PATH) != EXPECTED_TEST_KEY_SET_SHA256:
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key-set hash changed")
    if sha256_file(CENTRAL_PROJECTION_SPEC_PATH) != EXPECTED_CENTRAL_PROJECTION_SHA256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "central projection spec hash changed")
    spec = strict_load_canonical_json(PHILOX_SPEC_PATH.read_bytes())
    for vector in spec["known_answer_vectors"]:
        counter = tuple(int(word, 16) for word in vector["counter_words"])
        key = tuple(int(word, 16) for word in vector["key_words"])
        expected = tuple(int(word, 16) for word in vector["output_words"])
        if philox4x32_10(counter, key) != expected:
            raise SelectorError("HOLD_RNG_SPEC", "Philox known-answer vector mismatch")
    return {
        "algorithm": spec["algorithm"],
        "philox_spec_sha256": EXPECTED_PHILOX_SPEC_SHA256,
        "test_key_set_sha256": EXPECTED_TEST_KEY_SET_SHA256,
    }


def verify_runtime_spec() -> dict[str, Any]:
    runtime_raw = _read_ordinary_file_snapshot(
        RUNTIME_SPEC_PATH,
        "special-function runtime spec snapshot changed",
        maximum_bytes=65_536,
    )
    runtime_spec_sha256 = sha256_bytes(runtime_raw)
    if runtime_spec_sha256 != EXPECTED_RUNTIME_SPEC_SHA256:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "special-function runtime spec hash changed")
    runtime = strict_load_canonical_json(runtime_raw)
    import gmpy2.gmpy2 as gmpy2_core

    library_directory = Path(gmpy2_core.__file__).resolve().parent.parent / "gmpy2.libs"
    observed = {
        "gmp": {
            "library_sha256": sha256_file(library_directory / "libgmp.10.dylib"),
            "version": gmpy2.mp_version().removeprefix("GMP "),
        },
        "gmpy2": {
            "extension_sha256": sha256_file(Path(gmpy2_core.__file__)),
            "package_init_sha256": sha256_file(Path(gmpy2.__file__)),
            "version": gmpy2.version(),
        },
        "jsonschema": {
            "draft": "2020-12",
            "version": importlib.metadata.version("jsonschema"),
        },
        "mpc": {
            "library_sha256": sha256_file(library_directory / "libmpc.3.dylib"),
            "version": gmpy2.mpc_version().removeprefix("MPC "),
        },
        "mpfr": {
            "emax": gmpy2.get_context().emax,
            "emin": gmpy2.get_context().emin,
            "library_sha256": sha256_file(library_directory / "libmpfr.6.dylib"),
            "subnormalize": gmpy2.get_context().subnormalize,
            "version": gmpy2.mpfr_version().removeprefix("MPFR "),
        },
        "python": {
            "binary_sha256": sha256_file(Path(sys.executable)),
            "implementation": sys.implementation.name.replace("cpython", "CPython"),
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "schema_version": 1,
        "special_dag": {
            "canonical_interval_endpoint_encoding": "mpfr-base16-mantissa-exponent-precision",
            "precision_bits": list(PRECISION_LADDER),
            "producer_lower_rounding": "MPFR_RNDD",
            "producer_upper_rounding": "MPFR_RNDU",
        },
    }
    if observed != runtime:
        raise SelectorError("HOLD_DEPENDENCY_HASH", "special-function runtime identity changed")
    return {"runtime_spec_sha256": runtime_spec_sha256, "runtime_verified": True}


def derive_seed_basis(
    accepted_f1_manifest_sha256: str,
    accepted_f1_result_sha256: str,
    accepted_f1_audit_sha256: str,
) -> bytes:
    fields = (
        accepted_f1_manifest_sha256,
        accepted_f1_result_sha256,
        accepted_f1_audit_sha256,
        EXPECTED_PHILOX_SPEC_SHA256,
        EXPECTED_TEST_KEY_SET_SHA256,
        EXPECTED_CENTRAL_PROJECTION_SHA256,
        EXPECTED_RUNTIME_SPEC_SHA256,
    )
    if any(
        type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in fields
    ):
        raise SelectorError("HOLD_DEPENDENCY_HASH", "seed dependency is not lowercase SHA-256")
    decoded = b"".join(bytes.fromhex(value) for value in fields)
    return hashlib.sha256(b"encounter-f2-common-observable-v2\0" + decoded).digest()


def load_test_keys() -> tuple[int, ...]:
    try:
        raw = TEST_KEY_SET_PATH.read_bytes()
    except OSError as exc:
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key-set file cannot be read") from exc
    if sha256_bytes(raw) != EXPECTED_TEST_KEY_SET_SHA256:
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key-set hash changed at point of use")
    payload = strict_load_canonical_json(raw)
    if not isinstance(payload, dict) or set(payload) != {
        "format",
        "ordered_keys_be_u64_hex",
        "schema_version",
        "set_purpose",
    }:
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key-set shape changed")
    if (
        type(payload["schema_version"]) is not int
        or payload["schema_version"] != 1
        or payload["format"] != "unsigned-64-bit-big-endian-lowercase-hex"
        or payload["set_purpose"]
        != "pre-f1 excluded philox4x32-10 known-answer and transform test keys"
        or not isinstance(payload["ordered_keys_be_u64_hex"], list)
        or len(payload["ordered_keys_be_u64_hex"]) != 8
        or any(
            type(text) is not str or re.fullmatch(r"[0-9a-f]{16}", text) is None
            for text in payload["ordered_keys_be_u64_hex"]
        )
    ):
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key-set identity or encoding changed")
    values = tuple(int(text, 16) for text in payload["ordered_keys_be_u64_hex"])
    if values != EXPECTED_TEST_KEYS or len(values) != len(set(values)):
        raise SelectorError("HOLD_TEST_KEY_SET", "test-key order or identity changed")
    return values


def derive_pool_keys(seed_basis: bytes) -> dict[tuple[int, int], int]:
    if type(seed_basis) is not bytes or len(seed_basis) != 32:
        raise SelectorError("HOLD_RNG_SPEC", "seed basis must be exactly 32 immutable bytes")
    excluded = set(load_test_keys())
    keys = {}
    for control in range(3):
        for pool in range(2):
            digest = hashlib.sha256(
                b"philox-pool-v2\0" + seed_basis + bytes((control, pool))
            ).digest()
            key = int.from_bytes(digest[:8], "big", signed=False)
            keys[(control, pool)] = key
    if len(set(keys.values())) != 6 or any(value in excluded for value in keys.values()):
        raise SelectorError("HOLD_SEED_COLLISION", "production pool key collision")
    return keys


def counter_and_key_words(
    draw_block: int, trajectory_id: int, pool_key64: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if (
        not 0 <= draw_block <= MASK64
        or not 0 <= trajectory_id <= MASK64
        or not 0 <= pool_key64 <= MASK64
    ):
        raise ValueError("counter or key outside uint64")
    return (
        (
            draw_block & MASK32,
            (draw_block >> 32) & MASK32,
            trajectory_id & MASK32,
            (trajectory_id >> 32) & MASK32,
        ),
        (pool_key64 & MASK32, (pool_key64 >> 32) & MASK32),
    )


def chunk_id(
    seed_basis: bytes,
    control: int,
    pool: int,
    chunk_index: int,
    first_trajectory: int,
    exclusive_last_trajectory: int,
) -> str:
    if not (0 <= control < 3 and 0 <= pool < 2):
        raise ValueError("invalid control or pool")
    integers = (chunk_index, first_trajectory, exclusive_last_trajectory)
    if (
        any(not 0 <= value <= MASK64 for value in integers)
        or first_trajectory >= exclusive_last_trajectory
    ):
        raise ValueError("invalid chunk interval")
    message = (
        b"philox-chunk-v2\0"
        + seed_basis
        + bytes((control, pool))
        + b"".join(value.to_bytes(8, "big") for value in integers)
    )
    return hashlib.sha256(message).hexdigest()


def first_passing_schedule(pass_predicate: Callable[[str, int], bool]) -> dict[str, int]:
    selected = {}
    for control in CONTROL_ORDER:
        selected_n = next((n for n in CANDIDATE_GRID if pass_predicate(control, n)), None)
        if selected_n is None:
            raise SelectorError("HOLD_N_CAP", f"{control} has no passing candidate")
        selected[control] = selected_n
    if 2 * sum(selected.values()) > WHOLE_CAMPAIGN_CAP:
        raise SelectorError("HOLD_N_CAP", "whole-campaign trajectory cap exceeded")
    return selected


def require_no_refit(selector_core_sha256: str, f1b_echo_sha256: str) -> None:
    if selector_core_sha256 != f1b_echo_sha256:
        raise SelectorError("HOLD_NO_REFIT_VIOLATION", "F1-B changed the selected bytes")


def run_science_free_self_check() -> dict[str, Any]:
    rng = verify_rng_specs()
    runtime = verify_runtime_spec()
    minimum_subnormal = float.fromhex("0x0.0000000000001p-1022")
    if minimum_subnormal == 0 or Fraction.from_float(minimum_subnormal) != Fraction(1, 1 << 1074):
        raise SelectorError("HOLD_NUMERIC_LEAF", "binary64 subnormal was flushed to zero")
    zero_10 = tuple(f"{word:08x}" for word in philox4x32_10((0, 0, 0, 0), (0, 0)))
    zero_7 = tuple(f"{word:08x}" for word in philox4x32((0, 0, 0, 0), (0, 0), 7))
    if zero_10 == zero_7:
        raise SelectorError("HOLD_RNG_SPEC", "seven-round mutation was not killed")
    return {
        "authorized_scientific_command": None,
        "canonical_constants": {
            "basin_floor": canonical_rational(BASIN_FLOOR),
            "h_cap": canonical_rational(H_CAP),
            "tau_basin_cap": canonical_rational(TAU_CAPS["basin"]),
            "tau_survival_cap": canonical_rational(TAU_CAPS["survival"]),
        },
        "candidate_count": len(CANDIDATE_GRID),
        "central_projection_spec_sha256": EXPECTED_CENTRAL_PROJECTION_SHA256,
        "f1_executed": False,
        "monte_carlo_executed": False,
        "philox4x32_10_zero_vector": list(zero_10),
        "philox4x32_7_zero_vector": list(zero_7),
        "positive_budget_evaluated": False,
        "rng": rng,
        "runtime": runtime,
        "subnormal_preserved": True,
        "schema_version": 2,
        "status": "PASS_SCIENCE_FREE_SELF_CHECK",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--synthetic-power-resource-gate", action="store_true")
    parser.add_argument("--internal-cp-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--internal-power-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if (
        sum(
            (
                args.self_check,
                args.synthetic_power_resource_gate,
                args.internal_cp_worker,
                args.internal_power_worker,
            )
        )
        != 1
    ):
        parser.error("exactly one explicit science-free mode is required")
    if args.internal_cp_worker:
        authorization = _worker_authorization_from_inherited_descriptor()
        raw = sys.stdin.buffer.read(16_385)
        if len(raw) > 16_384:
            raise SelectorError("HOLD_SCHEMA", "CP worker request exceeds its byte cap")
        sys.stdout.buffer.write(_run_internal_cp_worker(raw, authorization))
        return 0
    if args.internal_power_worker:
        authorization = _worker_authorization_from_inherited_descriptor()
        raw = sys.stdin.buffer.read(32_769)
        if len(raw) > 32_768:
            raise SelectorError("HOLD_SCHEMA", "power worker request exceeds its byte cap")
        sys.stdout.buffer.write(_run_internal_power_worker(raw, authorization))
        return 0
    if args.synthetic_power_resource_gate:
        result = run_synthetic_power_resource_gate()
    else:
        result = run_science_free_self_check()
    print(canonical_json_bytes(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
