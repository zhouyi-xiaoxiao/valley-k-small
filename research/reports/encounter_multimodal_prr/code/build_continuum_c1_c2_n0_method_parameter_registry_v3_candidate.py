#!/usr/bin/env python3
"""Build the candidate-native role-8--10 method-parameter registry v3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any, Final

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_OUTPUT: Final = (
    REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
)

SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v3_candidate"
STATUS: Final = "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v3"
CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
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


def canonical_bytes(value: Any) -> bytes:
    def check(node: Any, depth: int = 0) -> None:
        if depth > 32:
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
                check(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                    raise RegistryBuildError("invalid JSON key")
                check(item, depth + 1)
            return
        raise RegistryBuildError(f"forbidden JSON type: {type(node).__name__}")

    check(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def method_digest(parameters: dict[str, Any]) -> str:
    return hashlib.sha256(
        DIGEST_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(parameters)
    ).hexdigest()


def entry(identifier: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "method_parameter_sha256": method_digest(parameters),
        "parameter_id": identifier,
        "parameters": parameters,
    }


def normative_registry() -> dict[str, Any]:
    exact_scope = [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ]
    parameters = [
        entry(
            "stationary_directed_mpfr_320_v2",
            {
                "aggregation": ("exact_Fraction_endpoint_sums_and_nonnegative_products"),
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
            "killing_contact_profile_mpfr_192_v2",
            {
                "contact_fraction_record_format": ">dd",
                "panels_per_unit": 16384,
                "precision_bits": 192,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_factor_geometry"],
                "support_density_record_format": ">dd",
            },
        ),
        entry(
            "killing_analytic_disk_area_mpfr_256_v2",
            {
                "analytic_area_precision_bits": 256,
                "formula": "pi_times_radius_squared",
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
        entry(
            "killing_independent_simpson_remainder_v2",
            {
                "independent_backend": False,
                "maximum_panel_count": 4194304,
                "primary_precision_bits": 384,
                "remainder_rule": ("rigorous_fourth_derivative_simpson_remainder"),
                "sentinel_precision_bits": 512,
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
        entry(
            "killing_exact_full_cell_classification_v2",
            {
                "classification": (
                    "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
                ),
                "full_cell_serialization": "exact_[1,1]",
                "precision_bits": "exact_rational",
                "rounding_mode": "exact",
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
    ]
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "parameter_count": 10,
        "parameters": parameters,
        "schema": SCHEMA,
        "status": STATUS,
    }


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or len(path.parts) < 2:
        raise RegistryBuildError("absolute output or candidate path required")
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
                raise RegistryBuildError("unsafe path component")
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise RegistryBuildError("unsafe leaf name")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def same_parent_is_live(path: Path, anchored: int) -> bool:
    verification, _ = open_parent_anchored(path)
    try:
        left = os.fstat(anchored)
        right = os.fstat(verification)
        return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)
    finally:
        os.close(verification)


def read_regular(path: Path, cap: int = 1_000_000) -> bytes:
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
            raise RegistryBuildError("unstable or oversized candidate")
        payload = bytearray()
        while len(payload) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(payload))
            if not block:
                raise RegistryBuildError("short candidate read")
            payload.extend(block)
        if os.read(descriptor, 1):
            raise RegistryBuildError("candidate grew during read")
        after = os.fstat(descriptor)
        if (
            after.st_size != opened.st_size
            or after.st_mtime_ns != opened.st_mtime_ns
            or after.st_ctime_ns != opened.st_ctime_ns
        ):
            raise RegistryBuildError("candidate changed during read")
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (linked.st_dev, linked.st_ino) != (
            opened.st_dev,
            opened.st_ino,
        ) or not same_parent_is_live(path, parent):
            raise RegistryBuildError("candidate path changed during read")
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


def publish_no_replace(path: Path, payload: bytes) -> None:
    parent, leaf = open_parent_anchored(path)
    stage = f".{leaf}.{secrets.token_hex(16)}.stage"
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = -1
    staged_identity: tuple[int, int] | None = None
    final_created = False
    success = False
    try:
        descriptor = os.open(stage, flags, 0o400, dir_fd=parent)
        created = os.fstat(descriptor)
        staged_identity = (created.st_dev, created.st_ino)
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0:
                raise RegistryBuildError("short staged write")
            written += count
        os.fsync(descriptor)
        os.fchmod(descriptor, 0o444)
        staged = os.fstat(descriptor)
        if (staged.st_dev, staged.st_ino) != staged_identity:
            raise RegistryBuildError("staging descriptor identity changed")
        os.close(descriptor)
        descriptor = -1
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
        final_created = True
        if staged_identity is None or not unlink_owned(parent, stage, staged_identity):
            raise RegistryBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != staged_identity
            or final.st_nlink != 1
            or not same_parent_is_live(path, parent)
        ):
            raise RegistryBuildError("published output path changed")
        success = True
    except BaseException:
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staged_identity is not None:
            unlink_owned(parent, stage, staged_identity)
        if final_created and not success and staged_identity is not None:
            if unlink_owned(parent, leaf, staged_identity):
                os.fsync(parent)
        os.close(parent)


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
                "PASS_METHOD_PARAMETER_REGISTRY_V3_CANDIDATE_CHECK "
                f"sha256={hashlib.sha256(payload).hexdigest()}"
            )
            return 0
        publish_no_replace(output, payload)
        print(
            "PASS_METHOD_PARAMETER_REGISTRY_V3_CANDIDATE_BUILD "
            f"path={output} sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    except (OSError, RegistryBuildError) as error:
        print(
            f"ERROR MethodParameterRegistryV3CandidateBuild: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
