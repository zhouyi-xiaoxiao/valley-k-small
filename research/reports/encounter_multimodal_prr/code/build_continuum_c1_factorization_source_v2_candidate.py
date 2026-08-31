#!/usr/bin/env python3
"""Build the outcome-free role-3 factorization authority candidate.

This source freezes only geometry, coordinate, normalization, factorization,
and storage semantics.  It contains no role-8--10 enclosure payload, control
weight, budget, production killing tensor, or acceptance claim.
"""

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
from pathlib import Path
from typing import Any, Final

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_OUTPUT: Final = (
    REPORT / "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)

GEOMETRY_RELATIVE: Final = "artifacts/data/physical_killing_geometry_source_v1.json"
CONFIGURATION_RELATIVE: Final = "artifacts/data/physical_configuration_family_control_free_v1.json"
PARTITION_BUNDLE_RELATIVE: Final = (
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)

GEOMETRY_SHA256: Final = "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
PARTITION_BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"

PROFILE_CENTRES: Final = (
    "3152519739159347/9007199254740992",
    "5404319552844595/9007199254740992",
    "3/4",
    "8106479329266893/9007199254740992",
)
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


class FactorizationBuildError(RuntimeError):
    """A source, semantic, or immutable-publication invariant failed."""


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
            name="factorization-v2-stage-create",
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
                raise FactorizationBuildError("new staging inode invariant failure")
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
            raise FactorizationBuildError("stage transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise FactorizationBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def canonical_bytes(value: Any) -> bytes:
    def check(node: Any, depth: int = 0) -> None:
        if depth > 48:
            raise FactorizationBuildError("JSON depth cap exceeded")
        if isinstance(node, float):
            raise FactorizationBuildError("floating JSON literals are forbidden")
        if type(node) in (bool, int) or node is None:
            return
        if type(node) is str:
            if unicodedata.normalize("NFC", node) != node:
                raise FactorizationBuildError("non-NFC JSON string")
            return
        if type(node) is list:
            for item in node:
                check(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                    raise FactorizationBuildError("invalid JSON key")
                check(item, depth + 1)
            return
        raise FactorizationBuildError(f"forbidden JSON type: {type(node).__name__}")

    check(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def parse_canonical(payload: bytes, role: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in value:
                raise FactorizationBuildError(f"duplicate or invalid key in {role}")
            value[key] = item
        return value

    def reject_number(token: str) -> Any:
        raise FactorizationBuildError(f"non-integer JSON number in {role}: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise FactorizationBuildError(f"strict JSON failure for {role}") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise FactorizationBuildError(f"canonical JSON byte drift for {role}")
    return value


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or len(path.parts) < 2:
        raise FactorizationBuildError("absolute source or output path required")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:-1]:
            if component in {"", ".", ".."}:
                raise FactorizationBuildError("unsafe path component")
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise FactorizationBuildError("unsafe path leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def verify_live_parent(path: Path, anchored: int) -> None:
    current, _ = open_parent_anchored(path)
    try:
        expected = os.fstat(anchored)
        observed = os.fstat(current)
        if (expected.st_dev, expected.st_ino) != (observed.st_dev, observed.st_ino):
            raise FactorizationBuildError("directory chain changed during operation")
    finally:
        os.close(current)


def read_regular(path: Path, role: str, cap: int = 64 * 1024 * 1024) -> bytes:
    parent, leaf = open_parent_anchored(path)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    descriptor = -1
    try:
        descriptor = os.open(leaf, flags, dir_fd=parent)
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened.st_size <= 0
            or opened.st_size > cap
            or stat.S_IMODE(opened.st_mode) != 0o444
        ):
            raise FactorizationBuildError(f"unstable or oversized source for {role}")
        chunks: list[bytes] = []
        remaining = opened.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            if not chunk:
                raise FactorizationBuildError(f"short read for {role}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise FactorizationBuildError(f"source grew while reading {role}")
        after = os.fstat(descriptor)
        if (
            after.st_size != opened.st_size
            or after.st_mtime_ns != opened.st_mtime_ns
            or after.st_ctime_ns != opened.st_ctime_ns
        ):
            raise FactorizationBuildError(f"source changed while reading {role}")
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino):
            raise FactorizationBuildError(f"source path changed while reading {role}")
        verify_live_parent(path, parent)
        return b"".join(chunks)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def load_pinned(relative: str, expected_sha256: str, role: str) -> dict[str, Any]:
    payload = read_regular(REPORT / relative, role)
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise FactorizationBuildError(f"SHA-256 mismatch for {role}")
    return parse_canonical(payload, role)


def require_equal(actual: Any, expected: Any, message: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        raise FactorizationBuildError(message)


def validate_sources() -> dict[str, Any]:
    geometry = load_pinned(GEOMETRY_RELATIVE, GEOMETRY_SHA256, "geometry source")
    configuration = load_pinned(
        CONFIGURATION_RELATIVE,
        CONFIGURATION_SHA256,
        "configuration source",
    )
    partition = load_pinned(
        PARTITION_BUNDLE_RELATIVE,
        PARTITION_BUNDLE_SHA256,
        "partition bundle",
    )

    require_equal(
        geometry.get("schema"),
        "encounter_physical_killing_geometry_source_v1",
        "geometry schema drift",
    )
    require_equal(
        geometry.get("status"),
        (
            "FROZEN_CONTROL_FREE_CONTACT_AND_SUPPORT_BASIS_SOURCE_ONLY_"
            "NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
        ),
        "geometry status drift",
    )
    require_equal(
        geometry.get("configuration_bundle"),
        {
            "configuration_path": CONFIGURATION_RELATIVE,
            "configuration_sha256": CONFIGURATION_SHA256,
            "partition_bundle_path": PARTITION_BUNDLE_RELATIVE,
            "partition_bundle_sha256": PARTITION_BUNDLE_SHA256,
        },
        "geometry source-pin drift",
    )
    require_equal(
        geometry.get("coordinate_order"),
        ["midpoint", "relative_parallel", "relative_perpendicular"],
        "geometry coordinate order drift",
    )
    require_equal(geometry.get("physical_dimension"), 2, "physical dimension drift")
    require_equal(geometry.get("quotient_dimension"), 3, "quotient dimension drift")
    require_equal(
        geometry.get("contact_geometry"),
        {
            "cell_fraction_definition": (
                "physical_area_of_contact_disk_intersection_with_relative_cell_"
                "divided_by_exact_relative_cell_volume"
            ),
            "contact_set": (
                "r_parallel_squared_plus_minimum_image_r_perpendicular_squared_"
                "less_than_or_equal_to_radius_squared"
            ),
            "radius_binary64_hex": "0x1.47ae147ae147bp-3",
            "radius_exact": "5764607523034235/36028797018963968",
            "transverse_cut_locus_condition": "2*radius<transverse_period",
            "transverse_period_exact": "1/1",
        },
        "contact geometry drift",
    )
    require_equal(
        geometry.get("support_basis"),
        {
            "analytic_integral_each": "1/1",
            "centres_binary64_hex": [
                "0x1.6666666666666p-2",
                "0x1.3333333333333p-1",
                "0x1.8000000000000p-1",
                "0x1.ccccccccccccdp-1",
            ],
            "centres_exact": list(PROFILE_CENTRES),
            "density_definition": ("phi_j(M)=b((M-centre_j)/half_width)/(half_width*I_b)"),
            "half_width_binary64_hex": "0x1.47ae147ae147bp-5",
            "half_width_exact": "5764607523034235/144115188075855872",
            "normalizer_definition": "I_b=integral_from_minus_one_to_one_b(u)_du",
            "profile_count": 4,
            "shape_definition": ("b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))"),
        },
        "support-basis drift",
    )
    require_equal(
        geometry.get("flags"),
        {
            "authorizes_scientific_execution": False,
            "concrete_killing_constructed": False,
            "contact_geometry_defined": True,
            "contains_budget_value": False,
            "contains_control_values": False,
            "continuum_verified": False,
            "f0_pass": False,
            "full_operator_bound": False,
            "positive_budget_executed": False,
            "production_resource_gate": False,
            "propagation_executed": False,
            "science_executed": False,
            "support_basis_defined": True,
            "topology_complete": False,
        },
        "geometry flag drift",
    )

    require_equal(
        configuration.get("schema"),
        "encounter_physical_configuration_family_control_free_v1",
        "configuration schema drift",
    )
    require_equal(configuration.get("configuration_count"), 12, "configuration count drift")
    require_equal(
        configuration.get("coordinate_order"),
        ["midpoint", "relative_parallel", "relative_perpendicular"],
        "configuration coordinate order drift",
    )
    require_equal(
        configuration.get("authorizes_scientific_execution"),
        False,
        "configuration execution flag drift",
    )
    require_equal(
        configuration.get("contains_budget_value"),
        False,
        "configuration budget boundary drift",
    )
    require_equal(
        configuration.get("contains_control_values"),
        False,
        "configuration control boundary drift",
    )

    require_equal(
        partition.get("schema"),
        "encounter_control_free_production_initial_stream_v1",
        "partition schema drift",
    )
    require_equal(partition.get("configuration_count"), 12, "partition count drift")
    require_equal(
        partition.get("configuration_sha256"),
        CONFIGURATION_SHA256,
        "partition configuration binding drift",
    )
    partition_flags = partition.get("flags")
    if type(partition_flags) is not dict:
        raise FactorizationBuildError("partition flags missing")
    for key in (
        "authorizes_scientific_execution",
        "contains_budget_value",
        "contains_control_values",
        "full_operator_bound",
        "positive_budget_executed",
        "science_executed",
        "topology_complete",
    ):
        require_equal(partition_flags.get(key), False, f"partition flag drift: {key}")

    forbidden_geometry_tokens = (
        "physical_production_killing_geometry_v1",
        "two_repeat",
        "canonical_object_sha256",
        "factorization_contract_sha256",
        "acceptance_receipt",
        "observed",
        "result",
    )

    def scan(node: Any) -> None:
        if type(node) is dict:
            for key, item in node.items():
                lowered = key.lower()
                if any(token in lowered for token in forbidden_geometry_tokens):
                    raise FactorizationBuildError(f"outcome-bound key in geometry source: {key}")
                scan(item)
        elif type(node) is list:
            for item in node:
                scan(item)
        elif type(node) is str:
            lowered = node.lower()
            if any(token in lowered for token in forbidden_geometry_tokens):
                raise FactorizationBuildError("outcome-bound value in geometry source")

    scan(geometry)
    return geometry


def expected_candidate(geometry: dict[str, Any]) -> dict[str, Any]:
    support = geometry["support_basis"]
    contact = geometry["contact_geometry"]
    return {
        "cell_average_formulae": {
            "contact_average": (
                "C_ab=(|R_a|*|Y_b|)^-1*integral_{R_a x Y_b}*indicator_contact(R,Y)*dR*dY"
            ),
            "factorized_profile_cell_average": "V_jmab=W^-1*C_ab*Phi_jm",
            "profile_average": ("Phi_jm=|M_m|^-1*integral_{M_m}*phi_j(M)*dM"),
            "symbolic_weighted_cell_average": ("V_control_mab=sum_j*w_j*V_jmab"),
        },
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "contact_geometry": {
            "contact_indicator": ("indicator(R^2+minimum_image_W(Y)^2<=radius^2)"),
            "contact_radius_exact": contact["radius_exact"],
            "transverse_cut_locus_condition": contact["transverse_cut_locus_condition"],
            "transverse_period_exact": contact["transverse_period_exact"],
        },
        "coordinate_and_measure_contract": {
            "coordinate_order": [
                "midpoint",
                "relative_parallel",
                "relative_perpendicular",
            ],
            "longitudinal_absolute_jacobian_exact": "1/1",
            "longitudinal_transform": "M=(X_1+X_2)/2;R=X_1-X_2",
            "physical_cell": "M_m x R_a x Y_b",
            "physical_volume_measure": "dM*dR*dY",
            "quotient_density_normalization": "W^-1",
            "transverse_common_coordinate_reduction": (
                "periodic_Haar_change_preserves_measure_and_integrating_"
                "the_common_coordinate_yields_the_explicit_W^-1_factor"
            ),
            "transverse_period_symbol": "W",
        },
        "dependency_closure": {
            "acyclic": True,
            "edges": [
                {
                    "from": "configuration_source",
                    "to": "killing_geometry_source",
                },
                {
                    "from": "initial_partition_bundle",
                    "to": "killing_geometry_source",
                },
                {
                    "from": "killing_geometry_source",
                    "to": "factorization_source_v2_candidate",
                },
            ],
            "node_order": [
                "configuration_source",
                "initial_partition_bundle",
                "killing_geometry_source",
                "factorization_source_v2_candidate",
            ],
        },
        "enclosure_semantics": {
            "exact_contact_and_profile_averages_may_be_irrational": True,
            "exact_full_contact_cell_value": "1/1",
            "exact_zero_cell_value": "0/1",
            "future_numeric_payload_present": False,
            "future_role10_representation": (
                "closed_outward_dyadic_intervals_with_separate_primary_"
                "and_higher_precision_same_backend_sentinel"
            ),
            "stored_binary64_endpoints_are_not_exact_averages_or_centres": True,
        },
        "outcome_free_contract": {
            "budget_present": False,
            "concrete_killing_tensor_present": False,
            "control_weights_present": False,
            "external_commitment_present": False,
            "numeric_enclosure_payload_present": False,
            "primitive_source_only": True,
            "production_bridge_present": False,
        },
        "profile_basis": {
            "analytic_integral_each": support["analytic_integral_each"],
            "density": support["density_definition"],
            "half_width_exact": support["half_width_exact"],
            "normalizer": support["normalizer_definition"],
            "ordered_profile_mapping": [
                {
                    "centre_exact": centre,
                    "profile_index": index,
                    "source_role": f"physical_midpoint_support_density_{index:02d}",
                }
                for index, centre in enumerate(PROFILE_CENTRES)
            ],
            "profile_count": support["profile_count"],
            "shape": support["shape_definition"],
        },
        "schema": "encounter_continuum_c1_factorization_source_v2_candidate",
        "source_pins": {
            "configuration_source": {
                "path": CONFIGURATION_RELATIVE,
                "schema": "encounter_physical_configuration_family_control_free_v1",
                "sha256": CONFIGURATION_SHA256,
            },
            "initial_partition_bundle": {
                "path": PARTITION_BUNDLE_RELATIVE,
                "schema": "encounter_control_free_production_initial_stream_v1",
                "sha256": PARTITION_BUNDLE_SHA256,
            },
            "killing_geometry_source": {
                "path": GEOMETRY_RELATIVE,
                "schema": "encounter_physical_killing_geometry_source_v1",
                "sha256": GEOMETRY_SHA256,
            },
        },
        "status": (
            "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_"
            "NOT_EXTERNALLY_COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
        ),
        "storage_contract": {
            "contact_flat_index": "a*n_Y+b",
            "contact_logical_shape": ["n_R", "n_Y"],
            "full_flat_index": "(m*n_R+a)*n_Y+b",
            "full_logical_shape": ["n_M", "n_R", "n_Y"],
            "midpoint_broadcast": "C_ab_is_unchanged_over_m",
            "profile_support_files_separate_by_profile": True,
            "profile_support_flat_index": "m",
            "profile_support_logical_shape_each": ["n_M"],
            "tensor_storage_order": "C",
        },
    }


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


def publish_no_replace(path: Path, payload: bytes) -> None:
    parent, leaf = open_parent_anchored(path)
    opened_parent = os.fstat(parent)
    parent_identity = opened_parent.st_dev, opened_parent.st_ino
    stage = f".{leaf}.{secrets.token_hex(16)}.stage"
    recovery_parent = -1
    descriptor = -1
    transaction: StageCreationTransaction | None = None
    stage_identity: tuple[int, int] | None = None
    stage_attempted = False
    final_attempted = False
    try:
        stage_attempted = True
        transaction = StageCreationTransaction(parent, stage)
        transaction.start()
        transaction.await_ready()
        descriptor = -1 if transaction.descriptor is None else transaction.descriptor
        stage_identity = transaction.identity
        if descriptor < 0 or stage_identity is None:
            raise FactorizationBuildError("stage transaction result missing")
        transaction.release_descriptor(descriptor)

        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise FactorizationBuildError("short staged write")
            written += count
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if (staged.st_dev, staged.st_ino) != stage_identity:
            raise FactorizationBuildError("staging descriptor identity changed")
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
            raise FactorizationBuildError(f"refusing to replace existing output: {path}") from error
        if stage_identity is None or not unlink_owned(parent, stage, stage_identity):
            raise FactorizationBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != stage_identity
            or stat.S_IMODE(final.st_mode) != 0o444
            or final.st_nlink != 1
            or final.st_size != len(payload)
        ):
            raise FactorizationBuildError("published output identity/mode/size drift")
        if read_regular(path, "published factorization acknowledgement", len(payload)) != payload:
            raise FactorizationBuildError("published output byte acknowledgement drift")
        acknowledged = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (acknowledged.st_dev, acknowledged.st_ino) != stage_identity
            or stat.S_IMODE(acknowledged.st_mode) != 0o444
            or acknowledged.st_nlink != 1
            or acknowledged.st_size != len(payload)
        ):
            raise FactorizationBuildError("published output post-read identity drift")
        verify_live_parent(path, parent)
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
            if stage_attempted and stage_identity is not None:
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
        if descriptor >= 0:
            close_safely(descriptor)
        close_safely(recovery_parent)
        close_safely(parent)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="check that --output already equals the reconstructed candidate",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        payload = canonical_bytes(expected_candidate(validate_sources()))
        output = Path(os.path.abspath(os.fspath(arguments.output.expanduser())))
        if arguments.check:
            current = read_regular(output, "candidate output")
            if current != payload:
                raise FactorizationBuildError("candidate output byte drift")
            print(
                "PASS_FACTORIZATION_SOURCE_V2_CANDIDATE_CHECK "
                f"sha256={hashlib.sha256(payload).hexdigest()}"
            )
            return 0
        publish_no_replace(output, payload)
        print(
            "PASS_FACTORIZATION_SOURCE_V2_CANDIDATE_BUILD "
            f"path={output} sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    except (FactorizationBuildError, OSError) as error:
        print(f"ERROR FactorizationSourceV2CandidateBuild: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
