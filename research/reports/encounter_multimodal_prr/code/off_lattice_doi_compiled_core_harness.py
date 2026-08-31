#!/usr/bin/env /usr/bin/python3
"""Build, independently reference, parse, and benchmark the compiled Doi core.

Only method fixtures for constant and broad-four-slab hazards are exposed.
This harness never imports the scalar POC, reads Stage-B output, or supplies
scientific windows, valleys, power, or a production trajectory count.
"""

from __future__ import annotations

import argparse
import bisect
import dataclasses
import hashlib
import json
import math
import os
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "off_lattice_doi_compiled_core.cpp"
COMPILER = Path("/usr/bin/clang++")
BUILD_FLAGS = (
    "-std=c++20",
    "-O3",
    "-DNDEBUG",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-pedantic",
    "-fno-fast-math",
    "-ffp-contract=off",
    "-fno-associative-math",
)
RAW_MAGIC = b"ODTCOR2\x00"
RAW_ENDIAN_MARKER = 0x01020304
RAW_SCHEMA = 2
RAW_FIXED_HEADER_BYTES = 88
RAW_RECORD_BYTES = 24
POSITIVE_INFINITY_BITS = 0x7FF0000000000000
UINT32_MAX = (1 << 32) - 1
UINT64_MAX = (1 << 64) - 1
KNOWN_PHILOX_ZERO_VECTOR = (0x6627E8D5, 0xE169C58D, 0xBC57AC4C, 0x9B00DBD8)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: Dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def minimal_environment() -> Dict[str, str]:
    return {
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
    }


def compiler_identity() -> Dict[str, Any]:
    completed = subprocess.run(
        [str(COMPILER), "--version"],
        env=minimal_environment(),
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        "path": str(COMPILER),
        "sha256": sha256_file(COMPILER),
        "version": completed.stdout.strip().splitlines(),
    }


