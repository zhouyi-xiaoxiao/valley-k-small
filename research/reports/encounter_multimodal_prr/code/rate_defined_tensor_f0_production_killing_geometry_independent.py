"""Separate-source verifier for the frozen control-free killing-geometry bundle.

This module treats the candidate bundle and the accepted partition bundle as
untrusted data.  It owns its schemas, exact partition reconstruction, directed
MPFR arithmetic, disk/contact oracle, compact-bump Simpson oracle, relation
digests, and deterministic semantic receipt.  It deliberately does not import
any producer, F0, or production-initial-stream implementation.

The result is same-backend containment evidence only.  No budget, control,
concrete killing array, full operator, propagation, topology, F0, or F1 object
is constructed here.
"""

from __future__ import annotations

import ast
import gc
import hashlib
import hmac
import json
import math
import os
import re
import resource
import stat
import struct
import sys
import time
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Final, Sequence

import gmpy2

PASS_STATUS: Final = (
    "PASS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_SAME_BACKEND_"
    "CONTAINMENT_CHILD_ONLY_NOT_CLEAN_REPLAY_NOT_CONCRETE_KILLING_"
    "NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
OUTER_PASS_STATUS: Final = (
    "PASS_TWO_REPEAT_CLEAN_PROCESS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_"
    "SAME_BACKEND_CONTAINMENT_ONLY_NOT_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
HOLD_API: Final = "HOLD_KILLING_GEOMETRY_VERIFY_API"
HOLD_SOURCE: Final = "HOLD_KILLING_GEOMETRY_VERIFY_SOURCE"
HOLD_IMPORT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_IMPORT_BOUNDARY"
HOLD_TREE: Final = "HOLD_KILLING_GEOMETRY_VERIFY_TREE"
HOLD_MANIFEST: Final = "HOLD_KILLING_GEOMETRY_VERIFY_MANIFEST"
HOLD_PARTITION: Final = "HOLD_KILLING_GEOMETRY_VERIFY_PARTITION"
HOLD_CONTACT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CONTACT_ORACLE"
HOLD_SUPPORT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_SUPPORT_ORACLE"
HOLD_CONTAINMENT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CONTAINMENT"
HOLD_WIDTH: Final = "HOLD_KILLING_GEOMETRY_VERIFY_WIDTH"
HOLD_NORMALIZATION: Final = "HOLD_KILLING_GEOMETRY_VERIFY_NORMALIZATION"
HOLD_REPEAT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_REPEAT"
HOLD_TIMEOUT: Final = "HOLD_KILLING_GEOMETRY_VERIFY_TIMEOUT"
HOLD_CLEANUP: Final = "HOLD_KILLING_GEOMETRY_VERIFY_CLEANUP"

AUTHORITY_SHA256: Final = "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
PARTITION_BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
PARTITION_TREE_SHA256: Final = "4541bf03d895ddd167b1e19a226747b3bdab3f987e134a80403c4b675a67129f"
PRODUCER_SHA256: Final = "2cada45143914edf1142daf6a5b7a8b5367757c664855dd6d836e7f43935dd9b"
PRODUCER_TEST_SHA256: Final = "887a19536e2f81d4c99dda198cb4f7d488c9ccfff52673c843cec47bf8a2852c"
CANDIDATE_BUNDLE_SHA256: Final = "f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684"
CANDIDATE_TREE_SHA256: Final = "b05dd83f3756528c0fd09f78f3a79eb4b1894e2bb423e45e1af55f6cce928568"
PARTITION_REFERENCE_GRAPH_SHA256: Final = (
    "ce259a13975f43b7eeec4f468b0fe1ed92d1d4b9b60ac9b93ebb0f4418c3267e"
)
FAMILY_RELATION_SHA256: Final = "3f2bf086ffac6d30b65ab0c0be866432756d3581979b8a3372bf8c7891bbf1c8"
DESIGN_SHA256: Final = "f6c810ca77251b6f1c1683a8c85d2eb015bacb0fedcd0fe7ffb3174341e106f2"
OPERATION_MODEL_SHA256: Final = "53f709139c380e9512740a6fdabcd7570c1822650817915454ddbd7d7395feb0"
FACTORIZATION_CONTRACT_SHA256: Final = (
    "de42fefbfc163fdcffd573d49d1156d761341c78b3756903755579dc8e9b23af"
)
F0_CORE_SHA256: Final = "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
INITIAL_STREAM_SOURCE_SHA256: Final = (
    "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb"
)

AUTHORITY_PATH: Final = Path("artifacts/data/physical_killing_geometry_source_v1.json")
CONFIGURATION_PATH: Final = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
PARTITION_BUNDLE_PATH: Final = Path(
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)
PARTITION_ROOT_PATH: Final = PARTITION_BUNDLE_PATH.parent
PRODUCER_PATH: Final = Path("code/rate_defined_tensor_f0_production_killing_geometry.py")
PRODUCER_TEST_PATH: Final = Path("code/test_rate_defined_tensor_f0_production_killing_geometry.py")
F0_CORE_PATH: Final = Path("code/rate_defined_tensor_f0.py")
INITIAL_STREAM_SOURCE_PATH: Final = Path("code/rate_defined_tensor_f0_production_initial_stream.py")
DESIGN_PATH: Final = Path("notes/f0_production_killing_geometry_independent_verifier_design.md")
OPERATION_MODEL_PATH: Final = Path(
    "code/rate_defined_tensor_f0_production_killing_geometry_independent_operation_model_v2.json"
)

CONFIGURATION_COUNT: Final = 12
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
EXPECTED_LABELS: Final = (
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
PRIMARY_BITS: Final = 384
SENTINEL_BITS: Final = 512
CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH: Final = Fraction(1, 1 << 40)
SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH: Final = Fraction(1, 1 << 40)
CONTACT_ORACLE_MAX_WIDTH: Final = Fraction(1, 1 << 180)
ORACLE_TO_CANDIDATE_WIDTH_RATIO_MAX: Final = Fraction(1, 8)
SUPPORT_AGGREGATE_WIDTH_CAP: Final = Fraction(1, 10_000_000_000)
MAX_TREE_FILES: Final = 256
MAX_TREE_BYTES: Final = 67_108_864
MAX_TREE_DIRECTORIES: Final = 64
MAX_TREE_RELATIVE_DEPTH: Final = 3
MAX_JSON_FILE_BYTES: Final = 2_097_152
MAX_RAW_CONTACT_FILE_BYTES: Final = 553_840
MAX_RAW_SUPPORT_FILE_BYTES: Final = 3_312
MAX_SIMPSON_PANELS: Final = 4_194_304
MAX_SIMPSON_DYADIC_DEPTH: Final = 64
MAX_SIMPSON_DFS_STACK: Final = 65
MAX_BUMP_BREAKPOINTS: Final = 20_000
MAX_DYADIC_COORDINATE_COMPONENT_BITS: Final = 256
MAX_MPFR_TO_MPQ_DENOMINATOR_BITS: Final = 4_096
MAX_SIMPSON_EXACT_COMPONENT_BITS: Final = 8_192
FLAT_TAIL_THRESHOLD: Final = 2_048
PRIMARY_SIMPSON_TARGET_WIDTH: Final = Fraction(1, 1 << 64)
RUN_DEADLINE_SECONDS: Final = 1_140
MAX_RECEIPT_BYTES: Final = 2_097_152
MAX_CHILD_OBSERVATION_BYTES: Final = 65_536
MAX_CHILD_ACK_BYTES: Final = 4_096
EXPECTED_TREE_FILES: Final = 76
EXPECTED_TREE_DIRECTORIES: Final = 14
EXPECTED_PARTITION_TREE_FILES: Final = 207
EXPECTED_PARTITION_TREE_DIRECTORIES: Final = 14
EXPECTED_PARTITION_TREE_BYTES: Final = 1_439_598
EXPECTED_INVENTORY_FILES: Final = 75
EXPECTED_CONTACT_RECORDS: Final = 233_139
EXPECTED_CONTACT_BYTES: Final = 3_730_224
EXPECTED_SUPPORT_RECORDS: Final = 6_852
EXPECTED_SUPPORT_BYTES: Final = 109_632
EXPECTED_RAW_LEAVES: Final = 60

FLAT_TAIL_BUMP_UPPER: Final = Fraction(1, 1 << FLAT_TAIL_THRESHOLD)
FLAT_TAIL_M4_UPPER: Final = Fraction(
    sum(
        coefficient * FLAT_TAIL_THRESHOLD**power
        for power, coefficient in (
            (3, 24),
            (4, 300),
            (5, 672),
            (6, 624),
            (7, 192),
            (8, 16),
        )
    ),
    1 << FLAT_TAIL_THRESHOLD,
)
FLAT_TAIL_POLICY: Final = {
    "bump_upper_exact": f"1/{1 << FLAT_TAIL_THRESHOLD}",
    "derivative_coefficients": [[3, 24], [4, 300], [5, 672], [6, 624], [7, 192], [8, 16]],
    "derivative_upper_exact": (f"{FLAT_TAIL_M4_UPPER.numerator}/{FLAT_TAIL_M4_UPPER.denominator}"),
    "elementary_bound": "exp(-s)<2^-s_for_s_positive_because_e>2",
    "schema": "encounter_independent_compact_bump_flat_tail_policy_v1",
    "threshold_exact": f"{FLAT_TAIL_THRESHOLD}/1",
}
FLAT_TAIL_POLICY_SHA256: Final = "b7720e13964c58cb14a6f1ca9aa4060a45b0cfaf8108587a62333dcf14933f9a"
FLAT_TAIL_BUMP_UPPER_SHA256: Final = (
    "209e99ef1b9622813aaec0eb98c40dca8c5c31b34d26eb002931a93c92d30c23"
)
FLAT_TAIL_M4_UPPER_SHA256: Final = (
    "6c7dbadf0085bd6977a06e6fd3308955808e69a71e7eead3a712dbbf4551538a"
)

PAIRED_SIMPSON_POLICY: Final = {
    "accepted_panel_rule": "exact_panel_enclosure_width_le_root_target_width_over_2^depth",
    "accumulation": "per_segment_exact_balanced_binary_bins",
    "dyadic_depth_cap": MAX_SIMPSON_DYADIC_DEPTH,
    "coordinate_component_bit_cap": MAX_DYADIC_COORDINATE_COMPONENT_BITS,
    "exact_component_bit_cap": MAX_SIMPSON_EXACT_COMPONENT_BITS,
    "execution_model": "single_threaded_child",
    "flat_tail_threshold": FLAT_TAIL_THRESHOLD,
    "maximum_stack_nodes": MAX_SIMPSON_DFS_STACK,
    "mpfr_to_mpq_denominator_bit_cap": MAX_MPFR_TO_MPQ_DENOMINATOR_BITS,
    "panel_cap": MAX_SIMPSON_PANELS,
    "primary_target_width_exact": f"1/{1 << 64}",
    "remainder_prefilter": "split_without_estimate_when_exact_root_local_R_exceeds_allowance",
    "root_derivative_rule": "one_rigorous_M4_upper_per_frozen_root_and_precision",
    "sample_rule": "paired_384_512_samples_with_parent_endpoint_and_midpoint_reuse",
    "schema": "encounter_independent_paired_root_local_simpson_policy_v2",
    "sentinel_rule": "512_bit_containment_only_on_primary_accepted_leaves_not_2^-68_adaptive",
    "traversal": "per_root_explicit_DFS_push_right_then_left_execute_left_first",
}
PAIRED_SIMPSON_POLICY_SHA256: Final = (
    "0fb7e19ff04a60c0ebee938fc725fe49ba5c030bb3a18f2570bbabb519a25895"
)
EXPECTED_ACCEPTED_LEAF_PARTITION_SHA256: Final = (
    "5899c7ba287a274717d2460479f92a9a9f00cb2d6af273d79f5f1be257b4275b"
)

BUNDLE_SCHEMA: Final = "encounter_control_free_production_killing_geometry_v1"
ROW_SCHEMA: Final = "encounter_control_free_production_killing_geometry_row_v1"
RAW_SCHEMA: Final = "encounter_big_endian_binary64_interval_file_v1"
AUTHORITY_SCHEMA: Final = "encounter_physical_killing_geometry_source_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
PARTITION_ROW_SCHEMA: Final = "encounter_control_free_production_initial_row_v1"
BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_KILLING_GEOMETRY_PRODUCER_CONSISTENCY_ONLY_"
    "NOT_INDEPENDENT_NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
ROW_STATUS: Final = (
    "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0"
)

_FORBIDDEN_IMPORTS: Final = {
    "rate_defined_tensor_f0",
    "rate_defined_tensor_f0_production_initial_stream",
    "rate_defined_tensor_f0_production_killing_geometry",
}
_SHA_RE: Final = re.compile(r"[0-9a-f]{64}\Z")
_HEX_RE: Final = re.compile(
    r"(?P<sign>-?)(?P<int>0x[0-9a-f])\.(?P<frac>[0-9a-f]{13})p(?P<exp>[+-][0-9]+)\Z"
)
_LAUNCH_NONCE_RE: Final = re.compile(r"[0-9a-f]{64}\Z")

CHILD_SEMANTIC_SUCCESS_SCHEMA: Final = (
    "encounter_killing_geometry_separate_source_child_semantic_receipt_v2"
)
CHILD_SEMANTIC_HOLD_SCHEMA: Final = "encounter_killing_geometry_separate_source_hold_v1"
CHILD_OBSERVATION_SCHEMA: Final = "encounter_killing_geometry_child_observation_v1"
CHILD_BOUND_ACK_SCHEMA: Final = "encounter_killing_geometry_child_ack_v1"
CHILD_UNBOUND_HOLD_ACK_SCHEMA: Final = "encounter_killing_geometry_child_unbound_hold_ack_v1"

_HOLD_STATUSES: Final = (
    HOLD_API,
    HOLD_SOURCE,
    HOLD_IMPORT,
    HOLD_TREE,
    HOLD_MANIFEST,
    HOLD_PARTITION,
    HOLD_CONTACT,
    HOLD_SUPPORT,
    HOLD_CONTAINMENT,
    HOLD_WIDTH,
    HOLD_NORMALIZATION,
    HOLD_REPEAT,
    HOLD_TIMEOUT,
    HOLD_CLEANUP,
)
_CHILD_SEMANTIC_SUCCESS_KEYS: Final = {
    "candidate",
    "contact_summary",
    "flags",
    "frozen_sources",
    "independent_partition_semantic_sha256s",
    "precision_bits",
    "runtime",
    "schema",
    "status",
    "support_policy_digests",
    "support_summary",
    "verifier_staged_file_sha256_at_receipt",
}
_CHILD_OBSERVATION_KEYS: Final = {
    "elapsed_monotonic_ns",
    "launch_nonce",
    "peak_rss_bytes",
    "pgid",
    "pid",
    "ppid",
    "run_index",
    "schema",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "status",
    "verifier_staged_file_sha256_at_observation",
}
_CHILD_BOUND_ACK_KEYS: Final = {
    "launch_nonce",
    "observation_byte_length",
    "observation_sha256",
    "run_index",
    "schema",
    "semantic_receipt_byte_length",
    "semantic_receipt_sha256",
    "status",
}

_FILE_KEYS: Final = {"byte_length", "path", "sha256"}
_RAW_KEYS: Final = {
    "byte_order",
    "logical_shape",
    "raw_byte_length",
    "raw_sha256",
    "record_count",
    "record_format",
    "role",
    "schema",
}
_BUNDLE_KEYS: Final = {
    "configuration_count",
    "factorization_contract",
    "factorization_contract_sha256",
    "family_relation_sha256",
    "file_inventory",
    "flags",
    "method",
    "partition_reference_graph_sha256",
    "request_snapshots",
    "rows",
    "schema",
    "source_pins",
    "status",
    "totals",
}
_SUMMARY_KEYS: Final = {
    "active_contact_cell_count",
    "configuration_index",
    "configuration_label",
    "contact_fraction_records",
    "expected_states",
    "full_contact_cell_count",
    "midpoint_cells",
    "row_manifest",
    "row_relation_sha256",
    "shape",
    "support_density_records",
    "support_profile_count",
}
_ROW_KEYS: Final = {
    "configuration_index",
    "configuration_label",
    "contact_fraction_relative",
    "expected_states",
    "factorization_contract_sha256",
    "flags",
    "gates",
    "partition_source",
    "row_relation_sha256",
    "schema",
    "shape",
    "source_pins",
    "status",
    "support_densities",
}
_CONTACT_KEYS: Final = {
    "active_cell_count",
    "area_enclosure_exact",
    "file",
    "full_cell_count",
    "manifest",
    "quality_ledger",
    "relation_sha256",
}
_SUPPORT_KEYS: Final = {
    "centre_binary64_hex",
    "centre_exact",
    "file",
    "half_width_binary64_hex",
    "half_width_exact",
    "integral_enclosure_exact",
    "manifest",
    "profile_index",
    "quality_ledger",
    "relation_sha256",
}
_PARTITION_SOURCE_KEYS: Final = {
    "bundle_manifest_sha256",
    "bundle_row_manifest",
    "bundle_row_relation_sha256",
    "partitions",
}
_PARTITION_BINDING_KEYS: Final = {"axis_relation_sha256", "coordinate", "file"}
_PARTITION_KEYS: Final = {
    "cell_segments_exact",
    "cell_volumes_exact",
    "construction",
    "coordinate",
    "domain_start_exact",
    "domain_width_exact",
    "periodic",
    "periodic_shift_exact",
    "positions_exact",
    "schema",
    "size",
}
_CONFIGURATION_KEYS: Final = {
    "authority",
    "authorizes_scientific_execution",
    "axis_construction_contracts",
    "configuration_count",
    "configuration_order",
    "configurations",
    "contains_budget_value",
    "contains_control_values",
    "coordinate_order",
    "dynamics",
    "initial_geometry",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "scope",
    "status",
    "total_state_workload",
    "workload_semantics",
}
_CONFIGURATION_ROW_KEYS: Final = {
    "expected_states",
    "label",
    "midpoint",
    "purpose",
    "relative_parallel",
    "relative_perpendicular",
    "shape",
}
_REFLECTING_SPEC_KEYS: Final = {
    "alignment",
    "lower_binary64_hex",
    "size",
    "upper_binary64_hex",
}
_PERIODIC_SPEC_KEYS: Final = {"alignment", "periodic_shift_exact", "size"}
_AUTHORITY_SUPPORT_KEYS: Final = {
    "analytic_integral_each",
    "centres_binary64_hex",
    "centres_exact",
    "density_definition",
    "half_width_binary64_hex",
    "half_width_exact",
    "normalizer_definition",
    "profile_count",
    "shape_definition",
}

_BUNDLE_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "concrete_killing_constructed": False,
    "contact_fraction_geometry_producer_consistent_all_rows": True,
    "contains_budget_value": False,
    "contains_control_values": False,
    "continuum_verified": False,
    "f0_pass": False,
    "full_operator_bound": False,
    "independent_killing_geometry_replay_complete": False,
    "killing_geometry_bound": True,
    "positive_budget_executed": False,
    "producer_consistent_control_free_killing_geometry_all_rows": True,
    "production_resource_gate": False,
    "propagation_executed": False,
    "same_core_producer_consistency_only": True,
    "science_executed": False,
    "single_physical_operator_bound": False,
    "support_density_basis_producer_consistent_all_rows": True,
    "topology_complete": False,
}
_ROW_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "concrete_killing_constructed": False,
    "contact_fraction_geometry_producer_consistent": True,
    "contains_budget_value": False,
    "contains_control_values": False,
    "continuum_verified": False,
    "f0_pass": False,
    "full_operator_bound": False,
    "independent_killing_geometry_replay": False,
    "killing_geometry_bound": True,
    "positive_budget_executed": False,
    "producer_consistent_control_free_killing_geometry": True,
    "production_resource_gate": False,
    "propagation_executed": False,
    "same_core_producer_consistency_only": True,
    "science_executed": False,
    "single_physical_operator_bound": False,
    "support_density_basis_producer_consistent": True,
    "topology_complete": False,
}
_ROW_GATES: Final = {
    "analytic_disk_area_anchor_is_contained_and_quality_capped": True,
    "contact_area_enclosure_is_positive_and_domain_bounded": True,
    "contact_area_overlaps_direct_core_domain_enclosure": True,
    "contact_fraction_intervals_are_canonical_and_in_unit_range": True,
    "geometrically_full_contact_cells_are_exact_unit_intervals": True,
    "partition_bytes_match_same_core_exact_reconstruction": True,
    "support_centres_are_strictly_distinct_and_pairwise_disjoint": True,
    "support_density_intervals_are_canonical_and_nonnegative": True,
    "support_integral_enclosures_contain_analytic_unit_mass": True,
    "support_integral_widths_pass_predeclared_cap": True,
    "support_ranges_are_strictly_inside_midpoint_domain": True,
}
_METHOD: Final = {
    "concrete_killing_materialized": False,
    "contact_active_cell_count_definition": "saved_interval_upper_endpoint_strictly_positive",
    "contact_coordinate_order": ["relative_parallel", "relative_perpendicular"],
    "contact_fraction_record_format": ">dd",
    "contact_full_cell_count_definition": (
        "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
    ),
    "contact_full_cell_serialization": ("exact_[1,1]_after_exact_rational_corner_classification"),
    "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
    "panels_per_unit": 16_384,
    "precision_bits": 192,
    "same_core_numerical_primitives": [
        "build_contact_fraction_intervals_v2",
        "build_normalized_bump_profile",
    ],
    "same_mpfr_backend_anchor_is_independent": False,
    "support_density_record_format": ">dd",
}
_EXPECTED_TOTALS: Final = {
    "active_contact_cell_count": 5_446,
    "contact_fraction_raw_bytes": EXPECTED_CONTACT_BYTES,
    "contact_fraction_records": EXPECTED_CONTACT_RECORDS,
    "full_contact_cell_count": 4_142,
    "midpoint_cells": 1_713,
    "raw_interval_bytes": EXPECTED_CONTACT_BYTES + EXPECTED_SUPPORT_BYTES,
    "raw_interval_records": EXPECTED_CONTACT_RECORDS + EXPECTED_SUPPORT_RECORDS,
    "support_density_raw_bytes": EXPECTED_SUPPORT_BYTES,
    "support_density_records": EXPECTED_SUPPORT_RECORDS,
    "support_profile_count": 48,
}
_CONTACT_QUALITY_KEYS: Final = {
    "aggregate_contains_analytic_enclosure",
    "aggregate_width_exact",
    "aggregate_width_over_radius_squared_cap_exact",
    "aggregate_width_over_radius_squared_exact",
    "analytic_area_enclosure_exact",
    "analytic_area_precision_bits",
    "analytic_width_exact",
    "analytic_width_over_radius_squared_cap_exact",
    "analytic_width_over_radius_squared_exact",
    "backend",
    "independent_backend",
    "separately_directed_formula",
}
_SUPPORT_QUALITY_KEYS: Final = {
    "analytic_mass_exact",
    "integral_width_cap_exact",
    "integral_width_exact",
    "midpoint_domain_lower_exact",
    "midpoint_domain_upper_exact",
    "support_lower_exact",
    "support_strictly_inside_midpoint_domain",
    "support_upper_exact",
}


class IndependentVerificationFailure(RuntimeError):
    """Fail-closed verifier outcome with one bounded stable HOLD code."""

    def __init__(self, code: str, message: str) -> None:
        bounded = message.replace("\n", " ")[:320]
        super().__init__(f"{code}: {bounded}")
        self.code = code


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise IndependentVerificationFailure(HOLD_API, "interval endpoints are not Fractions")
        if self.lower > self.upper:
            raise IndependentVerificationFailure(HOLD_API, "interval is reversed")

    @property
    def width(self) -> Fraction:
        return self.upper - self.lower

    def contains(self, other: "ExactInterval") -> bool:
        return self.lower <= other.lower <= other.upper <= self.upper


@dataclass(frozen=True, slots=True)
class AxisPartition:
    coordinate: str
    construction: str
    domain_start: Fraction
    domain_width: Fraction
    periodic: bool
    periodic_shift: Fraction
    positions: tuple[Fraction, ...]
    volumes: tuple[Fraction, ...]
    segments: tuple[tuple[tuple[Fraction, Fraction], ...], ...]

    @property
    def size(self) -> int:
        return len(self.positions)

    def payload(self) -> dict[str, object]:
        return {
            "cell_segments_exact": [
                [[fraction_text(a), fraction_text(b)] for a, b in cell] for cell in self.segments
            ],
            "cell_volumes_exact": [fraction_text(value) for value in self.volumes],
            "construction": self.construction,
            "coordinate": self.coordinate,
            "domain_start_exact": fraction_text(self.domain_start),
            "domain_width_exact": fraction_text(self.domain_width),
            "periodic": self.periodic,
            "periodic_shift_exact": fraction_text(self.periodic_shift),
            "positions_exact": [fraction_text(value) for value in self.positions],
            "schema": PARTITION_SCHEMA,
            "size": self.size,
        }

    @property
    def semantic_sha256(self) -> str:
        return digest_domain(b"independent-killing-axis-partition-semantics-v1\0", self.payload())


@dataclass(frozen=True, slots=True)
class GeometryAuthority:
    radius: Fraction
    period: Fraction
    centres: tuple[Fraction, Fraction, Fraction, Fraction]
    half_width: Fraction


@dataclass(frozen=True, slots=True)
class TreeSnapshot:
    files: dict[str, dict[str, object]]
    directories: frozenset[str]
    total_bytes: int
    digest: str


@dataclass(frozen=True, slots=True)
class ChildWireArguments:
    report_root: Path
    bundle_root: Path
    semantic_receipt_path: Path
    observation_path: Path
    launch_nonce: str
    run_index: int


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def digest_domain(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise IndependentVerificationFailure(HOLD_API, "digest domain lacks NUL terminator")
    return sha256_bytes(domain + canonical_json_bytes(payload))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise IndependentVerificationFailure(HOLD_MANIFEST, "duplicate or invalid JSON key")
        result[key] = value
    return result


def _reject_float(token: str) -> object:
    raise IndependentVerificationFailure(HOLD_MANIFEST, f"JSON float forbidden: {token[:32]}")


def strict_load_ascii_json(source: bytes, *, label: str) -> object:
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as error:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not UTF-8") from error
    if not text.isascii():
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} contains non-ASCII text")
    try:
        payload = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_float=_reject_float,
            parse_constant=_reject_float,
        )
    except json.JSONDecodeError as error:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is invalid JSON") from error
    if canonical_json_bytes(payload) != source:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not canonical JSON")
    return payload


