"""Implementation-independent semantic replay for the frozen F0 candidate.

This module deliberately imports no F0 producer or numerical implementation.
It independently checks canonical bytes and immutable source pins, rebuilds
the selector/configuration cross product, proves the exact polynomial
topologies, evaluates the closed two-state generator with two Decimal
precisions, reconstructs the complete topology schedule, and classifies the
separate measured-resource receipt.

The receipt emitted here is not an F0 acceptance authority.  In particular,
method replay success cannot override a missing or failed resource gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Final, NoReturn, Sequence


class ReplayFailure(RuntimeError):
    """Fail-closed independent replay error with a stable category."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


HOLD_JSON: Final = "HOLD_F0_INDEPENDENT_CANONICAL_JSON"
HOLD_SOURCE: Final = "HOLD_F0_INDEPENDENT_SOURCE_BINDING"
HOLD_SELECTOR: Final = "HOLD_F0_INDEPENDENT_SELECTOR_CONFIGURATION"
HOLD_ANALYTIC: Final = "HOLD_F0_INDEPENDENT_ANALYTIC_TOPOLOGY"
HOLD_HETEROGENEOUS: Final = "HOLD_F0_INDEPENDENT_HETEROGENEOUS_REPLAY"
HOLD_SCHEDULE: Final = "HOLD_F0_INDEPENDENT_TOPOLOGY_SCHEDULE"
HOLD_RESOURCE: Final = "HOLD_F0_INDEPENDENT_RESOURCE_RECEIPT"
HOLD_PROMOTION: Final = "HOLD_F0_INDEPENDENT_FALSE_PROMOTION"

SCHEMA: Final = "rate_defined_tensor_f0_semantic_independent_receipt_v1"
_SOURCE_PATH: Final = Path(__file__).resolve(strict=True)
_REPORT_DIR: Final = _SOURCE_PATH.parent.parent
_ARTIFACT_DIR: Final = _REPORT_DIR / "artifacts" / "data"

_CANDIDATE_A: Final = (
    _ARTIFACT_DIR / "rate_defined_tensor_f0_candidate_v1_replica_a.json"
)
_CANDIDATE_B: Final = (
    _ARTIFACT_DIR / "rate_defined_tensor_f0_candidate_v1_replica_b.json"
)
_SCHEDULE: Final = (
    _ARTIFACT_DIR / "rate_defined_tensor_f0_topology_schedule_v1.json"
)
_RESOURCE: Final = _ARTIFACT_DIR / "rate_defined_tensor_f0_resource_v1.json"
_RESOURCE_RECEIPT: Final = Path(f"{_RESOURCE}.resources.json")

_CANDIDATE_SHA256: Final = (
    "f3c294fbc6323845b530b986197ee43d3f0b3fb8a690aa9f5bb71e4f343889dd"
)
_SCHEDULE_SHA256: Final = (
    "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344"
)

_LIVE_CANDIDATE_SOURCES: Final = {
    "semantic_candidate": (
        "code/rate_defined_tensor_f0_candidate_v1.py",
        "acf32cc3babd269d4dec26081ab2e5f5b616a537c7d2989a38c47b72f1d64aba",
    ),
    "semantic_candidate_test": (
        "code/test_rate_defined_tensor_f0_candidate_v1.py",
        "f4259eb7cc00d262894ff61554621c14acff18c41106eb713d07bd59629116da",
    ),
}

