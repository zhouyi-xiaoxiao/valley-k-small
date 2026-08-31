#!/usr/bin/env python3
"""Independently validate the fixed-row stationary-integral source.

This verifier does not import or execute the builder or the production F0
implementation.  It snapshots externally pinned source authorities, rebuilds
all exact partitions from the configuration authority, and independently
evaluates every physical axis-cell mass with directed 320-bit MPFR arithmetic.
A same-backend 640-bit evaluation is required to be contained cell by cell.

The expected canonical artifact is reconstructed in memory and compared
byte-for-byte with the selected artifact.  Absolute artifact paths are accepted
only to support read-only mutation tests; every scientific input remains pinned
inside this report.  No result of this verifier promotes a fixed finite row to
a refinement sequence or establishes complete C1/C2.
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
    or _authenticated_context.get("target_key") != "stationary_validator"
    or _authenticated_context.get("target_source_path")
    != "code/validate_continuum_c1_stationary_integral_source_v1.py"
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
import re
import stat
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

HERE: Final = Path(__file__).resolve()
REPORT: Final = HERE.parents[1]
SCHEMA: Final = "encounter_continuum_c1_stationary_integral_source_v1"
STATUS: Final = (
    "PASS_FIXED_12_ROW_FACTORIZED_PHYSICAL_STATIONARY_INTEGRALS_"
    "SAME_MPFR_BACKEND_SENTINEL_ONLY_NO_REFINEMENT_NO_COMPLETE_C1_C2"
)
VALIDATION_STATUS: Final = (
    "PASS_FIXED_12_ROW_STATIONARY_INTEGRAL_SOURCE_INDEPENDENT_VALIDATION_ONLY"
)
PRIMARY_BITS: Final = 320
SENTINEL_BITS: Final = 640
AXES: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)

REFERENCE_PATH: Final = "artifacts/data/continuum_c1_reference_density_source_v1.json"
REFERENCE_SHA256: Final = "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575"
FORMULA_PATH: Final = "artifacts/data/continuum_c1_ideal_formula_source_v1.json"
FORMULA_SHA256: Final = "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be"
MEMBER_PATH: Final = "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json"
MEMBER_SHA256: Final = "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef"
METHOD_PATH: Final = "artifacts/data/continuum_c1_c2_fixed_row_outward_method_registry_v1.json"
METHOD_SHA256: Final = "ac00450edf826029b157a98ad2835592630c07b2a75334c25d8d1232a4fe69c3"
CONFIGURATION_PATH: Final = "artifacts/data/physical_configuration_family_control_free_v1.json"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
RAW_BINDING_PATH: Final = "artifacts/data/continuum_c1_raw_axis_production_binding_v1.json"
RAW_BINDING_SHA256: Final = "7028fecf4538abb1df56f03d8cea01d0ed208a43356cb9b1e24c67fb54d47480"
BUNDLE_PATH: Final = "artifacts/data/physical_production_initial_stream_v1/bundle.json"
BUNDLE_ROOT: Final = "artifacts/data/physical_production_initial_stream_v1"
BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
BUILDER_PATH: Final = "code/build_continuum_c1_stationary_integral_source_v1.py"
DEFAULT_ARTIFACT: Final = REPORT / "artifacts/data/continuum_c1_stationary_integral_source_v1.json"

PINNED_SOURCES: Final = {
    "reference": (REFERENCE_PATH, REFERENCE_SHA256, 100_000),
    "formula": (FORMULA_PATH, FORMULA_SHA256, 100_000),
    "member": (MEMBER_PATH, MEMBER_SHA256, 100_000),
    "method": (METHOD_PATH, METHOD_SHA256, 100_000),
    "configuration": (CONFIGURATION_PATH, CONFIGURATION_SHA256, 1_000_000),
    "raw_binding": (RAW_BINDING_PATH, RAW_BINDING_SHA256, 100_000),
    "bundle": (BUNDLE_PATH, BUNDLE_SHA256, 2_000_000),
}


class StationaryIntegralVerificationFailure(RuntimeError):
    """Fail-closed scientific validation error."""


@dataclass(frozen=True, slots=True)
class ExactBounds:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not Fraction
            or type(self.upper) is not Fraction
            or self.lower > self.upper
        ):
            raise StationaryIntegralVerificationFailure("invalid exact interval")

    def plus(self, other: ExactBounds) -> ExactBounds:
        return ExactBounds(self.lower + other.lower, self.upper + other.upper)

    def nonnegative_product(self, other: ExactBounds) -> ExactBounds:
        if self.lower < 0 or other.lower < 0:
            raise StationaryIntegralVerificationFailure("nonnegative interval product required")
        return ExactBounds(self.lower * other.lower, self.upper * other.upper)

    def overlap(self, other: ExactBounds) -> ExactBounds:
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise StationaryIntegralVerificationFailure(
                "independently reconstructed intervals are disjoint"
            )
        return ExactBounds(lower, upper)

    def encloses(self, other: ExactBounds) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper


@dataclass(frozen=True, slots=True)
class DirectedBounds:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    bits: int

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not gmpy2.mpfr
            or type(self.upper) is not gmpy2.mpfr
            or self.bits not in {PRIMARY_BITS, SENTINEL_BITS}
            or not gmpy2.is_finite(self.lower)
            or not gmpy2.is_finite(self.upper)
            or self.lower > self.upper
        ):
            raise StationaryIntegralVerificationFailure("invalid directed MPFR interval")

    def exact(self) -> ExactBounds:
        return ExactBounds(_mpfr_fraction(self.lower), _mpfr_fraction(self.upper))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise StationaryIntegralVerificationFailure("duplicate or non-string JSON object key")
        result[key] = value
    return result


def _strict_json_tree(value: Any, depth: int = 0) -> None:
    if depth > 40:
        raise StationaryIntegralVerificationFailure("JSON depth cap exceeded")
    if isinstance(value, float):
        raise StationaryIntegralVerificationFailure("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise StationaryIntegralVerificationFailure("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_json_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise StationaryIntegralVerificationFailure("invalid JSON object key")
            _strict_json_tree(item, depth + 1)
        return
    raise StationaryIntegralVerificationFailure(
        f"forbidden JSON value type: {type(value).__name__}"
    )


def _exactly(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(right) is dict:
        return set(left) == set(right) and all(_exactly(left[key], right[key]) for key in right)
    if type(right) is list:
        return len(left) == len(right) and all(
            _exactly(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )
    return left == right


def _canonical_bytes(value: Any) -> bytes:
    _strict_json_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_report_relative(value: object) -> str:
    if type(value) is not str:
        raise StationaryIntegralVerificationFailure("report-relative path must be a string")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or "." in path.parts
        or ".." in path.parts
        or any(not component for component in path.parts)
    ):
        raise StationaryIntegralVerificationFailure("unsafe report-relative path")
    return path.as_posix()


def _join_report_relative(parent: str, child: object) -> str:
    child_relative = _safe_report_relative(child)
    combined = PurePosixPath(parent) / PurePosixPath(child_relative)
    result = _safe_report_relative(combined.as_posix())
    parent_parts = PurePosixPath(parent).parts
    if PurePosixPath(result).parts[: len(parent_parts)] != parent_parts:
        raise StationaryIntegralVerificationFailure("report path escaped pinned root")
    return result


def _stable_absolute_snapshot(path: Path, cap: int) -> tuple[bytes, str]:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_absolute() or cap <= 0:
        raise StationaryIntegralVerificationFailure("invalid snapshot request")
    components = absolute.parts[1:]
    if not components:
        raise StationaryIntegralVerificationFailure("ordinary file path required")
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directories = [os.open("/", directory_flags)]
    descriptor = -1
    try:
        for component in components[:-1]:
            if component in {"", ".", ".."}:
                raise StationaryIntegralVerificationFailure("unsafe absolute path")
            directories.append(os.open(component, directory_flags, dir_fd=directories[-1]))
        filename = components[-1]
        descriptor = os.open(filename, file_flags, dir_fd=directories[-1])
        before = os.fstat(descriptor)
        named_before = os.stat(filename, dir_fd=directories[-1], follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise StationaryIntegralVerificationFailure("ordinary single-link input file required")
        if (before.st_dev, before.st_ino) != (named_before.st_dev, named_before.st_ino):
            raise StationaryIntegralVerificationFailure("descriptor/name mismatch")
        if before.st_size > cap:
            raise StationaryIntegralVerificationFailure("snapshot file cap exceeded")
        chunks: list[bytes] = []
        remaining = before.st_size + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        named_after = os.stat(filename, dir_fd=directories[-1], follow_symlinks=False)
        before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        named_id = (
            named_after.st_dev,
            named_after.st_ino,
            named_after.st_size,
            named_after.st_mtime_ns,
        )
        if len(payload) != before.st_size or before_id != after_id or after_id != named_id:
            raise StationaryIntegralVerificationFailure("unstable file snapshot")
        for index, component in enumerate(components[:-1]):
            held = os.fstat(directories[index + 1])
            named = os.stat(component, dir_fd=directories[index], follow_symlinks=False)
            if not stat.S_ISDIR(held.st_mode) or (held.st_dev, held.st_ino) != (
                named.st_dev,
                named.st_ino,
            ):
                raise StationaryIntegralVerificationFailure("snapshot directory chain changed")
    except OSError as error:
        raise StationaryIntegralVerificationFailure(f"cannot snapshot input: {absolute}") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)
    return payload, _sha256(payload)


def _report_snapshot(relative: object, cap: int) -> tuple[bytes, str]:
    normalized = _safe_report_relative(relative)
    absolute = REPORT.joinpath(*PurePosixPath(normalized).parts)
    return _stable_absolute_snapshot(absolute, cap)


def _parse_canonical_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        text = payload.decode("ascii")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                StationaryIntegralVerificationFailure(
                    f"JSON floating literal forbidden in {label}: {token}"
                )
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                StationaryIntegralVerificationFailure(
                    f"JSON constant forbidden in {label}: {token}"
                )
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StationaryIntegralVerificationFailure(f"invalid strict JSON: {label}") from error
    _strict_json_tree(value)
    if type(value) is not dict or _canonical_bytes(value) != payload:
        raise StationaryIntegralVerificationFailure(f"noncanonical top-level JSON object: {label}")
    return value


def _pinned_json(relative: str, digest: str, cap: int) -> dict[str, Any]:
    payload, observed = _report_snapshot(relative, cap)
    if observed != digest:
        raise StationaryIntegralVerificationFailure(
            f"pinned scientific source hash drift: {relative}"
        )
    return _parse_canonical_json(payload, relative)


def _manifest_json(
    relative: str,
    digest: object,
    cap: int,
    expected_byte_length: object,
) -> dict[str, Any]:
    if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise StationaryIntegralVerificationFailure("invalid manifest SHA-256")
    if (
        type(expected_byte_length) is not int
        or isinstance(expected_byte_length, bool)
        or expected_byte_length < 0
        or expected_byte_length > cap
    ):
        raise StationaryIntegralVerificationFailure("invalid manifest byte length")
    payload, observed = _report_snapshot(relative, cap)
    if observed != digest or len(payload) != expected_byte_length:
        raise StationaryIntegralVerificationFailure(
            f"manifest-bound source hash or length drift: {relative}"
        )
    return _parse_canonical_json(payload, relative)


def _fraction_string(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: object) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise StationaryIntegralVerificationFailure("canonical p/q string required")
    numerator, denominator = value.split("/")
    try:
        result = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError) as error:
        raise StationaryIntegralVerificationFailure("invalid p/q string") from error
    if result.denominator <= 0 or _fraction_string(result) != value:
        raise StationaryIntegralVerificationFailure("noncanonical p/q string")
    return result


def _binary64_fraction(value: object) -> Fraction:
    if type(value) is not str:
        raise StationaryIntegralVerificationFailure("binary64 hex string required")
    try:
        number = float.fromhex(value)
    except ValueError as error:
        raise StationaryIntegralVerificationFailure("invalid binary64 hex string") from error
    if (
        not math.isfinite(number)
        or number.hex() != value
        or (number == 0.0 and math.copysign(1.0, number) < 0)
    ):
        raise StationaryIntegralVerificationFailure("noncanonical finite binary64 hex string")
    return Fraction.from_float(number)


def _interval_object(value: ExactBounds) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _fraction_string(value.lower),
        "upper_exact_p_over_q": _fraction_string(value.upper),
    }


def _mpfr_context(bits: int, rounding: int) -> gmpy2.context:
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


def _rounded_fraction(value: Fraction, bits: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(_mpfr_context(bits, rounding)):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mpfr_fraction(value: gmpy2.mpfr) -> Fraction:
    rational = gmpy2.mpq(value)
    return Fraction(int(rational.numerator), int(rational.denominator))


def _from_exact(value: Fraction, bits: int) -> DirectedBounds:
    return DirectedBounds(
        _rounded_fraction(value, bits, gmpy2.RoundDown),
        _rounded_fraction(value, bits, gmpy2.RoundUp),
        bits,
    )


def _rounded_operation(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    bits: int,
    rounding: int,
    operation: str,
) -> gmpy2.mpfr:
    with gmpy2.context(_mpfr_context(bits, rounding)):
        if operation == "subtract":
            return +(left - right)
        if operation == "multiply":
            return +(left * right)
    raise StationaryIntegralVerificationFailure("unknown MPFR operation")


def _directed_subtract(left: DirectedBounds, right: DirectedBounds) -> DirectedBounds:
    if left.bits != right.bits:
        raise StationaryIntegralVerificationFailure("MPFR precision mismatch")
    return DirectedBounds(
        _rounded_operation(
            left.lower,
            right.upper,
            left.bits,
            gmpy2.RoundDown,
            "subtract",
        ),
        _rounded_operation(
            left.upper,
            right.lower,
            left.bits,
            gmpy2.RoundUp,
            "subtract",
        ),
        left.bits,
    )


def _directed_product(left: DirectedBounds, right: DirectedBounds) -> DirectedBounds:
    if left.bits != right.bits:
        raise StationaryIntegralVerificationFailure("MPFR precision mismatch")
    pairs = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    lower_candidates = [
        _rounded_operation(a, b, left.bits, gmpy2.RoundDown, "multiply") for a, b in pairs
    ]
    upper_candidates = [
        _rounded_operation(a, b, left.bits, gmpy2.RoundUp, "multiply") for a, b in pairs
    ]
    return DirectedBounds(min(lower_candidates), max(upper_candidates), left.bits)


def _monotone_image(value: DirectedBounds, function: Any) -> DirectedBounds:
    with gmpy2.context(_mpfr_context(value.bits, gmpy2.RoundDown)):
        lower = +function(value.lower)
    with gmpy2.context(_mpfr_context(value.bits, gmpy2.RoundUp)):
        upper = +function(value.upper)
    return DirectedBounds(lower, upper, value.bits)


def _normal_segment_mass(
    lower: Fraction,
    upper: Fraction,
    coefficient: Fraction,
    centre: Fraction,
    bits: int,
) -> ExactBounds:
    if lower >= upper or coefficient <= 0:
        raise StationaryIntegralVerificationFailure("invalid Gaussian segment")
    root = _monotone_image(_from_exact(coefficient, bits), gmpy2.sqrt)
    lower_argument = _directed_product(root, _from_exact(lower - centre, bits))
    upper_argument = _directed_product(root, _from_exact(upper - centre, bits))
    lower_erf = _monotone_image(lower_argument, gmpy2.erf)
    upper_erf = _monotone_image(upper_argument, gmpy2.erf)
    difference = _directed_subtract(upper_erf, lower_erf)
    result = _directed_product(difference, _from_exact(Fraction(1, 2), bits)).exact()
    if not (0 < result.lower <= result.upper < 1):
        raise StationaryIntegralVerificationFailure("Gaussian segment mass escaped (0,1)")
    return result


def _sum_bounds(values: list[ExactBounds]) -> ExactBounds:
    total = ExactBounds(Fraction(0), Fraction(0))
    for value in values:
        total = total.plus(value)
    return total


def _modulo(value: Fraction, period: Fraction) -> Fraction:
    if period <= 0:
        raise StationaryIntegralVerificationFailure("positive period required")
    return value - (value // period) * period


def _independent_partition(
    coordinate: str,
    axis: dict[str, Any],
    transverse_start: Fraction,
    transverse_width: Fraction,
) -> dict[str, Any]:
    size = axis.get("size")
    alignment = axis.get("alignment")
    if type(size) is not int or isinstance(size, bool) or size < 2 or type(alignment) is not str:
        raise StationaryIntegralVerificationFailure("invalid configuration axis")

    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        lower = _binary64_fraction(axis.get("lower_binary64_hex"))
        upper = _binary64_fraction(axis.get("upper_binary64_hex"))
        if lower >= upper:
            raise StationaryIntegralVerificationFailure("invalid reflecting domain")
        domain_start = lower
        domain_width = upper - lower
        shift = Fraction(0)
        periodic = False
        if alignment == "cell_centred_reflecting":
            step = domain_width / size
            positions = [lower + (Fraction(index) + Fraction(1, 2)) * step for index in range(size)]
            cells = [[(lower + index * step, lower + (index + 1) * step)] for index in range(size)]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = domain_width / (size - 1)
            positions = [lower + index * step for index in range(size)]
            boundaries = (
                [lower]
                + [lower + (Fraction(index) - Fraction(1, 2)) * step for index in range(1, size)]
                + [upper]
            )
            cells = [[(boundaries[index], boundaries[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
    elif alignment in {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    }:
        step = transverse_width / size
        shift = _fraction(axis.get("periodic_shift_exact"))
        expected_shift = Fraction(0) if alignment == "cell_centred_periodic_base" else step / 2
        if shift != expected_shift:
            raise StationaryIntegralVerificationFailure("periodic shift drift")
        domain_start = transverse_start
        domain_width = transverse_width
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
        cells = []
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
        raise StationaryIntegralVerificationFailure("unknown axis alignment")

    volumes = [
        sum((segment_upper - segment_lower for segment_lower, segment_upper in cell), Fraction(0))
        for cell in cells
    ]
    if any(volume <= 0 for volume in volumes):
        raise StationaryIntegralVerificationFailure("nonpositive partition cell")
    return {
        "cell_segments_exact": [
            [
                [_fraction_string(segment_lower), _fraction_string(segment_upper)]
                for segment_lower, segment_upper in cell
            ]
            for cell in cells
        ],
        "cell_volumes_exact": [_fraction_string(volume) for volume in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _fraction_string(domain_start),
        "domain_width_exact": _fraction_string(domain_width),
        "periodic": periodic,
        "periodic_shift_exact": _fraction_string(shift),
        "positions_exact": [_fraction_string(position) for position in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def _domain_digest(domain: bytes, value: Any) -> str:
    if not domain.endswith(b"\0"):
        raise StationaryIntegralVerificationFailure("digest domain must be NUL terminated")
    return _sha256(domain + _canonical_bytes(value))


def _require_exact_false_map(value: Any, expected_keys: set[str], label: str) -> None:
    if (
        type(value) is not dict
        or set(value) != expected_keys
        or any(value[key] is not False for key in expected_keys)
    ):
        raise StationaryIntegralVerificationFailure(
            f"{label} claim boundary must contain exact false booleans"
        )


def _check_authority_semantics(sources: dict[str, dict[str, Any]]) -> None:
    expected_schemas = {
        "reference": "encounter_continuum_c1_reference_density_source_v1",
        "formula": "encounter_continuum_c1_ideal_formula_source_v1",
        "member": "encounter_continuum_c1_c2_fixed_row_member_spec_v1",
        "method": "encounter_continuum_c1_c2_fixed_row_outward_method_registry_v1",
        "configuration": "encounter_physical_configuration_family_control_free_v1",
        "raw_binding": "encounter_continuum_c1_raw_axis_production_binding_v1",
        "bundle": "encounter_control_free_production_initial_stream_v1",
    }
    for role, expected_schema in expected_schemas.items():
        if sources[role].get("schema") != expected_schema:
            raise StationaryIntegralVerificationFailure(f"{role} source schema drift")

    _require_exact_false_map(
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
    _require_exact_false_map(
        sources["member"].get("claim_boundary"),
        {
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "genuine_refinement_sequence_present",
            "production_bridge_accepted",
            "release_eligible",
        },
        "member",
    )
    _require_exact_false_map(
        sources["method"].get("claim_boundary"),
        {
            "backend_independence_claimed",
            "complete_C1",
            "complete_C2",
            "formal_production_bridge_accepted",
            "release_eligible",
        },
        "method",
    )
    _require_exact_false_map(
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
        "raw binding",
    )
    reference_normalization = sources["reference"].get("normalization")
    if (
        type(reference_normalization) is not dict
        or reference_normalization.get("conditional_box_renormalization_used") is not False
        or reference_normalization.get("restricted_density_retains_global_normalization")
        is not True
        or reference_normalization.get("periodic_factor") != "1/W"
    ):
        raise StationaryIntegralVerificationFailure(
            "reference-density normalization semantics drift"
        )
    formula_semantics = sources["formula"].get("member_semantics")
    if (
        type(formula_semantics) is not dict
        or formula_semantics.get("one_correlated_distinguished_member_required") is not True
        or formula_semantics.get("formula_defined_member_is_independent_of_production_centres")
        is not True
    ):
        raise StationaryIntegralVerificationFailure("ideal-formula member semantics drift")
    methods = sources["method"].get("methods")
    if type(methods) is not list:
        raise StationaryIntegralVerificationFailure("method registry rows missing")
    method_by_id: dict[str, dict[str, Any]] = {}
    for row in methods:
        if type(row) is not dict or type(row.get("method_id")) is not str:
            raise StationaryIntegralVerificationFailure("invalid method registry row")
        method_id = row["method_id"]
        if method_id in method_by_id:
            raise StationaryIntegralVerificationFailure("duplicate method id")
        method_by_id[method_id] = row
    expected_methods = {
        "directed_mpfr_320_reference_density_v1": PRIMARY_BITS,
        "directed_mpfr_640_reference_density_sentinel_v1": SENTINEL_BITS,
    }
    for method_id, bits in expected_methods.items():
        row = method_by_id.get(method_id)
        if (
            row is None
            or row.get("precision_bits") != bits
            or row.get("rounding_mode") != "directed_RoundDown_RoundUp"
            or row.get("special_function_backend_and_version") != "gmpy2_2.2.1_MPFR_4.2.1"
        ):
            raise StationaryIntegralVerificationFailure(
                "stationary-integral method registration drift"
            )


def _independent_expected_artifact() -> tuple[dict[str, Any], dict[str, int]]:
    if gmpy2.__version__ != "2.2.1" or gmpy2.mpfr_version() != "MPFR 4.2.1":
        raise StationaryIntegralVerificationFailure("unaccepted gmpy2/MPFR runtime")

    sources = {
        role: _pinned_json(path, digest, cap)
        for role, (path, digest, cap) in PINNED_SOURCES.items()
    }
    _check_authority_semantics(sources)
    reference = sources["reference"]
    member = sources["member"]
    configuration = sources["configuration"]
    bundle = sources["bundle"]

    parameters = reference.get("physical_parameter_bundle")
    if type(parameters) is not dict:
        raise StationaryIntegralVerificationFailure("physical parameter bundle missing")
    diffusion = _binary64_fraction(parameters.get("particle_diffusion_binary64_hex"))
    stiffness = _binary64_fraction(parameters.get("ou_stiffness_binary64_hex"))
    mean = _binary64_fraction(parameters.get("ou_mean_binary64_hex"))
    period = _fraction(parameters.get("transverse_period_exact"))
    if diffusion <= 0 or stiffness <= 0 or period <= 0:
        raise StationaryIntegralVerificationFailure("nonpositive physical parameter")
    coefficients = {
        "midpoint": stiffness / diffusion,
        "relative_parallel": stiffness / (4 * diffusion),
    }

    config_rows = configuration.get("configurations")
    bundle_rows = bundle.get("rows")
    mappings = member.get("configuration_semantic_ids")
    order = member.get("configuration_order")
    if (
        type(config_rows) is not list
        or type(bundle_rows) is not list
        or type(mappings) is not list
        or type(order) is not list
        or len(config_rows) != 12
        or len(bundle_rows) != 12
        or len(mappings) != 12
        or len(order) != 12
    ):
        raise StationaryIntegralVerificationFailure("fixed 12-row cardinality drift")
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
            raise StationaryIntegralVerificationFailure("invalid semantic member mapping")
        label = mapping["authority_label"]
        if label in mapping_by_label:
            raise StationaryIntegralVerificationFailure("duplicate semantic member mapping")
        mapping_by_label[label] = mapping
    if set(mapping_by_label) != set(order):
        raise StationaryIntegralVerificationFailure("member mapping/order mismatch")

    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        raise StationaryIntegralVerificationFailure("configuration dynamics missing")
    transverse_start = _fraction(dynamics.get("transverse_domain_start_exact"))
    transverse_width = _fraction(dynamics.get("transverse_period_exact"))
    if transverse_width != period:
        raise StationaryIntegralVerificationFailure("transverse period authority mismatch")
    parameter_digest = _domain_digest(
        b"encounter-fixed-row-physical-parameter-bundle-v1\0",
        {
            "physical_parameter_bundle": parameters,
            "unit_table": reference.get("unit_table"),
        },
    )
    role_bindings = member.get("role_bindings")
    member_semantics = member.get("member_semantics")
    if (
        type(role_bindings) is not dict
        or type(member_semantics) is not dict
        or role_bindings.get("reference_density_source")
        != {"path": REFERENCE_PATH, "sha256": REFERENCE_SHA256}
        or role_bindings.get("ideal_formula_source")
        != {"path": FORMULA_PATH, "sha256": FORMULA_SHA256}
        or role_bindings.get("configuration_source")
        != {"path": CONFIGURATION_PATH, "sha256": CONFIGURATION_SHA256}
        or type(role_bindings.get("factorization_source")) is not dict
        or re.fullmatch(
            r"[0-9a-f]{64}",
            role_bindings["factorization_source"].get("sha256", ""),
        )
        is None
        or member_semantics.get("scalar_convention")
        != "complex_inner_product_conjugate_first_factor"
    ):
        raise StationaryIntegralVerificationFailure("member role binding drift")

    rows: list[dict[str, Any]] = []
    gaussian_cells = 0
    periodic_cells = 0
    largest_relative_width = Fraction(0)
    smallest_positive_lower: Fraction | None = None
    all_primary_contain_sentinel = True
    partition_cells_reconstructed = 0

    for index, (config_row, bundle_row) in enumerate(zip(config_rows, bundle_rows, strict=True)):
        if type(config_row) is not dict or type(bundle_row) is not dict:
            raise StationaryIntegralVerificationFailure("invalid source row object")
        label = config_row.get("label")
        if (
            type(label) is not str
            or order[index] != label
            or bundle_row.get("configuration_index") != index
            or bundle_row.get("configuration_label") != label
        ):
            raise StationaryIntegralVerificationFailure("configuration/bundle row join drift")
        mapping = mapping_by_label[label]
        expected_states = config_row.get("expected_states")
        if type(expected_states) is not int or isinstance(expected_states, bool):
            raise StationaryIntegralVerificationFailure("invalid expected tensor state count")
        axis_sizes: list[int] = []
        for coordinate in AXES:
            axis = config_row.get(coordinate)
            if type(axis) is not dict or type(axis.get("size")) is not int:
                raise StationaryIntegralVerificationFailure("configuration axis missing")
            axis_sizes.append(axis["size"])
        if math.prod(axis_sizes) != expected_states:
            raise StationaryIntegralVerificationFailure("tensor state count/product mismatch")

        row_binding = bundle_row.get("row_manifest")
        if type(row_binding) is not dict or set(row_binding) != {"byte_length", "path", "sha256"}:
            raise StationaryIntegralVerificationFailure("row-manifest binding drift")
        row_relative = _join_report_relative(BUNDLE_ROOT, row_binding["path"])
        row_manifest = _manifest_json(
            row_relative,
            row_binding["sha256"],
            200_000,
            row_binding["byte_length"],
        )
        axes = row_manifest.get("axes")
        if type(axes) is not list or len(axes) != len(AXES):
            raise StationaryIntegralVerificationFailure("row axis-manifest cardinality drift")

        partition_hashes: list[str] = []
        partitions: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for coordinate, axis_entry in zip(AXES, axes, strict=True):
            if type(axis_entry) is not dict or axis_entry.get("coordinate") != coordinate:
                raise StationaryIntegralVerificationFailure("axis-manifest order drift")
            partition_binding = axis_entry.get("partition_file")
            if type(partition_binding) is not dict or set(partition_binding) != {
                "byte_length",
                "path",
                "sha256",
            }:
                raise StationaryIntegralVerificationFailure("partition-file binding drift")
            partition_relative = _join_report_relative(BUNDLE_ROOT, partition_binding["path"])
            partition = _manifest_json(
                partition_relative,
                partition_binding["sha256"],
                1_000_000,
                partition_binding["byte_length"],
            )
            config_axis = config_row.get(coordinate)
            if type(config_axis) is not dict:
                raise StationaryIntegralVerificationFailure("configuration axis missing")
            expected_partition = _independent_partition(
                coordinate,
                config_axis,
                transverse_start,
                transverse_width,
            )
            if not _exactly(partition, expected_partition):
                raise StationaryIntegralVerificationFailure(
                    f"partition reconstruction mismatch: {label}/{coordinate}"
                )
            partition_cells_reconstructed += partition["size"]
            partition_hashes.append(partition_binding["sha256"])
            partitions.append((partition, partition_binding))

        member_digest = _domain_digest(
            b"encounter-fixed-row-correlated-member-v1\0",
            {
                "authority_label": label,
                "coordinate_order": list(AXES),
                "factorization_source_sha256": role_bindings["factorization_source"]["sha256"],
                "ideal_formula_source_sha256": role_bindings["ideal_formula_source"]["sha256"],
                "normalization": (
                    "one_global_gauge_and_globally_normalized_pi_no_box_renormalization"
                ),
                "partition_sha256s": partition_hashes,
                "physical_parameter_digest": parameter_digest,
                "reference_density_source_sha256": role_bindings["reference_density_source"][
                    "sha256"
                ],
                "refinement_family_id": mapping["refinement_family_id"],
                "refinement_member_id": mapping["refinement_member_id"],
                "scalar_convention": member_semantics["scalar_convention"],
            },
        )

        axis_outputs: list[dict[str, Any]] = []
        axis_cell_sums: list[ExactBounds] = []
        axis_direct_masses: list[ExactBounds] = []
        for coordinate, (partition, partition_binding) in zip(AXES, partitions, strict=True):
            primary_cells: list[ExactBounds] = []
            sentinel_cells: list[ExactBounds] = []
            for segments in partition["cell_segments_exact"]:
                if type(segments) is not list or not segments:
                    raise StationaryIntegralVerificationFailure("empty partition cell")
                if coordinate == "relative_perpendicular":
                    cell_volume = Fraction(0)
                    for segment in segments:
                        if type(segment) is not list or len(segment) != 2:
                            raise StationaryIntegralVerificationFailure(
                                "invalid periodic partition segment"
                            )
                        cell_volume += _fraction(segment[1]) - _fraction(segment[0])
                    primary = ExactBounds(cell_volume / period, cell_volume / period)
                    sentinel = primary
                    periodic_cells += 1
                else:
                    primary_pieces: list[ExactBounds] = []
                    sentinel_pieces: list[ExactBounds] = []
                    centre = mean if coordinate == "midpoint" else Fraction(0)
                    for segment in segments:
                        if type(segment) is not list or len(segment) != 2:
                            raise StationaryIntegralVerificationFailure(
                                "invalid Gaussian partition segment"
                            )
                        lower = _fraction(segment[0])
                        upper = _fraction(segment[1])
                        primary_pieces.append(
                            _normal_segment_mass(
                                lower,
                                upper,
                                coefficients[coordinate],
                                centre,
                                PRIMARY_BITS,
                            )
                        )
                        sentinel_pieces.append(
                            _normal_segment_mass(
                                lower,
                                upper,
                                coefficients[coordinate],
                                centre,
                                SENTINEL_BITS,
                            )
                        )
                    primary = _sum_bounds(primary_pieces)
                    sentinel = _sum_bounds(sentinel_pieces)
                    gaussian_cells += 1
                if not primary.encloses(sentinel):
                    all_primary_contain_sentinel = False
                    raise StationaryIntegralVerificationFailure(
                        "320-bit cell interval misses 640-bit sentinel"
                    )
                if primary.lower <= 0:
                    raise StationaryIntegralVerificationFailure(
                        "nonpositive physical cell-mass lower bound"
                    )
                relative_width = (primary.upper - primary.lower) / primary.lower
                largest_relative_width = max(largest_relative_width, relative_width)
                smallest_positive_lower = (
                    primary.lower
                    if smallest_positive_lower is None
                    else min(smallest_positive_lower, primary.lower)
                )
                primary_cells.append(primary)
                sentinel_cells.append(sentinel)

            cell_sum = _sum_bounds(primary_cells)
            sentinel_sum = _sum_bounds(sentinel_cells)
            domain_start = _fraction(partition["domain_start_exact"])
            domain_end = domain_start + _fraction(partition["domain_width_exact"])
            if coordinate == "relative_perpendicular":
                direct = ExactBounds(Fraction(1), Fraction(1))
                sentinel_direct = direct
            else:
                centre = mean if coordinate == "midpoint" else Fraction(0)
                direct = _normal_segment_mass(
                    domain_start,
                    domain_end,
                    coefficients[coordinate],
                    centre,
                    PRIMARY_BITS,
                )
                sentinel_direct = _normal_segment_mass(
                    domain_start,
                    domain_end,
                    coefficients[coordinate],
                    centre,
                    SENTINEL_BITS,
                )
            joint = cell_sum.overlap(direct)
            if not cell_sum.encloses(sentinel_sum) or not direct.encloses(sentinel_direct):
                raise StationaryIntegralVerificationFailure(
                    "320-bit axis interval misses 640-bit sentinel"
                )
            axis_cell_sums.append(cell_sum)
            axis_direct_masses.append(direct)
            axis_outputs.append(
                {
                    "cell_count": partition["size"],
                    "cell_mass_intervals": [
                        {
                            "cell_index": cell_index,
                            **_interval_object(interval),
                        }
                        for cell_index, interval in enumerate(primary_cells)
                    ],
                    "coordinate": coordinate,
                    "direct_domain_mass_interval": _interval_object(direct),
                    "formula_id": (
                        "periodic_cell_volume_divided_by_W_v1"
                        if coordinate == "relative_perpendicular"
                        else f"globally_normalized_gaussian_erf_{coordinate}_v1"
                    ),
                    "joint_domain_mass_interval": _interval_object(joint),
                    "partition_path": partition_binding["path"],
                    "partition_sha256": partition_binding["sha256"],
                    "sum_of_cells_mass_interval": _interval_object(cell_sum),
                }
            )

        factorized_box = ExactBounds(Fraction(1), Fraction(1))
        direct_box = ExactBounds(Fraction(1), Fraction(1))
        for cell_sum, direct_mass in zip(axis_cell_sums, axis_direct_masses, strict=True):
            factorized_box = factorized_box.nonnegative_product(cell_sum)
            direct_box = direct_box.nonnegative_product(direct_mass)
        joint_box = factorized_box.overlap(direct_box)
        if not (0 < joint_box.lower <= joint_box.upper < 1):
            raise StationaryIntegralVerificationFailure(
                "finite box mass must be strictly below one"
            )
        rows.append(
            {
                "axes": axis_outputs,
                "configuration_index": index,
                "configuration_label": label,
                "factorized_box_mass_interval": _interval_object(factorized_box),
                "factorized_tensor_cell_mass_formula": (
                    "M_pi[i_midpoint,i_relative_parallel,i_relative_perpendicular]="
                    "M_midpoint[i_midpoint]*M_relative_parallel[i_relative_parallel]*"
                    "M_relative_perpendicular[i_relative_perpendicular]"
                ),
                "joint_box_mass_interval": _interval_object(joint_box),
                "member_digest_sha256": member_digest,
                "refinement_family_id": mapping["refinement_family_id"],
                "refinement_member_id": mapping["refinement_member_id"],
                "single_domain_box_mass_interval": _interval_object(direct_box),
                "tensor_state_count": expected_states,
            }
        )

    if (
        gaussian_cells != 3_446
        or periodic_cells != 1_591
        or partition_cells_reconstructed != 5_037
        or smallest_positive_lower is None
    ):
        raise StationaryIntegralVerificationFailure("fixed family cell-count identity drift")

    builder_payload, builder_sha = _report_snapshot(BUILDER_PATH, 1_000_000)
    if not builder_payload:
        raise StationaryIntegralVerificationFailure("empty builder source")
    expected = {
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
            "sentinel_method_id": ("directed_mpfr_640_reference_density_sentinel_v1"),
            "sentinel_precision_bits": SENTINEL_BITS,
            "sentinel_semantics": (
                "same_backend_higher_precision_containment_not_backend_independence"
            ),
        },
        "rows": rows,
        "schema": SCHEMA,
        "source_pins": {
            "builder_source": {
                "path": BUILDER_PATH,
                "sha256": builder_sha,
            },
            "configuration_source": {
                "path": CONFIGURATION_PATH,
                "sha256": CONFIGURATION_SHA256,
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
            "production_partition_bundle": {
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
        },
        "status": STATUS,
        "summary": {
            "all_primary_intervals_contain_640_bit_sentinels": (all_primary_contain_sentinel),
            "configuration_count": len(rows),
            "factorized_axis_cell_count": gaussian_cells + periodic_cells,
            "gaussian_axis_cell_count": gaussian_cells,
            "maximum_primary_cell_relative_width_exact": _fraction_string(largest_relative_width),
            "minimum_positive_primary_cell_lower_exact": _fraction_string(smallest_positive_lower),
            "periodic_axis_cell_count": periodic_cells,
            "total_virtual_tensor_state_count": sum(row["tensor_state_count"] for row in rows),
        },
    }
    counters = {
        "configuration_count": len(rows),
        "factorized_axis_cell_count": partition_cells_reconstructed,
        "gaussian_axis_cell_count": gaussian_cells,
        "periodic_axis_cell_count": periodic_cells,
        "total_virtual_tensor_state_count": sum(row["tensor_state_count"] for row in rows),
    }
    return expected, counters


def validate(artifact_path: Path) -> dict[str, Any]:
    expected, counters = _independent_expected_artifact()
    artifact_bytes, artifact_sha = _stable_absolute_snapshot(artifact_path, 4_000_000)
    artifact = _parse_canonical_json(
        artifact_bytes, os.fspath(Path(os.path.abspath(artifact_path)))
    )
    expected_bytes = _canonical_bytes(expected)
    if not _exactly(artifact, expected) or artifact_bytes != expected_bytes:
        raise StationaryIntegralVerificationFailure(
            "artifact differs from independent exact reconstruction"
        )
    _require_exact_false_map(
        artifact.get("claim_boundary"),
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
        "artifact",
    )
    return {
        "artifact_sha256": artifact_sha,
        **counters,
        "status": VALIDATION_STATUS,
    }


def _artifact_argument(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPORT / candidate
    return Path(os.path.abspath(candidate))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        default=DEFAULT_ARTIFACT.as_posix(),
        help="canonical report-relative or absolute read-only artifact path",
    )
    arguments = parser.parse_args()
    try:
        summary = validate(_artifact_argument(arguments.artifact))
    except (StationaryIntegralVerificationFailure, OSError, ValueError) as error:
        print(f"HOLD {error}", file=sys.stderr)
        return 1
    print("PASS " + json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