def exact_json_equal(observed: object, expected: object) -> bool:
    """Compare the verifier's integer-only JSON domain without bool/int aliasing."""
    if type(observed) is not type(expected):
        return False
    if type(observed) is dict:
        observed_dict = observed
        expected_dict = expected
        if set(observed_dict) != set(expected_dict):
            return False
        return all(
            exact_json_equal(observed_dict[key], expected_dict[key]) for key in observed_dict
        )
    if type(observed) is list:
        observed_list = observed
        expected_list = expected
        return len(observed_list) == len(expected_list) and all(
            exact_json_equal(left, right)
            for left, right in zip(observed_list, expected_list, strict=True)
        )
    return type(observed) in {str, int, bool, type(None)} and observed == expected


def require_keys(payload: object, keys: set[str], *, label: str) -> dict[str, object]:
    if type(payload) is not dict or set(payload) != keys:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} key set drifted")
    return payload


def require_sha256(value: object, *, label: str) -> str:
    if type(value) is not str or _SHA_RE.fullmatch(value) is None:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not SHA-256 text")
    return value


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def parse_reduced_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not a fraction")
    numerator_text, denominator_text = value.split("/")
    if not re.fullmatch(r"-?(0|[1-9][0-9]*)", numerator_text) or not re.fullmatch(
        r"[1-9][0-9]*", denominator_text
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} fraction spelling drifted")
    result = Fraction(int(numerator_text), int(denominator_text))
    if fraction_text(result) != value:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} fraction is not reduced")
    return result


def parse_binary64_hex_as_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise IndependentVerificationFailure(
            HOLD_MANIFEST, f"{label} binary64 hex spelling drifted"
        )
    match = _HEX_RE.fullmatch(value)
    if match is None:
        raise IndependentVerificationFailure(
            HOLD_MANIFEST, f"{label} binary64 hex spelling drifted"
        )
    significand = int(match.group("int")[2:] + match.group("frac"), 16)
    if significand == 0:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} zero is not authorized")
    if match.group("sign") == "-":
        significand = -significand
    written_exponent = int(match.group("exp"))
    if not -1022 <= written_exponent <= 1023:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} binary64 exponent escaped")
    exponent = written_exponent - 52
    result = (
        Fraction(significand * (1 << exponent), 1)
        if exponent >= 0
        else Fraction(significand, 1 << -exponent)
    )
    try:
        parsed = float.fromhex(value)
        rerounded = float(result)
    except (OverflowError, ValueError) as error:
        raise IndependentVerificationFailure(
            HOLD_MANIFEST, f"{label} binary64 hex invalid"
        ) from error
    if (
        not math.isfinite(parsed)
        or not math.isfinite(rerounded)
        or parsed == 0.0
        or rerounded == 0.0
        or parsed.hex() != value
        or rerounded.hex() != value
        or Fraction.from_float(parsed) != result
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not canonical binary64")
    return result


def validate_relative_manifest_path(value: object, *, label: str) -> str:
    if (
        type(value) is not str
        or not value
        or value == "."
        or "\0" in value
        or not value.isascii()
        or "\\" in value
    ):
        raise IndependentVerificationFailure(HOLD_TREE, f"{label} path spelling is unsafe")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or "." in pure.parts
        or "" in pure.parts
        or pure.as_posix() != value
    ):
        raise IndependentVerificationFailure(HOLD_TREE, f"{label} path is unsafe")
    return value


def _stat_identity(item: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_nlink,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


def _validated_root_directory(path: Path, *, code: str, label: str) -> Path:
    try:
        before = path.lstat()
    except OSError as error:
        raise IndependentVerificationFailure(code, f"{label} root lstat failed") from error
    if stat.S_ISLNK(before.st_mode):
        raise IndependentVerificationFailure(code, f"{label} root is a symlink")
    if not stat.S_ISDIR(before.st_mode):
        raise IndependentVerificationFailure(code, f"{label} root is not a directory")
    resolved = path.resolve()
    try:
        after = resolved.lstat()
    except OSError as error:
        raise IndependentVerificationFailure(code, f"{label} root resolve failed") from error
    if _stat_identity(before) != _stat_identity(after):
        raise IndependentVerificationFailure(code, f"{label} root changed while resolving")
    return resolved


def read_regular_stable(
    path: Path,
    *,
    maximum_bytes: int,
    code: str = HOLD_SOURCE,
    expected_identity: tuple[int, int, int, int, int, int, int] | None = None,
) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise IndependentVerificationFailure(
            code, f"cannot open required file {path.name}"
        ) from error
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > maximum_bytes
        ):
            raise IndependentVerificationFailure(code, f"unsafe or oversized file {path.name}")
        if expected_identity is not None and _stat_identity(before) != expected_identity:
            raise IndependentVerificationFailure(
                code, f"path identity changed before read {path.name}"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            block = os.read(descriptor, min(1 << 20, maximum_bytes + 1 - total))
            if not block:
                break
            chunks.append(block)
            total += len(block)
            if total > maximum_bytes:
                raise IndependentVerificationFailure(code, f"oversized file {path.name}")
        after = os.fstat(descriptor)
        try:
            path_after = path.lstat()
        except OSError as error:
            raise IndependentVerificationFailure(
                code, f"path vanished after read {path.name}"
            ) from error
        if (
            _stat_identity(before) != _stat_identity(after)
            or _stat_identity(after) != _stat_identity(path_after)
            or total != before.st_size
        ):
            raise IndependentVerificationFailure(code, f"file changed during read {path.name}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _read_regular_stable_at(
    directory_descriptor: int,
    name: str,
    *,
    maximum_bytes: int,
    code: str,
    expected_identity: tuple[int, int, int, int, int, int, int],
) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory_descriptor)
    except OSError as error:
        raise IndependentVerificationFailure(code, f"cannot open required file {name}") from error
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > maximum_bytes
            or _stat_identity(before) != expected_identity
        ):
            raise IndependentVerificationFailure(code, f"unsafe or replaced file {name}")
        chunks: list[bytes] = []
        total = 0
        while True:
            block = os.read(descriptor, min(1 << 20, maximum_bytes + 1 - total))
            if not block:
                break
            chunks.append(block)
            total += len(block)
            if total > maximum_bytes:
                raise IndependentVerificationFailure(code, f"oversized file {name}")
        after = os.fstat(descriptor)
        try:
            linked_after = os.stat(
                name,
                dir_fd=directory_descriptor,
                follow_symlinks=False,
            )
        except OSError as error:
            raise IndependentVerificationFailure(
                code, f"file vanished after read {name}"
            ) from error
        if (
            _stat_identity(before) != _stat_identity(after)
            or _stat_identity(after) != _stat_identity(linked_after)
            or total != before.st_size
        ):
            raise IndependentVerificationFailure(code, f"file changed during read {name}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def verify_exact_file(report_root: Path, relative: Path, expected_sha256: str) -> bytes:
    payload = read_regular_stable(report_root / relative, maximum_bytes=MAX_JSON_FILE_BYTES)
    if not hmac.compare_digest(sha256_bytes(payload), expected_sha256):
        raise IndependentVerificationFailure(HOLD_SOURCE, f"frozen source drifted: {relative.name}")
    return payload


def _is_forbidden_module_name(name: str) -> bool:
    return any(component in _FORBIDDEN_IMPORTS for component in name.split("."))


def _assert_source_import_boundary(source: bytes, *, filename: str) -> None:
    try:
        tree = ast.parse(source.decode("utf-8"), filename=filename)
    except (UnicodeDecodeError, SyntaxError) as error:
        raise IndependentVerificationFailure(
            HOLD_IMPORT, "verifier source cannot be parsed"
        ) from error
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                imported.add(module)
            for alias in node.names:
                imported.add(alias.name)
                if module:
                    imported.add(f"{module}.{alias.name}")
    if any(_is_forbidden_module_name(name) for name in imported):
        raise IndependentVerificationFailure(HOLD_IMPORT, "forbidden implementation import found")
    dynamic_names = {"__import__", "compile", "eval", "exec"}
    dynamic_attributes = {
        "exec_module",
        "find_spec",
        "import_module",
        "load_module",
        "module_from_spec",
        "spec_from_file_location",
    }
    if any(
        isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id in dynamic_names)
            or (isinstance(node.func, ast.Attribute) and node.func.attr in dynamic_attributes)
        )
        for node in ast.walk(tree)
    ):
        raise IndependentVerificationFailure(HOLD_IMPORT, "dynamic import path found")


def assert_import_boundary() -> None:
    source = read_regular_stable(
        Path(__file__), maximum_bytes=MAX_JSON_FILE_BYTES, code=HOLD_IMPORT
    )
    _assert_source_import_boundary(source, filename=Path(__file__).name)
    if any(_is_forbidden_module_name(name) for name in sys.modules):
        raise IndependentVerificationFailure(HOLD_IMPORT, "forbidden runtime module is loaded")


def inventory_candidate_tree(root: Path) -> TreeSnapshot:
    try:
        root_before = root.lstat()
    except OSError as error:
        raise IndependentVerificationFailure(HOLD_TREE, "candidate root lstat failed") from error
    if stat.S_ISLNK(root_before.st_mode):
        raise IndependentVerificationFailure(HOLD_TREE, "candidate root is a symlink")
    root = root.resolve()
    if not stat.S_ISDIR(root_before.st_mode):
        raise IndependentVerificationFailure(HOLD_TREE, "candidate root is not a directory")
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        root_descriptor = os.open(root, directory_flags)
    except OSError as error:
        raise IndependentVerificationFailure(HOLD_TREE, "candidate root open failed") from error
    if _stat_identity(os.fstat(root_descriptor)) != _stat_identity(root_before):
        os.close(root_descriptor)
        raise IndependentVerificationFailure(HOLD_TREE, "candidate root changed before traversal")
    files: dict[str, dict[str, object]] = {}
    directories: set[str] = set()
    inodes: dict[tuple[int, int], str] = {}
    total_bytes = 0
    pending: list[tuple[int, PurePosixPath, tuple[int, int, int, int, int, int, int]]] = [
        (root_descriptor, PurePosixPath("."), _stat_identity(root_before))
    ]
    try:
        while pending:
            directory_descriptor, parent, expected_directory_identity = pending.pop()
            try:
                directory_before = os.fstat(directory_descriptor)
                if _stat_identity(directory_before) != expected_directory_identity:
                    raise IndependentVerificationFailure(
                        HOLD_TREE, "queued candidate directory changed before traversal"
                    )
                with os.scandir(directory_descriptor) as entries:
                    for entry in entries:
                        relative = (
                            PurePosixPath(entry.name)
                            if parent == PurePosixPath(".")
                            else parent / entry.name
                        )
                        if len(relative.parts) > MAX_TREE_RELATIVE_DEPTH:
                            raise IndependentVerificationFailure(
                                HOLD_TREE, "candidate tree relative-depth cap exceeded"
                            )
                        name = validate_relative_manifest_path(relative.as_posix(), label="tree")
                        try:
                            metadata = entry.stat(follow_symlinks=False)
                        except OSError as error:
                            raise IndependentVerificationFailure(
                                HOLD_TREE, "tree lstat failed"
                            ) from error
                        inode = (metadata.st_dev, metadata.st_ino)
                        if inode in inodes:
                            raise IndependentVerificationFailure(
                                HOLD_TREE, "hard-link or inode alias found"
                            )
                        inodes[inode] = name
                        if stat.S_ISLNK(metadata.st_mode):
                            raise IndependentVerificationFailure(
                                HOLD_TREE, "symlink found in candidate"
                            )
                        if stat.S_ISDIR(metadata.st_mode):
                            if len(directories) >= MAX_TREE_DIRECTORIES:
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "candidate directory cap exceeded"
                                )
                            directories.add(name)
                            try:
                                child_descriptor = os.open(
                                    entry.name,
                                    directory_flags,
                                    dir_fd=directory_descriptor,
                                )
                            except OSError as error:
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "candidate directory open failed"
                                ) from error
                            child_identity = _stat_identity(os.fstat(child_descriptor))
                            if child_identity != _stat_identity(metadata):
                                os.close(child_descriptor)
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "candidate directory changed while queued"
                                )
                            pending.append((child_descriptor, relative, child_identity))
                        elif stat.S_ISREG(metadata.st_mode):
                            if metadata.st_nlink != 1:
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "multiple hard links found"
                                )
                            if len(files) >= MAX_TREE_FILES:
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "candidate file cap exceeded"
                                )
                            total_bytes += metadata.st_size
                            if total_bytes > MAX_TREE_BYTES:
                                raise IndependentVerificationFailure(
                                    HOLD_TREE, "candidate byte cap exceeded"
                                )
                            payload = _read_regular_stable_at(
                                directory_descriptor,
                                entry.name,
                                maximum_bytes=MAX_JSON_FILE_BYTES,
                                code=HOLD_TREE,
                                expected_identity=_stat_identity(metadata),
                            )
                            files[name] = {
                                "byte_length": metadata.st_size,
                                "path": name,
                                "sha256": sha256_bytes(payload),
                            }
                        else:
                            raise IndependentVerificationFailure(
                                HOLD_TREE, "nonregular tree node found"
                            )
                if _stat_identity(os.fstat(directory_descriptor)) != expected_directory_identity:
                    raise IndependentVerificationFailure(
                        HOLD_TREE, "candidate directory changed during traversal"
                    )
            except OSError as error:
                raise IndependentVerificationFailure(
                    HOLD_TREE, "candidate tree enumeration failed"
                ) from error
            finally:
                os.close(directory_descriptor)
        try:
            root_after = root.lstat()
        except OSError as error:
            raise IndependentVerificationFailure(HOLD_TREE, "candidate root vanished") from error
        if _stat_identity(root_after) != _stat_identity(root_before):
            raise IndependentVerificationFailure(
                HOLD_TREE, "candidate root changed during traversal"
            )
    finally:
        for descriptor, _, _ in pending:
            try:
                os.close(descriptor)
            except OSError:
                pass
    lines = [f"{files[path]['sha256']}  ./{path}\n".encode("ascii") for path in sorted(files)]
    return TreeSnapshot(files, frozenset(directories), total_bytes, sha256_bytes(b"".join(lines)))


