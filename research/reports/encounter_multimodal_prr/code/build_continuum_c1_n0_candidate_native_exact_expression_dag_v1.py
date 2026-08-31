#!/usr/bin/env python3
"""Build separated outward-interval and fixed formal-identity DAG evidence."""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import secrets
import stat
import sys
import threading
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Final

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_candidate_native_exact_expression_dag_request_v1"
ARTIFACT_SCHEMA: Final = (
    "encounter_continuum_c1_n0_candidate_native_exact_expression_dag_artifact_v1"
)
FORMAL_SCHEMA: Final = "formal_q_laurent_polynomial_v1"
CLAIM_KEYS: Final = (
    "external_predecessor_commitment_present",
    "ordered_roles_8_10_replay_executed",
    "production_data_read",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "science_executed",
)
INPUT_TYPES: Final = {"interval_nonnegative", "interval_positive"}
INTERVAL_OPERATIONS: Final = {
    "interval_add_nonnegative",
    "interval_divide_positive",
    "interval_intersection",
    "interval_multiply_nonnegative",
}
INTERVAL_RELATIONS: Final = {"interval_contains", "interval_equal"}
FORMAL_OPERATIONS: Final = {
    "formal_add",
    "formal_divide_monomial",
    "formal_identity",
    "formal_multiply",
}
TEMPLATE_DOMAIN: Final = (
    b"encounter-c1-n0-candidate-native-exact-expression-dag-semantic-template-v2\0"
)
OUTWARD_DOMAIN: Final = (
    b"encounter-c1-n0-candidate-native-exact-expression-dag-outward-interval-v1\0"
)
FORMAL_DOMAIN: Final = b"encounter-c1-n0-candidate-native-exact-expression-dag-formal-proof-v1\0"


