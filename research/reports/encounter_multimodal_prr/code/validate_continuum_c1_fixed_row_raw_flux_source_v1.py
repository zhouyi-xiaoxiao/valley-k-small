#!/usr/bin/env python3
"""Independently validate the fixed-row raw-axis/common-flux source.

This verifier never imports or executes the source builder, a production
producer, or F0.  The Round-171 authenticated launcher must snapshot and
execute these source bytes after authenticating the pinned gmpy2/MPFR
dependency closure.  Consequently this file deliberately has no ordinary
``import gmpy2`` path: direct execution fails before scientific work.

The verifier snapshots all fixed authorities, all 206 production-bundle
inventory files, and the selected artifact.  It independently reconstructs
all 36 exact partitions, decodes all 108 raw interval files, and re-evaluates
every formula-defined mass, rate, and common edge flux at 320 and 640 bits.
An alternate 768-bit Bernoulli evaluation is used as a same-backend route
sentinel.  Exact rational arithmetic then reconstructs the gauge and rho
factorization and the complete expected artifact.

Passing this verifier establishes only a source-consistency result for twelve
fixed finite anchors.  It is not a same-member acceptance receipt, does not
bind killing, is not backend independence, and does not complete C1 or C2.
"""

# ruff: noqa: E402, I001 -- authenticated entry must precede ordinary imports.
from __future__ import annotations

import sys


class _UnauthenticatedEntry(RuntimeError):
    """Raised before scientific imports when the authenticated launcher is absent."""


_EXECUTION_CONTEXT = globals().get("_CONTINUUM_C1_AUTHENTICATED_EXECUTION_CONTEXT")
if type(_EXECUTION_CONTEXT) is not dict:
    raise _UnauthenticatedEntry(
        "HOLD_AUTHENTICATED_RUNTIME: use the Round-171 continuum C1 MPFR launcher"
    )
gmpy2 = sys.modules.get("gmpy2")
if gmpy2 is None:
    raise _UnauthenticatedEntry(
        "HOLD_AUTHENTICATED_RUNTIME: launcher did not preload authenticated gmpy2"
    )

import argparse
import hashlib
import json
import math
import os
import re
import stat
import struct
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final


HERE: Final = Path(__file__).resolve()
REPORT: Final = HERE.parents[1]
SCHEMA: Final = "encounter_continuum_c1_fixed_row_raw_flux_source_v1"
STATUS: Final = (
    "PASS_FIXED_12_ROW_RAW_FORMULA_COMMON_KAPPA_AND_FACTORIZED_RHO_"
    "SOURCE_CANDIDATE_ONLY_NO_SAME_MEMBER_ACCEPTANCE_NO_COMPLETE_C1_C2"
)
VALIDATION_STATUS: Final = (
    "PASS_FIXED_12_ROW_RAW_FLUX_SOURCE_INDEPENDENT_VALIDATION_ONLY_"
    "NO_SAME_MEMBER_ACCEPTANCE_NO_COMPLETE_C1_C2"
)
PRIMARY_BITS: Final = 320
SENTINEL_BITS: Final = 640
ALTERNATE_BITS: Final = 768
COORDINATES: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)

REFERENCE_PATH: Final = "artifacts/data/continuum_c1_reference_density_source_v1.json"
REFERENCE_SHA256: Final = "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575"
FORMULA_PATH: Final = "artifacts/data/continuum_c1_ideal_formula_source_v1.json"
FORMULA_SHA256: Final = "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be"
FACTORIZATION_PATH: Final = "artifacts/data/continuum_c1_factorization_source_v1.json"
FACTORIZATION_SHA256: Final = "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca"
MEMBER_PATH: Final = "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json"
MEMBER_SHA256: Final = "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef"
METHOD_PATH: Final = "artifacts/data/continuum_c1_c2_fixed_row_outward_method_registry_v1.json"
METHOD_SHA256: Final = "ac00450edf826029b157a98ad2835592630c07b2a75334c25d8d1232a4fe69c3"
CONFIGURATION_PATH: Final = "artifacts/data/physical_configuration_family_control_free_v1.json"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
RAW_BINDING_PATH: Final = "artifacts/data/continuum_c1_raw_axis_production_binding_v1.json"
RAW_BINDING_SHA256: Final = "7028fecf4538abb1df56f03d8cea01d0ed208a43356cb9b1e24c67fb54d47480"
STATIONARY_PATH: Final = "artifacts/data/continuum_c1_stationary_integral_source_v1.json"
STATIONARY_SHA256: Final = "03db61b4aa9c2b7a4ab2fd78c86fbbf90dd1548657c615d91c1526ae3ed77212"
BUNDLE_PATH: Final = "artifacts/data/physical_production_initial_stream_v1/bundle.json"
BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
BUNDLE_ROOT: Final = "artifacts/data/physical_production_initial_stream_v1"
BUILDER_PATH: Final = "code/build_continuum_c1_fixed_row_raw_flux_source_v1.py"
BUILDER_SHA256: Final = "48b29162e533c02950b673d8b207efc771091b9b16581967a5e9ef487bf20a92"
DEFAULT_ARTIFACT: Final = REPORT / (
    "artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json"
)
DEFAULT_ARTIFACT_SHA256: Final = (
    "04fee91f8708d90febc23e1f1ee4cfc1cb4800b9e35980eb99006fad327b40f3"
)

PINNED_JSON: Final = {
    "reference": (REFERENCE_PATH, REFERENCE_SHA256, 100_000),
    "formula": (FORMULA_PATH, FORMULA_SHA256, 100_000),
    "factorization": (FACTORIZATION_PATH, FACTORIZATION_SHA256, 100_000),
    "member": (MEMBER_PATH, MEMBER_SHA256, 100_000),
    "method": (METHOD_PATH, METHOD_SHA256, 100_000),
    "configuration": (CONFIGURATION_PATH, CONFIGURATION_SHA256, 1_000_000),
    "raw_binding": (RAW_BINDING_PATH, RAW_BINDING_SHA256, 100_000),
    "stationary": (STATIONARY_PATH, STATIONARY_SHA256, 4_000_000),
    "bundle": (BUNDLE_PATH, BUNDLE_SHA256, 2_000_000),
}

HEX_SHA256_RE: Final = re.compile(r"[0-9a-f]{64}\Z")
SAFE_COMPONENT_RE: Final = re.compile(r"[A-Za-z0-9_.+-]+\Z")
MAX_JSON_DEPTH: Final = 48
MAX_INTEGER_BITS: Final = 16_384


class RawFluxVerificationFailure(RuntimeError):
    """Fail-closed scientific validation error."""


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not Fraction
            or type(self.upper) is not Fraction
            or self.lower > self.upper
        ):
            raise RawFluxVerificationFailure("invalid exact interval")

    def plus(self, other: ExactInterval) -> ExactInterval:
        return ExactInterval(self.lower + other.lower, self.upper + other.upper)

    def times_nonnegative(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower < 0:
            raise RawFluxVerificationFailure("nonnegative interval product required")
        return ExactInterval(self.lower * other.lower, self.upper * other.upper)

    def divided_by_positive(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower <= 0:
            raise RawFluxVerificationFailure("positive interval divisor required")
        return ExactInterval(self.lower / other.upper, self.upper / other.lower)

    def reciprocal_positive(self) -> ExactInterval:
        if self.lower <= 0:
            raise RawFluxVerificationFailure("positive reciprocal interval required")
        return ExactInterval(1 / self.upper, 1 / self.lower)

    def intersection(self, other: ExactInterval) -> ExactInterval:
        result = ExactInterval(max(self.lower, other.lower), min(self.upper, other.upper))
        if result.lower > result.upper:
            raise RawFluxVerificationFailure("disjoint interval witnesses")
        return result

    def contains(self, other: ExactInterval) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper


@dataclass(frozen=True, slots=True)
class DirectedInterval:
    lower: Any
    upper: Any
    bits: int

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not gmpy2.mpfr
            or type(self.upper) is not gmpy2.mpfr
            or self.bits not in {PRIMARY_BITS, SENTINEL_BITS, ALTERNATE_BITS}
            or not gmpy2.is_finite(self.lower)
            or not gmpy2.is_finite(self.upper)
            or self.lower > self.upper
        ):
            raise RawFluxVerificationFailure("invalid directed MPFR interval")

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_to_fraction(self.lower), _mpfr_to_fraction(self.upper))


def _strict_path(value: object) -> str:
    if type(value) is not str or unicodedata.normalize("NFC", value) != value:
        raise RawFluxVerificationFailure("report-relative path must be an NFC string")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or not pure.parts
        or pure.as_posix() != value
        or any(
            component in {"", ".", ".."} or SAFE_COMPONENT_RE.fullmatch(component) is None
            for component in pure.parts
        )
    ):
        raise RawFluxVerificationFailure("unsafe or noncanonical report-relative path")
    return value


def _join_relative(parent: str, child: object) -> str:
    parent_value = _strict_path(parent)
    child_value = _strict_path(child)
    joined = (PurePosixPath(parent_value) / PurePosixPath(child_value)).as_posix()
    result = _strict_path(joined)
    parent_parts = PurePosixPath(parent_value).parts
    if PurePosixPath(result).parts[: len(parent_parts)] != parent_parts:
        raise RawFluxVerificationFailure("joined path escaped its pinned root")
    return result