def _construction(alignment: str, coordinate: str) -> str:
    if alignment == "cell_centred_reflecting":
        return "cell_centred_reflecting_scharfetter_gummel"
    if alignment == "vertex_centred_reflecting_dual":
        return "vertex_centred_reflecting_scharfetter_gummel"
    if alignment == "cell_centred_periodic_base":
        return "cell_centred_periodic_diffusion"
    if alignment == "cell_centred_periodic_half_shift":
        return "cell_centred_periodic_diffusion_half_shift"
    raise IndependentVerificationFailure(HOLD_PARTITION, f"unknown {coordinate} alignment")


def reconstruct_axis_partition(coordinate: str, spec: object) -> AxisPartition:
    if type(spec) is not dict:
        raise IndependentVerificationFailure(HOLD_PARTITION, f"{coordinate} spec is not an object")
    alignment = spec.get("alignment")
    size = spec.get("size")
    if type(alignment) is not str or type(size) is not int or size < 3:
        raise IndependentVerificationFailure(HOLD_PARTITION, f"{coordinate} alignment/size drifted")
    construction = _construction(alignment, coordinate)
    if alignment.startswith("cell_centred_periodic"):
        if set(spec) != _PERIODIC_SPEC_KEYS:
            raise IndependentVerificationFailure(HOLD_PARTITION, "periodic spec key set drifted")
        lower, width = Fraction(-1, 2), Fraction(1)
        step = Fraction(1, size)
        expected_shift = Fraction(0) if alignment.endswith("base") else step / 2
        shift = parse_reduced_fraction(spec["periodic_shift_exact"], label="periodic shift")
        if shift != expected_shift:
            raise IndependentVerificationFailure(HOLD_PARTITION, "periodic shift drifted")
        positions: list[Fraction] = []
        segments: list[tuple[tuple[Fraction, Fraction], ...]] = []
        upper = lower + width
        for index in range(size):
            start = lower + index * step + shift
            end = start + step
            position = start + step / 2
            if position >= upper:
                position -= width
            positions.append(position)
            if end <= upper:
                segments.append(((start, end),))
            else:
                segments.append(((start, upper), (lower, end - width)))
        return AxisPartition(
            coordinate,
            construction,
            lower,
            width,
            True,
            shift,
            tuple(positions),
            tuple(step for _ in range(size)),
            tuple(segments),
        )
    if set(spec) != _REFLECTING_SPEC_KEYS:
        raise IndependentVerificationFailure(HOLD_PARTITION, "reflecting spec key set drifted")
    lower = parse_binary64_hex_as_fraction(spec["lower_binary64_hex"], label=f"{coordinate} lower")
    upper = parse_binary64_hex_as_fraction(spec["upper_binary64_hex"], label=f"{coordinate} upper")
    if lower >= upper:
        raise IndependentVerificationFailure(HOLD_PARTITION, "reflecting bounds drifted")
    width = upper - lower
    if alignment == "cell_centred_reflecting":
        step = width / size
        positions = tuple(lower + (2 * index + 1) * step / 2 for index in range(size))
        boundaries = tuple(lower + index * step for index in range(size + 1))
    elif alignment == "vertex_centred_reflecting_dual":
        step = width / (size - 1)
        positions = tuple(lower + index * step for index in range(size))
        boundaries = (
            (lower,) + tuple((a + b) / 2 for a, b in zip(positions, positions[1:])) + (upper,)
        )
    else:
        raise IndependentVerificationFailure(HOLD_PARTITION, "reflecting alignment drifted")
    segments = tuple(((boundaries[index], boundaries[index + 1]),) for index in range(size))
    volumes = tuple(boundaries[index + 1] - boundaries[index] for index in range(size))
    if sum(volumes, Fraction(0)) != width or any(value <= 0 for value in volumes):
        raise IndependentVerificationFailure(HOLD_PARTITION, "reflecting partition closure failed")
    return AxisPartition(
        coordinate,
        construction,
        lower,
        width,
        False,
        Fraction(0),
        positions,
        volumes,
        segments,
    )


def reconstruct_all_partitions(configuration: dict[str, object]) -> tuple[AxisPartition, ...]:
    if set(configuration) != _CONFIGURATION_ROW_KEYS:
        raise IndependentVerificationFailure(HOLD_PARTITION, "configuration row key set drifted")
    return tuple(reconstruct_axis_partition(name, configuration[name]) for name in COORDINATES)


def load_frozen_geometry_authority(report_root: Path) -> GeometryAuthority:
    source = verify_exact_file(report_root, AUTHORITY_PATH, AUTHORITY_SHA256)
    payload = strict_load_ascii_json(source, label="geometry authority")
    authority = require_keys(
        payload,
        {
            "configuration_bundle",
            "contact_geometry",
            "coordinate_order",
            "flags",
            "physical_dimension",
            "quotient_dimension",
            "schema",
            "status",
            "support_basis",
        },
        label="geometry authority",
    )
    contact = require_keys(
        authority["contact_geometry"],
        {
            "cell_fraction_definition",
            "contact_set",
            "radius_binary64_hex",
            "radius_exact",
            "transverse_cut_locus_condition",
            "transverse_period_exact",
        },
        label="contact authority",
    )
    support = require_keys(
        authority["support_basis"], _AUTHORITY_SUPPORT_KEYS, label="support authority"
    )
    if authority["schema"] != AUTHORITY_SCHEMA:
        raise IndependentVerificationFailure(HOLD_SOURCE, "authority schema drifted")
    radius = parse_reduced_fraction(contact["radius_exact"], label="radius exact")
    radius_hex = parse_binary64_hex_as_fraction(contact["radius_binary64_hex"], label="radius hex")
    period = parse_reduced_fraction(contact["transverse_period_exact"], label="period")
    centres = tuple(
        parse_reduced_fraction(value, label=f"support centre {index}")
        for index, value in enumerate(support.get("centres_exact", []))
    )
    centres_hex = tuple(
        parse_binary64_hex_as_fraction(value, label=f"support centre hex {index}")
        for index, value in enumerate(support.get("centres_binary64_hex", []))
    )
    half_width = parse_reduced_fraction(support.get("half_width_exact"), label="half width")
    half_width_hex = parse_binary64_hex_as_fraction(
        support.get("half_width_binary64_hex"), label="half width hex"
    )
    if (
        authority["physical_dimension"] != 2
        or authority["quotient_dimension"] != 3
        or not exact_json_equal(authority["coordinate_order"], list(COORDINATES))
        or radius != radius_hex
        or not 0 < 2 * radius < period == 1
        or len(centres) != 4
        or centres != centres_hex
        or tuple(sorted(centres)) != centres
        or half_width != half_width_hex
        or half_width <= 0
        or type(support.get("profile_count")) is not int
        or support.get("profile_count") != 4
        or any(a + half_width >= b - half_width for a, b in zip(centres, centres[1:]))
        or support.get("analytic_integral_each") != "1/1"
    ):
        raise IndependentVerificationFailure(HOLD_SOURCE, "authority geometry drifted")
    return GeometryAuthority(radius, period, centres, half_width)  # type: ignore[arg-type]


def load_control_free_configuration(report_root: Path) -> tuple[dict[str, object], bytes]:
    source = verify_exact_file(report_root, CONFIGURATION_PATH, CONFIGURATION_SHA256)
    payload = strict_load_ascii_json(source, label="control-free configuration")
    payload = require_keys(payload, _CONFIGURATION_KEYS, label="control-free configuration")
    rows = payload.get("configurations")
    if (
        payload.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or type(payload.get("configuration_count")) is not int
        or payload.get("configuration_count") != CONFIGURATION_COUNT
        or not exact_json_equal(payload.get("configuration_order"), list(EXPECTED_LABELS))
        or not exact_json_equal(payload.get("coordinate_order"), list(COORDINATES))
        or payload.get("total_state_workload") != 34_787_462
        or payload.get("authorizes_scientific_execution") is not False
        or payload.get("contains_budget_value") is not False
        or payload.get("contains_control_values") is not False
        or type(rows) is not list
        or len(rows) != CONFIGURATION_COUNT
    ):
        raise IndependentVerificationFailure(HOLD_SOURCE, "configuration boundary drifted")
    for index, row in enumerate(rows):
        if type(row) is not dict or row.get("label") != EXPECTED_LABELS[index]:
            raise IndependentVerificationFailure(HOLD_PARTITION, "configuration order drifted")
        axes = reconstruct_all_partitions(row)
        shape = [axis.size for axis in axes]
        if not exact_json_equal(row.get("shape"), shape) or row.get("expected_states") != math.prod(
            shape
        ):
            raise IndependentVerificationFailure(HOLD_PARTITION, "shape/state product drifted")
    return payload, source


@dataclass(frozen=True, slots=True)
class MPInterval:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    precision_bits: int

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not gmpy2.mpfr
            or type(self.upper) is not gmpy2.mpfr
            or self.precision_bits not in {PRIMARY_BITS, SENTINEL_BITS}
            or not gmpy2.is_finite(self.lower)
            or not gmpy2.is_finite(self.upper)
            or self.lower > self.upper
        ):
            raise IndependentVerificationFailure(HOLD_API, "invalid MPFR interval")

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_exact_fraction(self.lower), _mpfr_exact_fraction(self.upper))


def _mpfr_exact_fraction(value: gmpy2.mpfr) -> Fraction:
    return _mpq_exact_fraction(_support_mpfr_exact_mpq(value))


def _support_mpfr_exact_mpq(value: gmpy2.mpfr) -> gmpy2.mpq:
    if type(value) is not gmpy2.mpfr or not gmpy2.is_finite(value):
        raise IndependentVerificationFailure(HOLD_API, "invalid MPFR-to-MPQ input")
    if value == 0:
        return gmpy2.mpq(0)
    exponent = int(gmpy2.get_exp(value))
    precision = int(value.precision)
    implied_denominator_bits = max(1, precision - exponent + 1)
    if implied_denominator_bits > MAX_MPFR_TO_MPQ_DENOMINATOR_BITS:
        raise IndependentVerificationFailure(
            HOLD_SUPPORT,
            "MPFR exact denominator cap exceeded before MPQ conversion",
        )
    if max(1, precision, exponent) + 1 > MAX_SIMPSON_EXACT_COMPONENT_BITS:
        raise IndependentVerificationFailure(
            HOLD_SUPPORT,
            "MPFR exact numerator cap exceeded before MPQ conversion",
        )
    exact = gmpy2.mpq(value)
    _require_exact_component_cap(
        exact.numerator,
        exact.denominator,
        label="MPFR-to-MPQ conversion",
        code=HOLD_SUPPORT,
    )
    return exact


def _require_exact_component_cap(
    numerator: int | gmpy2.mpz,
    denominator: int | gmpy2.mpz,
    *,
    label: str,
    code: str = HOLD_API,
) -> None:
    if (
        numerator.bit_length() > MAX_SIMPSON_EXACT_COMPONENT_BITS
        or denominator.bit_length() > MAX_SIMPSON_EXACT_COMPONENT_BITS
    ):
        raise IndependentVerificationFailure(code, f"{label} exact component cap exceeded")


def _require_fraction_cap(
    value: Fraction,
    *,
    label: str,
    code: str = HOLD_API,
) -> Fraction:
    if type(value) is not Fraction:
        raise IndependentVerificationFailure(code, f"{label} is not an exact Fraction")
    _require_exact_component_cap(
        value.numerator,
        value.denominator,
        label=label,
        code=code,
    )
    return value


def _require_coordinate_cap(value: Fraction, *, label: str) -> Fraction:
    value = _require_fraction_cap(value, label=label, code=HOLD_SUPPORT)
    if (
        value.numerator.bit_length() > MAX_DYADIC_COORDINATE_COMPONENT_BITS
        or value.denominator.bit_length() > MAX_DYADIC_COORDINATE_COMPONENT_BITS
    ):
        raise IndependentVerificationFailure(
            HOLD_SUPPORT,
            f"{label} dyadic coordinate component cap exceeded",
        )
    return value


def _checked_dyadic_midpoint(lower: Fraction, upper: Fraction, *, label: str) -> Fraction:
    lower = _require_coordinate_cap(lower, label=f"{label} lower")
    upper = _require_coordinate_cap(upper, label=f"{label} upper")
    return _require_coordinate_cap((lower + upper) / 2, label=label)


def _fraction_exact_mpq(value: Fraction) -> gmpy2.mpq:
    _require_fraction_cap(value, label="Fraction-to-MPQ conversion")
    return gmpy2.mpq(value.numerator, value.denominator)


def _mpq_exact_fraction(value: gmpy2.mpq) -> Fraction:
    if type(value) is not gmpy2.mpq:
        raise IndependentVerificationFailure(HOLD_API, "MPQ-to-Fraction input drifted")
    _require_exact_component_cap(
        value.numerator,
        value.denominator,
        label="MPQ-to-Fraction conversion",
    )
    return Fraction(int(value.numerator), int(value.denominator))


def _new_verifier_context(precision: int, rounding: int) -> gmpy2.context:
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


_VERIFIER_MPFR_CONTEXTS: Final = {
    (precision, rounding): _new_verifier_context(precision, rounding)
    for precision in (PRIMARY_BITS, SENTINEL_BITS)
    for rounding in (gmpy2.RoundDown, gmpy2.RoundUp)
}


def _configure_verifier_context(
    context: gmpy2.context,
    precision: int,
    rounding: int,
) -> None:
    context.precision = precision
    context.real_prec = precision
    context.imag_prec = precision
    context.round = rounding
    context.real_round = gmpy2.RoundToNearest
    context.imag_round = gmpy2.RoundToNearest
    context.emax = 1_073_741_823
    context.emin = -1_073_741_823
    context.subnormalize = False
    context.trap_underflow = False
    context.trap_overflow = False
    context.trap_inexact = False
    context.trap_invalid = False
    context.trap_erange = False
    context.trap_divzero = False
    context.allow_complex = False
    context.rational_division = False
    context.allow_release_gil = False
    context.clear_flags()


def _enter_verifier_context(precision: int, rounding: int) -> gmpy2.context:
    try:
        selected = _VERIFIER_MPFR_CONTEXTS[(precision, rounding)]
    except KeyError as error:
        raise IndependentVerificationFailure(HOLD_API, "unsupported MPFR context") from error
    caller = gmpy2.get_context()
    if caller is selected:
        # This rare nested/signal-style path must not clear or reconfigure the
        # caller-owned cached object.  A clone is used only here; the ordinary
        # clean-child path reuses the four prebuilt contexts with zero clones.
        operation_context = gmpy2.context(selected)
    else:
        operation_context = selected
    _configure_verifier_context(operation_context, precision, rounding)
    gmpy2.set_context(operation_context)
    return caller


def _mpfr_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    _require_fraction_cap(value, label="Fraction-to-MPFR conversion")
    caller = _enter_verifier_context(precision, rounding)
    try:
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))
    finally:
        gmpy2.set_context(caller)


def mp_interval_from_fraction(value: Fraction, precision: int = PRIMARY_BITS) -> MPInterval:
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
    operation: str,
) -> gmpy2.mpfr:
    caller = _enter_verifier_context(precision, rounding)
    try:
        if operation == "add":
            return +(left + right)
        if operation == "sub":
            return +(left - right)
        if operation == "mul":
            return +(left * right)
        if operation == "div":
            return +(left / right)
    finally:
        gmpy2.set_context(caller)
    raise IndependentVerificationFailure(HOLD_API, "unknown MPFR binary operation")


def _same_precision(left: MPInterval, right: MPInterval) -> int:
    if left.precision_bits != right.precision_bits:
        raise IndependentVerificationFailure(HOLD_API, "MPFR precision mismatch")
    return left.precision_bits


def mp_add(left: MPInterval, right: MPInterval) -> MPInterval:
    precision = _same_precision(left, right)
    return MPInterval(
        _mp_binary(left.lower, right.lower, precision, gmpy2.RoundDown, "add"),
        _mp_binary(left.upper, right.upper, precision, gmpy2.RoundUp, "add"),
        precision,
    )


def mp_sub(left: MPInterval, right: MPInterval) -> MPInterval:
    precision = _same_precision(left, right)
    return MPInterval(
        _mp_binary(left.lower, right.upper, precision, gmpy2.RoundDown, "sub"),
        _mp_binary(left.upper, right.lower, precision, gmpy2.RoundUp, "sub"),
        precision,
    )


def mp_mul(left: MPInterval, right: MPInterval) -> MPInterval:
    precision = _same_precision(left, right)
    pairs = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    lows = [_mp_binary(a, b, precision, gmpy2.RoundDown, "mul") for a, b in pairs]
    highs = [_mp_binary(a, b, precision, gmpy2.RoundUp, "mul") for a, b in pairs]
    return MPInterval(min(lows), max(highs), precision)


def _support_nonnegative_interval_mul(left: MPInterval, right: MPInterval) -> MPInterval:
    """Multiply nonnegative support-Simpson intervals using monotonicity."""
    precision = _same_precision(left, right)
    if left.lower < 0 or right.lower < 0:
        raise IndependentVerificationFailure(
            HOLD_API,
            "support Simpson nonnegative multiplication received a signed interval",
        )
    return MPInterval(
        _mp_binary(left.lower, right.lower, precision, gmpy2.RoundDown, "mul"),
        _mp_binary(left.upper, right.upper, precision, gmpy2.RoundUp, "mul"),
        precision,
    )


def mp_div(left: MPInterval, right: MPInterval) -> MPInterval:
    precision = _same_precision(left, right)
    if right.lower <= 0 <= right.upper:
        raise IndependentVerificationFailure(HOLD_API, "MPFR division interval contains zero")
    pairs = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    lows = [_mp_binary(a, b, precision, gmpy2.RoundDown, "div") for a, b in pairs]
    highs = [_mp_binary(a, b, precision, gmpy2.RoundUp, "div") for a, b in pairs]
    return MPInterval(min(lows), max(highs), precision)


def _mp_unary_value(
    value: gmpy2.mpfr,
    precision: int,
    rounding: int,
    function: object,
) -> gmpy2.mpfr:
    caller = _enter_verifier_context(precision, rounding)
    try:
        return +function(value)  # type: ignore[operator]
    finally:
        gmpy2.set_context(caller)


