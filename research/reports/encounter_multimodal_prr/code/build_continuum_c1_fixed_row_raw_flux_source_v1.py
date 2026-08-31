"""Build the finite-row raw-axis/common-flux source candidate.

The builder is deliberately independent of every project F0 or production
builder module.  It decodes the frozen big-endian binary64 interval files,
loads the exact partitions, and re-evaluates the formula-defined ungauged
axis masses, Scharfetter--Gummel rates, and one common edge flux with directed
MPFR rounding at 320 and 640 bits.

The physical stationary-cell masses are read from the separately generated
stationary-integral source.  Their ratios against the formula-defined raw
masses are retained as one-dimensional factors, so the global gauge and the
range of rho can be enclosed without materializing any tensor state.

This remains a source candidate for twelve finite anchors.  It does not issue
a same-member acceptance receipt, reconstruct killing, prove a refinement
limit, or complete any continuum obligation.
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
    or _authenticated_context.get("target_key") != "raw_flux_builder"
    or _authenticated_context.get("target_source_path")
    != "code/build_continuum_c1_fixed_row_raw_flux_source_v1.py"
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
import struct
import tempfile
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

REPORT: Final = Path(__file__).resolve().parents[1]
SCHEMA: Final = "encounter_continuum_c1_fixed_row_raw_flux_source_v1"
STATUS: Final = (
    "PASS_FIXED_12_ROW_RAW_FORMULA_COMMON_KAPPA_AND_FACTORIZED_RHO_"
    "SOURCE_CANDIDATE_ONLY_NO_SAME_MEMBER_ACCEPTANCE_NO_COMPLETE_C1_C2"
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
FACTORIZATION_PATH: Final = Path("artifacts/data/continuum_c1_factorization_source_v1.json")
FACTORIZATION_SHA256: Final = "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca"
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
STATIONARY_PATH: Final = Path("artifacts/data/continuum_c1_stationary_integral_source_v1.json")
STATIONARY_SHA256: Final = "03db61b4aa9c2b7a4ab2fd78c86fbbf90dd1548657c615d91c1526ae3ed77212"
BUNDLE_PATH: Final = Path("artifacts/data/physical_production_initial_stream_v1/bundle.json")
BUNDLE_ROOT: Final = BUNDLE_PATH.parent
BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
DEFAULT_OUTPUT: Final = Path("artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json")


class RawFluxSourceFailure(RuntimeError):
    """Fail-closed error for the fixed-row raw-flux source."""


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise RawFluxSourceFailure("interval endpoints must be exact Fractions")
        if self.lower > self.upper:
            raise RawFluxSourceFailure("reversed exact interval")

    def add(self, other: ExactInterval) -> ExactInterval:
        return ExactInterval(self.lower + other.lower, self.upper + other.upper)

    def multiply_nonnegative(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower < 0:
            raise RawFluxSourceFailure("nonnegative interval multiplication required")
        return ExactInterval(self.lower * other.lower, self.upper * other.upper)

    def divide_positive(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower <= 0:
            raise RawFluxSourceFailure("positive interval divisor required")
        return ExactInterval(self.lower / other.upper, self.upper / other.lower)

    def reciprocal_positive(self) -> ExactInterval:
        if self.lower <= 0:
            raise RawFluxSourceFailure("positive reciprocal interval required")
        return ExactInterval(1 / self.upper, 1 / self.lower)

    def intersect(self, other: ExactInterval) -> ExactInterval:
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise RawFluxSourceFailure("interval witnesses are disjoint")
        return ExactInterval(lower, upper)

    def contains(self, other: ExactInterval) -> bool:
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
            raise RawFluxSourceFailure("invalid MPFR interval")

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_fraction(self.lower), _mpfr_fraction(self.upper))


def _duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise RawFluxSourceFailure("duplicate or invalid JSON key")
        result[key] = value
    return result


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 40:
        raise RawFluxSourceFailure("JSON depth cap exceeded")
    if isinstance(value, float):
        raise RawFluxSourceFailure("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise RawFluxSourceFailure("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise RawFluxSourceFailure("invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise RawFluxSourceFailure(f"forbidden JSON value type: {type(value).__name__}")


def _pretty(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path, cap: int = 16_000_000) -> str:
    data = path.read_bytes()
    if len(data) > cap:
        raise RawFluxSourceFailure(f"oversized input: {path}")
    return _sha256_bytes(data)


def _safe_relative(value: object) -> Path:
    if type(value) is not str:
        raise RawFluxSourceFailure("report-relative path must be a string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or "." in pure.parts:
        raise RawFluxSourceFailure("unsafe report-relative path")
    return Path(*pure.parts)


def _resolved_regular_file(relative: Path) -> Path:
    candidate = REPORT / relative
    if candidate.is_symlink() or not candidate.is_file():
        raise RawFluxSourceFailure(f"source is not a regular file: {relative}")
    try:
        candidate.resolve().relative_to(REPORT.resolve())
    except ValueError as error:
        raise RawFluxSourceFailure(f"source escapes report root: {relative}") from error
    return candidate


def _json_source(
    path: Path,
    expected_sha256: str,
    cap: int = 16_000_000,
) -> dict[str, Any]:
    absolute = _resolved_regular_file(path)
    data = absolute.read_bytes()
    if len(data) > cap or _sha256_bytes(data) != expected_sha256:
        raise RawFluxSourceFailure(f"source hash or size drift: {path}")
    try:
        value = json.loads(
            data.decode("ascii"),
            object_pairs_hook=_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                RawFluxSourceFailure(f"JSON float forbidden: {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                RawFluxSourceFailure(f"JSON constant forbidden: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RawFluxSourceFailure(f"invalid strict JSON: {path}") from error
    _strict_tree(value)
    if type(value) is not dict or _pretty(value) != data:
        raise RawFluxSourceFailure(f"noncanonical JSON object: {path}")
    return value


def _q(value: object) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise RawFluxSourceFailure("canonical p/q string required")
    numerator_text, denominator_text = value.split("/")
    try:
        result = Fraction(int(numerator_text), int(denominator_text))
    except (ValueError, ZeroDivisionError) as error:
        raise RawFluxSourceFailure("invalid p/q string") from error
    if result.denominator <= 0 or _qs(result) != value:
        raise RawFluxSourceFailure("noncanonical p/q string")
    return result


def _qs(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _hex_q(value: object) -> Fraction:
    if type(value) is not str:
        raise RawFluxSourceFailure("binary64 hex string required")
    try:
        number = float.fromhex(value)
    except ValueError as error:
        raise RawFluxSourceFailure("invalid binary64 hex string") from error
    if (
        not math.isfinite(number)
        or number.hex() != value
        or (number == 0.0 and math.copysign(1.0, number) < 0)
    ):
        raise RawFluxSourceFailure("noncanonical finite binary64 hex string")
    return Fraction.from_float(number)


def _interval_json(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _qs(value.lower),
        "upper_exact_p_over_q": _qs(value.upper),
    }


def _interval_source(value: object) -> ExactInterval:
    if type(value) is not dict or set(value) != {
        "lower_exact_p_over_q",
        "upper_exact_p_over_q",
    }:
        raise RawFluxSourceFailure("strict interval object required")
    return ExactInterval(
        _q(value["lower_exact_p_over_q"]),
        _q(value["upper_exact_p_over_q"]),
    )


def _sum_intervals(values: list[ExactInterval]) -> ExactInterval:
    result = ExactInterval(Fraction(0), Fraction(0))
    for value in values:
        result = result.add(value)
    return result


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


def _mp_from_q(value: Fraction, precision: int) -> MPInterval:
    return MPInterval(
        _mp_q(value, precision, gmpy2.RoundDown),
        _mp_q(value, precision, gmpy2.RoundUp),
        precision,
    )


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
        if operation == "div":
            return +(left / right)
    raise RawFluxSourceFailure("unknown MPFR binary operation")


def _mp_exp(value: Fraction, precision: int) -> MPInterval:
    source = _mp_from_q(value, precision)
    with gmpy2.context(_context(precision, gmpy2.RoundDown)):
        lower = +gmpy2.exp(source.lower)
    with gmpy2.context(_context(precision, gmpy2.RoundUp)):
        upper = +gmpy2.exp(source.upper)
    return MPInterval(lower, upper, precision)


def _mp_mul_nonnegative(left: MPInterval, right: MPInterval) -> MPInterval:
    if left.precision != right.precision or left.lower < 0 or right.lower < 0:
        raise RawFluxSourceFailure("nonnegative MPFR multiplication mismatch")
    precision = left.precision
    return MPInterval(
        _mp_binary(
            left.lower,
            right.lower,
            precision,
            gmpy2.RoundDown,
            "mul",
        ),
        _mp_binary(
            left.upper,
            right.upper,
            precision,
            gmpy2.RoundUp,
            "mul",
        ),
        precision,
    )


def _mp_scale_nonnegative(value: MPInterval, factor: Fraction) -> MPInterval:
    if factor < 0:
        raise RawFluxSourceFailure("negative MPFR scale")
    return _mp_mul_nonnegative(value, _mp_from_q(factor, value.precision))


def _mp_bernoulli_positive(value: Fraction, precision: int) -> MPInterval:
    if value <= 0:
        raise RawFluxSourceFailure("positive Bernoulli input required")
    source = _mp_from_q(value, precision)
    one = _mp_q(Fraction(1), precision, gmpy2.RoundToNearest)
    with gmpy2.context(_context(precision, gmpy2.RoundDown)):
        denominator_lower = +(gmpy2.exp(source.lower) - one)
    with gmpy2.context(_context(precision, gmpy2.RoundUp)):
        denominator_upper = +(gmpy2.exp(source.upper) - one)
    if denominator_lower <= 0:
        raise RawFluxSourceFailure("Bernoulli denominator is not positive")
    return MPInterval(
        _mp_binary(
            source.lower,
            denominator_upper,
            precision,
            gmpy2.RoundDown,
            "div",
        ),
        _mp_binary(
            source.upper,
            denominator_lower,
            precision,
            gmpy2.RoundUp,
            "div",
        ),
        precision,
    )


def _mp_bernoulli(value: Fraction, precision: int) -> MPInterval:
    if value == 0:
        return _mp_from_q(Fraction(1), precision)
    if value > 0:
        return _mp_bernoulli_positive(value, precision)
    positive = -value
    return _mp_mul_nonnegative(
        _mp_exp(positive, precision),
        _mp_bernoulli_positive(positive, precision),
    )


def _formula_mu(
    potential: Fraction,
    volume: Fraction,
    precision: int,
) -> ExactInterval:
    return _mp_scale_nonnegative(_mp_exp(-potential, precision), volume).exact()


def _formula_rate(
    delta_potential: Fraction,
    diffusion: Fraction,
    origin_volume: Fraction,
    distance: Fraction,
    precision: int,
) -> ExactInterval:
    if diffusion <= 0 or origin_volume <= 0 or distance <= 0:
        raise RawFluxSourceFailure("invalid SG rate parameter")
    return _mp_scale_nonnegative(
        _mp_bernoulli(delta_potential, precision),
        diffusion / (origin_volume * distance),
    ).exact()


def _formula_kappa(
    left_potential: Fraction,
    delta_potential: Fraction,
    diffusion: Fraction,
    distance: Fraction,
    precision: int,
) -> ExactInterval:
    if diffusion <= 0 or distance <= 0:
        raise RawFluxSourceFailure("invalid common-flux parameter")
    return _mp_scale_nonnegative(
        _mp_mul_nonnegative(
            _mp_exp(-left_potential, precision),
            _mp_bernoulli(delta_potential, precision),
        ),
        diffusion / distance,
    ).exact()


def _binary64_intervals(
    *,
    relative: Path,
    expected_sha256: str,
    expected_count: int,
    expected_bytes: int,
) -> list[ExactInterval]:
    absolute = _resolved_regular_file(relative)
    data = absolute.read_bytes()
    if (
        len(data) != expected_bytes
        or expected_bytes != 16 * expected_count
        or _sha256_bytes(data) != expected_sha256
    ):
        raise RawFluxSourceFailure(f"binary interval file drift: {relative}")
    result: list[ExactInterval] = []
    for lower_float, upper_float in struct.iter_unpack(">dd", data):
        if (
            not math.isfinite(lower_float)
            or not math.isfinite(upper_float)
            or lower_float < 0
            or lower_float > upper_float
            or (lower_float == 0.0 and math.copysign(1.0, lower_float) < 0)
            or (upper_float == 0.0 and math.copysign(1.0, upper_float) < 0)
        ):
            raise RawFluxSourceFailure(f"invalid stored interval: {relative}")
        result.append(
            ExactInterval(
                Fraction.from_float(lower_float),
                Fraction.from_float(upper_float),
            )
        )
    if len(result) != expected_count:
        raise RawFluxSourceFailure(f"binary interval count drift: {relative}")
    return result


def _rate_file(
    axis_entry: dict[str, Any],
    coordinate: str,
    role: str,
    count: int,
) -> tuple[list[ExactInterval], dict[str, str]]:
    rates = axis_entry.get("rates")
    if type(rates) is not dict or type(rates.get(role)) is not dict:
        raise RawFluxSourceFailure("axis rate manifest missing")
    role_entry = rates[role]
    file_entry = role_entry.get("file")
    manifest = role_entry.get("manifest")
    if type(file_entry) is not dict or type(manifest) is not dict:
        raise RawFluxSourceFailure("axis rate file binding missing")
    path_value = file_entry.get("path")
    sha_value = file_entry.get("sha256")
    byte_length = file_entry.get("byte_length")
    if (
        type(path_value) is not str
        or type(sha_value) is not str
        or type(byte_length) is not int
        or isinstance(byte_length, bool)
        or manifest.get("record_format") != ">dd"
        or manifest.get("byte_order") != "big"
        or manifest.get("record_count") != count
        or manifest.get("raw_byte_length") != byte_length
        or manifest.get("raw_sha256") != sha_value
        or manifest.get("logical_shape") != [count]
        or manifest.get("schema") != "encounter_big_endian_binary64_interval_file_v1"
        or manifest.get("role") != f"control_free_axis_{coordinate}_{role}"
    ):
        raise RawFluxSourceFailure("strict binary interval manifest drift")
    relative = BUNDLE_ROOT / _safe_relative(path_value)
    return (
        _binary64_intervals(
            relative=relative,
            expected_sha256=sha_value,
            expected_count=count,
            expected_bytes=byte_length,
        ),
        {
            "path": path_value,
            "sha256": sha_value,
        },
    )


def _metric_relative_width(
    enclosure: ExactInterval,
    reference: ExactInterval,
) -> Fraction:
    if reference.lower <= 0:
        raise RawFluxSourceFailure("positive metric reference required")
    return (enclosure.upper - enclosure.lower) / reference.lower


def _metric_relative_margin(
    enclosure: ExactInterval,
    contained: ExactInterval,
) -> Fraction:
    if contained.upper <= 0 or not enclosure.contains(contained):
        raise RawFluxSourceFailure("invalid containment margin")
    return (
        min(
            contained.lower - enclosure.lower,
            enclosure.upper - contained.upper,
        )
        / contained.upper
    )


def _update_maximum(
    current: tuple[Fraction, str] | None,
    value: Fraction,
    location: str,
) -> tuple[Fraction, str]:
    if current is None or value > current[0]:
        return value, location
    return current


def _update_minimum(
    current: tuple[Fraction, str] | None,
    value: Fraction,
    location: str,
) -> tuple[Fraction, str]:
    if current is None or value < current[0]:
        return value, location
    return current


def _metric_json(value: tuple[Fraction, str] | None) -> dict[str, str]:
    if value is None:
        raise RawFluxSourceFailure("missing summary metric")
    return {
        "location": value[1],
        "value_exact_p_over_q": _qs(value[0]),
    }


def _digest_stream(domain: bytes) -> Any:
    if not domain.endswith(b"\0"):
        raise RawFluxSourceFailure("digest domain must be NUL terminated")
    result = hashlib.sha256()
    result.update(domain)
    return result


def _digest_update(digest: Any, value: Any) -> None:
    digest.update(_pretty(value))


def _source_pin_matches(
    source: dict[str, Any],
    key: str,
    path: Path,
    sha256: str,
) -> bool:
    pins = source.get("source_pins")
    return type(pins) is dict and pins.get(key) == {
        "path": path.as_posix(),
        "sha256": sha256,
    }


def _build() -> dict[str, Any]:
    if gmpy2.__version__ != "2.2.1" or gmpy2.mpfr_version() != "MPFR 4.2.1":
        raise RawFluxSourceFailure("unaccepted gmpy2/MPFR runtime")

    reference = _json_source(REFERENCE_PATH, REFERENCE_SHA256, 100_000)
    formula = _json_source(FORMULA_PATH, FORMULA_SHA256, 100_000)
    factorization = _json_source(FACTORIZATION_PATH, FACTORIZATION_SHA256, 100_000)
    member = _json_source(MEMBER_PATH, MEMBER_SHA256, 100_000)
    method = _json_source(METHOD_PATH, METHOD_SHA256, 100_000)
    configuration = _json_source(CONFIGURATION_PATH, CONFIGURATION_SHA256, 1_000_000)
    raw_binding = _json_source(RAW_BINDING_PATH, RAW_BINDING_SHA256, 100_000)
    stationary = _json_source(STATIONARY_PATH, STATIONARY_SHA256, 4_000_000)
    bundle = _json_source(BUNDLE_PATH, BUNDLE_SHA256, 2_000_000)

    if (
        reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1"
        or formula.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1"
        or factorization.get("schema") != "encounter_continuum_c1_factorization_source_v1"
        or member.get("schema") != "encounter_continuum_c1_c2_fixed_row_member_spec_v1"
        or method.get("schema") != "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1"
        or configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or raw_binding.get("schema") != "encounter_continuum_c1_raw_axis_production_binding_v1"
        or stationary.get("schema") != "encounter_continuum_c1_stationary_integral_source_v1"
        or bundle.get("schema") != "encounter_control_free_production_initial_stream_v1"
    ):
        raise RawFluxSourceFailure("source schema drift")

    if (
        not _source_pin_matches(raw_binding, "member_spec", MEMBER_PATH, MEMBER_SHA256)
        or not _source_pin_matches(
            raw_binding,
            "method_registry",
            METHOD_PATH,
            METHOD_SHA256,
        )
        or not _source_pin_matches(
            raw_binding,
            "production_bundle",
            BUNDLE_PATH,
            BUNDLE_SHA256,
        )
        or not _source_pin_matches(stationary, "member_spec", MEMBER_PATH, MEMBER_SHA256)
        or not _source_pin_matches(
            stationary,
            "method_registry",
            METHOD_PATH,
            METHOD_SHA256,
        )
        or not _source_pin_matches(
            stationary,
            "raw_axis_binding",
            RAW_BINDING_PATH,
            RAW_BINDING_SHA256,
        )
        or not _source_pin_matches(
            stationary,
            "production_partition_bundle",
            BUNDLE_PATH,
            BUNDLE_SHA256,
        )
        or not _source_pin_matches(
            stationary,
            "configuration_source",
            CONFIGURATION_PATH,
            CONFIGURATION_SHA256,
        )
        or not _source_pin_matches(
            stationary,
            "ideal_formula_source",
            FORMULA_PATH,
            FORMULA_SHA256,
        )
        or not _source_pin_matches(
            stationary,
            "reference_density_source",
            REFERENCE_PATH,
            REFERENCE_SHA256,
        )
    ):
        raise RawFluxSourceFailure("cross-source pin drift")
    role_bindings = member.get("role_bindings")
    if (
        type(role_bindings) is not dict
        or role_bindings.get("configuration_source")
        != {
            "path": CONFIGURATION_PATH.as_posix(),
            "sha256": CONFIGURATION_SHA256,
        }
        or role_bindings.get("factorization_source")
        != {
            "path": FACTORIZATION_PATH.as_posix(),
            "sha256": FACTORIZATION_SHA256,
        }
        or role_bindings.get("ideal_formula_source")
        != {
            "path": FORMULA_PATH.as_posix(),
            "sha256": FORMULA_SHA256,
        }
        or role_bindings.get("reference_density_source")
        != {
            "path": REFERENCE_PATH.as_posix(),
            "sha256": REFERENCE_SHA256,
        }
    ):
        raise RawFluxSourceFailure("member role binding drift")

    methods = method.get("methods")
    if type(methods) is not list:
        raise RawFluxSourceFailure("method registry rows missing")
    method_by_id = {
        row.get("method_id"): row
        for row in methods
        if type(row) is dict and type(row.get("method_id")) is str
    }
    if (
        method_by_id.get("directed_mpfr_320_reference_density_v1", {}).get("precision_bits")
        != PRIMARY_BITS
        or method_by_id.get(
            "directed_mpfr_640_reference_density_sentinel_v1",
            {},
        ).get("precision_bits")
        != SENTINEL_BITS
        or method_by_id.get("binary64_interval_decode_v1", {}).get("rounding_mode")
        != "stored_outward_endpoints"
        or method_by_id.get("exact_rational_tensor_factorization_v1", {}).get("rounding_mode")
        != "exact"
    ):
        raise RawFluxSourceFailure("registered method drift")

    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        raise RawFluxSourceFailure("configuration dynamics missing")
    particle_diffusion = _hex_q(dynamics.get("particle_diffusion_binary64_hex"))
    stiffness = _hex_q(dynamics.get("ou_stiffness_binary64_hex"))
    mean = _hex_q(dynamics.get("ou_mean_binary64_hex"))
    period = _q(dynamics.get("transverse_period_exact"))
    if particle_diffusion <= 0 or stiffness <= 0 or period <= 0:
        raise RawFluxSourceFailure("nonpositive physical parameter")
    axis_diffusions = {
        "midpoint": particle_diffusion / 2,
        "relative_parallel": 2 * particle_diffusion,
        "relative_perpendicular": 2 * particle_diffusion,
    }

    config_rows = configuration.get("configurations")
    bundle_rows = bundle.get("rows")
    stationary_rows = stationary.get("rows")
    mappings = member.get("configuration_semantic_ids")
    expected_order = member.get("configuration_order")
    if not all(
        type(value) is list
        for value in (config_rows, bundle_rows, stationary_rows, mappings, expected_order)
    ):
        raise RawFluxSourceFailure("row sources must be lists")
    if not all(
        len(value) == 12
        for value in (config_rows, bundle_rows, stationary_rows, mappings, expected_order)
    ):
        raise RawFluxSourceFailure("12-row source cardinality drift")

    mapping_by_label: dict[str, dict[str, Any]] = {}
    for mapping in mappings:
        if type(mapping) is not dict or type(mapping.get("authority_label")) is not str:
            raise RawFluxSourceFailure("invalid semantic mapping")
        label = mapping["authority_label"]
        if label in mapping_by_label:
            raise RawFluxSourceFailure("duplicate semantic mapping")
        mapping_by_label[label] = mapping

    output_rows: list[dict[str, Any]] = []
    cell_count = 0
    rate_count = 0
    positive_rate_count = 0
    zero_boundary_rate_count = 0
    edge_count = 0
    raw_file_count = 0
    maximum_mu_width: tuple[Fraction, str] | None = None
    maximum_rate_width: tuple[Fraction, str] | None = None
    maximum_flux_width: tuple[Fraction, str] | None = None
    minimum_mu_margin: tuple[Fraction, str] | None = None
    minimum_rate_margin: tuple[Fraction, str] | None = None
    minimum_kappa_margin: tuple[Fraction, str] | None = None
    all_primary_contain_sentinel = True
    all_saved_contain_primary_and_sentinel = True
    all_common_kappa_contained = True
    all_left_right_kappa_intersect = True

    for index, (config_row, bundle_row, stationary_row) in enumerate(
        zip(config_rows, bundle_rows, stationary_rows, strict=True)
    ):
        if (
            type(config_row) is not dict
            or type(bundle_row) is not dict
            or type(stationary_row) is not dict
        ):
            raise RawFluxSourceFailure("invalid row object")
        label = config_row.get("label")
        if (
            type(label) is not str
            or expected_order[index] != label
            or bundle_row.get("configuration_index") != index
            or bundle_row.get("configuration_label") != label
            or stationary_row.get("configuration_index") != index
            or stationary_row.get("configuration_label") != label
        ):
            raise RawFluxSourceFailure("row order or label drift")
        mapping = mapping_by_label.get(label)
        if (
            mapping is None
            or stationary_row.get("refinement_family_id") != mapping.get("refinement_family_id")
            or stationary_row.get("refinement_member_id") != mapping.get("refinement_member_id")
        ):
            raise RawFluxSourceFailure("semantic member mapping drift")

        row_manifest_entry = bundle_row.get("row_manifest")
        if type(row_manifest_entry) is not dict:
            raise RawFluxSourceFailure("row manifest entry missing")
        row_path = BUNDLE_ROOT / _safe_relative(row_manifest_entry.get("path"))
        row_hash = row_manifest_entry.get("sha256")
        if type(row_hash) is not str:
            raise RawFluxSourceFailure("row manifest hash missing")
        row_manifest = _json_source(row_path, row_hash, 300_000)
        axes = row_manifest.get("axes")
        stationary_axes = stationary_row.get("axes")
        if (
            type(axes) is not list
            or type(stationary_axes) is not list
            or len(axes) != 3
            or len(stationary_axes) != 3
        ):
            raise RawFluxSourceFailure("row axis cardinality drift")

        row_axis_outputs: list[dict[str, Any]] = []
        row_axis_sums: list[ExactInterval] = []
        row_axis_factor_ranges: list[ExactInterval] = []
        for coordinate, axis_entry, stationary_axis in zip(
            COORDINATES,
            axes,
            stationary_axes,
            strict=True,
        ):
            if (
                type(axis_entry) is not dict
                or type(stationary_axis) is not dict
                or axis_entry.get("coordinate") != coordinate
                or stationary_axis.get("coordinate") != coordinate
            ):
                raise RawFluxSourceFailure("axis order drift")
            partition_entry = axis_entry.get("partition_file")
            if type(partition_entry) is not dict:
                raise RawFluxSourceFailure("partition entry missing")
            partition_path_value = partition_entry.get("path")
            partition_hash = partition_entry.get("sha256")
            if type(partition_path_value) is not str or type(partition_hash) is not str:
                raise RawFluxSourceFailure("partition binding drift")
            partition_path = BUNDLE_ROOT / _safe_relative(partition_path_value)
            partition = _json_source(partition_path, partition_hash, 1_000_000)
            if (
                partition.get("schema") != "encounter_exact_axis_partition_v1"
                or partition.get("coordinate") != coordinate
                or stationary_axis.get("partition_path") != partition_path_value
                or stationary_axis.get("partition_sha256") != partition_hash
            ):
                raise RawFluxSourceFailure("partition/stationary binding drift")
            size = partition.get("size")
            positions_source = partition.get("positions_exact")
            volumes_source = partition.get("cell_volumes_exact")
            segments_source = partition.get("cell_segments_exact")
            periodic = partition.get("periodic")
            if (
                type(size) is not int
                or isinstance(size, bool)
                or size < 2
                or type(positions_source) is not list
                or type(volumes_source) is not list
                or type(segments_source) is not list
                or type(periodic) is not bool
                or len(positions_source) != size
                or len(volumes_source) != size
                or len(segments_source) != size
                or stationary_axis.get("cell_count") != size
            ):
                raise RawFluxSourceFailure("partition cardinality drift")
            positions = [_q(value) for value in positions_source]
            volumes = [_q(value) for value in volumes_source]
            if any(value <= 0 for value in volumes):
                raise RawFluxSourceFailure("nonpositive cell volume")
            for volume, segments in zip(volumes, segments_source, strict=True):
                if type(segments) is not list or not segments:
                    raise RawFluxSourceFailure("empty cell segments")
                reconstructed_volume = Fraction(0)
                for segment in segments:
                    if type(segment) is not list or len(segment) != 2:
                        raise RawFluxSourceFailure("invalid cell segment")
                    lower, upper = _q(segment[0]), _q(segment[1])
                    if lower >= upper:
                        raise RawFluxSourceFailure("invalid cell segment order")
                    reconstructed_volume += upper - lower
                if reconstructed_volume != volume:
                    raise RawFluxSourceFailure("cell-volume reconstruction drift")
            if not periodic and any(
                left >= right for left, right in zip(positions, positions[1:], strict=False)
            ):
                raise RawFluxSourceFailure("reflecting positions are not increasing")
            if periodic:
                expected_volume = _q(partition.get("domain_width_exact")) / size
                if any(volume != expected_volume for volume in volumes):
                    raise RawFluxSourceFailure("nonuniform periodic partition")

            saved_mu, mu_file = _rate_file(
                axis_entry,
                coordinate,
                "stationary_mass",
                size,
            )
            saved_forward, forward_file = _rate_file(
                axis_entry,
                coordinate,
                "forward",
                size,
            )
            saved_backward, backward_file = _rate_file(
                axis_entry,
                coordinate,
                "backward",
                size,
            )
            raw_file_count += 3
            rate_count += 2 * size
            cell_count += size

            if coordinate == "midpoint":
                potentials = [
                    stiffness * (position - mean) ** 2 / particle_diffusion
                    for position in positions
                ]
            elif coordinate == "relative_parallel":
                potentials = [
                    stiffness * position**2 / (4 * particle_diffusion) for position in positions
                ]
            else:
                potentials = [Fraction(0) for _ in positions]
            diffusion = axis_diffusions[coordinate]

            physical_cells_source = stationary_axis.get("cell_mass_intervals")
            if type(physical_cells_source) is not list or len(physical_cells_source) != size:
                raise RawFluxSourceFailure("physical cell source cardinality drift")
            physical_cells: list[ExactInterval] = []
            for cell_index, physical_source in enumerate(physical_cells_source):
                if (
                    type(physical_source) is not dict
                    or physical_source.get("cell_index") != cell_index
                ):
                    raise RawFluxSourceFailure("physical cell index drift")
                physical_cells.append(
                    _interval_source(
                        {
                            "lower_exact_p_over_q": physical_source.get("lower_exact_p_over_q"),
                            "upper_exact_p_over_q": physical_source.get("upper_exact_p_over_q"),
                        }
                    )
                )

            formula_mu_primary: list[ExactInterval] = []
            rho_axis_factors: list[ExactInterval] = []
            cell_records: list[dict[str, Any]] = []
            cell_audit_digest = _digest_stream(b"encounter-fixed-row-raw-flux-cell-audit-v1\0")
            for cell_index, (potential, volume, saved, physical) in enumerate(
                zip(
                    potentials,
                    volumes,
                    saved_mu,
                    physical_cells,
                    strict=True,
                )
            ):
                primary_mu = _formula_mu(
                    potential,
                    volume,
                    PRIMARY_BITS,
                )
                sentinel_mu = _formula_mu(
                    potential,
                    volume,
                    SENTINEL_BITS,
                )
                if not primary_mu.contains(sentinel_mu):
                    all_primary_contain_sentinel = False
                    raise RawFluxSourceFailure("320-bit mu misses 640-bit sentinel")
                if not saved.contains(primary_mu) or not saved.contains(sentinel_mu):
                    all_saved_contain_primary_and_sentinel = False
                    raise RawFluxSourceFailure("saved mu misses formula-defined member")
                location = f"{label}:{coordinate}:mu[{cell_index}]"
                maximum_mu_width = _update_maximum(
                    maximum_mu_width,
                    _metric_relative_width(saved, primary_mu),
                    location,
                )
                minimum_mu_margin = _update_minimum(
                    minimum_mu_margin,
                    _metric_relative_margin(saved, sentinel_mu),
                    location,
                )
                factor = physical.divide_positive(primary_mu)
                formula_mu_primary.append(primary_mu)
                rho_axis_factors.append(factor)
                _digest_update(
                    cell_audit_digest,
                    {
                        "cell_index": cell_index,
                        "formula_primary": _interval_json(primary_mu),
                        "formula_sentinel": _interval_json(sentinel_mu),
                        "physical_pi_axis_mass": _interval_json(physical),
                        "rho_axis_factor": _interval_json(factor),
                        "saved_ungauged_mu": _interval_json(saved),
                    },
                )
                cell_records.append(
                    {
                        "cell_index": cell_index,
                        "formula_ungauged_mu_interval": _interval_json(primary_mu),
                        "rho_axis_factor_interval": _interval_json(factor),
                    }
                )

            edge_records: list[dict[str, Any]] = []
            edge_audit_digest = _digest_stream(b"encounter-fixed-row-raw-flux-edge-audit-v1\0")
            edge_indices = range(size) if periodic else range(size - 1)
            for left_index in edge_indices:
                right_index = (left_index + 1) % size
                if periodic:
                    forward_primary = _mp_from_q(
                        diffusion / volumes[left_index] ** 2,
                        PRIMARY_BITS,
                    ).exact()
                    forward_sentinel = _mp_from_q(
                        diffusion / volumes[left_index] ** 2,
                        SENTINEL_BITS,
                    ).exact()
                    reverse_primary = _mp_from_q(
                        diffusion / volumes[right_index] ** 2,
                        PRIMARY_BITS,
                    ).exact()
                    reverse_sentinel = _mp_from_q(
                        diffusion / volumes[right_index] ** 2,
                        SENTINEL_BITS,
                    ).exact()
                    common_primary = _mp_from_q(
                        diffusion / volumes[left_index],
                        PRIMARY_BITS,
                    ).exact()
                    common_sentinel = _mp_from_q(
                        diffusion / volumes[left_index],
                        SENTINEL_BITS,
                    ).exact()
                    reverse_kappa_primary = common_primary
                    reverse_kappa_sentinel = common_sentinel
                else:
                    distance = positions[right_index] - positions[left_index]
                    delta = potentials[right_index] - potentials[left_index]
                    forward_primary = _formula_rate(
                        delta,
                        diffusion,
                        volumes[left_index],
                        distance,
                        PRIMARY_BITS,
                    )
                    forward_sentinel = _formula_rate(
                        delta,
                        diffusion,
                        volumes[left_index],
                        distance,
                        SENTINEL_BITS,
                    )
                    reverse_primary = _formula_rate(
                        -delta,
                        diffusion,
                        volumes[right_index],
                        distance,
                        PRIMARY_BITS,
                    )
                    reverse_sentinel = _formula_rate(
                        -delta,
                        diffusion,
                        volumes[right_index],
                        distance,
                        SENTINEL_BITS,
                    )
                    common_primary = _formula_kappa(
                        potentials[left_index],
                        delta,
                        diffusion,
                        distance,
                        PRIMARY_BITS,
                    )
                    common_sentinel = _formula_kappa(
                        potentials[left_index],
                        delta,
                        diffusion,
                        distance,
                        SENTINEL_BITS,
                    )
                    reverse_kappa_primary = _formula_kappa(
                        potentials[right_index],
                        -delta,
                        diffusion,
                        distance,
                        PRIMARY_BITS,
                    )
                    reverse_kappa_sentinel = _formula_kappa(
                        potentials[right_index],
                        -delta,
                        diffusion,
                        distance,
                        SENTINEL_BITS,
                    )

                if (
                    not forward_primary.contains(forward_sentinel)
                    or not reverse_primary.contains(reverse_sentinel)
                    or not common_primary.contains(common_sentinel)
                ):
                    all_primary_contain_sentinel = False
                    raise RawFluxSourceFailure("320-bit edge formula misses 640-bit sentinel")
                saved_forward_rate = saved_forward[left_index]
                saved_reverse_rate = saved_backward[right_index]
                if (
                    not saved_forward_rate.contains(forward_primary)
                    or not saved_forward_rate.contains(forward_sentinel)
                    or not saved_reverse_rate.contains(reverse_primary)
                    or not saved_reverse_rate.contains(reverse_sentinel)
                ):
                    all_saved_contain_primary_and_sentinel = False
                    raise RawFluxSourceFailure("saved edge rate misses formula-defined member")
                forward_flux = saved_mu[left_index].multiply_nonnegative(saved_forward_rate)
                reverse_flux = saved_mu[right_index].multiply_nonnegative(saved_reverse_rate)
                flux_intersection = forward_flux.intersect(reverse_flux)
                if (
                    not forward_flux.contains(common_primary)
                    or not forward_flux.contains(common_sentinel)
                    or not reverse_flux.contains(common_primary)
                    or not reverse_flux.contains(common_sentinel)
                    or not flux_intersection.contains(common_primary)
                    or not flux_intersection.contains(common_sentinel)
                ):
                    all_common_kappa_contained = False
                    raise RawFluxSourceFailure("single common kappa misses saved flux")
                try:
                    common_primary.intersect(reverse_kappa_primary)
                    common_sentinel.intersect(reverse_kappa_sentinel)
                except RawFluxSourceFailure:
                    all_left_right_kappa_intersect = False
                    raise RawFluxSourceFailure(
                        "left/right analytic kappa enclosures are disjoint"
                    ) from None

                edge_location = f"{label}:{coordinate}:edge[{left_index}->{right_index}]"
                maximum_rate_width = _update_maximum(
                    maximum_rate_width,
                    _metric_relative_width(saved_forward_rate, forward_primary),
                    f"{label}:{coordinate}:forward[{left_index}]",
                )
                maximum_rate_width = _update_maximum(
                    maximum_rate_width,
                    _metric_relative_width(saved_reverse_rate, reverse_primary),
                    f"{label}:{coordinate}:backward[{right_index}]",
                )
                minimum_rate_margin = _update_minimum(
                    minimum_rate_margin,
                    _metric_relative_margin(saved_forward_rate, forward_sentinel),
                    f"{label}:{coordinate}:forward[{left_index}]",
                )
                minimum_rate_margin = _update_minimum(
                    minimum_rate_margin,
                    _metric_relative_margin(saved_reverse_rate, reverse_sentinel),
                    f"{label}:{coordinate}:backward[{right_index}]",
                )
                maximum_flux_width = _update_maximum(
                    maximum_flux_width,
                    _metric_relative_width(flux_intersection, common_primary),
                    edge_location,
                )
                minimum_kappa_margin = _update_minimum(
                    minimum_kappa_margin,
                    _metric_relative_margin(flux_intersection, common_sentinel),
                    edge_location,
                )
                _digest_update(
                    edge_audit_digest,
                    {
                        "common_primary": _interval_json(common_primary),
                        "common_sentinel": _interval_json(common_sentinel),
                        "edge_index": left_index,
                        "forward_formula_primary": _interval_json(forward_primary),
                        "forward_formula_sentinel": _interval_json(forward_sentinel),
                        "left_cell_index": left_index,
                        "reverse_formula_primary": _interval_json(reverse_primary),
                        "reverse_formula_sentinel": _interval_json(reverse_sentinel),
                        "reverse_kappa_primary": _interval_json(reverse_kappa_primary),
                        "reverse_kappa_sentinel": _interval_json(reverse_kappa_sentinel),
                        "right_cell_index": right_index,
                        "saved_flux_intersection": _interval_json(flux_intersection),
                        "saved_forward_flux": _interval_json(forward_flux),
                        "saved_forward_rate": _interval_json(saved_forward_rate),
                        "saved_reverse_flux": _interval_json(reverse_flux),
                        "saved_reverse_rate": _interval_json(saved_reverse_rate),
                    },
                )
                edge_records.append(
                    {
                        "common_kappa_formula_interval": _interval_json(common_primary),
                        "edge_index": left_index,
                        "left_cell_index": left_index,
                        "right_cell_index": right_index,
                        "saved_flux_intersection_interval": _interval_json(flux_intersection),
                    }
                )
                edge_count += 1
                positive_rate_count += 2

            boundary_records: list[dict[str, Any]] = []
            if not periodic:
                boundary_pairs = (
                    ("backward", 0, saved_backward[0]),
                    ("forward", size - 1, saved_forward[size - 1]),
                )
                for role, cell_index, saved_zero in boundary_pairs:
                    if saved_zero != ExactInterval(Fraction(0), Fraction(0)):
                        raise RawFluxSourceFailure("reflecting boundary rate is not exact zero")
                    boundary_records.append(
                        {
                            "cell_index": cell_index,
                            "rate_interval": _interval_json(saved_zero),
                            "role": role,
                        }
                    )
                    zero_boundary_rate_count += 1

            axis_sum = _sum_intervals(formula_mu_primary)
            physical_axis_sum = _interval_source(stationary_axis.get("joint_domain_mass_interval"))
            axis_factor_range = ExactInterval(
                min(value.lower for value in rho_axis_factors),
                max(value.upper for value in rho_axis_factors),
            )
            row_axis_sums.append(axis_sum)
            row_axis_factor_ranges.append(axis_factor_range)
            row_axis_outputs.append(
                {
                    "boundary_zero_rate_records": boundary_records,
                    "cell_containment_audit_digest_sha256": (cell_audit_digest.hexdigest()),
                    "cell_count": size,
                    "cell_records": cell_records,
                    "coordinate": coordinate,
                    "edge_containment_audit_digest_sha256": (edge_audit_digest.hexdigest()),
                    "edge_count": len(edge_records),
                    "edge_records": edge_records,
                    "formula_axis_mu_sum_interval": _interval_json(axis_sum),
                    "partition_path": partition_path_value,
                    "partition_sha256": partition_hash,
                    "periodic": periodic,
                    "physical_axis_mass_sum_interval": _interval_json(physical_axis_sum),
                    "raw_files": {
                        "backward": backward_file,
                        "forward": forward_file,
                        "stationary_mass": mu_file,
                    },
                    "rho_axis_factor_range_interval": _interval_json(axis_factor_range),
                }
            )

        axis_sum_product = ExactInterval(Fraction(1), Fraction(1))
        rho_factor_product_range = ExactInterval(Fraction(1), Fraction(1))
        for axis_sum, factor_range in zip(
            row_axis_sums,
            row_axis_factor_ranges,
            strict=True,
        ):
            axis_sum_product = axis_sum_product.multiply_nonnegative(axis_sum)
            rho_factor_product_range = rho_factor_product_range.multiply_nonnegative(factor_range)
        box_mass = _interval_source(stationary_row.get("joint_box_mass_interval"))
        global_gauge = box_mass.divide_positive(axis_sum_product)
        inverse_global_gauge = global_gauge.reciprocal_positive()
        rho_range = rho_factor_product_range.multiply_nonnegative(inverse_global_gauge)
        output_rows.append(
            {
                "axes": row_axis_outputs,
                "axis_mu_sum_product_interval": _interval_json(axis_sum_product),
                "configuration_index": index,
                "configuration_label": label,
                "factorized_box_mass_interval": _interval_json(box_mass),
                "global_gauge_formula": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
                "global_gauge_interval": _interval_json(global_gauge),
                "inverse_global_gauge_interval": _interval_json(inverse_global_gauge),
                "member_digest_sha256": stationary_row.get("member_digest_sha256"),
                "refinement_family_id": mapping.get("refinement_family_id"),
                "refinement_member_id": mapping.get("refinement_member_id"),
                "rho_factorization_formula": (
                    "rho[i,j,k]=G^-1*"
                    "(M_midpoint[i]/mu_midpoint[i])*"
                    "(M_relative_parallel[j]/mu_relative_parallel[j])*"
                    "(M_relative_perpendicular[k]/mu_relative_perpendicular[k])"
                ),
                "rho_range_interval": _interval_json(rho_range),
                "tensor_state_count": stationary_row.get("tensor_state_count"),
            }
        )

    if (
        cell_count != 5_037
        or rate_count != 10_074
        or positive_rate_count != 10_026
        or zero_boundary_rate_count != 48
        or edge_count != 5_013
        or raw_file_count != 108
    ):
        raise RawFluxSourceFailure("fixed family inventory identity drift")

    return {
        "claim_boundary": {
            "backend_independence_claimed": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "concrete_killing_reconstructed": False,
            "formal_production_bridge_accepted": False,
            "genuine_refinement_sequence_present": False,
            "one_correlated_distinguished_member_certified": False,
            "production_source_roles_1_through_11_bound": False,
            "release_eligible": False,
            "same_member_acceptance_receipt_present": False,
        },
        "factorization": {
            "dense_tensor_materialized": False,
            "global_gauge": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
            "rho": (
                "rho[i,j,k]=G^-1*"
                "(M_midpoint[i]/mu_midpoint[i])*"
                "(M_relative_parallel[j]/mu_relative_parallel[j])*"
                "(M_relative_perpendicular[k]/mu_relative_perpendicular[k])"
            ),
            "tensor_common_conductance": (
                "c_axis_edge=G*kappa_axis_edge*product_spectator_axis_mu"
            ),
        },
        "method": {
            "aggregation": "exact_Fraction_endpoint_algebra",
            "binary64_decode_method_id": "binary64_interval_decode_v1",
            "common_kappa_definition": (
                "reflecting:(D_axis/d_ij)*exp(-Phi_i)*Bernoulli(Phi_j-Phi_i);"
                "periodic:D_axis/cell_width"
            ),
            "dense_tensor_materialized": False,
            "primary_method_id": "directed_mpfr_320_reference_density_v1",
            "primary_precision_bits": PRIMARY_BITS,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_method_id": "directed_mpfr_640_reference_density_sentinel_v1",
            "sentinel_precision_bits": SENTINEL_BITS,
            "sentinel_semantics": (
                "same_backend_higher_precision_containment_not_backend_independence"
            ),
        },
        "rows": output_rows,
        "schema": SCHEMA,
        "source_pins": {
            "builder_source": {
                "path": "code/build_continuum_c1_fixed_row_raw_flux_source_v1.py",
                "sha256": _sha256_file(Path(__file__).resolve(), 1_000_000),
            },
            "configuration_source": {
                "path": CONFIGURATION_PATH.as_posix(),
                "sha256": CONFIGURATION_SHA256,
            },
            "factorization_source": {
                "path": FACTORIZATION_PATH.as_posix(),
                "sha256": FACTORIZATION_SHA256,
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
            "production_bundle": {
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
            "stationary_integral_source": {
                "path": STATIONARY_PATH.as_posix(),
                "sha256": STATIONARY_SHA256,
            },
        },
        "status": STATUS,
        "summary": {
            "all_320_bit_formula_intervals_contain_640_bit_sentinels": (
                all_primary_contain_sentinel
            ),
            "all_formula_mu_and_rate_intervals_contained_by_saved_raw_intervals": (
                all_saved_contain_primary_and_sentinel
            ),
            "all_left_and_right_common_kappa_formula_enclosures_intersect": (
                all_left_right_kappa_intersect
            ),
            "all_single_common_kappa_intervals_contained_by_both_saved_flux_sides_and_intersections": (
                all_common_kappa_contained
            ),
            "axis_cell_count": cell_count,
            "axis_edge_count": edge_count,
            "configuration_count": len(output_rows),
            "maximum_saved_flux_intersection_relative_width": _metric_json(maximum_flux_width),
            "maximum_saved_mu_relative_width": _metric_json(maximum_mu_width),
            "maximum_saved_rate_relative_width": _metric_json(maximum_rate_width),
            "minimum_common_kappa_containment_relative_margin": _metric_json(minimum_kappa_margin),
            "minimum_saved_mu_containment_relative_margin": _metric_json(minimum_mu_margin),
            "minimum_saved_rate_containment_relative_margin": _metric_json(minimum_rate_margin),
            "positive_saved_rate_entry_count": positive_rate_count,
            "raw_binary_interval_file_count": raw_file_count,
            "saved_rate_entry_count": rate_count,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count"] for row in output_rows
            ),
            "zero_reflecting_boundary_rate_entry_count": zero_boundary_rate_count,
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
        raise RawFluxSourceFailure("output must remain within report root") from error
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
            raise RawFluxSourceFailure("current fixed-row raw-flux artifact is stale")
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
