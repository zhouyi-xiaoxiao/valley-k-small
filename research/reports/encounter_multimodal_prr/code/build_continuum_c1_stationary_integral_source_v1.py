"""Build factorized physical stationary-cell integrals for the frozen 12 rows.

This source is intentionally narrower than the continuum bridge.  It reads the
frozen exact partitions, independently reconstructs their geometry from the
configuration authority, and evaluates the globally normalized Gaussian cell
integrals with directed MPFR rounding.  It never reads the production
``stationary_mass`` arrays, which are representative quadrature primitives
rather than physical cell integrals.

The output remains a fixed-row source artifact.  It does not prove a genuine
refinement sequence, C1/C2 convergence, a concrete killing operator, or release
eligibility.
"""

# ruff: noqa: E402

from __future__ import annotations

import sys

_AUTHENTICATED_CONTEXT_KEYS = {
    "authority_sha256",
    "gmpy2_module",
    "launcher_sha256",
    "runtime_attestation",
    "schema",
    "target_key",
    "target_source_path",
    "target_source_sha256",
}
_authenticated_context = globals().get("_CONTINUUM_C1_AUTHENTICATED_EXECUTION_CONTEXT")
if (
    type(_authenticated_context) is not dict
    or set(_authenticated_context) != _AUTHENTICATED_CONTEXT_KEYS
    or _authenticated_context.get("schema")
    != "encounter_continuum_c1_authenticated_target_context_v1"
    or _authenticated_context.get("target_key") != "stationary_builder"
    or _authenticated_context.get("target_source_path")
    != "code/build_continuum_c1_stationary_integral_source_v1.py"
):
    raise RuntimeError("authenticated MPFR launcher context required before imports")
for _digest_key in (
    "authority_sha256",
    "launcher_sha256",
    "target_source_sha256",
):
    _digest = _authenticated_context[_digest_key]
    if (
        type(_digest) is not str
        or len(_digest) != 64
        or any(character not in "0123456789abcdef" for character in _digest)
    ):
        raise RuntimeError("authenticated MPFR launcher digest context drift")
_authenticated_gmpy2 = sys.modules.get("gmpy2")
if (
    _authenticated_gmpy2 is None
    or _authenticated_context["gmpy2_module"] is not _authenticated_gmpy2
    or getattr(_authenticated_gmpy2, "__t0_wrapper_execution__", None)
    != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
):
    raise RuntimeError("authenticated gmpy2 module identity required before imports")
_runtime_attestation = _authenticated_context["runtime_attestation"]
if (
    type(_runtime_attestation) is not dict
    or set(_runtime_attestation)
    != {
        "entry",
        "implementation_filename",
        "implementation_sha256",
        "runtime",
        "trust_contract",
    }
    or type(_runtime_attestation["runtime"]) is not dict
    or _runtime_attestation["runtime"].get("gmpy2") != "2.2.1"
    or _runtime_attestation["runtime"].get("mpfr") != "MPFR 4.2.1"
    or _runtime_attestation["runtime"].get("python_wrapper_execution")
    != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
):
    raise RuntimeError("authenticated gmpy2 runtime attestation drift")
gmpy2 = _authenticated_gmpy2

import argparse
import hashlib
import json
import math
import os
import tempfile
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

REPORT: Final = Path(__file__).resolve().parents[1]
SCHEMA: Final = "encounter_continuum_c1_stationary_integral_source_v1"
STATUS: Final = (
    "PASS_FIXED_12_ROW_FACTORIZED_PHYSICAL_STATIONARY_INTEGRALS_"
    "SAME_MPFR_BACKEND_SENTINEL_ONLY_NO_REFINEMENT_NO_COMPLETE_C1_C2"
)
PRIMARY_BITS: Final = 320
SENTINEL_BITS: Final = 640
COORDINATES: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)