def _mp_monotone(interval: MPInterval, operation: str) -> MPInterval:
    if operation == "sqrt" and interval.lower < 0:
        raise IndependentVerificationFailure(HOLD_API, "sqrt domain escaped")
    if operation == "asin" and (interval.lower < -1 or interval.upper > 1):
        raise IndependentVerificationFailure(HOLD_API, "asin domain escaped")
    function = {"sqrt": gmpy2.sqrt, "asin": gmpy2.asin, "exp": gmpy2.exp}.get(operation)
    if function is None:
        raise IndependentVerificationFailure(HOLD_API, "unknown MPFR unary operation")
    lower = _mp_unary_value(
        interval.lower,
        interval.precision_bits,
        gmpy2.RoundDown,
        function,
    )
    upper = _mp_unary_value(
        interval.upper,
        interval.precision_bits,
        gmpy2.RoundUp,
        function,
    )
    return MPInterval(lower, upper, interval.precision_bits)


def mp_sqrt(interval: MPInterval) -> MPInterval:
    return _mp_monotone(interval, "sqrt")


def mp_asin(interval: MPInterval) -> MPInterval:
    return _mp_monotone(interval, "asin")


def mp_exp(interval: MPInterval) -> MPInterval:
    return _mp_monotone(interval, "exp")


def mp_pi(precision: int = PRIMARY_BITS) -> MPInterval:
    caller = _enter_verifier_context(precision, gmpy2.RoundDown)
    try:
        lower = +gmpy2.const_pi()
    finally:
        gmpy2.set_context(caller)
    caller = _enter_verifier_context(precision, gmpy2.RoundUp)
    try:
        upper = +gmpy2.const_pi()
    finally:
        gmpy2.set_context(caller)
    return MPInterval(lower, upper, precision)


def _validate_file_entry(entry: object, *, label: str) -> dict[str, object]:
    current = require_keys(entry, _FILE_KEYS, label=label)
    validate_relative_manifest_path(current["path"], label=label)
    require_sha256(current["sha256"], label=f"{label} SHA-256")
    if type(current["byte_length"]) is not int or current["byte_length"] < 0:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} byte length drifted")
    return current


def _inventory_map(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    entries = manifest.get("file_inventory")
    if type(entries) is not list or len(entries) != EXPECTED_INVENTORY_FILES:
        raise IndependentVerificationFailure(HOLD_MANIFEST, "candidate inventory count drifted")
    result: dict[str, dict[str, object]] = {}
    for item in entries:
        entry = _validate_file_entry(item, label="candidate inventory entry")
        path = entry["path"]
        if path in result:
            raise IndependentVerificationFailure(HOLD_MANIFEST, "duplicate inventory path")
        result[path] = entry
    if list(result) != sorted(result):
        raise IndependentVerificationFailure(HOLD_MANIFEST, "inventory order drifted")
    return result


def _read_candidate_entry(
    root: Path,
    entry: object,
    inventory: dict[str, dict[str, object]],
    snapshot: TreeSnapshot,
    referenced: set[str],
    *,
    maximum_bytes: int,
    label: str,
) -> bytes:
    current = _validate_file_entry(entry, label=label)
    path = current["path"]
    if inventory.get(path) != current or snapshot.files.get(path) != current:
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} is not inventory-bound")
    if path in referenced:
        raise IndependentVerificationFailure(HOLD_MANIFEST, "duplicate candidate file reference")
    referenced.add(path)
    payload = read_regular_stable(root / path, maximum_bytes=maximum_bytes, code=HOLD_TREE)
    if len(payload) != current["byte_length"] or not hmac.compare_digest(
        sha256_bytes(payload), current["sha256"]
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, f"{label} bytes drifted")
    return payload


def stream_be64_intervals(
    raw: bytes,
    manifest: object,
    *,
    role: str,
    shape: Sequence[int],
) -> tuple[ExactInterval, ...]:
    current = require_keys(manifest, _RAW_KEYS, label="raw interval manifest")
    if any(type(dimension) is not int or dimension < 0 for dimension in shape):
        raise IndependentVerificationFailure(
            HOLD_MANIFEST, "raw logical shape is not exact integers"
        )
    count = math.prod(shape)
    if (
        current["schema"] != RAW_SCHEMA
        or current["byte_order"] != "big"
        or current["record_format"] != ">dd"
        or current["role"] != role
        or type(current["logical_shape"]) is not list
        or any(type(dimension) is not int for dimension in current["logical_shape"])
        or not exact_json_equal(current["logical_shape"], list(shape))
        or type(current["record_count"]) is not int
        or current["record_count"] != count
        or type(current["raw_byte_length"]) is not int
        or current["raw_byte_length"] != len(raw)
        or current["raw_sha256"] != sha256_bytes(raw)
        or len(raw) != 16 * count
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, "raw manifest drifted")
    result: list[ExactInterval] = []
    for offset in range(0, len(raw), 16):
        lower_bits, upper_bits = struct.unpack_from(">QQ", raw, offset)
        lower, upper = struct.unpack_from(">dd", raw, offset)
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower_bits == 0x8000000000000000
            or upper_bits == 0x8000000000000000
            or lower > upper
        ):
            raise IndependentVerificationFailure(HOLD_MANIFEST, "raw endpoint is noncanonical")
        result.append(ExactInterval(Fraction.from_float(lower), Fraction.from_float(upper)))
    return tuple(result)


def _source_pins() -> dict[str, dict[str, str]]:
    return {
        "configuration": {"path": CONFIGURATION_PATH.as_posix(), "sha256": CONFIGURATION_SHA256},
        "f0_core": {"path": F0_CORE_PATH.as_posix(), "sha256": F0_CORE_SHA256},
        "killing_geometry_source": {
            "path": AUTHORITY_PATH.as_posix(),
            "sha256": AUTHORITY_SHA256,
        },
        "partition_bundle_manifest": {
            "path": PARTITION_BUNDLE_PATH.as_posix(),
            "sha256": PARTITION_BUNDLE_SHA256,
        },
        "producer": {"path": PRODUCER_PATH.as_posix(), "sha256": PRODUCER_SHA256},
        "production_initial_stream": {
            "path": INITIAL_STREAM_SOURCE_PATH.as_posix(),
            "sha256": INITIAL_STREAM_SOURCE_SHA256,
        },
    }


