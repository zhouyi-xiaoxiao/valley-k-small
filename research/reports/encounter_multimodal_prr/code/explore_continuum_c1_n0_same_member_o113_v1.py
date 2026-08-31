"""Explore one O113/Base level-zero mass/flux/map/killing composition.

This is deliberately a small scientific de-risking tool, not a production
roles-8--10 implementation.  It recomputes the formula-defined raw SG factors
and physical cell integrals, evaluates the accepted control-free contact and
profile kernels, and composes one factorized O113/Base object in one ordinary
Python process.

The resulting JSON is an exploratory same-process composition receipt only.
It is not an externally committed correlated production member, does not turn
marginal interval boxes into one exact irrational point, and does not promote
C1/C2/C3, F0/F1, propagation, topology, release, or submission claims.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import resource
import struct
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

REPORT_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = Path(__file__).resolve().parent
COORDINATES = ("midpoint", "relative_parallel", "relative_perpendicular")
ROW_LABEL = "O113/Base"
SHAPE = (113, 113, 113)
PRIMARY_BITS = 320
SENTINEL_BITS = 640
ROLE10_BITS = 192
PANELS_PER_UNIT = 16_384
MAX_WALL_SECONDS = 180.0
MAX_RSS_BYTES = 512 * 1024 * 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
SCHEMA = "encounter_continuum_c1_n0_o113_exploratory_composition_receipt_v1"
STATUS = (
    "PASS_EXPLORATORY_O113_SAME_PROCESS_FORMULA_COMPOSITION_WITH_"
    "DISCLOSED_BARYCENTRE_CONTROL_ONLY_"
    "NOT_CORRELATED_PRODUCTION_MEMBER_NOT_SAME_MEMBER_ACCEPTANCE"
)

PRIMARY_PATHS = {
    "configuration": Path("artifacts/data/physical_configuration_family_control_free_v1.json"),
    "reference_density": Path("artifacts/data/continuum_c1_reference_density_source_v1.json"),
    "ideal_formula": Path("artifacts/data/continuum_c1_ideal_formula_source_v1.json"),
    "factorization": Path("artifacts/data/continuum_c1_factorization_source_v1.json"),
    "killing_geometry": Path("artifacts/data/physical_killing_geometry_source_v1.json"),
    "symbolic_control": Path("artifacts/data/continuum_c1_symbolic_control_method_source_v1.json"),
}
PARTITION_ROOT = Path("artifacts/data/physical_production_initial_stream_v1/rows/00_o113_base")
RAW_ORACLE_PATH = Path("artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json")
STATIONARY_ORACLE_PATH = Path("artifacts/data/continuum_c1_stationary_integral_source_v1.json")
ROLE10_ROOT = Path("artifacts/data/physical_production_killing_geometry_v1")
PRIMARY_SHA256 = {
    "configuration": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    "reference_density": "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    "ideal_formula": "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    "factorization": "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
    "killing_geometry": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    "symbolic_control": "fd6edf9046956d311366ff51f229523ab605d80073515b9768d5fa5cafa8904f",
}
PARTITION_SHA256 = {
    "midpoint": "f36127a87a19a13df6108a527a2285361be082ca81f2184e68c3c47655e7ca94",
    "relative_parallel": "318ee1287c419f8ed91e19e4426657e2ec28d4e367859f71373061ada7382424",
    "relative_perpendicular": "66f21ab3a8314dbede0f1aac6cd0bbba0738d22f75f8a7334bd79463a204d9d8",
}
ORACLE_SHA256 = {
    "raw": "04fee91f8708d90febc23e1f1ee4cfc1cb4800b9e35980eb99006fad327b40f3",
    "stationary": "03db61b4aa9c2b7a4ab2fd78c86fbbf90dd1548657c615d91c1526ae3ed77212",
    "role10_row": "63ccb3bc7a339c29bebf5609b699c203ba931844ffdf7d31e675af557589b55a",
}
KERNEL_PATHS = {
    "role8_formula_kernel": Path(
        "code/build_continuum_c1_n0_candidate_native_raw_axis_formula_v1.py"
    ),
    "role9_integral_kernel": Path(
        "code/build_continuum_c1_n0_candidate_native_stationary_integrals_v1.py"
    ),
    "role10_factor_kernel": Path("code/rate_defined_tensor_f0.py"),
    "partition_kernel": Path("code/rate_defined_tensor_f0_production_initial_stream.py"),
}
KERNEL_SHA256 = {
    "role8_formula_kernel": "667855b3dc1a24f03b1c118b8c1f5f09a86850c5e359e47f345e5e66c20e2f9f",
    "role9_integral_kernel": "9b1c4867ff74e1bb0df388b093312d866f6b4fdf455110a1dd36240612ae3aca",
    "role10_factor_kernel": "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5",
    "partition_kernel": "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb",
}


class ExploratoryReceiptError(RuntimeError):
    """Fail-closed error for the bounded exploratory computation."""


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: Any, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise ExploratoryReceiptError(f"{label}: canonical p/q required")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ExploratoryReceiptError(f"{label}: invalid fraction") from error
    if _fraction_text(result) != value:
        raise ExploratoryReceiptError(f"{label}: noncanonical fraction")
    return result


def _hex_fraction(value: Any, label: str) -> Fraction:
    if type(value) is not str:
        raise ExploratoryReceiptError(f"{label}: binary64 hex required")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise ExploratoryReceiptError(f"{label}: invalid binary64 hex") from error
    if not math.isfinite(parsed) or parsed.hex() != value:
        raise ExploratoryReceiptError(f"{label}: noncanonical binary64 hex")
    return Fraction.from_float(parsed)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise ExploratoryReceiptError("duplicate or non-string JSON key")
        result[key] = value
    return result


def _read_json(relative: Path) -> tuple[dict[str, Any], bytes]:
    path = REPORT_ROOT / relative
    raw = path.read_bytes()
    try:
        payload = json.loads(raw, object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExploratoryReceiptError(f"invalid JSON: {relative}") from error
    if type(payload) is not dict:
        raise ExploratoryReceiptError(f"JSON root is not an object: {relative}")
    return payload, raw


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


@dataclass
class ResourceGuard:
    started: float

    @classmethod
    def start(cls) -> "ResourceGuard":
        return cls(time.monotonic())

    def check(self, phase: str) -> None:
        elapsed = time.monotonic() - self.started
        rss = _peak_rss_bytes()
        if elapsed > MAX_WALL_SECONDS:
            raise ExploratoryReceiptError(f"resource cap: {phase} exceeded {MAX_WALL_SECONDS:.0f}s")
        if rss > MAX_RSS_BYTES:
            raise ExploratoryReceiptError(
                f"resource cap: {phase} exceeded {MAX_RSS_BYTES} RSS bytes"
            )


@dataclass(frozen=True, slots=True)
class Interval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise ExploratoryReceiptError("interval endpoints must be exact Fractions")
        if self.lower > self.upper:
            raise ExploratoryReceiptError("reversed interval")

    @classmethod
    def point(cls, value: Fraction | int) -> "Interval":
        exact = Fraction(value)
        return cls(exact, exact)

    @classmethod
    def from_kernel(cls, value: Any) -> "Interval":
        return cls(Fraction(value.lower), Fraction(value.upper))

    @classmethod
    def from_f0(cls, value: Any) -> "Interval":
        return cls(Fraction.from_float(value.lower), Fraction.from_float(value.upper))

    def add(self, other: "Interval") -> "Interval":
        return Interval(self.lower + other.lower, self.upper + other.upper)

    def multiply(self, other: "Interval") -> "Interval":
        if self.lower < 0 or other.lower < 0:
            raise ExploratoryReceiptError("negative interval product factor")
        return Interval(self.lower * other.lower, self.upper * other.upper)

    def scale(self, value: Fraction | int) -> "Interval":
        scale = Fraction(value)
        if scale < 0:
            raise ExploratoryReceiptError("negative interval scale")
        return Interval(self.lower * scale, self.upper * scale)

    def divide(self, other: "Interval") -> "Interval":
        if self.lower < 0 or other.lower <= 0:
            raise ExploratoryReceiptError("invalid positive interval division")
        return Interval(self.lower / other.upper, self.upper / other.lower)

    def intersect(self, other: "Interval") -> "Interval":
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise ExploratoryReceiptError("disjoint interval witnesses")
        return Interval(lower, upper)

    def contains(self, other: "Interval") -> bool:
        return self.lower <= other.lower and other.upper <= self.upper

    def overlaps(self, other: "Interval") -> bool:
        return max(self.lower, other.lower) <= min(self.upper, other.upper)

    def json(self) -> dict[str, str]:
        return {
            "lower_exact_p_over_q": _fraction_text(self.lower),
            "upper_exact_p_over_q": _fraction_text(self.upper),
        }


def _sum_intervals(values: Iterable[Interval]) -> Interval:
    result = Interval.point(0)
    for value in values:
        result = result.add(value)
    return result


def _product_intervals(values: Iterable[Interval]) -> Interval:
    result = Interval.point(1)
    for value in values:
        result = result.multiply(value)
    return result


def _interval_from_json(value: Any, label: str) -> Interval:
    if type(value) is not dict:
        raise ExploratoryReceiptError(f"{label}: interval object required")
    lower = value.get("lower_exact_p_over_q", value.get("lower_exact"))
    upper = value.get("upper_exact_p_over_q", value.get("upper_exact"))
    return Interval(_fraction(lower, f"{label} lower"), _fraction(upper, f"{label} upper"))


class RecordDigest:
    """Length-framed deterministic digest for factorized or streamed records."""

    def __init__(self, domain: str):
        self._digest = hashlib.sha256(domain.encode("ascii") + b"\0")
        self.count = 0

    def add(self, value: Any) -> None:
        raw = _canonical_bytes(value)
        self._digest.update(len(raw).to_bytes(8, "big"))
        self._digest.update(raw)
        self.count += 1

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


@dataclass(frozen=True, slots=True)
class FormalMonomial:
    coefficient: Fraction
    powers: tuple[tuple[str, int], ...]

    @classmethod
    def atom(cls, name: str) -> "FormalMonomial":
        return cls(Fraction(1), ((name, 1),))

    @classmethod
    def one(cls) -> "FormalMonomial":
        return cls(Fraction(1), ())

    @classmethod
    def make(cls, coefficient: Fraction, powers: dict[str, int]) -> "FormalMonomial":
        return cls(
            coefficient, tuple(sorted((key, value) for key, value in powers.items() if value))
        )

    def multiply(self, other: "FormalMonomial") -> "FormalMonomial":
        powers = dict(self.powers)
        for key, value in other.powers:
            powers[key] = powers.get(key, 0) + value
        return FormalMonomial.make(self.coefficient * other.coefficient, powers)

    def divide(self, other: "FormalMonomial") -> "FormalMonomial":
        if other.coefficient == 0:
            raise ExploratoryReceiptError("formal division by zero")
        powers = dict(self.powers)
        for key, value in other.powers:
            powers[key] = powers.get(key, 0) - value
        return FormalMonomial.make(self.coefficient / other.coefficient, powers)

    def json(self) -> dict[str, Any]:
        return {
            "coefficient_exact": _fraction_text(self.coefficient),
            "powers": [{"symbol": key, "exponent": value} for key, value in self.powers],
        }


def build_formal_lane() -> dict[str, Any]:
    ml = FormalMonomial.atom("M_L")
    sm = FormalMonomial.atom("S_M")
    sr = FormalMonomial.atom("S_R")
    sy = FormalMonomial.atom("S_Y")
    gauge = ml.divide(sm.multiply(sr).multiply(sy))
    mu_a = FormalMonomial.atom("mu_axis")
    mu_s1 = FormalMonomial.atom("mu_spectator_1")
    mu_s2 = FormalMonomial.atom("mu_spectator_2")
    kappa = FormalMonomial.atom("kappa_edge")
    pi_h = gauge.multiply(mu_a).multiply(mu_s1).multiply(mu_s2)
    q = kappa.divide(mu_a)
    conductance = gauge.multiply(kappa).multiply(mu_s1).multiply(mu_s2)
    mpi = FormalMonomial.atom("M_pi_cell")
    rho = mpi.divide(pi_h)
    c = FormalMonomial.atom("contact_average")
    phi = FormalMonomial.atom("profile_average")
    width = FormalMonomial.atom("W")
    v = c.multiply(phi).divide(width)
    k = v.divide(rho)
    identities = {
        "global_gauge_mass": (
            gauge.multiply(sm).multiply(sr).multiply(sy),
            ml,
        ),
        "detailed_balance_conductance": (pi_h.multiply(q), conductance),
        "map_ratio": (rho.multiply(pi_h), mpi),
        "two_path_k": (k, v.multiply(pi_h).divide(mpi)),
        "killing_mass_identity": (mpi.multiply(k), pi_h.multiply(v)),
    }
    serialized: dict[str, Any] = {}
    for name, (left, right) in identities.items():
        serialized[name] = {
            "canonical_equal": left == right,
            "left": left.json(),
            "right": right.json(),
        }
    missing_w = c.multiply(phi)
    duplicate_w = v.divide(width)
    return {
        "method": "sparse_exact_rational_laurent_monomials_over_formula_bound_atoms",
        "irrational_primitives_remain_unselected_formula_atoms": True,
        "interval_midpoint_or_rational_selector_used": False,
        "identities": serialized,
        "all_identities_passed": all(item["canonical_equal"] for item in serialized.values()),
        "mutation_sentinels": {
            "missing_W_inverse_rejected": missing_w != v,
            "duplicated_W_inverse_rejected": duplicate_w != v,
            "V_is_not_K_without_rho": v != k,
            "raw_mu_is_not_physical_M_pi": FormalMonomial.atom("mu_axis")
            != FormalMonomial.atom("M_pi_axis"),
        },
    }


@lru_cache(maxsize=1)
def _kernels() -> tuple[Any, Any, Any, Any]:
    for role, relative in KERNEL_PATHS.items():
        if _file_sha256(REPORT_ROOT / relative) != KERNEL_SHA256[role]:
            raise ExploratoryReceiptError(f"{role}: kernel SHA-256 currentness failure")
    if str(CODE_ROOT) not in sys.path:
        sys.path.insert(0, str(CODE_ROOT))
    raw = importlib.import_module("build_continuum_c1_n0_candidate_native_raw_axis_formula_v1")
    stationary = importlib.import_module(
        "build_continuum_c1_n0_candidate_native_stationary_integrals_v1"
    )
    f0 = importlib.import_module("rate_defined_tensor_f0")
    initial = importlib.import_module("rate_defined_tensor_f0_production_initial_stream")
    return raw, stationary, f0, initial


def _validate_semantic_source_joins(
    payloads: dict[str, dict[str, Any]],
    partitions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    config = payloads["configuration"]
    reference = payloads["reference_density"]
    factorization = payloads["factorization"]
    killing = payloads["killing_geometry"]
    control = payloads["symbolic_control"]
    coordinates = list(COORDINATES)
    if not (
        config.get("coordinate_order")
        == reference.get("coordinate_order")
        == factorization.get("coordinate_and_storage", {}).get("coordinate_order")
        == killing.get("coordinate_order")
        == coordinates
    ):
        raise ExploratoryReceiptError("cross-source coordinate-order join failed")

    dynamics = config["dynamics"]
    reference_parameters = reference.get("physical_parameter_bundle", {})
    for key in (
        "particle_diffusion_binary64_hex",
        "ou_stiffness_binary64_hex",
        "ou_mean_binary64_hex",
        "transverse_period_exact",
    ):
        if dynamics.get(key) != reference_parameters.get(key):
            raise ExploratoryReceiptError(f"configuration/reference parameter join failed: {key}")
    for key in ("physical_dimension", "quotient_dimension"):
        if config.get(key) != reference_parameters.get(key):
            raise ExploratoryReceiptError(f"configuration/reference dimension join failed: {key}")

    configuration_sha = PRIMARY_SHA256["configuration"]
    killing_sha = PRIMARY_SHA256["killing_geometry"]
    factorization_sha = PRIMARY_SHA256["factorization"]
    if (
        reference.get("source_pins", {}).get("configuration_source", {}).get("sha256")
        != configuration_sha
        or killing.get("configuration_bundle", {}).get("configuration_sha256") != configuration_sha
        or factorization.get("source_pins", {}).get("killing_geometry_authority", {}).get("sha256")
        != killing_sha
        or control.get("source_pins", {}).get("factorization_source", {}).get("sha256")
        != factorization_sha
        or control.get("source_pins", {}).get("killing_geometry_authority", {}).get("sha256")
        != killing_sha
    ):
        raise ExploratoryReceiptError("cross-source authority-hash join failed")

    factor_contact = factorization.get("contact_geometry", {})
    killing_contact = killing.get("contact_geometry", {})
    if (
        factor_contact.get("contact_radius_exact") != killing_contact.get("radius_exact")
        or factor_contact.get("transverse_period_exact")
        != killing_contact.get("transverse_period_exact")
        or dynamics.get("transverse_period_exact") != killing_contact.get("transverse_period_exact")
    ):
        raise ExploratoryReceiptError("contact radius/period semantic join failed")
    factor_profile = factorization.get("profile_basis", {})
    killing_profile = killing.get("support_basis", {})
    if (
        factor_profile.get("centre_exact") != killing_profile.get("centres_exact")
        or factor_profile.get("half_width_exact") != killing_profile.get("half_width_exact")
        or factor_profile.get("profile_count") != killing_profile.get("profile_count")
        or factor_profile.get("analytic_integral_each")
        != killing_profile.get("analytic_integral_each")
    ):
        raise ExploratoryReceiptError("profile-basis semantic join failed")

    control_contract = control.get("control_contract", {})
    control_boundary = control.get("claim_boundary", {})
    if not (
        control.get("schema") == "encounter_continuum_c1_symbolic_control_method_source_v1"
        and control_contract.get("future_weight_vector_length") == 4
        and control_contract.get("each_weight_nonnegative") is True
        and control_contract.get("exact_sum_one_required") is True
        and control_boundary.get("actual_control_values_present") is False
        and control_boundary.get("budget_present") is False
    ):
        raise ExploratoryReceiptError("symbolic control/no-value contract drift")

    row = config["configurations"][0]
    for coordinate in COORDINATES:
        partition = partitions[coordinate]
        axis = row[coordinate]
        expected_construction = config["axis_construction_contracts"][axis["alignment"]][
            "source_construction_tag"
        ]
        if coordinate == "relative_perpendicular":
            expected_start = _fraction(
                dynamics["transverse_domain_start_exact"], "transverse domain start"
            )
            expected_width = _fraction(dynamics["transverse_period_exact"], "transverse period")
            expected_periodic = True
            expected_shift = _fraction(axis["periodic_shift_exact"], "periodic shift")
        else:
            expected_start = _hex_fraction(axis["lower_binary64_hex"], f"{coordinate} lower")
            expected_upper = _hex_fraction(axis["upper_binary64_hex"], f"{coordinate} upper")
            expected_width = expected_upper - expected_start
            expected_periodic = False
            expected_shift = Fraction(0)
        if not (
            partition.get("construction") == expected_construction
            and partition.get("periodic") is expected_periodic
            and _fraction(partition.get("domain_start_exact"), f"{coordinate} partition start")
            == expected_start
            and _fraction(partition.get("domain_width_exact"), f"{coordinate} partition width")
            == expected_width
            and _fraction(
                partition.get("periodic_shift_exact"),
                f"{coordinate} partition shift",
            )
            == expected_shift
        ):
            raise ExploratoryReceiptError(
                f"{coordinate}: configuration/partition semantic join failed"
            )

    return {
        "coordinate_order_equal": True,
        "configuration_reference_parameters_equal": True,
        "authority_hash_edges_equal": True,
        "contact_radius_period_equal": True,
        "profile_basis_equal": True,
        "symbolic_control_source_contains_no_values_or_budget": True,
        "configuration_partition_geometry_equal": True,
    }


def _validate_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    sources: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, relative in PRIMARY_PATHS.items():
        payload, raw = _read_json(relative)
        observed = _sha256(raw)
        if observed != PRIMARY_SHA256[name]:
            raise ExploratoryReceiptError(f"{name}: primary SHA-256 currentness failure")
        payloads[name] = payload
        sources[name] = {
            "path": relative.as_posix(),
            "sha256": observed,
            "literal_current_sha256_pin_checked": True,
        }
    config = payloads["configuration"]
    reference = payloads["reference_density"]
    formula = payloads["ideal_formula"]
    factorization = payloads["factorization"]
    killing = payloads["killing_geometry"]
    control = payloads["symbolic_control"]
    if config.get("schema") != "encounter_physical_configuration_family_control_free_v1":
        raise ExploratoryReceiptError("configuration schema drift")
    rows = config.get("configurations")
    if type(rows) is not list or not rows or rows[0].get("label") != ROW_LABEL:
        raise ExploratoryReceiptError("O113/Base is not configuration row zero")
    row = rows[0]
    if tuple(row.get("shape", ())) != SHAPE or row.get("expected_states") != math.prod(SHAPE):
        raise ExploratoryReceiptError("O113 shape/state count drift")
    if reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1":
        raise ExploratoryReceiptError("reference-density schema drift")
    if formula.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1":
        raise ExploratoryReceiptError("ideal-formula schema drift")
    if (
        factorization.get("schema") != "encounter_continuum_c1_factorization_source_v1"
        or factorization.get("coordinate_and_storage", {}).get("periodic_normalization") != "W^-1"
    ):
        raise ExploratoryReceiptError("factorization/W^-1 contract drift")
    if (
        killing.get("schema") != "encounter_physical_killing_geometry_source_v1"
        or killing.get("flags", {}).get("contains_budget_value") is not False
        or killing.get("flags", {}).get("contains_control_values") is not False
    ):
        raise ExploratoryReceiptError("control-free killing source drift")
    if control.get("schema") != "encounter_continuum_c1_symbolic_control_method_source_v1":
        raise ExploratoryReceiptError("symbolic-control schema drift")
    partitions: dict[str, Any] = {}
    for coordinate in COORDINATES:
        relative = PARTITION_ROOT / f"{coordinate}.partition.json"
        partition, raw = _read_json(relative)
        if (
            partition.get("schema") != "encounter_exact_axis_partition_v1"
            or partition.get("coordinate") != coordinate
            or partition.get("size") != 113
        ):
            raise ExploratoryReceiptError(f"{coordinate}: partition identity drift")
        observed = _sha256(raw)
        if observed != PARTITION_SHA256[coordinate]:
            raise ExploratoryReceiptError(f"{coordinate}: partition SHA-256 currentness failure")
        partitions[coordinate] = partition
        sources[f"partition_{coordinate}"] = {
            "path": relative.as_posix(),
            "sha256": observed,
            "literal_current_sha256_pin_checked": True,
        }
    for role, relative in KERNEL_PATHS.items():
        observed = _file_sha256(REPORT_ROOT / relative)
        if observed != KERNEL_SHA256[role]:
            raise ExploratoryReceiptError(f"{role}: kernel SHA-256 currentness failure")
        sources[role] = {
            "path": relative.as_posix(),
            "sha256": observed,
            "literal_current_sha256_pin_checked": True,
        }
    semantic_joins = _validate_semantic_source_joins(payloads, partitions)
    return (
        config,
        partitions,
        {
            "sources": sources,
            "payloads": payloads,
            "semantic_joins": semantic_joins,
        },
    )


def _partition_values(
    partition: dict[str, Any],
) -> tuple[
    tuple[Fraction, ...],
    tuple[Fraction, ...],
    tuple[tuple[tuple[Fraction, Fraction], ...], ...],
]:
    positions = tuple(
        _fraction(value, "partition position") for value in partition["positions_exact"]
    )
    volumes = tuple(
        _fraction(value, "partition volume") for value in partition["cell_volumes_exact"]
    )
    segments = tuple(
        tuple(
            (
                _fraction(pair[0], "segment lower"),
                _fraction(pair[1], "segment upper"),
            )
            for pair in cell
        )
        for cell in partition["cell_segments_exact"]
    )
    if len(positions) != 113 or len(volumes) != 113 or len(segments) != 113:
        raise ExploratoryReceiptError("partition array length drift")
    if any(
        sum((upper - lower for lower, upper in cell), Fraction(0)) != volume
        for cell, volume in zip(segments, volumes, strict=True)
    ):
        raise ExploratoryReceiptError("partition segment-volume closure failed")
    return positions, volumes, segments


@dataclass(frozen=True, slots=True)
class RawEdge:
    left: int
    right: int
    q_forward: Interval
    q_reverse: Interval
    kappa: Interval
    direct_left: Interval


@dataclass(frozen=True, slots=True)
class AxisScience:
    coordinate: str
    periodic: bool
    positions: tuple[Fraction, ...]
    volumes: tuple[Fraction, ...]
    segments: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    raw_mu: tuple[Interval, ...]
    physical_mass: tuple[Interval, ...]
    edges: tuple[RawEdge, ...]
    raw_sum: Interval
    physical_sum: Interval
    sentinel_containment_checks: int


def _build_role8_role9(
    config: dict[str, Any],
    partitions: dict[str, Any],
    guard: ResourceGuard,
) -> tuple[tuple[AxisScience, ...], dict[str, Any]]:
    raw_kernel, stationary_kernel, _, _ = _kernels()
    dynamics = config["dynamics"]
    particle_diffusion = _hex_fraction(
        dynamics["particle_diffusion_binary64_hex"], "particle diffusion"
    )
    stiffness = _hex_fraction(dynamics["ou_stiffness_binary64_hex"], "OU stiffness")
    mean = _hex_fraction(dynamics["ou_mean_binary64_hex"], "OU mean")
    width = _fraction(dynamics["transverse_period_exact"], "transverse period")
    axes: list[AxisScience] = []
    factor_digest = RecordDigest("encounter-o113-role8-role9-factors-v1")
    total_sentinel_checks = 0

    for coordinate in COORDINATES:
        partition = partitions[coordinate]
        positions, volumes, segments = _partition_values(partition)
        potentials = raw_kernel._potentials(
            coordinate,
            list(positions),
            stiffness=stiffness,
            diffusion=particle_diffusion,
            mean=mean,
        )
        axis_diffusion = (
            particle_diffusion / 2 if coordinate == "midpoint" else 2 * particle_diffusion
        )
        raw_mu_primary: list[Interval] = []
        raw_mu_sentinel: list[Interval] = []
        for potential, volume in zip(potentials, volumes, strict=True):
            primary = Interval.from_kernel(raw_kernel._raw_mu(potential, volume, PRIMARY_BITS))
            sentinel = Interval.from_kernel(raw_kernel._raw_mu(potential, volume, SENTINEL_BITS))
            if not primary.contains(sentinel):
                raise ExploratoryReceiptError(f"{coordinate}: raw-mu sentinel escaped")
            raw_mu_primary.append(primary)
            raw_mu_sentinel.append(sentinel)
            total_sentinel_checks += 1

        periodic = bool(partition["periodic"])
        edge_pairs = (
            [(index, index + 1) for index in range(112)]
            if not periodic
            else [(index, (index + 1) % 113) for index in range(113)]
        )
        edges: list[RawEdge] = []
        for left, right in edge_pairs:
            distance = (
                _fraction(partition["domain_width_exact"], "period width") / 113
                if periodic
                else positions[right] - positions[left]
            )
            delta = potentials[right] - potentials[left]
            q_forward = Interval.from_kernel(
                raw_kernel._directed_rate(
                    delta, axis_diffusion, volumes[left], distance, PRIMARY_BITS
                )
            )
            q_reverse = Interval.from_kernel(
                raw_kernel._directed_rate(
                    -delta, axis_diffusion, volumes[right], distance, PRIMARY_BITS
                )
            )
            direct_left = Interval.from_kernel(
                raw_kernel._direct_kappa(
                    potentials[left], delta, axis_diffusion, distance, PRIMARY_BITS
                )
            )
            direct_right = Interval.from_kernel(
                raw_kernel._direct_kappa(
                    potentials[right], -delta, axis_diffusion, distance, PRIMARY_BITS
                )
            )
            witnesses = (
                direct_left,
                direct_right,
                raw_mu_primary[left].multiply(q_forward),
                raw_mu_primary[right].multiply(q_reverse),
            )
            common = witnesses[0]
            for witness in witnesses[1:]:
                common = common.intersect(witness)
            sentinel_left = Interval.from_kernel(
                raw_kernel._direct_kappa(
                    potentials[left], delta, axis_diffusion, distance, SENTINEL_BITS
                )
            )
            if not direct_left.contains(sentinel_left) or not common.overlaps(sentinel_left):
                raise ExploratoryReceiptError(f"{coordinate}: common-kappa sentinel escaped")
            total_sentinel_checks += 1
            edges.append(
                RawEdge(
                    left=left,
                    right=right,
                    q_forward=q_forward,
                    q_reverse=q_reverse,
                    kappa=common,
                    direct_left=direct_left,
                )
            )

        physical: list[Interval] = []
        coefficient = (
            stiffness / particle_diffusion
            if coordinate == "midpoint"
            else stiffness / (4 * particle_diffusion)
        )
        centre = mean if coordinate == "midpoint" else Fraction(0)
        for cell, volume in zip(segments, volumes, strict=True):
            if coordinate == "relative_perpendicular":
                primary = Interval.point(volume / width)
                sentinel = primary
            else:
                primary = _sum_intervals(
                    Interval.from_kernel(
                        stationary_kernel._gaussian_mass(
                            lower,
                            upper,
                            coefficient=coefficient,
                            centre=centre,
                            bits=PRIMARY_BITS,
                        )
                    )
                    for lower, upper in cell
                )
                sentinel = _sum_intervals(
                    Interval.from_kernel(
                        stationary_kernel._gaussian_mass(
                            lower,
                            upper,
                            coefficient=coefficient,
                            centre=centre,
                            bits=SENTINEL_BITS,
                        )
                    )
                    for lower, upper in cell
                )
            if not primary.contains(sentinel):
                raise ExploratoryReceiptError(f"{coordinate}: physical-mass sentinel escaped")
            physical.append(primary)
            total_sentinel_checks += 1

        axis = AxisScience(
            coordinate=coordinate,
            periodic=periodic,
            positions=positions,
            volumes=volumes,
            segments=segments,
            raw_mu=tuple(raw_mu_primary),
            physical_mass=tuple(physical),
            edges=tuple(edges),
            raw_sum=_sum_intervals(raw_mu_primary),
            physical_sum=_sum_intervals(physical),
            sentinel_containment_checks=total_sentinel_checks,
        )
        for index, value in enumerate(axis.raw_mu):
            factor_digest.add(["raw_mu", coordinate, index, value.json()])
        for index, value in enumerate(axis.physical_mass):
            factor_digest.add(["physical_mass", coordinate, index, value.json()])
        for index, edge in enumerate(axis.edges):
            factor_digest.add(
                [
                    "edge",
                    coordinate,
                    index,
                    edge.left,
                    edge.right,
                    edge.q_forward.json(),
                    edge.q_reverse.json(),
                    edge.kappa.json(),
                ]
            )
        axes.append(axis)
        guard.check(f"role8/9 {coordinate}")

    return tuple(axes), {
        "factor_record_count": factor_digest.count,
        "factor_sha256": factor_digest.hexdigest(),
        "sentinel_containment_checks": total_sentinel_checks,
        "raw_cell_count": sum(len(axis.raw_mu) for axis in axes),
        "physical_cell_count": sum(len(axis.physical_mass) for axis in axes),
        "axis_edge_count": sum(len(axis.edges) for axis in axes),
        "positive_directed_axis_rate_count": 2 * sum(len(axis.edges) for axis in axes),
        "reflecting_boundary_zero_rate_count": 4,
    }


def _full_contact_mask(relative: Any, transverse: Any, radius: Fraction) -> tuple[bool, ...]:
    radius_squared = radius * radius
    result: list[bool] = []
    for x_segments in relative.cell_segments:
        for y_segments in transverse.cell_segments:
            result.append(
                all(
                    max(
                        x0 * x0 + y0 * y0,
                        x0 * x0 + y1 * y1,
                        x1 * x1 + y0 * y0,
                        x1 * x1 + y1 * y1,
                    )
                    <= radius_squared
                    for x0, x1 in x_segments
                    for y0, y1 in y_segments
                )
            )
    return tuple(result)


def _build_role10(
    config: dict[str, Any],
    primary_payloads: dict[str, Any],
    partitions: dict[str, Any],
    guard: ResourceGuard,
) -> tuple[tuple[tuple[Interval, ...], ...], tuple[Interval, ...], dict[str, Any]]:
    _, _, f0, initial = _kernels()
    row = config["configurations"][0]
    axes = initial._build_control_free_axes(row, config["dynamics"])
    for axis, coordinate in zip(axes, COORDINATES, strict=True):
        positions, volumes, segments = _partition_values(partitions[coordinate])
        if (
            axis.positions != positions
            or axis.cell_volumes != volumes
            or axis.cell_segments != segments
        ):
            raise ExploratoryReceiptError(f"{coordinate}: role10 axis/partition drift")
    source = primary_payloads["killing_geometry"]
    radius = _fraction(source["contact_geometry"]["radius_exact"], "contact radius")
    support = source["support_basis"]
    half_width = _fraction(support["half_width_exact"], "support half width")
    centres = tuple(_fraction(value, "support centre") for value in support["centres_exact"])
    midpoint, relative, transverse = axes
    f0_contact = f0.build_contact_fraction_intervals_v2(
        relative, transverse, radius=radius, precision_bits=ROLE10_BITS
    )
    full_mask = _full_contact_mask(relative, transverse, radius)
    canonical_contact = tuple(
        f0.OutwardInterval(1.0, 1.0) if full else value
        for value, full in zip(f0_contact, full_mask, strict=True)
    )
    profiles = tuple(
        f0.build_normalized_bump_profile(
            midpoint,
            centre=centre,
            half_width=half_width,
            panels_per_unit=PANELS_PER_UNIT,
            precision_bits=ROLE10_BITS,
        )
        for centre in centres
    )
    profile_intervals = tuple(
        tuple(Interval.from_f0(value) for value in profile.density_intervals)
        for profile in profiles
    )
    contact_intervals = tuple(Interval.from_f0(value) for value in canonical_contact)
    digest = RecordDigest("encounter-o113-role10-control-free-factors-v1")
    for index, value in enumerate(contact_intervals):
        digest.add(["contact", index, value.json()])
    for profile_index, values in enumerate(profile_intervals):
        for midpoint_index, value in enumerate(values):
            digest.add(["profile", profile_index, midpoint_index, value.json()])
    guard.check("role10")
    return (
        profile_intervals,
        contact_intervals,
        {
            "factor_record_count": digest.count,
            "factor_sha256": digest.hexdigest(),
            "contact_record_count": len(contact_intervals),
            "active_contact_cell_count": sum(value.upper > 0 for value in contact_intervals),
            "full_contact_cell_count": sum(
                value.lower == value.upper == 1 for value in contact_intervals
            ),
            "profile_record_count": sum(len(values) for values in profile_intervals),
            "profile_count": len(profile_intervals),
            "same_backend_kernel": True,
            "independent_backend": False,
        },
    )


def _enclosure_hull(values: Iterable[Interval]) -> Interval:
    current = tuple(values)
    if not current:
        raise ExploratoryReceiptError("empty interval enclosure hull")
    return Interval(min(value.lower for value in current), max(value.upper for value in current))


def _compose(
    axes: tuple[AxisScience, ...],
    profiles: tuple[tuple[Interval, ...], ...],
    contact: tuple[Interval, ...],
    guard: ResourceGuard,
) -> dict[str, Any]:
    raw_total = _product_intervals(axis.raw_sum for axis in axes)
    physical_total = _product_intervals(axis.physical_sum for axis in axes)
    gauge = physical_total.divide(raw_total)
    gauged_total = gauge.multiply(raw_total)
    rho_axis = tuple(
        tuple(
            physical.divide(raw)
            for physical, raw in zip(axis.physical_mass, axis.raw_mu, strict=True)
        )
        for axis in axes
    )
    rho_hull = _product_intervals(_enclosure_hull(values) for values in rho_axis).divide(gauge)
    if not gauged_total.overlaps(physical_total):
        raise ExploratoryReceiptError("gauged mass enclosure misses physical box mass")

    width = Fraction(1)
    basis: list[dict[str, Any]] = []
    quarter = Fraction(1, 4)
    bary_profile = tuple(
        _sum_intervals(profile[index].scale(quarter) for profile in profiles)
        for index in range(113)
    )
    profile_sets: list[tuple[Interval, ...]] = [*profiles, bary_profile]
    labels = ["basis_0", "basis_1", "basis_2", "basis_3", "barycentre_1_4_each"]
    basis_digest = RecordDigest("encounter-o113-v-k-factor-summaries-v1")
    for label, profile in zip(labels, profile_sets, strict=True):
        v_longitudinal = tuple(value.scale(1 / width) for value in profile)
        v_hull = _enclosure_hull(v_longitudinal).multiply(_enclosure_hull(contact))
        k_longitudinal = tuple(
            value.divide(rho) for value, rho in zip(v_longitudinal, rho_axis[0], strict=True)
        )
        k_relative: list[Interval] = []
        for r_index in range(113):
            for y_index in range(113):
                denominator = rho_axis[1][r_index].multiply(rho_axis[2][y_index])
                k_relative.append(contact[r_index * 113 + y_index].divide(denominator))
        k_hull = gauge.multiply(_enclosure_hull(k_longitudinal)).multiply(
            _enclosure_hull(k_relative)
        )
        record = {
            "label": label,
            "V_interval_enclosure_hull": v_hull.json(),
            "K_interval_enclosure_hull": k_hull.json(),
            "hull_endpoints_are_not_claimed_attained_extrema": True,
            "nonnegative": v_hull.lower >= 0 and k_hull.lower >= 0,
            "virtual_value_count": math.prod(SHAPE),
        }
        basis.append(record)
        basis_digest.add(record)

    conductance_factor_digest = RecordDigest("encounter-o113-tensor-conductance-factors-v1")
    for dimension, axis in enumerate(axes):
        spectators = [item for index, item in enumerate(axes) if index != dimension]
        conductance_factor_digest.add(
            [
                dimension,
                axis.coordinate,
                gauge.json(),
                [edge.kappa.json() for edge in axis.edges],
                [[value.json() for value in spectator.raw_mu] for spectator in spectators],
            ]
        )
    guard.check("composition")
    return {
        "raw_axis_sum_product_interval": raw_total.json(),
        "physical_box_mass_interval": physical_total.json(),
        "global_gauge_interval": gauge.json(),
        "gauged_mass_sum_interval": gauged_total.json(),
        "gauged_mass_overlaps_physical_box_mass": gauged_total.overlaps(physical_total),
        "rho_interval_enclosure_hull": rho_hull.json(),
        "rho_axis_factor_enclosure_hulls": [
            {"coordinate": axis.coordinate, "interval": _enclosure_hull(values).json()}
            for axis, values in zip(axes, rho_axis, strict=True)
        ],
        "conductance_factor_record_count": conductance_factor_digest.count,
        "conductance_factor_sha256": conductance_factor_digest.hexdigest(),
        "control_free_basis_and_barycentre": basis,
        "basis_summary_sha256": basis_digest.hexdigest(),
        "barycentre_contract": {
            "weights_exact": ["1/4", "1/4", "1/4", "1/4"],
            "predeclared_not_result_selected": True,
            "numerical_exploratory_witness_only": True,
            "actual_exploratory_control_values_present": True,
            "source_control_authority_contains_these_values": False,
            "concrete_production_control": False,
            "budget_used": False,
        },
    }


def stream_tensor_topology(
    shape: Sequence[int] = SHAPE,
    *,
    include_periodic_seam: bool = True,
    require_periodic_seam: bool = True,
) -> dict[str, Any]:
    if tuple(shape) != tuple(int(value) for value in shape) or len(shape) != 3:
        raise ExploratoryReceiptError("invalid topology shape")
    n_m, n_r, n_y = (int(value) for value in shape)
    if min(n_m, n_r, n_y) < 2:
        raise ExploratoryReceiptError("topology dimensions are too small")
    state_digest = hashlib.sha256(b"encounter-o113-state-order-v1\0")
    degree_histogram: dict[int, int] = {}
    state_count = 0
    state_buffer = bytearray()
    for m in range(n_m):
        for r in range(n_r):
            for y in range(n_y):
                degree = 1 if m in {0, n_m - 1} else 2
                degree += 1 if r in {0, n_r - 1} else 2
                degree += 2
                degree_histogram[degree] = degree_histogram.get(degree, 0) + 1
                state_buffer.extend(struct.pack(">III", m, r, y))
                state_count += 1
                if len(state_buffer) >= 1 << 20:
                    state_digest.update(state_buffer)
                    state_buffer.clear()
    state_digest.update(state_buffer)

    edge_digest = hashlib.sha256(b"encounter-o113-undirected-edge-order-v1\0")
    edge_buffer = bytearray()
    edge_count = 0

    def add_edge(dimension: int, left: int, right: int) -> None:
        nonlocal edge_count
        edge_buffer.extend(struct.pack(">BQQ", dimension, left, right))
        edge_count += 1
        if len(edge_buffer) >= 1 << 20:
            edge_digest.update(edge_buffer)
            edge_buffer.clear()

    def flat(m: int, r: int, y: int) -> int:
        return (m * n_r + r) * n_y + y

    for m in range(n_m - 1):
        for r in range(n_r):
            for y in range(n_y):
                add_edge(0, flat(m, r, y), flat(m + 1, r, y))
    for m in range(n_m):
        for r in range(n_r - 1):
            for y in range(n_y):
                add_edge(1, flat(m, r, y), flat(m, r + 1, y))
    periodic_edge_stop = n_y if include_periodic_seam else n_y - 1
    for m in range(n_m):
        for r in range(n_r):
            for y in range(periodic_edge_stop):
                add_edge(2, flat(m, r, y), flat(m, r, (y + 1) % n_y))
    edge_digest.update(edge_buffer)
    expected = ((n_m - 1) * n_r * n_y) + (n_m * (n_r - 1) * n_y) + (n_m * n_r * n_y)
    if require_periodic_seam and edge_count != expected:
        raise ExploratoryReceiptError("periodic seam omission changed tensor edge count")
    return {
        "state_count": state_count,
        "state_order_sha256": state_digest.hexdigest(),
        "undirected_edge_count": edge_count,
        "directed_off_diagonal_count": 2 * edge_count,
        "logical_Q_entry_count_with_diagonal": state_count + 2 * edge_count,
        "edge_order_sha256": edge_digest.hexdigest(),
        "degree_histogram": {str(key): value for key, value in sorted(degree_histogram.items())},
        "periodic_seam_included_once_per_midpoint_relative_pair": include_periodic_seam,
        "row_diagonal_definition": "q_xx=-sum_off_diagonal_q_x_to_xprime",
        "row_sum_zero_by_exact_definition": True,
        "graph_connected_by_cartesian_product_of_two_paths_and_one_cycle": True,
        "topology_only_no_rates_conductances_or_diagonals_streamed": True,
        "topology_acceptance_promoted": False,
    }


def _read_be64_intervals(path: Path) -> tuple[Interval, ...]:
    raw = path.read_bytes()
    if len(raw) % 16:
        raise ExploratoryReceiptError(f"invalid >dd file length: {path}")
    return tuple(
        Interval(Fraction.from_float(lower), Fraction.from_float(upper))
        for lower, upper in struct.iter_unpack(">dd", raw)
    )


def _regression_cross_checks(
    axes: tuple[AxisScience, ...],
    composition: dict[str, Any],
    profiles: tuple[tuple[Interval, ...], ...],
    contact: tuple[Interval, ...],
) -> dict[str, Any]:
    """Compare only after new outputs exist; these oracles are not independent inputs."""

    raw_oracle, raw_bytes = _read_json(RAW_ORACLE_PATH)
    stationary_oracle, stationary_bytes = _read_json(STATIONARY_ORACLE_PATH)
    if _sha256(raw_bytes) != ORACLE_SHA256["raw"]:
        raise ExploratoryReceiptError("raw oracle SHA-256 currentness failure")
    if _sha256(stationary_bytes) != ORACLE_SHA256["stationary"]:
        raise ExploratoryReceiptError("stationary oracle SHA-256 currentness failure")
    raw_row = raw_oracle["rows"][0]
    stationary_row = stationary_oracle["rows"][0]
    checks: dict[str, bool] = {
        "raw_row_label": raw_row.get("configuration_label") == ROW_LABEL,
        "raw_member_digest": raw_row.get("member_digest_sha256")
        == "fa2b5008aaa8ec4a636f8797cf29174e9512e25cc5719a9b026ab748a6f91b80",
        "raw_tensor_state_count": raw_row.get("tensor_state_count") == math.prod(SHAPE),
        "stationary_row_label": stationary_row.get("configuration_label") == ROW_LABEL,
    }
    raw_pin_checks = 0
    raw_pin_total = 0
    for axis, raw_axis, stationary_axis in zip(
        axes, raw_row["axes"], stationary_row["axes"], strict=True
    ):
        checks[f"{axis.coordinate}_raw_coordinate"] = raw_axis.get("coordinate") == axis.coordinate
        checks[f"{axis.coordinate}_raw_cell_count"] = raw_axis.get("cell_count") == len(axis.raw_mu)
        checks[f"{axis.coordinate}_raw_edge_count"] = raw_axis.get("edge_count") == len(axis.edges)
        checks[f"{axis.coordinate}_stationary_cell_count"] = stationary_axis.get(
            "cell_count"
        ) == len(axis.physical_mass)
        for generated, oracle in zip(axis.raw_mu, raw_axis["cell_records"], strict=True):
            if not generated.overlaps(
                _interval_from_json(oracle["formula_ungauged_mu_interval"], "oracle raw mu")
            ):
                raise ExploratoryReceiptError(f"{axis.coordinate}: raw oracle disagreement")
        for generated, oracle in zip(axis.edges, raw_axis["edge_records"], strict=True):
            if not generated.direct_left.overlaps(
                _interval_from_json(oracle["common_kappa_formula_interval"], "oracle common kappa")
            ):
                raise ExploratoryReceiptError(f"{axis.coordinate}: kappa oracle disagreement")
        for generated, oracle in zip(
            axis.physical_mass,
            stationary_axis["cell_mass_intervals"],
            strict=True,
        ):
            if not generated.overlaps(_interval_from_json(oracle, "oracle physical mass")):
                raise ExploratoryReceiptError(f"{axis.coordinate}: stationary oracle disagreement")
        for raw_file in raw_axis.get("raw_files", {}).values():
            file_entry = raw_file.get("file", raw_file)
            if type(file_entry) is not dict or "path" not in file_entry:
                continue
            raw_pin_total += 1
            path = (
                REPORT_ROOT
                / "artifacts/data/physical_production_initial_stream_v1"
                / file_entry["path"]
            )
            if path.is_file() and _file_sha256(path) == file_entry.get("sha256"):
                raw_pin_checks += 1

    generated_gauge = _interval_from_json(composition["global_gauge_interval"], "generated gauge")
    oracle_gauge = _interval_from_json(raw_row["global_gauge_interval"], "oracle gauge")
    generated_rho = _interval_from_json(
        composition["rho_interval_enclosure_hull"], "generated rho hull"
    )
    oracle_rho = _interval_from_json(raw_row["rho_range_interval"], "oracle rho")
    checks["global_gauge_oracle_overlap"] = generated_gauge.overlaps(oracle_gauge)
    checks["rho_enclosure_hull_oracle_overlap"] = generated_rho.overlaps(oracle_rho)
    checks["raw_file_pins_all_match"] = raw_pin_total > 0 and raw_pin_checks == raw_pin_total

    role10_row_path = REPORT_ROOT / ROLE10_ROOT / "rows/00_o113_base/row.json"
    if _file_sha256(role10_row_path) != ORACLE_SHA256["role10_row"]:
        raise ExploratoryReceiptError("role10 row oracle SHA-256 currentness failure")
    role10_row = json.loads(role10_row_path.read_bytes())
    saved_contact = _read_be64_intervals(
        REPORT_ROOT / ROLE10_ROOT / role10_row["contact_fraction_relative"]["file"]["path"]
    )
    saved_profiles = tuple(
        _read_be64_intervals(REPORT_ROOT / ROLE10_ROOT / item["file"]["path"])
        for item in role10_row["support_densities"]
    )
    checks["role10_contact_exact_replay"] = saved_contact == contact
    checks["role10_profiles_exact_replay"] = saved_profiles == profiles
    checks["role10_row_label"] = role10_row.get("configuration_label") == ROW_LABEL
    checks["role10_same_backend_only"] = (
        role10_row.get("flags", {}).get("same_core_producer_consistency_only") is True
        and role10_row.get("flags", {}).get("independent_killing_geometry_replay") is False
    )
    return {
        "role": "post_computation_regression_only_not_scientific_input",
        "independent_oracle_claimed": False,
        "same_backend_outputs_used": True,
        "raw_oracle": {
            "path": RAW_ORACLE_PATH.as_posix(),
            "sha256": _sha256(raw_bytes),
            "literal_current_sha256_pin_checked": True,
            "member_digest_sha256": raw_row.get("member_digest_sha256"),
            "raw_file_pin_checks": raw_pin_checks,
            "raw_file_pin_total": raw_pin_total,
        },
        "stationary_oracle": {
            "path": STATIONARY_ORACLE_PATH.as_posix(),
            "sha256": _sha256(stationary_bytes),
            "literal_current_sha256_pin_checked": True,
        },
        "role10_oracle": {
            "path": role10_row_path.relative_to(REPORT_ROOT).as_posix(),
            "sha256": _file_sha256(role10_row_path),
            "literal_current_sha256_pin_checked": True,
        },
        "checks": checks,
        "all_passed": all(checks.values()),
    }


def build_receipt(*, include_regression_cross_checks: bool = True) -> dict[str, Any]:
    guard = ResourceGuard.start()
    config, partitions, inputs = _validate_sources()
    guard.check("inputs")
    axes, primitive_summary = _build_role8_role9(config, partitions, guard)
    profiles, contact, role10_summary = _build_role10(config, inputs["payloads"], partitions, guard)
    composition = _compose(axes, profiles, contact, guard)
    formal = build_formal_lane()
    if not formal["all_identities_passed"] or not all(formal["mutation_sentinels"].values()):
        raise ExploratoryReceiptError("formal lane failed")
    topology = stream_tensor_topology()
    guard.check("topology stream")
    regression = (
        _regression_cross_checks(axes, composition, profiles, contact)
        if include_regression_cross_checks
        else {
            "role": "disabled_by_explicit_test_only_option",
            "independent_oracle_claimed": False,
            "all_passed": None,
        }
    )
    if include_regression_cross_checks and not regression["all_passed"]:
        failed = [key for key, value in regression["checks"].items() if not value]
        raise ExploratoryReceiptError(f"regression cross-checks failed: {failed}")
    guard.check("regression cross-check")

    science_gates = {
        "three_primitive_roles_recomputed_before_composition": True,
        "raw_formula_primary_contains_same_backend_sentinels": True,
        "physical_mass_primary_contains_same_backend_sentinels": True,
        "common_flux_four_witness_intersections_nonempty": True,
        "global_gauge_is_one_scalar": True,
        "gauged_mass_and_physical_box_mass_enclosures_overlap": composition[
            "gauged_mass_overlaps_physical_box_mass"
        ],
        "rho_strictly_positive": _interval_from_json(
            composition["rho_interval_enclosure_hull"], "rho enclosure hull"
        ).lower
        > 0,
        "control_free_contact_profile_factors_nonnegative": True,
        "formal_identity_lane_passed": formal["all_identities_passed"],
        "full_state_and_edge_topology_orders_streamed": (
            topology["state_count"] == math.prod(SHAPE)
            and topology["undirected_edge_count"] == 4_303_153
        ),
    }
    if not all(science_gates.values()):
        raise ExploratoryReceiptError("science gate failed")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "configuration_index": 0,
            "configuration_label": ROW_LABEL,
            "refinement_level": 0,
            "shape": list(SHAPE),
            "ordinary_single_python_process": True,
            "factorized_no_dense_tensor": True,
        },
        "claims": {
            "exploratory_same_process_formula_composition_completed": True,
            "actual_exploratory_control_values_present": True,
            "exploratory_barycentre_control_witness_present": True,
            "one_exact_irrational_member_selected_from_interval_boxes": False,
            "correlated_production_member": False,
            "production_same_member_accepted": False,
            "external_predecessor_commitment_present": False,
            "candidate_native_roles_8_10_production_replay": False,
            "backend_independence_claimed": False,
            "control_weights_in_source_primitives": False,
            "concrete_production_control": False,
            "budget_used": False,
            "concrete_killing_diagonal_materialized": False,
            "full_numerical_operator_replayed": False,
            "cellwise_killing_identity_numerically_replayed": False,
            "propagation_executed": False,
            "topology_acceptance_promoted": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "F0_complete": False,
            "F1_complete": False,
            "release_eligible": False,
            "submission_eligible": False,
        },
        "source_inputs": inputs["sources"],
        "method": {
            "role8_primary_bits": PRIMARY_BITS,
            "role8_same_backend_sentinel_bits": SENTINEL_BITS,
            "role9_primary_bits": PRIMARY_BITS,
            "role9_same_backend_sentinel_bits": SENTINEL_BITS,
            "role10_primary_bits": ROLE10_BITS,
            "role10_panels_per_unit": PANELS_PER_UNIT,
            "interval_endpoint_selection": "none",
            "formal_and_outward_lanes_separate": True,
            "all_primary_and_oracle_literal_sha256_pins_checked": True,
            "cross_source_semantic_joins_checked": True,
            "imported_scientific_kernel_source_hashes_checked": True,
        },
        "semantic_source_joins": inputs["semantic_joins"],
        "formal_lane": formal,
        "outward_interval_lane": {
            "primitive_summary": primitive_summary,
            "role10_summary": role10_summary,
            "composition": composition,
        },
        "streamed_tensor": topology,
        "science_gates": science_gates,
        "all_science_gates_passed": all(science_gates.values()),
        "non_authoritative_regression_cross_checks": regression,
        "resource_contract": {
            "maximum_wall_seconds": MAX_WALL_SECONDS,
            "maximum_peak_rss_bytes": MAX_RSS_BYTES,
            "maximum_output_bytes": MAX_OUTPUT_BYTES,
            "network_used": False,
            "output_must_be_outside_report_tree": True,
        },
    }


def _output_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise ExploratoryReceiptError("--output must be an absolute temporary path")
    resolved_parent = path.parent.resolve()
    report = REPORT_ROOT.resolve()
    if resolved_parent == report or report in resolved_parent.parents:
        raise ExploratoryReceiptError("persistent output inside the report tree is forbidden")
    if path.exists():
        raise ExploratoryReceiptError("output already exists")
    return path


def write_receipt(path: Path, receipt: dict[str, Any]) -> tuple[str, int]:
    raw = _canonical_bytes(receipt) + b"\n"
    if len(raw) > MAX_OUTPUT_BYTES:
        raise ExploratoryReceiptError("receipt exceeds output cap")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("xb") as target:
        target.write(raw)
    return _sha256(raw), len(raw)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        output = _output_path(args.output)
        receipt = build_receipt()
        digest, byte_length = write_receipt(output, receipt)
        observation = {
            "status": STATUS,
            "output": str(output),
            "receipt_sha256": digest,
            "receipt_byte_length": byte_length,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "peak_rss_bytes": _peak_rss_bytes(),
        }
        print(json.dumps(observation, sort_keys=True, separators=(",", ":")))
        return 0
    except (ExploratoryReceiptError, OSError, ValueError) as error:
        print(
            json.dumps(
                {
                    "status": "HOLD_EXPLORATORY_O113_RECEIPT",
                    "error": str(error),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
