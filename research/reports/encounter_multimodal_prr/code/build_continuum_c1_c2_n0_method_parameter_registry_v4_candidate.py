#!/usr/bin/env python3
"""Build the standalone result-blind method-parameter registry v4 candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import sys
import threading
import unicodedata
from fractions import Fraction
from pathlib import Path
from typing import Any, Final

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_OUTPUT: Final = (
    REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
)

SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
STATUS: Final = "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v4"
CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
ROLE10_SCOPE: Final = ["role10_killing_factor_geometry"]
PAIRED_SIMPSON_POLICY_DOMAIN: Final = "killing-geometry-independent-paired-simpson-policy-v2"
PAIRED_SIMPSON_POLICY_SHA256: Final = (
    "0fb7e19ff04a60c0ebee938fc725fe49ba5c030bb3a18f2570bbabb519a25895"
)
FLAT_TAIL_POLICY_DOMAIN: Final = "killing-geometry-independent-flat-tail-policy-v1"
FLAT_TAIL_POLICY_SHA256: Final = "b7720e13964c58cb14a6f1ca9aa4060a45b0cfaf8108587a62333dcf14933f9a"
FLAT_TAIL_THRESHOLD: Final = 2048
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
FLAT_TAIL_POLICY_PREIMAGE: Final = {
    "bump_upper_exact": f"1/{1 << FLAT_TAIL_THRESHOLD}",
    "derivative_coefficients": [
        [3, 24],
        [4, 300],
        [5, 672],
        [6, 624],
        [7, 192],
        [8, 16],
    ],
    "derivative_upper_exact": (f"{FLAT_TAIL_M4_UPPER.numerator}/{FLAT_TAIL_M4_UPPER.denominator}"),
    "elementary_bound": "exp(-s)<2^-s_for_s_positive_because_e>2",
    "schema": "encounter_independent_compact_bump_flat_tail_policy_v1",
    "threshold_exact": f"{FLAT_TAIL_THRESHOLD}/1",
}
PAIRED_SIMPSON_POLICY_PREIMAGE: Final = {
    "accepted_panel_rule": ("exact_panel_enclosure_width_le_root_target_width_over_2^depth"),
    "accumulation": "per_segment_exact_balanced_binary_bins",
    "coordinate_component_bit_cap": 256,
    "dyadic_depth_cap": 64,
    "exact_component_bit_cap": 8192,
    "execution_model": "single_threaded_child",
    "flat_tail_threshold": FLAT_TAIL_THRESHOLD,
    "maximum_stack_nodes": 65,
    "mpfr_to_mpq_denominator_bit_cap": 4096,
    "panel_cap": 4194304,
    "primary_target_width_exact": "1/18446744073709551616",
    "remainder_prefilter": ("split_without_estimate_when_exact_root_local_R_exceeds_allowance"),
    "root_derivative_rule": "one_rigorous_M4_upper_per_frozen_root_and_precision",
    "sample_rule": "paired_384_512_samples_with_parent_endpoint_and_midpoint_reuse",
    "schema": "encounter_independent_paired_root_local_simpson_policy_v2",
    "sentinel_rule": ("512_bit_containment_only_on_primary_accepted_leaves_not_2^-68_adaptive"),
    "traversal": "per_root_explicit_DFS_push_right_then_left_execute_left_first",
}
CLAIM_KEYS: Final = (
    "backend_independence_claimed",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "external_predecessor_commitment_present",
    "formal_outer_open_operation_model_present",
    "formal_selected_source_dag_complete",
    "formal_symbolic_candidate_materialized",
    "one_correlated_distinguished_ideal_member_is_contained",
    "ordered_roles_8_10_replay_executed",
    "policy_predecessor_order_independently_sealed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "root_transfer_complete",
    "science_executed",
    "submission_eligible",
    "symbolic_acceptance_receipt_materialized",
)


class RegistryBuildError(RuntimeError):
    """The normative registry or immutable publication failed."""


class StageCreationTransaction:
    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="method-registry-v4-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o400,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            opened = _STAGE_FSTAT(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or opened.st_size != 0:
                raise RegistryBuildError("new staging inode invariant failure")
            self.identity = opened.st_dev, opened.st_ino
        except BaseException as error:
            self.error = error
        finally:
            self._ready.set()

    def start(self) -> None:
        self._thread.start()

    def await_ready(self) -> None:
        self._ready.wait()
        if self.error is not None:
            raise self.error
        if self.descriptor is None or self.identity is None:
            raise RegistryBuildError("stage transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise RegistryBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def canonical_bytes(value: Any) -> bytes:
    def visit(node: Any, depth: int = 0) -> None:
        if depth > 64:
            raise RegistryBuildError("JSON depth cap exceeded")
        if isinstance(node, float):
            raise RegistryBuildError("floating JSON literal forbidden")
        if type(node) in (bool, int) or node is None:
            return
        if type(node) is str:
            if unicodedata.normalize("NFC", node) != node:
                raise RegistryBuildError("non-NFC JSON string")
            return
        if type(node) is list:
            for item in node:
                visit(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                    raise RegistryBuildError("invalid JSON key")
                visit(item, depth + 1)
            return
        raise RegistryBuildError(f"forbidden JSON type: {type(node).__name__}")

    visit(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def method_digest(parameters: dict[str, Any]) -> str:
    return hashlib.sha256(
        DIGEST_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(parameters)
    ).hexdigest()


def policy_digest(domain: str, preimage: dict[str, Any]) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical_bytes(preimage)).hexdigest()


def entry(identifier: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "method_parameter_sha256": method_digest(parameters),
        "parameter_id": identifier,
        "parameters": parameters,
    }


def parameter_records() -> list[dict[str, Any]]:
    if (
        policy_digest(PAIRED_SIMPSON_POLICY_DOMAIN, PAIRED_SIMPSON_POLICY_PREIMAGE)
        != PAIRED_SIMPSON_POLICY_SHA256
        or policy_digest(FLAT_TAIL_POLICY_DOMAIN, FLAT_TAIL_POLICY_PREIMAGE)
        != FLAT_TAIL_POLICY_SHA256
    ):
        raise RegistryBuildError("embedded policy preimage digest drift")
    exact_scope = [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ]
    return [
        entry(
            "stationary_directed_mpfr_320_v2",
            {
                "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
                "dense_tensor_materialized": False,
                "precision_bits": 320,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role9_stationary_physical_integral"],
            },
        ),
        entry(
            "stationary_directed_mpfr_640_sentinel_v2",
            {
                "containment_relation": CONTAINMENT,
                "independent_backend": False,
                "precision_bits": 640,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role9_stationary_physical_integral"],
            },
        ),
        entry(
            "raw_flux_directed_mpfr_320_v2",
            {
                "aggregation": "exact_Fraction_endpoint_algebra",
                "common_kappa_rule": "intersection_after_formula_witness",
                "precision_bits": 320,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        entry(
            "raw_flux_directed_mpfr_640_sentinel_v2",
            {
                "containment_relation": CONTAINMENT,
                "independent_backend": False,
                "precision_bits": 640,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        entry(
            "raw_flux_binary64_decode_v2",
            {
                "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
                "precision_bits": 53,
                "rounding_mode": "stored_outward_endpoints",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        entry(
            "exact_fraction_expression_dag_v2",
            {
                "arithmetic": "Python_Fraction_exact_reduced_rationals",
                "precision_bits": "unbounded_integer_fraction",
                "rounding_mode": "exact",
                "source_role_scope": exact_scope,
            },
        ),
        entry(
            "killing_contact_profile_mpfr_192_v3",
            {
                "contact_algorithm": (
                    "directed_disk_primitive_over_exact_wrapped_segments_with_sqrt_asin_"
                    "quadrant_inclusion_exclusion_and_[0,1]_clipping"
                ),
                "contact_area_relative_width_gate": "1/10000000000",
                "contact_fraction_record_format": ">dd",
                "panels_per_unit": 16384,
                "precision_bits": 192,
                "profile_algorithm": "directed_compact_bump_cell_mass_composite_Simpson",
                "profile_cell_mass_width_gate": "1/1099511627776",
                "profile_integral_relative_width_gate": "1/10000000000",
                "published_contact_width_gate": "1/1099511627776",
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ROLE10_SCOPE,
                "support_density_record_format": ">dd",
                "support_fourth_derivative_global_bound": "322000/1",
                "support_panel_rule": "even(max(2,ceil_exact(length*16384)))",
                "support_simpson_remainder": "length*h^4*M4/180",
                "support_normalization_division": "outward_positive_interval_division",
            },
        ),
        entry(
            "killing_analytic_disk_area_mpfr_256_v3",
            {
                "analytic_area_precision_bits": 256,
                "analytic_area_relative_width_gate": "1/1000000000000",
                "containment_chain": [
                    "saved_256_contains_oracle_384",
                    "oracle_384_contains_sentinel_512",
                ],
                "formula": "pi_times_radius_squared",
                "oracle_precision_bits": 384,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "sentinel_precision_bits": 512,
                "source_role_scope": ROLE10_SCOPE,
            },
        ),
        entry(
            "killing_source_independent_same_backend_verifier_v3",
            {
                "accumulation": "balanced_exact_bin_accumulation",
                "aggregate_profile_relative_width_gate": "1/10000000000",
                "analytic_area_containment": (
                    "saved_256_contains_oracle_384_contains_sentinel_512"
                ),
                "contact_aggregate_identity": (
                    "each_row_volume_weighted_contact_cell_sum_contains_analytic_"
                    "pi_times_radius_squared"
                ),
                "contact_cell_verification": (
                    "every_partial_contact_cell_independently_recomputed_at_384_bits_"
                    "and_first_partial_contact_cell_per_row_at_512_bits"
                ),
                "contact_oracle": ("exact_disk_rectangle_oracle_not_Simpson_contact_quadrature"),
                "contact_oracle_width_gate": (
                    "1/1532495540865888858358347027150309183618739122183602176"
                ),
                "contact_containment_relations": [
                    "published_192_contains_primary_384_for_every_partial_contact_cell",
                    "primary_384_contains_sentinel_512_for_first_partial_contact_cell_per_row",
                    "published_192_contains_sentinel_512_for_first_partial_contact_cell_per_row",
                ],
                "child_process_deadline_seconds": 1200,
                "dfs_order": "right_push_left_first_depth_first",
                "flat_tail_policy_digest_domain": FLAT_TAIL_POLICY_DOMAIN,
                "flat_tail_policy_preimage": FLAT_TAIL_POLICY_PREIMAGE,
                "flat_tail_policy_sha256": FLAT_TAIL_POLICY_SHA256,
                "flat_tail_threshold": FLAT_TAIL_THRESHOLD,
                "independent_backend": False,
                "maximum_bump_breakpoints": 20000,
                "maximum_child_ack_bytes": 4096,
                "maximum_child_observation_bytes": 65536,
                "maximum_child_semantic_receipt_bytes": 2097152,
                "maximum_child_stderr_bytes": 4096,
                "maximum_dyadic_coordinate_component_bits": 256,
                "maximum_json_file_bytes": 2097152,
                "maximum_mpfr_to_mpq_denominator_bits": 4096,
                "maximum_outer_receipt_bytes": 262144,
                "maximum_raw_contact_file_bytes": 553840,
                "maximum_raw_support_file_bytes": 3312,
                "maximum_simpson_dfs_stack": 65,
                "maximum_simpson_dyadic_depth": 64,
                "maximum_simpson_exact_component_bits": 8192,
                "maximum_simpson_panels": 4194304,
                "maximum_tree_directories": 64,
                "maximum_tree_files": 256,
                "maximum_tree_relative_depth": 3,
                "maximum_tree_total_bytes": 67108864,
                "oracle_to_nonzero_producer_width_max": "1/8",
                "outer_deadline_seconds": 2700,
                "outer_nonchild_reserve_seconds": 300,
                "paired_simpson_policy_digest_domain": PAIRED_SIMPSON_POLICY_DOMAIN,
                "paired_simpson_policy_preimage": PAIRED_SIMPSON_POLICY_PREIMAGE,
                "paired_simpson_policy_sha256": PAIRED_SIMPSON_POLICY_SHA256,
                "parent_sample_reuse": True,
                "primary_precision_bits": 384,
                "primary_target_width": "1/18446744073709551616",
                "same_backend": "MPFR_directed_RoundDown_RoundUp",
                "semantic_deadline_seconds": 1140,
                "sentinel_evaluation_rule": ("512_bits_only_on_leaves_accepted_by_384_bit_primary"),
                "sentinel_precision_bits": 512,
                "simpson_applicability": ("compact_support_bump_cells_only_not_disk_contact_cells"),
                "source_independence": (
                    "oracle_reconstruction_from_frozen_role3_sources_without_using_published_"
                    "192_bit_producer_values_while_the_verifier_reads_those_values_as_"
                    "candidate_enclosures_for_containment"
                ),
                "source_role_scope": ROLE10_SCOPE,
                "support_aggregate_identity": (
                    "each_compact_support_profile_volume_weighted_cell_mass_sum_contains_exact_one"
                ),
                "support_cell_verification": (
                    "every_support_cell_and_aggregate_at_384_and_512_bits"
                ),
                "support_containment_relations": [
                    "published_192_contains_primary_384_per_cell_and_aggregate",
                    "primary_384_contains_sentinel_512_per_cell_and_aggregate",
                    "published_192_contains_sentinel_512_per_cell_and_aggregate",
                ],
            },
        ),
        entry(
            "killing_exact_contact_cell_classification_v3",
            {
                "full_rule": (
                    "all_corners_of_every_exact_wrapped_segment_inside_or_on_closed_disk"
                ),
                "full_serialization": "exact_[1,1]",
                "partial_rule": "otherwise_partial_directed_interval",
                "partial_serialization": "exact_[lower,upper]",
                "periodic_segmentation": "exact_wrapped_periodic_segments",
                "precision_bits": "exact_rational",
                "rounding_mode": "exact",
                "source_role_scope": ROLE10_SCOPE,
                "tangency_convention": "boundary_tangency_is_measure_zero",
                "zero_rule": (
                    "nearest_squared_distance_of_every_wrapped_segment_outside_closed_disk"
                ),
                "zero_serialization": "exact_[0,0]",
            },
        ),
    ]


def normative_registry() -> dict[str, Any]:
    records = parameter_records()
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "parameter_count": len(records),
        "parameters": records,
        "schema": SCHEMA,
        "status": STATUS,
    }


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or path != Path(os.path.abspath(path)) or len(path.parts) < 2:
        raise RegistryBuildError("canonical absolute registry path required")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:-1]:
            if component in {"", ".", ".."}:
                raise RegistryBuildError("unsafe registry path component")
            following = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise RegistryBuildError("unsafe registry leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def parent_matches(descriptor: int, identity: tuple[int, int]) -> bool:
    try:
        observed = os.fstat(descriptor)
    except BaseException:
        return False
    return (
        stat.S_ISDIR(observed.st_mode)
        and (
            observed.st_dev,
            observed.st_ino,
        )
        == identity
    )


def verify_live_parent(path: Path, anchored: int, identity: tuple[int, int]) -> None:
    verification, _ = open_parent_anchored(path)
    try:
        if not parent_matches(anchored, identity) or not parent_matches(
            verification,
            identity,
        ):
            raise RegistryBuildError("registry directory chain changed")
    finally:
        os.close(verification)


def read_regular(path: Path, cap: int = 1_000_000) -> bytes:
    parent, leaf = open_parent_anchored(path)
    opened_parent = os.fstat(parent)
    parent_identity = opened_parent.st_dev, opened_parent.st_ino
    descriptor = -1
    try:
        descriptor = os.open(
            leaf,
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
            dir_fd=parent,
        )
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened.st_size <= 0
            or opened.st_size > cap
            or stat.S_IMODE(opened.st_mode) != 0o444
        ):
            raise RegistryBuildError("immutable single-link registry required")
        payload = bytearray()
        while len(payload) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(payload))
            if not block:
                raise RegistryBuildError("short registry read")
            payload.extend(block)
        if os.read(descriptor, 1):
            raise RegistryBuildError("registry grew during read")
        after = os.fstat(descriptor)
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        ) or (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino):
            raise RegistryBuildError("registry changed during read")
        verify_live_parent(path, parent, parent_identity)
        return bytes(payload)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def unlink_owned(parent: int, leaf: str, identity: tuple[int, int]) -> bool:
    try:
        current = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if (current.st_dev, current.st_ino) != identity:
        return False
    os.unlink(leaf, dir_fd=parent)
    return True


def close_safely(descriptor: int) -> None:
    if descriptor < 0:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


def publish_no_replace(path: Path, payload: bytes) -> None:
    parent, leaf = open_parent_anchored(path)
    opened_parent = os.fstat(parent)
    parent_identity = opened_parent.st_dev, opened_parent.st_ino
    stage = f".{leaf}.{secrets.token_hex(16)}.stage"
    recovery_parent = -1
    descriptor = -1
    transaction: StageCreationTransaction | None = None
    stage_identity: tuple[int, int] | None = None
    final_attempted = False
    try:
        transaction = StageCreationTransaction(parent, stage)
        transaction.start()
        transaction.await_ready()
        descriptor = -1 if transaction.descriptor is None else transaction.descriptor
        stage_identity = transaction.identity
        if descriptor < 0 or stage_identity is None:
            raise RegistryBuildError("stage transaction result missing")
        transaction.release_descriptor(descriptor)

        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise RegistryBuildError("short staged write")
            written += count
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if (staged.st_dev, staged.st_ino) != stage_identity:
            raise RegistryBuildError("staging descriptor identity changed")
        os.close(descriptor)
        descriptor = -1

        final_attempted = True
        try:
            os.link(
                stage,
                leaf,
                src_dir_fd=parent,
                dst_dir_fd=parent,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise RegistryBuildError(f"refusing to replace existing output: {path}") from error
        if not unlink_owned(parent, stage, stage_identity):
            raise RegistryBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != stage_identity
            or stat.S_IMODE(final.st_mode) != 0o444
            or final.st_nlink != 1
            or final.st_size != len(payload)
        ):
            raise RegistryBuildError("published registry identity/mode/size drift")
        if read_regular(path, len(payload)) != payload:
            raise RegistryBuildError("published registry byte acknowledgement drift")
        acknowledged = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (acknowledged.st_dev, acknowledged.st_ino) != stage_identity
            or stat.S_IMODE(acknowledged.st_mode) != 0o444
            or acknowledged.st_nlink != 1
            or acknowledged.st_size != len(payload)
        ):
            raise RegistryBuildError("published registry post-read identity drift")
        verify_live_parent(path, parent, parent_identity)
        os.close(parent)
        parent = -1
    except BaseException:
        if transaction is not None:
            transaction.settle()
            if stage_identity is None:
                stage_identity = transaction.identity
            if transaction.descriptor is not None:
                if descriptor < 0:
                    descriptor = transaction.descriptor
                elif descriptor != transaction.descriptor:
                    close_safely(transaction.descriptor)
                transaction.descriptor = None
        if descriptor >= 0 and stage_identity is None:
            try:
                opened = _STAGE_FSTAT(descriptor)
                stage_identity = opened.st_dev, opened.st_ino
            except BaseException:
                pass
        close_safely(descriptor)
        descriptor = -1

        cleanup_parent = -1
        if parent_matches(parent, parent_identity):
            cleanup_parent = parent
        else:
            try:
                recovered, recovered_leaf = open_parent_anchored(path)
                if recovered_leaf == leaf and parent_matches(recovered, parent_identity):
                    recovery_parent = recovered
                    cleanup_parent = recovered
                else:
                    close_safely(recovered)
            except BaseException:
                pass
        if cleanup_parent >= 0:
            if final_attempted and stage_identity is not None:
                try:
                    unlink_owned(cleanup_parent, leaf, stage_identity)
                except BaseException:
                    pass
            if stage_identity is not None:
                try:
                    unlink_owned(cleanup_parent, stage, stage_identity)
                except BaseException:
                    pass
            try:
                os.fsync(cleanup_parent)
            except BaseException:
                pass
        raise
    finally:
        if transaction is not None:
            transaction.settle()
            if transaction.descriptor is not None:
                close_safely(transaction.descriptor)
                transaction.descriptor = None
        close_safely(descriptor)
        close_safely(recovery_parent)
        close_safely(parent)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        payload = canonical_bytes(normative_registry())
        output = Path(os.path.abspath(os.fspath(arguments.output.expanduser())))
        if arguments.check:
            if read_regular(output) != payload:
                raise RegistryBuildError("registry candidate byte drift")
            print(
                "PASS_METHOD_PARAMETER_REGISTRY_V4_CANDIDATE_CHECK "
                f"sha256={hashlib.sha256(payload).hexdigest()}"
            )
            return 0
        publish_no_replace(output, payload)
        print(
            "PASS_METHOD_PARAMETER_REGISTRY_V4_CANDIDATE_BUILD "
            f"path={output} sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    except (OSError, RegistryBuildError) as error:
        print(
            f"ERROR MethodParameterRegistryV4CandidateBuild: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