def _external_inventory(partition_manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    entries = partition_manifest.get("file_inventory")
    if type(entries) is not list or len(entries) != 206:
        raise IndependentVerificationFailure(HOLD_PARTITION, "accepted partition inventory drifted")
    result: dict[str, dict[str, object]] = {}
    for item in entries:
        entry = _validate_file_entry(item, label="accepted partition inventory")
        path = entry["path"]
        if path in result:
            raise IndependentVerificationFailure(
                HOLD_PARTITION, "accepted partition path duplicate"
            )
        result[path] = entry
    return result


def _read_external(
    report_root: Path,
    entry: object,
    inventory: dict[str, dict[str, object]],
    *,
    label: str,
) -> bytes:
    current = _validate_file_entry(entry, label=label)
    if inventory.get(current["path"]) != current:
        raise IndependentVerificationFailure(
            HOLD_PARTITION, f"{label} lacks accepted inventory pin"
        )
    payload = read_regular_stable(
        report_root / PARTITION_ROOT_PATH / current["path"],
        maximum_bytes=MAX_JSON_FILE_BYTES,
        code=HOLD_PARTITION,
    )
    if len(payload) != current["byte_length"] or sha256_bytes(payload) != current["sha256"]:
        raise IndependentVerificationFailure(HOLD_PARTITION, f"{label} bytes drifted")
    return payload


def _contact_relation_payload(
    row: dict[str, object],
    contact: dict[str, object],
    partition_source: dict[str, object],
    authority: GeometryAuthority,
) -> dict[str, object]:
    bindings = partition_source["partitions"]
    partition_hashes = {
        entry["coordinate"]: entry["file"]["sha256"]
        for entry in bindings
        if entry["coordinate"] in COORDINATES[1:]
    }
    axis_hashes = {
        entry["coordinate"]: entry["axis_relation_sha256"]
        for entry in bindings
        if entry["coordinate"] in COORDINATES[1:]
    }
    return {
        "active_cell_count": contact["active_cell_count"],
        "area_enclosure_exact": contact["area_enclosure_exact"],
        "axis_relation_sha256s": axis_hashes,
        "configuration_index": row["configuration_index"],
        "configuration_label": row["configuration_label"],
        "contact_coordinate_order": list(COORDINATES[1:]),
        "contact_raw_sha256": contact["file"]["sha256"],
        "full_cell_count": contact["full_cell_count"],
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "killing_geometry_source_sha256": AUTHORITY_SHA256,
        "logical_shape": row["shape"][1:],
        "partition_sha256s": partition_hashes,
        "producer_source_sha256": PRODUCER_SHA256,
        "quality_ledger": contact["quality_ledger"],
        "radius_exact": fraction_text(authority.radius),
    }


def _support_relation_payload(
    row: dict[str, object],
    support: dict[str, object],
    partition_source: dict[str, object],
) -> dict[str, object]:
    midpoint = next(
        entry for entry in partition_source["partitions"] if entry["coordinate"] == "midpoint"
    )
    return {
        "configuration_index": row["configuration_index"],
        "configuration_label": row["configuration_label"],
        "centre_exact": support["centre_exact"],
        "half_width_exact": support["half_width_exact"],
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "integral_enclosure_exact": support["integral_enclosure_exact"],
        "killing_geometry_source_sha256": AUTHORITY_SHA256,
        "logical_shape": [row["shape"][0]],
        "midpoint_axis_relation_sha256": midpoint["axis_relation_sha256"],
        "midpoint_partition_sha256": midpoint["file"]["sha256"],
        "profile_index": support["profile_index"],
        "producer_source_sha256": PRODUCER_SHA256,
        "quality_ledger": support["quality_ledger"],
        "support_density_raw_sha256": support["file"]["sha256"],
    }


@dataclass(frozen=True, slots=True)
class ParsedCandidate:
    manifest: dict[str, object]
    rows: tuple[dict[str, object], ...]
    axes: tuple[tuple[AxisPartition, AxisPartition, AxisPartition], ...]
    contacts: tuple[tuple[ExactInterval, ...], ...]
    supports: tuple[tuple[tuple[ExactInterval, ...], ...], ...]
    independent_partition_sha256s: tuple[tuple[str, str, str], ...]
    tree: TreeSnapshot
    partition_tree: TreeSnapshot


@dataclass(frozen=True, slots=True)
class BumpIntegralTable:
    precision_bits: int
    breakpoints: tuple[Fraction, ...]
    intervals: tuple[ExactInterval, ...]
    normalizer: ExactInterval
    tree_panel_count: int
    accepted_leaf_count: int
    maximum_dyadic_depth: int
    maximum_dfs_stack: int

    def integral(self, lower: Fraction, upper: Fraction) -> ExactInterval:
        if lower >= upper:
            return ExactInterval(Fraction(0), Fraction(0))
        try:
            left = self.breakpoints.index(lower)
            right = self.breakpoints.index(upper)
        except ValueError as error:
            raise IndependentVerificationFailure(
                HOLD_SUPPORT, "support endpoint absent from shared table"
            ) from error
        selected = self.intervals[left:right]
        return ExactInterval(
            sum((item.lower for item in selected), Fraction(0)),
            sum((item.upper for item in selected), Fraction(0)),
        )


def parse_candidate_bundle(report_root: Path, bundle_root: Path) -> ParsedCandidate:
    report_root = _validated_root_directory(
        report_root,
        code=HOLD_TREE,
        label="report",
    )
    assert_import_boundary()
    snapshot = inventory_candidate_tree(bundle_root)
    if (
        len(snapshot.files) != EXPECTED_TREE_FILES
        or len(snapshot.directories) != EXPECTED_TREE_DIRECTORIES
    ):
        raise IndependentVerificationFailure(HOLD_TREE, "candidate tree cardinality drifted")
    if snapshot.digest != CANDIDATE_TREE_SHA256:
        raise IndependentVerificationFailure(HOLD_TREE, "candidate tree digest drifted")
    authority = load_frozen_geometry_authority(report_root)
    configuration, configuration_bytes = load_control_free_configuration(report_root)
    partition_bytes = verify_exact_file(report_root, PARTITION_BUNDLE_PATH, PARTITION_BUNDLE_SHA256)
    partition_manifest_payload = strict_load_ascii_json(partition_bytes, label="partition bundle")
    if type(partition_manifest_payload) is not dict:
        raise IndependentVerificationFailure(HOLD_PARTITION, "partition bundle is not an object")
    partition_inventory = _external_inventory(partition_manifest_payload)
    partition_snapshot = inventory_candidate_tree(report_root / PARTITION_ROOT_PATH)
    if (
        len(partition_snapshot.files) != EXPECTED_PARTITION_TREE_FILES
        or len(partition_snapshot.directories) != EXPECTED_PARTITION_TREE_DIRECTORIES
        or partition_snapshot.total_bytes != EXPECTED_PARTITION_TREE_BYTES
        or partition_snapshot.digest != PARTITION_TREE_SHA256
    ):
        raise IndependentVerificationFailure(HOLD_PARTITION, "accepted partition tree drifted")
    partition_bundle_entry = {
        "byte_length": len(partition_bytes),
        "path": "bundle.json",
        "sha256": PARTITION_BUNDLE_SHA256,
    }
    if partition_snapshot.files != partition_inventory | {"bundle.json": partition_bundle_entry}:
        raise IndependentVerificationFailure(
            HOLD_PARTITION, "accepted partition inventory/tree closure drifted"
        )
    verify_exact_file(report_root, PRODUCER_PATH, PRODUCER_SHA256)
    verify_exact_file(report_root, PRODUCER_TEST_PATH, PRODUCER_TEST_SHA256)
    verify_exact_file(report_root, F0_CORE_PATH, F0_CORE_SHA256)
    verify_exact_file(report_root, INITIAL_STREAM_SOURCE_PATH, INITIAL_STREAM_SOURCE_SHA256)
    verify_exact_file(report_root, DESIGN_PATH, DESIGN_SHA256)

    bundle_bytes = read_regular_stable(
        bundle_root / "bundle.json", maximum_bytes=MAX_JSON_FILE_BYTES, code=HOLD_TREE
    )
    if sha256_bytes(bundle_bytes) != CANDIDATE_BUNDLE_SHA256:
        raise IndependentVerificationFailure(HOLD_MANIFEST, "candidate bundle hash drifted")
    manifest = require_keys(
        strict_load_ascii_json(bundle_bytes, label="candidate bundle"),
        _BUNDLE_KEYS,
        label="candidate bundle",
    )
    factor_digest = digest_domain(
        b"production-killing-factorization-flatten-contract-v1\0",
        manifest["factorization_contract"],
    )
    if (
        manifest["schema"] != BUNDLE_SCHEMA
        or manifest["status"] != BUNDLE_STATUS
        or type(manifest["configuration_count"]) is not int
        or manifest["configuration_count"] != CONFIGURATION_COUNT
        or not exact_json_equal(manifest["flags"], _BUNDLE_FLAGS)
        or not exact_json_equal(manifest["method"], _METHOD)
        or not exact_json_equal(manifest["totals"], _EXPECTED_TOTALS)
        or not exact_json_equal(manifest["source_pins"], _source_pins())
        or manifest["factorization_contract_sha256"] != FACTORIZATION_CONTRACT_SHA256
        or factor_digest != FACTORIZATION_CONTRACT_SHA256
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, "candidate bundle boundary drifted")
    inventory = _inventory_map(manifest)
    if snapshot.files != inventory | {"bundle.json": snapshot.files["bundle.json"]}:
        raise IndependentVerificationFailure(HOLD_TREE, "candidate inventory/tree closure drifted")
    referenced: set[str] = set()
    request = manifest["request_snapshots"]
    if type(request) is not dict or set(request) != {
        "configuration",
        "killing_geometry_source",
        "partition_bundle_manifest",
    }:
        raise IndependentVerificationFailure(HOLD_MANIFEST, "request snapshot keys drifted")
    for role, expected in (
        ("configuration", configuration_bytes),
        (
            "killing_geometry_source",
            verify_exact_file(report_root, AUTHORITY_PATH, AUTHORITY_SHA256),
        ),
        ("partition_bundle_manifest", partition_bytes),
    ):
        observed = _read_candidate_entry(
            bundle_root,
            request[role],
            inventory,
            snapshot,
            referenced,
            maximum_bytes=MAX_JSON_FILE_BYTES,
            label=f"{role} snapshot",
        )
        if observed != expected:
            raise IndependentVerificationFailure(HOLD_MANIFEST, f"{role} snapshot drifted")

    summaries = manifest["rows"]
    config_rows = configuration["configurations"]
    if type(summaries) is not list or len(summaries) != CONFIGURATION_COUNT:
        raise IndependentVerificationFailure(HOLD_MANIFEST, "candidate row summaries drifted")
    parsed_rows: list[dict[str, object]] = []
    all_axes: list[tuple[AxisPartition, AxisPartition, AxisPartition]] = []
    all_contacts: list[tuple[ExactInterval, ...]] = []
    all_supports: list[tuple[tuple[ExactInterval, ...], ...]] = []
    partition_semantics: list[tuple[str, str, str]] = []
    row_relations: list[str] = []
    graph_rows: list[tuple[dict[str, object], dict[str, object]]] = []
    for row_index, (summary_payload, config_row) in enumerate(
        zip(summaries, config_rows, strict=True)
    ):
        summary = require_keys(summary_payload, _SUMMARY_KEYS, label="candidate row summary")
        axes = reconstruct_all_partitions(config_row)
        shape = [axis.size for axis in axes]
        if (
            type(summary["configuration_index"]) is not int
            or summary["configuration_index"] != row_index
            or summary["configuration_label"] != EXPECTED_LABELS[row_index]
            or not exact_json_equal(summary["shape"], shape)
            or summary["expected_states"] != math.prod(shape)
            or summary["contact_fraction_records"] != shape[1] * shape[2]
            or type(summary["active_contact_cell_count"]) is not int
            or summary["active_contact_cell_count"] < 0
            or type(summary["full_contact_cell_count"]) is not int
            or summary["full_contact_cell_count"] < 0
            or summary["midpoint_cells"] != shape[0]
            or summary["support_density_records"] != 4 * shape[0]
            or summary["support_profile_count"] != 4
        ):
            raise IndependentVerificationFailure(HOLD_MANIFEST, "row summary scalar drifted")
        row_bytes = _read_candidate_entry(
            bundle_root,
            summary["row_manifest"],
            inventory,
            snapshot,
            referenced,
            maximum_bytes=MAX_JSON_FILE_BYTES,
            label="candidate row manifest",
        )
        row = require_keys(
            strict_load_ascii_json(row_bytes, label="candidate row"),
            _ROW_KEYS,
            label="candidate row",
        )
        if (
            row["schema"] != ROW_SCHEMA
            or row["status"] != ROW_STATUS
            or type(row["configuration_index"]) is not int
            or row["configuration_index"] != row_index
            or row["configuration_label"] != EXPECTED_LABELS[row_index]
            or not exact_json_equal(row["shape"], shape)
            or row["expected_states"] != math.prod(shape)
            or row["factorization_contract_sha256"] != FACTORIZATION_CONTRACT_SHA256
            or not exact_json_equal(row["flags"], _ROW_FLAGS)
            or not exact_json_equal(row["gates"], _ROW_GATES)
            or not exact_json_equal(row["source_pins"], _source_pins())
            or row["row_relation_sha256"] != summary["row_relation_sha256"]
        ):
            raise IndependentVerificationFailure(HOLD_MANIFEST, "row boundary drifted")
        partition_source = require_keys(
            row["partition_source"], _PARTITION_SOURCE_KEYS, label="candidate partition source"
        )
        if partition_source["bundle_manifest_sha256"] != PARTITION_BUNDLE_SHA256:
            raise IndependentVerificationFailure(HOLD_PARTITION, "partition bundle pin drifted")
        accepted_row_bytes = _read_external(
            report_root,
            partition_source["bundle_row_manifest"],
            partition_inventory,
            label="accepted partition row",
        )
        accepted_row = strict_load_ascii_json(accepted_row_bytes, label="accepted partition row")
        if (
            type(accepted_row) is not dict
            or accepted_row.get("schema") != PARTITION_ROW_SCHEMA
            or type(accepted_row.get("configuration_index")) is not int
            or accepted_row.get("configuration_index") != row_index
            or accepted_row.get("configuration_label") != EXPECTED_LABELS[row_index]
            or accepted_row.get("configuration_sha256") != CONFIGURATION_SHA256
            or accepted_row.get("expected_states") != math.prod(shape)
            or accepted_row.get("row_relation_sha256")
            != partition_source["bundle_row_relation_sha256"]
        ):
            raise IndependentVerificationFailure(HOLD_PARTITION, "accepted partition row drifted")
        bindings = partition_source["partitions"]
        accepted_axes = accepted_row.get("axes")
        if type(bindings) is not list or len(bindings) != 3 or type(accepted_axes) is not list:
            raise IndependentVerificationFailure(HOLD_PARTITION, "partition binding shape drifted")
        semantic_row: list[str] = []
        for coordinate_index, (binding_payload, axis, accepted_axis) in enumerate(
            zip(bindings, axes, accepted_axes, strict=True)
        ):
            binding = require_keys(
                binding_payload, _PARTITION_BINDING_KEYS, label="candidate partition binding"
            )
            if (
                type(accepted_axis) is not dict
                or binding["coordinate"] != COORDINATES[coordinate_index]
                or accepted_axis.get("coordinate") != binding["coordinate"]
                or accepted_axis.get("axis_relation_sha256") != binding["axis_relation_sha256"]
                or not exact_json_equal(accepted_axis.get("partition_file"), binding["file"])
            ):
                raise IndependentVerificationFailure(HOLD_PARTITION, "partition binding drifted")
            external = _read_external(
                report_root,
                binding["file"],
                partition_inventory,
                label="accepted partition file",
            )
            external_payload = require_keys(
                strict_load_ascii_json(external, label="accepted partition"),
                _PARTITION_KEYS,
                label="accepted partition",
            )
            if not exact_json_equal(external_payload, axis.payload()):
                raise IndependentVerificationFailure(
                    HOLD_PARTITION, "accepted partition differs from independent reconstruction"
                )
            semantic_row.append(axis.semantic_sha256)
        partition_semantics.append(tuple(semantic_row))  # type: ignore[arg-type]

        contact = require_keys(row["contact_fraction_relative"], _CONTACT_KEYS, label="contact")
        if (
            type(contact["active_cell_count"]) is not int
            or contact["active_cell_count"] != summary["active_contact_cell_count"]
            or type(contact["full_cell_count"]) is not int
            or contact["full_cell_count"] != summary["full_contact_cell_count"]
        ):
            raise IndependentVerificationFailure(
                HOLD_MANIFEST, "contact summary/row count binding drifted"
            )
        require_keys(
            contact["quality_ledger"], _CONTACT_QUALITY_KEYS, label="contact quality ledger"
        )
        contact_raw = _read_candidate_entry(
            bundle_root,
            contact["file"],
            inventory,
            snapshot,
            referenced,
            maximum_bytes=MAX_RAW_CONTACT_FILE_BYTES,
            label="contact raw",
        )
        decoded_contact = stream_be64_intervals(
            contact_raw,
            contact["manifest"],
            role="physical_contact_fraction_relative",
            shape=shape[1:],
        )
        if any(item.lower < 0 or item.upper > 1 for item in decoded_contact):
            raise IndependentVerificationFailure(HOLD_MANIFEST, "contact endpoint escaped [0,1]")
        contact_relation = digest_domain(
            b"production-killing-contact-relation-v1\0",
            _contact_relation_payload(row, contact, partition_source, authority),
        )
        if contact["relation_sha256"] != contact_relation:
            raise IndependentVerificationFailure(HOLD_MANIFEST, "contact relation drifted")

        support_payloads = row["support_densities"]
        if type(support_payloads) is not list or len(support_payloads) != 4:
            raise IndependentVerificationFailure(HOLD_MANIFEST, "support list drifted")
        decoded_supports: list[tuple[ExactInterval, ...]] = []
        support_relations: list[str] = []
        for profile_index, support_payload in enumerate(support_payloads):
            support = require_keys(support_payload, _SUPPORT_KEYS, label="support")
            require_keys(
                support["quality_ledger"],
                _SUPPORT_QUALITY_KEYS,
                label="support quality ledger",
            )
            if (
                type(support["profile_index"]) is not int
                or support["profile_index"] != profile_index
                or parse_reduced_fraction(support["centre_exact"], label="support centre")
                != authority.centres[profile_index]
                or parse_binary64_hex_as_fraction(
                    support["centre_binary64_hex"], label="support centre hex"
                )
                != authority.centres[profile_index]
                or parse_reduced_fraction(support["half_width_exact"], label="support half width")
                != authority.half_width
                or parse_binary64_hex_as_fraction(
                    support["half_width_binary64_hex"], label="support half width hex"
                )
                != authority.half_width
            ):
                raise IndependentVerificationFailure(
                    HOLD_MANIFEST, "support authority binding drifted"
                )
            support_raw = _read_candidate_entry(
                bundle_root,
                support["file"],
                inventory,
                snapshot,
                referenced,
                maximum_bytes=MAX_RAW_SUPPORT_FILE_BYTES,
                label="support raw",
            )
            decoded = stream_be64_intervals(
                support_raw,
                support["manifest"],
                role=f"physical_midpoint_support_density_{profile_index:02d}",
                shape=(shape[0],),
            )
            if any(item.lower < 0 for item in decoded):
                raise IndependentVerificationFailure(HOLD_MANIFEST, "support endpoint is negative")
            relation = digest_domain(
                b"production-killing-support-relation-v1\0",
                _support_relation_payload(row, support, partition_source),
            )
            if support["relation_sha256"] != relation:
                raise IndependentVerificationFailure(HOLD_MANIFEST, "support relation drifted")
            decoded_supports.append(decoded)
            support_relations.append(relation)
        expected_row_relation = digest_domain(
            b"production-killing-row-relation-v1\0",
            {
                "configuration_index": row_index,
                "configuration_label": EXPECTED_LABELS[row_index],
                "contact_relation_sha256": contact_relation,
                "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
                "partition_bundle_row_relation_sha256": partition_source[
                    "bundle_row_relation_sha256"
                ],
                "shape": shape,
                "source_pins": _source_pins(),
                "support_relation_sha256s": support_relations,
            },
        )
        if row["row_relation_sha256"] != expected_row_relation:
            raise IndependentVerificationFailure(HOLD_MANIFEST, "row relation drifted")
        parsed_rows.append(row)
        all_axes.append(axes)  # type: ignore[arg-type]
        all_contacts.append(decoded_contact)
        all_supports.append(tuple(decoded_supports))
        row_relations.append(expected_row_relation)
        graph_rows.append((summary, partition_source))
    if referenced != set(inventory):
        raise IndependentVerificationFailure(
            HOLD_MANIFEST, "candidate reference graph is not exact"
        )
    graph_payload = {
        "partition_bundle_manifest_sha256": PARTITION_BUNDLE_SHA256,
        "rows": [
            {
                "configuration_index": summary["configuration_index"],
                "bundle_row_manifest": source["bundle_row_manifest"],
                "bundle_row_relation_sha256": source["bundle_row_relation_sha256"],
                "partitions": source["partitions"],
            }
            for summary, source in graph_rows
        ],
    }
    graph_digest = digest_domain(
        b"production-killing-partition-reference-graph-v1\0", graph_payload
    )
    family_digest = digest_domain(
        b"production-killing-family-relation-v1\0",
        {
            "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
            "ordered_row_relation_sha256s": row_relations,
            "partition_reference_graph_sha256": graph_digest,
            "source_pins": _source_pins(),
        },
    )
    if (
        manifest["partition_reference_graph_sha256"] != graph_digest
        or manifest["family_relation_sha256"] != family_digest
        or graph_digest != PARTITION_REFERENCE_GRAPH_SHA256
        or family_digest != FAMILY_RELATION_SHA256
    ):
        raise IndependentVerificationFailure(HOLD_MANIFEST, "family relation graph drifted")
    return ParsedCandidate(
        manifest,
        tuple(parsed_rows),
        tuple(all_axes),
        tuple(all_contacts),
        tuple(all_supports),
        tuple(partition_semantics),
        snapshot,
        partition_snapshot,
    )


def _mp_zero(precision: int) -> gmpy2.mpfr:
    return _mpfr_fraction(Fraction(0), precision, gmpy2.RoundDown)


def _mp_one(precision: int) -> gmpy2.mpfr:
    return _mpfr_fraction(Fraction(1), precision, gmpy2.RoundUp)


def _clip_mp(interval: MPInterval, lower: Fraction, upper: Fraction) -> MPInterval:
    lo = max(interval.lower, _mpfr_fraction(lower, interval.precision_bits, gmpy2.RoundDown))
    hi = min(interval.upper, _mpfr_fraction(upper, interval.precision_bits, gmpy2.RoundUp))
    if lo > hi:
        raise IndependentVerificationFailure(HOLD_CONTACT, "MPFR interval clipping became empty")
    return MPInterval(lo, hi, interval.precision_bits)


def disk_antiderivative_enclosure(
    coordinate: MPInterval,
    radius: Fraction,
) -> MPInterval:
    precision = coordinate.precision_bits
    radius_interval = mp_interval_from_fraction(radius, precision)
    radius_squared = mp_interval_from_fraction(radius * radius, precision)
    coordinate = _clip_mp(coordinate, Fraction(0), radius)
    squared = mp_mul(coordinate, coordinate)
    radicand = mp_sub(radius_squared, squared)
    radicand = MPInterval(max(_mp_zero(precision), radicand.lower), radicand.upper, precision)
    root = mp_sqrt(radicand)
    product = mp_mul(coordinate, root)
    ratio = _clip_mp(mp_div(coordinate, radius_interval), Fraction(0), Fraction(1))
    angle = mp_asin(ratio)
    angular = mp_mul(radius_squared, angle)
    return mp_mul(mp_interval_from_fraction(Fraction(1, 2), precision), mp_add(product, angular))


def disk_quadrant_prefix_enclosure(
    x: Fraction,
    y: Fraction,
    radius: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> MPInterval:
    if x <= 0 or y <= 0:
        return mp_interval_from_fraction(Fraction(0), precision)
    x = min(x, radius)
    y = min(y, radius)
    if x * x + y * y <= radius * radius:
        return mp_interval_from_fraction(x * y, precision)
    threshold = mp_sqrt(mp_interval_from_fraction(radius * radius - y * y, precision))
    first = mp_mul(mp_interval_from_fraction(y, precision), threshold)
    at_x = disk_antiderivative_enclosure(mp_interval_from_fraction(x, precision), radius)
    at_threshold = disk_antiderivative_enclosure(threshold, radius)
    return mp_add(first, mp_sub(at_x, at_threshold))


def _quadrant_rectangle_area(
    x0: Fraction,
    x1: Fraction,
    y0: Fraction,
    y1: Fraction,
    radius: Fraction,
    precision: int,
) -> MPInterval:
    q11 = disk_quadrant_prefix_enclosure(x1, y1, radius, precision=precision)
    q01 = disk_quadrant_prefix_enclosure(x0, y1, radius, precision=precision)
    q10 = disk_quadrant_prefix_enclosure(x1, y0, radius, precision=precision)
    q00 = disk_quadrant_prefix_enclosure(x0, y0, radius, precision=precision)
    result = mp_add(mp_sub(q11, q01), mp_sub(q00, q10))
    return MPInterval(max(_mp_zero(precision), result.lower), result.upper, precision)


def _absolute_nonnegative_segments(
    lower: Fraction, upper: Fraction
) -> tuple[tuple[Fraction, Fraction], ...]:
    if lower >= upper:
        raise IndependentVerificationFailure(HOLD_CONTACT, "rectangle segment is reversed")
    if upper <= 0:
        return ((-upper, -lower),)
    if lower >= 0:
        return ((lower, upper),)
    return ((Fraction(0), -lower), (Fraction(0), upper))


def disk_rectangle_area_enclosure(
    x0: Fraction,
    x1: Fraction,
    y0: Fraction,
    y1: Fraction,
    radius: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> MPInterval:
    result = mp_interval_from_fraction(Fraction(0), precision)
    for a, b in _absolute_nonnegative_segments(x0, x1):
        for c, d in _absolute_nonnegative_segments(y0, y1):
            result = mp_add(result, _quadrant_rectangle_area(a, b, c, d, radius, precision))
    rectangle = (x1 - x0) * (y1 - y0)
    return _clip_mp(result, Fraction(0), rectangle)


def _nearest_axis_distance(lower: Fraction, upper: Fraction) -> Fraction:
    if lower <= 0 <= upper:
        return Fraction(0)
    return min(abs(lower), abs(upper))


def _rectangle_classification(
    x0: Fraction,
    x1: Fraction,
    y0: Fraction,
    y1: Fraction,
    radius_squared: Fraction,
) -> str:
    nearest = _nearest_axis_distance(x0, x1) ** 2 + _nearest_axis_distance(y0, y1) ** 2
    farthest = max(abs(x0), abs(x1)) ** 2 + max(abs(y0), abs(y1)) ** 2
    if nearest >= radius_squared:
        return "zero"
    if farthest <= radius_squared:
        return "full"
    return "partial"


def contact_fraction_oracle(
    x_segments: Sequence[tuple[Fraction, Fraction]],
    y_segments: Sequence[tuple[Fraction, Fraction]],
    cell_volume: Fraction,
    radius: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> tuple[ExactInterval, str]:
    radius_squared = radius * radius
    classifications = tuple(
        _rectangle_classification(x0, x1, y0, y1, radius_squared)
        for x0, x1 in x_segments
        for y0, y1 in y_segments
    )
    if all(item == "zero" for item in classifications):
        return ExactInterval(Fraction(0), Fraction(0)), "zero"
    if all(item == "full" for item in classifications):
        return ExactInterval(Fraction(1), Fraction(1)), "full"
    area = mp_interval_from_fraction(Fraction(0), precision)
    for x0, x1 in x_segments:
        for y0, y1 in y_segments:
            area = mp_add(
                area,
                disk_rectangle_area_enclosure(x0, x1, y0, y1, radius, precision=precision),
            )
    fraction = mp_div(area, mp_interval_from_fraction(cell_volume, precision)).exact()
    return ExactInterval(
        max(Fraction(0), fraction.lower), min(Fraction(1), fraction.upper)
    ), "partial"


def _parse_enclosure(payload: object, *, label: str) -> ExactInterval:
    current = require_keys(payload, {"lower_exact", "upper_exact"}, label=label)
    return ExactInterval(
        parse_reduced_fraction(current["lower_exact"], label=f"{label} lower"),
        parse_reduced_fraction(current["upper_exact"], label=f"{label} upper"),
    )


def require_exact_containment(
    candidate: ExactInterval,
    oracle: ExactInterval,
    *,
    label: str,
) -> None:
    if not candidate.contains(oracle):
        raise IndependentVerificationFailure(HOLD_CONTAINMENT, f"{label} excludes oracle")


def _pi_radius_squared(radius: Fraction, precision: int) -> ExactInterval:
    return mp_mul(mp_pi(precision), mp_interval_from_fraction(radius * radius, precision)).exact()


def verify_contact_rows(
    candidate: ParsedCandidate,
    authority: GeometryAuthority,
) -> dict[str, object]:
    if not 2 * authority.radius < authority.period == 1:
        raise IndependentVerificationFailure(HOLD_CONTACT, "cut-locus condition failed")
    max_candidate_width = Fraction(0)
    max_oracle_width = Fraction(0)
    partial_count = 0
    full_count = 0
    active_count = 0
    sentinel_count = 0
    for row_index, (summary, row, axes, intervals) in enumerate(
        zip(
            candidate.manifest["rows"],
            candidate.rows,
            candidate.axes,
            candidate.contacts,
            strict=True,
        )
    ):
        _, parallel, transverse = axes
        candidate_sum = ExactInterval(Fraction(0), Fraction(0))
        oracle_sum = ExactInterval(Fraction(0), Fraction(0))
        row_active = 0
        row_full = 0
        flat = 0
        sentinel_done = False
        for x_segments, x_volume in zip(parallel.segments, parallel.volumes, strict=True):
            for y_segments, y_volume in zip(transverse.segments, transverse.volumes, strict=True):
                saved = intervals[flat]
                volume = x_volume * y_volume
                oracle, classification = contact_fraction_oracle(
                    x_segments, y_segments, volume, authority.radius
                )
                require_exact_containment(
                    saved, oracle, label=f"contact row {row_index} cell {flat}"
                )
                if saved.width > CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH:
                    raise IndependentVerificationFailure(
                        HOLD_WIDTH, "contact candidate width cap failed"
                    )
                if oracle.width > CONTACT_ORACLE_MAX_WIDTH:
                    raise IndependentVerificationFailure(
                        HOLD_WIDTH, "contact oracle width cap failed"
                    )
                if saved.width and oracle.width > saved.width * ORACLE_TO_CANDIDATE_WIDTH_RATIO_MAX:
                    raise IndependentVerificationFailure(
                        HOLD_WIDTH, "contact one-eighth width rule failed"
                    )
                if classification == "zero" and saved != ExactInterval(Fraction(0), Fraction(0)):
                    raise IndependentVerificationFailure(
                        HOLD_CONTACT, "exact zero contact cell widened"
                    )
                if classification == "full" and saved != ExactInterval(Fraction(1), Fraction(1)):
                    raise IndependentVerificationFailure(
                        HOLD_CONTACT, "exact full contact cell widened"
                    )
                if classification == "full":
                    row_full += 1
                if saved.upper > 0:
                    row_active += 1
                if classification == "partial":
                    partial_count += 1
                    if not sentinel_done:
                        sentinel, _ = contact_fraction_oracle(
                            x_segments,
                            y_segments,
                            volume,
                            authority.radius,
                            precision=SENTINEL_BITS,
                        )
                        require_exact_containment(
                            oracle, sentinel, label="384/512 contact sentinel"
                        )
                        sentinel_count += 1
                        sentinel_done = True
                max_candidate_width = max(max_candidate_width, saved.width)
                max_oracle_width = max(max_oracle_width, oracle.width)
                candidate_sum = ExactInterval(
                    candidate_sum.lower + volume * saved.lower,
                    candidate_sum.upper + volume * saved.upper,
                )
                oracle_sum = ExactInterval(
                    oracle_sum.lower + volume * oracle.lower,
                    oracle_sum.upper + volume * oracle.upper,
                )
                flat += 1
        contact_payload = row["contact_fraction_relative"]
        if (
            flat != len(intervals)
            or type(summary) is not dict
            or type(summary["active_contact_cell_count"]) is not int
            or summary["active_contact_cell_count"] != row_active
            or type(summary["full_contact_cell_count"]) is not int
            or summary["full_contact_cell_count"] != row_full
            or type(contact_payload["active_cell_count"]) is not int
            or contact_payload["active_cell_count"] != row_active
            or type(contact_payload["full_cell_count"]) is not int
            or contact_payload["full_cell_count"] != row_full
            or _parse_enclosure(contact_payload["area_enclosure_exact"], label="contact area")
            != candidate_sum
        ):
            raise IndependentVerificationFailure(HOLD_CONTACT, "contact aggregate ledger drifted")
        analytic = _pi_radius_squared(authority.radius, PRIMARY_BITS)
        require_exact_containment(candidate_sum, analytic, label=f"row {row_index} pi*r^2")
        require_exact_containment(oracle_sum, analytic, label=f"row {row_index} oracle pi*r^2")
        quality = require_keys(
            contact_payload["quality_ledger"],
            _CONTACT_QUALITY_KEYS,
            label="contact quality ledger",
        )
        recorded_analytic = _parse_enclosure(
            quality["analytic_area_enclosure_exact"], label="producer analytic area"
        )
        require_exact_containment(recorded_analytic, analytic, label="producer/independent pi*r^2")
        expected_quality = {
            "aggregate_contains_analytic_enclosure": True,
            "aggregate_width_exact": fraction_text(candidate_sum.width),
            "aggregate_width_over_radius_squared_cap_exact": "1/10000000000",
            "aggregate_width_over_radius_squared_exact": fraction_text(
                candidate_sum.width / (authority.radius * authority.radius)
            ),
            "analytic_area_enclosure_exact": quality["analytic_area_enclosure_exact"],
            "analytic_area_precision_bits": 256,
            "analytic_width_exact": fraction_text(recorded_analytic.width),
            "analytic_width_over_radius_squared_cap_exact": "1/1000000000000",
            "analytic_width_over_radius_squared_exact": fraction_text(
                recorded_analytic.width / (authority.radius * authority.radius)
            ),
            "backend": "gmpy2_mpfr_same_backend_as_producer_core",
            "independent_backend": False,
            "separately_directed_formula": "pi*radius_exact^2",
        }
        if not exact_json_equal(quality, expected_quality):
            raise IndependentVerificationFailure(HOLD_CONTACT, "contact quality ledger drifted")
        sentinel_pi = _pi_radius_squared(authority.radius, SENTINEL_BITS)
        require_exact_containment(analytic, sentinel_pi, label="384/512 pi sentinel")
        row_width_cap = (
            parallel.domain_width * transverse.domain_width * CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH
        )
        if candidate_sum.width > row_width_cap:
            raise IndependentVerificationFailure(HOLD_WIDTH, "contact weighted width cap failed")
        active_count += row_active
        full_count += row_full
    return {
        "active_cell_count": active_count,
        "full_cell_count": full_count,
        "maximum_candidate_interval_width_exact": fraction_text(max_candidate_width),
        "maximum_oracle_interval_width_exact": fraction_text(max_oracle_width),
        "partial_oracle_count": partial_count,
        "sentinel_partial_count": sentinel_count,
    }


def _bump_value_enclosure_with_tail(
    value: Fraction,
    *,
    precision: int,
) -> tuple[MPInterval, bool]:
    value = _require_coordinate_cap(value, label="bump coordinate")
    if abs(value) >= 1:
        return mp_interval_from_fraction(Fraction(0), precision), False
    exponent_magnitude = Fraction(1, 1) / (1 - value * value)
    _require_fraction_cap(
        exponent_magnitude,
        label="bump exponent",
        code=HOLD_SUPPORT,
    )
    if exponent_magnitude >= FLAT_TAIL_THRESHOLD:
        return (
            MPInterval(
                _mpfr_fraction(Fraction(0), precision, gmpy2.RoundDown),
                _mpfr_fraction(FLAT_TAIL_BUMP_UPPER, precision, gmpy2.RoundUp),
                precision,
            ),
            True,
        )
    return (
        mp_exp(mp_interval_from_fraction(-exponent_magnitude, precision)),
        False,
    )


def bump_value_enclosure(value: Fraction, *, precision: int = PRIMARY_BITS) -> MPInterval:
    return _bump_value_enclosure_with_tail(value, precision=precision)[0]


def _positive_power_exp_upper_mpq_reference(
    value: Fraction,
    power: int,
    precision: int,
) -> gmpy2.mpq:
    """Generic interval path retained as a test oracle for the upper-only path."""
    base = mp_interval_from_fraction(value, precision)
    result = mp_interval_from_fraction(Fraction(1), precision)
    for _ in range(power):
        result = mp_mul(result, base)
    exponential = mp_exp(mp_interval_from_fraction(-value, precision))
    return _support_mpfr_exact_mpq(mp_mul(result, exponential).upper)


def _positive_power_exp_uppers_mpq(
    value: Fraction,
    powers: Sequence[int],
    precision: int,
) -> dict[int, gmpy2.mpq]:
    """Directed upper bounds for positive ``value**power * exp(-value)``."""
    supplied = tuple(powers)
    if value <= 0 or not supplied or any(type(power) is not int or power < 1 for power in supplied):
        raise IndependentVerificationFailure(HOLD_API, "invalid positive power/exp request")
    requested = tuple(sorted(set(supplied)))
    base_upper = _mpfr_fraction(value, precision, gmpy2.RoundUp)
    exponent_argument_upper = _mpfr_fraction(-value, precision, gmpy2.RoundUp)
    exponential_upper = _mp_unary_value(
        exponent_argument_upper,
        precision,
        gmpy2.RoundUp,
        gmpy2.exp,
    )
    power_upper = _mp_one(precision)
    results: dict[int, gmpy2.mpq] = {}
    requested_set = set(requested)
    for power in range(1, requested[-1] + 1):
        power_upper = _mp_binary(
            power_upper,
            base_upper,
            precision,
            gmpy2.RoundUp,
            "mul",
        )
        if power in requested_set:
            results[power] = _support_mpfr_exact_mpq(
                _mp_binary(
                    power_upper,
                    exponential_upper,
                    precision,
                    gmpy2.RoundUp,
                    "mul",
                )
            )
    return results


def _positive_power_exp_upper_mpq(
    value: Fraction,
    power: int,
    precision: int,
) -> gmpy2.mpq:
    return _positive_power_exp_uppers_mpq(value, (power,), precision)[power]


def _bump_fourth_derivative_bound_mpq_reference(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> gmpy2.mpq:
    """Original generic interval computation retained only for equivalence tests."""
    lower = _require_coordinate_cap(lower, label="M4 lower coordinate")
    upper = _require_coordinate_cap(upper, label="M4 upper coordinate")
    if not -1 <= lower < upper <= 1 or lower < 0 < upper:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid Simpson derivative panel")
    near = min(abs(lower), abs(upper))
    far = max(abs(lower), abs(upper))
    s_min = Fraction(1, 1) / (1 - near * near)
    s_max: Fraction | None = None if far == 1 else Fraction(1, 1) / (1 - far * far)
    total = gmpy2.mpq(0)
    for power, coefficient in (
        (3, 24),
        (4, 300),
        (5, 672),
        (6, 624),
        (7, 192),
        (8, 16),
    ):
        maximizer = max(s_min, Fraction(power))
        if s_max is not None:
            maximizer = min(maximizer, s_max)
        total += coefficient * _positive_power_exp_upper_mpq_reference(
            maximizer,
            power,
            precision,
        )
    return total


def _bump_fourth_derivative_bound_with_tail_mpq(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> tuple[gmpy2.mpq, bool]:
    lower = _require_coordinate_cap(lower, label="M4 lower coordinate")
    upper = _require_coordinate_cap(upper, label="M4 upper coordinate")
    if not -1 <= lower < upper <= 1 or lower < 0 < upper:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid Simpson derivative panel")
    near = min(abs(lower), abs(upper))
    far = max(abs(lower), abs(upper))
    s_min = Fraction(1, 1) / (1 - near * near)
    s_max: Fraction | None = None if far == 1 else Fraction(1, 1) / (1 - far * far)
    _require_fraction_cap(s_min, label="M4 minimum exponent", code=HOLD_SUPPORT)
    if s_max is not None:
        _require_fraction_cap(s_max, label="M4 maximum exponent", code=HOLD_SUPPORT)
    if s_min >= FLAT_TAIL_THRESHOLD:
        return _fraction_exact_mpq(FLAT_TAIL_M4_UPPER), True
    grouped: dict[Fraction, list[tuple[int, int]]] = {}
    for power, coefficient in (
        (3, 24),
        (4, 300),
        (5, 672),
        (6, 624),
        (7, 192),
        (8, 16),
    ):
        maximizer = max(s_min, Fraction(power))
        if s_max is not None:
            maximizer = min(maximizer, s_max)
        grouped.setdefault(maximizer, []).append((power, coefficient))
    total = gmpy2.mpq(0)
    for maximizer, terms in grouped.items():
        powers = tuple(power for power, _ in terms)
        uppers = _positive_power_exp_uppers_mpq(maximizer, powers, precision)
        for power, coefficient in terms:
            total += coefficient * uppers[power]
    return total, False


def _bump_fourth_derivative_bound_mpq(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> gmpy2.mpq:
    return _bump_fourth_derivative_bound_with_tail_mpq(
        lower,
        upper,
        precision=precision,
    )[0]


def bump_fourth_derivative_bound(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> Fraction:
    return _mpq_exact_fraction(_bump_fourth_derivative_bound_mpq(lower, upper, precision=precision))


def _simpson_remainder_mpq(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> gmpy2.mpq:
    lower = _require_coordinate_cap(lower, label="Simpson lower coordinate")
    upper = _require_coordinate_cap(upper, label="Simpson upper coordinate")
    if not -1 <= lower < upper <= 1 or lower < 0 < upper:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid Simpson panel")
    return (
        _fraction_exact_mpq((upper - lower) ** 5)
        * _bump_fourth_derivative_bound_mpq(lower, upper, precision=precision)
        / 2880
    )


def _simpson_panel_enclosure_mpq(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> tuple[tuple[gmpy2.mpq, gmpy2.mpq], gmpy2.mpq]:
    lower = _require_coordinate_cap(lower, label="Simpson lower coordinate")
    upper = _require_coordinate_cap(upper, label="Simpson upper coordinate")
    if not -1 <= lower < upper <= 1 or lower < 0 < upper:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid Simpson panel")
    midpoint = _checked_dyadic_midpoint(lower, upper, label="Simpson midpoint")
    values = (
        bump_value_enclosure(lower, precision=precision),
        bump_value_enclosure(midpoint, precision=precision),
        bump_value_enclosure(upper, precision=precision),
    )
    weighted = mp_add(
        values[0],
        mp_add(
            _support_nonnegative_interval_mul(
                mp_interval_from_fraction(Fraction(4), precision),
                values[1],
            ),
            values[2],
        ),
    )
    estimate = _support_nonnegative_interval_mul(
        mp_interval_from_fraction((upper - lower) / 6, precision),
        weighted,
    )
    remainder = _simpson_remainder_mpq(lower, upper, precision=precision)
    return (
        (
            max(gmpy2.mpq(0), _support_mpfr_exact_mpq(estimate.lower) - remainder),
            _support_mpfr_exact_mpq(estimate.upper) + remainder,
        ),
        remainder,
    )


def simpson_panel_enclosure(
    lower: Fraction,
    upper: Fraction,
    *,
    precision: int = PRIMARY_BITS,
) -> tuple[ExactInterval, Fraction]:
    panel, remainder = _simpson_panel_enclosure_mpq(
        lower,
        upper,
        precision=precision,
    )
    return (
        ExactInterval(_mpq_exact_fraction(panel[0]), _mpq_exact_fraction(panel[1])),
        _mpq_exact_fraction(remainder),
    )


def _simpson_panel_from_samples_mpq(
    lower: Fraction,
    upper: Fraction,
    values: tuple[MPInterval, MPInterval, MPInterval],
    remainder: gmpy2.mpq,
    *,
    four: MPInterval,
    scale: MPInterval,
) -> tuple[gmpy2.mpq, gmpy2.mpq]:
    lower = _require_coordinate_cap(lower, label="Simpson lower coordinate")
    upper = _require_coordinate_cap(upper, label="Simpson upper coordinate")
    if not -1 <= lower < upper <= 1 or lower < 0 < upper:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid Simpson panel")
    precision = four.precision_bits
    if scale.precision_bits != precision or any(
        item.precision_bits != precision for item in values
    ):
        raise IndependentVerificationFailure(HOLD_API, "paired Simpson precision drifted")
    weighted = mp_add(
        values[0],
        mp_add(_support_nonnegative_interval_mul(four, values[1]), values[2]),
    )
    estimate = _support_nonnegative_interval_mul(scale, weighted)
    panel = (
        max(gmpy2.mpq(0), _support_mpfr_exact_mpq(estimate.lower) - remainder),
        _support_mpfr_exact_mpq(estimate.upper) + remainder,
    )
    for endpoint in panel:
        _require_exact_component_cap(
            endpoint.numerator,
            endpoint.denominator,
            label="Simpson panel endpoint",
            code=HOLD_SUPPORT,
        )
    return panel


def _simpson_prefilter_requires_split(
    remainder: gmpy2.mpq,
    allowance: gmpy2.mpq,
) -> bool:
    if type(remainder) is not gmpy2.mpq or type(allowance) is not gmpy2.mpq:
        raise IndependentVerificationFailure(HOLD_API, "Simpson prefilter input drifted")
    return remainder > allowance


def _exact_interval_table_sha256(
    breakpoints: tuple[Fraction, ...],
    intervals: tuple[ExactInterval, ...],
    *,
    precision: int,
) -> str:
    return digest_domain(
        b"killing-geometry-independent-bump-table-v2\0",
        {
            "breakpoints_exact": [fraction_text(value) for value in breakpoints],
            "intervals_exact": [
                {
                    "lower_exact": fraction_text(item.lower),
                    "upper_exact": fraction_text(item.upper),
                }
                for item in intervals
            ],
            "precision_bits": precision,
        },
    )


def _paired_root_local_bump_tables(
    breakpoints: tuple[Fraction, ...],
    *,
    target_width: Fraction = PRIMARY_SIMPSON_TARGET_WIDTH,
    deadline: float,
) -> tuple[BumpIntegralTable, BumpIntegralTable, dict[str, object]]:
    if len(breakpoints) < 2 or any(
        lower >= upper for lower, upper in zip(breakpoints, breakpoints[1:])
    ):
        raise IndependentVerificationFailure(HOLD_SUPPORT, "invalid shared bump breakpoints")
    if len(breakpoints) > MAX_BUMP_BREAKPOINTS:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "bump breakpoint cap exceeded")
    for value in breakpoints:
        _require_coordinate_cap(value, label="shared bump breakpoint")
    target_mpq = _fraction_exact_mpq(target_width)
    metrics: dict[str, object] = {
        "accepted_leaf_count": 0,
        "all_leaf_panels_nested": True,
        "all_root_m4_nested": True,
        "all_samples_nested": True,
        "estimate_split_count": 0,
        "leaf_panel_nesting_count": 0,
        "maximum_dfs_stack": 0,
        "maximum_dyadic_depth": 0,
        "maximum_exact_component_bits": 0,
        "maximum_coordinate_component_bits": max(
            max(value.numerator.bit_length(), value.denominator.bit_length())
            for value in breakpoints
        ),
        "maximum_primary_scale_cache_entries": 0,
        "maximum_sentinel_scale_cache_entries": 0,
        "paired_sample_count": 0,
        "prefilter_split_count": 0,
        "primary_estimate_count": 0,
        "primary_flat_tail_sample_count": 0,
        "primary_flat_tail_root_count": 0,
        "primary_sample_count": 0,
        "root_m4_nesting_count": 0,
        "sample_nesting_count": 0,
        "sentinel_estimate_count": 0,
        "sentinel_flat_tail_sample_count": 0,
        "sentinel_flat_tail_root_count": 0,
        "sentinel_sample_count": 0,
        "tree_panel_count": 0,
    }

    def increment(name: str, amount: int = 1) -> None:
        current = metrics[name]
        if type(current) is not int:
            raise IndependentVerificationFailure(HOLD_API, "paired metric type drifted")
        metrics[name] = current + amount

    def observe_exact(*values: gmpy2.mpq) -> None:
        maximum = int(metrics["maximum_exact_component_bits"])
        for value in values:
            _require_exact_component_cap(
                value.numerator,
                value.denominator,
                label="paired Simpson exact value",
                code=HOLD_SUPPORT,
            )
            maximum = max(
                maximum,
                value.numerator.bit_length(),
                value.denominator.bit_length(),
            )
        metrics["maximum_exact_component_bits"] = maximum

    def observe_fraction(*values: Fraction) -> None:
        maximum = int(metrics["maximum_exact_component_bits"])
        for value in values:
            _require_fraction_cap(value, label="paired Simpson exact Fraction", code=HOLD_SUPPORT)
            maximum = max(
                maximum,
                value.numerator.bit_length(),
                value.denominator.bit_length(),
            )
        metrics["maximum_exact_component_bits"] = maximum

    def observe_coordinate(value: Fraction) -> None:
        _require_coordinate_cap(value, label="paired Simpson sampled coordinate")
        metrics["maximum_coordinate_component_bits"] = max(
            int(metrics["maximum_coordinate_component_bits"]),
            value.numerator.bit_length(),
            value.denominator.bit_length(),
        )

    def check_deadline() -> None:
        if time.monotonic() > deadline:
            raise IndependentVerificationFailure(HOLD_TIMEOUT, "support Simpson deadline exceeded")

    root_m4_primary: list[gmpy2.mpq] = []
    root_m4_sentinel: list[gmpy2.mpq] = []
    for lower, upper in zip(breakpoints, breakpoints[1:]):
        check_deadline()
        primary, primary_tail = _bump_fourth_derivative_bound_with_tail_mpq(
            lower,
            upper,
            precision=PRIMARY_BITS,
        )
        check_deadline()
        sentinel, sentinel_tail = _bump_fourth_derivative_bound_with_tail_mpq(
            lower,
            upper,
            precision=SENTINEL_BITS,
        )
        check_deadline()
        if sentinel > primary:
            raise IndependentVerificationFailure(HOLD_CONTAINMENT, "512-bit root M4 escaped 384")
        observe_exact(primary, sentinel)
        increment("root_m4_nesting_count")
        root_m4_primary.append(primary)
        root_m4_sentinel.append(sentinel)
        increment("primary_flat_tail_root_count", int(primary_tail))
        increment("sentinel_flat_tail_root_count", int(sentinel_tail))

    segment_count = len(breakpoints) - 1
    primary_lower = [gmpy2.mpq(0) for _ in range(segment_count)]
    primary_upper = [gmpy2.mpq(0) for _ in range(segment_count)]
    sentinel_lower = [gmpy2.mpq(0) for _ in range(segment_count)]
    sentinel_upper = [gmpy2.mpq(0) for _ in range(segment_count)]
    four_primary = mp_interval_from_fraction(Fraction(4), PRIMARY_BITS)
    four_sentinel = mp_interval_from_fraction(Fraction(4), SENTINEL_BITS)
    leaf_hasher = hashlib.sha256(b"killing-geometry-independent-left-first-leaves-v2\0")

    def sample_pair(value: Fraction) -> tuple[MPInterval, MPInterval]:
        observe_coordinate(value)
        primary, primary_tail = _bump_value_enclosure_with_tail(
            value,
            precision=PRIMARY_BITS,
        )
        sentinel, sentinel_tail = _bump_value_enclosure_with_tail(
            value,
            precision=SENTINEL_BITS,
        )
        increment("paired_sample_count")
        increment("primary_sample_count")
        increment("sentinel_sample_count")
        increment("primary_flat_tail_sample_count", int(primary_tail))
        increment("sentinel_flat_tail_sample_count", int(sentinel_tail))
        if primary.lower > sentinel.lower or sentinel.upper > primary.upper:
            raise IndependentVerificationFailure(
                HOLD_CONTAINMENT, "512-bit bump sample escaped 384"
            )
        increment("sample_nesting_count")
        return primary, sentinel

    for segment, (root_lower, root_upper, primary_m4, sentinel_m4) in enumerate(
        zip(
            breakpoints[:-1],
            breakpoints[1:],
            root_m4_primary,
            root_m4_sentinel,
            strict=True,
        )
    ):
        check_deadline()
        root_width = root_upper - root_lower
        primary_remainders = {0: _fraction_exact_mpq(root_width**5) * primary_m4 / 2880}
        sentinel_remainders = {0: _fraction_exact_mpq(root_width**5) * sentinel_m4 / 2880}
        observe_exact(primary_remainders[0], sentinel_remainders[0])
        allowances = {0: target_mpq}
        primary_scales = {0: mp_interval_from_fraction(root_width / 6, PRIMARY_BITS)}
        sentinel_scales = {0: mp_interval_from_fraction(root_width / 6, SENTINEL_BITS)}
        bins: list[tuple[gmpy2.mpq, gmpy2.mpq, gmpy2.mpq, gmpy2.mpq] | None] = []

        def accept(
            primary_panel: tuple[gmpy2.mpq, gmpy2.mpq],
            sentinel_panel: tuple[gmpy2.mpq, gmpy2.mpq],
        ) -> None:
            carry = (*primary_panel, *sentinel_panel)
            observe_exact(*carry)
            level = 0
            while level < len(bins) and bins[level] is not None:
                present = bins[level]
                assert present is not None
                carry = tuple(present[index] + carry[index] for index in range(4))  # type: ignore[assignment]
                observe_exact(*carry)
                bins[level] = None
                level += 1
            if level == len(bins):
                bins.append(carry)
            else:
                bins[level] = carry

        midpoint = _checked_dyadic_midpoint(
            root_lower,
            root_upper,
            label="root Simpson midpoint",
        )
        root_values = (
            sample_pair(root_lower),
            sample_pair(midpoint),
            sample_pair(root_upper),
        )
        # (depth, dyadic index, lower, upper, three paired samples).  Push the
        # right child first so the next pop executes the left child.
        stack: list[
            tuple[int, int, Fraction, Fraction, tuple[tuple[MPInterval, MPInterval], ...]]
        ] = [(0, 0, root_lower, root_upper, root_values)]
        increment("tree_panel_count")
        metrics["maximum_dfs_stack"] = max(int(metrics["maximum_dfs_stack"]), len(stack))
        while stack:
            check_deadline()
            depth, index, lower, upper, values = stack.pop()
            metrics["maximum_dyadic_depth"] = max(int(metrics["maximum_dyadic_depth"]), depth)
            allowance = allowances[depth]
            remainder_primary = primary_remainders[depth]
            split = _simpson_prefilter_requires_split(remainder_primary, allowance)
            if split:
                increment("prefilter_split_count")
            else:
                primary_panel = _simpson_panel_from_samples_mpq(
                    lower,
                    upper,
                    tuple(item[0] for item in values),  # type: ignore[arg-type]
                    remainder_primary,
                    four=four_primary,
                    scale=primary_scales[depth],
                )
                increment("primary_estimate_count")
                if primary_panel[1] - primary_panel[0] <= allowance:
                    sentinel_panel = _simpson_panel_from_samples_mpq(
                        lower,
                        upper,
                        tuple(item[1] for item in values),  # type: ignore[arg-type]
                        sentinel_remainders[depth],
                        four=four_sentinel,
                        scale=sentinel_scales[depth],
                    )
                    increment("sentinel_estimate_count")
                    if primary_panel[0] > sentinel_panel[0] or sentinel_panel[1] > primary_panel[1]:
                        raise IndependentVerificationFailure(
                            HOLD_CONTAINMENT,
                            "512-bit accepted leaf escaped 384",
                        )
                    observe_exact(*primary_panel, *sentinel_panel)
                    increment("leaf_panel_nesting_count")
                    accept(primary_panel, sentinel_panel)
                    increment("accepted_leaf_count")
                    leaf_hasher.update(f"{segment}:{depth}:{index}\n".encode("ascii"))
                    continue
                increment("estimate_split_count")
                split = True
            if not split:
                raise IndependentVerificationFailure(HOLD_API, "paired DFS decision drifted")
            child_depth = depth + 1
            if child_depth > MAX_SIMPSON_DYADIC_DEPTH:
                raise IndependentVerificationFailure(
                    HOLD_SUPPORT, "support Simpson dyadic-depth cap exceeded"
                )
            if int(metrics["tree_panel_count"]) + 2 > MAX_SIMPSON_PANELS:
                raise IndependentVerificationFailure(
                    HOLD_SUPPORT, "support Simpson panel cap exceeded"
                )
            if len(stack) + 2 > MAX_SIMPSON_DFS_STACK:
                raise IndependentVerificationFailure(
                    HOLD_SUPPORT, "support Simpson DFS stack cap exceeded"
                )
            if child_depth not in allowances:
                allowances[child_depth] = target_mpq / (1 << child_depth)
                primary_remainders[child_depth] = remainder_primary / 32
                sentinel_remainders[child_depth] = sentinel_remainders[depth] / 32
                observe_exact(
                    primary_remainders[child_depth],
                    sentinel_remainders[child_depth],
                )
                child_width = root_width / (1 << child_depth)
                primary_scales[child_depth] = mp_interval_from_fraction(
                    child_width / 6,
                    PRIMARY_BITS,
                )
                sentinel_scales[child_depth] = mp_interval_from_fraction(
                    child_width / 6,
                    SENTINEL_BITS,
                )
            midpoint = _checked_dyadic_midpoint(lower, upper, label="child midpoint")
            quarter = _checked_dyadic_midpoint(lower, midpoint, label="left quarter")
            three_quarter = _checked_dyadic_midpoint(
                midpoint,
                upper,
                label="right quarter",
            )
            left_values = (values[0], sample_pair(quarter), values[1])
            right_values = (values[1], sample_pair(three_quarter), values[2])
            stack.append((child_depth, 2 * index + 1, midpoint, upper, right_values))
            stack.append((child_depth, 2 * index, lower, midpoint, left_values))
            increment("tree_panel_count", 2)
            metrics["maximum_dfs_stack"] = max(int(metrics["maximum_dfs_stack"]), len(stack))
        metrics["maximum_primary_scale_cache_entries"] = max(
            int(metrics["maximum_primary_scale_cache_entries"]), len(primary_scales)
        )
        metrics["maximum_sentinel_scale_cache_entries"] = max(
            int(metrics["maximum_sentinel_scale_cache_entries"]), len(sentinel_scales)
        )
        for quad in bins:
            if quad is not None:
                primary_lower[segment] += quad[0]
                primary_upper[segment] += quad[1]
                sentinel_lower[segment] += quad[2]
                sentinel_upper[segment] += quad[3]
                observe_exact(
                    primary_lower[segment],
                    primary_upper[segment],
                    sentinel_lower[segment],
                    sentinel_upper[segment],
                )

    primary_intervals = tuple(
        ExactInterval(_mpq_exact_fraction(lower), _mpq_exact_fraction(upper))
        for lower, upper in zip(primary_lower, primary_upper, strict=True)
    )
    sentinel_intervals = tuple(
        ExactInterval(_mpq_exact_fraction(lower), _mpq_exact_fraction(upper))
        for lower, upper in zip(sentinel_lower, sentinel_upper, strict=True)
    )
    if any(item.width > target_width for item in primary_intervals):
        raise IndependentVerificationFailure(HOLD_SUPPORT, "support Simpson width invariant failed")
    table_nesting_count = 0
    for primary, sentinel in zip(primary_intervals, sentinel_intervals, strict=True):
        require_exact_containment(primary, sentinel, label="paired 384/512 bump table")
        table_nesting_count += 1
    primary_normalizer = ExactInterval(
        sum((item.lower for item in primary_intervals), Fraction(0)),
        sum((item.upper for item in primary_intervals), Fraction(0)),
    )
    sentinel_normalizer = ExactInterval(
        sum((item.lower for item in sentinel_intervals), Fraction(0)),
        sum((item.upper for item in sentinel_intervals), Fraction(0)),
    )
    observe_fraction(
        primary_normalizer.lower,
        primary_normalizer.upper,
        sentinel_normalizer.lower,
        sentinel_normalizer.upper,
    )
    require_exact_containment(
        primary_normalizer,
        sentinel_normalizer,
        label="paired 384/512 bump normalizer",
    )
    panel_count = int(metrics["tree_panel_count"])
    accepted_count = int(metrics["accepted_leaf_count"])
    maximum_depth = int(metrics["maximum_dyadic_depth"])
    maximum_stack = int(metrics["maximum_dfs_stack"])
    primary_table = BumpIntegralTable(
        PRIMARY_BITS,
        breakpoints,
        primary_intervals,
        primary_normalizer,
        panel_count,
        accepted_count,
        maximum_depth,
        maximum_stack,
    )
    sentinel_table = BumpIntegralTable(
        SENTINEL_BITS,
        breakpoints,
        sentinel_intervals,
        sentinel_normalizer,
        panel_count,
        accepted_count,
        maximum_depth,
        maximum_stack,
    )
    metrics.update(
        {
            "accepted_leaf_partition_sha256": leaf_hasher.hexdigest(),
            "normalizer_nested": True,
            "primary_table_sha256": _exact_interval_table_sha256(
                breakpoints,
                primary_intervals,
                precision=PRIMARY_BITS,
            ),
            "sentinel_table_sha256": _exact_interval_table_sha256(
                breakpoints,
                sentinel_intervals,
                precision=SENTINEL_BITS,
            ),
            "table_nesting_count": table_nesting_count,
        }
    )
    return primary_table, sentinel_table, metrics


def _support_breakpoints(
    candidate: ParsedCandidate,
    authority: GeometryAuthority,
) -> tuple[Fraction, ...]:
    points = {Fraction(-1), Fraction(0), Fraction(1)}
    for axes in candidate.axes:
        midpoint = axes[0]
        for cell in midpoint.segments:
            if len(cell) != 1:
                raise IndependentVerificationFailure(
                    HOLD_SUPPORT, "midpoint cell unexpectedly wraps"
                )
            lower, upper = cell[0]
            for centre in authority.centres:
                transformed = (
                    (lower - centre) / authority.half_width,
                    (upper - centre) / authority.half_width,
                )
                for value in transformed:
                    points.add(
                        _require_coordinate_cap(
                            max(Fraction(-1), min(Fraction(1), value)),
                            label="transformed support breakpoint",
                        )
                    )
    ordered = tuple(sorted(points))
    if len(ordered) > MAX_BUMP_BREAKPOINTS:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "bump breakpoint cap exceeded")
    return ordered


def _verify_support_policy_digests() -> None:
    checks = (
        (
            digest_domain(
                b"killing-geometry-independent-paired-simpson-policy-v2\0",
                PAIRED_SIMPSON_POLICY,
            ),
            PAIRED_SIMPSON_POLICY_SHA256,
        ),
        (
            digest_domain(
                b"killing-geometry-independent-flat-tail-policy-v1\0",
                FLAT_TAIL_POLICY,
            ),
            FLAT_TAIL_POLICY_SHA256,
        ),
        (
            digest_domain(
                b"killing-geometry-independent-flat-tail-bump-upper-v1\0",
                {"upper_exact": fraction_text(FLAT_TAIL_BUMP_UPPER)},
            ),
            FLAT_TAIL_BUMP_UPPER_SHA256,
        ),
        (
            digest_domain(
                b"killing-geometry-independent-flat-tail-M4-upper-v1\0",
                {"upper_exact": fraction_text(FLAT_TAIL_M4_UPPER)},
            ),
            FLAT_TAIL_M4_UPPER_SHA256,
        ),
    )
    if any(observed != expected for observed, expected in checks):
        raise IndependentVerificationFailure(HOLD_SOURCE, "support policy digest drifted")


def build_paired_shared_bump_integral_tables(
    candidate: ParsedCandidate,
    authority: GeometryAuthority,
    *,
    deadline: float | None = None,
) -> tuple[BumpIntegralTable, BumpIntegralTable, dict[str, object]]:
    _verify_support_policy_digests()
    end_time = time.monotonic() + RUN_DEADLINE_SECONDS if deadline is None else deadline
    breakpoints = _support_breakpoints(candidate, authority)
    tables = _paired_root_local_bump_tables(
        breakpoints,
        target_width=PRIMARY_SIMPSON_TARGET_WIDTH,
        deadline=end_time,
    )
    if (
        tables[0].breakpoints[0] != -1
        or tables[0].breakpoints[-1] != 1
        or bump_value_enclosure(Fraction(1, 2), precision=PRIMARY_BITS).exact().lower
        <= Fraction(1, 4)
        or tables[0].normalizer.lower <= Fraction(1, 4)
    ):
        raise IndependentVerificationFailure(HOLD_NORMALIZATION, "bump normalizer lower failed")
    return tables


def support_average_oracle(
    cell: tuple[tuple[Fraction, Fraction], ...],
    cell_volume: Fraction,
    centre: Fraction,
    half_width: Fraction,
    table: BumpIntegralTable,
) -> ExactInterval:
    if len(cell) != 1:
        raise IndependentVerificationFailure(HOLD_SUPPORT, "midpoint support cell wraps")
    lower, upper = cell[0]
    transformed_lower = max(Fraction(-1), (lower - centre) / half_width)
    transformed_upper = min(Fraction(1), (upper - centre) / half_width)
    if transformed_lower >= transformed_upper:
        return ExactInterval(Fraction(0), Fraction(0))
    numerator = table.integral(transformed_lower, transformed_upper)
    if table.normalizer.lower <= 0:
        raise IndependentVerificationFailure(HOLD_NORMALIZATION, "normalizer is nonpositive")
    return ExactInterval(
        numerator.lower / (cell_volume * table.normalizer.upper),
        numerator.upper / (cell_volume * table.normalizer.lower),
    )


def verify_support_rows(
    candidate: ParsedCandidate,
    authority: GeometryAuthority,
    *,
    deadline: float | None = None,
) -> tuple[dict[str, object], BumpIntegralTable]:
    end_time = time.monotonic() + RUN_DEADLINE_SECONDS if deadline is None else deadline
    table, sentinel_table, paired_metrics = build_paired_shared_bump_integral_tables(
        candidate,
        authority,
        deadline=end_time,
    )
    if paired_metrics["accepted_leaf_partition_sha256"] != (
        EXPECTED_ACCEPTED_LEAF_PARTITION_SHA256
    ):
        raise IndependentVerificationFailure(
            HOLD_SUPPORT,
            "accepted production leaf partition drifted",
        )
    maximum_candidate_mass_width = Fraction(0)
    maximum_oracle_mass_width = Fraction(0)
    maximum_sentinel_mass_width = Fraction(0)
    nonzero_oracle_cells = 0
    sentinel_cells = 0
    for row_index, (row, axes, support_profiles) in enumerate(
        zip(candidate.rows, candidate.axes, candidate.supports, strict=True)
    ):
        midpoint = axes[0]
        if any(
            not midpoint.domain_start
            < centre - authority.half_width
            < centre + authority.half_width
            < midpoint.domain_start + midpoint.domain_width
            for centre in authority.centres
        ):
            raise IndependentVerificationFailure(HOLD_SUPPORT, "support is not strictly in domain")
        support_payloads = row["support_densities"]
        for profile_index, (saved_profile, centre, support_payload) in enumerate(
            zip(support_profiles, authority.centres, support_payloads, strict=True)
        ):
            candidate_sum = ExactInterval(Fraction(0), Fraction(0))
            oracle_sum = ExactInterval(Fraction(0), Fraction(0))
            sentinel_sum = ExactInterval(Fraction(0), Fraction(0))
            for cell_index, (saved, cell, volume) in enumerate(
                zip(saved_profile, midpoint.segments, midpoint.volumes, strict=True)
            ):
                oracle = support_average_oracle(cell, volume, centre, authority.half_width, table)
                sentinel = support_average_oracle(
                    cell,
                    volume,
                    centre,
                    authority.half_width,
                    sentinel_table,
                )
                require_exact_containment(
                    saved,
                    oracle,
                    label=f"support row {row_index} profile {profile_index} cell {cell_index}",
                )
                require_exact_containment(
                    oracle,
                    sentinel,
                    label=f"paired support row {row_index} profile {profile_index} cell {cell_index}",
                )
                require_exact_containment(
                    saved,
                    sentinel,
                    label=(
                        f"producer/sentinel row {row_index} profile {profile_index} "
                        f"cell {cell_index}"
                    ),
                )
                sentinel_cells += 1
                candidate_mass_width = volume * saved.width
                oracle_mass_width = volume * oracle.width
                sentinel_mass_width = volume * sentinel.width
                if candidate_mass_width > SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH:
                    raise IndependentVerificationFailure(
                        HOLD_WIDTH, "support cell-mass width failed"
                    )
                if saved.width and oracle_mass_width > (
                    candidate_mass_width * ORACLE_TO_CANDIDATE_WIDTH_RATIO_MAX
                ):
                    raise IndependentVerificationFailure(
                        HOLD_WIDTH, "support one-eighth width failed"
                    )
                if oracle == ExactInterval(Fraction(0), Fraction(0)):
                    if saved != oracle:
                        raise IndependentVerificationFailure(
                            HOLD_SUPPORT, "outside-support cell widened"
                        )
                else:
                    nonzero_oracle_cells += 1
                maximum_candidate_mass_width = max(
                    maximum_candidate_mass_width, candidate_mass_width
                )
                maximum_oracle_mass_width = max(maximum_oracle_mass_width, oracle_mass_width)
                maximum_sentinel_mass_width = max(
                    maximum_sentinel_mass_width,
                    sentinel_mass_width,
                )
                candidate_sum = ExactInterval(
                    candidate_sum.lower + volume * saved.lower,
                    candidate_sum.upper + volume * saved.upper,
                )
                oracle_sum = ExactInterval(
                    oracle_sum.lower + volume * oracle.lower,
                    oracle_sum.upper + volume * oracle.upper,
                )
                sentinel_sum = ExactInterval(
                    sentinel_sum.lower + volume * sentinel.lower,
                    sentinel_sum.upper + volume * sentinel.upper,
                )
            recorded = _parse_enclosure(
                support_payload["integral_enclosure_exact"], label="support integral"
            )
            if recorded != candidate_sum:
                raise IndependentVerificationFailure(
                    HOLD_SUPPORT, "support integral ledger drifted"
                )
            quality = require_keys(
                support_payload["quality_ledger"],
                _SUPPORT_QUALITY_KEYS,
                label="support quality ledger",
            )
            support_lower = centre - authority.half_width
            support_upper = centre + authority.half_width
            expected_quality = {
                "analytic_mass_exact": "1/1",
                "integral_width_cap_exact": "1/10000000000",
                "integral_width_exact": fraction_text(candidate_sum.width),
                "midpoint_domain_lower_exact": fraction_text(midpoint.domain_start),
                "midpoint_domain_upper_exact": fraction_text(
                    midpoint.domain_start + midpoint.domain_width
                ),
                "support_lower_exact": fraction_text(support_lower),
                "support_strictly_inside_midpoint_domain": True,
                "support_upper_exact": fraction_text(support_upper),
            }
            if not exact_json_equal(quality, expected_quality):
                raise IndependentVerificationFailure(HOLD_SUPPORT, "support quality ledger drifted")
            unit = ExactInterval(Fraction(1), Fraction(1))
            require_exact_containment(candidate_sum, unit, label="candidate support unit mass")
            require_exact_containment(oracle_sum, unit, label="oracle support unit mass")
            require_exact_containment(sentinel_sum, unit, label="sentinel support unit mass")
            require_exact_containment(oracle_sum, sentinel_sum, label="paired support profile sum")
            if candidate_sum.width > SUPPORT_AGGREGATE_WIDTH_CAP:
                raise IndependentVerificationFailure(HOLD_WIDTH, "support aggregate width failed")
    return (
        {
            "breakpoint_count": len(table.breakpoints),
            "maximum_candidate_cell_mass_width_exact": fraction_text(maximum_candidate_mass_width),
            "maximum_oracle_cell_mass_width_exact": fraction_text(maximum_oracle_mass_width),
            "maximum_sentinel_cell_mass_width_exact": fraction_text(maximum_sentinel_mass_width),
            "nonzero_oracle_cell_count": nonzero_oracle_cells,
            "sentinel_support_cell_count": sentinel_cells,
            "paired_simpson_metrics": paired_metrics,
            "paired_simpson_policy": {
                "exact_component_bit_cap": MAX_SIMPSON_EXACT_COMPONENT_BITS,
                "flat_tail_bump_upper_sha256": FLAT_TAIL_BUMP_UPPER_SHA256,
                "flat_tail_M4_upper_sha256": FLAT_TAIL_M4_UPPER_SHA256,
                "flat_tail_policy_sha256": FLAT_TAIL_POLICY_SHA256,
                "operation_model_sha256": OPERATION_MODEL_SHA256,
                "paired_simpson_policy_sha256": PAIRED_SIMPSON_POLICY_SHA256,
                "sentinel_role": "containment_only_same_primary_accepted_leaves",
            },
            "normalizer_enclosure_exact": {
                "lower_exact": fraction_text(table.normalizer.lower),
                "upper_exact": fraction_text(table.normalizer.upper),
            },
            "sentinel_normalizer_enclosure_exact": {
                "lower_exact": fraction_text(sentinel_table.normalizer.lower),
                "upper_exact": fraction_text(sentinel_table.normalizer.upper),
            },
        },
        table,
    )


def _runtime_versions() -> dict[str, str]:
    return {
        "gmp": gmpy2.mp_version().removeprefix("GMP "),
        "gmpy2": gmpy2.version(),
        "mpc": gmpy2.mpc_version().removeprefix("MPC "),
        "mpfr": gmpy2.mpfr_version().removeprefix("MPFR "),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def _semantic_flags() -> dict[str, object]:
    return {
        "candidate_width_caps_passed": True,
        "concrete_killing_constructed": False,
        "contact_pi_r_squared_enclosed_all_rows": True,
        "continuum_verified": False,
        "directed_mpfr_contact_oracle": True,
        "f0_core_imported": False,
        "f0_pass": False,
        "f1_authorized": False,
        "full_operator_bound": False,
        "independent_backend": False,
        "independent_simpson_remainder_source": True,
        "flat_tail_bound_active": True,
        "initial_stream_imported": False,
        "installed_budget_used": False,
        "killing_geometry_bound": True,
        "largest_state_tensor_allocated": False,
        "partitions_reconstructed_from_control_free_config": True,
        "outer_staged_source_pre_post_required": True,
        "positive_budget_executed": False,
        "producer_envelopes_contain_independent_oracles": True,
        "producer_module_imported": False,
        "production_resource_gate": False,
        "propagation_executed": False,
        "prospective_control_used": False,
        "prr_release_authorized": False,
        "resource_promotion_eligible": False,
        "science_executed": False,
        "separate_source_implementation": True,
        "shared_simpson_remainder_lemma": True,
        "paired_same_leaf_precision_sentinel": True,
        "sentinel_independent_2^-68_adaptive": False,
        "single_physical_operator_bound": False,
        "support_unit_integral_enclosed_all_rows_profiles": True,
        "topology_complete": False,
        "verifier_executed_source_attested": False,
    }


def _build_semantic_receipt(
    candidate: ParsedCandidate,
    contact_summary: dict[str, object],
    support_summary: dict[str, object],
) -> dict[str, object]:
    assert_import_boundary()
    verifier_bytes = read_regular_stable(Path(__file__), maximum_bytes=MAX_JSON_FILE_BYTES)
    receipt = {
        "candidate": {
            "bundle_sha256": CANDIDATE_BUNDLE_SHA256,
            "family_relation_sha256": candidate.manifest["family_relation_sha256"],
            "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
            "partition_reference_graph_sha256": candidate.manifest[
                "partition_reference_graph_sha256"
            ],
            "tree_sha256": candidate.tree.digest,
        },
        "contact_summary": contact_summary,
        "flags": _semantic_flags(),
        "frozen_sources": {
            "authority_sha256": AUTHORITY_SHA256,
            "configuration_sha256": CONFIGURATION_SHA256,
            "design_sha256": DESIGN_SHA256,
            "f0_core_sha256": F0_CORE_SHA256,
            "initial_stream_source_sha256": INITIAL_STREAM_SOURCE_SHA256,
            "operation_model_sha256": OPERATION_MODEL_SHA256,
            "partition_bundle_sha256": PARTITION_BUNDLE_SHA256,
            "partition_tree_sha256": candidate.partition_tree.digest,
            "producer_sha256": PRODUCER_SHA256,
            "producer_test_sha256": PRODUCER_TEST_SHA256,
        },
        "independent_partition_semantic_sha256s": [
            list(row) for row in candidate.independent_partition_sha256s
        ],
        "precision_bits": {"primary": PRIMARY_BITS, "sentinel": SENTINEL_BITS},
        "runtime": _runtime_versions(),
        "schema": CHILD_SEMANTIC_SUCCESS_SCHEMA,
        "status": PASS_STATUS,
        "support_policy_digests": {
            "flat_tail_bump_upper_sha256": FLAT_TAIL_BUMP_UPPER_SHA256,
            "flat_tail_M4_upper_sha256": FLAT_TAIL_M4_UPPER_SHA256,
            "flat_tail_policy_sha256": FLAT_TAIL_POLICY_SHA256,
            "paired_simpson_policy_sha256": PAIRED_SIMPSON_POLICY_SHA256,
        },
        "support_summary": support_summary,
        "verifier_staged_file_sha256_at_receipt": sha256_bytes(verifier_bytes),
    }
    encoded = canonical_json_bytes(receipt)
    if len(encoded) > MAX_RECEIPT_BYTES:
        raise IndependentVerificationFailure(HOLD_API, "semantic receipt cap exceeded")
    assert_import_boundary()
    return receipt


def verify_semantic_core(report_root: Path, bundle_root: Path) -> dict[str, object]:
    assert_import_boundary()
    started = time.monotonic()
    deadline = started + RUN_DEADLINE_SECONDS
    candidate = parse_candidate_bundle(report_root, bundle_root)
    if time.monotonic() > deadline:
        raise IndependentVerificationFailure(HOLD_TIMEOUT, "semantic core deadline exceeded")
    authority = load_frozen_geometry_authority(report_root.resolve())
    verify_exact_file(report_root.resolve(), OPERATION_MODEL_PATH, OPERATION_MODEL_SHA256)
    contact_summary = verify_contact_rows(candidate, authority)
    if time.monotonic() > deadline:
        raise IndependentVerificationFailure(HOLD_TIMEOUT, "semantic core deadline exceeded")
    candidate = replace(candidate, contacts=())
    gc.collect()
    support_summary, _ = verify_support_rows(candidate, authority, deadline=deadline)
    if time.monotonic() > deadline:
        raise IndependentVerificationFailure(HOLD_TIMEOUT, "semantic core deadline exceeded")
    ending_candidate_tree = inventory_candidate_tree(bundle_root)
    if ending_candidate_tree != candidate.tree:
        raise IndependentVerificationFailure(
            HOLD_TREE, "candidate tree changed across verification"
        )
    verified_report_root = _validated_root_directory(
        report_root,
        code=HOLD_TREE,
        label="report",
    )
    ending_partition_tree = inventory_candidate_tree(verified_report_root / PARTITION_ROOT_PATH)
    if ending_partition_tree != candidate.partition_tree:
        raise IndependentVerificationFailure(
            HOLD_PARTITION, "accepted partition tree changed across verification"
        )
    assert_import_boundary()
    return _build_semantic_receipt(candidate, contact_summary, support_summary)


def _hold_receipt(code: str) -> dict[str, object]:
    if code not in _HOLD_STATUSES:
        code = HOLD_API
    return {
        "schema": CHILD_SEMANTIC_HOLD_SCHEMA,
        "status": code,
    }


def _unbound_hold_ack() -> dict[str, object]:
    return {
        "schema": CHILD_UNBOUND_HOLD_ACK_SCHEMA,
        "status": HOLD_API,
    }


def _require_absolute_directory(value: str, *, label: str) -> Path:
    if type(value) is not str or not value or "\0" in value:
        raise IndependentVerificationFailure(HOLD_API, f"invalid {label} path")
    path = Path(value)
    if not path.is_absolute():
        raise IndependentVerificationFailure(HOLD_API, f"{label} path is not absolute")
    return _validated_root_directory(path, code=HOLD_API, label=label)


def _require_absent_output_path(value: str, *, label: str) -> Path:
    if type(value) is not str or not value or "\0" in value:
        raise IndependentVerificationFailure(HOLD_API, f"invalid {label} path")
    path = Path(value)
    if not path.is_absolute() or not path.name:
        raise IndependentVerificationFailure(HOLD_API, f"{label} path is not absolute")
    parent = _validated_root_directory(path.parent, code=HOLD_API, label=f"{label} parent")
    resolved = parent / path.name
    try:
        resolved.lstat()
    except FileNotFoundError:
        return resolved
    except OSError as error:
        raise IndependentVerificationFailure(HOLD_API, f"cannot inspect {label} path") from error
    raise IndependentVerificationFailure(HOLD_API, f"{label} path already exists")


def _path_is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _parse_cli(argv: Sequence[str]) -> ChildWireArguments:
    if len(argv) != 12:
        raise IndependentVerificationFailure(HOLD_API, "expected six named arguments")
    arguments: dict[str, str] = {}
    for index in range(0, len(argv), 2):
        name, value = argv[index : index + 2]
        if (
            type(name) is not str
            or type(value) is not str
            or name
            not in {
                "--report-root",
                "--bundle",
                "--semantic-receipt",
                "--observation",
                "--launch-nonce",
                "--run-index",
            }
            or name in arguments
            or not value
        ):
            raise IndependentVerificationFailure(HOLD_API, "invalid named argument")
        arguments[name] = value
    if set(arguments) != {
        "--report-root",
        "--bundle",
        "--semantic-receipt",
        "--observation",
        "--launch-nonce",
        "--run-index",
    }:
        raise IndependentVerificationFailure(HOLD_API, "missing named argument")
    launch_nonce = arguments["--launch-nonce"]
    run_index_text = arguments["--run-index"]
    if _LAUNCH_NONCE_RE.fullmatch(launch_nonce) is None:
        raise IndependentVerificationFailure(HOLD_API, "launch nonce is not 64 lower hex")
    if run_index_text not in {"0", "1"}:
        raise IndependentVerificationFailure(HOLD_API, "run index is not zero or one")
    report_root = _require_absolute_directory(arguments["--report-root"], label="report")
    bundle_root = _require_absolute_directory(arguments["--bundle"], label="bundle")
    semantic_path = _require_absent_output_path(
        arguments["--semantic-receipt"], label="semantic receipt"
    )
    observation_path = _require_absent_output_path(arguments["--observation"], label="observation")
    if semantic_path == observation_path:
        raise IndependentVerificationFailure(HOLD_API, "output paths are not distinct")
    if any(
        _path_is_within(output, input_root)
        for output in (semantic_path, observation_path)
        for input_root in (report_root, bundle_root)
    ):
        raise IndependentVerificationFailure(HOLD_API, "output path is within an input root")
    return ChildWireArguments(
        report_root=report_root,
        bundle_root=bundle_root,
        semantic_receipt_path=semantic_path,
        observation_path=observation_path,
        launch_nonce=launch_nonce,
        run_index=int(run_index_text),
    )


def _directory_link_identity(item: os.stat_result) -> tuple[int, int, int, int]:
    return item.st_dev, item.st_ino, item.st_mode, item.st_nlink


def _publish_exclusive_stable(path: Path, payload: bytes, *, maximum_bytes: int) -> bytes:
    if type(payload) is not bytes or type(maximum_bytes) is not int or maximum_bytes < 0:
        raise IndependentVerificationFailure(HOLD_API, "invalid publication request")
    if len(payload) > maximum_bytes:
        raise IndependentVerificationFailure(HOLD_API, "publication byte cap exceeded")
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        directory_descriptor = os.open(path.parent, directory_flags)
    except OSError as error:
        raise IndependentVerificationFailure(HOLD_API, "publication parent open failed") from error
    try:
        parent_before = os.fstat(directory_descriptor)
        try:
            parent_link = path.parent.lstat()
        except OSError as error:
            raise IndependentVerificationFailure(HOLD_API, "publication parent vanished") from error
        if (
            not stat.S_ISDIR(parent_before.st_mode)
            or stat.S_ISLNK(parent_link.st_mode)
            or _directory_link_identity(parent_before) != _directory_link_identity(parent_link)
        ):
            raise IndependentVerificationFailure(HOLD_API, "publication parent is unsafe")
        create_flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            descriptor = os.open(path.name, create_flags, 0o600, dir_fd=directory_descriptor)
        except OSError as error:
            raise IndependentVerificationFailure(
                HOLD_API, "exclusive publication failed"
            ) from error
        file_after: os.stat_result | None = None
        try:
            created = os.fstat(descriptor)
            if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
                raise IndependentVerificationFailure(HOLD_API, "published file is unsafe")
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise IndependentVerificationFailure(HOLD_API, "publication write stalled")
                offset += written
            file_after = os.fstat(descriptor)
            if (
                not stat.S_ISREG(file_after.st_mode)
                or file_after.st_nlink != 1
                or file_after.st_size != len(payload)
            ):
                raise IndependentVerificationFailure(HOLD_API, "published file size drifted")
        finally:
            os.close(descriptor)
        assert file_after is not None
        reread = _read_regular_stable_at(
            directory_descriptor,
            path.name,
            maximum_bytes=maximum_bytes,
            code=HOLD_API,
            expected_identity=_stat_identity(file_after),
        )
        try:
            parent_after = path.parent.lstat()
        except OSError as error:
            raise IndependentVerificationFailure(
                HOLD_API, "publication parent vanished after write"
            ) from error
        if _directory_link_identity(os.fstat(directory_descriptor)) != _directory_link_identity(
            parent_after
        ):
            raise IndependentVerificationFailure(HOLD_API, "publication parent changed")
        if not hmac.compare_digest(reread, payload):
            raise IndependentVerificationFailure(HOLD_API, "published bytes changed on reread")
        return reread
    finally:
        os.close(directory_descriptor)


def _validated_semantic_bytes(receipt: dict[str, object]) -> bytes:
    if type(receipt) is not dict:
        raise IndependentVerificationFailure(HOLD_API, "semantic receipt is not an object")
    status = receipt.get("status")
    if status == PASS_STATUS:
        if (
            set(receipt) != _CHILD_SEMANTIC_SUCCESS_KEYS
            or receipt.get("schema") != CHILD_SEMANTIC_SUCCESS_SCHEMA
        ):
            raise IndependentVerificationFailure(HOLD_API, "semantic success schema drifted")
    elif status in _HOLD_STATUSES:
        if not exact_json_equal(receipt, _hold_receipt(status)):
            raise IndependentVerificationFailure(HOLD_API, "semantic HOLD schema drifted")
    else:
        raise IndependentVerificationFailure(HOLD_API, "semantic status drifted")
    encoded = canonical_json_bytes(receipt)
    if len(encoded) > MAX_RECEIPT_BYTES:
        raise IndependentVerificationFailure(HOLD_API, "semantic receipt cap exceeded")
    return encoded


def _peak_rss_bytes() -> int:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if type(raw) is int:
        integral = raw
    elif type(raw) is float and math.isfinite(raw) and raw.is_integer():
        integral = int(raw)
    else:
        raise IndependentVerificationFailure(HOLD_API, "peak RSS observation is invalid")
    if integral < 0:
        raise IndependentVerificationFailure(HOLD_API, "peak RSS observation is invalid")
    if sys.platform == "darwin":
        multiplier = 1
    elif sys.platform.startswith("linux"):
        multiplier = 1_024
    else:
        raise IndependentVerificationFailure(HOLD_API, "peak RSS platform is unsupported")
    return integral * multiplier


def _build_observation(
    arguments: ChildWireArguments,
    semantic_bytes: bytes,
    *,
    status: str,
    started_monotonic_ns: int,
) -> dict[str, object]:
    verifier_bytes = read_regular_stable(
        Path(__file__), maximum_bytes=MAX_JSON_FILE_BYTES, code=HOLD_API
    )
    elapsed = time.monotonic_ns() - started_monotonic_ns
    if elapsed < 0:
        raise IndependentVerificationFailure(HOLD_API, "monotonic clock moved backwards")
    observation = {
        "elapsed_monotonic_ns": elapsed,
        "launch_nonce": arguments.launch_nonce,
        "peak_rss_bytes": _peak_rss_bytes(),
        "pgid": os.getpgid(0),
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "run_index": arguments.run_index,
        "schema": CHILD_OBSERVATION_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_bytes),
        "semantic_receipt_sha256": sha256_bytes(semantic_bytes),
        "status": status,
        "verifier_staged_file_sha256_at_observation": sha256_bytes(verifier_bytes),
    }
    if set(observation) != _CHILD_OBSERVATION_KEYS:
        raise IndependentVerificationFailure(HOLD_API, "observation schema drifted")
    return observation


def _build_bound_ack(
    arguments: ChildWireArguments,
    semantic_bytes: bytes,
    observation_bytes: bytes,
    *,
    status: str,
) -> dict[str, object]:
    acknowledgement = {
        "launch_nonce": arguments.launch_nonce,
        "observation_byte_length": len(observation_bytes),
        "observation_sha256": sha256_bytes(observation_bytes),
        "run_index": arguments.run_index,
        "schema": CHILD_BOUND_ACK_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_bytes),
        "semantic_receipt_sha256": sha256_bytes(semantic_bytes),
        "status": status,
    }
    if set(acknowledgement) != _CHILD_BOUND_ACK_KEYS:
        raise IndependentVerificationFailure(HOLD_API, "child acknowledgement schema drifted")
    return acknowledgement


def _emit_stdout(payload: dict[str, object]) -> bool:
    try:
        encoded = canonical_json_bytes(payload)
        if len(encoded) > MAX_CHILD_ACK_BYTES:
            return False
        sys.stdout.write(encoded.decode("ascii"))
        sys.stdout.flush()
    except Exception:
        return False
    return True


def _main(argv: Sequence[str] | None = None) -> int:
    started_monotonic_ns = time.monotonic_ns()
    try:
        arguments = _parse_cli(list(sys.argv[1:] if argv is None else argv))
    except Exception:
        _emit_stdout(_unbound_hold_ack())
        return 2
    try:
        receipt = verify_semantic_core(arguments.report_root, arguments.bundle_root)
    except IndependentVerificationFailure as error:
        receipt = _hold_receipt(error.code)
    except Exception:
        receipt = _hold_receipt(HOLD_API)
    try:
        semantic_bytes = _validated_semantic_bytes(receipt)
        semantic_bytes = _publish_exclusive_stable(
            arguments.semantic_receipt_path,
            semantic_bytes,
            maximum_bytes=MAX_RECEIPT_BYTES,
        )
        status = receipt["status"]
        assert type(status) is str
        observation = _build_observation(
            arguments,
            semantic_bytes,
            status=status,
            started_monotonic_ns=started_monotonic_ns,
        )
        observation_bytes = canonical_json_bytes(observation)
        observation_bytes = _publish_exclusive_stable(
            arguments.observation_path,
            observation_bytes,
            maximum_bytes=MAX_CHILD_OBSERVATION_BYTES,
        )
        acknowledgement = _build_bound_ack(
            arguments,
            semantic_bytes,
            observation_bytes,
            status=status,
        )
        if not _emit_stdout(acknowledgement):
            return 2
    except Exception:
        _emit_stdout(_unbound_hold_ack())
        return 2
    return 0 if receipt["status"] == PASS_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(_main())
