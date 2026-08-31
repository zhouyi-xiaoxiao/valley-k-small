"""Deterministic semantic F0 candidate with the compiled method fixture.

This producer has no public scientific numerical input.  It binds immutable
claim, selector, configuration, topology, and closed synthetic-operator
fixtures, runs the frozen heterogeneous operator-to-compiled-stream-to-
topology method fixture, then emits canonical ASCII JSON.  The artifact still
cannot self-authorize F0 or F1: the largest-shape measured resource execution
and the implementation-independent replay remain separate required gates.

The legacy topology engine is reachable only through a private, exact-type
adapter closed over three fixed rational polynomials.  Neither a caller oracle
nor a legacy self-declared ``science_free`` Boolean is accepted as authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, NoReturn, Sequence

import numpy as np

_SOURCE_PATH_AT_IMPORT: Final = Path(__file__).resolve(strict=True)
_CODE_DIR: Final = _SOURCE_PATH_AT_IMPORT.parent
if str(_CODE_DIR) not in sys.path:
    # ``python -I path/to/this_file.py`` intentionally omits the script
    # directory.  This fixed insertion enables clean isolated replicas; it
    # does not accept a caller-controlled module path.
    sys.path.insert(0, str(_CODE_DIR))

import rate_defined_tensor_f0 as legacy  # noqa: E402
import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched  # noqa: E402
import rate_defined_tensor_f0_compiled_batch_v1 as integrated  # noqa: E402
import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled  # noqa: E402
import rate_defined_tensor_f0_production_operator_v1 as operator  # noqa: E402


class CandidateFailure(RuntimeError):
    """Fail-closed semantic-candidate outcome with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


HOLD_SOURCE: Final = "HOLD_F0_CANDIDATE_SOURCE_BINDING"
HOLD_JSON: Final = "HOLD_F0_CANDIDATE_CANONICAL_JSON"
HOLD_SELECTOR: Final = "HOLD_F0_CANDIDATE_SELECTOR_BOUNDARY"
HOLD_CONFIGURATION: Final = "HOLD_F0_CANDIDATE_CONFIGURATION"
HOLD_OPERATOR: Final = "HOLD_F0_CANDIDATE_OPERATOR_FIXTURE"
HOLD_TOPOLOGY: Final = "HOLD_F0_CANDIDATE_ANALYTIC_TOPOLOGY"
HOLD_CLAIM: Final = "HOLD_F0_CANDIDATE_FALSE_PROMOTION"

SCHEMA: Final = "rate_defined_tensor_f0_candidate_v1_method_complete"
STATUS: Final = "PASS_F0_METHOD_CANDIDATE_AWAITING_RESOURCE_AND_INDEPENDENT_AUDIT"
STAGE: Final = "F0_DETERMINISTIC_METHOD_CANDIDATE_PRE_RESOURCE_ACCEPTANCE"
INTEGRATED_STATUS: Final = "PASS_FIXED_HETEROGENEOUS_COMPILED_TOPOLOGY_METHOD"
SOURCE_OBSERVATION_SCOPE: Final = (
    "SAME_PROCESS_SELF_OBSERVED_NON_AUTHORITATIVE"
)

_REPORT_DIR: Final = _CODE_DIR.parent
_TEST_PATH_AT_IMPORT: Final = (
    _CODE_DIR / "test_rate_defined_tensor_f0_candidate_v1.py"
).resolve()
_LEGACY_PATH_AT_IMPORT: Final = Path(legacy.__file__).resolve(strict=True)
_OPERATOR_PATH_AT_IMPORT: Final = Path(operator.__file__).resolve(strict=True)
_BATCHED_PATH_AT_IMPORT: Final = Path(batched.__file__).resolve(strict=True)
_COMPILED_PATH_AT_IMPORT: Final = Path(compiled.__file__).resolve(strict=True)
_INTEGRATED_PATH_AT_IMPORT: Final = Path(integrated.__file__).resolve(strict=True)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as error:
        raise CandidateFailure(HOLD_SOURCE, f"source unavailable: {path}") from error


_SOURCE_SHA256_AT_IMPORT: Final = _sha256_path(_SOURCE_PATH_AT_IMPORT)
_TEST_SHA256_AT_IMPORT: Final = _sha256_path(_TEST_PATH_AT_IMPORT)