def _snapshot_descriptor(fd: int, cap: int, label: str) -> bytes:
    before = os.fstat(fd)
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_size < 0
        or before.st_size > cap
        or before.st_nlink < 1
    ):
        raise RawFluxVerificationFailure(f"{label} is not an accepted regular file")
    chunks: list[bytes] = []
    remaining = cap + 1
    while remaining:
        chunk = os.read(fd, min(1 << 20, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    data = b"".join(chunks)
    after = os.fstat(fd)
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_nlink,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_nlink,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if len(data) > cap or len(data) != before.st_size or identity_before != identity_after:
        raise RawFluxVerificationFailure(f"{label} changed during descriptor snapshot")
    return data


def _report_snapshot(relative: str, cap: int) -> bytes:
    canonical = _strict_path(relative)
    components = PurePosixPath(canonical).parts
    directory_flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        directory_flags |= os.O_DIRECTORY
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    root_fd = os.open(REPORT, directory_flags | nofollow)
    current_fd = root_fd
    try:
        for component in components[:-1]:
            next_fd = os.open(
                component,
                directory_flags | nofollow,
                dir_fd=current_fd,
            )
            if current_fd != root_fd:
                os.close(current_fd)
            current_fd = next_fd
        file_fd = os.open(
            components[-1],
            os.O_RDONLY | os.O_CLOEXEC | nofollow,
            dir_fd=current_fd,
        )
        try:
            return _snapshot_descriptor(file_fd, cap, canonical)
        finally:
            os.close(file_fd)
    except OSError as error:
        raise RawFluxVerificationFailure(f"cannot snapshot pinned file: {canonical}") from error
    finally:
        if current_fd != root_fd:
            os.close(current_fd)
        os.close(root_fd)


def _selected_artifact_snapshot(path: Path, cap: int = 12_000_000) -> bytes:
    if path == DEFAULT_ARTIFACT:
        return _report_snapshot(
            "artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json",
            cap,
        )
    absolute = Path(os.path.abspath(path))
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, os.O_RDONLY | os.O_CLOEXEC | nofollow)
    except OSError as error:
        raise RawFluxVerificationFailure("cannot open selected artifact") from error
    try:
        return _snapshot_descriptor(descriptor, cap, "selected artifact")
    finally:
        os.close(descriptor)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise RawFluxVerificationFailure("duplicate or non-string JSON object key")
        result[key] = value
    return result


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise RawFluxVerificationFailure("JSON depth cap exceeded")
    if isinstance(value, float):
        raise RawFluxVerificationFailure("JSON floating literals are forbidden")
    if type(value) is bool or value is None:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise RawFluxVerificationFailure("JSON integer magnitude cap exceeded")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise RawFluxVerificationFailure("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise RawFluxVerificationFailure("invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise RawFluxVerificationFailure(
        f"forbidden JSON value type: {type(value).__name__}"
    )


def _canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("ascii")


def _strict_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=lambda token: (_ for _ in ()).throw(
                RawFluxVerificationFailure(f"JSON float forbidden in {label}: {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                RawFluxVerificationFailure(f"JSON constant forbidden in {label}: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RawFluxVerificationFailure(f"invalid ASCII JSON: {label}") from error
    _strict_tree(value)
    if type(value) is not dict or _canonical_bytes(value) != raw:
        raise RawFluxVerificationFailure(f"noncanonical JSON object: {label}")
    return value


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha256(value: object) -> bool:
    return type(value) is str and HEX_SHA256_RE.fullmatch(value) is not None


def _pinned_json(path: str, expected_hash: str, cap: int) -> tuple[dict[str, Any], bytes]:
    if not _is_sha256(expected_hash):
        raise RawFluxVerificationFailure("invalid compiled source digest")
    raw = _report_snapshot(path, cap)
    if _sha256(raw) != expected_hash:
        raise RawFluxVerificationFailure(f"source hash drift: {path}")
    return _strict_json(raw, path), raw


def _fraction(value: object) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise RawFluxVerificationFailure("canonical p/q string required")
    numerator_text, denominator_text = value.split("/")
    if (
        not re.fullmatch(r"0|-?[1-9][0-9]*", numerator_text)
        or not re.fullmatch(r"[1-9][0-9]*", denominator_text)
    ):
        raise RawFluxVerificationFailure("noncanonical p/q lexical form")
    try:
        result = Fraction(int(numerator_text), int(denominator_text))
    except (ValueError, ZeroDivisionError) as error:
        raise RawFluxVerificationFailure("invalid p/q string") from error
    if _fraction_text(result) != value:
        raise RawFluxVerificationFailure("unreduced p/q string")
    return result


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _binary64_fraction(value: object) -> Fraction:
    if type(value) is not str:
        raise RawFluxVerificationFailure("canonical binary64 hexadecimal string required")
    try:
        decoded = float.fromhex(value)
    except ValueError as error:
        raise RawFluxVerificationFailure("invalid binary64 hexadecimal string") from error
    if (
        not math.isfinite(decoded)
        or decoded.hex() != value
        or (decoded == 0.0 and math.copysign(1.0, decoded) < 0)
    ):
        raise RawFluxVerificationFailure("noncanonical finite binary64 string")
    return Fraction.from_float(decoded)


def _interval(value: object) -> ExactInterval:
    if type(value) is not dict or set(value) != {
        "lower_exact_p_over_q",
        "upper_exact_p_over_q",
    }:
        raise RawFluxVerificationFailure("strict exact-interval object required")
    return ExactInterval(
        _fraction(value["lower_exact_p_over_q"]),
        _fraction(value["upper_exact_p_over_q"]),
    )


def _interval_json(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _fraction_text(value.lower),
        "upper_exact_p_over_q": _fraction_text(value.upper),
    }


def _sum_intervals(values: list[ExactInterval]) -> ExactInterval:
    result = ExactInterval(Fraction(0), Fraction(0))
    for value in values:
        result = result.plus(value)
    return result


def _mp_context(bits: int, rounding: int) -> Any:
    return gmpy2.context(
        precision=bits,
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


def _mp_value(value: Fraction, bits: int, rounding: int) -> Any:
    with gmpy2.context(_mp_context(bits, rounding)):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mpfr_to_fraction(value: Any) -> Fraction:
    rational = gmpy2.mpq(value)
    return Fraction(int(rational.numerator), int(rational.denominator))


def _directed_rational(value: Fraction, bits: int) -> DirectedInterval:
    return DirectedInterval(
        _mp_value(value, bits, gmpy2.RoundDown),
        _mp_value(value, bits, gmpy2.RoundUp),
        bits,
    )


def _mp_binary(
    left: Any,
    right: Any,
    bits: int,
    rounding: int,
    operation: str,
) -> Any:
    with gmpy2.context(_mp_context(bits, rounding)):
        if operation == "add":
            return +(left + right)
        if operation == "sub":
            return +(left - right)
        if operation == "mul":
            return +(left * right)
        if operation == "div":
            return +(left / right)
    raise RawFluxVerificationFailure("unknown MPFR operation")


def _directed_product(
    left: DirectedInterval,
    right: DirectedInterval,
) -> DirectedInterval:
    if (
        left.bits != right.bits
        or left.lower < 0
        or right.lower < 0
    ):
        raise RawFluxVerificationFailure("nonnegative MPFR product mismatch")
    bits = left.bits
    return DirectedInterval(
        _mp_binary(left.lower, right.lower, bits, gmpy2.RoundDown, "mul"),
        _mp_binary(left.upper, right.upper, bits, gmpy2.RoundUp, "mul"),
        bits,
    )


def _directed_scale(value: DirectedInterval, factor: Fraction) -> DirectedInterval:
    if factor < 0:
        raise RawFluxVerificationFailure("negative MPFR scale")
    return _directed_product(value, _directed_rational(factor, value.bits))


def _directed_exp(value: Fraction, bits: int) -> DirectedInterval:
    argument = _directed_rational(value, bits)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundDown)):
        lower = +gmpy2.exp(argument.lower)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundUp)):
        upper = +gmpy2.exp(argument.upper)
    return DirectedInterval(lower, upper, bits)


def _registered_positive_bernoulli(value: Fraction, bits: int) -> DirectedInterval:
    if value <= 0:
        raise RawFluxVerificationFailure("positive Bernoulli argument required")
    argument = _directed_rational(value, bits)
    one = _mp_value(Fraction(1), bits, gmpy2.RoundToNearest)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundDown)):
        denominator_lower = +(gmpy2.exp(argument.lower) - one)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundUp)):
        denominator_upper = +(gmpy2.exp(argument.upper) - one)
    if denominator_lower <= 0:
        raise RawFluxVerificationFailure("invalid positive Bernoulli denominator")
    return DirectedInterval(
        _mp_binary(
            argument.lower,
            denominator_upper,
            bits,
            gmpy2.RoundDown,
            "div",
        ),
        _mp_binary(
            argument.upper,
            denominator_lower,
            bits,
            gmpy2.RoundUp,
            "div",
        ),
        bits,
    )


def _registered_bernoulli(value: Fraction, bits: int) -> DirectedInterval:
    if value == 0:
        return _directed_rational(Fraction(1), bits)
    if value > 0:
        return _registered_positive_bernoulli(value, bits)
    magnitude = -value
    return _directed_product(
        _directed_exp(magnitude, bits),
        _registered_positive_bernoulli(magnitude, bits),
    )


def _alternate_positive_bernoulli(value: Fraction, bits: int) -> DirectedInterval:
    """Evaluate B(value) via MPFR expm1 rather than the registered exp-minus-one route."""

    if value <= 0:
        raise RawFluxVerificationFailure("positive alternate Bernoulli argument required")
    argument = _directed_rational(value, bits)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundDown)):
        denominator_lower = +gmpy2.expm1(argument.lower)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundUp)):
        denominator_upper = +gmpy2.expm1(argument.upper)
    if denominator_lower <= 0:
        raise RawFluxVerificationFailure("invalid alternate Bernoulli denominator")
    return DirectedInterval(
        _mp_binary(
            argument.lower,
            denominator_upper,
            bits,
            gmpy2.RoundDown,
            "div",
        ),
        _mp_binary(
            argument.upper,
            denominator_lower,
            bits,
            gmpy2.RoundUp,
            "div",
        ),
        bits,
    )


def _alternate_bernoulli(value: Fraction, bits: int) -> DirectedInterval:
    """Independent algebraic route for B(s), including negative s."""

    if value == 0:
        return _directed_rational(Fraction(1), bits)
    if value > 0:
        return _alternate_positive_bernoulli(value, bits)
    magnitude = -value
    argument = _directed_rational(-magnitude, bits)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundDown)):
        exponential_lower = +gmpy2.exp(argument.lower)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundUp)):
        exponential_upper = +gmpy2.exp(argument.upper)
    one_down = _mp_value(Fraction(1), bits, gmpy2.RoundDown)
    one_up = _mp_value(Fraction(1), bits, gmpy2.RoundUp)
    denominator_lower = _mp_binary(
        one_down,
        exponential_upper,
        bits,
        gmpy2.RoundDown,
        "sub",
    )
    denominator_upper = _mp_binary(
        one_up,
        exponential_lower,
        bits,
        gmpy2.RoundUp,
        "sub",
    )
    if denominator_lower <= 0:
        raise RawFluxVerificationFailure("invalid negative alternate Bernoulli denominator")
    positive_argument = _directed_rational(magnitude, bits)
    return DirectedInterval(
        _mp_binary(
            positive_argument.lower,
            denominator_upper,
            bits,
            gmpy2.RoundDown,
            "div",
        ),
        _mp_binary(
            positive_argument.upper,
            denominator_lower,
            bits,
            gmpy2.RoundUp,
            "div",
        ),
        bits,
    )


def _formula_mu(
    potential: Fraction,
    volume: Fraction,
    bits: int,
) -> ExactInterval:
    return _directed_scale(_directed_exp(-potential, bits), volume).exact()


def _formula_rate(
    delta: Fraction,
    diffusion: Fraction,
    origin_volume: Fraction,
    distance: Fraction,
    bits: int,
    *,
    alternate: bool = False,
) -> ExactInterval:
    if diffusion <= 0 or origin_volume <= 0 or distance <= 0:
        raise RawFluxVerificationFailure("invalid Scharfetter-Gummel parameters")
    bernoulli = (
        _alternate_bernoulli(delta, bits)
        if alternate
        else _registered_bernoulli(delta, bits)
    )
    return _directed_scale(
        bernoulli,
        diffusion / (origin_volume * distance),
    ).exact()