REFERENCE_PATH: Final = Path("artifacts/data/continuum_c1_reference_density_source_v1.json")
REFERENCE_SHA256: Final = "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575"
FORMULA_PATH: Final = Path("artifacts/data/continuum_c1_ideal_formula_source_v1.json")
FORMULA_SHA256: Final = "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be"
MEMBER_PATH: Final = Path("artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json")
MEMBER_SHA256: Final = "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef"
METHOD_PATH: Final = Path(
    "artifacts/data/continuum_c1_c2_fixed_row_outward_method_registry_v1.json"
)
METHOD_SHA256: Final = "ac00450edf826029b157a98ad2835592630c07b2a75334c25d8d1232a4fe69c3"
CONFIGURATION_PATH: Final = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
RAW_BINDING_PATH: Final = Path("artifacts/data/continuum_c1_raw_axis_production_binding_v1.json")
RAW_BINDING_SHA256: Final = "7028fecf4538abb1df56f03d8cea01d0ed208a43356cb9b1e24c67fb54d47480"
BUNDLE_PATH: Final = Path("artifacts/data/physical_production_initial_stream_v1/bundle.json")
BUNDLE_ROOT: Final = BUNDLE_PATH.parent
BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
DEFAULT_OUTPUT: Final = Path("artifacts/data/continuum_c1_stationary_integral_source_v1.json")


class StationaryIntegralFailure(RuntimeError):
    """Fail-closed error for the fixed-row stationary-integral source."""


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise StationaryIntegralFailure("interval endpoints must be exact Fractions")
        if self.lower > self.upper:
            raise StationaryIntegralFailure("reversed exact interval")

    def add(self, other: "ExactInterval") -> "ExactInterval":
        return ExactInterval(self.lower + other.lower, self.upper + other.upper)

    def multiply_nonnegative(self, other: "ExactInterval") -> "ExactInterval":
        if self.lower < 0 or other.lower < 0:
            raise StationaryIntegralFailure("nonnegative interval multiplication required")
        return ExactInterval(self.lower * other.lower, self.upper * other.upper)

    def intersect(self, other: "ExactInterval") -> "ExactInterval":
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise StationaryIntegralFailure("independent interval witnesses are disjoint")
        return ExactInterval(lower, upper)

    def contains(self, other: "ExactInterval") -> bool:
        return self.lower <= other.lower and other.upper <= self.upper


@dataclass(frozen=True, slots=True)
class MPInterval:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    precision: int

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not gmpy2.mpfr
            or type(self.upper) is not gmpy2.mpfr
            or self.precision not in {PRIMARY_BITS, SENTINEL_BITS}
            or not gmpy2.is_finite(self.lower)
            or not gmpy2.is_finite(self.upper)
            or self.lower > self.upper
        ):
            raise StationaryIntegralFailure("invalid MPFR interval")

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_fraction(self.lower), _mpfr_fraction(self.upper))