_PINNED_SOURCES: Final = (
    (
        "candidate_freeze",
        "notes/rate_defined_tensor_f0_candidate_v1_freeze.md",
        "0f282f7227220c4a0dc6ae13996ee650759d0cf6679a6d360897929386796d9b",
    ),
    (
        "completion_contract_human",
        "notes/manuscript_completion_contract_v1.md",
        "cf60bad1680d487e610811c60e5d9e37fa27a87b935f94adcf83a5b8b6ec716d",
    ),
    (
        "completion_contract_json",
        "artifacts/data/manuscript_completion_contract_v1.json",
        "f32fee61edb48fad4e0da0ad5e747db8c417fd25c3acb18da74354c60ec68ee0",
    ),
    (
        "completion_contract_independent_audit",
        "audits/round_186_manuscript_completion_contract_independent_attack.md",
        "a14a7a1657dd467e7133c4ef2a57e76a829105ac65e62d3d763dcfa7e0c5231b",
    ),
    (
        "exact_selector",
        "scratch/modal_certificate_exact_selector_method_only_result.json",
        "77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98",
    ),
    (
        "control_free_configurations",
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    (
        "fixed_36_row_design",
        "notes/positive_b_fixed_control_robustness_design_v2.md",
        "264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd",
    ),
    (
        "legacy_topology_engine",
        "code/rate_defined_tensor_f0.py",
        "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5",
    ),
    (
        "legacy_topology_test",
        "code/test_rate_defined_tensor_f0.py",
        "f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d",
    ),
    (
        "closed_operator_engine",
        "code/rate_defined_tensor_f0_production_operator_v1.py",
        "dc46bbf39c72df547e7bd9f5364969b0b39293f84db19509353a712221bb5908",
    ),
    (
        "closed_operator_test",
        "code/test_rate_defined_tensor_f0_production_operator_v1.py",
        "b22c446aa747449a486818d5ce14af46a8a9bc3c6a55da84bababbd7f4ecfe1c",
    ),
    (
        "batched_scalar_source",
        "code/rate_defined_tensor_f0_batched_scalar_uniformization_v1.py",
        "56b783f073528146e6cdd3321f078a89978b5e5453b8fdfcabfe35412614b280",
    ),
    (
        "batched_scalar_test",
        "code/test_rate_defined_tensor_f0_batched_scalar_uniformization_v1.py",
        "ddddb839f3b50c1dc2ca05fbce2ddad1b5e025d08f549665585b7a866159dac1",
    ),
    (
        "compiled_power_c_source",
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.c",
        "9db8c672a04732b23dedb332854c4f4259911cfac32ec130d1d16b64db274917",
    ),
    (
        "compiled_power_python_source",
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.py",
        "13c7fabd4118c3858b03d839dcfea037eb15eb6b64b08f7fb69f0757342eae55",
    ),
    (
        "compiled_power_test",
        "code/test_rate_defined_tensor_f0_compiled_power_stream_v1.py",
        "513c0ce06b4424c4a8c3cf6cfea3bb21cd588fc389af8a9e760e451fb9b6dd51",
    ),
    (
        "compiled_batch_source",
        "code/rate_defined_tensor_f0_compiled_batch_v1.py",
        "798d605d5cfc79319a633a5f9e487b4da34a55638b534f35804b3636cb402aa7",
    ),
    (
        "compiled_batch_test",
        "code/test_rate_defined_tensor_f0_compiled_batch_v1.py",
        "c1a378aa9851335391d3dfd016be8cf7943abfc388754eb9fb5d59c49d941e4e",
    ),
)

_CONTROL_ORDER: Final = ("lp_m1", "lp_m2", "lp_m3")
_SELECTOR_KEYS: Final = ("m1", "m2", "m3")
_SELECTOR_TO_ROLE: Final = {
    "m1": "lp_m1",
    "m2": "lp_m2",
    "m3": "lp_m3",
}
_CONFIGURATION_ORDER: Final = (
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
_COORDINATE_ORDER: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
_ANALYTIC_ROOTS: Final = {
    "lp_m1": (Fraction(8),),
    "lp_m2": (Fraction(4), Fraction(9), Fraction(24)),
    "lp_m3": (
        Fraction(3),
        Fraction(6),
        Fraction(9),
        Fraction(14),
        Fraction(24),
    ),
}
_EXPECTED_TOPOLOGY_LEDGERS: Final = {
    "lp_m1": (146, 350, 147, 4),
    "lp_m2": (162, 498, 168, 4),
    "lp_m3": (178, 646, 188, 4),
}
_INTEGRATED_QUERY_TIMES: Final = (
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(7, 8),
    Fraction(15, 16),
    Fraction(1),
    Fraction(17, 16),
    Fraction(35, 32),
    Fraction(71, 64),
    Fraction(5_061_605_598_534_793, 4_503_599_627_370_496),
    Fraction(1_265_448_808_820_377, 1_125_899_906_842_624),
    Fraction(5_061_807_140_876_903, 4_503_599_627_370_496),
    Fraction(2_530_903_570_783_937, 2_251_799_813_685_248),
    Fraction(5_061_807_141_589_427, 4_503_599_627_370_496),
    Fraction(2_530_903_570_794_729, 2_251_799_813_685_248),
    Fraction(9, 8),
    Fraction(73, 64),
    Fraction(37, 32),
    Fraction(19, 16),
    Fraction(5, 4),
    Fraction(21, 16),
    Fraction(11, 8),
    Fraction(3, 2),
    Fraction(13, 8),
    Fraction(7, 4),
    Fraction(15, 8),
)
_VALID_FORWARD_RADIUS: Final = Fraction(1, 4)
_DERIVATIVE_PADDING: Final = Fraction(1, 10**9)


def _fail_json_constant(value: str) -> NoReturn:
    raise CandidateFailure(HOLD_JSON, f"nonfinite JSON constant forbidden: {value}")


def _fail_json_float(value: str) -> NoReturn:
    raise CandidateFailure(HOLD_JSON, f"JSON floating point forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateFailure(HOLD_JSON, "duplicate or non-string object key")
        result[key] = value
    return result


def _validate_json_tree(value: Any, *, path: str = "$") -> None:
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_json_tree(item, path=f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise CandidateFailure(HOLD_JSON, f"{path} has a non-string key")
            _validate_json_tree(item, path=f"{path}.{key}")
        return
    raise CandidateFailure(
        HOLD_JSON,
        f"{path} has forbidden type {type(value).__name__}",
    )


def _strict_json_load_bytes(payload: bytes) -> dict[str, Any]:
    if type(payload) is not bytes:
        raise CandidateFailure(HOLD_JSON, "JSON payload must be exact bytes")
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise CandidateFailure(HOLD_JSON, "JSON payload must be ASCII") from error
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_float=_fail_json_float,
            parse_constant=_fail_json_constant,
        )
    except CandidateFailure:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise CandidateFailure(HOLD_JSON, "malformed strict JSON") from error
    if type(parsed) is not dict:
        raise CandidateFailure(HOLD_JSON, "top-level JSON must be an exact object")
    _validate_json_tree(parsed)
    return parsed


def _strict_json_source(
    relative_path: str,
    expected_sha256: str,
) -> dict[str, Any]:
    path = (_REPORT_DIR / relative_path).resolve(strict=True)
    payload = path.read_bytes()
    if _sha256_bytes(payload) != expected_sha256:
        raise CandidateFailure(HOLD_SOURCE, f"immutable JSON drift: {relative_path}")
    return _strict_json_load_bytes(payload)


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    _validate_json_tree(payload)
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (TypeError, ValueError) as error:
        raise CandidateFailure(HOLD_JSON, "artifact is not canonicalizable") from error


def _require_exact_keys(
    value: Any,
    expected: Sequence[str],
    *,
    code: str,
    label: str,
) -> dict[str, Any]:
    if type(value) is not dict or tuple(value) != tuple(expected):
        raise CandidateFailure(code, f"{label} keys/order are invalid")
    return value


def _fraction_text(value: Fraction) -> str:
    if type(value) is not Fraction:
        raise CandidateFailure(HOLD_JSON, "fraction serializer received wrong type")
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_text(value: Any, *, code: str, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateFailure(code, f"{label} is not canonical rational text")
    numerator_text, denominator_text = value.split("/")
    if (
        not numerator_text
        or not denominator_text
        or denominator_text.startswith(("+", "-"))
        or (numerator_text.startswith("+"))
        or not numerator_text.lstrip("-").isdigit()
        or not denominator_text.isdigit()
        or denominator_text.startswith("0") and denominator_text != "0"
    ):
        raise CandidateFailure(code, f"{label} has malformed rational integers")
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    if denominator <= 0:
        raise CandidateFailure(code, f"{label} has nonpositive denominator")
    result = Fraction(numerator, denominator)
    if _fraction_text(result) != value:
        raise CandidateFailure(code, f"{label} is not reduced canonical rational text")
    return result


def _source_pin(label: str) -> tuple[str, str]:
    matches = [
        (path, digest)
        for source_label, path, digest in _PINNED_SOURCES
        if source_label == label
    ]
    if len(matches) != 1:
        raise CandidateFailure(HOLD_SOURCE, f"source pin missing: {label}")
    return matches[0]


def _validate_source_bindings() -> None:
    try:
        if (
            Path(__file__).resolve(strict=True) != _SOURCE_PATH_AT_IMPORT
            or _TEST_PATH_AT_IMPORT.resolve(strict=True) != _TEST_PATH_AT_IMPORT
            or Path(legacy.__file__).resolve(strict=True) != _LEGACY_PATH_AT_IMPORT
            or Path(operator.__file__).resolve(strict=True) != _OPERATOR_PATH_AT_IMPORT
            or Path(batched.__file__).resolve(strict=True) != _BATCHED_PATH_AT_IMPORT
            or Path(compiled.__file__).resolve(strict=True) != _COMPILED_PATH_AT_IMPORT
            or Path(integrated.__file__).resolve(strict=True)
            != _INTEGRATED_PATH_AT_IMPORT
        ):
            raise CandidateFailure(HOLD_SOURCE, "implementation path binding drifted")
    except (OSError, TypeError) as error:
        raise CandidateFailure(HOLD_SOURCE, "implementation path unavailable") from error
    if (
        _sha256_path(_SOURCE_PATH_AT_IMPORT) != _SOURCE_SHA256_AT_IMPORT
        or _sha256_path(_TEST_PATH_AT_IMPORT) != _TEST_SHA256_AT_IMPORT
    ):
        raise CandidateFailure(HOLD_SOURCE, "candidate/test bytes changed after import")
    for _label, relative_path, expected_sha256 in _PINNED_SOURCES:
        path = (_REPORT_DIR / relative_path).resolve(strict=True)
        if _sha256_path(path) != expected_sha256:
            raise CandidateFailure(HOLD_SOURCE, f"pinned source drift: {relative_path}")


def _pinned_source_summary() -> dict[str, Any]:
    _validate_source_bindings()
    return {
        "external_exact_byte_audit_complete": False,
        "external_exact_byte_audit_required": True,
        "live_candidate_sources": [
            {
                "label": "semantic_candidate",
                "path": "code/rate_defined_tensor_f0_candidate_v1.py",
                "sha256": _SOURCE_SHA256_AT_IMPORT,
            },
            {
                "label": "semantic_candidate_test",
                "path": "code/test_rate_defined_tensor_f0_candidate_v1.py",
                "sha256": _TEST_SHA256_AT_IMPORT,
            },
        ],
        "observation_scope": SOURCE_OBSERVATION_SCOPE,
        "pinned_sources": [
            {"label": label, "path": path, "sha256": digest}
            for label, path, digest in _PINNED_SOURCES
        ],
        "source_hashes_authoritative": False,
    }


def _parse_selector_weight(value: Any, *, label: str) -> Fraction:
    expected_keys = (
        "decimal_40_significant",
        "denominator",
        "exact",
        "numerator",
    )
    entry = _require_exact_keys(
        value,
        expected_keys,
        code=HOLD_SELECTOR,
        label=label,
    )
    if (
        type(entry["numerator"]) is not str
        or type(entry["denominator"]) is not str
        or not entry["numerator"].lstrip("-").isdigit()
        or not entry["denominator"].isdigit()
    ):
        raise CandidateFailure(HOLD_SELECTOR, f"{label} integer strings are invalid")
    rational = Fraction(int(entry["numerator"]), int(entry["denominator"]))
    if (
        rational.denominator <= 0
        or _fraction_text(rational) != entry["exact"]
        or rational.numerator != int(entry["numerator"])
        or rational.denominator != int(entry["denominator"])
        or type(entry["decimal_40_significant"]) is not str
    ):
        raise CandidateFailure(HOLD_SELECTOR, f"{label} exact fields disagree")
    return rational


def _selector_control_weights(
    selector: dict[str, Any],
) -> tuple[tuple[str, tuple[Fraction, ...]], ...]:
    results = selector.get("selector_results")
    if type(results) is not dict or tuple(results) != _SELECTOR_KEYS:
        raise CandidateFailure(HOLD_SELECTOR, "selector result key/order drifted")
    parsed: list[tuple[str, tuple[Fraction, ...]]] = []
    for selector_key in _SELECTOR_KEYS:
        result = results[selector_key]
        if type(result) is not dict:
            raise CandidateFailure(HOLD_SELECTOR, "selector result has wrong exact type")
        # Fail closed if the normative selected branch is absent.  Historical
        # raw, S_c, or raw-hex fields can never substitute for it.
        if "selected" not in result or type(result["selected"]) is not dict:
            raise CandidateFailure(
                HOLD_SELECTOR,
                f"{selector_key} lacks normative selected weights",
            )
        weights = result["selected"].get("weights")
        if type(weights) is not list or len(weights) != 4:
            raise CandidateFailure(
                HOLD_SELECTOR,
                f"{selector_key} must contain exactly four selected entries",
            )
        exact_weights = tuple(
            _parse_selector_weight(weight, label=f"{selector_key}.weights[{index}]")
            for index, weight in enumerate(weights)
        )
        if sum(exact_weights, Fraction(0)) != 1:
            raise CandidateFailure(HOLD_SELECTOR, "selector vertex is not unit sum")
        parsed.append((_SELECTOR_TO_ROLE[selector_key], exact_weights))
    return tuple(parsed)


def _row_scale_at(
    selector: dict[str, Any],
    selector_key: str,
    checkpoint: str,
) -> str:
    source = selector["selector_results"][selector_key].get(
        "frozen_coefficient_source"
    )
    if type(source) is not dict:
        raise CandidateFailure(HOLD_SELECTOR, "frozen coefficient source missing")
    times = source.get("checkpoint_times_decimal")
    scales = source.get("row_scales_decimal")
    if (
        type(times) is not list
        or type(scales) is not list
        or len(times) != len(scales)
        or any(type(value) is not str for value in times + scales)
        or times.count(checkpoint) != 1
    ):
        raise CandidateFailure(HOLD_SELECTOR, "checkpoint/row-scale table is invalid")
    return scales[times.index(checkpoint)]


def _selector_boundary_summary(
    contract: dict[str, Any],
    selector: dict[str, Any],
) -> dict[str, Any]:
    parsed = _selector_control_weights(selector)
    if tuple(role for role, _weights in parsed) != _CONTROL_ORDER:
        raise CandidateFailure(HOLD_SELECTOR, "fixed selector-role mapping drifted")
    exact_controls = contract.get("exact_controls")
    if type(exact_controls) is not dict:
        raise CandidateFailure(HOLD_SELECTOR, "completion contract controls missing")
    controls: list[dict[str, Any]] = []
    for role, weights in parsed:
        contract_weights = exact_controls.get(role)
        if (
            type(contract_weights) is not list
            or len(contract_weights) != 4
            or any(type(value) is not str for value in contract_weights)
            or tuple(_fraction_text(value) for value in weights)
            != tuple(contract_weights)
        ):
            raise CandidateFailure(
                HOLD_SELECTOR,
                f"selector and completion contract disagree for {role}",
            )
        controls.append(
            {
                "control_role": role,
                "production_evaluation": False,
                "selected_entry_count": 4,
                "unit_sum_exact": _fraction_text(sum(weights, Fraction(0))),
                "weights": [_fraction_text(value) for value in weights],
            }
        )

    m1_decimal = _row_scale_at(selector, "m1", "5.5")
    m2_decimal = _row_scale_at(selector, "m2", "5.5")
    if m1_decimal != "0.2674801474024189" or m2_decimal != "0.2674801474024188":
        raise CandidateFailure(HOLD_SELECTOR, "one-ulp decimal fixture drifted")
    m1_value = float(m1_decimal)
    m2_value = float(m2_decimal)
    if (
        m1_value.hex() != "0x1.11e650d5b0cacp-2"
        or m2_value.hex() != "0x1.11e650d5b0cabp-2"
        or math.nextafter(m2_value, math.inf) != m1_value
        or Fraction.from_float(m1_value) - Fraction.from_float(m2_value)
        != Fraction(1, 18_014_398_509_481_984)
    ):
        raise CandidateFailure(HOLD_SELECTOR, "one-ulp binary64 fixture is invalid")
    one_ulp_interval = legacy.OutwardInterval(m2_value, m1_value)
    return {
        "accepted_source_kind": "selector_json_selected_numerator_denominator_v2",
        "controls": controls,
        "fixed_role_mapping": [
            {"selector_key": key, "control_role": _SELECTOR_TO_ROLE[key]}
            for key in _SELECTOR_KEYS
        ],
        "positive_budget_production_evaluation": False,
        "retired_source_kind_rejection": {
            "missing_selected_with_raw_fields_is_rejected": True,
            "rejected_source_kinds": ["raw", "S_c", "raw_hex"],
            "selected_entries_required_exactly": 4,
        },
        "t_5_5_adjacent_binary64": {
            "exact_difference": "1/18014398509481984",
            "lower_binary64_hex": one_ulp_interval.lower.hex(),
            "lower_decimal_source": m2_decimal,
            "m1_source_path": (
                "selector_results.m1.frozen_coefficient_source."
                "row_scales_decimal[checkpoint_times_decimal==5.5]"
            ),
            "m2_source_path": (
                "selector_results.m2.frozen_coefficient_source."
                "row_scales_decimal[checkpoint_times_decimal==5.5]"
            ),
            "strictly_adjacent": True,
            "upper_binary64_hex": one_ulp_interval.upper.hex(),
            "upper_decimal_source": m1_decimal,
        },
    }


def _axis_summary(
    axis: legacy.TensorAxis,
    expected: dict[str, Any],
    *,
    coordinate: str,
) -> dict[str, Any]:
    if type(axis) is not legacy.TensorAxis or axis.name != coordinate:
        raise CandidateFailure(HOLD_CONFIGURATION, "constructed axis type/name drifted")
    if type(expected) is not dict:
        raise CandidateFailure(HOLD_CONFIGURATION, "configuration axis row is invalid")
    alignment = expected.get("alignment")
    expected_construction = {
        "cell_centred_reflecting": "cell_centred_reflecting_scharfetter_gummel",
        "vertex_centred_reflecting_dual": (
            "vertex_centred_reflecting_scharfetter_gummel"
        ),
        "cell_centred_periodic_base": "cell_centred_periodic_diffusion",
        "cell_centred_periodic_half_shift": (
            "cell_centred_periodic_diffusion_half_shift"
        ),
    }.get(alignment)
    if (
        type(alignment) is not str
        or expected_construction is None
        or axis.construction != expected_construction
        or type(expected.get("size")) is not int
        or axis.size != expected["size"]
    ):
        raise CandidateFailure(HOLD_CONFIGURATION, "axis alignment construction drifted")
    expected_periodic = coordinate == "relative_perpendicular"
    if axis.periodic is not expected_periodic:
        raise CandidateFailure(HOLD_CONFIGURATION, "axis periodic semantics drifted")
    expected_half_volume = alignment == "vertex_centred_reflecting_dual"
    if axis.has_half_boundary_volumes is not expected_half_volume:
        raise CandidateFailure(HOLD_CONFIGURATION, "axis half-volume semantics drifted")
    expected_shift = (
        _parse_fraction_text(
            expected.get("periodic_shift_exact"),
            code=HOLD_CONFIGURATION,
            label="periodic shift",
        )
        if expected_periodic
        else Fraction(0)
    )
    if axis.periodic_shift != expected_shift:
        raise CandidateFailure(HOLD_CONFIGURATION, "axis periodic shift drifted")
    return {
        "alignment": alignment,
        "construction": axis.construction,
        "coordinate": coordinate,
        "has_half_boundary_volumes": axis.has_half_boundary_volumes,
        "periodic": axis.periodic,
        "periodic_shift_exact": _fraction_text(axis.periodic_shift),
        "reflecting_zero_flux": not axis.periodic,
        "size": axis.size,
    }


def _configuration_summary(configuration: dict[str, Any]) -> dict[str, Any]:
    if (
        configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
        or configuration.get("configuration_count") != 12
        or configuration.get("configuration_order") != list(_CONFIGURATION_ORDER)
        or configuration.get("coordinate_order") != list(_COORDINATE_ORDER)
    ):
        raise CandidateFailure(HOLD_CONFIGURATION, "configuration header drifted")
    rows = configuration.get("configurations")
    if (
        type(rows) is not list
        or len(rows) != 12
        or [row.get("label") for row in rows if type(row) is dict]
        != list(_CONFIGURATION_ORDER)
    ):
        raise CandidateFailure(HOLD_CONFIGURATION, "configuration row order drifted")
    built = legacy.build_all_physical_axes_v2()
    if type(built) is not tuple or len(built) != 12:
        raise CandidateFailure(HOLD_CONFIGURATION, "constructor family is incomplete")
    output_rows: list[dict[str, Any]] = []
    for row, built_row in zip(rows, built, strict=True):
        if type(row) is not dict or type(built_row) is not tuple or len(built_row) != 2:
            raise CandidateFailure(HOLD_CONFIGURATION, "configuration nested type drifted")
        spec, axes = built_row
        if (
            type(spec) is not legacy.PhysicalConfigurationSpec
            or type(axes) is not tuple
            or len(axes) != 3
            or spec.label != row.get("label")
            or type(row.get("shape")) is not list
            or any(type(value) is not int for value in row["shape"])
            or tuple(row["shape"]) != tuple(axis.size for axis in axes)
            or type(row.get("expected_states")) is not int
            or math.prod(row["shape"]) != row["expected_states"]
            or spec.expected_states != row["expected_states"]
        ):
            raise CandidateFailure(HOLD_CONFIGURATION, "configuration shape/state drifted")
        axis_rows = [
            _axis_summary(axis, row[coordinate], coordinate=coordinate)
            for coordinate, axis in zip(_COORDINATE_ORDER, axes, strict=True)
        ]
        output_rows.append(
            {
                "axes": axis_rows,
                "label": spec.label,
                "shape": list(row["shape"]),
                "state_count": spec.expected_states,
            }
        )
    if sum(row["state_count"] for row in output_rows) != 34_787_462:
        raise CandidateFailure(HOLD_CONFIGURATION, "configuration workload drifted")
    return {
        "all_axis_constructors_built": True,
        "configuration_count": 12,
        "configuration_order": list(_CONFIGURATION_ORDER),
        "control_killing_allocated": False,
        "positive_budget_control_evaluated": False,
        "rows": output_rows,
        "total_state_workload": 34_787_462,
    }


def _operator_receipt_summary(
    candidate: operator.ProductionOperatorCandidate,
) -> dict[str, Any]:
    if type(candidate) is not operator.ProductionOperatorCandidate:
        raise CandidateFailure(HOLD_OPERATOR, "closed operator returned wrong exact type")
    operator.validate_production_operator_candidate(candidate)
    receipt = candidate.receipt
    required_true = (
        receipt.exact_type_and_owned_bytes,
        receipt.diagonal_derived_not_supplied,
        receipt.q_killed_row_identity_enclosed,
        receipt.p_submarkov,
        receipt.pairwise_balance_interval_overlap,
        receipt.global_detailed_balance_witness,
        receipt.killing_nonnegative,
        receipt.primary_control_excluded_by_construction,
        receipt.budget_excluded_by_construction,
    )
    required_false = (
        receipt.caller_supplied_unclassified_inputs,
        receipt.topology_executed,
        receipt.authorizes_scientific_execution,
        receipt.science_executed,
        receipt.measured_resource_evidence,
        receipt.production_resource_gate,
        receipt.f0_pass,
        candidate.science_executed,
        candidate.production_resource_gate,
        candidate.f0_pass,
    )
    if (
        any(value is not True for value in required_true)
        or any(value is not False for value in required_false)
        or receipt.source_hashes_authoritative is not False
        or receipt.external_exact_byte_audit_required is not True
        or receipt.external_exact_byte_audit_complete is not False
    ):
        raise CandidateFailure(HOLD_OPERATOR, "closed operator receipt was promoted")
    return {
        "axis_template_edge_count": receipt.axis_template_edge_count,
        "budget_excluded_by_construction": True,
        "diagonal_derived_not_supplied": True,
        "fixture_role": receipt.fixture_role,
        "global_detailed_balance_witness": True,
        "input_manifest_sha256": receipt.input_manifest_sha256,
        "input_provenance": receipt.input_provenance,
        "kernel_binding_sha256": receipt.kernel_binding_sha256,
        "killing_binding_sha256": receipt.killing_binding_sha256,
        "operator_receipt_sha256": receipt.receipt_sha256,
        "pairwise_balance_overlap_chain_sha256": (
            receipt.pairwise_balance_overlap_chain_sha256
        ),
        "primary_control_excluded_by_construction": True,
        "q_killed_row_identity_enclosed": True,
        "state_count": receipt.state_count,
        "tensor_shape": list(receipt.tensor_shape),
        "topology_executed": False,
        "uniformization_rate_exact": _fraction_text(candidate.kernel.rate_fraction),
    }


def _verify_exact_float(value: float, expected: Fraction, *, label: str) -> None:
    if type(value) is not float or Fraction.from_float(value) != expected:
        raise CandidateFailure(HOLD_OPERATOR, f"{label} literal bytes drifted")


def _operator_fixture_summary() -> dict[str, Any]:
    neutral = operator.build_fixed_neutral_synthetic_operator(
        (2, 3),
        block_size=2,
        maximum_working_bytes=20_000,
    )
    for dimension, axis in enumerate(neutral.kernel.axes):
        for index, value in enumerate(neutral.kernel.forward_center[dimension]):
            _verify_exact_float(
                float(value),
                Fraction(0) if index + 1 == axis.size else Fraction(1, 16),
                label="neutral forward",
            )
        for index, value in enumerate(neutral.kernel.backward_center[dimension]):
            _verify_exact_float(
                float(value),
                Fraction(0) if index == 0 else Fraction(1, 16),
                label="neutral backward",
            )
        for endpoints in neutral.stationary_masses[dimension].intervals:
            _verify_exact_float(float(endpoints[0]), Fraction(1), label="neutral mass")
            _verify_exact_float(float(endpoints[1]), Fraction(1), label="neutral mass")
    for endpoints in neutral.kernel.killing.intervals:
        _verify_exact_float(
            float(endpoints[0]),
            Fraction(1, 64),
            label="neutral killing",
        )
        _verify_exact_float(
            float(endpoints[1]),
            Fraction(1, 64),
            label="neutral killing",
        )

    heterogeneous = operator.build_fixed_heterogeneous_two_state_operator(
        block_size=2,
        maximum_working_bytes=20_000,
    )
    axis = heterogeneous.kernel.axes[0]
    expected_forward = (Fraction(1, 2), Fraction(0))
    expected_backward = (Fraction(0), Fraction(1, 4))
    expected_mass = (Fraction(1), Fraction(2))
    expected_killing = (Fraction(1, 8), Fraction(1, 2))
    for index in range(2):
        _verify_exact_float(
            float(heterogeneous.kernel.forward_center[0][index]),
            expected_forward[index],
            label="heterogeneous forward",
        )
        _verify_exact_float(
            float(heterogeneous.kernel.backward_center[0][index]),
            expected_backward[index],
            label="heterogeneous backward",
        )
        _verify_exact_float(
            float(heterogeneous.stationary_masses[0].intervals[index, 0]),
            expected_mass[index],
            label="heterogeneous mass",
        )
        _verify_exact_float(
            float(heterogeneous.kernel.killing.intervals[index, 0]),
            expected_killing[index],
            label="heterogeneous killing",
        )
    if axis.periodic:
        raise CandidateFailure(HOLD_OPERATOR, "heterogeneous axis became periodic")

    return {
        "fixed_heterogeneous_two_state": {
            "dense_generator_exact": [
                ["-5/8", "1/2"],
                ["1/4", "-3/4"],
            ],
            "initial_state_exact": ["1/1", "0/1"],
            "killing_exact": ["1/8", "1/2"],
            "stationary_masses_exact": ["1/1", "2/1"],
            "structural_receipt": _operator_receipt_summary(heterogeneous),
        },
        "fixed_neutral": {
            "directed_rate_exact": "1/16",
            "killing_exact": "1/64",
            "stationary_mass_exact": "1/1",
            "structural_receipt": _operator_receipt_summary(neutral),
        },
        "integrated_compiled_fixture_status": INTEGRATED_STATUS,
    }


class _FixedIntegratedTopologyOracle:
    """Private lookup adapter over frozen, serialized compiled evaluations."""

    __slots__ = ("_lookup", "calls")

    def __init__(
        self,
        result: integrated.CompiledCanonicalScalarSeriesResult,
        metadata: integrated.GenericCompiledBatchMethodMetadata,
    ) -> None:
        if (
            type(result) is not integrated.CompiledCanonicalScalarSeriesResult
            or type(metadata) is not integrated.GenericCompiledBatchMethodMetadata
        ):
            raise CandidateFailure(
                HOLD_TOPOLOGY,
                "integrated oracle received a noncanonical method object",
            )
        integrated.validate_compiled_canonical_scalar_series_result(result)
        if metadata.evaluation_times != _INTEGRATED_QUERY_TIMES:
            raise CandidateFailure(
                HOLD_TOPOLOGY,
                "integrated evaluation schedule is not frozen",
            )
        lookup: dict[Fraction, legacy.TimeJetSample] = {}
        for row in result.evaluations:
            time = Fraction(row.time_numerator, row.time_denominator)
            magnitudes = {bound.order: bound for bound in row.magnitudes}
            if (
                time in lookup
                or tuple(jet.order for jet in row.jets) != (0, 1, 2, 3)
                or set(magnitudes) != {2, 3, 4}
                or row.absolute_time_from_initial is not True
                or row.state_chaining_used is not False
            ):
                raise CandidateFailure(
                    HOLD_TOPOLOGY,
                    "integrated frozen jet semantics drifted",
                )
            try:
                sample = legacy.TimeJetSample(
                    time=time,
                    jets=tuple(
                        legacy.OutwardInterval(
                            float.fromhex(jet.lower_hex),
                            float.fromhex(jet.upper_hex),
                        )
                        for jet in row.jets
                    ),
                    m2=Fraction.from_float(
                        float.fromhex(magnitudes[2].upper_hex)
                    ),
                    m3=Fraction.from_float(
                        float.fromhex(magnitudes[3].upper_hex)
                    ),
                    m4=Fraction.from_float(
                        float.fromhex(magnitudes[4].upper_hex)
                    ),
                    direct_from_initial=True,
                )
            except (KeyError, TypeError, ValueError) as error:
                raise CandidateFailure(
                    HOLD_TOPOLOGY,
                    "integrated scalar row could not be converted",
                ) from error
            sample.validate(time)
            lookup[time] = sample
        if tuple(sorted(lookup)) != _INTEGRATED_QUERY_TIMES:
            raise CandidateFailure(
                HOLD_TOPOLOGY,
                "integrated serialized evaluation set drifted",
            )
        self._lookup = lookup
        self.calls: list[Fraction] = []

    def __call__(self, time: Fraction) -> legacy.TimeJetSample:
        if type(self) is not _FixedIntegratedTopologyOracle or type(time) is not Fraction:
            raise CandidateFailure(
                HOLD_TOPOLOGY,
                "integrated oracle exact type violated",
            )
        self.calls.append(time)
        try:
            return self._lookup[time]
        except KeyError as error:
            raise CandidateFailure(
                HOLD_TOPOLOGY,
                "topology requested a non-frozen integrated time",
            ) from error


def _integrated_compiled_topology_summary() -> dict[str, Any]:
    """Run the frozen heterogeneous operator through the complete method path."""

    try:
        heterogeneous = operator.build_fixed_heterogeneous_two_state_operator(
            block_size=2,
            maximum_working_bytes=20_000,
        )
        operator.validate_production_operator_candidate(heterogeneous)
        witnesses = {
            row.name: row.value for row in heterogeneous.kernel.ledger.witnesses
        }
        required_witnesses = {
            "delta_p_selected",
            "maximum_center_row_sum",
            "maximum_killing_upper",
            "maximum_killing_uncertainty",
        }
        if not required_witnesses.issubset(witnesses):
            raise CandidateFailure(
                HOLD_OPERATOR,
                "heterogeneous interval witness set is incomplete",
            )
        backend = compiled.build_compiled_power_stream_backend(
            heterogeneous.kernel
        )
        initial = np.array((1.0, 0.0), dtype=np.float64)
        initial.setflags(write=False)
        metadata = integrated.GenericCompiledBatchMethodMetadata(
            uniformization_rate=heterogeneous.kernel.rate_fraction,
            coefficient_l1_uncertainty_upper=witnesses["delta_p_selected"],
            maximum_center_row_sum=witnesses["maximum_center_row_sum"],
            maximum_killing_upper=witnesses["maximum_killing_upper"],
            maximum_killing_uncertainty=witnesses[
                "maximum_killing_uncertainty"
            ],
            initial_l1_radius_upper=Fraction(0),
            initial_mass_cap=Fraction(1),
            series_horizon=Fraction(2),
            tail_tolerance=Fraction(1, 10**18),
            mpfr_precision_bits=192,
            maximum_poisson_terms=200_000,
            evaluation_times=_INTEGRATED_QUERY_TIMES,
        )
        result = integrated.build_compiled_canonical_scalar_series(
            backend,
            initial,
            metadata,
        )
        integrated.validate_compiled_canonical_scalar_series_result(result)
    except CandidateFailure:
        raise
    except Exception as error:
        raise CandidateFailure(
            HOLD_OPERATOR,
            "heterogeneous compiled integration failed",
        ) from error

    oracle = _FixedIntegratedTopologyOracle(result, metadata)
    try:
        certificate = legacy.certify_full_window_topology(
            oracle,
            window_lower=Fraction(1, 2),
            window_upper=Fraction(2),
            root_bands=(
                legacy.RootBand(
                    "P1",
                    Fraction(1, 2),
                    Fraction(2),
                    "maximum",
                ),
            ),
            initial_derivative_sign=1,
            initial_tile_width=Fraction(1, 4),
            maximum_bisection_depth=20,
            maximum_newton_steps=12,
            maximum_root_width=Fraction(1, 20),
        )
    except Exception as error:
        raise CandidateFailure(
            HOLD_TOPOLOGY,
            "heterogeneous compiled topology failed",
        ) from error
    unique_times = sorted(set(oracle.calls))
    root = certificate.roots[0] if len(certificate.roots) == 1 else None
    if (
        len(certificate.tiles) != 20
        or len(oracle.calls) != 104
        or len(unique_times) != 26
        or max(tile.depth for tile in certificate.tiles) != 4
        or certificate.complete_window_covered is not True
        or certificate.unresolved_tiles != 0
        or root is None
        or root.role != "P1"
        or root.kind != "maximum"
        or len(root.newton_steps) != 12
        or root.inclusion_observed is not True
        or result.receipt.compiled_power_stream_run_count != 1
        or result.receipt.repeated_p_actions_during_reevaluation != 0
        or result.receipt.resources.maximum_power_index != 26
        or result.receipt.resources.p_action_call_count != 26
        or result.receipt.resources.evaluation_count != 26
        or len(result.evaluations) != 26
    ):
        raise CandidateFailure(
            HOLD_TOPOLOGY,
            "heterogeneous compiled topology ledger drifted",
        )
    series_bytes = batched.canonical_scalar_power_series_bytes(
        result.scalar_series
    )
    compiled_evidence_bytes = integrated.compiled_batch_evidence_bytes(result)
    return {
        "compiled_batch_evidence": _strict_json_load_bytes(
            compiled_evidence_bytes
        ),
        "compiled_batch_evidence_sha256": _sha256_bytes(
            compiled_evidence_bytes
        ),
        "compiled_backend_receipt_sha256": (
            result.receipt.compiled_backend_receipt_sha256
        ),
        "compiled_build_c_source_sha256": (
            result.receipt.compiled_build_receipt.c_source_sha256
        ),
        "compiled_build_python_wrapper_sha256": (
            result.receipt.compiled_build_receipt.python_wrapper_sha256
        ),
        "compiled_power_stream_run_count": 1,
        "compiled_stream_binding_sha256": (
            result.receipt.compiled_stream_receipt.stream_binding_sha256
        ),
        "control_path_evaluated": False,
        "frozen_evaluation_count": 26,
        "initial_state_exact": ["1/1", "0/1"],
        "maximum_depth": 4,
        "maximum_power_index": 26,
        "method_metadata": {
            "coefficient_l1_uncertainty_upper": _fraction_text(
                metadata.coefficient_l1_uncertainty_upper
            ),
            "initial_l1_radius_upper": "0/1",
            "initial_mass_cap": "1/1",
            "maximum_center_row_sum": _fraction_text(
                metadata.maximum_center_row_sum
            ),
            "maximum_killing_uncertainty": _fraction_text(
                metadata.maximum_killing_uncertainty
            ),
            "maximum_killing_upper": _fraction_text(
                metadata.maximum_killing_upper
            ),
            "maximum_poisson_terms": 200_000,
            "mpfr_precision_bits": 192,
            "series_horizon": "2/1",
            "tail_tolerance": "1/1000000000000000000",
            "uniformization_rate": _fraction_text(
                metadata.uniformization_rate
            ),
        },
        "oracle_call_count": 104,
        "p_action_call_count": 26,
        "positive_budget_primary_control_evaluated": False,
        "repeated_p_actions_during_reevaluation": 0,
        "root": _root_summary(root),
        "scalar_series_binding_sha256": result.scalar_series.series_binding_sha256,
        "scalar_series_bytes_sha256": _sha256_bytes(series_bytes),
        "scalar_stream_sha256": result.scalar_series.scalar_stream_sha256,
        "status": INTEGRATED_STATUS,
        "tile_count": 20,
        "tiles": [_tile_summary(tile) for tile in certificate.tiles],
        "unique_call_count": 26,
        "unique_query_times": [
            _fraction_text(value) for value in unique_times
        ],
        "window": ["1/2", "2/1"],
    }


def _poly_multiply(
    left: tuple[Fraction, ...],
    right: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return tuple(result)


def _poly_derivative(
    coefficients: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    if len(coefficients) == 1:
        return (Fraction(0),)
    return tuple(
        Fraction(index) * coefficients[index]
        for index in range(1, len(coefficients))
    )


def _poly_antiderivative(
    coefficients: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    return (Fraction(0),) + tuple(
        coefficients[index] / Fraction(index + 1)
        for index in range(len(coefficients))
    )


def _poly_evaluate(
    coefficients: tuple[Fraction, ...],
    value: Fraction,
) -> Fraction:
    if type(value) is not Fraction:
        raise CandidateFailure(HOLD_TOPOLOGY, "polynomial time has wrong exact type")
    result = Fraction(0)
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def _taylor_absolute_sum_bound(
    f_coefficients: tuple[Fraction, ...],
    time: Fraction,
    derivative_order: int,
) -> Fraction:
    if type(time) is not Fraction or type(derivative_order) is not int:
        raise CandidateFailure(HOLD_TOPOLOGY, "Taylor-bound input type drifted")
    derivative = f_coefficients
    for _unused in range(derivative_order):
        derivative = _poly_derivative(derivative)
    result = Fraction(0)
    taylor_order = 0
    while True:
        result += (
            abs(_poly_evaluate(derivative, time))
            * _VALID_FORWARD_RADIUS**taylor_order
            / Fraction(math.factorial(taylor_order))
        )
        if len(derivative) == 1:
            break
        derivative = _poly_derivative(derivative)
        taylor_order += 1
    return result


class _FixedAnalyticTopologyOracle:
    """Private exact-type adapter closed over one fixed analytic fixture."""

    __slots__ = ("calls", "f_coefficients", "role", "roots")

    def __init__(self, role: str) -> None:
        if type(role) is not str or role not in _CONTROL_ORDER:
            raise CandidateFailure(HOLD_TOPOLOGY, "analytic role is not fixed")
        roots = _ANALYTIC_ROOTS[role]
        derivative = (Fraction(-1),)
        for root in roots:
            derivative = _poly_multiply(
                derivative,
                (-root, Fraction(1)),
            )
        self.role = role
        self.roots = roots
        self.f_coefficients = _poly_antiderivative(derivative)
        self.calls: list[Fraction] = []

    def __call__(self, time: Fraction) -> legacy.TimeJetSample:
        if type(self) is not _FixedAnalyticTopologyOracle or type(time) is not Fraction:
            raise CandidateFailure(HOLD_TOPOLOGY, "private oracle exact type violated")
        self.calls.append(time)
        f_prime = _poly_derivative(self.f_coefficients)
        f_second = _poly_derivative(f_prime)
        f_third = _poly_derivative(f_second)
        j0 = _poly_evaluate(self.f_coefficients, time)
        j1 = _poly_evaluate(f_prime, time)
        j2 = _poly_evaluate(f_second, time)
        j3 = _poly_evaluate(f_third, time)
        sample = legacy.TimeJetSample(
            time=time,
            jets=(
                legacy.OutwardInterval.from_fraction(j0),
                legacy.OutwardInterval.from_fraction_bounds(
                    j1 - _DERIVATIVE_PADDING,
                    j1 + _DERIVATIVE_PADDING,
                ),
                legacy.OutwardInterval.from_fraction(j2),
                legacy.OutwardInterval.from_fraction(j3),
            ),
            m2=_taylor_absolute_sum_bound(self.f_coefficients, time, 2),
            m3=_taylor_absolute_sum_bound(self.f_coefficients, time, 3),
            m4=_taylor_absolute_sum_bound(self.f_coefficients, time, 4),
            direct_from_initial=True,
        )
        if (
            type(sample) is not legacy.TimeJetSample
            or type(sample.time) is not Fraction
            or type(sample.jets) is not tuple
            or len(sample.jets) != 4
            or any(type(value) is not legacy.OutwardInterval for value in sample.jets)
            or any(type(value) is not Fraction for value in (sample.m2, sample.m3, sample.m4))
            or type(sample.direct_from_initial) is not bool
            or sample.direct_from_initial is not True
        ):
            raise CandidateFailure(HOLD_TOPOLOGY, "private oracle sample type drifted")
        sample.validate(time)
        return sample


def _interval_summary(value: legacy.OutwardInterval) -> dict[str, str]:
    if type(value) is not legacy.OutwardInterval:
        raise CandidateFailure(HOLD_TOPOLOGY, "interval has wrong exact type")
    for endpoint in (value.lower, value.upper):
        if (
            type(endpoint) is not float
            or not math.isfinite(endpoint)
            or endpoint == 0.0 and math.copysign(1.0, endpoint) < 0.0
        ):
            raise CandidateFailure(HOLD_TOPOLOGY, "interval endpoint is noncanonical")
    return {
        "lower_binary64_hex": value.lower.hex(),
        "upper_binary64_hex": value.upper.hex(),
    }


def _tile_summary(tile: legacy.TimeTileCertificate) -> dict[str, Any]:
    if (
        type(tile) is not legacy.TimeTileCertificate
        or type(tile.lower) is not Fraction
        or type(tile.upper) is not Fraction
        or type(tile.depth) is not int
        or type(tile.derivative_sign) is not int
        or type(tile.candidate) is not bool
        or tile.upper - tile.lower > _VALID_FORWARD_RADIUS
    ):
        raise CandidateFailure(HOLD_TOPOLOGY, "tile exact type/radius drifted")
    return {
        "candidate": tile.candidate,
        "curvature": _interval_summary(tile.curvature),
        "depth": tile.depth,
        "derivative": _interval_summary(tile.derivative),
        "derivative_sign": tile.derivative_sign,
        "local_lipschitz_curvature": _interval_summary(
            tile.local_lipschitz_curvature
        ),
        "local_lipschitz_derivative": _interval_summary(
            tile.local_lipschitz_derivative
        ),
        "local_taylor_curvature": _interval_summary(tile.local_taylor_curvature),
        "local_taylor_derivative": _interval_summary(tile.local_taylor_derivative),
        "lower": _fraction_text(tile.lower),
        "upper": _fraction_text(tile.upper),
        "valid_forward_span": _fraction_text(tile.upper - tile.lower),
    }


def _newton_summary(step: legacy.IntervalNewtonStep) -> dict[str, Any]:
    if (
        type(step) is not legacy.IntervalNewtonStep
        or type(step.index) is not int
        or type(step.input_lower) is not Fraction
        or type(step.input_upper) is not Fraction
        or type(step.midpoint) is not Fraction
        or type(step.output_lower) is not Fraction
        or type(step.output_upper) is not Fraction
        or type(step.inclusion_in_interior) is not bool
        or step.input_upper - step.input_lower > _VALID_FORWARD_RADIUS
    ):
        raise CandidateFailure(HOLD_TOPOLOGY, "Newton exact type/radius drifted")
    return {
        "curvature_on_input": _interval_summary(step.curvature_on_input),
        "derivative_at_midpoint": _interval_summary(step.derivative_at_midpoint),
        "inclusion_in_interior": step.inclusion_in_interior,
        "index": step.index,
        "input_lower": _fraction_text(step.input_lower),
        "input_upper": _fraction_text(step.input_upper),
        "midpoint": _fraction_text(step.midpoint),
        "newton_image": _interval_summary(step.newton_image),
        "output_lower": _fraction_text(step.output_lower),
        "output_upper": _fraction_text(step.output_upper),
        "valid_forward_span": _fraction_text(
            step.input_upper - step.input_lower
        ),
    }


def _root_summary(root: legacy.RootIntervalCertificate) -> dict[str, Any]:
    if (
        type(root) is not legacy.RootIntervalCertificate
        or type(root.role) is not str
        or type(root.kind) is not str
        or type(root.required_curvature_sign) is not int
        or type(root.inclusion_observed) is not bool
        or type(root.newton_steps) is not tuple
        or len(root.newton_steps) != 12
        or root.inclusion_observed is not True
        or root.final_upper - root.final_lower > Fraction(1, 20)
        or not any(step.inclusion_in_interior for step in root.newton_steps)
    ):
        raise CandidateFailure(HOLD_TOPOLOGY, "root/Newton semantics drifted")
    return {
        "band_lower": _fraction_text(root.band_lower),
        "band_upper": _fraction_text(root.band_upper),
        "final_lower": _fraction_text(root.final_lower),
        "final_upper": _fraction_text(root.final_upper),
        "final_width": _fraction_text(root.final_upper - root.final_lower),
        "inclusion_observed": root.inclusion_observed,
        "initial_cluster_lower": _fraction_text(root.initial_cluster_lower),
        "initial_cluster_upper": _fraction_text(root.initial_cluster_upper),
        "kind": root.kind,
        "newton_steps": [_newton_summary(step) for step in root.newton_steps],
        "required_curvature_sign": root.required_curvature_sign,
        "role": root.role,
    }


def _run_fixed_analytic_topology(
    role: str,
) -> tuple[dict[str, Any], set[Fraction]]:
    oracle = _FixedAnalyticTopologyOracle(role)
    if type(oracle) is not _FixedAnalyticTopologyOracle:
        raise CandidateFailure(HOLD_TOPOLOGY, "private adapter was subclassed")
    certificate = legacy.certify_physical_full_window_topology_v2(
        oracle,
        control_id=role,
    )
    if type(certificate) is not legacy.FullWindowTopologyCertificate:
        raise CandidateFailure(HOLD_TOPOLOGY, "legacy certificate type drifted")
    tiles, calls, unique_calls, maximum_depth = _EXPECTED_TOPOLOGY_LEDGERS[role]
    if (
        len(certificate.tiles) != tiles
        or len(oracle.calls) != calls
        or len(set(oracle.calls)) != unique_calls
        or max(tile.depth for tile in certificate.tiles) != maximum_depth
        or len(certificate.roots) != len(_ANALYTIC_ROOTS[role])
        or certificate.complete_window_covered is not True
        or certificate.unresolved_tiles != 0
    ):
        raise CandidateFailure(HOLD_TOPOLOGY, f"{role} frozen ledger drifted")
    expected_kinds = tuple(
        "maximum" if index % 2 == 0 else "minimum"
        for index in range(len(_ANALYTIC_ROOTS[role]))
    )
    if tuple(root.kind for root in certificate.roots) != expected_kinds:
        raise CandidateFailure(HOLD_TOPOLOGY, f"{role} curvature types drifted")
    unique_times = set(oracle.calls)
    return (
        {
            "analytic_definition": {
                "derivative_interval_padding": "1/1000000000",
                "f_coefficients_low_to_high": [
                    _fraction_text(value) for value in oracle.f_coefficients
                ],
                "f_prime_definition": "minus_product_of_t_minus_root",
                "roots": [_fraction_text(value) for value in oracle.roots],
                "taylor_absolute_sum_forward_radius": "1/4",
            },
            "control_path_evaluated": False,
            "legacy_science_free_fields_used_as_authority": False,
            "maximum_depth": maximum_depth,
            "oracle_call_count": calls,
            "root_count": len(certificate.roots),
            "roots": [_root_summary(root) for root in certificate.roots],
            "role": role,
            "tile_count": tiles,
            "tiles": [_tile_summary(tile) for tile in certificate.tiles],
            "unique_call_count": unique_calls,
            "unique_query_times": [
                _fraction_text(value) for value in sorted(unique_times)
            ],
            "valid_forward_radius": "1/4",
            "window": ["1/2", "35/1"],
        },
        unique_times,
    )


def _analytic_topology_summary() -> dict[str, Any]:
    fixtures: list[dict[str, Any]] = []
    union: set[Fraction] = set()
    for role in _CONTROL_ORDER:
        fixture, unique_times = _run_fixed_analytic_topology(role)
        fixtures.append(fixture)
        union.update(unique_times)
    if len(union) != 211:
        raise CandidateFailure(HOLD_TOPOLOGY, "analytic query-time union drifted")
    return {
        "fixed_role_order": list(_CONTROL_ORDER),
        "fixtures": fixtures,
        "legacy_oracle_publicly_injectable": False,
        "private_adapter_exact_type_required": True,
        "union_unique_call_count": 211,
        "union_unique_query_times": [
            _fraction_text(value) for value in sorted(union)
        ],
        "valid_forward_radius": "1/4",
    }


def _resource_contract_summary() -> dict[str, Any]:
    return {
        "expected_maximum_power": 27018,
        "expected_poisson_mode": 25600,
        "expected_right_index": 27014,
        "mandatory_tail_times": ["35/1", "50/1", "75/1", "100/1"],
        "maximum_distinct_query_count": 515,
        "maximum_peak_footprint_bytes": 8_589_934_592,
        "maximum_poisson_terms": 200_000,
        "maximum_process_swaps": 0,
        "maximum_rss_bytes": 4_294_967_296,
        "maximum_state_radius_upper": "1/100000000",
        "maximum_time_query_count": 512,
        "maximum_wall_seconds": 3600,
        "mpfr_precision_bits": 192,
        "poisson_tail_tolerance": "1/1000000000000000000",
        "reduction_block_size": 65_536,
        "series_horizon": "100/1",
        "shape": [207, 215, 161],
        "state_count": 7_165_305,
        "uniformization_rate": "256/1",
    }


def _build_semantic_candidate() -> dict[str, Any]:
    _validate_source_bindings()
    contract_path, contract_sha = _source_pin("completion_contract_json")
    selector_path, selector_sha = _source_pin("exact_selector")
    configuration_path, configuration_sha = _source_pin(
        "control_free_configurations"
    )
    contract = _strict_json_source(contract_path, contract_sha)
    selector = _strict_json_source(selector_path, selector_sha)
    configuration = _strict_json_source(configuration_path, configuration_sha)
    if (
        contract.get("status") != "FROZEN_PRE_F0_NO_SCIENTIFIC_EXECUTION"
        or contract.get("authorized_scientific_command") is not None
        or contract.get("current_state", {}).get("f0_independently_accepted")
        is not False
        or contract.get("current_state", {}).get("f1_authorized") is not False
    ):
        raise CandidateFailure(HOLD_CLAIM, "completion contract was promoted")
    return {
        "analytic_topology_fixtures": _analytic_topology_summary(),
        "claim_flags": {
            "authorizes_scientific_execution": False,
            "f0_accepted": False,
            "f0_pass": False,
            "f1_authorized": False,
            "independent_audit_complete": False,
            "measured_resource_evidence": False,
            "positive_budget_primary_controls_evaluated": False,
            "production_resource_gate": False,
            "scientific_execution": False,
        },
        "configuration_constructors": _configuration_summary(configuration),
        "integrated_compiled_fixture": _integrated_compiled_topology_summary(),
        "integrated_compiled_fixture_status": INTEGRATED_STATUS,
        "operator_fixtures": _operator_fixture_summary(),
        "resource_contract_declared_not_executed": _resource_contract_summary(),
        "schema": SCHEMA,
        "selector_boundary": _selector_boundary_summary(contract, selector),
        "source_bindings": _pinned_source_summary(),
        "stage": STAGE,
        "status": STATUS,
    }


@lru_cache(maxsize=1)
def canonical_semantic_candidate_bytes() -> bytes:
    """Return deterministic canonical bytes for this method candidate."""

    return _canonical_json_bytes(_build_semantic_candidate())


def build_semantic_candidate() -> dict[str, Any]:
    """Build the fixed semantic candidate with no caller numerical input."""

    return _strict_json_load_bytes(canonical_semantic_candidate_bytes())


def validate_semantic_candidate(payload: dict[str, Any]) -> None:
    """Reject every byte-relevant mutation against a fresh source binding."""

    _validate_source_bindings()
    if type(payload) is not dict:
        raise CandidateFailure(HOLD_JSON, "candidate must be an exact built-in dict")
    actual = _canonical_json_bytes(payload)
    expected = canonical_semantic_candidate_bytes()
    if actual != expected:
        raise CandidateFailure(HOLD_CLAIM, "candidate differs from frozen semantic bytes")


def parse_and_validate_semantic_candidate_bytes(payload: bytes) -> dict[str, Any]:
    """Strictly parse canonical ASCII JSON and replay the fixed candidate."""

    parsed = _strict_json_load_bytes(payload)
    if _canonical_json_bytes(parsed) != payload:
        raise CandidateFailure(HOLD_JSON, "candidate JSON is not canonical")
    validate_semantic_candidate(parsed)
    return parsed


def _write_output(path_text: str, payload: bytes) -> None:
    if type(path_text) is not str or not path_text:
        raise CandidateFailure(HOLD_JSON, "output path is invalid")
    if path_text == "-":
        sys.stdout.buffer.write(payload + b"\n")
        return
    output = Path(path_text).expanduser()
    if not output.is_absolute() or not output.parent.is_dir():
        raise CandidateFailure(
            HOLD_JSON,
            "output must be an absolute path in an existing directory",
        )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(output, flags, 0o600)
    except OSError as error:
        raise CandidateFailure(
            HOLD_JSON,
            "output could not be reserved exclusively",
        ) from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise CandidateFailure(HOLD_JSON, "output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    except BaseException:
        os.close(descriptor)
        output.unlink(missing_ok=True)
        raise
    os.close(descriptor)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI with output-path plumbing only; no scientific option exists."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="-",
        help="canonical candidate JSON path, or '-' for stdout",
    )
    arguments = parser.parse_args(argv)
    payload = canonical_semantic_candidate_bytes()
    parse_and_validate_semantic_candidate_bytes(payload)
    _write_output(arguments.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
