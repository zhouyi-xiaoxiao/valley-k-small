"""Portable strict-binary64 backend for the packed scalar power stream.

The adjacent C source evaluates the nominal packed ``P.T`` recurrence and the
two positive reductions used by the batched scalar method.  Its accumulation
order is byte-compatible with the current scalar NumPy action: self first,
then incoming-forward and incoming-backward for each dimension in increasing
dimension order.

This module deliberately has no physical-control, selector, scientific-budget,
or filesystem-path argument.  All numerical inputs are caller-supplied and
remain ``CALLER_SUPPLIED_UNCLASSIFIED``.  The backend is a method accelerator,
not an authority boundary: it never authorizes science, F0, or a resource
PASS.  It owns read-only native-endian copies of all inputs and allocates every
output privately.
"""

from __future__ import annotations

import ctypes
import dataclasses
import hashlib
import hmac
import json
import math
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np

try:
    import rate_defined_tensor_f0_packed as packed
except ImportError:  # pragma: no cover - package-style import fallback.
    from . import rate_defined_tensor_f0_packed as packed


SCHEMA: Final = "rate_defined_tensor_f0_compiled_power_stream_v1"
BUILD_RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_compiled_build_receipt_v1"
BACKEND_RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_compiled_backend_receipt_v1"
ACTION_LEDGER_SCHEMA: Final = "rate_defined_tensor_f0_compiled_action_ledger_v1"
REDUCTION_LEDGER_SCHEMA: Final = "rate_defined_tensor_f0_compiled_reduction_ledger_v1"
STREAM_RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_compiled_stream_receipt_v1"
METHOD_STATUS: Final = "COMPILED_METHOD_BACKEND_ONLY_NOT_F0"
INPUT_PROVENANCE_CLASSIFICATION: Final = "CALLER_SUPPLIED_UNCLASSIFIED"
ACCUMULATION_ORDER: Final = (
    "self_then_each_dimension_increasing_incoming_forward_then_incoming_backward_v1"
)
FLOAT64_ETA: Final = Fraction(1, 2**1074)
FLOAT64_UNIT_ROUNDOFF: Final = Fraction(1, 2**53)
MAXIMUM_DIMENSIONS: Final = 3
MAXIMUM_POWER_INDEX: Final = 1_000_000

_MODULE_PATH: Final = Path(__file__).resolve(strict=True)
_C_SOURCE_PATH: Final = _MODULE_PATH.with_suffix(".c").resolve(strict=True)
_MODULE_SHA256_AT_IMPORT: Final = hashlib.sha256(_MODULE_PATH.read_bytes()).hexdigest()
_C_SOURCE_SHA256_AT_IMPORT: Final = hashlib.sha256(
    _C_SOURCE_PATH.read_bytes()
).hexdigest()
_BUILD_LOCK: Final = threading.Lock()
_DOUBLE_POINTER: Final = ctypes.POINTER(ctypes.c_double)
_SIZE_POINTER: Final = ctypes.POINTER(ctypes.c_size_t)
_UINT8_POINTER: Final = ctypes.POINTER(ctypes.c_uint8)


class CompiledPowerStreamFailure(RuntimeError):
    """Fail-closed method-layer error."""


@dataclass(frozen=True, slots=True)
class GenericPackedTensorInput:
    """Generic numerical input; names and roles cannot classify provenance."""

    tensor_shape: tuple[int, ...]
    periodic: tuple[bool, ...]
    p_self_center: np.ndarray
    p_forward_center: tuple[np.ndarray, ...]
    p_backward_center: tuple[np.ndarray, ...]
    killing_center: np.ndarray
    reduction_block_size: int


@dataclass(frozen=True, slots=True)
class RuntimeProbe:
    abi_version: int
    sizeof_double: int
    flt_radix: int
    dbl_mant_dig: int
    dbl_max_exp: int
    dbl_min_exp: int
    flt_eval_method: int
    rounding_mode: int
    fe_tonearest_value: int
    binary64_layout: bool
    tonearest_active: bool
    smallest_subnormal_preserved: bool
    subnormal_arithmetic_preserved: bool


@dataclass(frozen=True, slots=True)
class CompiledBuildReceipt:
    schema: str
    status: str
    c_source_sha256: str
    python_wrapper_sha256: str
    compiler_binary_sha256: str
    compiler_identity_sha256: str
    normalized_compile_command_sha256: str
    post_link_normalization_sha256: str
    compiled_binary_sha256: str
    target_identity_sha256: str
    optimization_level: str
    fast_math_enabled: bool
    fp_contraction_enabled: bool
    unsafe_fp_optimizations_enabled: bool
    runtime_probe: RuntimeProbe
    input_provenance_classification: str
    authorizes_scientific_execution: bool
    science_executed: bool
    resource_pass: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class ActionOperationLedger:
    schema: str
    states: int
    dimensions: int
    self_multiplication_count: int
    present_incoming_edge_count: int
    present_incoming_multiplication_count: int
    accumulator_addition_count: int
    actual_arithmetic_operation_count: int
    conservative_arithmetic_operation_budget: int
    maximum_dependency_operation_count: int
    underflow_event_operation_budget: int
    underflow_unit_hex: str
    accumulation_order: str
    relative_error_model: str
    underflow_error_model: str
    changes_upstream_enclosure: bool


@dataclass(frozen=True, slots=True)
class ReductionOperationLedger:
    schema: str
    reduction: str
    states: int
    block_size: int
    block_count: int
    multiplication_count: int
    addition_count: int
    actual_arithmetic_operation_count: int
    upstream_enclosure_operation_count: int
    maximum_dependency_operation_count: int
    underflow_event_operation_budget: int
    underflow_unit_hex: str
    accumulation_order: str
    changes_upstream_enclosure: bool