def build_core(output: Path, *, optimization: str = "-O3") -> Dict[str, Any]:
    output = output.resolve()
    if optimization not in {"-O0", "-O3"}:
        raise ValueError("only the audited -O0 and -O3 optimization fixtures are allowed")
    flags = tuple(optimization if flag == "-O3" else flag for flag in BUILD_FLAGS)
    command = [str(COMPILER), *flags, str(SOURCE), "-o", str(output)]
    completed = subprocess.run(
        command,
        cwd=HERE,
        env=minimal_environment(),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("compiled-core build failed:\n" + completed.stdout + completed.stderr)
    return {
        "command": command,
        "compiler": compiler_identity(),
        "source_sha256": sha256_file(SOURCE),
        "binary_sha256": sha256_file(output),
        "optimization": optimization,
    }


MASK32 = (1 << 32) - 1
PHILOX_M0 = 0xD2511F53
PHILOX_M1 = 0xCD9E8D57
PHILOX_W0 = 0x9E3779B9
PHILOX_W1 = 0xBB67AE85
PARTICLE_DIFFUSION = 0.002
OU_STIFFNESS = 0.1
OU_MEAN = 0.95
TRANSVERSE_WIDTH = 1.0
MIDPOINT_START = 0.14
RELATIVE_PARALLEL_START = -0.35
RELATIVE_PERP_START = 0.0
INITIAL_HALF_WIDTH = 0.02
BROAD_BUDGET = 0.01
BROAD_LAMBDA = 0.35
CONTACT_RADIUS = 0.16
PATCH_HALF_WIDTH = 0.04
BASE_BUMP_INTEGRAL = 0.4439938161680794
PATCH_CENTRES = (0.35, 0.60, 0.75, 0.90)
HAZARD_MODE_TAGS = {"constant": 0, "broad-four-slab": 1}


def philox4x32_10_reference(
    counter: Sequence[int], key: Sequence[int]
) -> Tuple[int, int, int, int]:
    """Independent pure-Python integer reference for Random123 Philox4x32-10."""

    if len(counter) != 4 or len(key) != 2:
        raise ValueError("Philox requires four counter and two key words")
    words = tuple(int(value) & MASK32 for value in counter)
    key_words = [int(value) & MASK32 for value in key]
    for round_index in range(10):
        product0 = PHILOX_M0 * words[0]
        product1 = PHILOX_M1 * words[2]
        words = (
            ((product1 >> 32) ^ words[1] ^ key_words[0]) & MASK32,
            product1 & MASK32,
            ((product0 >> 32) ^ words[3] ^ key_words[1]) & MASK32,
            product0 & MASK32,
        )
        if round_index != 9:
            key_words[0] = (key_words[0] + PHILOX_W0) & MASK32
            key_words[1] = (key_words[1] + PHILOX_W1) & MASK32
    return words


class ReferenceStream:
    def __init__(self, master_seed: int, replicate_id: int, trajectory_id: int) -> None:
        for label, value, maximum in (
            ("master_seed", master_seed, MASK32),
            ("replicate_id", replicate_id, MASK32),
            ("trajectory_id", trajectory_id, (1 << 64) - 1),
        ):
            if int(value) != value or not 0 <= value <= maximum:
                raise ValueError("{} is outside its frozen integer domain".format(label))
        self.master_seed = int(master_seed)
        self.replicate_id = int(replicate_id)
        self.key = (trajectory_id & MASK32, (trajectory_id >> 32) & MASK32)
        self.block = 0
        self.words: List[int] = []
        self.normal_cache: List[float] = []

    def next_u32(self) -> int:
        if not self.words:
            if self.block > (1 << 64) - 1:
                raise RuntimeError("reference Philox block counter exhausted")
            self.words.extend(
                philox4x32_10_reference(
                    (
                        self.block & MASK32,
                        (self.block >> 32) & MASK32,
                        self.master_seed,
                        self.replicate_id,
                    ),
                    self.key,
                )
            )
            self.block += 1
        return self.words.pop(0)

    def next_u64(self) -> int:
        return (self.next_u32() << 32) | self.next_u32()

    def uniform_open(self) -> float:
        mantissa = self.next_u64() >> 12
        value = math.ldexp(float(mantissa) + 0.5, -52)
        if not 0.0 < value < 1.0:
            raise RuntimeError("reference open uniform escaped its interval")
        return value

    def exponential(self, rate: float) -> float:
        return -math.log(self.uniform_open()) / rate

    def normal(self) -> float:
        if self.normal_cache:
            return self.normal_cache.pop()
        first = self.uniform_open()
        second = self.uniform_open()
        radius = math.sqrt(-2.0 * math.log(first))
        angle = 2.0 * float.fromhex("0x1.921fb54442d18p+1") * second
        self.normal_cache.append(radius * math.sin(angle))
        return radius * math.cos(angle)


def double_bits_hex(value: float) -> str:
    return "{:016x}".format(struct.unpack("<Q", struct.pack("<d", value))[0])


def bits_hex_to_double(value: str) -> float:
    return struct.unpack("<d", struct.pack("<Q", int(value, 16)))[0]


def sample_unit_bump_reference(stream: ReferenceStream) -> Tuple[float, int]:
    for attempt in range(1, 513):
        value = 2.0 * stream.uniform_open() - 1.0
        acceptance = math.exp(-(value * value) / (1.0 - value * value))
        if stream.uniform_open() < acceptance:
            return value, attempt
    raise RuntimeError("reference compact-bump cap reached")


def wrap_periodic_reference(value: float, period: float) -> float:
    wrapped = value - period * math.floor((value + 0.5 * period) / period)
    if wrapped >= 0.5 * period:
        wrapped -= period
    if wrapped < -0.5 * period:
        wrapped += period
    return wrapped


def unit_bump_value_reference(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("compact-bump argument must be finite")
    if abs(value) >= 1.0:
        return 0.0
    result = math.exp(-1.0 / (1.0 - value * value))
    if not math.isfinite(result) or result < 0.0:
        raise RuntimeError("compact-bump evaluation returned an invalid value")
    return result


def validate_broad_weights_reference(weights: Sequence[float]) -> Tuple[float, ...]:
    frozen = tuple(float(weight) for weight in weights)
    if len(frozen) != 4:
        raise ValueError("broad-four-slab mode requires exactly four weights")
    if any(not math.isfinite(weight) or weight < 0.0 for weight in frozen):
        raise ValueError("broad-four-slab weights must be finite and nonnegative")
    total = 0.0
    for weight in frozen:
        total += weight
    if abs(total - 1.0) > 2.0e-14:
        raise ValueError("broad-four-slab weights must sum to one")
    return frozen


def broad_analytic_bound_reference(weights: Sequence[float]) -> float:
    frozen = validate_broad_weights_reference(weights)
    if BASE_BUMP_INTEGRAL < math.exp(-4.0 / 3.0):
        raise ValueError("pinned bump normalization violates the elementary lower bound")
    if any(
        right - left <= 2.0 * PATCH_HALF_WIDTH
        for left, right in zip(PATCH_CENTRES[:-1], PATCH_CENTRES[1:])
    ):
        raise ValueError("broad-four-slab supports are not disjoint")
    return (
        BROAD_BUDGET
        * max(frozen)
        * math.exp(1.0 / 3.0)
        / (PATCH_HALF_WIDTH * TRANSVERSE_WIDTH)
    )


def broad_four_slab_rate_reference(
    state: Tuple[float, float, float], weights: Sequence[float]
) -> float:
    frozen = validate_broad_weights_reference(weights)
    if any(not math.isfinite(value) for value in state):
        raise ValueError("hazard state must be finite")
    relative_perp = wrap_periodic_reference(state[2], TRANSVERSE_WIDTH)
    if (
        abs(state[1]) >= CONTACT_RADIUS
        or abs(relative_perp) >= CONTACT_RADIUS
        or state[1] * state[1] + relative_perp * relative_perp
        >= CONTACT_RADIUS * CONTACT_RADIUS
    ):
        return 0.0
    midpoint_profile = 0.0
    for weight, centre in zip(frozen, PATCH_CENTRES):
        left = centre - PATCH_HALF_WIDTH
        right = centre + PATCH_HALF_WIDTH
        if not left < state[0] < right:
            continue
        standardized = (state[0] - centre) / PATCH_HALF_WIDTH
        midpoint_profile += (
            weight
            * unit_bump_value_reference(standardized)
            / (PATCH_HALF_WIDTH * BASE_BUMP_INTEGRAL)
        )
    rate = BROAD_BUDGET * midpoint_profile / TRANSVERSE_WIDTH
    if not math.isfinite(rate) or rate < 0.0:
        raise RuntimeError("broad-four-slab hazard returned an invalid rate")
    return rate


def checked_killing_rate_reference(rate: float, lambda_rate: float) -> float:
    if not math.isfinite(rate) or rate < 0.0:
        raise RuntimeError("hazard evaluation returned an invalid rate")
    if rate > lambda_rate:
        raise RuntimeError("declared Lambda does not dominate an evaluated hazard")
    return rate


def fixed_transition_reference() -> Tuple[float, float, float]:
    midpoint, relative_parallel, relative_perp = 0.2, -0.3, 0.49
    delta = 1.7
    normals = (0.25, -0.5, 1.25)
    decay = math.exp(-OU_STIFFNESS * delta)
    factor = -math.expm1(-2.0 * OU_STIFFNESS * delta)
    midpoint_variance = PARTICLE_DIFFUSION * factor / (2.0 * OU_STIFFNESS)
    relative_variance = 2.0 * PARTICLE_DIFFUSION * factor / OU_STIFFNESS
    return (
        OU_MEAN
        + decay * (midpoint - OU_MEAN)
        + math.sqrt(midpoint_variance) * normals[0],
        decay * relative_parallel + math.sqrt(relative_variance) * normals[1],
        wrap_periodic_reference(
            relative_perp
            + math.sqrt(4.0 * PARTICLE_DIFFUSION * delta) * normals[2],
            TRANSVERSE_WIDTH,
        ),
    )


def free_transition_reference(
    state: Tuple[float, float, float], delta: float, stream: ReferenceStream
) -> Tuple[float, float, float]:
    decay = math.exp(-OU_STIFFNESS * delta)
    factor = -math.expm1(-2.0 * OU_STIFFNESS * delta)
    midpoint_variance = PARTICLE_DIFFUSION * factor / (2.0 * OU_STIFFNESS)
    relative_variance = 2.0 * PARTICLE_DIFFUSION * factor / OU_STIFFNESS
    normals = (stream.normal(), stream.normal(), stream.normal())
    return (
        OU_MEAN
        + decay * (state[0] - OU_MEAN)
        + math.sqrt(midpoint_variance) * normals[0],
        decay * state[1] + math.sqrt(relative_variance) * normals[1],
        wrap_periodic_reference(
            state[2] + math.sqrt(4.0 * PARTICLE_DIFFUSION * delta) * normals[2],
            TRANSVERSE_WIDTH,
        ),
    )


def simulate_trajectory_reference(
    spec: "ChunkSpec", trajectory_id: int
) -> Tuple[float, int, int]:
    """Independent Python replay of one synthetic compiled trajectory."""

    stream = ReferenceStream(spec.master_seed, spec.replicate_id, trajectory_id)
    state = (
        MIDPOINT_START + INITIAL_HALF_WIDTH * sample_unit_bump_reference(stream)[0],
        RELATIVE_PARALLEL_START
        + INITIAL_HALF_WIDTH * sample_unit_bump_reference(stream)[0],
        wrap_periodic_reference(
            RELATIVE_PERP_START
            + INITIAL_HALF_WIDTH * sample_unit_bump_reference(stream)[0],
            TRANSVERSE_WIDTH,
        ),
    )
    time_value = 0.0
    candidates = 0
    while True:
        delta = stream.exponential(spec.lambda_rate)
        if delta > spec.horizon - time_value:
            return math.inf, candidates, 0
        candidate_time = time_value + delta
        state = free_transition_reference(state, delta, stream)
        time_value = candidate_time
        candidates += 1
        if spec.hazard_mode == "constant":
            killing_rate = spec.constant_hazard
        elif spec.hazard_mode == "broad-four-slab":
            killing_rate = broad_four_slab_rate_reference(state, spec.weights)
        else:
            raise ValueError("unknown reference hazard mode")
        killing_rate = checked_killing_rate_reference(killing_rate, spec.lambda_rate)
        if stream.uniform_open() < killing_rate / spec.lambda_rate:
            return time_value, candidates, 1


def simulate_constant_hazard_reference(
    spec: "ChunkSpec", trajectory_id: int
) -> Tuple[float, int, int]:
    if spec.hazard_mode != "constant":
        raise ValueError("constant-hazard replay requires constant mode")
    return simulate_trajectory_reference(spec, trajectory_id)


def fixture_reference() -> Dict[str, Any]:
    master = 0x12345678
    replicate = 0x9ABCDEF0
    trajectory = 0x0123456789ABCDEF
    blocks = [
        philox4x32_10_reference(
            (block, 0, master, replicate),
            (trajectory & MASK32, (trajectory >> 32) & MASK32),
        )
        for block in range(4)
    ]
    raw_stream = ReferenceStream(master, replicate, trajectory)
    raw_words = [raw_stream.next_u32() for _ in range(12)]
    uniform_stream = ReferenceStream(master, replicate, trajectory)
    uniforms = [uniform_stream.uniform_open() for _ in range(4)]
    exponential_stream = ReferenceStream(master, replicate, trajectory)
    exponentials = [exponential_stream.exponential(0.13) for _ in range(4)]
    normal_stream = ReferenceStream(master, replicate, trajectory)
    normals = [normal_stream.normal() for _ in range(6)]
    bump_stream = ReferenceStream(master, replicate, trajectory)
    bumps = [sample_unit_bump_reference(bump_stream) for _ in range(3)]
    hazard_weights = (0.4, 0.3, 0.2, 0.1)
    unit_weight = (1.0, 0.0, 0.0, 0.0)
    simplex_bound = broad_analytic_bound_reference(unit_weight)
    fixture_bound = broad_analytic_bound_reference(hazard_weights)
    all_center_rates = [
        broad_four_slab_rate_reference((centre, 0.0, 0.0), hazard_weights)
        for centre in PATCH_CENTRES
    ]
    center_rate = all_center_rates[0]
    contact_inside_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0], math.nextafter(CONTACT_RADIUS, 0.0), 0.0),
        hazard_weights,
    )
    contact_edge_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0], CONTACT_RADIUS, 0.0), hazard_weights
    )
    contact_outside_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0], math.nextafter(CONTACT_RADIUS, 1.0), 0.0),
        hazard_weights,
    )
    minimum_image_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0], 0.0, 0.99), hazard_weights
    )
    minimum_image_reference_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0], 0.0, -0.01), hazard_weights
    )
    bump_edge_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0] + PATCH_HALF_WIDTH, 0.0, 0.0), hazard_weights
    )
    bump_near_edge_rate = broad_four_slab_rate_reference(
        (PATCH_CENTRES[0] + 0.75 * PATCH_HALF_WIDTH, 0.0, 0.0),
        hazard_weights,
    )
    zero_rate = broad_four_slab_rate_reference((0.0, 0.0, 0.0), hazard_weights)
    near_lambda_guard = checked_killing_rate_reference(
        math.nextafter(BROAD_LAMBDA, 0.0), BROAD_LAMBDA
    )
    return {
        "known_zero": KNOWN_PHILOX_ZERO_VECTOR,
        "blocks": blocks,
        "raw_words": raw_words,
        "uniform_bits": [double_bits_hex(value) for value in uniforms],
        "exponentials": exponentials,
        "normals": normals,
        "bumps": bumps,
        "transition": fixed_transition_reference(),
        "hazard_fixtures": {
            "all_center_rate_bits": [double_bits_hex(rate) for rate in all_center_rates],
            "analytic_fixture_bound_bits": double_bits_hex(fixture_bound),
            "analytic_simplex_bound_bits": double_bits_hex(simplex_bound),
            "broad_budget_bits": double_bits_hex(BROAD_BUDGET),
            "broad_lambda_bits": double_bits_hex(BROAD_LAMBDA),
            "bump_edge_rate_bits": double_bits_hex(bump_edge_rate),
            "bump_near_edge_rate_bits": double_bits_hex(bump_near_edge_rate),
            "center_rate_bits": double_bits_hex(center_rate),
            "contact_edge_rate_bits": double_bits_hex(contact_edge_rate),
            "contact_inside_rate_bits": double_bits_hex(contact_inside_rate),
            "contact_outside_rate_bits": double_bits_hex(contact_outside_rate),
            "minimum_image_equal": double_bits_hex(minimum_image_rate)
            == double_bits_hex(minimum_image_reference_rate),
            "minimum_image_rate_bits": double_bits_hex(minimum_image_rate),
            "near_lambda_guard_bits": double_bits_hex(near_lambda_guard),
            "normalization_bits": double_bits_hex(BASE_BUMP_INTEGRAL),
            "simplex_margin_bits": double_bits_hex(BROAD_LAMBDA - simplex_bound),
            "zero_rate_bits": double_bits_hex(zero_rate),
        },
    }