_PINNED_SOURCES: Final = {
    "candidate_freeze": (
        "notes/rate_defined_tensor_f0_candidate_v1_freeze.md",
        "0f282f7227220c4a0dc6ae13996ee650759d0cf6679a6d360897929386796d9b",
    ),
    "completion_contract_human": (
        "notes/manuscript_completion_contract_v1.md",
        "cf60bad1680d487e610811c60e5d9e37fa27a87b935f94adcf83a5b8b6ec716d",
    ),
    "completion_contract_json": (
        "artifacts/data/manuscript_completion_contract_v1.json",
        "f32fee61edb48fad4e0da0ad5e747db8c417fd25c3acb18da74354c60ec68ee0",
    ),
    "completion_contract_independent_audit": (
        "audits/round_186_manuscript_completion_contract_independent_attack.md",
        "a14a7a1657dd467e7133c4ef2a57e76a829105ac65e62d3d763dcfa7e0c5231b",
    ),
    "exact_selector": (
        "scratch/modal_certificate_exact_selector_method_only_result.json",
        "77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98",
    ),
    "control_free_configurations": (
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    "fixed_36_row_design": (
        "notes/positive_b_fixed_control_robustness_design_v2.md",
        "264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd",
    ),
    "legacy_topology_engine": (
        "code/rate_defined_tensor_f0.py",
        "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5",
    ),
    "legacy_topology_test": (
        "code/test_rate_defined_tensor_f0.py",
        "f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d",
    ),
    "closed_operator_engine": (
        "code/rate_defined_tensor_f0_production_operator_v1.py",
        "dc46bbf39c72df547e7bd9f5364969b0b39293f84db19509353a712221bb5908",
    ),
    "closed_operator_test": (
        "code/test_rate_defined_tensor_f0_production_operator_v1.py",
        "b22c446aa747449a486818d5ce14af46a8a9bc3c6a55da84bababbd7f4ecfe1c",
    ),
    "batched_scalar_source": (
        "code/rate_defined_tensor_f0_batched_scalar_uniformization_v1.py",
        "56b783f073528146e6cdd3321f078a89978b5e5453b8fdfcabfe35412614b280",
    ),
    "batched_scalar_test": (
        "code/test_rate_defined_tensor_f0_batched_scalar_uniformization_v1.py",
        "ddddb839f3b50c1dc2ca05fbce2ddad1b5e025d08f549665585b7a866159dac1",
    ),
    "compiled_power_c_source": (
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.c",
        "9db8c672a04732b23dedb332854c4f4259911cfac32ec130d1d16b64db274917",
    ),
    "compiled_power_python_source": (
        "code/rate_defined_tensor_f0_compiled_power_stream_v1.py",
        "13c7fabd4118c3858b03d839dcfea037eb15eb6b64b08f7fb69f0757342eae55",
    ),
    "compiled_power_test": (
        "code/test_rate_defined_tensor_f0_compiled_power_stream_v1.py",
        "513c0ce06b4424c4a8c3cf6cfea3bb21cd588fc389af8a9e760e451fb9b6dd51",
    ),
    "compiled_batch_source": (
        "code/rate_defined_tensor_f0_compiled_batch_v1.py",
        "798d605d5cfc79319a633a5f9e487b4da34a55638b534f35804b3636cb402aa7",
    ),
    "compiled_batch_test": (
        "code/test_rate_defined_tensor_f0_compiled_batch_v1.py",
        "c1a378aa9851335391d3dfd016be8cf7943abfc388754eb9fb5d59c49d941e4e",
    ),
}

_SCHEDULE_SOURCES: Final = {
    "topology_schedule_source": (
        "code/rate_defined_tensor_f0_topology_schedule_v1.py",
        "f188cbbf7c9e6c31e90ab01c21c9effd334e4ab449102c5501271f83723d2ca7",
    ),
    "topology_schedule_test": (
        "code/test_rate_defined_tensor_f0_topology_schedule_v1.py",
        "0deed13b23eec298047e290513232094c4ba3ca18db1c8177c6e7e0d7607fcaf",
    ),
    "topology_schedule_artifact": (
        "artifacts/data/rate_defined_tensor_f0_topology_schedule_v1.json",
        _SCHEDULE_SHA256,
    ),
}

_CONTROL_ORDER: Final = ("lp_m1", "lp_m2", "lp_m3")
_SELECTOR_KEYS: Final = ("m1", "m2", "m3")
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
_ANALYTIC_COUNTS: Final = {
    "lp_m1": (146, 350, 147, 4),
    "lp_m2": (162, 498, 168, 4),
    "lp_m3": (178, 646, 188, 4),
}
_DERIVATIVE_PADDING: Final = Fraction(1, 1_000_000_000)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    try:
        return _sha256(path.read_bytes())
    except OSError as error:
        raise ReplayFailure(HOLD_SOURCE, f"unavailable source: {path}") from error


def _fail_float(value: str) -> NoReturn:
    raise ReplayFailure(HOLD_JSON, f"raw JSON float forbidden: {value}")


def _fail_constant(value: str) -> NoReturn:
    raise ReplayFailure(HOLD_JSON, f"nonfinite JSON constant forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise ReplayFailure(HOLD_JSON, "duplicate or non-string JSON key")
        result[key] = value
    return result


def _validate_tree(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_tree(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ReplayFailure(HOLD_JSON, f"{path} has non-string key")
            _validate_tree(item, f"{path}.{key}")
        return
    raise ReplayFailure(HOLD_JSON, f"{path} contains {type(value).__name__}")


def strict_json_bytes(
    payload: bytes,
    *,
    canonical: bool,
    allow_one_terminal_newline: bool = False,
) -> dict[str, Any]:
    """Parse exact ASCII JSON, rejecting duplicate keys and raw floats."""

    if type(payload) is not bytes:
        raise ReplayFailure(HOLD_JSON, "payload must be exact bytes")
    raw = payload
    if allow_one_terminal_newline and raw.endswith(b"\n"):
        raw = raw[:-1]
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise ReplayFailure(HOLD_JSON, "JSON must be ASCII") from error
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_float=_fail_float,
            parse_constant=_fail_constant,
        )
    except ReplayFailure:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ReplayFailure(HOLD_JSON, "malformed JSON") from error
    if type(parsed) is not dict:
        raise ReplayFailure(HOLD_JSON, "top-level JSON must be an object")
    _validate_tree(parsed)
    if canonical and canonical_bytes(parsed) != raw:
        raise ReplayFailure(HOLD_JSON, "JSON is not canonical")
    return parsed


def canonical_bytes(value: Any) -> bytes:
    _validate_tree(value)
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _require(condition: bool, code: str, message: str) -> None:
    if condition is not True:
        raise ReplayFailure(code, message)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: Any, code: str, label: str) -> Fraction:
    _require(type(value) is str and value.count("/") == 1, code, f"{label} rational")
    try:
        result = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ReplayFailure(code, f"{label} malformed rational") from error
    _require(_fraction_text(result) == value, code, f"{label} noncanonical rational")
    return result


def _fraction_row(value: Any, code: str, label: str) -> Fraction:
    _require(
        type(value) is dict
        and type(value.get("numerator")) is int
        and type(value.get("denominator")) is int,
        code,
        f"{label} fraction row",
    )
    result = Fraction(value["numerator"], value["denominator"])
    _require(
        result.numerator == value["numerator"]
        and result.denominator == value["denominator"],
        code,
        f"{label} fraction row is not reduced",
    )
    return result


def _hex_interval(value: Any, code: str, label: str) -> tuple[Fraction, Fraction]:
    _require(
        type(value) is dict
        and type(value.get("lower_binary64_hex")) is str
        and type(value.get("upper_binary64_hex")) is str,
        code,
        f"{label} interval structure",
    )
    try:
        lower_float = float.fromhex(value["lower_binary64_hex"])
        upper_float = float.fromhex(value["upper_binary64_hex"])
    except (TypeError, ValueError) as error:
        raise ReplayFailure(code, f"{label} invalid binary64") from error
    _require(
        math.isfinite(lower_float)
        and math.isfinite(upper_float)
        and lower_float.hex() == value["lower_binary64_hex"]
        and upper_float.hex() == value["upper_binary64_hex"]
        and lower_float <= upper_float,
        code,
        f"{label} noncanonical binary64 interval",
    )
    return Fraction.from_float(lower_float), Fraction.from_float(upper_float)


def _read_pinned_json(label: str) -> dict[str, Any]:
    relative, expected = _PINNED_SOURCES[label]
    path = _REPORT_DIR / relative
    payload = path.read_bytes()
    _require(_sha256(payload) == expected, HOLD_SOURCE, f"{relative} drifted")
    return strict_json_bytes(payload, canonical=False)


def _validate_source_bindings(candidate: dict[str, Any]) -> dict[str, Any]:
    embedded = candidate.get("source_bindings")
    _require(type(embedded) is dict, HOLD_SOURCE, "source bindings missing")
    live = embedded.get("live_candidate_sources")
    expected_live = [
        {"label": label, "path": path, "sha256": digest}
        for label, (path, digest) in _LIVE_CANDIDATE_SOURCES.items()
    ]
    _require(live == expected_live, HOLD_SOURCE, "live candidate source pins drifted")
    pinned = embedded.get("pinned_sources")
    expected_pinned = [
        {"label": label, "path": path, "sha256": digest}
        for label, (path, digest) in _PINNED_SOURCES.items()
    ]
    _require(pinned == expected_pinned, HOLD_SOURCE, "embedded source pins drifted")
    for _label, (relative, digest) in {
        **_LIVE_CANDIDATE_SOURCES,
        **_PINNED_SOURCES,
        **_SCHEDULE_SOURCES,
    }.items():
        _require(
            _sha256_path(_REPORT_DIR / relative) == digest,
            HOLD_SOURCE,
            f"external exact-byte audit failed: {relative}",
        )
    return {
        "external_exact_byte_audit_complete": True,
        "live_candidate_source_count": len(_LIVE_CANDIDATE_SOURCES),
        "pinned_source_count": len(_PINNED_SOURCES),
        "schedule_source_count": len(_SCHEDULE_SOURCES),
    }


def _selector_configuration_replay(candidate: dict[str, Any]) -> dict[str, Any]:
    contract = _read_pinned_json("completion_contract_json")
    selector = _read_pinned_json("exact_selector")
    configuration = _read_pinned_json("control_free_configurations")
    _require(
        contract.get("status") == "FROZEN_PRE_F0_NO_SCIENTIFIC_EXECUTION"
        and contract.get("current_state", {}).get("f0_independently_accepted")
        is False
        and contract.get("current_state", {}).get("f1_authorized") is False,
        HOLD_PROMOTION,
        "completion contract was promoted",
    )

    controls: list[dict[str, Any]] = []
    candidate_controls = candidate.get("selector_boundary", {}).get("controls")
    _require(
        type(candidate_controls) is list and len(candidate_controls) == 3,
        HOLD_SELECTOR,
        "candidate control rows missing",
    )
    exact_controls = contract.get("exact_controls")
    results = selector.get("selector_results")
    _require(
        type(exact_controls) is dict
        and type(results) is dict
        and tuple(results) == _SELECTOR_KEYS,
        HOLD_SELECTOR,
        "selector sources malformed",
    )
    for index, (selector_key, role) in enumerate(
        zip(_SELECTOR_KEYS, _CONTROL_ORDER, strict=True)
    ):
        weights = results[selector_key].get("selected", {}).get("weights")
        _require(
            type(weights) is list and len(weights) == 4,
            HOLD_SELECTOR,
            f"{selector_key} selected weights missing",
        )
        parsed: list[Fraction] = []
        for row in weights:
            _require(
                type(row) is dict
                and type(row.get("numerator")) is str
                and type(row.get("denominator")) is str
                and row["numerator"].lstrip("-").isdigit()
                and row["denominator"].isdigit(),
                HOLD_SELECTOR,
                f"{selector_key} selected integer strings malformed",
            )
            value = Fraction(int(row["numerator"]), int(row["denominator"]))
            _require(
                _fraction_text(value) == row.get("exact"),
                HOLD_SELECTOR,
                f"{selector_key} exact selected weight disagrees",
            )
            parsed.append(value)
        texts = [_fraction_text(value) for value in parsed]
        _require(
            sum(parsed, Fraction(0)) == 1
            and exact_controls.get(role) == texts
            and candidate_controls[index].get("control_role") == role
            and candidate_controls[index].get("weights") == texts
            and candidate_controls[index].get("unit_sum_exact") == "1/1"
            and candidate_controls[index].get("production_evaluation") is False,
            HOLD_SELECTOR,
            f"{role} source/candidate mismatch",
        )
        controls.append({"control_role": role, "weights": texts})

    _require(
        configuration.get("contains_budget_value") is False
        and configuration.get("contains_control_values") is False
        and configuration.get("configuration_count") == 12
        and configuration.get("configuration_order") == list(_CONFIGURATION_ORDER)
        and configuration.get("coordinate_order") == list(_COORDINATE_ORDER),
        HOLD_SELECTOR,
        "control-free configuration header drifted",
    )
    source_rows = configuration.get("configurations")
    candidate_rows = candidate.get("configuration_constructors", {}).get("rows")
    _require(
        type(source_rows) is list
        and type(candidate_rows) is list
        and len(source_rows) == len(candidate_rows) == 12,
        HOLD_SELECTOR,
        "configuration rows missing",
    )
    constructions = {
        "cell_centred_reflecting": (
            "cell_centred_reflecting_scharfetter_gummel",
            False,
            False,
        ),
        "vertex_centred_reflecting_dual": (
            "vertex_centred_reflecting_scharfetter_gummel",
            False,
            True,
        ),
        "cell_centred_periodic_base": (
            "cell_centred_periodic_diffusion",
            True,
            False,
        ),
        "cell_centred_periodic_half_shift": (
            "cell_centred_periodic_diffusion_half_shift",
            True,
            False,
        ),
    }
    total_states = 0
    configuration_states: list[tuple[str, int]] = []
    for source_row, candidate_row, label in zip(
        source_rows, candidate_rows, _CONFIGURATION_ORDER, strict=True
    ):
        _require(
            type(source_row) is dict
            and type(candidate_row) is dict
            and source_row.get("label") == candidate_row.get("label") == label
            and source_row.get("shape") == candidate_row.get("shape")
            and math.prod(source_row["shape"]) == source_row.get("expected_states")
            == candidate_row.get("state_count"),
            HOLD_SELECTOR,
            f"{label} shape/state mismatch",
        )
        for coordinate, axis in zip(
            _COORDINATE_ORDER, candidate_row.get("axes", []), strict=True
        ):
            source_axis = source_row.get(coordinate)
            _require(
                type(source_axis) is dict and type(axis) is dict,
                HOLD_SELECTOR,
                f"{label}/{coordinate} axis missing",
            )
            alignment = source_axis.get("alignment")
            expected = constructions.get(alignment)
            _require(
                expected is not None
                and axis.get("coordinate") == coordinate
                and axis.get("alignment") == alignment
                and axis.get("construction") == expected[0]
                and axis.get("periodic") is expected[1]
                and axis.get("has_half_boundary_volumes") is expected[2]
                and axis.get("size") == source_axis.get("size"),
                HOLD_SELECTOR,
                f"{label}/{coordinate} construction mismatch",
            )
        total_states += source_row["expected_states"]
        configuration_states.append((label, source_row["expected_states"]))
    # The preregistered row order is control-major: all 12 frozen
    # configurations for lp_m1, followed by lp_m2, then lp_m3.
    cross_product = [
        {
            "configuration": label,
            "control_role": role,
            "state_count": state_count,
        }
        for role in _CONTROL_ORDER
        for label, state_count in configuration_states
    ]
    _require(
        total_states == 34_787_462
        and candidate.get("configuration_constructors", {}).get(
            "total_state_workload"
        )
        == total_states
        and len(cross_product) == 36,
        HOLD_SELECTOR,
        "configuration workload or 36-row design drifted",
    )
    return {
        "configuration_count": 12,
        "control_count": 3,
        "fixed_36_row_cross_product_sha256": _sha256(canonical_bytes(cross_product)),
        "fixed_36_row_order": cross_product,
        "selector_controls": controls,
        "total_state_workload_per_control": total_states,
    }


def _poly_multiply(
    left: tuple[Fraction, ...], right: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return tuple(result)


def _poly_derivative(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(Fraction(i) * values[i] for i in range(1, len(values))) or (
        Fraction(0),
    )


def _poly_evaluate(values: tuple[Fraction, ...], x: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(values):
        result = result * x + coefficient
    return result


def _analytic_replay(candidate: dict[str, Any]) -> tuple[dict[str, Any], list[Fraction]]:
    top = candidate.get("analytic_topology_fixtures")
    fixtures = top.get("fixtures") if type(top) is dict else None
    _require(
        type(fixtures) is list
        and len(fixtures) == 3
        and top.get("fixed_role_order") == list(_CONTROL_ORDER),
        HOLD_ANALYTIC,
        "analytic fixture family malformed",
    )
    union: set[Fraction] = set()
    summaries: list[dict[str, Any]] = []
    for fixture, role in zip(fixtures, _CONTROL_ORDER, strict=True):
        roots = _ANALYTIC_ROOTS[role]
        derivative = (Fraction(-1),)
        for root in roots:
            derivative = _poly_multiply(derivative, (-root, Fraction(1)))
        coefficients = (Fraction(0),) + tuple(
            derivative[index] / Fraction(index + 1)
            for index in range(len(derivative))
        )
        definition = fixture.get("analytic_definition")
        _require(
            type(definition) is dict
            and fixture.get("role") == role
            and definition.get("roots") == [_fraction_text(root) for root in roots]
            and definition.get("f_coefficients_low_to_high")
            == [_fraction_text(value) for value in coefficients]
            and definition.get("derivative_interval_padding")
            == "1/1000000000",
            HOLD_ANALYTIC,
            f"{role} exact polynomial definition drifted",
        )
        tiles = fixture.get("tiles")
        expected_tiles, expected_calls, expected_unique, expected_depth = (
            _ANALYTIC_COUNTS[role]
        )
        _require(
            type(tiles) is list
            and len(tiles) == expected_tiles
            and fixture.get("tile_count") == expected_tiles
            and fixture.get("oracle_call_count") == expected_calls
            and fixture.get("unique_call_count") == expected_unique
            and fixture.get("maximum_depth") == expected_depth,
            HOLD_ANALYTIC,
            f"{role} ledger count drifted",
        )
        previous = Fraction(1, 2)
        candidate_cluster: list[tuple[Fraction, Fraction]] = []
        second = _poly_derivative(derivative)
        for index, tile in enumerate(tiles):
            lower = _fraction(tile.get("lower"), HOLD_ANALYTIC, "tile lower")
            upper = _fraction(tile.get("upper"), HOLD_ANALYTIC, "tile upper")
            _require(
                lower == previous
                and lower < upper
                and upper - lower <= Fraction(1, 4)
                and tile.get("valid_forward_span") == _fraction_text(upper - lower),
                HOLD_ANALYTIC,
                f"{role} tile {index} breaks exact coverage",
            )
            previous = upper
            derivative_interval = _hex_interval(
                tile.get("derivative"), HOLD_ANALYTIC, "tile derivative"
            )
            curvature_interval = _hex_interval(
                tile.get("curvature"), HOLD_ANALYTIC, "tile curvature"
            )
            derivative_values = (
                _poly_evaluate(derivative, lower),
                _poly_evaluate(derivative, upper),
            )
            curvature_values = (
                _poly_evaluate(second, lower),
                _poly_evaluate(second, upper),
            )
            _require(
                derivative_interval[0]
                <= min(derivative_values) - _DERIVATIVE_PADDING
                and derivative_interval[1]
                >= max(derivative_values) + _DERIVATIVE_PADDING
                and curvature_interval[0] <= min(curvature_values)
                and curvature_interval[1] >= max(curvature_values),
                HOLD_ANALYTIC,
                f"{role} tile {index} misses exact endpoint values",
            )
            enclosed_roots = [root for root in roots if lower <= root <= upper]
            if tile.get("candidate") is True:
                _require(
                    bool(enclosed_roots),
                    HOLD_ANALYTIC,
                    f"{role} spurious candidate tile",
                )
                candidate_cluster.append((lower, upper))
            else:
                _require(
                    not enclosed_roots,
                    HOLD_ANALYTIC,
                    f"{role} noncandidate tile contains an exact root",
                )
                midpoint_sign = 1 if _poly_evaluate(
                    derivative, (lower + upper) / 2
                ) > 0 else -1
                _require(
                    tile.get("derivative_sign") == midpoint_sign,
                    HOLD_ANALYTIC,
                    f"{role} tile derivative sign disagrees",
                )
        _require(previous == Fraction(35), HOLD_ANALYTIC, f"{role} window incomplete")
        _require(
            len(candidate_cluster) == 2 * len(roots),
            HOLD_ANALYTIC,
            f"{role} root candidate clustering drifted",
        )
        root_rows = fixture.get("roots")
        _require(
            type(root_rows) is list and len(root_rows) == len(roots),
            HOLD_ANALYTIC,
            f"{role} root rows missing",
        )
        for index, (root_row, exact_root) in enumerate(
            zip(root_rows, roots, strict=True)
        ):
            final_lower = _fraction(
                root_row.get("final_lower"), HOLD_ANALYTIC, "root lower"
            )
            final_upper = _fraction(
                root_row.get("final_upper"), HOLD_ANALYTIC, "root upper"
            )
            expected_kind = "maximum" if index % 2 == 0 else "minimum"
            expected_curvature = -1 if expected_kind == "maximum" else 1
            steps = root_row.get("newton_steps")
            _require(
                final_lower <= exact_root <= final_upper
                and final_upper - final_lower <= Fraction(1, 20)
                and root_row.get("kind") == expected_kind
                and root_row.get("required_curvature_sign") == expected_curvature
                and root_row.get("inclusion_observed") is True
                and type(steps) is list
                and len(steps) == 12
                and any(step.get("inclusion_in_interior") is True for step in steps),
                HOLD_ANALYTIC,
                f"{role} exact root/Newton certificate drifted",
            )
            for step_index, step in enumerate(steps):
                input_lower = _fraction(
                    step.get("input_lower"), HOLD_ANALYTIC, "Newton input lower"
                )
                input_upper = _fraction(
                    step.get("input_upper"), HOLD_ANALYTIC, "Newton input upper"
                )
                output_lower = _fraction(
                    step.get("output_lower"), HOLD_ANALYTIC, "Newton output lower"
                )
                output_upper = _fraction(
                    step.get("output_upper"), HOLD_ANALYTIC, "Newton output upper"
                )
                _require(
                    step.get("index") == step_index
                    and input_lower <= exact_root <= input_upper
                    and output_lower <= exact_root <= output_upper,
                    HOLD_ANALYTIC,
                    f"{role} Newton step loses exact root",
                )
        query_times = [
            _fraction(value, HOLD_ANALYTIC, "analytic query time")
            for value in fixture.get("unique_query_times", [])
        ]
        _require(
            len(query_times) == expected_unique
            and query_times == sorted(set(query_times)),
            HOLD_ANALYTIC,
            f"{role} unique query set drifted",
        )
        union.update(query_times)
        summaries.append(
            {
                "exact_root_count": len(roots),
                "full_window_exact_factorization_proved": True,
                "role": role,
                "tile_count": expected_tiles,
            }
        )
    _require(
        len(union) == 211
        and top.get("union_unique_call_count") == 211
        and top.get("union_unique_query_times")
        == [_fraction_text(value) for value in sorted(union)],
        HOLD_ANALYTIC,
        "analytic union query set drifted",
    )
    return (
        {
            "exact_factorization_topology_complete": True,
            "fixture_summaries": summaries,
            "union_unique_query_count": len(union),
        },
        sorted(union),
    )


def _decimal_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _two_state_parameters(
    precision: int,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    with localcontext() as context:
        context.prec = precision
        root = Decimal(33).sqrt()
        lambda_plus = (-Decimal(11) + root) / Decimal(16)
        lambda_minus = (-Decimal(11) - root) / Decimal(16)
        j0 = Decimal(1) / Decimal(8)
        j1 = Decimal(11) / Decimal(64)
        c_plus = (j1 - lambda_minus * j0) / (lambda_plus - lambda_minus)
        c_minus = (lambda_plus * j0 - j1) / (lambda_plus - lambda_minus)
        return +lambda_plus, +lambda_minus, +c_plus, +c_minus


def _two_state_jets(time: Fraction, precision: int) -> tuple[Decimal, ...]:
    with localcontext() as context:
        context.prec = precision
        lp, lm, cp, cm = _two_state_parameters(precision)
        decimal_time = _decimal_fraction(time)
        return tuple(
            +(cp * (lp**order) * (lp * decimal_time).exp())
            + (cm * (lm**order) * (lm * decimal_time).exp())
            for order in range(4)
        )


def _two_state_root(precision: int) -> Decimal:
    with localcontext() as context:
        context.prec = precision
        lp, lm, cp, cm = _two_state_parameters(precision)
        return +((-(cm * lm) / (cp * lp)).ln() / (lp - lm))


def _decimal_enclosure(
    low_precision: Decimal, high_precision: Decimal
) -> tuple[Fraction, Fraction]:
    epsilon = Decimal("1e-70")
    lower = min(low_precision, high_precision) - epsilon
    upper = max(low_precision, high_precision) + epsilon
    return Fraction(lower), Fraction(upper)


def _heterogeneous_replay(
    candidate: dict[str, Any],
) -> tuple[dict[str, Any], list[Fraction]]:
    fixture = candidate.get("operator_fixtures", {}).get(
        "fixed_heterogeneous_two_state"
    )
    _require(
        type(fixture) is dict
        and fixture.get("dense_generator_exact")
        == [["-5/8", "1/2"], ["1/4", "-3/4"]]
        and fixture.get("initial_state_exact") == ["1/1", "0/1"]
        and fixture.get("killing_exact") == ["1/8", "1/2"]
        and fixture.get("stationary_masses_exact") == ["1/1", "2/1"],
        HOLD_HETEROGENEOUS,
        "closed two-state exact generator drifted",
    )
    integrated = candidate.get("integrated_compiled_fixture")
    evidence = (
        integrated.get("compiled_batch_evidence")
        if type(integrated) is dict
        else None
    )
    _require(
        type(evidence) is dict
        and integrated.get("compiled_batch_evidence_sha256")
        == _sha256(canonical_bytes(evidence))
        and integrated.get("status")
        == "PASS_FIXED_HETEROGENEOUS_COMPILED_TOPOLOGY_METHOD",
        HOLD_HETEROGENEOUS,
        "nested compiled evidence binding drifted",
    )
    metadata = evidence.get("metadata")
    _require(
        type(metadata) is dict
        and _fraction_row(
            metadata.get("uniformization_rate"),
            HOLD_HETEROGENEOUS,
            "uniformization rate",
        )
        == Fraction(3, 4)
        and _fraction_row(
            metadata.get("maximum_killing_upper"),
            HOLD_HETEROGENEOUS,
            "maximum killing",
        )
        == Fraction(1, 2)
        and metadata.get("mpfr_precision_bits") == 192
        and metadata.get("maximum_poisson_terms") == 200_000,
        HOLD_HETEROGENEOUS,
        "compiled method metadata drifted",
    )
    evaluations = evidence.get("evaluations")
    _require(
        type(evaluations) is list and len(evaluations) == 26,
        HOLD_HETEROGENEOUS,
        "heterogeneous evaluations missing",
    )
    times: list[Fraction] = []
    maximum_dual_precision_delta = Decimal(0)
    for row_index, row in enumerate(evaluations):
        _require(
            type(row) is dict
            and row.get("absolute_time_from_initial") is True
            and row.get("state_chaining_used") is False,
            HOLD_HETEROGENEOUS,
            f"evaluation {row_index} time semantics drifted",
        )
        time = Fraction(row.get("time_numerator"), row.get("time_denominator"))
        times.append(time)
        jets = row.get("jets")
        _require(
            type(jets) is list
            and [jet.get("order") for jet in jets] == [0, 1, 2, 3],
            HOLD_HETEROGENEOUS,
            f"evaluation {row_index} jet order drifted",
        )
        replay_96 = _two_state_jets(time, 96)
        replay_160 = _two_state_jets(time, 160)
        for order, jet in enumerate(jets):
            try:
                lower_float = float.fromhex(jet.get("lower_hex"))
                upper_float = float.fromhex(jet.get("upper_hex"))
            except (TypeError, ValueError) as error:
                raise ReplayFailure(
                    HOLD_HETEROGENEOUS,
                    f"evaluation {row_index} invalid jet binary64",
                ) from error
            _require(
                math.isfinite(lower_float)
                and math.isfinite(upper_float)
                and lower_float.hex() == jet.get("lower_hex")
                and upper_float.hex() == jet.get("upper_hex")
                and lower_float <= upper_float,
                HOLD_HETEROGENEOUS,
                f"evaluation {row_index} noncanonical jet interval",
            )
            replay_lower, replay_upper = _decimal_enclosure(
                replay_96[order], replay_160[order]
            )
            _require(
                Fraction.from_float(lower_float) <= replay_lower
                and Fraction.from_float(upper_float) >= replay_upper,
                HOLD_HETEROGENEOUS,
                f"evaluation {row_index} J{order} misses independent replay",
            )
            maximum_dual_precision_delta = max(
                maximum_dual_precision_delta,
                abs(replay_96[order] - replay_160[order]),
            )
    _require(
        times == sorted(set(times))
        and integrated.get("unique_query_times")
        == [_fraction_text(value) for value in times],
        HOLD_HETEROGENEOUS,
        "heterogeneous query times drifted",
    )

    root_96 = _two_state_root(96)
    root_160 = _two_state_root(160)
    root_lower, root_upper = _decimal_enclosure(root_96, root_160)
    root_row = integrated.get("root")
    final_lower = _fraction(
        root_row.get("final_lower"), HOLD_HETEROGENEOUS, "root lower"
    )
    final_upper = _fraction(
        root_row.get("final_upper"), HOLD_HETEROGENEOUS, "root upper"
    )
    _require(
        final_lower <= root_lower <= root_upper <= final_upper
        and root_row.get("kind") == "maximum"
        and root_row.get("required_curvature_sign") == -1,
        HOLD_HETEROGENEOUS,
        "two-state analytic root is outside certified maximum",
    )
    root_time = Fraction(root_160)
    root_jets = _two_state_jets(root_time, 160)
    _require(
        root_jets[2] < 0,
        HOLD_HETEROGENEOUS,
        "two-state stationary point is not a maximum",
    )
    tiles = integrated.get("tiles")
    _require(
        type(tiles) is list
        and len(tiles) == 20
        and integrated.get("oracle_call_count") == 104
        and integrated.get("unique_call_count") == 26
        and integrated.get("maximum_depth") == 4,
        HOLD_HETEROGENEOUS,
        "two-state topology ledger drifted",
    )
    previous = Fraction(1, 2)
    candidate_tiles: list[tuple[Fraction, Fraction]] = []
    for tile_index, tile in enumerate(tiles):
        lower = _fraction(tile.get("lower"), HOLD_HETEROGENEOUS, "tile lower")
        upper = _fraction(tile.get("upper"), HOLD_HETEROGENEOUS, "tile upper")
        _require(
            lower == previous and lower < upper and upper - lower <= Fraction(1, 4),
            HOLD_HETEROGENEOUS,
            f"two-state tile {tile_index} breaks coverage",
        )
        previous = upper
        if tile.get("candidate") is True:
            candidate_tiles.append((lower, upper))
        else:
            _require(
                not (lower <= root_upper and root_lower <= upper),
                HOLD_HETEROGENEOUS,
                f"noncandidate tile {tile_index} intersects replayed root",
            )
            expected_sign = 1 if upper < root_lower else -1
            _require(
                tile.get("derivative_sign") == expected_sign,
                HOLD_HETEROGENEOUS,
                f"two-state tile {tile_index} sign disagrees",
            )
    _require(
        previous == Fraction(2)
        and candidate_tiles
        == [
            (Fraction(71, 64), Fraction(9, 8)),
            (Fraction(9, 8), Fraction(73, 64)),
        ]
        and candidate_tiles[0][0] <= root_lower
        and root_upper <= candidate_tiles[-1][1],
        HOLD_HETEROGENEOUS,
        "two-state candidate root cluster drifted",
    )
    return (
        {
            "dense_generator_exact_rebuilt": True,
            "dual_decimal_precisions": [96, 160],
            "evaluation_count": 26,
            "j0_j3_independent_enclosures_all_contained": True,
            "maximum_dual_precision_delta_decimal": str(
                maximum_dual_precision_delta
            ),
            "root_decimal_160": str(root_160),
            "topology_unique_maximum_replayed": True,
        },
        times,
    )


def _query_rows(values: Sequence[Fraction]) -> list[dict[str, int]]:
    return [
        {"denominator": value.denominator, "numerator": value.numerator}
        for value in values
    ]


def _parse_query_rows(value: Any, label: str) -> list[Fraction]:
    _require(type(value) is list, HOLD_SCHEDULE, f"{label} query list missing")
    result = [
        _fraction_row(row, HOLD_SCHEDULE, f"{label}[{index}]")
        for index, row in enumerate(value)
    ]
    _require(result == sorted(set(result)), HOLD_SCHEDULE, f"{label} not sorted unique")
    return result


def _schedule_replay(
    schedule: dict[str, Any],
    analytic_times: list[Fraction],
    heterogeneous_times: list[Fraction],
) -> dict[str, Any]:
    _require(
        schedule.get("schema") == "rate_defined_tensor_f0_topology_schedule_v1"
        and schedule.get("status") == "PASS_F0_TOPOLOGY_SCHEDULE_FROZEN_NOT_F0",
        HOLD_SCHEDULE,
        "schedule header drifted",
    )
    query_sets = schedule.get("query_sets")
    _require(type(query_sets) is dict, HOLD_SCHEDULE, "schedule query sets missing")
    schedule_analytic = _parse_query_rows(query_sets.get("analytic"), "analytic")
    schedule_heterogeneous = _parse_query_rows(
        query_sets.get("heterogeneous"), "heterogeneous"
    )
    required = sorted(set(analytic_times) | set(heterogeneous_times))
    schedule_required = _parse_query_rows(query_sets.get("required_union"), "required")
    _require(
        schedule_analytic == analytic_times
        and schedule_heterogeneous == heterogeneous_times
        and schedule_required == required
        and len(required) == 231
        and Fraction(35) not in required,
        HOLD_SCHEDULE,
        "required topology query union disagrees with independent replay",
    )
    hashes = schedule.get("hashes")
    _require(type(hashes) is dict, HOLD_SCHEDULE, "schedule hashes missing")
    for label, values, expected_key in (
        ("analytic", analytic_times, "analytic_times_sha256"),
        ("heterogeneous", heterogeneous_times, "heterogeneous_times_sha256"),
        ("required", required, "required_union_sha256"),
    ):
        _require(
            hashes.get(expected_key) == _sha256(canonical_bytes(_query_rows(values))),
            HOLD_SCHEDULE,
            f"{label} query hash drifted",
        )

    padding_expected: set[Fraction] = set()
    denominator = 4
    required_set = set(required)
    while len(padding_expected) < 281:
        for numerator in range(denominator // 2, 35 * denominator + 1):
            value = Fraction(numerator, denominator)
            if value not in required_set and value not in padding_expected:
                padding_expected.add(value)
                if len(padding_expected) == 281:
                    break
        denominator *= 2
    padding = _parse_query_rows(schedule.get("padding_times"), "padding")
    topology = _parse_query_rows(schedule.get("topology_times"), "topology")
    expected_topology = sorted(required_set | padding_expected)
    _require(
        padding == sorted(padding_expected)
        and topology == expected_topology
        and len(topology) == 512
        and Fraction(35) in topology
        and hashes.get("padding_times_sha256")
        == _sha256(canonical_bytes(_query_rows(padding)))
        and hashes.get("topology_times_sha256")
        == _sha256(canonical_bytes(_query_rows(topology))),
        HOLD_SCHEDULE,
        "deterministic dyadic padding/topology schedule drifted",
    )
    tails = _parse_query_rows(schedule.get("mandatory_tail_times"), "tail")
    _require(
        tails
        == [Fraction(35), Fraction(50), Fraction(75), Fraction(100)]
        and len(set(topology) | set(tails)) == 515,
        HOLD_SCHEDULE,
        "mandatory tail union drifted",
    )
    _require(
        all(value is False for value in schedule.get("promotion_flags", {}).values()),
        HOLD_PROMOTION,
        "schedule contains a promoted authority flag",
    )
    return {
        "analytic_count": 211,
        "heterogeneous_count": 26,
        "padding_recipe_independently_rebuilt": True,
        "required_union_count": 231,
        "tail_union_count": 515,
        "topology_count": 512,
        "topology_times_sha256": hashes["topology_times_sha256"],
    }


def _all_false_flags(value: Any, code: str, label: str) -> None:
    _require(
        type(value) is dict
        and value
        and all(type(flag) is bool and flag is False for flag in value.values()),
        code,
        f"{label} promotion flags are not all false",
    )


def _resource_replay(
    resource_payload: bytes | None,
    receipt_payload: bytes | None,
    schedule: dict[str, Any],
) -> dict[str, Any]:
    if resource_payload is None or receipt_payload is None:
        return {
            "failure_reasons": ["formal_resource_receipt_missing"],
            "formal_resource_receipt_present": False,
            "resource_gate_pass": False,
            "status": "AWAITING_FORMAL_RESOURCE_RECEIPT",
        }
    resource = strict_json_bytes(resource_payload, canonical=True)
    receipt = strict_json_bytes(
        receipt_payload,
        # The external observation sidecar is intentionally pretty-printed.
        # Its raw bytes are hash-bound below; duplicate keys, raw floats, and
        # non-ASCII still fail closed before semantic canonicalization.
        canonical=False,
        allow_one_terminal_newline=True,
    )
    resource_sha = _sha256(resource_payload)
    canonical_artifact = receipt.get("canonical_artifact")
    _require(
        type(canonical_artifact) is dict
        and canonical_artifact.get("sha256") == resource_sha
        and canonical_artifact.get("byte_count") == len(resource_payload)
        and resource.get("schema") == "rate_defined_tensor_f0_resource_canonical_v1",
        HOLD_RESOURCE,
        "resource artifact/receipt binding drifted",
    )
    expected_fixture = {
        "shape": [207, 215, 161],
        "state_count": 7_165_305,
        "series_horizon": {"denominator": 1, "numerator": 100},
        "uniformization_rate": {"denominator": 1, "numerator": 256},
        "maximum_rss_bytes": 4_294_967_296,
        "maximum_peak_footprint_bytes": 8_589_934_592,
        "maximum_process_swap_delta": 0,
        "maximum_wall_seconds": {"denominator": 1, "numerator": 3600},
    }
    fixture = receipt.get("fixture")
    resource_fixture = resource.get("fixture")
    _require(
        type(fixture) is dict
        and fixture == resource_fixture
        and all(fixture.get(key) == value for key, value in expected_fixture.items()),
        HOLD_RESOURCE,
        "formal largest-shape fixture drifted",
    )
    _all_false_flags(resource.get("promotion_flags"), HOLD_PROMOTION, "resource")
    _all_false_flags(receipt.get("promotion_flags"), HOLD_PROMOTION, "receipt")
    dependencies = receipt.get("dependencies_after")
    _require(
        type(dependencies) is dict
        and dependencies == receipt.get("dependencies_before")
        and dependencies == resource.get("dependencies"),
        HOLD_RESOURCE,
        "resource dependency snapshots disagree",
    )
    for label, (relative, digest) in {
        "candidate_freeze": _PINNED_SOURCES["candidate_freeze"],
        "batched_scalar_source": _PINNED_SOURCES["batched_scalar_source"],
        "batched_scalar_test": _PINNED_SOURCES["batched_scalar_test"],
        "compiled_power_c_source": _PINNED_SOURCES["compiled_power_c_source"],
        "compiled_power_python_source": _PINNED_SOURCES[
            "compiled_power_python_source"
        ],
        "compiled_power_test": _PINNED_SOURCES["compiled_power_test"],
        "compiled_batch_source": _PINNED_SOURCES["compiled_batch_source"],
        "compiled_batch_test": _PINNED_SOURCES["compiled_batch_test"],
        **_SCHEDULE_SOURCES,
    }.items():
        row = dependencies.get(label)
        _require(
            type(row) is dict
            and row.get("accepted") is True
            and row.get("expected_sha256") == digest
            and row.get("observed_sha256") == digest
            and _sha256_path(_REPORT_DIR / relative) == digest,
            HOLD_RESOURCE,
            f"resource dependency {label} drifted",
        )
    schedule_row = receipt.get("schedule")
    _require(
        type(schedule_row) is dict
        and schedule_row == resource.get("schedule")
        and schedule_row.get("artifact_sha256") == _SCHEDULE_SHA256
        and schedule_row.get("topology_times") == schedule.get("topology_times")
        and schedule_row.get("topology_time_count") == 512
        and schedule_row.get("combined_union_count") == 515,
        HOLD_RESOURCE,
        "resource schedule binding drifted",
    )
    counts = receipt.get("method_counts")
    _require(
        counts
        == {
            "canonical_scalar_record_count": 27019,
            "compiled_power_stream_run_count": 1,
            "mandatory_tail_evaluation_count": 4,
            "maximum_power_index": 27018,
            "p_action_call_count": 27018,
            "repeated_p_actions_during_reevaluation": 0,
            "topology_evaluation_count": 512,
        },
        HOLD_RESOURCE,
        "formal method counts drifted",
    )
    measurement = receipt.get("measurement")
    _require(type(measurement) is dict, HOLD_RESOURCE, "measurement missing")
    expected_failures: list[str] = []
    if measurement.get("peak_rss_bytes", 0) > fixture["maximum_rss_bytes"]:
        expected_failures.append("rss_cap_exceeded")
    if (
        measurement.get("host_peak_footprint_bytes", 0)
        > fixture["maximum_peak_footprint_bytes"]
    ):
        expected_failures.append("peak_footprint_cap_exceeded")
    if (
        measurement.get("process_swap_count_after", 0)
        - measurement.get("process_swap_count_before", 0)
        > fixture["maximum_process_swap_delta"]
    ):
        expected_failures.append("process_swap_cap_exceeded")
    try:
        wall_seconds = float.fromhex(measurement.get("wall_seconds_hex"))
    except (TypeError, ValueError) as error:
        raise ReplayFailure(HOLD_RESOURCE, "wall time is not binary64 hex") from error
    if wall_seconds > 3600:
        expected_failures.append("wall_time_cap_exceeded")
    _require(
        receipt.get("failure_reasons") == expected_failures
        and receipt.get("resource_caps_satisfied") is (not expected_failures),
        HOLD_RESOURCE,
        "resource PASS/HOLD classification is inconsistent",
    )
    runner_digest = _sha256_path(
        _REPORT_DIR / "code" / "run_rate_defined_tensor_f0_resource_v1.py"
    )
    _require(
        receipt.get("runner_source_sha256_same_process_observation")
        == runner_digest
        and receipt.get(
            "runner_source_sha256_same_process_observation_authoritative"
        )
        is False,
        HOLD_RESOURCE,
        "resource runner changed after its same-process observation",
    )
    resource_pass = not expected_failures
    return {
        "canonical_resource_artifact_sha256": resource_sha,
        "failure_reasons": expected_failures,
        "formal_resource_receipt_present": True,
        "formal_resource_receipt_sha256": _sha256(receipt_payload),
        "formal_resource_semantic_canonical_sha256": _sha256(
            canonical_bytes(receipt)
        ),
        "host_peak_footprint_bytes": measurement[
            "host_peak_footprint_bytes"
        ],
        "peak_rss_bytes": measurement["peak_rss_bytes"],
        "resource_gate_pass": resource_pass,
        "runner_source_sha256_external_replay": runner_digest,
        "status": (
            "PASS_FORMAL_RESOURCE_RECEIPT"
            if resource_pass
            else "HOLD_FORMAL_RESOURCE_CAPS_EXCEEDED"
        ),
        "wall_seconds_hex": measurement["wall_seconds_hex"],
    }


def independent_replay(
    candidate_a_payload: bytes,
    candidate_b_payload: bytes,
    schedule_payload: bytes,
    resource_payload: bytes | None,
    resource_receipt_payload: bytes | None,
) -> dict[str, Any]:
    """Replay all method semantics and classify, but never accept, F0."""

    _require(
        type(candidate_a_payload) is bytes
        and type(candidate_b_payload) is bytes
        and candidate_a_payload == candidate_b_payload
        and _sha256(candidate_a_payload) == _CANDIDATE_SHA256,
        HOLD_SOURCE,
        "candidate replicas are not byte-identical frozen artifacts",
    )
    _require(
        type(schedule_payload) is bytes
        and _sha256(schedule_payload) == _SCHEDULE_SHA256,
        HOLD_SCHEDULE,
        "topology schedule artifact hash drifted",
    )
    candidate = strict_json_bytes(candidate_a_payload, canonical=True)
    schedule = strict_json_bytes(schedule_payload, canonical=True)
    _require(
        candidate.get("schema")
        == "rate_defined_tensor_f0_candidate_v1_method_complete"
        and candidate.get("status")
        == "PASS_F0_METHOD_CANDIDATE_AWAITING_RESOURCE_AND_INDEPENDENT_AUDIT",
        HOLD_PROMOTION,
        "candidate header drifted or was promoted",
    )
    claim_flags = candidate.get("claim_flags")
    _all_false_flags(claim_flags, HOLD_PROMOTION, "candidate")
    source = _validate_source_bindings(candidate)
    selector_configuration = _selector_configuration_replay(candidate)
    analytic, analytic_times = _analytic_replay(candidate)
    heterogeneous, heterogeneous_times = _heterogeneous_replay(candidate)
    schedule_summary = _schedule_replay(
        schedule, analytic_times, heterogeneous_times
    )
    resource_summary = _resource_replay(
        resource_payload, resource_receipt_payload, schedule
    )
    resource_pass = resource_summary["resource_gate_pass"] is True
    status = (
        "PASS_F0_SEMANTIC_REPLAY_AWAITING_AGGREGATION"
        if resource_pass
        else (
            "PASS_F0_SEMANTIC_REPLAY_AWAITING_RESOURCE"
            if resource_summary["formal_resource_receipt_present"] is False
            else "PASS_F0_SEMANTIC_REPLAY_RESOURCE_HOLD_NOT_F0"
        )
    )
    return {
        "analytic_topology_replay": analytic,
        "authority_flags": {
            "authorizes_f1": False,
            "authorizes_scientific_execution": False,
            "f0_accepted": False,
            "f0_pass": False,
            "independent_aggregation_complete": False,
            "production_resource_gate": False,
            "science_executed": False,
        },
        "candidate_binding": {
            "replica_a_sha256": _sha256(candidate_a_payload),
            "replica_b_sha256": _sha256(candidate_b_payload),
            "replicas_byte_identical": True,
        },
        "heterogeneous_two_state_replay": heterogeneous,
        "method_semantic_replay_pass": True,
        "resource_replay": resource_summary,
        "schema": SCHEMA,
        "selector_configuration_replay": selector_configuration,
        "source_replay": source,
        "status": status,
        "terminal_branch_recommendation": (
            None if resource_pass else "HOLD_F0_METHOD_OR_RESOURCE"
        ),
        "topology_schedule_replay": schedule_summary,
    }


def replay_current_artifacts() -> dict[str, Any]:
    """Replay fixed report artifacts; a missing resource receipt stays closed."""

    resource_payload = _RESOURCE.read_bytes() if _RESOURCE.is_file() else None
    receipt_payload = (
        _RESOURCE_RECEIPT.read_bytes() if _RESOURCE_RECEIPT.is_file() else None
    )
    return independent_replay(
        _CANDIDATE_A.read_bytes(),
        _CANDIDATE_B.read_bytes(),
        _SCHEDULE.read_bytes(),
        resource_payload,
        receipt_payload,
    )


def _write_exclusive(path_text: str, payload: bytes) -> None:
    output = Path(path_text).expanduser()
    _require(output.is_absolute() and output.parent.is_dir(), HOLD_JSON, "output path")
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
        raise ReplayFailure(HOLD_JSON, "output reservation failed") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            _require(written > 0, HOLD_JSON, "output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    except BaseException:
        os.close(descriptor)
        output.unlink(missing_ok=True)
        raise
    os.close(descriptor)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    receipt = replay_current_artifacts()
    payload = canonical_bytes(receipt)
    strict_json_bytes(payload, canonical=True)
    _write_exclusive(arguments.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