@dataclass(frozen=True, slots=True)
class CompiledBackendReceipt:
    schema: str
    status: str
    tensor_shape: tuple[int, ...]
    periodic: tuple[bool, ...]
    states: int
    dimensions: int
    reduction_block_size: int
    input_binding_sha256: str
    p_self_sha256: str
    p_forward_sha256: tuple[str, ...]
    p_backward_sha256: tuple[str, ...]
    killing_sha256: str
    owned_native_readonly_inputs: bool
    input_provenance_classification: str
    control_exclusion_proved: bool
    science_free_proved: bool
    build: CompiledBuildReceipt
    action_operations: ActionOperationLedger
    mass_reduction_operations: ReductionOperationLedger
    killing_dot_operations: ReductionOperationLedger
    authorizes_scientific_execution: bool
    science_executed: bool
    resource_pass: bool
    f0_pass: bool
    receipt_sha256: str


@dataclass(frozen=True, slots=True)
class PositiveReductionResult:
    nominal: float
    exact_upper_numerator: int
    exact_upper_denominator: int
    roundoff_radius_numerator: int
    roundoff_radius_denominator: int
    ledger: ReductionOperationLedger

    @property
    def exact_upper(self) -> Fraction:
        return Fraction(self.exact_upper_numerator, self.exact_upper_denominator)

    @property
    def roundoff_radius(self) -> Fraction:
        return Fraction(
            self.roundoff_radius_numerator,
            self.roundoff_radius_denominator,
        )


@dataclass(frozen=True, slots=True)
class CompiledPowerStreamReceipt:
    schema: str
    status: str
    backend_receipt_sha256: str
    initial_raw_sha256: str
    maximum_power_index: int
    p_action_call_count: int
    mass_reduction_call_count: int
    killing_dot_call_count: int
    mass_stream_raw_sha256: str
    killing_dot_stream_raw_sha256: str
    final_power_raw_sha256: str
    stream_binding_sha256: str
    full_power_arrays_retained: int
    scalar_streams_retained: bool
    final_power_retained: bool
    private_owned_readonly_outputs: bool
    input_provenance_classification: str
    control_exclusion_proved: bool
    science_free_proved: bool
    authorizes_scientific_execution: bool
    science_executed: bool
    resource_pass: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class CompiledPowerStreamResult:
    mass_by_power: np.ndarray
    killing_dot_by_power: np.ndarray
    final_power: np.ndarray
    receipt: CompiledPowerStreamReceipt


class _CRuntimeProbe(ctypes.Structure):
    _fields_ = [
        ("abi_version", ctypes.c_uint32),
        ("sizeof_double", ctypes.c_uint32),
        ("flt_radix", ctypes.c_uint32),
        ("dbl_mant_dig", ctypes.c_uint32),
        ("dbl_max_exp", ctypes.c_int32),
        ("dbl_min_exp", ctypes.c_int32),
        ("flt_eval_method", ctypes.c_int32),
        ("rounding_mode", ctypes.c_int32),
        ("fe_tonearest_value", ctypes.c_int32),
        ("binary64_layout", ctypes.c_uint32),
        ("tonearest_active", ctypes.c_uint32),
        ("smallest_subnormal_preserved", ctypes.c_uint32),
        ("subnormal_arithmetic_preserved", ctypes.c_uint32),
    ]


@dataclass(frozen=True, slots=True)
class _CompiledArtifact:
    library: ctypes.CDLL
    binary_path: Path
    receipt: CompiledBuildReceipt


_ARTIFACT: _CompiledArtifact | None = None


def _sha256_bytes(payload: bytes | memoryview) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(1024 * 1024)
    with path.open("rb", buffering=0) as source:
        while True:
            count = source.readinto(scratch)
            if count == 0:
                break
            digest.update(memoryview(scratch)[:count])
    return digest.hexdigest()


def _raw_sha256(array: np.ndarray) -> str:
    return _sha256_bytes(memoryview(array).cast("B"))


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _canonical_json_sha256(payload: object) -> str:
    return _sha256_bytes(_canonical_json_bytes(payload))