def _duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise StationaryIntegralFailure("duplicate or invalid JSON key")
        result[key] = value
    return result


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise StationaryIntegralFailure("JSON depth cap exceeded")
    if isinstance(value, float):
        raise StationaryIntegralFailure("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise StationaryIntegralFailure("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise StationaryIntegralFailure("invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise StationaryIntegralFailure(f"forbidden JSON value type: {type(value).__name__}")


def _pretty(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path, cap: int = 8_000_000) -> str:
    data = path.read_bytes()
    if len(data) > cap:
        raise StationaryIntegralFailure(f"oversized input: {path}")
    return _sha256_bytes(data)


def _safe_relative(value: object) -> Path:
    if type(value) is not str:
        raise StationaryIntegralFailure("report-relative path must be a string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or "." in pure.parts:
        raise StationaryIntegralFailure("unsafe report-relative path")
    return Path(*pure.parts)


def _json_source(path: Path, expected_sha256: str, cap: int = 8_000_000) -> dict[str, Any]:
    absolute = REPORT / path
    data = absolute.read_bytes()
    if len(data) > cap or _sha256_bytes(data) != expected_sha256:
        raise StationaryIntegralFailure(f"source hash or size drift: {path}")
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                StationaryIntegralFailure(f"JSON float forbidden: {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                StationaryIntegralFailure(f"JSON constant forbidden: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StationaryIntegralFailure(f"invalid strict JSON: {path}") from error
    _strict_tree(value)
    if type(value) is not dict or _pretty(value) != data:
        raise StationaryIntegralFailure(f"noncanonical JSON object: {path}")
    return value


def _q(value: object) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise StationaryIntegralFailure("canonical p/q string required")
    numerator_text, denominator_text = value.split("/")
    try:
        result = Fraction(int(numerator_text), int(denominator_text))
    except (ValueError, ZeroDivisionError) as error:
        raise StationaryIntegralFailure("invalid p/q string") from error
    if result.denominator <= 0 or _qs(result) != value:
        raise StationaryIntegralFailure("noncanonical p/q string")
    return result


def _qs(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _hex_q(value: object) -> Fraction:
    if type(value) is not str:
        raise StationaryIntegralFailure("binary64 hex string required")
    try:
        number = float.fromhex(value)
    except ValueError as error:
        raise StationaryIntegralFailure("invalid binary64 hex string") from error
    if (
        not math.isfinite(number)
        or number.hex() != value
        or (number == 0.0 and math.copysign(1.0, number) < 0)
    ):
        raise StationaryIntegralFailure("noncanonical finite binary64 hex string")
    return Fraction.from_float(number)


def _interval_json(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _qs(value.lower),
        "upper_exact_p_over_q": _qs(value.upper),
    }


def _context(precision: int, rounding: int) -> gmpy2.context:
    return gmpy2.context(
        precision=precision,
        round=rounding,
        emax=1_073_741_823,
        emin=-1_073_741_823,
        subnormalize=False,
        trap_underflow=False,
        trap_overflow=False,
        trap_inexact=False,
        trap_invalid=False,
        trap_erange=False,
        trap_divzero=False,
        allow_complex=False,
        rational_division=False,
        allow_release_gil=False,
    )


def _mp_q(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(_context(precision, rounding)):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mpfr_fraction(value: gmpy2.mpfr) -> Fraction:
    exact = gmpy2.mpq(value)
    return Fraction(int(exact.numerator), int(exact.denominator))


def _mp_binary(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    precision: int,
    rounding: int,
    operation: str,
) -> gmpy2.mpfr:
    with gmpy2.context(_context(precision, rounding)):
        if operation == "add":
            return +(left + right)
        if operation == "sub":
            return +(left - right)
        if operation == "mul":
            return +(left * right)
    raise StationaryIntegralFailure("unknown MPFR binary operation")


def _mp_monotone(value: MPInterval, function: Any) -> MPInterval:
    with gmpy2.context(_context(value.precision, gmpy2.RoundDown)):
        lower = +function(value.lower)
    with gmpy2.context(_context(value.precision, gmpy2.RoundUp)):
        upper = +function(value.upper)
    return MPInterval(lower, upper, value.precision)


def _mp_from_q(value: Fraction, precision: int) -> MPInterval:
    return MPInterval(
        _mp_q(value, precision, gmpy2.RoundDown),
        _mp_q(value, precision, gmpy2.RoundUp),
        precision,
    )


def _mp_sub(left: MPInterval, right: MPInterval) -> MPInterval:
    if left.precision != right.precision:
        raise StationaryIntegralFailure("MPFR precision mismatch")
    precision = left.precision
    return MPInterval(
        _mp_binary(left.lower, right.upper, precision, gmpy2.RoundDown, "sub"),
        _mp_binary(left.upper, right.lower, precision, gmpy2.RoundUp, "sub"),
        precision,
    )


def _mp_mul(left: MPInterval, right: MPInterval) -> MPInterval:
    if left.precision != right.precision:
        raise StationaryIntegralFailure("MPFR precision mismatch")
    precision = left.precision
    pairs = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    lowers = [_mp_binary(a, b, precision, gmpy2.RoundDown, "mul") for a, b in pairs]
    uppers = [_mp_binary(a, b, precision, gmpy2.RoundUp, "mul") for a, b in pairs]
    return MPInterval(min(lowers), max(uppers), precision)


def _gaussian_segment(
    lower: Fraction,
    upper: Fraction,
    *,
    coefficient: Fraction,
    centre: Fraction,
    precision: int,
) -> ExactInterval:
    if lower >= upper or coefficient <= 0:
        raise StationaryIntegralFailure("invalid Gaussian segment")
    root = _mp_monotone(_mp_from_q(coefficient, precision), gmpy2.sqrt)
    lower_argument = _mp_mul(root, _mp_from_q(lower - centre, precision))
    upper_argument = _mp_mul(root, _mp_from_q(upper - centre, precision))
    lower_erf = _mp_monotone(lower_argument, gmpy2.erf)
    upper_erf = _mp_monotone(upper_argument, gmpy2.erf)
    difference = _mp_sub(upper_erf, lower_erf)
    mass = _mp_mul(difference, _mp_from_q(Fraction(1, 2), precision)).exact()
    if not (0 < mass.lower <= mass.upper < 1):
        raise StationaryIntegralFailure("Gaussian segment mass escaped (0,1)")
    return mass


def _sum_intervals(values: list[ExactInterval]) -> ExactInterval:
    result = ExactInterval(Fraction(0), Fraction(0))
    for value in values:
        result = result.add(value)
    return result


def _fraction_mod(value: Fraction, width: Fraction) -> Fraction:
    if width <= 0:
        raise StationaryIntegralFailure("positive modulus required")
    return value - (value // width) * width


def _reconstruct_partition(
    *,
    coordinate: str,
    configuration_axis: dict[str, Any],
    domain_start: Fraction,
    domain_width: Fraction,
) -> dict[str, Any]:
    size = configuration_axis.get("size")
    alignment = configuration_axis.get("alignment")
    if type(size) is not int or isinstance(size, bool) or size < 2 or type(alignment) is not str:
        raise StationaryIntegralFailure("invalid configuration axis")
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        lower = _hex_q(configuration_axis.get("lower_binary64_hex"))
        upper = _hex_q(configuration_axis.get("upper_binary64_hex"))
        if lower >= upper:
            raise StationaryIntegralFailure("invalid reflecting domain")
        domain_start = lower
        domain_width = upper - lower
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            step = domain_width / size
            positions = [lower + (Fraction(index) + Fraction(1, 2)) * step for index in range(size)]
            segments = [
                [(lower + index * step, lower + (index + 1) * step)] for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = domain_width / (size - 1)
            positions = [lower + index * step for index in range(size)]
            boundaries = (
                [lower]
                + [lower + (Fraction(index) - Fraction(1, 2)) * step for index in range(1, size)]
                + [upper]
            )
            segments = [[(boundaries[index], boundaries[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
        periodic = False
    elif alignment in {"cell_centred_periodic_base", "cell_centred_periodic_half_shift"}:
        step = domain_width / size
        shift = _q(configuration_axis.get("periodic_shift_exact"))
        expected_shift = Fraction(0) if alignment == "cell_centred_periodic_base" else step / 2
        if shift != expected_shift:
            raise StationaryIntegralFailure("periodic shift drift")
        positions = [
            domain_start
            + _fraction_mod((Fraction(index) + Fraction(1, 2)) * step + shift, domain_width)
            for index in range(size)
        ]
        domain_end = domain_start + domain_width
        segments = []
        for index in range(size):
            start = domain_start + _fraction_mod(index * step + shift, domain_width)
            end = start + step
            if end <= domain_end:
                segments.append([(start, end)])
            else:
                segments.append(
                    [(start, domain_end), (domain_start, domain_start + end - domain_end)]
                )
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment == "cell_centred_periodic_base"
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
    else:
        raise StationaryIntegralFailure("unknown axis alignment")
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in segments]
    return {
        "cell_segments_exact": [
            [[_qs(lower), _qs(upper)] for lower, upper in cell] for cell in segments
        ],
        "cell_volumes_exact": [_qs(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _qs(domain_start),
        "domain_width_exact": _qs(domain_width),
        "periodic": periodic,
        "periodic_shift_exact": _qs(shift),
        "positions_exact": [_qs(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def _domain_digest(domain: bytes, value: Any) -> str:
    if not domain.endswith(b"\0"):
        raise StationaryIntegralFailure("digest domain must be NUL terminated")
    return _sha256_bytes(domain + _pretty(value))


def _build() -> dict[str, Any]:
    if gmpy2.__version__ != "2.2.1" or gmpy2.mpfr_version() != "MPFR 4.2.1":
        raise StationaryIntegralFailure("unaccepted gmpy2/MPFR runtime")
    reference = _json_source(REFERENCE_PATH, REFERENCE_SHA256, 100_000)
    formula = _json_source(FORMULA_PATH, FORMULA_SHA256, 100_000)
    member = _json_source(MEMBER_PATH, MEMBER_SHA256, 100_000)
    method = _json_source(METHOD_PATH, METHOD_SHA256, 100_000)
    configuration = _json_source(CONFIGURATION_PATH, CONFIGURATION_SHA256, 1_000_000)
    raw_binding = _json_source(RAW_BINDING_PATH, RAW_BINDING_SHA256, 100_000)
    bundle = _json_source(BUNDLE_PATH, BUNDLE_SHA256, 2_000_000)

    if (
        reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1"
        or formula.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1"
        or member.get("schema") != "encounter_continuum_c1_c2_fixed_row_member_spec_v1"
        or method.get("schema") != "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1"
        or configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or raw_binding.get("schema") != "encounter_continuum_c1_raw_axis_production_binding_v1"
        or bundle.get("schema") != "encounter_control_free_production_initial_stream_v1"
    ):
        raise StationaryIntegralFailure("source schema drift")
    method_rows = method.get("methods")
    if type(method_rows) is not list:
        raise StationaryIntegralFailure("method registry rows missing")
    method_by_id = {
        row.get("method_id"): row
        for row in method_rows
        if type(row) is dict and type(row.get("method_id")) is str
    }
    if (
        method_by_id.get("directed_mpfr_320_reference_density_v1", {}).get("precision_bits")
        != PRIMARY_BITS
        or method_by_id.get("directed_mpfr_640_reference_density_sentinel_v1", {}).get(
            "precision_bits"
        )
        != SENTINEL_BITS
    ):
        raise StationaryIntegralFailure("stationary-integral method registration drift")

    parameters = reference.get("physical_parameter_bundle")
    if type(parameters) is not dict:
        raise StationaryIntegralFailure("physical parameter bundle missing")
    diffusion = _hex_q(parameters.get("particle_diffusion_binary64_hex"))
    stiffness = _hex_q(parameters.get("ou_stiffness_binary64_hex"))
    mean = _hex_q(parameters.get("ou_mean_binary64_hex"))
    period = _q(parameters.get("transverse_period_exact"))
    if diffusion <= 0 or stiffness <= 0 or period <= 0:
        raise StationaryIntegralFailure("nonpositive physical parameter")
    coefficients = {
        "midpoint": stiffness / diffusion,
        "relative_parallel": stiffness / (4 * diffusion),
    }

    config_rows = configuration.get("configurations")
    bundle_rows = bundle.get("rows")
    mappings = member.get("configuration_semantic_ids")
    expected_order = member.get("configuration_order")
    if (
        type(config_rows) is not list
        or type(bundle_rows) is not list
        or type(mappings) is not list
        or type(expected_order) is not list
        or len(config_rows) != len(bundle_rows) != 12
    ):
        raise StationaryIntegralFailure("12-row source cardinality drift")
    if len(config_rows) != 12 or len(bundle_rows) != 12 or len(mappings) != 12:
        raise StationaryIntegralFailure("12-row source cardinality drift")

    mapping_by_label: dict[str, dict[str, Any]] = {}
    for mapping in mappings:
        if type(mapping) is not dict or type(mapping.get("authority_label")) is not str:
            raise StationaryIntegralFailure("invalid semantic mapping")
        label = mapping["authority_label"]
        if label in mapping_by_label:
            raise StationaryIntegralFailure("duplicate semantic mapping")
        mapping_by_label[label] = mapping

    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        raise StationaryIntegralFailure("configuration dynamics missing")
    transverse_start = _q(dynamics.get("transverse_domain_start_exact"))
    transverse_width = _q(dynamics.get("transverse_period_exact"))
    if transverse_width != period:
        raise StationaryIntegralFailure("transverse period mismatch")

    parameter_digest = _domain_digest(
        b"encounter-fixed-row-physical-parameter-bundle-v1\0",
        {
            "physical_parameter_bundle": parameters,
            "unit_table": reference.get("unit_table"),
        },
    )
    role_bindings = member.get("role_bindings")
    if type(role_bindings) is not dict:
        raise StationaryIntegralFailure("member role bindings missing")

    output_rows: list[dict[str, Any]] = []
    gaussian_count = 0
    periodic_count = 0
    maximum_relative_width = Fraction(0)
    minimum_positive_lower: Fraction | None = None
    all_primary_contain_sentinel = True

    for index, (config_row, bundle_row) in enumerate(zip(config_rows, bundle_rows, strict=True)):
        if type(config_row) is not dict or type(bundle_row) is not dict:
            raise StationaryIntegralFailure("invalid row object")
        label = config_row.get("label")
        if (
            type(label) is not str
            or expected_order[index] != label
            or bundle_row.get("configuration_index") != index
            or bundle_row.get("configuration_label") != label
        ):
            raise StationaryIntegralFailure("row order or label drift")
        mapping = mapping_by_label.get(label)
        if mapping is None:
            raise StationaryIntegralFailure("semantic mapping missing")

        row_manifest_entry = bundle_row.get("row_manifest")
        if type(row_manifest_entry) is not dict:
            raise StationaryIntegralFailure("row manifest entry missing")
        row_relative = BUNDLE_ROOT / _safe_relative(row_manifest_entry.get("path"))
        expected_row_hash = row_manifest_entry.get("sha256")
        if type(expected_row_hash) is not str:
            raise StationaryIntegralFailure("row manifest hash missing")
        row_manifest = _json_source(row_relative, expected_row_hash, 200_000)
        axes = row_manifest.get("axes")
        if type(axes) is not list or len(axes) != 3:
            raise StationaryIntegralFailure("row axis manifest drift")

        partition_hashes: list[str] = []
        loaded_partitions: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for coordinate, axis_entry in zip(COORDINATES, axes, strict=True):
            if type(axis_entry) is not dict or axis_entry.get("coordinate") != coordinate:
                raise StationaryIntegralFailure("axis order drift")
            partition_entry = axis_entry.get("partition_file")
            if type(partition_entry) is not dict or type(partition_entry.get("sha256")) is not str:
                raise StationaryIntegralFailure("partition manifest entry drift")
            partition_relative = BUNDLE_ROOT / _safe_relative(partition_entry.get("path"))
            partition_hash = partition_entry["sha256"]
            partition = _json_source(partition_relative, partition_hash, 1_000_000)
            configuration_axis = config_row.get(coordinate)
            if type(configuration_axis) is not dict:
                raise StationaryIntegralFailure("configuration axis missing")
            expected_partition = _reconstruct_partition(
                coordinate=coordinate,
                configuration_axis=configuration_axis,
                domain_start=transverse_start,
                domain_width=transverse_width,
            )
            if partition != expected_partition:
                raise StationaryIntegralFailure(
                    f"partition reconstruction mismatch: {label}/{coordinate}"
                )
            partition_hashes.append(partition_hash)
            loaded_partitions.append((partition, partition_entry))

        member_digest = _domain_digest(
            b"encounter-fixed-row-correlated-member-v1\0",
            {
                "authority_label": label,
                "coordinate_order": list(COORDINATES),
                "factorization_source_sha256": role_bindings["factorization_source"]["sha256"],
                "ideal_formula_source_sha256": role_bindings["ideal_formula_source"]["sha256"],
                "normalization": "one_global_gauge_and_globally_normalized_pi_no_box_renormalization",
                "partition_sha256s": partition_hashes,
                "physical_parameter_digest": parameter_digest,
                "reference_density_source_sha256": role_bindings["reference_density_source"][
                    "sha256"
                ],
                "refinement_family_id": mapping.get("refinement_family_id"),
                "refinement_member_id": mapping.get("refinement_member_id"),
                "scalar_convention": member["member_semantics"]["scalar_convention"],
            },
        )

        axis_outputs: list[dict[str, Any]] = []
        axis_sums: list[ExactInterval] = []
        axis_directs: list[ExactInterval] = []
        for coordinate, (partition, partition_entry) in zip(
            COORDINATES, loaded_partitions, strict=True
        ):
            cell_intervals: list[ExactInterval] = []
            sentinel_cell_intervals: list[ExactInterval] = []
            for cell_segments in partition["cell_segments_exact"]:
                if type(cell_segments) is not list or not cell_segments:
                    raise StationaryIntegralFailure("empty partition cell")
                if coordinate == "relative_perpendicular":
                    cell_volume = sum(
                        (_q(segment[1]) - _q(segment[0]) for segment in cell_segments),
                        Fraction(0),
                    )
                    primary = ExactInterval(cell_volume / period, cell_volume / period)
                    sentinel = primary
                    periodic_count += 1
                else:
                    primary_parts: list[ExactInterval] = []
                    sentinel_parts: list[ExactInterval] = []
                    centre = mean if coordinate == "midpoint" else Fraction(0)
                    for segment in cell_segments:
                        if type(segment) is not list or len(segment) != 2:
                            raise StationaryIntegralFailure("invalid partition segment")
                        lower, upper = _q(segment[0]), _q(segment[1])
                        primary_parts.append(
                            _gaussian_segment(
                                lower,
                                upper,
                                coefficient=coefficients[coordinate],
                                centre=centre,
                                precision=PRIMARY_BITS,
                            )
                        )
                        sentinel_parts.append(
                            _gaussian_segment(
                                lower,
                                upper,
                                coefficient=coefficients[coordinate],
                                centre=centre,
                                precision=SENTINEL_BITS,
                            )
                        )
                    primary = _sum_intervals(primary_parts)
                    sentinel = _sum_intervals(sentinel_parts)
                    gaussian_count += 1
                if not primary.contains(sentinel):
                    all_primary_contain_sentinel = False
                    raise StationaryIntegralFailure("320-bit cell interval misses 640-bit sentinel")
                if primary.lower <= 0:
                    raise StationaryIntegralFailure(
                        "physical cell mass lower bound is not positive"
                    )
                relative_width = (primary.upper - primary.lower) / primary.lower
                maximum_relative_width = max(maximum_relative_width, relative_width)
                minimum_positive_lower = (
                    primary.lower
                    if minimum_positive_lower is None
                    else min(minimum_positive_lower, primary.lower)
                )
                cell_intervals.append(primary)
                sentinel_cell_intervals.append(sentinel)

            cell_sum = _sum_intervals(cell_intervals)
            sentinel_sum = _sum_intervals(sentinel_cell_intervals)
            domain_start = _q(partition["domain_start_exact"])
            domain_end = domain_start + _q(partition["domain_width_exact"])
            if coordinate == "relative_perpendicular":
                direct = ExactInterval(Fraction(1), Fraction(1))
                sentinel_direct = direct
            else:
                centre = mean if coordinate == "midpoint" else Fraction(0)
                direct = _gaussian_segment(
                    domain_start,
                    domain_end,
                    coefficient=coefficients[coordinate],
                    centre=centre,
                    precision=PRIMARY_BITS,
                )
                sentinel_direct = _gaussian_segment(
                    domain_start,
                    domain_end,
                    coefficient=coefficients[coordinate],
                    centre=centre,
                    precision=SENTINEL_BITS,
                )
            joint = cell_sum.intersect(direct)
            if not cell_sum.contains(sentinel_sum) or not direct.contains(sentinel_direct):
                raise StationaryIntegralFailure("320-bit axis interval misses 640-bit sentinel")
            axis_sums.append(cell_sum)
            axis_directs.append(direct)
            axis_outputs.append(
                {
                    "cell_count": partition["size"],
                    "cell_mass_intervals": [
                        {
                            "cell_index": cell_index,
                            **_interval_json(interval),
                        }
                        for cell_index, interval in enumerate(cell_intervals)
                    ],
                    "coordinate": coordinate,
                    "direct_domain_mass_interval": _interval_json(direct),
                    "formula_id": (
                        "periodic_cell_volume_divided_by_W_v1"
                        if coordinate == "relative_perpendicular"
                        else f"globally_normalized_gaussian_erf_{coordinate}_v1"
                    ),
                    "joint_domain_mass_interval": _interval_json(joint),
                    "partition_path": partition_entry["path"],
                    "partition_sha256": partition_entry["sha256"],
                    "sum_of_cells_mass_interval": _interval_json(cell_sum),
                }
            )

        factorized_box = ExactInterval(Fraction(1), Fraction(1))
        direct_box = ExactInterval(Fraction(1), Fraction(1))
        for axis_sum, axis_direct in zip(axis_sums, axis_directs, strict=True):
            factorized_box = factorized_box.multiply_nonnegative(axis_sum)
            direct_box = direct_box.multiply_nonnegative(axis_direct)
        joint_box = factorized_box.intersect(direct_box)
        if not (0 < joint_box.lower <= joint_box.upper < 1):
            raise StationaryIntegralFailure("finite box mass must remain strictly below one")
        output_rows.append(
            {
                "axes": axis_outputs,
                "configuration_index": index,
                "configuration_label": label,
                "factorized_box_mass_interval": _interval_json(factorized_box),
                "factorized_tensor_cell_mass_formula": (
                    "M_pi[i_midpoint,i_relative_parallel,i_relative_perpendicular]="
                    "M_midpoint[i_midpoint]*M_relative_parallel[i_relative_parallel]*"
                    "M_relative_perpendicular[i_relative_perpendicular]"
                ),
                "joint_box_mass_interval": _interval_json(joint_box),
                "member_digest_sha256": member_digest,
                "refinement_family_id": mapping["refinement_family_id"],
                "refinement_member_id": mapping["refinement_member_id"],
                "single_domain_box_mass_interval": _interval_json(direct_box),
                "tensor_state_count": config_row["expected_states"],
            }
        )

    if gaussian_count != 3_446 or periodic_count != 1_591 or minimum_positive_lower is None:
        raise StationaryIntegralFailure("fixed family cell-count identity drift")

    return {
        "claim_boundary": {
            "backend_independence_claimed": False,
            "box_conditionally_renormalized": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "formal_production_bridge_accepted": False,
            "genuine_refinement_sequence_present": False,
            "one_correlated_distinguished_ideal_member_is_contained": False,
            "release_eligible": False,
        },
        "method": {
            "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
            "backend": "gmpy2_2.2.1_MPFR_4.2.1",
            "dense_tensor_materialized": False,
            "primary_method_id": "directed_mpfr_320_reference_density_v1",
            "primary_precision_bits": PRIMARY_BITS,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_method_id": "directed_mpfr_640_reference_density_sentinel_v1",
            "sentinel_precision_bits": SENTINEL_BITS,
            "sentinel_semantics": "same_backend_higher_precision_containment_not_backend_independence",
        },
        "rows": output_rows,
        "schema": SCHEMA,
        "source_pins": {
            "builder_source": {
                "path": "code/build_continuum_c1_stationary_integral_source_v1.py",
                "sha256": _sha256_file(Path(__file__).resolve(), 1_000_000),
            },
            "configuration_source": {
                "path": CONFIGURATION_PATH.as_posix(),
                "sha256": CONFIGURATION_SHA256,
            },
            "ideal_formula_source": {
                "path": FORMULA_PATH.as_posix(),
                "sha256": FORMULA_SHA256,
            },
            "member_spec": {
                "path": MEMBER_PATH.as_posix(),
                "sha256": MEMBER_SHA256,
            },
            "method_registry": {
                "path": METHOD_PATH.as_posix(),
                "sha256": METHOD_SHA256,
            },
            "production_partition_bundle": {
                "path": BUNDLE_PATH.as_posix(),
                "sha256": BUNDLE_SHA256,
            },
            "raw_axis_binding": {
                "path": RAW_BINDING_PATH.as_posix(),
                "sha256": RAW_BINDING_SHA256,
            },
            "reference_density_source": {
                "path": REFERENCE_PATH.as_posix(),
                "sha256": REFERENCE_SHA256,
            },
        },
        "status": STATUS,
        "summary": {
            "all_primary_intervals_contain_640_bit_sentinels": all_primary_contain_sentinel,
            "configuration_count": len(output_rows),
            "factorized_axis_cell_count": gaussian_count + periodic_count,
            "gaussian_axis_cell_count": gaussian_count,
            "maximum_primary_cell_relative_width_exact": _qs(maximum_relative_width),
            "minimum_positive_primary_cell_lower_exact": _qs(minimum_positive_lower),
            "periodic_axis_cell_count": periodic_count,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count"] for row in output_rows
            ),
        },
    }


def _resolve_output(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPORT / candidate
    candidate = Path(os.path.abspath(candidate))
    try:
        candidate.relative_to(REPORT)
    except ValueError as error:
        raise StationaryIntegralFailure("output must remain within the report root") from error
    return candidate


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_OUTPUT.as_posix())
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    output = _resolve_output(arguments.output)
    payload = _pretty(_build())
    if arguments.check:
        if not output.is_file() or output.read_bytes() != payload:
            raise StationaryIntegralFailure("current stationary-integral artifact is stale")
        print(_sha256_bytes(payload))
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    print(_sha256_bytes(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
