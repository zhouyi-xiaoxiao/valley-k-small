#!/usr/bin/env python3
"""Independently validate the candidate-native method registry v3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any, Final

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_ARTIFACT: Final = (
    REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
)

SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v3_candidate"
STATUS: Final = "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v3"
CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
ORDER: Final = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    "killing_contact_profile_mpfr_192_v2",
    "killing_analytic_disk_area_mpfr_256_v2",
    "killing_independent_simpson_remainder_v2",
    "killing_exact_full_cell_classification_v2",
)
CLAIM_KEYS: Final = {
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
}


class RegistryValidationError(ValueError):
    """A byte, shape, digest, scope, or semantic invariant failed."""


def canonical_bytes(value: Any) -> bytes:
    def visit(node: Any, depth: int = 0) -> None:
        if depth > 32:
            raise RegistryValidationError("JSON depth cap exceeded")
        if isinstance(node, float):
            raise RegistryValidationError("floating JSON literal forbidden")
        if type(node) in (bool, int) or node is None:
            return
        if type(node) is str:
            if node != unicodedata.normalize("NFC", node):
                raise RegistryValidationError("non-NFC JSON string")
            return
        if type(node) is list:
            for item in node:
                visit(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or key != unicodedata.normalize("NFC", key):
                    raise RegistryValidationError("invalid JSON key")
                visit(item, depth + 1)
            return
        raise RegistryValidationError(f"forbidden JSON type: {type(node).__name__}")

    visit(value)
    text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
    return f"{text}\n".encode("ascii")


def decode_canonical(payload: bytes) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in result:
                raise RegistryValidationError("duplicate or invalid JSON key")
            result[key] = item
        return result

    def reject_noninteger(token: str) -> Any:
        raise RegistryValidationError(f"non-integer JSON number: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=unique_object,
            parse_float=reject_noninteger,
            parse_constant=reject_noninteger,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise RegistryValidationError("strict JSON decoding failed") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise RegistryValidationError("canonical registry byte drift")
    return value


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or len(path.parts) < 2:
        raise RegistryValidationError("absolute registry path required")
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
                raise RegistryValidationError("unsafe registry path component")
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise RegistryValidationError("unsafe registry leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def snapshot(path: Path, cap: int = 1_000_000) -> bytes:
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
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or opened.st_size > cap:
            raise RegistryValidationError("unstable or oversized registry")
        result = bytearray()
        while len(result) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(result))
            if not block:
                raise RegistryValidationError("short registry read")
            result.extend(block)
        if os.read(descriptor, 1):
            raise RegistryValidationError("registry grew during read")
        final = os.fstat(descriptor)
        if (
            final.st_size != opened.st_size
            or final.st_mtime_ns != opened.st_mtime_ns
            or final.st_ctime_ns != opened.st_ctime_ns
        ):
            raise RegistryValidationError("registry changed during read")
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        verification, verification_leaf = open_parent_anchored(path)
        try:
            current_parent = os.fstat(parent)
            live_parent = os.fstat(verification)
            live_leaf = os.stat(
                verification_leaf,
                dir_fd=verification,
                follow_symlinks=False,
            )
        finally:
            os.close(verification)
        if (
            (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino)
            or (live_leaf.st_dev, live_leaf.st_ino) != (opened.st_dev, opened.st_ino)
            or (current_parent.st_dev, current_parent.st_ino)
            != (live_parent.st_dev, live_parent.st_ino)
        ):
            raise RegistryValidationError("registry path changed during read")
        return bytes(result)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def digest(parameters: dict[str, Any]) -> str:
    return hashlib.sha256(
        DIGEST_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(parameters)
    ).hexdigest()


def expected_parameters() -> list[dict[str, Any]]:
    return [
        {
            "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
            "dense_tensor_materialized": False,
            "precision_bits": 320,
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role9_stationary_physical_integral"],
        },
        {
            "containment_relation": CONTAINMENT,
            "independent_backend": False,
            "precision_bits": 640,
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role9_stationary_physical_integral"],
        },
        {
            "aggregation": "exact_Fraction_endpoint_algebra",
            "common_kappa_rule": "intersection_after_formula_witness",
            "precision_bits": 320,
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role8_raw_axis_formula_primitive"],
        },
        {
            "containment_relation": CONTAINMENT,
            "independent_backend": False,
            "precision_bits": 640,
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role8_raw_axis_formula_primitive"],
        },
        {
            "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
            "precision_bits": 53,
            "rounding_mode": "stored_outward_endpoints",
            "source_role_scope": ["role8_raw_axis_formula_primitive"],
        },
        {
            "arithmetic": "Python_Fraction_exact_reduced_rationals",
            "precision_bits": "unbounded_integer_fraction",
            "rounding_mode": "exact",
            "source_role_scope": [
                "role8_raw_axis_formula_primitive",
                "role9_stationary_physical_integral",
                "same_member_mass_flux_composition",
                "symbolic_killing_composition",
            ],
        },
        {
            "contact_fraction_record_format": ">dd",
            "panels_per_unit": 16384,
            "precision_bits": 192,
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role10_killing_factor_geometry"],
            "support_density_record_format": ">dd",
        },
        {
            "analytic_area_precision_bits": 256,
            "formula": "pi_times_radius_squared",
            "rounding_mode": "directed_RoundDown_RoundUp",
            "source_role_scope": ["role10_killing_factor_geometry"],
        },
        {
            "independent_backend": False,
            "maximum_panel_count": 4194304,
            "primary_precision_bits": 384,
            "remainder_rule": "rigorous_fourth_derivative_simpson_remainder",
            "sentinel_precision_bits": 512,
            "source_role_scope": ["role10_killing_factor_geometry"],
        },
        {
            "classification": (
                "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
            ),
            "full_cell_serialization": "exact_[1,1]",
            "precision_bits": "exact_rational",
            "rounding_mode": "exact",
            "source_role_scope": ["role10_killing_factor_geometry"],
        },
    ]


def expected_registry() -> dict[str, Any]:
    entries = [
        {
            "method_parameter_sha256": digest(parameters),
            "parameter_id": identifier,
            "parameters": parameters,
        }
        for identifier, parameters in zip(
            ORDER,
            expected_parameters(),
            strict=True,
        )
    ]
    return {
        "claim_boundary": {key: False for key in sorted(CLAIM_KEYS)},
        "parameter_count": len(entries),
        "parameters": entries,
        "schema": SCHEMA,
        "status": STATUS,
    }


def validate_semantics(registry: dict[str, Any]) -> None:
    if set(registry) != {
        "claim_boundary",
        "parameter_count",
        "parameters",
        "schema",
        "status",
    }:
        raise RegistryValidationError("top-level registry keys drift")
    claims = registry["claim_boundary"]
    entries = registry["parameters"]
    if (
        registry["schema"] != SCHEMA
        or registry["status"] != STATUS
        or type(claims) is not dict
        or set(claims) != CLAIM_KEYS
        or any(value is not False for value in claims.values())
        or registry["parameter_count"] != 10
        or type(entries) is not list
        or len(entries) != 10
    ):
        raise RegistryValidationError("registry boundary or cardinality drift")
    parameters = expected_parameters()
    for index, (record, identifier, expected) in enumerate(
        zip(entries, ORDER, parameters, strict=True)
    ):
        if (
            type(record) is not dict
            or set(record) != {"method_parameter_sha256", "parameter_id", "parameters"}
            or record["parameter_id"] != identifier
            or record["parameters"] != expected
            or record["method_parameter_sha256"] != digest(expected)
        ):
            raise RegistryValidationError(
                f"method parameter record semantic drift at index {index}"
            )

    def walk_keys(node: Any) -> list[str]:
        if type(node) is dict:
            return [key for key, item in node.items() for key in [key, *walk_keys(item)]]
        if type(node) is list:
            return [key for item in node for key in walk_keys(item)]
        return []

    forbidden = [
        key for key in walk_keys(registry) if "result" in key.lower() or "observed" in key.lower()
    ]
    if forbidden:
        raise RegistryValidationError(f"outcome metadata key forbidden: {sorted(forbidden)[0]}")
    if registry != expected_registry():
        raise RegistryValidationError("normative registry reconstruction drift")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        path = Path(os.path.abspath(os.fspath(arguments.artifact.expanduser())))
        payload = snapshot(path)
        registry = decode_canonical(payload)
        validate_semantics(registry)
        if payload != canonical_bytes(expected_registry()):
            raise RegistryValidationError("normative registry byte drift")
        print(
            "PASS_METHOD_PARAMETER_REGISTRY_V3_CANDIDATE_VALIDATION "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    except (OSError, RegistryValidationError) as error:
        print(
            f"ERROR MethodParameterRegistryV3CandidateValidation: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