def _dataclass_payload(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _dataclass_payload(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if type(value) is tuple:
        return [_dataclass_payload(item) for item in value]
    if type(value) in {str, int, bool} or value is None:
        return value
    raise CompiledPowerStreamFailure(
        "receipt contains a noncanonical value"
    )


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _readonly_owned_float64_copy(
    value: object,
    *,
    expected_size: int,
    label: str,
) -> np.ndarray:
    if (
        type(value) is not np.ndarray
        or value.dtype != np.dtype(np.float64)
        or not value.dtype.isnative
        or value.shape != (expected_size,)
        or not value.flags.c_contiguous
    ):
        raise CompiledPowerStreamFailure(
            f"{label} must be a contiguous native exact float64 ndarray"
        )
    result = np.array(value, dtype=np.float64, copy=True, order="C", subok=False)
    if (
        not result.flags.owndata
        or result.base is not None
        or not result.flags.aligned
        or not bool(np.all(np.isfinite(result)))
        or bool(np.any(result < 0.0))
    ):
        raise CompiledPowerStreamFailure(
            f"{label} is nonfinite, negative, or not privately owned"
        )
    result.setflags(write=False)
    return result


def _readonly_output(array: np.ndarray) -> np.ndarray:
    if (
        type(array) is not np.ndarray
        or array.dtype != np.dtype(np.float64)
        or not array.dtype.isnative
        or not array.flags.c_contiguous
        or not array.flags.owndata
        or array.base is not None
        or not array.flags.aligned
        or not bool(np.all(np.isfinite(array)))
        or bool(np.any(array < 0.0))
    ):
        raise CompiledPowerStreamFailure("compiled output is not canonical")
    array.setflags(write=False)
    return array


def _find_compiler() -> Path:
    candidates: list[Path] = []
    for literal in ("/usr/bin/clang", "/usr/bin/cc", "/opt/homebrew/bin/clang"):
        candidate = Path(literal)
        if candidate.is_file() and os.access(candidate, os.X_OK):
            candidates.append(candidate)
    for name in ("clang", "cc"):
        resolved = shutil.which(name)
        if resolved is not None:
            candidate = Path(resolved).resolve()
            if candidate.is_file() and candidate not in candidates:
                candidates.append(candidate)
    if not candidates:
        raise CompiledPowerStreamFailure("no C11 compiler is available")
    return candidates[0].resolve()


def _compiler_flags() -> tuple[str, ...]:
    shared_flag = "-dynamiclib" if sys.platform == "darwin" else "-shared"
    platform_link_flags = (
        (
            "-Wl,-install_name,@rpath/librdf0_compiled_power_stream_v1.dylib",
        )
        if sys.platform == "darwin"
        else ("-Wl,--build-id=none",)
    )
    return (
        "-std=c11",
        "-O3",
        "-fPIC",
        shared_flag,
        "-ffp-contract=off",
        "-fno-fast-math",
        "-fno-associative-math",
        "-fno-unsafe-math-optimizations",
        "-frounding-math",
        "-fvisibility=hidden",
        *platform_link_flags,
    )


def _normalize_generated_binary(path: Path) -> str:
    """Remove only nondeterministic linker identity while preserving validity."""

    if sys.platform != "darwin":
        return _canonical_json_sha256(
            ["elf_build_id_disabled_by_link_command_v1"]
        )
    payload = bytearray(path.read_bytes())
    if len(payload) < 32 or struct.unpack_from("<I", payload, 0)[0] != 0xFEEDFACF:
        raise CompiledPowerStreamFailure(
            "generated Darwin library is not a little-endian Mach-O 64 image"
        )
    command_count = struct.unpack_from("<I", payload, 16)[0]
    offset = 32
    uuid_offset: int | None = None
    for _ in range(command_count):
        if offset + 8 > len(payload):
            raise CompiledPowerStreamFailure("Mach-O load commands are truncated")
        command, command_size = struct.unpack_from("<II", payload, offset)
        if command_size < 8 or offset + command_size > len(payload):
            raise CompiledPowerStreamFailure("Mach-O load command is malformed")
        if command == 0x1B:
            if command_size != 24 or uuid_offset is not None:
                raise CompiledPowerStreamFailure("Mach-O UUID command is noncanonical")
            uuid_offset = offset + 8
        offset += command_size
    if uuid_offset is None:
        raise CompiledPowerStreamFailure("Mach-O UUID command is absent")
    payload[uuid_offset : uuid_offset + 16] = b"\x00" * 16
    deterministic_uuid = bytearray(hashlib.sha256(payload).digest()[:16])
    deterministic_uuid[6] = (deterministic_uuid[6] & 0x0F) | 0x50
    deterministic_uuid[8] = (deterministic_uuid[8] & 0x3F) | 0x80
    payload[uuid_offset : uuid_offset + 16] = deterministic_uuid
    path.write_bytes(payload)
    try:
        signed = subprocess.run(
            [
                "/usr/bin/codesign",
                "--force",
                "--sign",
                "-",
                "--timestamp=none",
                str(path),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CompiledPowerStreamFailure(
            "deterministic Mach-O ad-hoc signing failed"
        ) from error
    if signed.returncode != 0:
        diagnostics = signed.stdout.decode("utf-8", errors="replace")[-2000:]
        raise CompiledPowerStreamFailure(
            f"deterministic Mach-O ad-hoc signing failed: {diagnostics}"
        )
    return _canonical_json_sha256(
        [
            "macho_lc_uuid_sha256_zeroed_image_prefix16_uuidv5_bits_v1",
            "codesign_force_adhoc_timestamp_none_v1",
        ]
    )


def _configure_library(library: ctypes.CDLL) -> None:
    pointer_pointer = ctypes.POINTER(_DOUBLE_POINTER)
    library.rdf0_runtime_probe.argtypes = [ctypes.POINTER(_CRuntimeProbe)]
    library.rdf0_runtime_probe.restype = ctypes.c_int
    library.rdf0_apply_p_transpose.argtypes = [
        ctypes.c_size_t,
        ctypes.c_uint32,
        _SIZE_POINTER,
        _UINT8_POINTER,
        _DOUBLE_POINTER,
        pointer_pointer,
        pointer_pointer,
        _DOUBLE_POINTER,
        _DOUBLE_POINTER,
    ]
    library.rdf0_apply_p_transpose.restype = ctypes.c_int
    library.rdf0_positive_mass.argtypes = [
        ctypes.c_size_t,
        _DOUBLE_POINTER,
        ctypes.POINTER(ctypes.c_double),
    ]
    library.rdf0_positive_mass.restype = ctypes.c_int
    library.rdf0_positive_dot.argtypes = [
        ctypes.c_size_t,
        _DOUBLE_POINTER,
        _DOUBLE_POINTER,
        ctypes.POINTER(ctypes.c_double),
    ]
    library.rdf0_positive_dot.restype = ctypes.c_int
    library.rdf0_power_stream.argtypes = [
        ctypes.c_size_t,
        ctypes.c_uint32,
        _SIZE_POINTER,
        _UINT8_POINTER,
        _DOUBLE_POINTER,
        pointer_pointer,
        pointer_pointer,
        _DOUBLE_POINTER,
        _DOUBLE_POINTER,
        ctypes.c_size_t,
        _DOUBLE_POINTER,
        _DOUBLE_POINTER,
        _DOUBLE_POINTER,
    ]
    library.rdf0_power_stream.restype = ctypes.c_int


def _runtime_probe(library: ctypes.CDLL) -> RuntimeProbe:
    raw = _CRuntimeProbe()
    status = library.rdf0_runtime_probe(ctypes.byref(raw))
    if status != 0:
        raise CompiledPowerStreamFailure(
            f"compiled binary64 runtime probe failed with code {status}"
        )
    probe = RuntimeProbe(
        abi_version=int(raw.abi_version),
        sizeof_double=int(raw.sizeof_double),
        flt_radix=int(raw.flt_radix),
        dbl_mant_dig=int(raw.dbl_mant_dig),
        dbl_max_exp=int(raw.dbl_max_exp),
        dbl_min_exp=int(raw.dbl_min_exp),
        flt_eval_method=int(raw.flt_eval_method),
        rounding_mode=int(raw.rounding_mode),
        fe_tonearest_value=int(raw.fe_tonearest_value),
        binary64_layout=bool(raw.binary64_layout),
        tonearest_active=bool(raw.tonearest_active),
        smallest_subnormal_preserved=bool(raw.smallest_subnormal_preserved),
        subnormal_arithmetic_preserved=bool(raw.subnormal_arithmetic_preserved),
    )
    if (
        probe.abi_version != 1
        or probe.sizeof_double != 8
        or probe.flt_radix != 2
        or probe.dbl_mant_dig != 53
        or probe.dbl_max_exp != 1024
        or probe.dbl_min_exp != -1021
        or probe.flt_eval_method != 0
        or not probe.binary64_layout
        or not probe.tonearest_active
        or probe.rounding_mode != probe.fe_tonearest_value
        or not probe.smallest_subnormal_preserved
        or not probe.subnormal_arithmetic_preserved
    ):
        raise CompiledPowerStreamFailure(
            "compiled runtime is not strict FE_TONEAREST binary64"
        )
    return probe


def _compile_artifact() -> _CompiledArtifact:
    global _ARTIFACT
    with _BUILD_LOCK:
        if _ARTIFACT is not None:
            return _ARTIFACT
        if (
            _file_sha256(_MODULE_PATH) != _MODULE_SHA256_AT_IMPORT
            or _file_sha256(_C_SOURCE_PATH) != _C_SOURCE_SHA256_AT_IMPORT
        ):
            raise CompiledPowerStreamFailure(
                "compiled backend source changed after module import"
            )
        if sys.platform not in {"darwin", "linux"}:
            raise CompiledPowerStreamFailure(
                "the strict compiled wrapper supports Darwin and Linux"
            )
        compiler = _find_compiler()
        try:
            identity_process = subprocess.run(
                [str(compiler), "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise CompiledPowerStreamFailure(
                "compiler identity query failed"
            ) from error
        identity = bytes(identity_process.stdout)
        flags = _compiler_flags()
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        build_directory = Path(
            tempfile.mkdtemp(prefix="rdf0_compiled_power_stream_v1_")
        ).resolve()
        binary_path = build_directory / f"librdf0_compiled_power_stream_v1{suffix}"
        command = [
            str(compiler),
            *flags,
            str(_C_SOURCE_PATH),
            "-o",
            str(binary_path),
        ]
        if sys.platform == "linux":
            command.append("-lm")
        normalized_command = [
            "$COMPILER",
            *flags,
            "$C_SOURCE",
            "-o",
            "$OUTPUT",
        ]
        if sys.platform == "linux":
            normalized_command.append("-lm")
        try:
            process = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise CompiledPowerStreamFailure("C compilation failed") from error
        if process.returncode != 0 or not binary_path.is_file():
            diagnostics = process.stdout.decode("utf-8", errors="replace")[-4000:]
            raise CompiledPowerStreamFailure(
                f"C compilation failed closed: {diagnostics}"
            )
        post_link_normalization = _normalize_generated_binary(binary_path)
        try:
            library = ctypes.CDLL(str(binary_path))
        except OSError as error:
            raise CompiledPowerStreamFailure(
                "compiled library could not be loaded"
            ) from error
        _configure_library(library)
        probe = _runtime_probe(library)
        target_payload = {
            "machine": platform.machine(),
            "platform": sys.platform,
            "pointer_bits": ctypes.sizeof(ctypes.c_void_p) * 8,
            "python_byteorder": sys.byteorder,
        }
        receipt = CompiledBuildReceipt(
            schema=BUILD_RECEIPT_SCHEMA,
            status=METHOD_STATUS,
            c_source_sha256=_C_SOURCE_SHA256_AT_IMPORT,
            python_wrapper_sha256=_MODULE_SHA256_AT_IMPORT,
            compiler_binary_sha256=_file_sha256(compiler),
            compiler_identity_sha256=_sha256_bytes(identity),
            normalized_compile_command_sha256=_canonical_json_sha256(
                normalized_command
            ),
            post_link_normalization_sha256=post_link_normalization,
            compiled_binary_sha256=_file_sha256(binary_path),
            target_identity_sha256=_canonical_json_sha256(target_payload),
            optimization_level="O3",
            fast_math_enabled=False,
            fp_contraction_enabled=False,
            unsafe_fp_optimizations_enabled=False,
            runtime_probe=probe,
            input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
            authorizes_scientific_execution=False,
            science_executed=False,
            resource_pass=False,
            f0_pass=False,
        )
        _ARTIFACT = _CompiledArtifact(
            library=library,
            binary_path=binary_path,
            receipt=receipt,
        )
        return _ARTIFACT


def _gamma(index: int) -> Fraction:
    if type(index) is not int or index < 0:
        raise CompiledPowerStreamFailure("gamma index is invalid")
    product = index * FLOAT64_UNIT_ROUNDOFF
    if product >= 1:
        raise CompiledPowerStreamFailure("gamma index is unresolved")
    return product / (1 - product)


def _positive_enclosure(
    nominal: float,
    ledger: ReductionOperationLedger,
) -> PositiveReductionResult:
    if (
        type(nominal) is not float
        or not math.isfinite(nominal)
        or nominal < 0.0
    ):
        raise CompiledPowerStreamFailure("positive nominal is invalid")
    operations = ledger.upstream_enclosure_operation_count
    gamma = _gamma(operations)
    underflow = operations * FLOAT64_ETA
    exact_upper = (Fraction.from_float(nominal) + underflow) / (1 - gamma)
    radius = gamma * exact_upper + underflow
    return PositiveReductionResult(
        nominal=nominal,
        exact_upper_numerator=exact_upper.numerator,
        exact_upper_denominator=exact_upper.denominator,
        roundoff_radius_numerator=radius.numerator,
        roundoff_radius_denominator=radius.denominator,
        ledger=ledger,
    )


def _action_ledger(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
) -> ActionOperationLedger:
    states = math.prod(shape)
    dimensions = len(shape)
    present_edges = sum(
        states if is_periodic else states - states // size
        for size, is_periodic in zip(shape, periodic, strict=True)
    ) * 2
    additions = 2 * dimensions * states
    actual = states + present_edges + additions
    conservative = states * (4 * dimensions + 1)
    return ActionOperationLedger(
        schema=ACTION_LEDGER_SCHEMA,
        states=states,
        dimensions=dimensions,
        self_multiplication_count=states,
        present_incoming_edge_count=present_edges,
        present_incoming_multiplication_count=present_edges,
        accumulator_addition_count=additions,
        actual_arithmetic_operation_count=actual,
        conservative_arithmetic_operation_budget=conservative,
        maximum_dependency_operation_count=2 * dimensions + 1,
        underflow_event_operation_budget=conservative,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order=ACCUMULATION_ORDER,
        relative_error_model="gamma_(2*d+1)_per_nonnegative_contribution_path_v1",
        underflow_error_model="N*(4*d+1)*2^-1074_v1",
        changes_upstream_enclosure=False,
    )


def _reduction_ledgers(
    states: int,
    block_size: int,
) -> tuple[ReductionOperationLedger, ReductionOperationLedger]:
    blocks = (states + block_size - 1) // block_size
    mass = ReductionOperationLedger(
        schema=REDUCTION_LEDGER_SCHEMA,
        reduction="positive_mass",
        states=states,
        block_size=block_size,
        block_count=blocks,
        multiplication_count=0,
        addition_count=states,
        actual_arithmetic_operation_count=states,
        upstream_enclosure_operation_count=states + blocks,
        maximum_dependency_operation_count=states,
        underflow_event_operation_budget=states + blocks,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order="strict_flat_index_left_to_right_v1",
        changes_upstream_enclosure=False,
    )
    dot = ReductionOperationLedger(
        schema=REDUCTION_LEDGER_SCHEMA,
        reduction="positive_killing_dot",
        states=states,
        block_size=block_size,
        block_count=blocks,
        multiplication_count=states,
        addition_count=states,
        actual_arithmetic_operation_count=2 * states,
        upstream_enclosure_operation_count=2 * states + blocks,
        maximum_dependency_operation_count=states + 1,
        underflow_event_operation_budget=2 * states + blocks,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order="strict_flat_index_multiply_then_left_to_right_add_v1",
        changes_upstream_enclosure=False,
    )
    return mass, dot


def generic_input_from_packed_kernel(
    kernel: packed.PackedTensorKernel,
) -> GenericPackedTensorInput:
    """Extract generic centre arrays without upgrading their provenance."""

    packed.validate_packed_tensor_kernel(kernel)
    return GenericPackedTensorInput(
        tensor_shape=kernel.contract.tensor_shape,
        periodic=tuple(axis.periodic for axis in kernel.axes),
        p_self_center=kernel.p_self_center,
        p_forward_center=kernel.p_forward_center,
        p_backward_center=kernel.p_backward_center,
        killing_center=kernel.killing_center,
        reduction_block_size=kernel.contract.block_size,
    )


class CompiledPowerStreamBackend:
    """Validated compiled backend with private read-only numerical inputs."""

    __slots__ = (
        "_artifact",
        "_shape",
        "_periodic",
        "_p_self",
        "_p_forward",
        "_p_backward",
        "_killing",
        "_shape_pointer",
        "_periodic_pointer",
        "_forward_pointer_array",
        "_backward_pointer_array",
        "_receipt",
    )

    def __init__(
        self,
        *,
        artifact: _CompiledArtifact,
        shape: np.ndarray,
        periodic: np.ndarray,
        p_self: np.ndarray,
        p_forward: tuple[np.ndarray, ...],
        p_backward: tuple[np.ndarray, ...],
        killing: np.ndarray,
        receipt: CompiledBackendReceipt,
    ) -> None:
        self._artifact = artifact
        self._shape = shape
        self._periodic = periodic
        self._p_self = p_self
        self._p_forward = p_forward
        self._p_backward = p_backward
        self._killing = killing
        self._shape_pointer = shape.ctypes.data_as(_SIZE_POINTER)
        self._periodic_pointer = periodic.ctypes.data_as(_UINT8_POINTER)
        pointer_array_type = _DOUBLE_POINTER * len(p_forward)
        self._forward_pointer_array = pointer_array_type(
            *(array.ctypes.data_as(_DOUBLE_POINTER) for array in p_forward)
        )
        self._backward_pointer_array = pointer_array_type(
            *(array.ctypes.data_as(_DOUBLE_POINTER) for array in p_backward)
        )
        self._receipt = receipt
        self.validate()

    @property
    def receipt(self) -> CompiledBackendReceipt:
        return self._receipt

    @property
    def states(self) -> int:
        return self._receipt.states

    def _check_status(self, status: int, *, operation: str) -> None:
        if status != 0:
            raise CompiledPowerStreamFailure(
                f"compiled {operation} failed with stable code {status}"
            )

    def _source_copy(self, source: object) -> np.ndarray:
        return _readonly_owned_float64_copy(
            source,
            expected_size=self.states,
            label="power-stream source",
        )

    def validate(self) -> None:
        receipt = self._receipt
        if (
            type(receipt) is not CompiledBackendReceipt
            or receipt.schema != BACKEND_RECEIPT_SCHEMA
            or receipt.status != METHOD_STATUS
            or receipt.input_provenance_classification
            != INPUT_PROVENANCE_CLASSIFICATION
            or receipt.control_exclusion_proved
            or receipt.science_free_proved
            or receipt.authorizes_scientific_execution
            or receipt.science_executed
            or receipt.resource_pass
            or receipt.f0_pass
            or not receipt.owned_native_readonly_inputs
            or not _is_sha256(receipt.receipt_sha256)
            or _file_sha256(_MODULE_PATH) != receipt.build.python_wrapper_sha256
            or _file_sha256(_C_SOURCE_PATH) != receipt.build.c_source_sha256
            or _file_sha256(self._artifact.binary_path)
            != receipt.build.compiled_binary_sha256
        ):
            raise CompiledPowerStreamFailure("backend receipt is invalid")
        arrays = (
            self._shape,
            self._periodic,
            self._p_self,
            self._killing,
            *self._p_forward,
            *self._p_backward,
        )
        if any(
            type(array) is not np.ndarray
            or not array.flags.owndata
            or array.base is not None
            or array.flags.writeable
            or not array.flags.c_contiguous
            or not array.flags.aligned
            for array in arrays
        ):
            raise CompiledPowerStreamFailure(
                "backend no longer owns immutable native inputs"
            )
        expected_payload = _dataclass_payload(
            dataclasses.replace(receipt, receipt_sha256="0" * 64)
        )
        if not hmac.compare_digest(
            receipt.receipt_sha256,
            _canonical_json_sha256(expected_payload),
        ):
            raise CompiledPowerStreamFailure("backend receipt binding is invalid")
        if (
            _raw_sha256(self._p_self) != receipt.p_self_sha256
            or _raw_sha256(self._killing) != receipt.killing_sha256
            or tuple(_raw_sha256(array) for array in self._p_forward)
            != receipt.p_forward_sha256
            or tuple(_raw_sha256(array) for array in self._p_backward)
            != receipt.p_backward_sha256
        ):
            raise CompiledPowerStreamFailure("backend input binding drifted")
        input_payload = {
            "killing_sha256": receipt.killing_sha256,
            "p_backward_sha256": list(receipt.p_backward_sha256),
            "p_forward_sha256": list(receipt.p_forward_sha256),
            "p_self_sha256": receipt.p_self_sha256,
            "periodic": list(receipt.periodic),
            "reduction_block_size": receipt.reduction_block_size,
            "tensor_shape": list(receipt.tensor_shape),
        }
        if not hmac.compare_digest(
            receipt.input_binding_sha256,
            _canonical_json_sha256(input_payload),
        ):
            raise CompiledPowerStreamFailure("backend input manifest is invalid")
        _runtime_probe(self._artifact.library)

    def apply_p_transpose(self, source: np.ndarray) -> np.ndarray:
        self.validate()
        owned_source = self._source_copy(source)
        destination = np.empty(self.states, dtype=np.float64)
        status = self._artifact.library.rdf0_apply_p_transpose(
            self.states,
            len(self._receipt.tensor_shape),
            self._shape_pointer,
            self._periodic_pointer,
            self._p_self.ctypes.data_as(_DOUBLE_POINTER),
            self._forward_pointer_array,
            self._backward_pointer_array,
            owned_source.ctypes.data_as(_DOUBLE_POINTER),
            destination.ctypes.data_as(_DOUBLE_POINTER),
        )
        self._check_status(status, operation="P transpose action")
        return _readonly_output(destination)

    def positive_mass(self, source: np.ndarray) -> PositiveReductionResult:
        self.validate()
        owned_source = self._source_copy(source)
        nominal = ctypes.c_double()
        status = self._artifact.library.rdf0_positive_mass(
            self.states,
            owned_source.ctypes.data_as(_DOUBLE_POINTER),
            ctypes.byref(nominal),
        )
        self._check_status(status, operation="positive mass reduction")
        return _positive_enclosure(
            float(nominal.value),
            self._receipt.mass_reduction_operations,
        )

    def killing_dot(self, source: np.ndarray) -> PositiveReductionResult:
        self.validate()
        owned_source = self._source_copy(source)
        nominal = ctypes.c_double()
        status = self._artifact.library.rdf0_positive_dot(
            self.states,
            self._killing.ctypes.data_as(_DOUBLE_POINTER),
            owned_source.ctypes.data_as(_DOUBLE_POINTER),
            ctypes.byref(nominal),
        )
        self._check_status(status, operation="positive killing dot")
        return _positive_enclosure(
            float(nominal.value),
            self._receipt.killing_dot_operations,
        )

    def run_power_stream(
        self,
        initial: np.ndarray,
        *,
        maximum_power: int,
    ) -> CompiledPowerStreamResult:
        self.validate()
        if (
            type(maximum_power) is not int
            or not 0 <= maximum_power <= MAXIMUM_POWER_INDEX
        ):
            raise CompiledPowerStreamFailure("maximum power is invalid")
        owned_initial = self._source_copy(initial)
        mass = np.empty(maximum_power + 1, dtype=np.float64)
        killing_dot = np.empty(maximum_power + 1, dtype=np.float64)
        final = np.empty(self.states, dtype=np.float64)
        status = self._artifact.library.rdf0_power_stream(
            self.states,
            len(self._receipt.tensor_shape),
            self._shape_pointer,
            self._periodic_pointer,
            self._p_self.ctypes.data_as(_DOUBLE_POINTER),
            self._forward_pointer_array,
            self._backward_pointer_array,
            self._killing.ctypes.data_as(_DOUBLE_POINTER),
            owned_initial.ctypes.data_as(_DOUBLE_POINTER),
            maximum_power,
            mass.ctypes.data_as(_DOUBLE_POINTER),
            killing_dot.ctypes.data_as(_DOUBLE_POINTER),
            final.ctypes.data_as(_DOUBLE_POINTER),
        )
        self._check_status(status, operation="power stream")
        _readonly_output(mass)
        _readonly_output(killing_dot)
        _readonly_output(final)
        provisional_receipt = CompiledPowerStreamReceipt(
            schema=STREAM_RECEIPT_SCHEMA,
            status=METHOD_STATUS,
            backend_receipt_sha256=self._receipt.receipt_sha256,
            initial_raw_sha256=_raw_sha256(owned_initial),
            maximum_power_index=maximum_power,
            p_action_call_count=maximum_power,
            mass_reduction_call_count=maximum_power + 1,
            killing_dot_call_count=maximum_power + 1,
            mass_stream_raw_sha256=_raw_sha256(mass),
            killing_dot_stream_raw_sha256=_raw_sha256(killing_dot),
            final_power_raw_sha256=_raw_sha256(final),
            stream_binding_sha256="0" * 64,
            full_power_arrays_retained=1,
            scalar_streams_retained=True,
            final_power_retained=True,
            private_owned_readonly_outputs=True,
            input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
            control_exclusion_proved=False,
            science_free_proved=False,
            authorizes_scientific_execution=False,
            science_executed=False,
            resource_pass=False,
            f0_pass=False,
        )
        receipt = dataclasses.replace(
            provisional_receipt,
            stream_binding_sha256=_canonical_json_sha256(
                _dataclass_payload(provisional_receipt)
            ),
        )
        result = CompiledPowerStreamResult(
            mass_by_power=mass,
            killing_dot_by_power=killing_dot,
            final_power=final,
            receipt=receipt,
        )
        validate_compiled_power_stream_result(self, result)
        return result


def build_compiled_power_stream_backend(
    source: GenericPackedTensorInput | packed.PackedTensorKernel,
) -> CompiledPowerStreamBackend:
    """Build a compiled method backend from generic, unclassified arrays."""

    if type(source) is packed.PackedTensorKernel:
        generic = generic_input_from_packed_kernel(source)
    elif type(source) is GenericPackedTensorInput:
        generic = source
    else:
        raise CompiledPowerStreamFailure(
            "compiled backend input has the wrong exact type"
        )
    shape = generic.tensor_shape
    periodic_tuple = generic.periodic
    if (
        type(shape) is not tuple
        or not shape
        or len(shape) > MAXIMUM_DIMENSIONS
        or any(type(size) is not int or size < 2 for size in shape)
        or type(periodic_tuple) is not tuple
        or len(periodic_tuple) != len(shape)
        or any(type(value) is not bool for value in periodic_tuple)
        or type(generic.p_forward_center) is not tuple
        or type(generic.p_backward_center) is not tuple
        or len(generic.p_forward_center) != len(shape)
        or len(generic.p_backward_center) != len(shape)
        or type(generic.reduction_block_size) is not int
        or generic.reduction_block_size < 1
    ):
        raise CompiledPowerStreamFailure("generic packed tensor header is invalid")
    states = math.prod(shape)
    if states > np.iinfo(np.uintp).max:
        raise CompiledPowerStreamFailure("tensor state count exceeds size_t")
    p_self = _readonly_owned_float64_copy(
        generic.p_self_center,
        expected_size=states,
        label="P self centre",
    )
    killing = _readonly_owned_float64_copy(
        generic.killing_center,
        expected_size=states,
        label="killing centre",
    )
    p_forward = tuple(
        _readonly_owned_float64_copy(
            value,
            expected_size=size,
            label=f"axis {dimension} P forward centre",
        )
        for dimension, (size, value) in enumerate(
            zip(shape, generic.p_forward_center, strict=True)
        )
    )
    p_backward = tuple(
        _readonly_owned_float64_copy(
            value,
            expected_size=size,
            label=f"axis {dimension} P backward centre",
        )
        for dimension, (size, value) in enumerate(
            zip(shape, generic.p_backward_center, strict=True)
        )
    )
    shape_array = np.array(shape, dtype=np.uintp, copy=True)
    periodic_array = np.array(periodic_tuple, dtype=np.uint8, copy=True)
    shape_array.setflags(write=False)
    periodic_array.setflags(write=False)
    if (
        not shape_array.flags.owndata
        or shape_array.base is not None
        or not periodic_array.flags.owndata
        or periodic_array.base is not None
    ):
        raise CompiledPowerStreamFailure("native topology arrays are not owned")
    action = _action_ledger(shape, periodic_tuple)
    mass_ledger, dot_ledger = _reduction_ledgers(
        states,
        generic.reduction_block_size,
    )
    artifact = _compile_artifact()
    p_self_hash = _raw_sha256(p_self)
    p_forward_hashes = tuple(_raw_sha256(value) for value in p_forward)
    p_backward_hashes = tuple(_raw_sha256(value) for value in p_backward)
    killing_hash = _raw_sha256(killing)
    input_payload = {
        "killing_sha256": killing_hash,
        "p_backward_sha256": list(p_backward_hashes),
        "p_forward_sha256": list(p_forward_hashes),
        "p_self_sha256": p_self_hash,
        "periodic": list(periodic_tuple),
        "reduction_block_size": generic.reduction_block_size,
        "tensor_shape": list(shape),
    }
    provisional = CompiledBackendReceipt(
        schema=BACKEND_RECEIPT_SCHEMA,
        status=METHOD_STATUS,
        tensor_shape=shape,
        periodic=periodic_tuple,
        states=states,
        dimensions=len(shape),
        reduction_block_size=generic.reduction_block_size,
        input_binding_sha256=_canonical_json_sha256(input_payload),
        p_self_sha256=p_self_hash,
        p_forward_sha256=p_forward_hashes,
        p_backward_sha256=p_backward_hashes,
        killing_sha256=killing_hash,
        owned_native_readonly_inputs=True,
        input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
        control_exclusion_proved=False,
        science_free_proved=False,
        build=artifact.receipt,
        action_operations=action,
        mass_reduction_operations=mass_ledger,
        killing_dot_operations=dot_ledger,
        authorizes_scientific_execution=False,
        science_executed=False,
        resource_pass=False,
        f0_pass=False,
        receipt_sha256="0" * 64,
    )
    receipt_hash = _canonical_json_sha256(_dataclass_payload(provisional))
    receipt = dataclasses.replace(provisional, receipt_sha256=receipt_hash)
    return CompiledPowerStreamBackend(
        artifact=artifact,
        shape=shape_array,
        periodic=periodic_array,
        p_self=p_self,
        p_forward=p_forward,
        p_backward=p_backward,
        killing=killing,
        receipt=receipt,
    )


def validate_compiled_power_stream_result(
    backend: CompiledPowerStreamBackend,
    result: CompiledPowerStreamResult,
) -> None:
    """Rebind one private-output result without promoting its authority."""

    if (
        type(backend) is not CompiledPowerStreamBackend
        or type(result) is not CompiledPowerStreamResult
        or type(result.receipt) is not CompiledPowerStreamReceipt
    ):
        raise CompiledPowerStreamFailure("compiled stream result has wrong types")
    backend.validate()
    receipt = result.receipt
    maximum_power = receipt.maximum_power_index
    arrays = (
        result.mass_by_power,
        result.killing_dot_by_power,
        result.final_power,
    )
    if (
        receipt.schema != STREAM_RECEIPT_SCHEMA
        or receipt.status != METHOD_STATUS
        or receipt.backend_receipt_sha256 != backend.receipt.receipt_sha256
        or type(maximum_power) is not int
        or not 0 <= maximum_power <= MAXIMUM_POWER_INDEX
        or receipt.p_action_call_count != maximum_power
        or receipt.mass_reduction_call_count != maximum_power + 1
        or receipt.killing_dot_call_count != maximum_power + 1
        or receipt.full_power_arrays_retained != 1
        or not receipt.scalar_streams_retained
        or not receipt.final_power_retained
        or not receipt.private_owned_readonly_outputs
        or receipt.input_provenance_classification
        != INPUT_PROVENANCE_CLASSIFICATION
        or receipt.control_exclusion_proved
        or receipt.science_free_proved
        or receipt.authorizes_scientific_execution
        or receipt.science_executed
        or receipt.resource_pass
        or receipt.f0_pass
        or result.mass_by_power.shape != (maximum_power + 1,)
        or result.killing_dot_by_power.shape != (maximum_power + 1,)
        or result.final_power.shape != (backend.states,)
        or not _is_sha256(receipt.stream_binding_sha256)
    ):
        raise CompiledPowerStreamFailure("compiled stream receipt is invalid")
    if any(
        type(array) is not np.ndarray
        or array.dtype != np.dtype(np.float64)
        or not array.dtype.isnative
        or not array.flags.c_contiguous
        or not array.flags.aligned
        or not array.flags.owndata
        or array.base is not None
        or array.flags.writeable
        or not bool(np.all(np.isfinite(array)))
        or bool(np.any(array < 0.0))
        for array in arrays
    ):
        raise CompiledPowerStreamFailure("compiled stream arrays are noncanonical")
    if (
        _raw_sha256(result.mass_by_power) != receipt.mass_stream_raw_sha256
        or _raw_sha256(result.killing_dot_by_power)
        != receipt.killing_dot_stream_raw_sha256
        or _raw_sha256(result.final_power) != receipt.final_power_raw_sha256
    ):
        raise CompiledPowerStreamFailure("compiled stream output binding drifted")
    expected_binding = _canonical_json_sha256(
        _dataclass_payload(
            dataclasses.replace(receipt, stream_binding_sha256="0" * 64)
        )
    )
    if not hmac.compare_digest(
        receipt.stream_binding_sha256,
        expected_binding,
    ):
        raise CompiledPowerStreamFailure("compiled stream binding is invalid")
