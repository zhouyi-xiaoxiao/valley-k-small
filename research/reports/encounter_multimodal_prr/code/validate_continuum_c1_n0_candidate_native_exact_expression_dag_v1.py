#!/usr/bin/env python3
"""Independently reconstruct outward intervals and fixed formal identities."""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import stat
import sys
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Final

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
    """Independently return the closed, value-free formula contract."""
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


class DagVerificationError(ValueError):
    """The retained request or artifact failed independent verification."""


@dataclass(frozen=True)
class Bounds:
    category: str
    lo: Fraction
    hi: Fraction


@dataclass(frozen=True)
class Laurent:
    terms: tuple[tuple[tuple[int, ...], Fraction], ...]


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def inspect_tree(value: Any, depth: int = 0) -> None:
    if depth > 48:
        raise DagVerificationError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise DagVerificationError("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if value != unicodedata.normalize("NFC", value):
            raise DagVerificationError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            inspect_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or key != unicodedata.normalize("NFC", key):
                raise DagVerificationError("invalid JSON key")
            inspect_tree(item, depth + 1)
        return
    raise DagVerificationError(f"forbidden JSON type: {type(value).__name__}")


def canonical(value: Any) -> bytes:
    inspect_tree(value)
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


SEMANTIC_TEMPLATE_SHA256: Final = digest(TEMPLATE_DOMAIN + canonical(SEMANTIC_TEMPLATE))


def distinct_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in output:
            raise DagVerificationError(f"duplicate or invalid JSON key: {key!r}")
        output[key] = value
    return output


def reject_number(token: str) -> Any:
    raise DagVerificationError(f"non-integer JSON number forbidden: {token}")


def decode(payload: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=distinct_pairs,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise DagVerificationError(f"strict JSON failure for {context}: {error}") from error
    if type(value) is not dict or canonical(value) != payload:
        raise DagVerificationError(f"canonical ASCII JSON object required: {context}")
    return value


def signature(item: os.stat_result) -> tuple[int, ...]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_nlink,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


def release_fds(descriptors: tuple[int, ...] | list[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def anchor_parent(
    path: Path,
) -> tuple[tuple[int, ...], str, tuple[tuple[int, int], ...]]:
    if (
        not path.is_absolute()
        or path != Path(os.path.abspath(path))
        or len(path.parts) < 2
        or any(part in {"", ".", ".."} for part in path.parts[1:])
    ):
        raise DagVerificationError(f"canonical absolute leaf path required: {path}")
    if not all(hasattr(os, name) for name in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")):
        raise DagVerificationError("O_DIRECTORY, O_NOFOLLOW, and O_NONBLOCK are required")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        root_descriptor = os.open(path.anchor, flags)
        descriptors.append(root_descriptor)
        root_stat = os.fstat(root_descriptor)
        if not stat.S_ISDIR(root_stat.st_mode):
            raise DagVerificationError("filesystem anchor is not a directory")
        identities.append((root_stat.st_dev, root_stat.st_ino))
        for component in path.parts[1:-1]:
            descriptor = os.open(component, flags, dir_fd=descriptors[-1])
            descriptors.append(descriptor)
            component_stat = os.fstat(descriptor)
            if not stat.S_ISDIR(component_stat.st_mode):
                raise DagVerificationError(f"non-directory path component: {component}")
            identities.append((component_stat.st_dev, component_stat.st_ino))
        return tuple(descriptors), path.parts[-1], tuple(identities)
    except OSError as error:
        release_fds(descriptors)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise DagVerificationError(
                "symlink or non-directory path component rejected"
            ) from error
        raise
    except Exception:
        release_fds(descriptors)
        raise


def confirm_parent(
    path: Path,
    expected_identities: tuple[tuple[int, int], ...],
) -> None:
    descriptors, _, observed_identities = anchor_parent(path)
    try:
        if observed_identities != expected_identities:
            raise DagVerificationError(f"directory chain changed during operation: {path}")
    finally:
        release_fds(descriptors)


def read_leaf(
    parent_descriptor: int,
    leaf: str,
    path: Path,
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
            raise DagVerificationError(f"symlink leaf rejected: {path}") from error
        raise
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > cap
            or before.st_mode & 0o222
        ):
            raise DagVerificationError(f"immutable single-link regular file required: {path}")
        parts: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise DagVerificationError(f"short read: {path}")
            parts.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise DagVerificationError(f"file grew during read: {path}")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    named = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
    if signature(before) != signature(after) or signature(named) != signature(after):
        raise DagVerificationError(f"file changed or was replaced: {path}")
    return b"".join(parts)


def retain(path: Path, cap: int = 2_000_000) -> bytes:
    descriptors, leaf, identities = anchor_parent(path)
    try:
        payload = read_leaf(descriptors[-1], leaf, path, cap)
        confirm_parent(path, identities)
        return payload
    finally:
        release_fds(descriptors)


def require_false_claim_map(value: Any, context: str) -> None:
    if (
        type(value) is not dict
        or set(value) != set(CLAIM_KEYS)
        or any(item is not False for item in value.values())
    ):
        raise DagVerificationError(f"exact false claim map required: {context}")


def q(text: Any) -> Fraction:
    if type(text) is not str or text.count("/") != 1:
        raise DagVerificationError(f"canonical p/q rational required: {text!r}")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise DagVerificationError(f"invalid rational: {text!r}") from error
    if f"{value.numerator}/{value.denominator}" != text:
        raise DagVerificationError(f"noncanonical rational: {text!r}")
    return value


def qs(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def identifier(value: Any, context: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    if (
        type(value) is not str
        or not value
        or len(value) > 96
        or not value[0].isalpha()
        or any(character not in allowed for character in value)
    ):
        raise DagVerificationError(f"invalid identifier for {context}: {value!r}")
    return value


def make_bounds(category: str, lo: Fraction, hi: Fraction) -> Bounds:
    if lo > hi:
        raise DagVerificationError("interval lower exceeds upper")
    if category == "interval_nonnegative" and lo < 0:
        raise DagVerificationError("negative nonnegative interval")
    if category == "interval_positive" and lo <= 0:
        raise DagVerificationError("nonpositive positive interval")
    if category not in INPUT_TYPES:
        raise DagVerificationError("invalid interval type")
    return Bounds(category, lo, hi)


def read_input(record: Any, binding: dict[str, str]) -> tuple[str, Bounds]:
    if type(record) is not dict or set(record) != {
        "input_id",
        "lower_exact",
        "provenance_lane",
        "upper_exact",
        "value_type",
    }:
        raise DagVerificationError("outward input key drift")
    input_id = identifier(record["input_id"], "input")
    if (
        input_id != binding["input_id"]
        or record["value_type"] != binding["value_type"]
        or record["provenance_lane"] != binding["provenance_lane"]
        or binding["semantic_shape"] != "interval"
        or record["value_type"] not in INPUT_TYPES
    ):
        raise DagVerificationError(f"outward interval semantic binding drift: {input_id}")
    return input_id, make_bounds(
        record["value_type"],
        q(record["lower_exact"]),
        q(record["upper_exact"]),
    )


def apply_interval(operation: str, values: list[Bounds]) -> Bounds:
    if operation == "interval_add_nonnegative":
        if len(values) < 2:
            raise DagVerificationError("interval add arity")
        category = (
            "interval_positive"
            if any(value.category == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return make_bounds(
            category,
            sum((value.lo for value in values), Fraction()),
            sum((value.hi for value in values), Fraction()),
        )
    if operation == "interval_multiply_nonnegative":
        if len(values) < 2:
            raise DagVerificationError("interval multiply arity")
        lo = Fraction(1)
        hi = Fraction(1)
        for value in values:
            lo *= value.lo
            hi *= value.hi
        category = (
            "interval_positive"
            if all(value.category == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return make_bounds(category, lo, hi)
    if operation == "interval_divide_positive":
        if len(values) != 2 or values[1].category != "interval_positive":
            raise DagVerificationError("positive denominator interval required")
        return make_bounds(
            values[0].category,
            values[0].lo / values[1].hi,
            values[0].hi / values[1].lo,
        )
    if operation == "interval_intersection":
        if len(values) < 2:
            raise DagVerificationError("interval intersection arity")
        lo = max(value.lo for value in values)
        hi = min(value.hi for value in values)
        if lo > hi:
            raise DagVerificationError("empty interval intersection")
        category = (
            "interval_positive"
            if all(value.category == "interval_positive" for value in values)
            else "interval_nonnegative"
        )
        return make_bounds(category, lo, hi)
    raise DagVerificationError(f"unsupported interval operation: {operation}")


def encode_bounds(value: Bounds) -> dict[str, str]:
    return {
        "lower_exact": qs(value.lo),
        "upper_exact": qs(value.hi),
        "value_type": value.category,
    }


def canonicalize_laurent(
    items: list[tuple[tuple[int, ...], Fraction]],
    atom_count: int,
    invertible: frozenset[int],
) -> Laurent:
    totals: dict[tuple[int, ...], Fraction] = {}
    for exponents, coefficient in items:
        if len(exponents) != atom_count or any(
            type(exponent) is not int or abs(exponent) > 16 for exponent in exponents
        ):
            raise DagVerificationError("invalid formal exponent vector")
        if any(
            exponent < 0 and index not in invertible for index, exponent in enumerate(exponents)
        ):
            raise DagVerificationError("negative exponent on noninvertible formal atom")
        totals[exponents] = totals.get(exponents, Fraction()) + coefficient
    return Laurent(
        tuple(
            (exponents, coefficient)
            for exponents, coefficient in sorted(totals.items())
            if coefficient
        )
    )


def independently_apply_formal(
    operation: str,
    arguments: list[Laurent],
    atom_count: int,
    invertible: frozenset[int],
) -> Laurent:
    if operation == "formal_identity":
        if len(arguments) != 1:
            raise DagVerificationError("formal identity arity")
        return arguments[0]
    if operation == "formal_add":
        if len(arguments) < 2:
            raise DagVerificationError("formal add arity")
        return canonicalize_laurent(
            [term for argument in arguments for term in argument.terms],
            atom_count,
            invertible,
        )
    if operation == "formal_multiply":
        if len(arguments) < 2:
            raise DagVerificationError("formal multiply arity")
        result = Laurent(((tuple(0 for _ in range(atom_count)), Fraction(1)),))
        for argument in arguments:
            result = canonicalize_laurent(
                [
                    (
                        tuple(
                            left + right for left, right in zip(left_exp, right_exp, strict=True)
                        ),
                        left_coefficient * right_coefficient,
                    )
                    for left_exp, left_coefficient in result.terms
                    for right_exp, right_coefficient in argument.terms
                ],
                atom_count,
                invertible,
            )
        return result
    if operation == "formal_divide_monomial":
        if len(arguments) != 2 or len(arguments[1].terms) != 1:
            raise DagVerificationError("formal monomial denominator required")
        denominator_exp, denominator_coefficient = arguments[1].terms[0]
        if denominator_coefficient == 0:
            raise DagVerificationError("formal division by zero")
        return canonicalize_laurent(
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
            atom_count,
            invertible,
        )
    raise DagVerificationError(f"unsupported formal operation: {operation}")


def encode_laurent(value: Laurent) -> dict[str, Any]:
    return {
        "terms": [
            {
                "coefficient_exact": qs(coefficient),
                "exponents": list(exponents),
            }
            for exponents, coefficient in value.terms
        ],
        "value_type": FORMAL_SCHEMA,
    }


def decode_laurent_artifact(
    value: Any,
    atom_count: int,
    invertible: frozenset[int],
) -> Laurent:
    if type(value) is not dict or set(value) != {"terms", "value_type"}:
        raise DagVerificationError("formal value key drift")
    if value["value_type"] != FORMAL_SCHEMA or type(value["terms"]) is not list:
        raise DagVerificationError("formal value schema drift")
    raw_terms: list[tuple[tuple[int, ...], Fraction]] = []
    previous: tuple[int, ...] | None = None
    for term in value["terms"]:
        if type(term) is not dict or set(term) != {"coefficient_exact", "exponents"}:
            raise DagVerificationError("formal term key drift")
        exponents_value = term["exponents"]
        if (
            type(exponents_value) is not list
            or len(exponents_value) != atom_count
            or any(type(exponent) is not int for exponent in exponents_value)
        ):
            raise DagVerificationError("formal exponent vector drift")
        exponents = tuple(exponents_value)
        coefficient = q(term["coefficient_exact"])
        if coefficient == 0:
            raise DagVerificationError("zero formal coefficient forbidden")
        if previous is not None and exponents <= previous:
            raise DagVerificationError("formal terms not strictly canonical")
        previous = exponents
        raw_terms.append((exponents, coefficient))
    normalized = canonicalize_laurent(raw_terms, atom_count, invertible)
    if normalized.terms != tuple(raw_terms):
        raise DagVerificationError("formal normalization drift")
    return normalized


def reconstruct_outward(inputs: list[Any]) -> dict[str, Any]:
    bindings = SEMANTIC_TEMPLATE["outward_inputs"]
    if len(inputs) != len(bindings):
        raise DagVerificationError("outward input cardinality drift")
    values: dict[str, Bounds] = {}
    input_receipts = []
    for index, record in enumerate(inputs):
        binding = bindings[index]
        input_id, value = read_input(record, binding)
        if input_id in values:
            raise DagVerificationError(f"duplicate outward input: {input_id}")
        values[input_id] = value
        input_receipts.append(
            {
                "formal_value_id": binding["formal_value_id"],
                "input_id": input_id,
                "provenance_lane": binding["provenance_lane"],
                **encode_bounds(value),
            }
        )
    node_receipts = []
    node_ids: set[str] = set()
    for record in SEMANTIC_TEMPLATE["outward_nodes"]:
        node_id = identifier(record["node_id"], "outward node")
        operation = record["operation"]
        argument_ids = record["argument_ids"]
        if (
            type(record) is not dict
            or set(record) != {"argument_ids", "node_id", "operation"}
            or node_id in values
            or operation not in INTERVAL_OPERATIONS
            or type(argument_ids) is not list
            or any(type(argument_id) is not str for argument_id in argument_ids)
            or any(argument_id not in values for argument_id in argument_ids)
        ):
            raise DagVerificationError(f"invalid or unordered outward node: {node_id}")
        value = apply_interval(
            operation,
            [values[argument_id] for argument_id in argument_ids],
        )
        values[node_id] = value
        node_ids.add(node_id)
        node_receipts.append({**record, "value": encode_bounds(value)})
    assertion_receipts = []
    assertion_ids: set[str] = set()
    for record in SEMANTIC_TEMPLATE["outward_assertions"]:
        assertion_id = identifier(record["assertion_id"], "outward assertion")
        relation = record["relation"]
        if (
            type(record) is not dict
            or set(record) != {"assertion_id", "left_id", "relation", "right_id"}
            or assertion_id in assertion_ids
            or relation not in INTERVAL_RELATIONS
            or record["left_id"] not in values
            or record["right_id"] not in values
        ):
            raise DagVerificationError(f"invalid outward assertion: {assertion_id}")
        left = values[record["left_id"]]
        right = values[record["right_id"]]
        holds = (
            (left.lo, left.hi) == (right.lo, right.hi)
            if relation == "interval_equal"
            else left.lo <= right.lo and left.hi >= right.hi
        )
        if not holds:
            raise DagVerificationError(f"outward assertion failed: {assertion_id}")
        assertion_ids.add(assertion_id)
        assertion_receipts.append({**record, "holds": True})
    output_receipts = []
    output_names: set[str] = set()
    for record in SEMANTIC_TEMPLATE["outward_outputs"]:
        if (
            type(record) is not dict
            or set(record) != {"output_name", "value_id"}
            or record["output_name"] in output_names
            or record["value_id"] not in node_ids
        ):
            raise DagVerificationError("invalid outward output")
        output_names.add(record["output_name"])
        output_receipts.append({**record, "value": encode_bounds(values[record["value_id"]])})
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


def reconstruct_formal() -> dict[str, Any]:
    atom_records = SEMANTIC_TEMPLATE["formal_atoms"]
    atom_count = len(atom_records)
    atom_ids = [record["atom_id"] for record in atom_records]
    if len(set(atom_ids)) != atom_count:
        raise DagVerificationError("duplicate formal atom")
    invertible = frozenset(
        index
        for index, record in enumerate(atom_records)
        if record["domain"] == "positive_invertible_exact_real"
    )
    values: dict[str, Laurent] = {}
    for index, record in enumerate(atom_records):
        if type(record) is not dict or set(record) != {
            "atom_id",
            "authority_binding",
            "domain",
        }:
            raise DagVerificationError("formal atom template drift")
        exponents = [0] * atom_count
        exponents[index] = 1
        values[record["atom_id"]] = Laurent(((tuple(exponents), Fraction(1)),))
    node_receipts = []
    node_ids: set[str] = set()
    for record in SEMANTIC_TEMPLATE["formal_nodes"]:
        node_id = identifier(record["node_id"], "formal node")
        operation = record["operation"]
        argument_ids = record["argument_ids"]
        if (
            type(record) is not dict
            or set(record) != {"argument_ids", "node_id", "operation"}
            or node_id in values
            or operation not in FORMAL_OPERATIONS
            or type(argument_ids) is not list
            or any(type(argument_id) is not str for argument_id in argument_ids)
            or any(argument_id not in values for argument_id in argument_ids)
        ):
            raise DagVerificationError(f"invalid or unordered formal node: {node_id}")
        value = independently_apply_formal(
            operation,
            [values[argument_id] for argument_id in argument_ids],
            atom_count,
            invertible,
        )
        values[node_id] = value
        node_ids.add(node_id)
        node_receipts.append({**record, "value": encode_laurent(value)})
    assertion_receipts = []
    assertion_ids: set[str] = set()
    for record in SEMANTIC_TEMPLATE["formal_assertions"]:
        assertion_id = identifier(record["assertion_id"], "formal assertion")
        if (
            type(record) is not dict
            or set(record) != {"assertion_id", "left_id", "relation", "right_id"}
            or assertion_id in assertion_ids
            or record["relation"] != "formal_equal"
            or record["left_id"] not in values
            or record["right_id"] not in values
        ):
            raise DagVerificationError(f"invalid formal assertion: {assertion_id}")
        if values[record["left_id"]] != values[record["right_id"]]:
            raise DagVerificationError(f"formal identity failed: {assertion_id}")
        assertion_ids.add(assertion_id)
        assertion_receipts.append({**record, "holds": True})
    output_receipts = []
    output_names: set[str] = set()
    for record in SEMANTIC_TEMPLATE["formal_outputs"]:
        if (
            type(record) is not dict
            or set(record) != {"output_name", "value_id"}
            or record["output_name"] in output_names
            or record["value_id"] not in node_ids
        ):
            raise DagVerificationError("invalid formal output")
        output_names.add(record["output_name"])
        output_receipts.append({**record, "value": encode_laurent(values[record["value_id"]])})
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


def reconstruct(request: dict[str, Any], request_payload: bytes) -> dict[str, Any]:
    if set(request) != {
        "claim_boundary",
        "inputs",
        "schema",
        "semantic_template",
        "semantic_template_sha256",
        "status",
    }:
        raise DagVerificationError("request top-level key drift")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != "OUTWARD_INTERVALS_AND_FIXED_FORMAL_IDENTITIES_ONLY"
    ):
        raise DagVerificationError("request identity drift")
    require_false_claim_map(request["claim_boundary"], "request")
    if request["semantic_template"] != SEMANTIC_TEMPLATE:
        raise DagVerificationError("fixed semantic template drift")
    if (
        type(request["semantic_template_sha256"]) is not str
        or request["semantic_template_sha256"] != SEMANTIC_TEMPLATE_SHA256
    ):
        raise DagVerificationError("domain-separated semantic template SHA drift")
    if type(request["inputs"]) is not list:
        raise DagVerificationError("outward input list required")
    outward = reconstruct_outward(request["inputs"])
    formal = reconstruct_formal()
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "formal_identity_proof": formal,
        "formal_identity_proof_sha256": digest(FORMAL_DOMAIN + canonical(formal)),
        "outward_interval_evaluation": outward,
        "outward_interval_evaluation_sha256": digest(OUTWARD_DOMAIN + canonical(outward)),
        "request": {
            "byte_length": len(request_payload),
            "schema": REQUEST_SCHEMA,
            "semantic_template_sha256": SEMANTIC_TEMPLATE_SHA256,
            "sha256": digest(request_payload),
        },
        "schema": ARTIFACT_SCHEMA,
        "semantic_template": SEMANTIC_TEMPLATE,
        "semantic_template_sha256": SEMANTIC_TEMPLATE_SHA256,
        "status": (
            "PASS_OUTWARD_INTERVAL_ARITHMETIC_AND_FIXED_FORMAL_IDENTITIES_"
            "NO_PRODUCTION_DATA_NO_REPLAY_NO_ACCEPTANCE"
        ),
    }


def validate_formal_section(section: Any) -> None:
    if type(section) is not dict:
        raise DagVerificationError("formal identity proof object required")
    atom_count = section.get("atom_count")
    if type(atom_count) is not int or type(section.get("atoms")) is not list:
        raise DagVerificationError("formal identity proof metadata drift")
    invertible = frozenset(
        index
        for index, record in enumerate(section["atoms"])
        if type(record) is dict and record.get("domain") == "positive_invertible_exact_real"
    )
    for collection_name in ("nodes", "outputs"):
        collection = section.get(collection_name)
        if type(collection) is not list:
            raise DagVerificationError(f"formal {collection_name} list required")
        for record in collection:
            if type(record) is not dict or "value" not in record:
                raise DagVerificationError(f"formal {collection_name} record drift")
            decode_laurent_artifact(record["value"], atom_count, invertible)


def validate(request_path: Path, artifact_path: Path) -> str:
    if not request_path.is_absolute() or not artifact_path.is_absolute():
        raise DagVerificationError("request and artifact paths must be absolute")
    if os.path.abspath(request_path) == os.path.abspath(artifact_path):
        raise DagVerificationError("request and artifact paths must be distinct")
    request_payload = retain(request_path)
    artifact_payload = retain(artifact_path)
    request = decode(request_payload, "request")
    artifact = decode(artifact_payload, "artifact")
    require_false_claim_map(artifact.get("claim_boundary"), "artifact")
    validate_formal_section(artifact.get("formal_identity_proof"))
    expected = reconstruct(request, request_payload)
    if artifact != expected or artifact_payload != canonical(expected):
        raise DagVerificationError(f"artifact reconstruction drift: {digest(artifact_payload)}")
    return digest(artifact_payload)


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--artifact", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        artifact_sha = validate(arguments.request, arguments.artifact)
        print(
            "PASS_CANDIDATE_NATIVE_EXACT_EXPRESSION_DAG_VALIDATION "
            f"artifact_sha256={artifact_sha} "
            "production_data=false replay=false acceptance=false"
        )
        return 0
    except (
        DagVerificationError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        print(
            f"ERROR CandidateNativeExactExpressionDagValidation: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