def run_fixtures(binary: Path) -> Dict[str, Any]:
    completed = subprocess.run(
        [str(binary.resolve()), "fixtures"],
        env=minimal_environment(),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("fixture command failed: " + completed.stderr)
    payload = json.loads(completed.stdout)
    if payload.get("core_boundary") != "METHOD_ONLY_OFF_LATTICE_COMPILED_CORE":
        raise RuntimeError("fixture command crossed the method-only core boundary")
    return payload


def run_hazard_bound_violation_fixture(binary: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(binary.resolve()), "hazard-bound-violation-fixture"],
        env=minimal_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


@dataclasses.dataclass(frozen=True)
class ChunkSpec:
    master_seed: int
    replicate_id: int
    chunk_id: int
    id_start: int
    id_count: int
    horizon: float
    lambda_rate: float
    hazard_mode: str
    constant_hazard: float
    weights: Tuple[float, ...]
    basin_cuts: Tuple[float, ...]
    windows: Tuple[Tuple[float, float], ...]


def synthetic_method_spec(
    *,
    id_start: int = 0,
    id_count: int = 4096,
    chunk_id: int = 0,
    constant_hazard: float = 0.05,
    lambda_rate: float = 0.13,
) -> ChunkSpec:
    """Return non-scientific analytic-fixture cuts/windows only."""

    return ChunkSpec(
        master_seed=0x13579BDF,
        replicate_id=7,
        chunk_id=chunk_id,
        id_start=id_start,
        id_count=id_count,
        horizon=100.0,
        lambda_rate=lambda_rate,
        hazard_mode="constant",
        constant_hazard=constant_hazard,
        weights=(),
        basin_cuts=(10.0, 30.0),
        windows=((2.0, 4.0), (12.0, 14.0), (40.0, 45.0)),
    )


def synthetic_broad_spec(
    *,
    id_start: int = 0,
    id_count: int = 128,
    chunk_id: int = 0,
    weights: Tuple[float, ...] = (0.4, 0.3, 0.2, 0.1),
) -> ChunkSpec:
    """Return a small non-scientific physical-hazard method fixture."""

    return ChunkSpec(
        master_seed=0x2468ACE0,
        replicate_id=11,
        chunk_id=chunk_id,
        id_start=id_start,
        id_count=id_count,
        horizon=12.0,
        lambda_rate=BROAD_LAMBDA,
        hazard_mode="broad-four-slab",
        constant_hazard=0.0,
        weights=weights,
        basin_cuts=(3.0, 8.0),
        windows=((1.0, 2.0), (5.0, 6.0), (10.0, 11.0)),
    )


def run_chunk(
    binary: Path, spec: ChunkSpec, raw_output: Path, *, expect_success: bool = True
) -> Tuple[subprocess.CompletedProcess, Dict[str, Any]]:
    raw_output = raw_output.resolve()
    command = [
        str(binary.resolve()),
        "run-chunk",
        "--master-seed",
        str(spec.master_seed),
        "--replicate-id",
        str(spec.replicate_id),
        "--chunk-id",
        str(spec.chunk_id),
        "--id-start",
        str(spec.id_start),
        "--id-count",
        str(spec.id_count),
        "--horizon",
        repr(spec.horizon),
        "--lambda",
        repr(spec.lambda_rate),
        "--hazard-mode",
        spec.hazard_mode,
        "--constant-hazard",
        repr(spec.constant_hazard),
        "--weights",
        ",".join(repr(value) for value in spec.weights),
        "--basin-cuts",
        ",".join(repr(value) for value in spec.basin_cuts),
        "--windows",
        ",".join("{}:{}".format(*window) for window in spec.windows),
        "--raw-output",
        str(raw_output),
    ]
    completed = subprocess.run(
        command,
        env=minimal_environment(),
        check=False,
        capture_output=True,
        text=True,
    )
    if expect_success and completed.returncode != 0:
        raise RuntimeError("chunk command failed: " + completed.stderr)
    payload = json.loads(completed.stdout) if completed.stdout else {}
    if expect_success and (
        payload.get("core_boundary") != "METHOD_ONLY_OFF_LATTICE_COMPILED_CORE"
        or payload.get("stage") != "METHOD_ONLY_OFF_LATTICE_RAW_CHUNK_COMPLETE"
        or payload.get("statistical_estimates_released") is not False
        or payload.get("claim_flags")
        != {
            "independent_solver_verified": False,
            "modality_confirmed": False,
            "production_run_authorized": False,
            "scientific_estimand_frozen": False,
            "scientific_event_ensemble": False,
        }
        or payload.get("hazard_mode") != spec.hazard_mode
        or payload.get("weight_bits")
        != [double_bits_hex(weight) for weight in spec.weights]
        or payload.get("schema_version") != 2
        or payload.get("raw_schema") != RAW_SCHEMA
        or payload.get("raw_record_bytes") != RAW_RECORD_BYTES
        or payload.get("constant_hazard_bits") != double_bits_hex(spec.constant_hazard)
        or payload.get("lambda_bits") != double_bits_hex(spec.lambda_rate)
        or payload.get("horizon_bits") != double_bits_hex(spec.horizon)
        or payload.get("master_seed") != spec.master_seed
        or payload.get("replicate_id") != spec.replicate_id
        or payload.get("chunk_id") != spec.chunk_id
        or payload.get("id_start") != spec.id_start
        or payload.get("id_count") != spec.id_count
    ):
        raise RuntimeError("chunk command violated the method-only operational boundary")
    forbidden_estimate_keys = {
        "reaction_count",
        "censored_count",
        "basin_counts",
        "window_counts",
        "candidate_count_sum",
    }
    if expect_success and forbidden_estimate_keys.intersection(payload):
        raise RuntimeError("chunk command released a partial statistical estimate")
    return completed, payload


def parse_raw_chunk(path: Path) -> Dict[str, Any]:
    payload = path.read_bytes()
    if len(payload) < RAW_FIXED_HEADER_BYTES or payload[:8] != RAW_MAGIC:
        raise ValueError("raw chunk magic/size is invalid")
    offset = 8

    def unpack(format_string: str) -> Tuple[Any, ...]:
        nonlocal offset
        size = struct.calcsize(format_string)
        if offset + size > len(payload):
            raise ValueError("raw chunk ended inside a field")
        values = struct.unpack_from(format_string, payload, offset)
        offset += size
        return values

    endian, schema, master_seed, replicate_id = unpack("<IIII")
    chunk_id, id_start, id_count = unpack("<QQQ")
    horizon_bits, lambda_bits, hazard_bits = unpack("<QQQ")
    hazard_mode_tag, weight_count, cut_count, window_count = unpack("<IIII")
    if endian != RAW_ENDIAN_MARKER or schema != RAW_SCHEMA:
        raise ValueError("raw chunk endian/schema changed")
    inverse_tags = {tag: mode for mode, tag in HAZARD_MODE_TAGS.items()}
    if hazard_mode_tag not in inverse_tags:
        raise ValueError("raw chunk hazard-mode tag changed")
    hazard_mode = inverse_tags[hazard_mode_tag]
    weights = [
        bits_hex_to_double("{:016x}".format(unpack("<Q")[0]))
        for _ in range(weight_count)
    ]
    cuts = [bits_hex_to_double("{:016x}".format(unpack("<Q")[0])) for _ in range(cut_count)]
    windows = [
        (
            bits_hex_to_double("{:016x}".format(unpack("<Q")[0])),
            bits_hex_to_double("{:016x}".format(unpack("<Q")[0])),
        )
        for _ in range(window_count)
    ]
    horizon = bits_hex_to_double("{:016x}".format(horizon_bits))
    lambda_rate = bits_hex_to_double("{:016x}".format(lambda_bits))
    constant_hazard = bits_hex_to_double("{:016x}".format(hazard_bits))
    if not math.isfinite(horizon) or horizon <= 0.0:
        raise ValueError("raw chunk has an invalid horizon")
    if not math.isfinite(lambda_rate) or lambda_rate <= 0.0:
        raise ValueError("raw chunk has an invalid Lambda")
    if hazard_mode == "constant":
        if (
            not math.isfinite(constant_hazard)
            or not 0.0 <= constant_hazard <= lambda_rate
            or weights
        ):
            raise ValueError("raw constant-hazard contract is invalid")
    else:
        if (
            lambda_bits != struct.unpack("<Q", struct.pack("<d", BROAD_LAMBDA))[0]
            or hazard_bits != 0
        ):
            raise ValueError("raw broad-four-slab frozen-rate contract is invalid")
        try:
            bound = broad_analytic_bound_reference(weights)
        except (RuntimeError, ValueError) as error:
            raise ValueError("raw broad-four-slab weights are invalid") from error
        if not bound < lambda_rate:
            raise ValueError("raw broad-four-slab analytic bound exceeds Lambda")
    previous_cut = 0.0
    for cut in cuts:
        if not math.isfinite(cut) or not previous_cut < cut < horizon:
            raise ValueError("raw chunk basin cuts are invalid")
        previous_cut = cut
    previous_right = -1.0
    for left, right in windows:
        if not (
            math.isfinite(left)
            and math.isfinite(right)
            and 0.0 <= left < right <= horizon
            and left >= previous_right
        ):
            raise ValueError("raw chunk windows are invalid")
        previous_right = right
    records = []
    for record_offset in range(id_count):
        trajectory_id, event_bits, candidate_count, flags = unpack("<QQII")
        if flags not in {0, 1}:
            raise ValueError("raw record reaction flag changed")
        event_time = struct.unpack("<d", struct.pack("<Q", event_bits))[0]
        if trajectory_id != id_start + record_offset:
            raise ValueError("raw trajectory IDs are not exact and ordered")
        if flags == 0:
            if event_bits != POSITIVE_INFINITY_BITS:
                raise ValueError("raw censor flag lacks the exact +infinity sentinel")
        elif not (math.isfinite(event_time) and 0.0 < event_time <= horizon):
            raise ValueError("raw reacted event time is outside (0,horizon]")
        if flags == 1 and candidate_count == 0:
            raise ValueError("raw reacted record has no evaluated candidate")
        records.append((trajectory_id, event_bits, candidate_count, flags))
    if offset != len(payload):
        raise ValueError("raw chunk has trailing or missing record bytes")
    expected_size = (
        RAW_FIXED_HEADER_BYTES
        + 8 * weight_count
        + 8 * cut_count
        + 16 * window_count
        + RAW_RECORD_BYTES * id_count
    )
    if len(payload) != expected_size:
        raise ValueError("raw chunk byte-count formula changed")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
        "master_seed": master_seed,
        "replicate_id": replicate_id,
        "chunk_id": chunk_id,
        "id_start": id_start,
        "id_count": id_count,
        "horizon_bits": "{:016x}".format(horizon_bits),
        "lambda_bits": "{:016x}".format(lambda_bits),
        "hazard_mode": hazard_mode,
        "constant_hazard_bits": "{:016x}".format(hazard_bits),
        "weights": weights,
        "basin_cuts": cuts,
        "windows": windows,
        "records": records,
    }