def _formula_kappa(
    potential: Fraction,
    delta: Fraction,
    diffusion: Fraction,
    distance: Fraction,
    bits: int,
    *,
    alternate: bool = False,
) -> ExactInterval:
    if diffusion <= 0 or distance <= 0:
        raise RawFluxVerificationFailure("invalid common-flux parameters")
    bernoulli = (
        _alternate_bernoulli(delta, bits)
        if alternate
        else _registered_bernoulli(delta, bits)
    )
    return _directed_scale(
        _directed_product(_directed_exp(-potential, bits), bernoulli),
        diffusion / distance,
    ).exact()


def _modulo(value: Fraction, width: Fraction) -> Fraction:
    if width <= 0:
        raise RawFluxVerificationFailure("positive periodic width required")
    return value - (value // width) * width


def _independent_partition(
    coordinate: str,
    axis: dict[str, Any],
    periodic_start: Fraction,
    periodic_width: Fraction,
) -> dict[str, Any]:
    """Reconstruct an exact partition only from the configuration authority."""

    if type(axis) is not dict:
        raise RawFluxVerificationFailure("configuration axis must be an object")
    size = axis.get("size")
    alignment = axis.get("alignment")
    if (
        type(size) is not int
        or isinstance(size, bool)
        or size < 2
        or type(alignment) is not str
    ):
        raise RawFluxVerificationFailure("invalid configuration axis cardinality")

    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        if set(axis) != {"alignment", "lower_binary64_hex", "size", "upper_binary64_hex"}:
            raise RawFluxVerificationFailure("reflecting configuration-axis schema drift")
        lower = _binary64_fraction(axis["lower_binary64_hex"])
        upper = _binary64_fraction(axis["upper_binary64_hex"])
        if lower >= upper:
            raise RawFluxVerificationFailure("invalid reflecting interval")
        domain_start = lower
        domain_width = upper - lower
        periodic = False
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            step = domain_width / size
            positions = [
                lower + (Fraction(index) + Fraction(1, 2)) * step
                for index in range(size)
            ]
            cells = [
                [(lower + index * step, lower + (index + 1) * step)]
                for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = domain_width / (size - 1)
            positions = [lower + index * step for index in range(size)]
            boundaries = [lower]
            boundaries.extend(
                lower + (Fraction(index) - Fraction(1, 2)) * step
                for index in range(1, size)
            )
            boundaries.append(upper)
            cells = [
                [(boundaries[index], boundaries[index + 1])]
                for index in range(size)
            ]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
    elif alignment in {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    }:
        if set(axis) != {"alignment", "periodic_shift_exact", "size"}:
            raise RawFluxVerificationFailure("periodic configuration-axis schema drift")
        if coordinate != "relative_perpendicular":
            raise RawFluxVerificationFailure("periodic alignment assigned to wrong coordinate")
        if periodic_width <= 0:
            raise RawFluxVerificationFailure("invalid periodic domain")
        step = periodic_width / size
        shift = _fraction(axis["periodic_shift_exact"])
        expected_shift = (
            Fraction(0)
            if alignment == "cell_centred_periodic_base"
            else step / 2
        )
        if shift != expected_shift:
            raise RawFluxVerificationFailure("periodic half-shift mismatch")
        domain_start = periodic_start
        domain_width = periodic_width
        domain_end = domain_start + domain_width
        periodic = True
        positions = [
            domain_start
            + _modulo(
                (Fraction(index) + Fraction(1, 2)) * step + shift,
                domain_width,
            )
            for index in range(size)
        ]
        cells: list[list[tuple[Fraction, Fraction]]] = []
        for index in range(size):
            start = domain_start + _modulo(index * step + shift, domain_width)
            end = start + step
            if end <= domain_end:
                cells.append([(start, end)])
            else:
                cells.append(
                    [
                        (start, domain_end),
                        (domain_start, domain_start + end - domain_end),
                    ]
                )
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment == "cell_centred_periodic_base"
            else "cell_centred_periodic_diffusion_half_shift"
        )
    else:
        raise RawFluxVerificationFailure("unknown axis alignment")

    volumes = [
        sum(
            (upper - lower for lower, upper in cell),
            Fraction(0),
        )
        for cell in cells
    ]
    if any(volume <= 0 for volume in volumes):
        raise RawFluxVerificationFailure("nonpositive reconstructed cell")
    return {
        "cell_segments_exact": [
            [
                [_fraction_text(lower), _fraction_text(upper)]
                for lower, upper in cell
            ]
            for cell in cells
        ],
        "cell_volumes_exact": [_fraction_text(volume) for volume in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _fraction_text(domain_start),
        "domain_width_exact": _fraction_text(domain_width),
        "periodic": periodic,
        "periodic_shift_exact": _fraction_text(shift),
        "positions_exact": [_fraction_text(position) for position in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def _decode_binary64_intervals(
    raw: bytes,
    *,
    count: int,
    label: str,
) -> list[ExactInterval]:
    if len(raw) != 16 * count:
        raise RawFluxVerificationFailure(f"binary interval byte count mismatch: {label}")
    result: list[ExactInterval] = []
    for lower, upper in struct.iter_unpack(">dd", raw):
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower < 0
            or lower > upper
            or (lower == 0.0 and math.copysign(1.0, lower) < 0)
            or (upper == 0.0 and math.copysign(1.0, upper) < 0)
        ):
            raise RawFluxVerificationFailure(f"invalid stored interval: {label}")
        result.append(
            ExactInterval(Fraction.from_float(lower), Fraction.from_float(upper))
        )
    if len(result) != count:
        raise RawFluxVerificationFailure(f"binary interval record mismatch: {label}")
    return result


def _inventory_map(bundle: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    inventory = bundle.get("file_inventory")
    if type(inventory) is not list or len(inventory) != 206:
        raise RawFluxVerificationFailure("production inventory cardinality drift")
    entries: dict[str, dict[str, Any]] = {}
    payloads: dict[str, bytes] = {}
    ordered_paths: list[str] = []
    for entry in inventory:
        if type(entry) is not dict or set(entry) != {"byte_length", "path", "sha256"}:
            raise RawFluxVerificationFailure("invalid production inventory entry")
        path = _strict_path(entry["path"])
        digest = entry["sha256"]
        byte_length = entry["byte_length"]
        if (
            HEX_SHA256_RE.fullmatch(digest) is None
            or type(byte_length) is not int
            or isinstance(byte_length, bool)
            or byte_length < 0
            or byte_length > 1_000_000
            or path in entries
        ):
            raise RawFluxVerificationFailure("invalid or duplicate inventory identity")
        relative = _join_relative(BUNDLE_ROOT, path)
        raw = _report_snapshot(relative, byte_length)
        if len(raw) != byte_length or _sha256(raw) != digest:
            raise RawFluxVerificationFailure(f"inventory file drift: {path}")
        entries[path] = entry
        payloads[path] = raw
        ordered_paths.append(path)
    if ordered_paths != sorted(ordered_paths):
        raise RawFluxVerificationFailure("production inventory is not canonically sorted")
    return entries, payloads


def _manifest_file(
    *,
    axis_entry: dict[str, Any],
    coordinate: str,
    role: str,
    count: int,
    inventory: dict[str, dict[str, Any]],
    payloads: dict[str, bytes],
) -> tuple[list[ExactInterval], dict[str, str], str]:
    rates = axis_entry.get("rates")
    if type(rates) is not dict or set(rates) != {"backward", "forward", "stationary_mass"}:
        raise RawFluxVerificationFailure("axis rates schema drift")
    binding = rates.get(role)
    if type(binding) is not dict or set(binding) != {"file", "manifest"}:
        raise RawFluxVerificationFailure("raw role binding schema drift")
    file_entry = binding["file"]
    manifest = binding["manifest"]
    if (
        type(file_entry) is not dict
        or set(file_entry) != {"byte_length", "path", "sha256"}
        or type(manifest) is not dict
    ):
        raise RawFluxVerificationFailure("raw file/manifest schema drift")
    path = _strict_path(file_entry["path"])
    digest = file_entry["sha256"]
    byte_length = file_entry["byte_length"]
    expected_manifest = {
        "byte_order": "big",
        "logical_shape": [count],
        "raw_byte_length": byte_length,
        "raw_sha256": digest,
        "record_count": count,
        "record_format": ">dd",
        "role": f"control_free_axis_{coordinate}_{role}",
        "schema": "encounter_big_endian_binary64_interval_file_v1",
    }
    if (
        file_entry != inventory.get(path)
        or manifest != expected_manifest
        or type(byte_length) is not int
        or isinstance(byte_length, bool)
        or byte_length != 16 * count
        or HEX_SHA256_RE.fullmatch(digest) is None
    ):
        raise RawFluxVerificationFailure("raw file inventory/manifest mismatch")
    raw = payloads.get(path)
    if raw is None or _sha256(raw) != digest:
        raise RawFluxVerificationFailure("raw file payload is absent from inventory snapshot")
    return (
        _decode_binary64_intervals(raw, count=count, label=path),
        {"path": path, "sha256": digest},
        path,
    )


def _metric_relative_width(
    enclosure: ExactInterval,
    reference: ExactInterval,
) -> Fraction:
    if reference.lower <= 0:
        raise RawFluxVerificationFailure("positive reference required for relative width")
    return (enclosure.upper - enclosure.lower) / reference.lower


def _metric_relative_margin(
    enclosure: ExactInterval,
    witness: ExactInterval,
) -> Fraction:
    if witness.upper <= 0 or not enclosure.contains(witness):
        raise RawFluxVerificationFailure("positive contained witness required for margin")
    return min(
        witness.lower - enclosure.lower,
        enclosure.upper - witness.upper,
    ) / witness.upper


def _update_maximum(
    current: tuple[Fraction, str] | None,
    value: Fraction,
    location: str,
) -> tuple[Fraction, str]:
    if current is None or value > current[0]:
        return (value, location)
    return current


def _update_minimum(
    current: tuple[Fraction, str] | None,
    value: Fraction,
    location: str,
) -> tuple[Fraction, str]:
    if current is None or value < current[0]:
        return (value, location)
    return current


def _metric_json(value: tuple[Fraction, str] | None) -> dict[str, str]:
    if value is None:
        raise RawFluxVerificationFailure("summary metric was not populated")
    return {
        "location": value[1],
        "value_exact_p_over_q": _fraction_text(value[0]),
    }


def _digest_stream(domain: bytes) -> Any:
    if not domain.endswith(b"\0"):
        raise RawFluxVerificationFailure("digest domain must be NUL terminated")
    result = hashlib.sha256()
    result.update(domain)
    return result


def _digest_update(stream: Any, value: Any) -> None:
    stream.update(_canonical_bytes(value))


def _domain_digest(domain: bytes, value: Any) -> str:
    if not domain.endswith(b"\0"):
        raise RawFluxVerificationFailure("digest domain must be NUL terminated")
    return _sha256(domain + _canonical_bytes(value))


def _require_false_map(value: Any, keys: set[str], label: str) -> None:
    if (
        type(value) is not dict
        or set(value) != keys
        or any(value[key] is not False for key in keys)
    ):
        raise RawFluxVerificationFailure(
            f"{label} claim boundary must be an exact all-false map"
        )


def _verify_declared_pins(source: dict[str, Any], label: str) -> None:
    pins = source.get("source_pins")
    if pins is None:
        return
    if type(pins) is not dict:
        raise RawFluxVerificationFailure(f"{label} source_pins must be an object")
    for role, binding in pins.items():
        if (
            type(role) is not str
            or type(binding) is not dict
            or set(binding) != {"path", "sha256"}
        ):
            raise RawFluxVerificationFailure(f"invalid declared pin in {label}")
        path = _strict_path(binding["path"])
        digest = binding["sha256"]
        if HEX_SHA256_RE.fullmatch(digest) is None:
            raise RawFluxVerificationFailure(f"invalid declared digest in {label}")
        raw = _report_snapshot(path, 16_000_000)
        if _sha256(raw) != digest:
            raise RawFluxVerificationFailure(
                f"declared source pin drift: {label}.{role}"
            )


def _assert_authority_semantics(sources: dict[str, dict[str, Any]]) -> None:
    expected_schemas = {
        "reference": "encounter_continuum_c1_reference_density_source_v1",
        "formula": "encounter_continuum_c1_ideal_formula_source_v1",
        "factorization": "encounter_continuum_c1_factorization_source_v1",
        "member": "encounter_continuum_c1_c2_fixed_row_member_spec_v1",
        "method": "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1",
        "configuration": "encounter_physical_configuration_family_control_free_v1",
        "raw_binding": "encounter_continuum_c1_raw_axis_production_binding_v1",
        "stationary": "encounter_continuum_c1_stationary_integral_source_v1",
        "bundle": "encounter_control_free_production_initial_stream_v1",
    }
    for role, schema in expected_schemas.items():
        if sources[role].get("schema") != schema:
            raise RawFluxVerificationFailure(f"{role} authority schema drift")

    _require_false_map(
        sources["reference"].get("claim_boundary"),
        {
            "box_truncation_proved",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "complete_C3",
            "continuum_topology_proved",
            "production_bridge_accepted",
            "release_eligible",
        },
        "reference",
    )
    _require_false_map(
        sources["formula"].get("claim_boundary"),
        {
            "binary64_centres_define_ideal_member",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "every_interval_endpoint_combination_is_a_model",
            "production_bridge_accepted",
            "release_eligible",
        },
        "ideal formula",
    )
    _require_false_map(
        sources["factorization"].get("claim_boundary"),
        {
            "budget_present",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "concrete_killing_constructed",
            "control_values_present",
            "production_bridge_accepted",
            "release_eligible",
        },
        "factorization",
    )
    _require_false_map(
        sources["member"].get("claim_boundary"),
        {
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "genuine_refinement_sequence_present",
            "production_bridge_accepted",
            "release_eligible",
        },
        "member specification",
    )
    _require_false_map(
        sources["method"].get("claim_boundary"),
        {
            "backend_independence_claimed",
            "complete_C1",
            "complete_C2",
            "formal_production_bridge_accepted",
            "release_eligible",
        },
        "method registry",
    )
    _require_false_map(
        sources["raw_binding"].get("claim_boundary"),
        {
            "common_flux_recomputed",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "formal_production_bridge_accepted",
            "formula_containment_recomputed",
            "physical_stationary_integrals_present",
            "release_eligible",
            "same_correlated_member_certified",
        },
        "raw production binding",
    )
    _require_false_map(
        sources["stationary"].get("claim_boundary"),
        {
            "backend_independence_claimed",
            "box_conditionally_renormalized",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "complete_C3",
            "formal_production_bridge_accepted",
            "genuine_refinement_sequence_present",
            "one_correlated_distinguished_ideal_member_is_contained",
            "release_eligible",
        },
        "stationary integral source",
    )

    anti_vacuity_binding = sources["raw_binding"]["source_pins"].get(
        "anti_vacuity_policy"
    )
    if (
        type(anti_vacuity_binding) is not dict
        or set(anti_vacuity_binding) != {"path", "sha256"}
        or not _is_sha256(anti_vacuity_binding.get("sha256"))
    ):
        raise RawFluxVerificationFailure("anti-vacuity policy binding drift")
    anti_vacuity, _ = _pinned_json(
        _strict_path(anti_vacuity_binding["path"]),
        anti_vacuity_binding["sha256"],
        100_000,
    )
    _require_false_map(
        anti_vacuity.get("claim_boundary"),
        {
            "complete_C1",
            "complete_C2",
            "formal_production_bridge_accepted",
            "policy_predecessor_order_independently_sealed",
            "release_eligible",
        },
        "anti-vacuity policy",
    )
    if anti_vacuity.get("requirements") != {
        "all_box_mass_and_gauge_denominator_lowers_strictly_positive": True,
        "all_common_flux_forward_reverse_intersections_nonempty": True,
        "all_formula_values_contained_by_saved_raw_intervals": True,
        "all_map_ratio_interval_lowers_strictly_positive": True,
        "every_configuration_and_axis_present_exactly_once": True,
        "maximum_gauge_relative_width": "1/1099511627776",
        "maximum_map_anchor_constant": "1000000/1",
        "maximum_reconstructed_killing_anchor_constant": "1000000/1",
        "maximum_reference_cell_mass_relative_width": "1/1099511627776",
        "maximum_stationary_axis_relative_width": "1/1099511627776",
        "minimum_configuration_count": 12,
    }:
        raise RawFluxVerificationFailure("anti-vacuity pilot requirements drift")

    formulae = sources["formula"].get("formulae")
    semantics = sources["formula"].get("member_semantics")
    if (
        type(formulae) is not dict
        or formulae.get("ideal_axis_mass")
        != "mu_i=cell_volume_i*exp(-potential(representative_i))"
        or formulae.get("reflecting_sg_rate")
        != (
            "q_i_to_j=D_axis/(cell_volume_i*distance_ij)*"
            "Bernoulli(potential_j-potential_i)"
        )
        or formulae.get("periodic_rate") != "q=D_axis/(cell_width^2)"
        or formulae.get("global_gauge")
        != "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)"
        or formulae.get("tensor_gauged_mass") != "pi_h_tensor=G*product_axis_mu"
        or type(semantics) is not dict
        or semantics.get("common_flux_uses_one_formula_defined_exact_value") is not True
        or semantics.get("one_correlated_distinguished_member_required") is not True
        or semantics.get("formula_defined_member_is_independent_of_production_centres")
        is not True
    ):
        raise RawFluxVerificationFailure("ideal formula semantics drift")

    normalization = sources["reference"].get("normalization")
    if (
        type(normalization) is not dict
        or normalization.get("conditional_box_renormalization_used") is not False
        or normalization.get("restricted_density_retains_global_normalization") is not True
        or normalization.get("periodic_factor") != "1/W"
    ):
        raise RawFluxVerificationFailure("reference normalization semantics drift")

    member_semantics = sources["member"].get("member_semantics")
    if (
        type(member_semantics) is not dict
        or member_semantics.get("configuration_count") != 12
        or member_semantics.get("configuration_rows_are_finite_anchors") is not True
        or member_semantics.get("coordinate_order") != list(COORDINATES)
        or member_semantics.get(
            "every_cartesian_interval_endpoint_combination_is_a_model"
        )
        is not False
        or member_semantics.get(
            "one_formula_defined_correlated_member_per_configuration"
        )
        is not True
        or member_semantics.get("scalar_convention")
        != "complex_inner_product_conjugate_first_factor"
    ):
        raise RawFluxVerificationFailure("member anti-smuggling semantics drift")

    methods = sources["method"].get("methods")
    if type(methods) is not list:
        raise RawFluxVerificationFailure("method registry is not a list")
    method_by_id: dict[str, dict[str, Any]] = {}
    for row in methods:
        if type(row) is not dict or type(row.get("method_id")) is not str:
            raise RawFluxVerificationFailure("invalid method registry row")
        method_id = row["method_id"]
        if method_id in method_by_id:
            raise RawFluxVerificationFailure("duplicate method registry id")
        method_by_id[method_id] = row
    for method_id, bits in (
        ("directed_mpfr_320_reference_density_v1", PRIMARY_BITS),
        ("directed_mpfr_640_reference_density_sentinel_v1", SENTINEL_BITS),
    ):
        row = method_by_id.get(method_id)
        if (
            row is None
            or row.get("precision_bits") != bits
            or row.get("rounding_mode") != "directed_RoundDown_RoundUp"
            or row.get("special_function_backend_and_version")
            != "gmpy2_2.2.1_MPFR_4.2.1"
        ):
            raise RawFluxVerificationFailure("registered MPFR method drift")
    if (
        method_by_id.get("binary64_interval_decode_v1", {}).get("rounding_mode")
        != "stored_outward_endpoints"
        or method_by_id.get("exact_rational_tensor_factorization_v1", {}).get(
            "rounding_mode"
        )
        != "exact"
    ):
        raise RawFluxVerificationFailure("registered exact/decode method drift")

    bundle_flags = sources["bundle"].get("flags")
    if (
        type(bundle_flags) is not dict
        or bundle_flags.get("authorizes_scientific_execution") is not False
        or bundle_flags.get("contains_budget_value") is not False
        or bundle_flags.get("contains_control_values") is not False
        or bundle_flags.get("full_operator_bound") is not False
        or bundle_flags.get("killing_contact_geometry_bound") is not False
        or bundle_flags.get("positive_budget_executed") is not False
        or bundle_flags.get("science_executed") is not False
        or bundle_flags.get("topology_complete") is not False
    ):
        raise RawFluxVerificationFailure("production-bundle scope boundary drift")

    for role, source in sources.items():
        if role not in {"configuration", "bundle"}:
            _verify_declared_pins(source, role)


def _source_binding(
    source: dict[str, Any],
    container: str,
    role: str,
    path: str,
    digest: str,
) -> bool:
    bindings = source.get(container)
    return type(bindings) is dict and bindings.get(role) == {
        "path": path,
        "sha256": digest,
    }


def _validate_cross_bindings(sources: dict[str, dict[str, Any]]) -> None:
    raw_binding = sources["raw_binding"]
    stationary = sources["stationary"]
    member = sources["member"]
    reference = sources["reference"]

    required = (
        _source_binding(
            raw_binding,
            "source_pins",
            "ideal_formula_source",
            FORMULA_PATH,
            FORMULA_SHA256,
        ),
        _source_binding(
            raw_binding,
            "source_pins",
            "member_spec",
            MEMBER_PATH,
            MEMBER_SHA256,
        ),
        _source_binding(
            raw_binding,
            "source_pins",
            "method_registry",
            METHOD_PATH,
            METHOD_SHA256,
        ),
        _source_binding(
            raw_binding,
            "source_pins",
            "production_bundle",
            BUNDLE_PATH,
            BUNDLE_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "configuration_source",
            CONFIGURATION_PATH,
            CONFIGURATION_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "ideal_formula_source",
            FORMULA_PATH,
            FORMULA_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "member_spec",
            MEMBER_PATH,
            MEMBER_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "method_registry",
            METHOD_PATH,
            METHOD_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "production_partition_bundle",
            BUNDLE_PATH,
            BUNDLE_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "raw_axis_binding",
            RAW_BINDING_PATH,
            RAW_BINDING_SHA256,
        ),
        _source_binding(
            stationary,
            "source_pins",
            "reference_density_source",
            REFERENCE_PATH,
            REFERENCE_SHA256,
        ),
        _source_binding(
            member,
            "role_bindings",
            "configuration_source",
            CONFIGURATION_PATH,
            CONFIGURATION_SHA256,
        ),
        _source_binding(
            member,
            "role_bindings",
            "factorization_source",
            FACTORIZATION_PATH,
            FACTORIZATION_SHA256,
        ),
        _source_binding(
            member,
            "role_bindings",
            "ideal_formula_source",
            FORMULA_PATH,
            FORMULA_SHA256,
        ),
        _source_binding(
            member,
            "role_bindings",
            "reference_density_source",
            REFERENCE_PATH,
            REFERENCE_SHA256,
        ),
        _source_binding(
            reference,
            "source_pins",
            "configuration_source",
            CONFIGURATION_PATH,
            CONFIGURATION_SHA256,
        ),
    )
    if not all(required):
        raise RawFluxVerificationFailure("cross-authority source binding drift")

    configuration_binding = raw_binding.get("configuration_binding")
    raw_roles = raw_binding.get("raw_role_binding")
    if configuration_binding != {
        "authority_join_key": "authority_label",
        "configuration_count": 12,
        "production_join_key": "configuration_label",
        "semantic_mapping_source": "configuration_semantic_ids",
        "strict_join_rule": (
            "configuration_label_equals_authority_label_exactly_once_in_each_source"
        ),
    }:
        raise RawFluxVerificationFailure("raw binding join semantics drift")
    if raw_roles != {
        "axis_order": list(COORDINATES),
        "partition_role": "exact_cell_geometry_and_representatives",
        "rate_roles": ["forward", "backward"],
        "saved_interval_record_format": ">dd",
        "saved_stationary_mass_role": (
            "ungauged_axis_primitive_mu_not_physical_cell_integral"
        ),
        "tensor_storage_order": (
            "C:midpoint_outer_relative_parallel_middle_transverse_inner"
        ),
    }:
        raise RawFluxVerificationFailure("raw role semantics drift")


def _expected_artifact() -> tuple[dict[str, Any], dict[str, int]]:
    if (
        gmpy2.__version__ != "2.2.1"
        or gmpy2.mpfr_version() != "MPFR 4.2.1"
        or gmpy2.mp_version() != "GMP 6.3.0"
        or gmpy2.mpc_version() != "MPC 1.3.1"
    ):
        raise RawFluxVerificationFailure("authenticated arithmetic runtime version drift")

    sources: dict[str, dict[str, Any]] = {}
    source_raw: dict[str, bytes] = {}
    for role, (path, digest, cap) in PINNED_JSON.items():
        source, raw = _pinned_json(path, digest, cap)
        sources[role] = source
        source_raw[role] = raw
    _assert_authority_semantics(sources)
    _validate_cross_bindings(sources)

    builder_raw = _report_snapshot(BUILDER_PATH, 1_000_000)
    if _sha256(builder_raw) != BUILDER_SHA256:
        raise RawFluxVerificationFailure("raw-flux builder source pin drift")

    reference = sources["reference"]
    formula = sources["formula"]
    configuration = sources["configuration"]
    member = sources["member"]
    stationary = sources["stationary"]
    bundle = sources["bundle"]

    inventory, inventory_payloads = _inventory_map(bundle)
    if (
        bundle.get("configuration_count") != 12
        or bundle.get("configuration_sha256") != CONFIGURATION_SHA256
        or bundle.get("total_state_workload") != 34_787_462
        or bundle.get("total_dense_expansion_byte_length") != 556_599_392
    ):
        raise RawFluxVerificationFailure("production-bundle identity drift")
    request_configuration = inventory.get("request/configuration.json")
    if (
        request_configuration
        != {
            "byte_length": len(source_raw["configuration"]),
            "path": "request/configuration.json",
            "sha256": CONFIGURATION_SHA256,
        }
        or inventory_payloads.get("request/configuration.json")
        != source_raw["configuration"]
    ):
        raise RawFluxVerificationFailure("bundle request/configuration snapshot drift")

    initial_geometry = configuration.get("initial_geometry")
    if type(initial_geometry) is not dict:
        raise RawFluxVerificationFailure("initial geometry binding missing")
    analytic_path = _strict_path(initial_geometry.get("source_path"))
    analytic_digest = initial_geometry.get("source_sha256")
    analytic_inventory = inventory.get("request/analytic_source.json")
    if (
        HEX_SHA256_RE.fullmatch(analytic_digest) is None
        or bundle.get("analytic_source_sha256") != analytic_digest
        or analytic_inventory
        != {
            "byte_length": len(inventory_payloads["request/analytic_source.json"]),
            "path": "request/analytic_source.json",
            "sha256": analytic_digest,
        }
        or _sha256(inventory_payloads["request/analytic_source.json"]) != analytic_digest
        or _report_snapshot(analytic_path, 1_000_000)
        != inventory_payloads["request/analytic_source.json"]
    ):
        raise RawFluxVerificationFailure("analytic-source production snapshot drift")

    dynamics = configuration.get("dynamics")
    parameters = reference.get("physical_parameter_bundle")
    if type(dynamics) is not dict or type(parameters) is not dict:
        raise RawFluxVerificationFailure("physical parameter bundle missing")
    expected_parameter_projection = {
        "ou_mean_binary64_hex": dynamics.get("ou_mean_binary64_hex"),
        "ou_stiffness_binary64_hex": dynamics.get("ou_stiffness_binary64_hex"),
        "particle_diffusion_binary64_hex": dynamics.get(
            "particle_diffusion_binary64_hex"
        ),
        "physical_dimension": configuration.get("physical_dimension"),
        "quotient_dimension": configuration.get("quotient_dimension"),
        "transverse_period_exact": dynamics.get("transverse_period_exact"),
    }
    if parameters != expected_parameter_projection:
        raise RawFluxVerificationFailure("reference/configuration parameter mismatch")
    diffusion = _binary64_fraction(parameters["particle_diffusion_binary64_hex"])
    stiffness = _binary64_fraction(parameters["ou_stiffness_binary64_hex"])
    mean = _binary64_fraction(parameters["ou_mean_binary64_hex"])
    periodic_start = _fraction(dynamics.get("transverse_domain_start_exact"))
    periodic_width = _fraction(parameters["transverse_period_exact"])
    if diffusion <= 0 or stiffness <= 0 or periodic_width <= 0:
        raise RawFluxVerificationFailure("nonpositive physical parameter")
    axis_diffusions = {
        "midpoint": diffusion / 2,
        "relative_parallel": 2 * diffusion,
        "relative_perpendicular": 2 * diffusion,
    }
    expected_potentials = {
        "midpoint": "ou_stiffness*(x-ou_mean)^2/particle_diffusion",
        "relative_parallel": "ou_stiffness*x^2/(4*particle_diffusion)",
        "relative_perpendicular": "0/1",
    }
    if (
        reference.get("coordinate_order") != list(COORDINATES)
        or configuration.get("coordinate_order") != list(COORDINATES)
        or formula.get("potential_formulae") != expected_potentials
    ):
        raise RawFluxVerificationFailure("coordinate/potential authority drift")

    config_rows = configuration.get("configurations")
    bundle_rows = bundle.get("rows")
    stationary_rows = stationary.get("rows")
    member_order = member.get("configuration_order")
    mappings = member.get("configuration_semantic_ids")
    configuration_order = configuration.get("configuration_order")
    if (
        type(config_rows) is not list
        or type(bundle_rows) is not list
        or type(stationary_rows) is not list
        or type(member_order) is not list
        or type(mappings) is not list
        or type(configuration_order) is not list
        or any(
            len(value) != 12
            for value in (
                config_rows,
                bundle_rows,
                stationary_rows,
                member_order,
                mappings,
                configuration_order,
            )
        )
        or member_order != configuration_order
        or configuration.get("configuration_count") != 12
    ):
        raise RawFluxVerificationFailure("fixed 12-row authority cardinality drift")

    mapping_by_label: dict[str, dict[str, Any]] = {}
    for mapping in mappings:
        if (
            type(mapping) is not dict
            or set(mapping)
            != {
                "authority_label",
                "refinement_family_id",
                "refinement_member_id",
            }
            or type(mapping.get("authority_label")) is not str
            or type(mapping.get("refinement_family_id")) is not str
            or type(mapping.get("refinement_member_id")) is not str
        ):
            raise RawFluxVerificationFailure("invalid semantic member mapping")
        label = mapping["authority_label"]
        if label in mapping_by_label:
            raise RawFluxVerificationFailure("duplicate semantic member label")
        mapping_by_label[label] = mapping
    if set(mapping_by_label) != set(member_order):
        raise RawFluxVerificationFailure("semantic member/order mismatch")

    parameter_digest = _domain_digest(
        b"encounter-fixed-row-physical-parameter-bundle-v1\0",
        {
            "physical_parameter_bundle": parameters,
            "unit_table": reference.get("unit_table"),
        },
    )
    role_bindings = member["role_bindings"]

    output_rows: list[dict[str, Any]] = []
    used_row_paths: set[str] = set()
    used_partition_paths: set[str] = set()
    used_raw_paths: set[str] = set()
    cell_count = 0
    edge_count = 0
    rate_count = 0
    positive_rate_count = 0
    zero_boundary_rate_count = 0
    maximum_mu_width: tuple[Fraction, str] | None = None
    maximum_rate_width: tuple[Fraction, str] | None = None
    maximum_flux_width: tuple[Fraction, str] | None = None
    minimum_mu_margin: tuple[Fraction, str] | None = None
    minimum_rate_margin: tuple[Fraction, str] | None = None
    minimum_kappa_margin: tuple[Fraction, str] | None = None

    for index, (config_row, bundle_row, stationary_row) in enumerate(
        zip(config_rows, bundle_rows, stationary_rows, strict=True)
    ):
        if (
            type(config_row) is not dict
            or type(bundle_row) is not dict
            or type(stationary_row) is not dict
        ):
            raise RawFluxVerificationFailure("invalid fixed-row object")
        label = config_row.get("label")
        expected_states = config_row.get("expected_states")
        shape = config_row.get("shape")
        if (
            type(label) is not str
            or label != member_order[index]
            or type(expected_states) is not int
            or isinstance(expected_states, bool)
            or type(shape) is not list
            or len(shape) != 3
            or any(type(value) is not int or isinstance(value, bool) for value in shape)
            or math.prod(shape) != expected_states
            or bundle_row.get("configuration_index") != index
            or bundle_row.get("configuration_label") != label
            or bundle_row.get("expected_states") != expected_states
            or stationary_row.get("configuration_index") != index
            or stationary_row.get("configuration_label") != label
            or stationary_row.get("tensor_state_count") != expected_states
        ):
            raise RawFluxVerificationFailure("row label/order/state identity drift")
        mapping = mapping_by_label[label]
        if (
            stationary_row.get("refinement_family_id")
            != mapping["refinement_family_id"]
            or stationary_row.get("refinement_member_id")
            != mapping["refinement_member_id"]
        ):
            raise RawFluxVerificationFailure("stationary/member semantic mapping drift")

        row_binding = bundle_row.get("row_manifest")
        if (
            type(row_binding) is not dict
            or set(row_binding) != {"byte_length", "path", "sha256"}
        ):
            raise RawFluxVerificationFailure("row manifest binding schema drift")
        row_path = _strict_path(row_binding["path"])
        if (
            row_path in used_row_paths
            or row_binding != inventory.get(row_path)
            or HEX_SHA256_RE.fullmatch(row_binding["sha256"]) is None
        ):
            raise RawFluxVerificationFailure("row manifest inventory/path reuse drift")
        used_row_paths.add(row_path)
        row_manifest = _strict_json(inventory_payloads[row_path], row_path)
        if (
            row_manifest.get("schema")
            != "encounter_control_free_production_initial_row_v1"
            or row_manifest.get("configuration_index") != index
            or row_manifest.get("configuration_label") != label
            or row_manifest.get("configuration_sha256") != CONFIGURATION_SHA256
            or row_manifest.get("expected_states") != expected_states
            or row_manifest.get("row_relation_sha256")
            != bundle_row.get("row_relation_sha256")
        ):
            raise RawFluxVerificationFailure("row manifest identity drift")
        axes = row_manifest.get("axes")
        stationary_axes = stationary_row.get("axes")
        if (
            type(axes) is not list
            or type(stationary_axes) is not list
            or len(axes) != 3
            or len(stationary_axes) != 3
        ):
            raise RawFluxVerificationFailure("row axis cardinality drift")

        partition_hashes: list[str] = []
        row_axis_outputs: list[dict[str, Any]] = []
        row_axis_sums: list[ExactInterval] = []
        row_axis_factor_ranges: list[ExactInterval] = []

        for axis_index, (coordinate, axis_entry, stationary_axis) in enumerate(
            zip(COORDINATES, axes, stationary_axes, strict=True)
        ):
            if (
                type(axis_entry) is not dict
                or type(stationary_axis) is not dict
                or axis_entry.get("coordinate") != coordinate
                or stationary_axis.get("coordinate") != coordinate
                or config_row.get(coordinate) is None
                or shape[axis_index] != config_row[coordinate].get("size")
            ):
                raise RawFluxVerificationFailure("axis orientation/order drift")
            partition_binding = axis_entry.get("partition_file")
            if (
                type(partition_binding) is not dict
                or set(partition_binding) != {"byte_length", "path", "sha256"}
            ):
                raise RawFluxVerificationFailure("partition binding schema drift")
            partition_path = _strict_path(partition_binding["path"])
            partition_hash = partition_binding["sha256"]
            if (
                partition_path in used_partition_paths
                or partition_binding != inventory.get(partition_path)
                or HEX_SHA256_RE.fullmatch(partition_hash) is None
            ):
                raise RawFluxVerificationFailure("partition inventory/path reuse drift")
            used_partition_paths.add(partition_path)
            partition = _strict_json(
                inventory_payloads[partition_path],
                partition_path,
            )
            expected_partition = _independent_partition(
                coordinate,
                config_row[coordinate],
                periodic_start,
                periodic_width,
            )
            if partition != expected_partition:
                raise RawFluxVerificationFailure(
                    f"independent partition reconstruction mismatch: {label}/{coordinate}"
                )
            if (
                stationary_axis.get("partition_path") != partition_path
                or stationary_axis.get("partition_sha256") != partition_hash
            ):
                raise RawFluxVerificationFailure("stationary/partition binding drift")
            partition_hashes.append(partition_hash)
            size = partition["size"]
            periodic = partition["periodic"]
            positions = [_fraction(value) for value in partition["positions_exact"]]
            volumes = [_fraction(value) for value in partition["cell_volumes_exact"]]
            if size != shape[axis_index] or any(volume <= 0 for volume in volumes):
                raise RawFluxVerificationFailure("partition size/volume drift")

            saved_mu, mu_file, mu_path = _manifest_file(
                axis_entry=axis_entry,
                coordinate=coordinate,
                role="stationary_mass",
                count=size,
                inventory=inventory,
                payloads=inventory_payloads,
            )
            saved_forward, forward_file, forward_path = _manifest_file(
                axis_entry=axis_entry,
                coordinate=coordinate,
                role="forward",
                count=size,
                inventory=inventory,
                payloads=inventory_payloads,
            )
            saved_backward, backward_file, backward_path = _manifest_file(
                axis_entry=axis_entry,
                coordinate=coordinate,
                role="backward",
                count=size,
                inventory=inventory,
                payloads=inventory_payloads,
            )
            for raw_path in (mu_path, forward_path, backward_path):
                if raw_path in used_raw_paths:
                    raise RawFluxVerificationFailure("raw role path was reused")
                used_raw_paths.add(raw_path)
            cell_count += size
            rate_count += 2 * size

            if coordinate == "midpoint":
                potentials = [
                    stiffness * (position - mean) ** 2 / diffusion
                    for position in positions
                ]
            elif coordinate == "relative_parallel":
                potentials = [
                    stiffness * position**2 / (4 * diffusion)
                    for position in positions
                ]
            else:
                potentials = [Fraction(0) for _ in positions]
            axis_diffusion = axis_diffusions[coordinate]

            physical_cell_sources = stationary_axis.get("cell_mass_intervals")
            if (
                type(physical_cell_sources) is not list
                or len(physical_cell_sources) != size
            ):
                raise RawFluxVerificationFailure("stationary cell cardinality drift")
            physical_cells: list[ExactInterval] = []
            for cell_index, physical_source in enumerate(physical_cell_sources):
                if (
                    type(physical_source) is not dict
                    or set(physical_source)
                    != {
                        "cell_index",
                        "lower_exact_p_over_q",
                        "upper_exact_p_over_q",
                    }
                    or physical_source.get("cell_index") != cell_index
                ):
                    raise RawFluxVerificationFailure("stationary cell index/schema drift")
                physical_cells.append(
                    _interval(
                        {
                            "lower_exact_p_over_q": physical_source[
                                "lower_exact_p_over_q"
                            ],
                            "upper_exact_p_over_q": physical_source[
                                "upper_exact_p_over_q"
                            ],
                        }
                    )
                )
                if (
                    physical_cells[-1].lower <= 0
                    or (
                        physical_cells[-1].upper - physical_cells[-1].lower
                    )
                    / physical_cells[-1].lower
                    > Fraction(1, 1_099_511_627_776)
                ):
                    raise RawFluxVerificationFailure(
                        "physical cell violates positive/relative-width pilot gate"
                    )

            primary_masses: list[ExactInterval] = []
            axis_factors: list[ExactInterval] = []
            cell_records: list[dict[str, Any]] = []
            cell_digest = _digest_stream(
                b"encounter-fixed-row-raw-flux-cell-audit-v1\0"
            )
            for cell_index, (potential, volume, saved, physical) in enumerate(
                zip(potentials, volumes, saved_mu, physical_cells, strict=True)
            ):
                primary = _formula_mu(potential, volume, PRIMARY_BITS)
                sentinel = _formula_mu(potential, volume, SENTINEL_BITS)
                alternate = _formula_mu(potential, volume, ALTERNATE_BITS)
                if (
                    not primary.contains(sentinel)
                    or not primary.contains(alternate)
                    or not saved.contains(primary)
                    or not saved.contains(sentinel)
                    or not saved.contains(alternate)
                    or primary.lower <= 0
                    or physical.lower <= 0
                ):
                    raise RawFluxVerificationFailure(
                        f"mass formula containment failed: {label}/{coordinate}/{cell_index}"
                    )
                factor = physical.divided_by_positive(primary)
                primary_masses.append(primary)
                axis_factors.append(factor)
                location = f"{label}:{coordinate}:mu[{cell_index}]"
                maximum_mu_width = _update_maximum(
                    maximum_mu_width,
                    _metric_relative_width(saved, primary),
                    location,
                )
                minimum_mu_margin = _update_minimum(
                    minimum_mu_margin,
                    _metric_relative_margin(saved, sentinel),
                    location,
                )
                _digest_update(
                    cell_digest,
                    {
                        "cell_index": cell_index,
                        "formula_primary": _interval_json(primary),
                        "formula_sentinel": _interval_json(sentinel),
                        "physical_pi_axis_mass": _interval_json(physical),
                        "rho_axis_factor": _interval_json(factor),
                        "saved_ungauged_mu": _interval_json(saved),
                    },
                )
                cell_records.append(
                    {
                        "cell_index": cell_index,
                        "formula_ungauged_mu_interval": _interval_json(primary),
                        "rho_axis_factor_interval": _interval_json(factor),
                    }
                )

            edge_records: list[dict[str, Any]] = []
            edge_digest = _digest_stream(
                b"encounter-fixed-row-raw-flux-edge-audit-v1\0"
            )
            edge_indices = range(size) if periodic else range(size - 1)
            for left_index in edge_indices:
                right_index = (left_index + 1) % size
                if periodic:
                    if coordinate != "relative_perpendicular":
                        raise RawFluxVerificationFailure("periodic edge on wrong coordinate")
                    forward_primary = _directed_rational(
                        axis_diffusion / volumes[left_index] ** 2,
                        PRIMARY_BITS,
                    ).exact()
                    forward_sentinel = _directed_rational(
                        axis_diffusion / volumes[left_index] ** 2,
                        SENTINEL_BITS,
                    ).exact()
                    forward_alternate = _directed_rational(
                        axis_diffusion / volumes[left_index] ** 2,
                        ALTERNATE_BITS,
                    ).exact()
                    reverse_primary = _directed_rational(
                        axis_diffusion / volumes[right_index] ** 2,
                        PRIMARY_BITS,
                    ).exact()
                    reverse_sentinel = _directed_rational(
                        axis_diffusion / volumes[right_index] ** 2,
                        SENTINEL_BITS,
                    ).exact()
                    reverse_alternate = _directed_rational(
                        axis_diffusion / volumes[right_index] ** 2,
                        ALTERNATE_BITS,
                    ).exact()
                    common_primary = _directed_rational(
                        axis_diffusion / volumes[left_index],
                        PRIMARY_BITS,
                    ).exact()
                    common_sentinel = _directed_rational(
                        axis_diffusion / volumes[left_index],
                        SENTINEL_BITS,
                    ).exact()
                    common_alternate = _directed_rational(
                        axis_diffusion / volumes[left_index],
                        ALTERNATE_BITS,
                    ).exact()
                    reverse_kappa_primary = common_primary
                    reverse_kappa_sentinel = common_sentinel
                    reverse_kappa_alternate = common_alternate
                else:
                    distance = positions[right_index] - positions[left_index]
                    if distance <= 0:
                        raise RawFluxVerificationFailure("nonpositive reflecting edge length")
                    delta = potentials[right_index] - potentials[left_index]
                    forward_primary = _formula_rate(
                        delta,
                        axis_diffusion,
                        volumes[left_index],
                        distance,
                        PRIMARY_BITS,
                    )
                    forward_sentinel = _formula_rate(
                        delta,
                        axis_diffusion,
                        volumes[left_index],
                        distance,
                        SENTINEL_BITS,
                    )
                    forward_alternate = _formula_rate(
                        delta,
                        axis_diffusion,
                        volumes[left_index],
                        distance,
                        ALTERNATE_BITS,
                        alternate=True,
                    )
                    reverse_primary = _formula_rate(
                        -delta,
                        axis_diffusion,
                        volumes[right_index],
                        distance,
                        PRIMARY_BITS,
                    )
                    reverse_sentinel = _formula_rate(
                        -delta,
                        axis_diffusion,
                        volumes[right_index],
                        distance,
                        SENTINEL_BITS,
                    )
                    reverse_alternate = _formula_rate(
                        -delta,
                        axis_diffusion,
                        volumes[right_index],
                        distance,
                        ALTERNATE_BITS,
                        alternate=True,
                    )
                    common_primary = _formula_kappa(
                        potentials[left_index],
                        delta,
                        axis_diffusion,
                        distance,
                        PRIMARY_BITS,
                    )
                    common_sentinel = _formula_kappa(
                        potentials[left_index],
                        delta,
                        axis_diffusion,
                        distance,
                        SENTINEL_BITS,
                    )
                    common_alternate = _formula_kappa(
                        potentials[left_index],
                        delta,
                        axis_diffusion,
                        distance,
                        ALTERNATE_BITS,
                        alternate=True,
                    )
                    reverse_kappa_primary = _formula_kappa(
                        potentials[right_index],
                        -delta,
                        axis_diffusion,
                        distance,
                        PRIMARY_BITS,
                    )
                    reverse_kappa_sentinel = _formula_kappa(
                        potentials[right_index],
                        -delta,
                        axis_diffusion,
                        distance,
                        SENTINEL_BITS,
                    )
                    reverse_kappa_alternate = _formula_kappa(
                        potentials[right_index],
                        -delta,
                        axis_diffusion,
                        distance,
                        ALTERNATE_BITS,
                        alternate=True,
                    )

                if (
                    not forward_primary.contains(forward_sentinel)
                    or not forward_primary.contains(forward_alternate)
                    or not reverse_primary.contains(reverse_sentinel)
                    or not reverse_primary.contains(reverse_alternate)
                    or not common_primary.contains(common_sentinel)
                    or not common_primary.contains(common_alternate)
                    or common_primary.lower <= 0
                ):
                    raise RawFluxVerificationFailure(
                        f"320/640/alternate edge enclosure failed: "
                        f"{label}/{coordinate}/{left_index}"
                    )
                saved_forward_rate = saved_forward[left_index]
                saved_reverse_rate = saved_backward[right_index]
                if (
                    not saved_forward_rate.contains(forward_primary)
                    or not saved_forward_rate.contains(forward_sentinel)
                    or not saved_forward_rate.contains(forward_alternate)
                    or not saved_reverse_rate.contains(reverse_primary)
                    or not saved_reverse_rate.contains(reverse_sentinel)
                    or not saved_reverse_rate.contains(reverse_alternate)
                    or saved_forward_rate.lower <= 0
                    or saved_reverse_rate.lower <= 0
                ):
                    raise RawFluxVerificationFailure(
                        f"saved rate misses formula member: "
                        f"{label}/{coordinate}/{left_index}"
                    )
                forward_flux = saved_mu[left_index].times_nonnegative(
                    saved_forward_rate
                )
                reverse_flux = saved_mu[right_index].times_nonnegative(
                    saved_reverse_rate
                )
                flux_intersection = forward_flux.intersection(reverse_flux)
                if (
                    not forward_flux.contains(common_primary)
                    or not forward_flux.contains(common_sentinel)
                    or not forward_flux.contains(common_alternate)
                    or not reverse_flux.contains(common_primary)
                    or not reverse_flux.contains(common_sentinel)
                    or not reverse_flux.contains(common_alternate)
                    or not flux_intersection.contains(common_primary)
                    or not flux_intersection.contains(common_sentinel)
                    or not flux_intersection.contains(common_alternate)
                ):
                    raise RawFluxVerificationFailure(
                        f"one common kappa not contained by both saved fluxes: "
                        f"{label}/{coordinate}/{left_index}"
                    )
                common_primary.intersection(reverse_kappa_primary)
                common_sentinel.intersection(reverse_kappa_sentinel)
                common_alternate.intersection(reverse_kappa_alternate)

                edge_location = (
                    f"{label}:{coordinate}:edge[{left_index}->{right_index}]"
                )
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
                    edge_digest,
                    {
                        "common_primary": _interval_json(common_primary),
                        "common_sentinel": _interval_json(common_sentinel),
                        "edge_index": left_index,
                        "forward_formula_primary": _interval_json(forward_primary),
                        "forward_formula_sentinel": _interval_json(forward_sentinel),
                        "left_cell_index": left_index,
                        "reverse_formula_primary": _interval_json(reverse_primary),
                        "reverse_formula_sentinel": _interval_json(reverse_sentinel),
                        "reverse_kappa_primary": _interval_json(
                            reverse_kappa_primary
                        ),
                        "reverse_kappa_sentinel": _interval_json(
                            reverse_kappa_sentinel
                        ),
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
                        "common_kappa_formula_interval": _interval_json(
                            common_primary
                        ),
                        "edge_index": left_index,
                        "left_cell_index": left_index,
                        "right_cell_index": right_index,
                        "saved_flux_intersection_interval": _interval_json(
                            flux_intersection
                        ),
                    }
                )
                edge_count += 1
                positive_rate_count += 2

            boundary_records: list[dict[str, Any]] = []
            if not periodic:
                for role, boundary_index, saved_zero in (
                    ("backward", 0, saved_backward[0]),
                    ("forward", size - 1, saved_forward[size - 1]),
                ):
                    if saved_zero != ExactInterval(Fraction(0), Fraction(0)):
                        raise RawFluxVerificationFailure(
                            "reflecting boundary rate is not exact zero"
                        )
                    boundary_records.append(
                        {
                            "cell_index": boundary_index,
                            "rate_interval": _interval_json(saved_zero),
                            "role": role,
                        }
                    )
                    zero_boundary_rate_count += 1

            axis_sum = _sum_intervals(primary_masses)
            physical_axis_sum = _interval(
                stationary_axis.get("joint_domain_mass_interval")
            )
            summed_physical = _sum_intervals(physical_cells)
            summed_physical.intersection(physical_axis_sum)
            if (
                physical_axis_sum.lower <= 0
                or (physical_axis_sum.upper - physical_axis_sum.lower)
                / physical_axis_sum.lower
                > Fraction(1, 1_099_511_627_776)
            ):
                raise RawFluxVerificationFailure(
                    "stationary axis violates positive/relative-width pilot gate"
                )
            factor_range = ExactInterval(
                min(value.lower for value in axis_factors),
                max(value.upper for value in axis_factors),
            )
            row_axis_sums.append(axis_sum)
            row_axis_factor_ranges.append(factor_range)
            row_axis_outputs.append(
                {
                    "boundary_zero_rate_records": boundary_records,
                    "cell_containment_audit_digest_sha256": cell_digest.hexdigest(),
                    "cell_count": size,
                    "cell_records": cell_records,
                    "coordinate": coordinate,
                    "edge_containment_audit_digest_sha256": edge_digest.hexdigest(),
                    "edge_count": len(edge_records),
                    "edge_records": edge_records,
                    "formula_axis_mu_sum_interval": _interval_json(axis_sum),
                    "partition_path": partition_path,
                    "partition_sha256": partition_hash,
                    "periodic": periodic,
                    "physical_axis_mass_sum_interval": _interval_json(
                        physical_axis_sum
                    ),
                    "raw_files": {
                        "backward": backward_file,
                        "forward": forward_file,
                        "stationary_mass": mu_file,
                    },
                    "rho_axis_factor_range_interval": _interval_json(factor_range),
                }
            )

        member_digest = _domain_digest(
            b"encounter-fixed-row-correlated-member-v1\0",
            {
                "authority_label": label,
                "coordinate_order": list(COORDINATES),
                "factorization_source_sha256": role_bindings[
                    "factorization_source"
                ]["sha256"],
                "ideal_formula_source_sha256": role_bindings[
                    "ideal_formula_source"
                ]["sha256"],
                "normalization": (
                    "one_global_gauge_and_globally_normalized_pi_no_box_renormalization"
                ),
                "partition_sha256s": partition_hashes,
                "physical_parameter_digest": parameter_digest,
                "reference_density_source_sha256": role_bindings[
                    "reference_density_source"
                ]["sha256"],
                "refinement_family_id": mapping["refinement_family_id"],
                "refinement_member_id": mapping["refinement_member_id"],
                "scalar_convention": member["member_semantics"]["scalar_convention"],
            },
        )
        if stationary_row.get("member_digest_sha256") != member_digest:
            raise RawFluxVerificationFailure("stationary correlated-member digest drift")

        axis_sum_product = ExactInterval(Fraction(1), Fraction(1))
        factor_product_range = ExactInterval(Fraction(1), Fraction(1))
        for axis_sum, factor_range in zip(
            row_axis_sums,
            row_axis_factor_ranges,
            strict=True,
        ):
            axis_sum_product = axis_sum_product.times_nonnegative(axis_sum)
            factor_product_range = factor_product_range.times_nonnegative(
                factor_range
            )
        box_mass = _interval(stationary_row.get("joint_box_mass_interval"))
        global_gauge = box_mass.divided_by_positive(axis_sum_product)
        inverse_gauge = global_gauge.reciprocal_positive()
        rho_range = factor_product_range.times_nonnegative(inverse_gauge)
        if (
            box_mass.lower <= 0
            or axis_sum_product.lower <= 0
            or global_gauge.lower <= 0
            or (global_gauge.upper - global_gauge.lower) / global_gauge.lower
            > Fraction(1, 1_099_511_627_776)
            or rho_range.lower <= 0
            or rho_range.upper > Fraction(1_000_000)
        ):
            raise RawFluxVerificationFailure(
                "gauge/rho violates finite-row anti-vacuity pilot gate"
            )
        output_rows.append(
            {
                "axes": row_axis_outputs,
                "axis_mu_sum_product_interval": _interval_json(axis_sum_product),
                "configuration_index": index,
                "configuration_label": label,
                "factorized_box_mass_interval": _interval_json(box_mass),
                "global_gauge_formula": (
                    "G=M_L/(S_midpoint*S_relative_parallel*"
                    "S_relative_perpendicular)"
                ),
                "global_gauge_interval": _interval_json(global_gauge),
                "inverse_global_gauge_interval": _interval_json(inverse_gauge),
                "member_digest_sha256": member_digest,
                "refinement_family_id": mapping["refinement_family_id"],
                "refinement_member_id": mapping["refinement_member_id"],
                "rho_factorization_formula": (
                    "rho[i,j,k]=G^-1*"
                    "(M_midpoint[i]/mu_midpoint[i])*"
                    "(M_relative_parallel[j]/mu_relative_parallel[j])*"
                    "(M_relative_perpendicular[k]/mu_relative_perpendicular[k])"
                ),
                "rho_range_interval": _interval_json(rho_range),
                "tensor_state_count": expected_states,
            }
        )

    if (
        len(used_row_paths) != 12
        or len(used_partition_paths) != 36
        or len(used_raw_paths) != 108
        or cell_count != 5_037
        or rate_count != 10_074
        or positive_rate_count != 10_026
        or zero_boundary_rate_count != 48
        or edge_count != 5_013
        or sum(row["tensor_state_count"] for row in output_rows) != 34_787_462
    ):
        raise RawFluxVerificationFailure("fixed-family inventory identity drift")

    expected = {
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
            "global_gauge": (
                "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)"
            ),
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
                "reflecting:(D_axis/d_ij)*exp(-Phi_i)*"
                "Bernoulli(Phi_j-Phi_i);periodic:D_axis/cell_width"
            ),
            "dense_tensor_materialized": False,
            "primary_method_id": "directed_mpfr_320_reference_density_v1",
            "primary_precision_bits": PRIMARY_BITS,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_method_id": (
                "directed_mpfr_640_reference_density_sentinel_v1"
            ),
            "sentinel_precision_bits": SENTINEL_BITS,
            "sentinel_semantics": (
                "same_backend_higher_precision_containment_not_backend_independence"
            ),
        },
        "rows": output_rows,
        "schema": SCHEMA,
        "source_pins": {
            "builder_source": {
                "path": BUILDER_PATH,
                "sha256": BUILDER_SHA256,
            },
            "configuration_source": {
                "path": CONFIGURATION_PATH,
                "sha256": CONFIGURATION_SHA256,
            },
            "factorization_source": {
                "path": FACTORIZATION_PATH,
                "sha256": FACTORIZATION_SHA256,
            },
            "ideal_formula_source": {
                "path": FORMULA_PATH,
                "sha256": FORMULA_SHA256,
            },
            "member_spec": {
                "path": MEMBER_PATH,
                "sha256": MEMBER_SHA256,
            },
            "method_registry": {
                "path": METHOD_PATH,
                "sha256": METHOD_SHA256,
            },
            "production_bundle": {
                "path": BUNDLE_PATH,
                "sha256": BUNDLE_SHA256,
            },
            "raw_axis_binding": {
                "path": RAW_BINDING_PATH,
                "sha256": RAW_BINDING_SHA256,
            },
            "reference_density_source": {
                "path": REFERENCE_PATH,
                "sha256": REFERENCE_SHA256,
            },
            "stationary_integral_source": {
                "path": STATIONARY_PATH,
                "sha256": STATIONARY_SHA256,
            },
        },
        "status": STATUS,
        "summary": {
            "all_320_bit_formula_intervals_contain_640_bit_sentinels": True,
            "all_formula_mu_and_rate_intervals_contained_by_saved_raw_intervals": True,
            "all_left_and_right_common_kappa_formula_enclosures_intersect": True,
            "all_single_common_kappa_intervals_contained_by_both_saved_flux_sides_and_intersections": True,
            "axis_cell_count": cell_count,
            "axis_edge_count": edge_count,
            "configuration_count": len(output_rows),
            "maximum_saved_flux_intersection_relative_width": _metric_json(
                maximum_flux_width
            ),
            "maximum_saved_mu_relative_width": _metric_json(maximum_mu_width),
            "maximum_saved_rate_relative_width": _metric_json(maximum_rate_width),
            "minimum_common_kappa_containment_relative_margin": _metric_json(
                minimum_kappa_margin
            ),
            "minimum_saved_mu_containment_relative_margin": _metric_json(
                minimum_mu_margin
            ),
            "minimum_saved_rate_containment_relative_margin": _metric_json(
                minimum_rate_margin
            ),
            "positive_saved_rate_entry_count": positive_rate_count,
            "raw_binary_interval_file_count": len(used_raw_paths),
            "saved_rate_entry_count": rate_count,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count"] for row in output_rows
            ),
            "zero_reflecting_boundary_rate_entry_count": zero_boundary_rate_count,
        },
    }
    return expected, {
        "axis_cells": cell_count,
        "axis_edges": edge_count,
        "partitions": len(used_partition_paths),
        "raw_files": len(used_raw_paths),
        "rate_entries": rate_count,
        "rows": len(output_rows),
    }


