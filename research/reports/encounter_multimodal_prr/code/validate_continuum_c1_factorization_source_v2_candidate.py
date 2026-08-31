#!/usr/bin/env python3
"""Independently validate the outcome-free role-3 factorization candidate."""

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
    REPORT / "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)

SOURCE_RECORDS: Final = (
    (
        "configuration_source",
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "encounter_physical_configuration_family_control_free_v1",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    (
        "initial_partition_bundle",
        "artifacts/data/physical_production_initial_stream_v1/bundle.json",
        "encounter_control_free_production_initial_stream_v1",
        "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
    ),
    (
        "killing_geometry_source",
        "artifacts/data/physical_killing_geometry_source_v1.json",
        "encounter_physical_killing_geometry_source_v1",
        "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    ),
)
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


class FactorizationValidationError(ValueError):
    """A byte-level, source-binding, or semantic invariant failed."""


def encode_document(value: Any) -> bytes:
    def visit(node: Any, depth: int = 0) -> None:
        if depth > 48:
            raise FactorizationValidationError("JSON nesting exceeds cap")
        if isinstance(node, float):
            raise FactorizationValidationError("floating JSON literal forbidden")
        if type(node) in (bool, int) or node is None:
            return
        if type(node) is str:
            if node != unicodedata.normalize("NFC", node):
                raise FactorizationValidationError("non-NFC JSON text")
            return
        if type(node) is list:
            for item in node:
                visit(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or key != unicodedata.normalize("NFC", key):
                    raise FactorizationValidationError("invalid JSON object key")
                visit(item, depth + 1)
            return
        raise FactorizationValidationError(f"unsupported JSON node: {type(node).__name__}")

    visit(value)
    text = json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True)
    return f"{text}\n".encode("ascii")


def decode_document(payload: bytes, label: str) -> dict[str, Any]:
    def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in output:
                raise FactorizationValidationError(f"duplicate or invalid object key in {label}")
            output[key] = item
        return output

    def reject_noninteger(token: str) -> Any:
        raise FactorizationValidationError(f"non-integer JSON number in {label}: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=object_without_duplicates,
            parse_float=reject_noninteger,
            parse_constant=reject_noninteger,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise FactorizationValidationError(f"strict JSON decoding failed for {label}") from error
    if type(value) is not dict or encode_document(value) != payload:
        raise FactorizationValidationError(f"canonical-byte drift for {label}")
    return value


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or len(path.parts) < 2:
        raise FactorizationValidationError("absolute candidate path required")
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
                raise FactorizationValidationError("unsafe candidate path component")
            next_descriptor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise FactorizationValidationError("unsafe candidate leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def snapshot_file(path: Path, label: str, cap: int = 64 * 1024 * 1024) -> bytes:
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
            raise FactorizationValidationError(f"unstable or oversized file for {label}")
        output = bytearray()
        while len(output) < opened.st_size:
            block = os.read(descriptor, min(1024 * 1024, opened.st_size - len(output)))
            if not block:
                raise FactorizationValidationError(f"short read for {label}")
            output.extend(block)
        if os.read(descriptor, 1):
            raise FactorizationValidationError(f"file grew during read for {label}")
        closed_snapshot = os.fstat(descriptor)
        if (
            closed_snapshot.st_size != opened.st_size
            or closed_snapshot.st_mtime_ns != opened.st_mtime_ns
            or closed_snapshot.st_ctime_ns != opened.st_ctime_ns
        ):
            raise FactorizationValidationError(f"file changed during read for {label}")
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        verification, verification_leaf = open_parent_anchored(path)
        try:
            original_parent = os.fstat(parent)
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
            or (original_parent.st_dev, original_parent.st_ino)
            != (live_parent.st_dev, live_parent.st_ino)
        ):
            raise FactorizationValidationError(f"file path changed during read for {label}")
        return bytes(output)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def validate_bound_sources() -> None:
    documents: dict[str, dict[str, Any]] = {}
    for role, relative, schema, digest in SOURCE_RECORDS:
        payload = snapshot_file(REPORT / relative, role)
        if hashlib.sha256(payload).hexdigest() != digest:
            raise FactorizationValidationError(f"source digest mismatch for {role}")
        document = decode_document(payload, role)
        if document.get("schema") != schema:
            raise FactorizationValidationError(f"source schema mismatch for {role}")
        documents[role] = document

    configuration = documents["configuration_source"]
    if (
        configuration.get("configuration_count") != 12
        or configuration.get("coordinate_order")
        != ["midpoint", "relative_parallel", "relative_perpendicular"]
        or configuration.get("authorizes_scientific_execution") is not False
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
    ):
        raise FactorizationValidationError("control-free configuration boundary drift")

    partition = documents["initial_partition_bundle"]
    partition_flags = partition.get("flags")
    if (
        partition.get("configuration_count") != 12
        or partition.get("configuration_sha256") != SOURCE_RECORDS[0][3]
        or type(partition_flags) is not dict
    ):
        raise FactorizationValidationError("partition source binding drift")
    for key in (
        "authorizes_scientific_execution",
        "contains_budget_value",
        "contains_control_values",
        "full_operator_bound",
        "positive_budget_executed",
        "science_executed",
        "topology_complete",
    ):
        if partition_flags.get(key) is not False:
            raise FactorizationValidationError(f"partition boundary drift: {key}")

    geometry = documents["killing_geometry_source"]
    expected_geometry_pins = {
        "configuration_path": SOURCE_RECORDS[0][1],
        "configuration_sha256": SOURCE_RECORDS[0][3],
        "partition_bundle_path": SOURCE_RECORDS[1][1],
        "partition_bundle_sha256": SOURCE_RECORDS[1][3],
    }
    if (
        geometry.get("configuration_bundle") != expected_geometry_pins
        or geometry.get("coordinate_order")
        != ["midpoint", "relative_parallel", "relative_perpendicular"]
        or geometry.get("physical_dimension") != 2
        or geometry.get("quotient_dimension") != 3
    ):
        raise FactorizationValidationError("geometry binding or dimension drift")
    contact = geometry.get("contact_geometry")
    support = geometry.get("support_basis")
    flags = geometry.get("flags")
    if (
        type(contact) is not dict
        or contact.get("radius_exact") != "5764607523034235/36028797018963968"
        or contact.get("transverse_period_exact") != "1/1"
        or contact.get("transverse_cut_locus_condition") != "2*radius<transverse_period"
        or type(support) is not dict
        or support.get("centres_exact") != list(PROFILE_CENTRES)
        or support.get("profile_count") != 4
        or support.get("half_width_exact") != "5764607523034235/144115188075855872"
        or support.get("analytic_integral_each") != "1/1"
        or type(flags) is not dict
    ):
        raise FactorizationValidationError("geometry semantic drift")
    for key in (
        "authorizes_scientific_execution",
        "concrete_killing_constructed",
        "contains_budget_value",
        "contains_control_values",
        "continuum_verified",
        "f0_pass",
        "full_operator_bound",
        "positive_budget_executed",
        "production_resource_gate",
        "propagation_executed",
        "science_executed",
        "topology_complete",
    ):
        if flags.get(key) is not False:
            raise FactorizationValidationError(f"geometry boundary drift: {key}")
    if flags.get("contact_geometry_defined") is not True:
        raise FactorizationValidationError("contact geometry is not defined")
    if flags.get("support_basis_defined") is not True:
        raise FactorizationValidationError("support basis is not defined")

    banned = (
        "physical_production_killing_geometry_v1",
        "two_repeat",
        "canonical_object_sha256",
        "factorization_contract_sha256",
        "acceptance_receipt",
        "observed",
        "result",
    )

    def reject_outcome_binding(node: Any) -> None:
        if type(node) is dict:
            for key, item in node.items():
                if any(token in key.lower() for token in banned):
                    raise FactorizationValidationError(f"outcome-bound geometry key: {key}")
                reject_outcome_binding(item)
        elif type(node) is list:
            for item in node:
                reject_outcome_binding(item)
        elif type(node) is str and any(token in node.lower() for token in banned):
            raise FactorizationValidationError("outcome-bound geometry value")

    reject_outcome_binding(geometry)


def normative_document() -> dict[str, Any]:
    source_pins = {
        role: {"path": path, "schema": schema, "sha256": digest}
        for role, path, schema, digest in SOURCE_RECORDS
    }
    profiles = [
        {
            "centre_exact": centre,
            "profile_index": index,
            "source_role": f"physical_midpoint_support_density_{index:02d}",
        }
        for index, centre in enumerate(PROFILE_CENTRES)
    ]
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
            "contact_radius_exact": "5764607523034235/36028797018963968",
            "transverse_cut_locus_condition": "2*radius<transverse_period",
            "transverse_period_exact": "1/1",
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
            "analytic_integral_each": "1/1",
            "density": ("phi_j(M)=b((M-centre_j)/half_width)/(half_width*I_b)"),
            "half_width_exact": "5764607523034235/144115188075855872",
            "normalizer": "I_b=integral_from_minus_one_to_one_b(u)_du",
            "ordered_profile_mapping": profiles,
            "profile_count": 4,
            "shape": "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))",
        },
        "schema": "encounter_continuum_c1_factorization_source_v2_candidate",
        "source_pins": source_pins,
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        validate_bound_sources()
        artifact_path = Path(os.path.abspath(os.fspath(arguments.artifact.expanduser())))
        payload = snapshot_file(artifact_path, "factorization candidate")
        artifact = decode_document(payload, "factorization candidate")
        expected = normative_document()
        if type(artifact) is not dict or artifact != expected:
            raise FactorizationValidationError("factorization candidate semantic drift")
        if encode_document(expected) != payload:
            raise FactorizationValidationError("factorization candidate byte reconstruction drift")
        print(
            "PASS_FACTORIZATION_SOURCE_V2_CANDIDATE_VALIDATION "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    except (FactorizationValidationError, OSError) as error:
        print(
            f"ERROR FactorizationSourceV2CandidateValidation: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