def make_semantic_template() -> dict[str, Any]:
    """Return the closed, value-free interval and formula contract."""
    input_specs = (
        ("M_L", "interval_positive", "outward_interval_algebra_witness", "M_L"),
        ("S_M", "interval_positive", "outward_interval_algebra_witness", "S_M"),
        ("S_R", "interval_positive", "outward_interval_algebra_witness", "S_R"),
        ("S_Y", "interval_positive", "outward_interval_algebra_witness", "S_Y"),
        ("mu_M", "interval_positive", "outward_interval_algebra_witness", "mu_M"),
        ("mu_R", "interval_positive", "outward_interval_algebra_witness", "mu_R"),
        ("mu_Y", "interval_positive", "outward_interval_algebra_witness", "mu_Y"),
        (
            "mu_edge_left",
            "interval_positive",
            "edge_mass_outward_interval_witness",
            "mu_edge_left",
        ),
        (
            "forward_q_interval",
            "interval_nonnegative",
            "edge_rate_outward_interval_witness",
            "q_forward_formula",
        ),
        (
            "mu_edge_right",
            "interval_positive",
            "edge_mass_outward_interval_witness",
            "mu_edge_right",
        ),
        (
            "reverse_q_interval",
            "interval_nonnegative",
            "edge_rate_outward_interval_witness",
            "q_reverse_formula",
        ),
        (
            "direct_left_kappa_interval",
            "interval_nonnegative",
            "direct_left_formula_outward_interval_witness",
            "kappa_direct_left_formula",
        ),
        (
            "direct_right_kappa_interval",
            "interval_nonnegative",
            "direct_right_formula_outward_interval_witness",
            "kappa_direct_right_formula",
        ),
        ("M_pi", "interval_positive", "outward_interval_algebra_witness", "M_pi"),
        (
            "C_contact",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "C_contact",
        ),
        ("W_norm", "interval_positive", "outward_interval_algebra_witness", "W_norm"),
        (
            "weight_0",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "weight_0",
        ),
        (
            "weight_1",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "weight_1",
        ),
        (
            "weight_2",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "weight_2",
        ),
        (
            "weight_3",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "weight_3",
        ),
        (
            "Phi_0",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "Phi_0",
        ),
        (
            "Phi_1",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "Phi_1",
        ),
        (
            "Phi_2",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "Phi_2",
        ),
        (
            "Phi_3",
            "interval_nonnegative",
            "outward_interval_algebra_witness",
            "Phi_3",
        ),
    )
    outward_inputs = [
        {
            "formal_value_id": formal_value_id,
            "input_id": input_id,
            "provenance_lane": provenance_lane,
            "semantic_shape": "interval",
            "value_type": value_type,
        }
        for input_id, value_type, provenance_lane, formal_value_id in input_specs
    ]

    outward_node_specs = (
        ("axis_mass_product", "interval_multiply_nonnegative", ("S_M", "S_R", "S_Y")),
        ("G", "interval_divide_positive", ("M_L", "axis_mass_product")),
        ("pi_h", "interval_multiply_nonnegative", ("G", "mu_M", "mu_R", "mu_Y")),
        (
            "forward_product_kappa_interval",
            "interval_multiply_nonnegative",
            ("mu_edge_left", "forward_q_interval"),
        ),
        (
            "reverse_product_kappa_interval",
            "interval_multiply_nonnegative",
            ("mu_edge_right", "reverse_q_interval"),
        ),
        (
            "common_kappa_interval",
            "interval_intersection",
            (
                "direct_left_kappa_interval",
                "direct_right_kappa_interval",
                "forward_product_kappa_interval",
                "reverse_product_kappa_interval",
            ),
        ),
        (
            "conductance",
            "interval_multiply_nonnegative",
            ("G", "common_kappa_interval", "mu_R", "mu_Y"),
        ),
        ("rho", "interval_divide_positive", ("M_pi", "pi_h")),
        (
            "weighted_profile_0",
            "interval_multiply_nonnegative",
            ("weight_0", "Phi_0"),
        ),
        (
            "weighted_profile_1",
            "interval_multiply_nonnegative",
            ("weight_1", "Phi_1"),
        ),
        (
            "weighted_profile_2",
            "interval_multiply_nonnegative",
            ("weight_2", "Phi_2"),
        ),
        (
            "weighted_profile_3",
            "interval_multiply_nonnegative",
            ("weight_3", "Phi_3"),
        ),
        (
            "weighted_profile_sum",
            "interval_add_nonnegative",
            (
                "weighted_profile_0",
                "weighted_profile_1",
                "weighted_profile_2",
                "weighted_profile_3",
            ),
        ),
        (
            "contact_weighted_sum",
            "interval_multiply_nonnegative",
            ("C_contact", "weighted_profile_sum"),
        ),
        ("V", "interval_divide_positive", ("contact_weighted_sum", "W_norm")),
        (
            "K_direct_numerator",
            "interval_multiply_nonnegative",
            ("V", "pi_h"),
        ),
        ("K_direct", "interval_divide_positive", ("K_direct_numerator", "M_pi")),
        ("K_via_rho", "interval_divide_positive", ("V", "rho")),
        (
            "physical_weight_left",
            "interval_multiply_nonnegative",
            ("M_pi", "K_direct"),
        ),
        (
            "physical_weight_right",
            "interval_multiply_nonnegative",
            ("pi_h", "V"),
        ),
    )
    outward_nodes = [
        {
            "argument_ids": list(argument_ids),
            "node_id": node_id,
            "operation": operation,
        }
        for node_id, operation, argument_ids in outward_node_specs
    ]
    outward_assertion_specs = (
        (
            "common_flux_inside_direct_left",
            "direct_left_kappa_interval",
            "interval_contains",
            "common_kappa_interval",
        ),
        (
            "common_flux_inside_direct_right",
            "direct_right_kappa_interval",
            "interval_contains",
            "common_kappa_interval",
        ),
        (
            "common_flux_inside_forward",
            "forward_product_kappa_interval",
            "interval_contains",
            "common_kappa_interval",
        ),
        (
            "common_flux_inside_reverse",
            "reverse_product_kappa_interval",
            "interval_contains",
            "common_kappa_interval",
        ),
        ("K_paths_equal_outward", "K_direct", "interval_equal", "K_via_rho"),
        (
            "physical_identity_outward_contains",
            "physical_weight_left",
            "interval_contains",
            "physical_weight_right",
        ),
    )
    outward_assertions = [
        {
            "assertion_id": assertion_id,
            "left_id": left_id,
            "relation": relation,
            "right_id": right_id,
        }
        for assertion_id, left_id, relation, right_id in outward_assertion_specs
    ]
    outward_output_ids = (
        "G",
        "pi_h",
        "forward_product_kappa_interval",
        "reverse_product_kappa_interval",
        "common_kappa_interval",
        "conductance",
        "rho",
        "V",
        "K_direct",
        "K_via_rho",
        "physical_weight_left",
        "physical_weight_right",
    )

    positive_atoms = (
        "M_L",
        "S_M",
        "S_R",
        "S_Y",
        "mu_M",
        "mu_R",
        "mu_Y",
        "mu_edge_left",
        "mu_edge_right",
        "M_pi",
        "W_norm",
    )
    nonnegative_atoms = (
        "kappa",
        "C_contact",
        "weight_0",
        "weight_1",
        "weight_2",
        "weight_3",
        "Phi_0",
        "Phi_1",
        "Phi_2",
        "Phi_3",
    )
    formal_atoms = [
        {
            "atom_id": atom_id,
            "authority_binding": "fixed_formula_exact_real_quantity",
            "domain": (
                "positive_invertible_exact_real"
                if atom_id in positive_atoms
                else "nonnegative_exact_real"
            ),
        }
        for atom_id in (*positive_atoms, *nonnegative_atoms)
    ]
    formal_node_specs = (
        ("axis_mass_product_formula", "formal_multiply", ("S_M", "S_R", "S_Y")),
        ("G_formula", "formal_divide_monomial", ("M_L", "axis_mass_product_formula")),
        (
            "pi_h_formula",
            "formal_multiply",
            ("G_formula", "mu_M", "mu_R", "mu_Y"),
        ),
        ("q_forward_formula", "formal_divide_monomial", ("kappa", "mu_edge_left")),
        ("q_reverse_formula", "formal_divide_monomial", ("kappa", "mu_edge_right")),
        (
            "flux_forward_formula",
            "formal_multiply",
            ("mu_edge_left", "q_forward_formula"),
        ),
        (
            "flux_reverse_formula",
            "formal_multiply",
            ("mu_edge_right", "q_reverse_formula"),
        ),
        ("kappa_direct_left_formula", "formal_identity", ("kappa",)),
        ("kappa_direct_right_formula", "formal_identity", ("kappa",)),
        ("common_flux_formula", "formal_identity", ("kappa",)),
        (
            "conductance_formula",
            "formal_multiply",
            ("G_formula", "common_flux_formula", "mu_R", "mu_Y"),
        ),
        ("rho_formula", "formal_divide_monomial", ("M_pi", "pi_h_formula")),
        (
            "weighted_profile_0_formula",
            "formal_multiply",
            ("weight_0", "Phi_0"),
        ),
        (
            "weighted_profile_1_formula",
            "formal_multiply",
            ("weight_1", "Phi_1"),
        ),
        (
            "weighted_profile_2_formula",
            "formal_multiply",
            ("weight_2", "Phi_2"),
        ),
        (
            "weighted_profile_3_formula",
            "formal_multiply",
            ("weight_3", "Phi_3"),
        ),
        (
            "weighted_profile_sum_formula",
            "formal_add",
            (
                "weighted_profile_0_formula",
                "weighted_profile_1_formula",
                "weighted_profile_2_formula",
                "weighted_profile_3_formula",
            ),
        ),
        (
            "contact_weighted_sum_formula",
            "formal_multiply",
            ("C_contact", "weighted_profile_sum_formula"),
        ),
        (
            "V_formula",
            "formal_divide_monomial",
            ("contact_weighted_sum_formula", "W_norm"),
        ),
        (
            "K_direct_numerator_formula",
            "formal_multiply",
            ("V_formula", "pi_h_formula"),
        ),
        (
            "K_direct_formula",
            "formal_divide_monomial",
            ("K_direct_numerator_formula", "M_pi"),
        ),
        ("K_via_rho_formula", "formal_divide_monomial", ("V_formula", "rho_formula")),
        (
            "physical_weight_left_formula",
            "formal_multiply",
            ("M_pi", "K_direct_formula"),
        ),
        (
            "physical_weight_right_formula",
            "formal_multiply",
            ("pi_h_formula", "V_formula"),
        ),
    )
    formal_nodes = [
        {
            "argument_ids": list(argument_ids),
            "node_id": node_id,
            "operation": operation,
        }
        for node_id, operation, argument_ids in formal_node_specs
    ]
    formal_assertion_specs = (
        (
            "direct_left_equals_common_formula",
            "kappa_direct_left_formula",
            "formal_equal",
            "common_flux_formula",
        ),
        (
            "direct_right_equals_common_formula",
            "kappa_direct_right_formula",
            "formal_equal",
            "common_flux_formula",
        ),
        (
            "forward_equals_common_formula",
            "flux_forward_formula",
            "formal_equal",
            "common_flux_formula",
        ),
        (
            "reverse_equals_common_formula",
            "flux_reverse_formula",
            "formal_equal",
            "common_flux_formula",
        ),
        (
            "K_paths_equal_formula",
            "K_direct_formula",
            "formal_equal",
            "K_via_rho_formula",
        ),
        (
            "physical_identity_exact_formula",
            "physical_weight_left_formula",
            "formal_equal",
            "physical_weight_right_formula",
        ),
    )
    formal_assertions = [
        {
            "assertion_id": assertion_id,
            "left_id": left_id,
            "relation": relation,
            "right_id": right_id,
        }
        for assertion_id, left_id, relation, right_id in formal_assertion_specs
    ]
    formal_output_ids = (
        "G_formula",
        "pi_h_formula",
        "q_forward_formula",
        "q_reverse_formula",
        "kappa_direct_left_formula",
        "kappa_direct_right_formula",
        "flux_forward_formula",
        "flux_reverse_formula",
        "common_flux_formula",
        "conductance_formula",
        "rho_formula",
        "V_formula",
        "K_direct_formula",
        "K_via_rho_formula",
        "physical_weight_left_formula",
        "physical_weight_right_formula",
    )
    return {
        "formal_assertions": formal_assertions,
        "formal_atoms": formal_atoms,
        "formal_nodes": formal_nodes,
        "formal_outputs": [
            {"output_name": value_id, "value_id": value_id} for value_id in formal_output_ids
        ],
        "outward_assertions": outward_assertions,
        "outward_inputs": outward_inputs,
        "outward_nodes": outward_nodes,
        "outward_outputs": [
            {"output_name": value_id, "value_id": value_id} for value_id in outward_output_ids
        ],
        "template_schema": (
            "encounter_continuum_c1_n0_candidate_native_exact_expression_dag_semantic_template_v2"
        ),
    }