def _verify_execution_context() -> None:
    """Check the launcher's injected target/runtime identity before validation."""

    expected_keys = {
        "authority_sha256",
        "gmpy2_module",
        "launcher_sha256",
        "runtime_attestation",
        "schema",
        "target_key",
        "target_source_path",
        "target_source_sha256",
    }
    if (
        type(_EXECUTION_CONTEXT) is not dict
        or set(_EXECUTION_CONTEXT) != expected_keys
    ):
        raise RawFluxVerificationFailure("authenticated execution context is absent")
    source_path = "code/validate_continuum_c1_fixed_row_raw_flux_source_v1.py"
    if (
        _EXECUTION_CONTEXT.get("schema")
        != "encounter_continuum_c1_authenticated_target_context_v1"
        or _EXECUTION_CONTEXT.get("target_key") != "raw_flux_validator"
        or _EXECUTION_CONTEXT.get("target_source_path") != source_path
        or not _is_sha256(_EXECUTION_CONTEXT.get("target_source_sha256"))
        or not _is_sha256(_EXECUTION_CONTEXT.get("authority_sha256"))
        or not _is_sha256(_EXECUTION_CONTEXT.get("launcher_sha256"))
        or _EXECUTION_CONTEXT.get("gmpy2_module") is not gmpy2
        or sys.modules.get("gmpy2") is not gmpy2
    ):
        raise RawFluxVerificationFailure("authenticated target context drift")
    if (
        _sha256(_report_snapshot(source_path, 2_000_000))
        != _EXECUTION_CONTEXT["target_source_sha256"]
    ):
        raise RawFluxVerificationFailure("target source changed after captured execution")

    attestation = _EXECUTION_CONTEXT.get("runtime_attestation")
    if (
        type(attestation) is not dict
        or set(attestation)
        != {
            "entry",
            "implementation_filename",
            "implementation_sha256",
            "runtime",
            "trust_contract",
        }
        or attestation.get("implementation_filename")
        != "positive_b_stage_b_t1_selector_v5.py"
        or not _is_sha256(attestation.get("implementation_sha256"))
    ):
        raise RawFluxVerificationFailure("runtime attestation envelope drift")
    expected_trust_contract = {
        "bootstrap_trust_base": (
            "CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES"
        ),
        "native_image_execution": (
            "PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT"
        ),
        "protection_claim": "DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY",
        "runtime_tree_concurrency": (
            "NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS"
        ),
        "schema": "positive-b-stage-b-t0-execution-trust-contract-v1",
        "wrapper_execution": "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
    }
    entry = attestation["entry"]
    if (
        attestation["trust_contract"] != expected_trust_contract
        or type(entry) is not dict
        or set(entry)
        != {
            "external_attestation_schema",
            "external_attestation_sha256",
            "external_attestation_status",
            "mode",
            "production_eligible",
            "trust_contract",
        }
        or entry.get("external_attestation_schema")
        != "positive-b-stage-b-t0-external-attestation-v2"
        or entry.get("external_attestation_status") != "INDEPENDENT-ATTACK-PASS"
        or entry.get("mode") != "VERIFIED-ISOLATED"
        or entry.get("production_eligible") is not True
        or entry.get("trust_contract") != expected_trust_contract
        or not _is_sha256(entry.get("external_attestation_sha256"))
    ):
        raise RawFluxVerificationFailure("runtime verified-entry contract drift")
    runtime = attestation["runtime"]
    if (
        type(runtime) is not dict
        or set(runtime)
        != {
            "bundled_libraries_sha256",
            "cpython_trust_base",
            "extension_sha256",
            "gmp",
            "gmpy2",
            "loaded_native_images",
            "mpc",
            "mpfr",
            "package_files_sha256",
            "package_init_sha256",
            "python_cflags",
            "python_compiler",
            "python_wrapper_execution",
            "runtime_lock_sha256",
        }
        or runtime.get("gmpy2") != "2.2.1"
        or runtime.get("gmp") != "GMP 6.3.0"
        or runtime.get("mpfr") != "MPFR 4.2.1"
        or runtime.get("mpc") != "MPC 1.3.1"
        or runtime.get("python_wrapper_execution")
        != "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC"
        or any(
            not _is_sha256(runtime.get(key))
            for key in (
                "extension_sha256",
                "package_init_sha256",
                "runtime_lock_sha256",
            )
        )
        or type(runtime.get("package_files_sha256")) is not dict
        or type(runtime.get("bundled_libraries_sha256")) is not dict
        or type(runtime.get("loaded_native_images")) is not list
        or type(runtime.get("cpython_trust_base")) is not dict
    ):
        raise RawFluxVerificationFailure("authenticated gmpy2/MPFR runtime drift")
    for digest_map in (
        runtime["package_files_sha256"],
        runtime["bundled_libraries_sha256"],
    ):
        if not digest_map or any(
            type(name) is not str or not _is_sha256(digest)
            for name, digest in digest_map.items()
        ):
            raise RawFluxVerificationFailure("runtime dependency digest map drift")