def summarize_parsed_chunk(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Release integer method-fixture counts from one already complete raw chunk."""

    cuts = parsed["basin_cuts"]
    windows = parsed["windows"]
    basin_counts = [0] * (len(cuts) + 1)
    window_counts = [0] * len(windows)
    reaction_count = 0
    censored_count = 0
    candidate_count_sum = 0
    candidate_count_maximum = 0
    for _trajectory_id, event_bits, candidate_count, reacted in parsed["records"]:
        event_time = struct.unpack("<d", struct.pack("<Q", event_bits))[0]
        candidate_count_sum += candidate_count
        candidate_count_maximum = max(candidate_count_maximum, candidate_count)
        if reacted:
            reaction_count += 1
            basin_counts[bisect.bisect_right(cuts, event_time)] += 1
            for index, (left, right) in enumerate(windows):
                if left <= event_time < right:
                    window_counts[index] += 1
        else:
            censored_count += 1
    if reaction_count + censored_count != parsed["id_count"]:
        raise ValueError("raw event/censor integer closure failed")
    if sum(basin_counts) != reaction_count:
        raise ValueError("raw basin integer closure failed")
    return {
        "reaction_count": reaction_count,
        "censored_count": censored_count,
        "candidate_count_sum": candidate_count_sum,
        "candidate_count_maximum": candidate_count_maximum,
        "basin_counts": basin_counts,
        "window_counts": window_counts,
    }


def combine_integer_summaries(summaries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not summaries:
        raise ValueError("at least one completed summary is required")
    basin_length = len(summaries[0]["basin_counts"])
    window_length = len(summaries[0]["window_counts"])
    if any(
        len(summary["basin_counts"]) != basin_length
        or len(summary["window_counts"]) != window_length
        for summary in summaries
    ):
        raise ValueError("cannot combine incompatible count specifications")
    return {
        "reaction_count": sum(summary["reaction_count"] for summary in summaries),
        "censored_count": sum(summary["censored_count"] for summary in summaries),
        "candidate_count_sum": sum(
            summary["candidate_count_sum"] for summary in summaries
        ),
        "candidate_count_maximum": max(
            summary["candidate_count_maximum"] for summary in summaries
        ),
        "basin_counts": [
            sum(summary["basin_counts"][index] for summary in summaries)
            for index in range(basin_length)
        ],
        "window_counts": [
            sum(summary["window_counts"][index] for summary in summaries)
            for index in range(window_length)
        ],
    }


def chunk_spec_payload(spec: ChunkSpec) -> Dict[str, Any]:
    return {
        "master_seed": spec.master_seed,
        "replicate_id": spec.replicate_id,
        "chunk_id": spec.chunk_id,
        "id_start": spec.id_start,
        "id_count": spec.id_count,
        "horizon_bits": double_bits_hex(spec.horizon),
        "lambda_bits": double_bits_hex(spec.lambda_rate),
        "hazard_mode": spec.hazard_mode,
        "constant_hazard_bits": double_bits_hex(spec.constant_hazard),
        "weight_bits": [double_bits_hex(value) for value in spec.weights],
        "basin_cut_bits": [double_bits_hex(value) for value in spec.basin_cuts],
        "window_bits": [
            [double_bits_hex(left), double_bits_hex(right)]
            for left, right in spec.windows
        ],
    }


def _validate_chunk_spec(spec: ChunkSpec) -> None:
    integer_fields = (
        ("master_seed", spec.master_seed, UINT32_MAX),
        ("replicate_id", spec.replicate_id, UINT32_MAX),
        ("chunk_id", spec.chunk_id, UINT64_MAX),
        ("id_start", spec.id_start, UINT64_MAX),
        ("id_count", spec.id_count, UINT64_MAX),
    )
    for label, value, maximum in integer_fields:
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError("{} is outside its frozen unsigned domain".format(label))
    if spec.id_count == 0 or spec.id_count - 1 > UINT64_MAX - spec.id_start:
        raise ValueError("trajectory ID range is empty or overflows uint64")
    if not math.isfinite(spec.horizon) or spec.horizon <= 0.0:
        raise ValueError("horizon is invalid")
    if not math.isfinite(spec.lambda_rate) or spec.lambda_rate <= 0.0:
        raise ValueError("Lambda is invalid")
    if spec.hazard_mode == "constant":
        if (
            not math.isfinite(spec.constant_hazard)
            or not 0.0 <= spec.constant_hazard <= spec.lambda_rate
            or spec.weights
        ):
            raise ValueError("constant-hazard contract is invalid")
    elif spec.hazard_mode == "broad-four-slab":
        if (
            double_bits_hex(spec.lambda_rate) != double_bits_hex(BROAD_LAMBDA)
            or double_bits_hex(spec.constant_hazard) != "0000000000000000"
        ):
            raise ValueError("broad-four-slab frozen-rate contract is invalid")
        bound = broad_analytic_bound_reference(spec.weights)
        if not bound < spec.lambda_rate:
            raise ValueError("broad-four-slab analytic bound exceeds Lambda")
    else:
        raise ValueError("hazard mode is invalid")
    previous_cut = 0.0
    for cut in spec.basin_cuts:
        if not math.isfinite(cut) or not previous_cut < cut < spec.horizon:
            raise ValueError("basin cuts must be finite and strictly ordered")
        previous_cut = cut
    previous_right = -1.0
    for left, right in spec.windows:
        if not (
            math.isfinite(left)
            and math.isfinite(right)
            and 0.0 <= left < right <= spec.horizon
            and left >= previous_right
        ):
            raise ValueError("windows must be finite, ordered, and disjoint")
        previous_right = right


def validate_plan(specs: Sequence[ChunkSpec]) -> Tuple[Dict[str, Any], str]:
    if not specs:
        raise ValueError("a resume plan must contain at least one chunk")
    for spec in specs:
        _validate_chunk_spec(spec)
    ordered = sorted(specs, key=lambda spec: spec.id_start)
    if len({spec.chunk_id for spec in ordered}) != len(ordered):
        raise ValueError("resume-plan chunk IDs must be unique")
    shared = (
        ordered[0].master_seed,
        ordered[0].replicate_id,
        ordered[0].horizon,
        ordered[0].lambda_rate,
        ordered[0].hazard_mode,
        ordered[0].constant_hazard,
        ordered[0].weights,
        ordered[0].basin_cuts,
        ordered[0].windows,
    )
    next_id = ordered[0].id_start
    for spec in ordered:
        observed_shared = (
            spec.master_seed,
            spec.replicate_id,
            spec.horizon,
            spec.lambda_rate,
            spec.hazard_mode,
            spec.constant_hazard,
            spec.weights,
            spec.basin_cuts,
            spec.windows,
        )
        if observed_shared != shared:
            raise ValueError("all resume-plan chunks must share one frozen method spec")
        if spec.id_count <= 0 or spec.id_start != next_id:
            raise ValueError("resume-plan trajectory ranges must be positive and contiguous")
        next_id += spec.id_count
        if next_id > 1 << 64:
            raise ValueError("resume-plan trajectory range overflows uint64")
    plan = {
        "schema_version": 2,
        "stage": "METHOD_ONLY_OFF_LATTICE_FROZEN_CHUNK_PLAN",
        "chunks": [chunk_spec_payload(spec) for spec in ordered],
        "statistical_estimates_released": False,
        "scientific_run_authorized": False,
    }
    return plan, hashlib.sha256(canonical_json_bytes(plan)).hexdigest()


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path = path.resolve()
    stage = path.with_name(".{}.partial.{}".format(path.name, os.getpid()))
    data = canonical_json_bytes(payload)
    try:
        with stage.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(stage), str(path))
        directory = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            stage.unlink()
        except FileNotFoundError:
            pass


def raw_path_for_chunk(raw_directory: Path, chunk_id: int) -> Path:
    return raw_directory.resolve() / "chunk_{:020d}.odtraw".format(chunk_id)


def attest_parsed_chunk(parsed: Dict[str, Any], spec: ChunkSpec) -> None:
    expected = {
        "master_seed": spec.master_seed,
        "replicate_id": spec.replicate_id,
        "chunk_id": spec.chunk_id,
        "id_start": spec.id_start,
        "id_count": spec.id_count,
        "horizon_bits": double_bits_hex(spec.horizon),
        "lambda_bits": double_bits_hex(spec.lambda_rate),
        "hazard_mode": spec.hazard_mode,
        "constant_hazard_bits": double_bits_hex(spec.constant_hazard),
        "weights": list(spec.weights),
        "basin_cuts": list(spec.basin_cuts),
        "windows": list(spec.windows),
    }
    for key, value in expected.items():
        if parsed[key] != value:
            raise ValueError("raw chunk does not match frozen plan field {}".format(key))
    expected_ids = range(spec.id_start, spec.id_start + spec.id_count)
    observed_ids = [record[0] for record in parsed["records"]]
    if observed_ids != list(expected_ids):
        raise ValueError("raw chunk trajectory IDs are not exact and ordered")


def execute_resume_plan(
    binary: Path,
    specs: Sequence[ChunkSpec],
    raw_directory: Path,
    ledger_path: Path,
    *,
    selected_chunk_ids: Sequence[int] = (),
) -> Dict[str, Any]:
    """Execute or exact-rerun selected chunks without releasing any estimate."""

    plan, plan_hash = validate_plan(specs)
    raw_directory = raw_directory.resolve()
    ledger_path = ledger_path.resolve()
    raw_directory.mkdir(parents=True, exist_ok=True)
    if ledger_path.parent != raw_directory:
        raise ValueError("resume ledger and raw chunks must share one directory")
    if ledger_path.exists():
        ledger_bytes = ledger_path.read_bytes()
        ledger = json.loads(ledger_bytes)
        if canonical_json_bytes(ledger) != ledger_bytes:
            raise ValueError("resume ledger is not canonical JSON")
        if (
            set(ledger)
            != {"schema_version", "plan", "plan_sha256", "completed_chunks"}
            or ledger["schema_version"] != 2
            or ledger["plan"] != plan
            or ledger["plan_sha256"] != plan_hash
            or type(ledger["completed_chunks"]) is not dict
        ):
            raise ValueError("resume ledger does not match the frozen plan")
    else:
        ledger = {
            "schema_version": 2,
            "plan": plan,
            "plan_sha256": plan_hash,
            "completed_chunks": {},
        }
        atomic_write_json(ledger_path, ledger)
    by_id = {spec.chunk_id: spec for spec in specs}
    selected = set(selected_chunk_ids) if selected_chunk_ids else set(by_id)
    if not selected.issubset(by_id):
        raise ValueError("selected resume chunk ID is outside the frozen plan")
    for chunk_id in sorted(selected):
        spec = by_id[chunk_id]
        key = str(chunk_id)
        raw_path = raw_path_for_chunk(raw_directory, chunk_id)
        entry = ledger["completed_chunks"].get(key)
        if entry is not None:
            if set(entry) != {"id_start", "id_count", "raw_byte_count", "raw_sha256"}:
                raise ValueError("resume ledger chunk entry is malformed")
            if not raw_path.exists():
                _completed, rerun = run_chunk(binary, spec, raw_path)
                if (
                    rerun["raw_sha256"] != entry["raw_sha256"]
                    or rerun["raw_byte_count"] != entry["raw_byte_count"]
                ):
                    raw_path.unlink(missing_ok=True)
                    raise ValueError("exact-ID resume rerun changed raw chunk bytes")
            parsed = parse_raw_chunk(raw_path)
            attest_parsed_chunk(parsed, spec)
            if (
                parsed["sha256"] != entry["raw_sha256"]
                or parsed["byte_count"] != entry["raw_byte_count"]
            ):
                raise ValueError("completed raw chunk disagrees with its resume ledger")
            continue
        if raw_path.exists():
            raise ValueError("unledgered raw chunk exists; implicit adoption is forbidden")
        _completed, operational = run_chunk(binary, spec, raw_path)
        forbidden_estimate_keys = {
            "reaction_count",
            "censored_count",
            "basin_counts",
            "window_counts",
            "candidate_count_sum",
        }
        if forbidden_estimate_keys.intersection(operational):
            raise ValueError("chunk command released a partial statistical estimate")
        parsed = parse_raw_chunk(raw_path)
        attest_parsed_chunk(parsed, spec)
        if parsed["sha256"] != operational["raw_sha256"]:
            raise ValueError("new raw chunk hash disagrees with independent parser")
        ledger["completed_chunks"][key] = {
            "id_start": spec.id_start,
            "id_count": spec.id_count,
            "raw_byte_count": parsed["byte_count"],
            "raw_sha256": parsed["sha256"],
        }
        atomic_write_json(ledger_path, ledger)
    completed = sorted(int(key) for key in ledger["completed_chunks"])
    missing = sorted(set(by_id) - set(completed))
    return {
        "schema_version": 2,
        "stage": "METHOD_ONLY_OFF_LATTICE_RESUME_STATUS",
        "plan_sha256": plan_hash,
        "completed_chunk_ids": completed,
        "missing_chunk_ids": missing,
        "statistical_estimates_released": False,
        "scientific_run_authorized": False,
    }


def finalize_resume_plan(
    specs: Sequence[ChunkSpec], raw_directory: Path, ledger_path: Path
) -> Dict[str, Any]:
    """Release integer fixture counts only after every frozen chunk attests."""

    plan, plan_hash = validate_plan(specs)
    raw_directory = raw_directory.resolve()
    ledger_path = ledger_path.resolve()
    if not ledger_path.exists():
        raise ValueError("cannot finalize a missing resume ledger")
    ledger_bytes = ledger_path.read_bytes()
    ledger = json.loads(ledger_bytes)
    if canonical_json_bytes(ledger) != ledger_bytes:
        raise ValueError("resume ledger is not canonical JSON")
    if (
        set(ledger) != {"schema_version", "plan", "plan_sha256", "completed_chunks"}
        or ledger.get("schema_version") != 2
        or ledger.get("plan") != plan
        or ledger.get("plan_sha256") != plan_hash
    ):
        raise ValueError("resume ledger plan changed before finalization")
    expected_ids = {str(spec.chunk_id) for spec in specs}
    completed = ledger.get("completed_chunks")
    if type(completed) is not dict or set(completed) != expected_ids:
        raise ValueError("all frozen chunks must complete before estimates are released")
    for spec in specs:
        entry = completed[str(spec.chunk_id)]
        if (
            type(entry) is not dict
            or set(entry) != {"id_start", "id_count", "raw_byte_count", "raw_sha256"}
            or entry["id_start"] != spec.id_start
            or entry["id_count"] != spec.id_count
            or type(entry["raw_byte_count"]) is not int
            or entry["raw_byte_count"] < 0
            or type(entry["raw_sha256"]) is not str
            or len(entry["raw_sha256"]) != 64
            or any(character not in "0123456789abcdef" for character in entry["raw_sha256"])
        ):
            raise ValueError("resume ledger chunk entry is malformed")
    partials = list(raw_directory.glob("*.partial.*")) + list(
        raw_directory.glob(".*.partial.*")
    )
    if partials:
        raise ValueError("partial staging files exist at finalization")
    summaries = []
    raw_hashes = []
    for spec in sorted(specs, key=lambda item: item.id_start):
        raw_path = raw_path_for_chunk(raw_directory, spec.chunk_id)
        parsed = parse_raw_chunk(raw_path)
        attest_parsed_chunk(parsed, spec)
        entry = completed[str(spec.chunk_id)]
        if (
            parsed["sha256"] != entry["raw_sha256"]
            or parsed["byte_count"] != entry["raw_byte_count"]
        ):
            raise ValueError("final raw chunk hash/size disagrees with ledger")
        summaries.append(summarize_parsed_chunk(parsed))
        raw_hashes.append(parsed["sha256"])
    combined = combine_integer_summaries(summaries)
    total_count = sum(spec.id_count for spec in specs)
    if combined["reaction_count"] + combined["censored_count"] != total_count:
        raise ValueError("final plan integer closure failed")
    return {
        "schema_version": 2,
        "stage": "METHOD_ONLY_OFF_LATTICE_COMPLETE_PLAN_INTEGER_COUNTS",
        "plan_sha256": plan_hash,
        "trajectory_count": total_count,
        "raw_chunk_sha256": raw_hashes,
        **combined,
        "statistical_estimates_released": True,
        "scientific_run_authorized": False,
    }


def dkw_half_width(sample_size: int, alpha: float) -> float:
    if type(sample_size) is not int or sample_size <= 0:
        raise ValueError("DKW sample size must be a positive integer")
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("DKW alpha must lie strictly inside (0,1)")
    return math.sqrt(math.log(2.0 / alpha) / (2.0 * sample_size))


def benchmark_core(
    binary: Path,
    trajectory_count: int,
    *,
    constant_hazard: float = 0.05,
    lambda_rate: float = 0.13,
) -> Dict[str, Any]:
    if trajectory_count < 1:
        raise ValueError("benchmark trajectory count must be positive")
    with tempfile.TemporaryDirectory(prefix="odt-core-benchmark-") as directory:
        raw = Path(directory) / "synthetic_constant_hazard.raw"
        spec = synthetic_method_spec(
            id_count=trajectory_count,
            constant_hazard=constant_hazard,
            lambda_rate=lambda_rate,
        )
        start = time.perf_counter()
        _completed, summary = run_chunk(binary, spec, raw)
        elapsed = time.perf_counter() - start
        parsed = parse_raw_chunk(raw)
        if parsed["sha256"] != summary["raw_sha256"]:
            raise RuntimeError("benchmark raw SHA-256 mismatch")
        integer_summary = summarize_parsed_chunk(parsed)
    throughput = trajectory_count / elapsed
    return {
        "stage": "SMALL_SYNTHETIC_CONSTANT_HAZARD_BENCHMARK_ONLY",
        "trajectory_count": trajectory_count,
        "horizon": 100.0,
        "lambda": lambda_rate,
        "constant_hazard": constant_hazard,
        "elapsed_seconds": elapsed,
        "trajectories_per_second": throughput,
        "raw_bytes": summary["raw_byte_count"],
        "candidate_count_sum": integer_summary["candidate_count_sum"],
        "candidate_count_per_trajectory": integer_summary["candidate_count_sum"]
        / trajectory_count,
        "candidates_per_second": integer_summary["candidate_count_sum"] / elapsed,
        "claim_boundary": (
            "bounded constant-hazard timing fixture only; no production-size "
            "projection and no scientific GO"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--trajectories", type=int, default=20_000)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    if not arguments.benchmark:
        raise SystemExit("harness execution requires --benchmark")
    with tempfile.TemporaryDirectory(prefix="odt-core-build-") as directory:
        binary = Path(directory) / "off_lattice_doi_compiled_core"
        build = build_core(binary)
        fixtures = run_fixtures(binary)
        reference = fixture_reference()
        if tuple(int(value, 16) for value in fixtures["philox_known_zero_vector"]) != tuple(
            reference["known_zero"]
        ):
            raise RuntimeError("known Philox vector mismatch before benchmark")
        result = {
            "build": build,
            "benchmarks": {
                "reacting_k_0p05": benchmark_core(
                    binary, arguments.trajectories, constant_hazard=0.05
                ),
                "zero_hazard_full_horizon": benchmark_core(
                    binary, arguments.trajectories, constant_hazard=0.0
                ),
                "zero_hazard_full_horizon_lambda_0p35": benchmark_core(
                    binary,
                    arguments.trajectories,
                    constant_hazard=0.0,
                    lambda_rate=0.35,
                ),
            },
            "scientific_run_authorized": False,
        }
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