SEMANTIC_TEMPLATE: Final = make_semantic_template()


class DagBuildError(ValueError):
    """The request, filesystem boundary, or exact evaluation was invalid."""


@dataclass(frozen=True)
class ExactInterval:
    kind: str
    lower: Fraction
    upper: Fraction


@dataclass(frozen=True)
class FormalPolynomial:
    terms: tuple[tuple[tuple[int, ...], Fraction], ...]


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 48:
        raise DagBuildError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise DagBuildError("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise DagBuildError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise DagBuildError("invalid JSON object key")
            strict_tree(item, depth + 1)
        return
    raise DagBuildError(f"forbidden JSON type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


SEMANTIC_TEMPLATE_SHA256: Final = sha256(TEMPLATE_DOMAIN + canonical_bytes(SEMANTIC_TEMPLATE))


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise DagBuildError(f"duplicate or invalid JSON key: {key!r}")
        result[key] = value
    return result


def reject_noninteger(token: str) -> Any:
    raise DagBuildError(f"non-integer JSON number forbidden: {token}")


def parse_canonical(payload: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=unique_pairs,
            parse_float=reject_noninteger,
            parse_constant=reject_noninteger,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise DagBuildError(f"strict JSON failure for {context}: {error}") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise DagBuildError(f"canonical ASCII JSON object required: {context}")
    return value


def stat_signature(item: os.stat_result) -> tuple[int, ...]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_nlink,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


def close_descriptors(descriptors: tuple[int, ...] | list[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def close_descriptors_safely(descriptors: tuple[int, ...] | list[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except BaseException:
            pass


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
            name="exact-dag-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o444,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            observed = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(observed.st_mode)
                or observed.st_nlink != 1
                or observed.st_size != 0
            ):
                raise DagBuildError("new staging inode invariant failure")
            self.identity = observed.st_dev, observed.st_ino
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
            raise DagBuildError("stage creation transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise DagBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def open_anchored_parent(
    path: Path,
) -> tuple[tuple[int, ...], str, tuple[tuple[int, int], ...]]:
    if (
        not path.is_absolute()
        or path != Path(os.path.abspath(path))
        or len(path.parts) < 2
        or any(part in {"", ".", ".."} for part in path.parts[1:])
    ):
        raise DagBuildError(f"canonical absolute leaf path required: {path}")
    if not all(hasattr(os, name) for name in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")):
        raise DagBuildError("O_DIRECTORY, O_NOFOLLOW, and O_NONBLOCK are required")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        root = os.open(path.anchor, flags)
        descriptors.append(root)
        root_stat = os.fstat(root)
        if not stat.S_ISDIR(root_stat.st_mode):
            raise DagBuildError("filesystem anchor is not a directory")
        identities.append((root_stat.st_dev, root_stat.st_ino))
        for component in path.parts[1:-1]:
            descriptor = os.open(component, flags, dir_fd=descriptors[-1])
            descriptors.append(descriptor)
            component_stat = os.fstat(descriptor)
            if not stat.S_ISDIR(component_stat.st_mode):
                raise DagBuildError(f"non-directory path component: {component}")
            identities.append((component_stat.st_dev, component_stat.st_ino))
        return tuple(descriptors), path.parts[-1], tuple(identities)
    except OSError as error:
        close_descriptors(descriptors)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise DagBuildError("symlink or non-directory path component rejected") from error
        raise
    except Exception:
        close_descriptors(descriptors)
        raise


def verify_anchored_parent(
    path: Path,
    expected_identities: tuple[tuple[int, int], ...],
) -> None:
    descriptors, _, observed_identities = open_anchored_parent(path)
    try:
        if observed_identities != expected_identities:
            raise DagBuildError(f"directory chain changed during operation: {path}")
    finally:
        close_descriptors(descriptors)


def require_false_claim_map(value: Any, context: str) -> None:
    if (
        type(value) is not dict
        or set(value) != set(CLAIM_KEYS)
        or any(item is not False for item in value.values())
    ):
        raise DagBuildError(f"exact false claim map required: {context}")


def snapshot_leaf_at(
    parent_descriptor: int,
    leaf: str,
    path: Path,
    *,
    immutable: bool,
    cap: int,
) -> bytes:
    try:
        descriptor = os.open(
            leaf,
            os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=parent_descriptor,
        )
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise DagBuildError(f"symlink leaf rejected: {path}") from error
        raise
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > cap
            or (immutable and before.st_mode & 0o222)
        ):
            raise DagBuildError(f"immutable single-link regular file required: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise DagBuildError(f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise DagBuildError(f"file grew during read: {path}")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    named = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
    if stat_signature(before) != stat_signature(after) or stat_signature(named) != stat_signature(
        after
    ):
        raise DagBuildError(f"file changed or was replaced during snapshot: {path}")
    return b"".join(chunks)


def stable_snapshot(path: Path, *, immutable: bool, cap: int = 2_000_000) -> bytes:
    descriptors, leaf, identities = open_anchored_parent(path)
    try:
        payload = snapshot_leaf_at(
            descriptors[-1],
            leaf,
            path,
            immutable=immutable,
            cap=cap,
        )
        verify_anchored_parent(path, identities)
        return payload
    finally:
        close_descriptors(descriptors)


def unlink_owned_leaf(
    parent_descriptor: int,
    leaf: str,
    expected_identity: tuple[int, int],
) -> bool:
    try:
        observed = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if (observed.st_dev, observed.st_ino) != expected_identity:
        return False
    os.unlink(leaf, dir_fd=parent_descriptor)
    return True


def parent_descriptor_matches(
    descriptor: int,
    expected_identity: tuple[int, int],
) -> bool:
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
        == expected_identity
    )


def rational(value: Any) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise DagBuildError(f"canonical p/q rational required: {value!r}")
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise DagBuildError(f"invalid rational: {value!r}") from error
    if f"{parsed.numerator}/{parsed.denominator}" != value:
        raise DagBuildError(f"noncanonical rational: {value!r}")
    return parsed


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def validate_identifier(value: Any, context: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    if (
        type(value) is not str
        or not value
        or len(value) > 96
        or not value[0].isalpha()
        or any(character not in allowed for character in value)
    ):
        raise DagBuildError(f"invalid identifier for {context}: {value!r}")
    return value


def interval(kind: str, lower: Fraction, upper: Fraction) -> ExactInterval:
    if lower > upper:
        raise DagBuildError("interval lower exceeds upper")
    if kind == "interval_nonnegative" and lower < 0:
        raise DagBuildError("nonnegative interval has negative lower endpoint")
    if kind == "interval_positive" and lower <= 0:
        raise DagBuildError("positive interval has nonpositive lower endpoint")
    if kind not in INPUT_TYPES:
        raise DagBuildError(f"invalid interval kind: {kind}")
    return ExactInterval(kind, lower, upper)


def parse_input(entry: Any, binding: dict[str, str]) -> tuple[str, ExactInterval]:
    if type(entry) is not dict or set(entry) != {
        "input_id",
        "lower_exact",
        "provenance_lane",
        "upper_exact",
        "value_type",
    }:
        raise DagBuildError("outward interval input key drift")
    input_id = validate_identifier(entry["input_id"], "input")
    if (
        input_id != binding["input_id"]
        or entry["value_type"] != binding["value_type"]
        or entry["provenance_lane"] != binding["provenance_lane"]
        or binding["semantic_shape"] != "interval"
        or entry["value_type"] not in INPUT_TYPES
    ):
        raise DagBuildError(f"outward interval semantic binding drift: {input_id}")
    return input_id, interval(
        entry["value_type"],
        rational(entry["lower_exact"]),
        rational(entry["upper_exact"]),
    )


def require_interval(value: ExactInterval, context: str) -> ExactInterval:
    if value.kind not in INPUT_TYPES:
        raise DagBuildError(f"interval required: {context}")
    return value


def evaluate_interval_operation(
    operation: str,
    arguments: list[ExactInterval],
) -> ExactInterval:
    values = [require_interval(value, operation) for value in arguments]
    if operation == "interval_add_nonnegative":
        if len(values) < 2:
            raise DagBuildError("interval_add_nonnegative arity")
        kind = (
            "interval_positive"
            if any(value.kind == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return interval(
            kind,
            sum((value.lower for value in values), Fraction()),
            sum((value.upper for value in values), Fraction()),
        )
    if operation == "interval_multiply_nonnegative":
        if len(values) < 2:
            raise DagBuildError("interval_multiply_nonnegative arity")
        lower = Fraction(1)
        upper = Fraction(1)
        for value in values:
            lower *= value.lower
            upper *= value.upper
        kind = (
            "interval_positive"
            if all(value.kind == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return interval(kind, lower, upper)
    if operation == "interval_divide_positive":
        if len(values) != 2 or values[1].kind != "interval_positive":
            raise DagBuildError("positive interval denominator required")
        numerator, denominator = values
        return interval(
            numerator.kind,
            numerator.lower / denominator.upper,
            numerator.upper / denominator.lower,
        )
    if operation == "interval_intersection":
        if len(values) < 2:
            raise DagBuildError("interval_intersection arity")
        lower = max(value.lower for value in values)
        upper = min(value.upper for value in values)
        if lower > upper:
            raise DagBuildError("empty interval intersection")
        kind = (
            "interval_positive"
            if all(value.kind == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return interval(kind, lower, upper)
    raise DagBuildError(f"unsupported interval operation: {operation}")


def serialize_interval(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact": rational_text(value.lower),
        "upper_exact": rational_text(value.upper),
        "value_type": value.kind,
    }


def normalize_formal(
    items: list[tuple[tuple[int, ...], Fraction]],
    *,
    atom_count: int,
    invertible_indices: frozenset[int],
) -> FormalPolynomial:
    totals: dict[tuple[int, ...], Fraction] = {}
    for exponents, coefficient in items:
        if len(exponents) != atom_count or any(
            type(exponent) is not int or abs(exponent) > 16 for exponent in exponents
        ):
            raise DagBuildError("invalid formal exponent vector")
        if any(
            exponent < 0 and index not in invertible_indices
            for index, exponent in enumerate(exponents)
        ):
            raise DagBuildError("negative exponent on noninvertible formal atom")
        totals[exponents] = totals.get(exponents, Fraction()) + coefficient
    return FormalPolynomial(
        tuple(
            (exponents, coefficient)
            for exponents, coefficient in sorted(totals.items())
            if coefficient
        )
    )


def multiply_formal(
    arguments: list[FormalPolynomial],
    *,
    atom_count: int,
    invertible_indices: frozenset[int],
) -> FormalPolynomial:
    if len(arguments) < 2:
        raise DagBuildError("formal_multiply arity")
    result = FormalPolynomial(((tuple(0 for _ in range(atom_count)), Fraction(1)),))
    for argument in arguments:
        products = [
            (
                tuple(left + right for left, right in zip(left_exp, right_exp, strict=True)),
                left_coefficient * right_coefficient,
            )
            for left_exp, left_coefficient in result.terms
            for right_exp, right_coefficient in argument.terms
        ]
        result = normalize_formal(
            products,
            atom_count=atom_count,
            invertible_indices=invertible_indices,
        )
    return result


def apply_formal_operation(
    operation: str,
    arguments: list[FormalPolynomial],
    *,
    atom_count: int,
    invertible_indices: frozenset[int],
) -> FormalPolynomial:
    if operation == "formal_identity":
        if len(arguments) != 1:
            raise DagBuildError("formal_identity arity")
        return arguments[0]
    if operation == "formal_add":
        if len(arguments) < 2:
            raise DagBuildError("formal_add arity")
        return normalize_formal(
            [term for argument in arguments for term in argument.terms],
            atom_count=atom_count,
            invertible_indices=invertible_indices,
        )
    if operation == "formal_multiply":
        return multiply_formal(
            arguments,
            atom_count=atom_count,
            invertible_indices=invertible_indices,
        )
    if operation == "formal_divide_monomial":
        if len(arguments) != 2 or len(arguments[1].terms) != 1:
            raise DagBuildError("formal division requires one monomial denominator")
        denominator_exp, denominator_coefficient = arguments[1].terms[0]
        if denominator_coefficient == 0:
            raise DagBuildError("formal division by zero")
        return normalize_formal(
            [
                (
                    tuple(
                        numerator - denominator
                        for numerator, denominator in zip(
                            numerator_exp, denominator_exp, strict=True
                        )
                    ),
                    numerator_coefficient / denominator_coefficient,
                )
                for numerator_exp, numerator_coefficient in arguments[0].terms
            ],
            atom_count=atom_count,
            invertible_indices=invertible_indices,
        )
    raise DagBuildError(f"unsupported formal operation: {operation}")


def serialize_formal(value: FormalPolynomial) -> dict[str, Any]:
    return {
        "terms": [
            {
                "coefficient_exact": rational_text(coefficient),
                "exponents": list(exponents),
            }
            for exponents, coefficient in value.terms
        ],
        "value_type": FORMAL_SCHEMA,
    }


def evaluate_outward(inputs: list[Any]) -> dict[str, Any]:
    bindings = SEMANTIC_TEMPLATE["outward_inputs"]
    if len(inputs) != len(bindings):
        raise DagBuildError("outward input cardinality drift")
    values: dict[str, ExactInterval] = {}
    input_receipts: list[dict[str, Any]] = []
    for index, entry in enumerate(inputs):
        binding = bindings[index]
        input_id, value = parse_input(entry, binding)
        if input_id in values:
            raise DagBuildError(f"duplicate outward input: {input_id}")
        values[input_id] = value
        input_receipts.append(
            {
                "formal_value_id": binding["formal_value_id"],
                "input_id": input_id,
                "provenance_lane": binding["provenance_lane"],
                **serialize_interval(value),
            }
        )

    node_receipts: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["outward_nodes"]:
        node_id = validate_identifier(entry["node_id"], "outward node")
        operation = entry["operation"]
        argument_ids = entry["argument_ids"]
        if (
            type(entry) is not dict
            or set(entry) != {"argument_ids", "node_id", "operation"}
            or node_id in values
            or operation not in INTERVAL_OPERATIONS
            or type(argument_ids) is not list
            or any(type(argument_id) is not str for argument_id in argument_ids)
            or any(argument_id not in values for argument_id in argument_ids)
        ):
            raise DagBuildError(f"invalid or unordered outward node: {node_id}")
        value = evaluate_interval_operation(
            operation,
            [values[argument_id] for argument_id in argument_ids],
        )
        values[node_id] = value
        node_ids.add(node_id)
        node_receipts.append({**entry, "value": serialize_interval(value)})

    assertion_receipts: list[dict[str, Any]] = []
    seen_assertions: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["outward_assertions"]:
        assertion_id = validate_identifier(entry["assertion_id"], "outward assertion")
        relation = entry["relation"]
        if (
            type(entry) is not dict
            or set(entry) != {"assertion_id", "left_id", "relation", "right_id"}
            or assertion_id in seen_assertions
            or relation not in INTERVAL_RELATIONS
            or entry["left_id"] not in values
            or entry["right_id"] not in values
        ):
            raise DagBuildError(f"invalid outward assertion: {assertion_id}")
        left = values[entry["left_id"]]
        right = values[entry["right_id"]]
        holds = (
            (left.lower, left.upper) == (right.lower, right.upper)
            if relation == "interval_equal"
            else left.lower <= right.lower and left.upper >= right.upper
        )
        if not holds:
            raise DagBuildError(f"outward interval assertion failed: {assertion_id}")
        seen_assertions.add(assertion_id)
        assertion_receipts.append({**entry, "holds": True})

    output_receipts: list[dict[str, Any]] = []
    seen_outputs: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["outward_outputs"]:
        if (
            type(entry) is not dict
            or set(entry) != {"output_name", "value_id"}
            or entry["output_name"] in seen_outputs
            or entry["value_id"] not in node_ids
        ):
            raise DagBuildError("invalid outward output binding")
        seen_outputs.add(entry["output_name"])
        output_receipts.append({**entry, "value": serialize_interval(values[entry["value_id"]])})
    return {
        "assertion_count": len(assertion_receipts),
        "assertions": assertion_receipts,
        "input_count": len(input_receipts),
        "inputs": input_receipts,
        "node_count": len(node_receipts),
        "nodes": node_receipts,
        "operation_set": sorted({record["operation"] for record in node_receipts}),
        "output_count": len(output_receipts),
        "outputs": output_receipts,
        "topological_order": [record["node_id"] for record in node_receipts],
        "value_semantics": "outward_interval_arithmetic_no_exact_member_selector",
    }


def evaluate_formal() -> dict[str, Any]:
    atom_records = SEMANTIC_TEMPLATE["formal_atoms"]
    atom_count = len(atom_records)
    atom_ids = [record["atom_id"] for record in atom_records]
    if len(set(atom_ids)) != atom_count:
        raise DagBuildError("duplicate formal atom")
    invertible_indices = frozenset(
        index
        for index, record in enumerate(atom_records)
        if record["domain"] == "positive_invertible_exact_real"
    )
    values: dict[str, FormalPolynomial] = {}
    for index, record in enumerate(atom_records):
        if type(record) is not dict or set(record) != {
            "atom_id",
            "authority_binding",
            "domain",
        }:
            raise DagBuildError("formal atom template drift")
        exponents = [0] * atom_count
        exponents[index] = 1
        values[record["atom_id"]] = FormalPolynomial(((tuple(exponents), Fraction(1)),))

    node_receipts: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["formal_nodes"]:
        node_id = validate_identifier(entry["node_id"], "formal node")
        operation = entry["operation"]
        argument_ids = entry["argument_ids"]
        if (
            type(entry) is not dict
            or set(entry) != {"argument_ids", "node_id", "operation"}
            or node_id in values
            or operation not in FORMAL_OPERATIONS
            or type(argument_ids) is not list
            or any(type(argument_id) is not str for argument_id in argument_ids)
            or any(argument_id not in values for argument_id in argument_ids)
        ):
            raise DagBuildError(f"invalid or unordered formal node: {node_id}")
        value = apply_formal_operation(
            operation,
            [values[argument_id] for argument_id in argument_ids],
            atom_count=atom_count,
            invertible_indices=invertible_indices,
        )
        values[node_id] = value
        node_ids.add(node_id)
        node_receipts.append({**entry, "value": serialize_formal(value)})

    assertion_receipts: list[dict[str, Any]] = []
    seen_assertions: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["formal_assertions"]:
        assertion_id = validate_identifier(entry["assertion_id"], "formal assertion")
        if (
            type(entry) is not dict
            or set(entry) != {"assertion_id", "left_id", "relation", "right_id"}
            or assertion_id in seen_assertions
            or entry["relation"] != "formal_equal"
            or entry["left_id"] not in values
            or entry["right_id"] not in values
        ):
            raise DagBuildError(f"invalid formal assertion: {assertion_id}")
        if values[entry["left_id"]] != values[entry["right_id"]]:
            raise DagBuildError(f"formal identity assertion failed: {assertion_id}")
        seen_assertions.add(assertion_id)
        assertion_receipts.append({**entry, "holds": True})

    output_receipts: list[dict[str, Any]] = []
    seen_outputs: set[str] = set()
    for entry in SEMANTIC_TEMPLATE["formal_outputs"]:
        if (
            type(entry) is not dict
            or set(entry) != {"output_name", "value_id"}
            or entry["output_name"] in seen_outputs
            or entry["value_id"] not in node_ids
        ):
            raise DagBuildError("invalid formal output binding")
        seen_outputs.add(entry["output_name"])
        output_receipts.append({**entry, "value": serialize_formal(values[entry["value_id"]])})
    return {
        "algebra_schema": FORMAL_SCHEMA,
        "assumption_scope": "conditional_on_authority_bound_exact_real_atoms",
        "assertion_count": len(assertion_receipts),
        "assertions": assertion_receipts,
        "atom_count": atom_count,
        "atom_order": atom_ids,
        "atoms": atom_records,
        "node_count": len(node_receipts),
        "nodes": node_receipts,
        "normalization": {
            "coefficient": "reduced_Fraction",
            "exponent_order": "fixed_atom_order_lexicographic",
            "zero_polynomial": "empty_terms",
        },
        "operation_set": sorted({record["operation"] for record in node_receipts}),
        "output_count": len(output_receipts),
        "outputs": output_receipts,
        "proof_scope": "fixed_formula_identities_without_numeric_exact_selectors",
        "topological_order": [record["node_id"] for record in node_receipts],
    }


def evaluate_request(request: dict[str, Any], request_payload: bytes) -> dict[str, Any]:
    if set(request) != {
        "claim_boundary",
        "inputs",
        "schema",
        "semantic_template",
        "semantic_template_sha256",
        "status",
    }:
        raise DagBuildError("request top-level key drift")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != "OUTWARD_INTERVALS_AND_FIXED_FORMAL_IDENTITIES_ONLY"
    ):
        raise DagBuildError("request identity drift")
    require_false_claim_map(request["claim_boundary"], "request")
    if request["semantic_template"] != SEMANTIC_TEMPLATE:
        raise DagBuildError("fixed semantic template drift")
    if (
        type(request["semantic_template_sha256"]) is not str
        or request["semantic_template_sha256"] != SEMANTIC_TEMPLATE_SHA256
    ):
        raise DagBuildError("domain-separated semantic template SHA drift")
    if type(request["inputs"]) is not list:
        raise DagBuildError("outward input list required")

    outward = evaluate_outward(request["inputs"])
    formal = evaluate_formal()
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "formal_identity_proof": formal,
        "formal_identity_proof_sha256": sha256(FORMAL_DOMAIN + canonical_bytes(formal)),
        "outward_interval_evaluation": outward,
        "outward_interval_evaluation_sha256": sha256(OUTWARD_DOMAIN + canonical_bytes(outward)),
        "request": {
            "byte_length": len(request_payload),
            "schema": REQUEST_SCHEMA,
            "semantic_template_sha256": SEMANTIC_TEMPLATE_SHA256,
            "sha256": sha256(request_payload),
        },
        "schema": ARTIFACT_SCHEMA,
        "semantic_template": SEMANTIC_TEMPLATE,
        "semantic_template_sha256": SEMANTIC_TEMPLATE_SHA256,
        "status": (
            "PASS_OUTWARD_INTERVAL_ARITHMETIC_AND_FIXED_FORMAL_IDENTITIES_"
            "NO_PRODUCTION_DATA_NO_REPLAY_NO_ACCEPTANCE"
        ),
    }


def write_immutable_exclusive(path: Path, payload: bytes) -> None:
    descriptors, leaf, identities = open_anchored_parent(path)
    parent_descriptor = descriptors[-1]
    recovery_descriptors: tuple[int, ...] = ()
    stage_name: str | None = None
    stage_attempted = False
    final_attempted = False
    stage_transaction: StageCreationTransaction | None = None
    stage_descriptor: int | None = None
    stage_identity: tuple[int, int] | None = None
    try:
        for _ in range(16):
            candidate = f".candidate-exact-dag-stage-{secrets.token_hex(16)}"
            if candidate == leaf:
                continue
            stage_name = candidate
            stage_attempted = True
            stage_transaction = StageCreationTransaction(parent_descriptor, candidate)
            try:
                stage_transaction.start()
                stage_transaction.await_ready()
                stage_descriptor = stage_transaction.descriptor
                stage_identity = stage_transaction.identity
                if stage_descriptor is None or stage_identity is None:
                    raise DagBuildError("stage transaction result missing")
                stage_transaction.release_descriptor(stage_descriptor)
                break
            except FileExistsError:
                stage_transaction.settle()
                stage_transaction = None
                stage_name = None
                stage_attempted = False
                continue
        if stage_descriptor is None or stage_name is None:
            raise DagBuildError("could not reserve same-directory staging file")

        written = 0
        while written < len(payload):
            count = os.write(stage_descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise DagBuildError("short output write")
            written += count
        os.fchmod(stage_descriptor, 0o444)
        os.fsync(stage_descriptor)
        os.close(stage_descriptor)
        stage_descriptor = None

        final_attempted = True
        try:
            os.link(
                stage_name,
                leaf,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise DagBuildError("output already exists; use --check") from error
        if stage_identity is None or not unlink_owned_leaf(
            parent_descriptor,
            stage_name,
            stage_identity,
        ):
            raise DagBuildError("same-directory staging identity changed")

        observed = snapshot_leaf_at(
            parent_descriptor,
            leaf,
            path,
            immutable=True,
            cap=max(2_000_000, len(payload)),
        )
        if observed != payload:
            raise DagBuildError("stable staged output reread mismatch")
        verify_anchored_parent(path, identities)
        os.fsync(parent_descriptor)
        close_descriptors(descriptors)
        descriptors = ()
    except BaseException:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_identity is None:
                stage_identity = stage_transaction.identity
            if stage_transaction.descriptor is not None:
                if stage_descriptor is None:
                    stage_descriptor = stage_transaction.descriptor
                elif stage_descriptor != stage_transaction.descriptor:
                    close_descriptors_safely((stage_transaction.descriptor,))
                stage_transaction.descriptor = None
        if stage_descriptor is not None and stage_identity is None:
            try:
                stage_stat = _STAGE_FSTAT(stage_descriptor)
                stage_identity = (stage_stat.st_dev, stage_stat.st_ino)
            except BaseException:
                pass
        if stage_descriptor is not None:
            close_descriptors_safely((stage_descriptor,))
            stage_descriptor = None

        cleanup_parent: int | None = None
        if parent_descriptor_matches(parent_descriptor, identities[-1]):
            cleanup_parent = parent_descriptor
        else:
            try:
                recovered, recovered_leaf, recovered_identities = open_anchored_parent(path)
                if recovered_leaf == leaf and recovered_identities == identities:
                    recovery_descriptors = recovered
                    cleanup_parent = recovered[-1]
                else:
                    close_descriptors_safely(recovered)
            except BaseException:
                pass

        if cleanup_parent is not None:
            if final_attempted and stage_identity is not None:
                try:
                    unlink_owned_leaf(cleanup_parent, leaf, stage_identity)
                except BaseException:
                    pass
            if stage_attempted and stage_name is not None and stage_identity is not None:
                try:
                    unlink_owned_leaf(cleanup_parent, stage_name, stage_identity)
                except BaseException:
                    pass
            try:
                os.fsync(cleanup_parent)
            except BaseException:
                pass
        raise
    finally:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_transaction.descriptor is not None:
                close_descriptors_safely((stage_transaction.descriptor,))
                stage_transaction.descriptor = None
        if stage_descriptor is not None:
            close_descriptors_safely((stage_descriptor,))
        close_descriptors_safely(recovery_descriptors)
        close_descriptors_safely(descriptors)


def build_or_check(request_path: Path, output_path: Path, *, check: bool) -> str:
    if not request_path.is_absolute() or not output_path.is_absolute():
        raise DagBuildError("request and output paths must be absolute")
    if os.path.abspath(request_path) == os.path.abspath(output_path):
        raise DagBuildError("request and output paths must be distinct")
    request_payload = stable_snapshot(request_path, immutable=True)
    request = parse_canonical(request_payload, "request")
    expected = canonical_bytes(evaluate_request(request, request_payload))
    if check:
        observed = stable_snapshot(output_path, immutable=True)
        if observed != expected:
            raise DagBuildError(f"artifact byte drift: {sha256(observed)} != {sha256(expected)}")
    else:
        write_immutable_exclusive(output_path, expected)
    return sha256(expected)


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        artifact_sha = build_or_check(
            arguments.request,
            arguments.output,
            check=arguments.check,
        )
        print(
            "PASS_CANDIDATE_NATIVE_EXACT_EXPRESSION_DAG_BUILD "
            f"artifact_sha256={artifact_sha} check={str(arguments.check).lower()} "
            "production_data=false replay=false acceptance=false"
        )
        return 0
    except (DagBuildError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"ERROR CandidateNativeExactExpressionDagBuild: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