def validate(selected_artifact: Path) -> dict[str, Any]:
    _verify_execution_context()
    selected_raw = _selected_artifact_snapshot(selected_artifact)
    selected = _strict_json(selected_raw, str(selected_artifact))
    expected, counts = _expected_artifact()
    expected_raw = _canonical_bytes(expected)
    if selected_raw != expected_raw or selected != expected:
        raise RawFluxVerificationFailure(
            "selected raw-flux artifact differs from independent reconstruction"
        )
    artifact_hash = _sha256(selected_raw)
    if artifact_hash != DEFAULT_ARTIFACT_SHA256:
        raise RawFluxVerificationFailure("canonical raw-flux artifact digest drift")
    return {
        "artifact_sha256": artifact_hash,
        "backend_independence_claimed": False,
        "complete_C1": False,
        "complete_C2": False,
        "formula_route_sentinel_bits": ALTERNATE_BITS,
        "inventory": counts,
        "same_member_acceptance_receipt_present": False,
        "status": VALIDATION_STATUS,
    }


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="selected canonical artifact or launcher-snapshotted mutation probe",
    )
    arguments = parser.parse_args()
    try:
        result = validate(arguments.artifact)
    except (RawFluxVerificationFailure, OSError, ValueError) as error:
        print(f"HOLD: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
