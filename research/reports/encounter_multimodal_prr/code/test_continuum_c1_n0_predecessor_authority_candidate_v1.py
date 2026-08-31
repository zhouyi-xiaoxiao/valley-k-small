"""Static and currentness tests for the Round-177 predecessor candidate."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_n0_predecessor_authority_candidate_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py"
PACKAGE_RELATIVE = Path("artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1")
PACKAGE = REPORT / PACKAGE_RELATIVE

MEMBER = "continuum_c1_c2_n0_member_spec_v3_candidate.json"
PARAMETERS = "continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json"
METHODS = "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json"
POLICY = "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json"
MANIFEST = "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json"
REVIEW_REQUEST = "continuum_c1_c2_n0_external_commitment_review_request_v1.json"
BUNDLE = "bundle.json"
OUTPUT_NAMES = {
    MEMBER,
    PARAMETERS,
    METHODS,
    POLICY,
    MANIFEST,
    REVIEW_REQUEST,
    BUNDLE,
}
AXIS_ORDER = ["midpoint", "relative_parallel", "relative_perpendicular"]
EXPECTED_COUNTS = {
    "axis_count": 36,
    "axis_cell_count": 5037,
    "axis_edge_count": 5013,
    "configuration_count": 12,
    "periodic_seam_count": 12,
    "profile_index_count": 48,
    "total_virtual_tensor_state_count": 34_787_462,
}
CLAIM_KEYS = {
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
FORBIDDEN_BASENAMES = {
    "encounter_c1_gauge_killing_symbolic_candidate_v1.json",
    "encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
}


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run_builder(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(BUILDER), *arguments],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


def run_validator(package: Path = PACKAGE) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(VALIDATOR), "--package", str(package.resolve())],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict[str, Any]:
    value = json.loads((PACKAGE / name).read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def package_snapshot(package: Path) -> dict[str, tuple[int, str]]:
    return {
        path.name: (path.stat().st_size, sha256(path))
        for path in sorted(package.iterdir())
        if path.is_file()
    }


def test_independent_validator_accepts_canonical_package() -> None:
    result = run_validator()
    assert result.returncode == 0, result.stderr
    assert "PASS_PREDECESSOR_AUTHORITY_CANDIDATE_VALIDATION" in result.stdout
    assert "configurations=12" in result.stdout
    assert "partitions=36" in result.stdout
    assert "B06_structural_remedy_prepared=false" in result.stdout


def test_builder_check_is_current_and_does_not_write() -> None:
    before = package_snapshot(PACKAGE)
    result = run_builder("--check")
    after = package_snapshot(PACKAGE)
    assert result.returncode == 0, result.stderr
    assert before == after
    assert set(after) == OUTPUT_NAMES
    assert "blockers_cleared=0" in result.stdout
    assert "external_commitment=false" in result.stdout
    assert "release=false" in result.stdout


def test_builder_check_rejects_mutable_package_file(tmp_path: Path) -> None:
    root = tmp_path / "mutable-root"
    package = root / PACKAGE_RELATIVE
    shutil.copytree(PACKAGE, package)
    (package / BUNDLE).chmod(0o644)
    result = run_builder("--check", "--output-root", str(root))
    assert result.returncode != 0
    assert "immutable single-link regular package file required" in result.stderr


def test_builder_check_rejects_hard_linked_package_file(tmp_path: Path) -> None:
    root = tmp_path / "hardlink-root"
    package = root / PACKAGE_RELATIVE
    shutil.copytree(PACKAGE, package)
    alias = root / "bundle-alias.json"
    alias.write_bytes((package / BUNDLE).read_bytes())
    alias.chmod(0o444)
    (package / BUNDLE).unlink()
    os.link(alias, package / BUNDLE)
    result = run_builder("--check", "--output-root", str(root))
    assert result.returncode != 0
    assert "immutable single-link regular package file required" in result.stderr


def test_two_clean_builds_are_byte_identical(tmp_path: Path) -> None:
    roots = [tmp_path / "first", tmp_path / "second"]
    results = [run_builder("--output-root", str(root)) for root in roots]
    assert all(result.returncode == 0 for result in results), "\n".join(
        result.stderr for result in results
    )
    packages = [root / PACKAGE_RELATIVE for root in roots]
    for name in OUTPUT_NAMES:
        first = (packages[0] / name).read_bytes()
        assert first == (packages[1] / name).read_bytes()
        assert first == (PACKAGE / name).read_bytes()


def test_check_on_missing_package_writes_nothing(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"
    result = run_builder("--check", "--output-root", str(missing_root))
    assert result.returncode != 0
    assert not missing_root.exists()


def test_exact_seven_file_inventory_and_hashes() -> None:
    assert {entry.name for entry in PACKAGE.iterdir()} == OUTPUT_NAMES
    bundle = load(BUNDLE)
    inventory = bundle["file_inventory"]
    assert len(inventory) == 6
    assert {item["path"] for item in inventory} == OUTPUT_NAMES - {BUNDLE}
    for item in inventory:
        path = PACKAGE / item["path"]
        assert item["byte_length"] == len(path.read_bytes())
        assert item["sha256"] == sha256(path)


def test_all_claims_and_all_blocker_clearances_remain_false() -> None:
    for name in OUTPUT_NAMES:
        value = load(name)
        if "claim_boundary" in value:
            assert set(value["claim_boundary"]) == CLAIM_KEYS
            assert all(flag is False for flag in value["claim_boundary"].values())
    bundle = load(BUNDLE)
    blockers = bundle["blocking_conditions"]
    assert len(blockers) == 9
    assert all(item["cleared"] is False for item in blockers)
    prepared = {
        item["blocker_id"] for item in blockers if item["structural_remedy_prepared"] is True
    }
    assert prepared == {"B04_round172_has_no_partition_sha256"}
    assert all(
        item["structural_remedy_prepared"] is False
        for item in blockers
        if item["blocker_id"] != "B04_round172_has_no_partition_sha256"
    )


def test_member_binds_exactly_36_partitions_and_reconstruction_counts() -> None:
    member = load(MEMBER)
    rows = member["n0_sequence_bindings"]
    assert len(rows) == 12
    assert member["reconstruction_counts"] == EXPECTED_COUNTS
    assert member["identity_properties"]["partition_file_count"] == 36
    assert [row["configuration_index"] for row in rows] == list(range(12))
    assert len({row["sequence_id"] for row in rows}) == 12
    semantic_pairs = {(row["refinement_family_id"], row["refinement_member_id"]) for row in rows}
    assert len(semantic_pairs) == 12
    axes = [axis for row in rows for axis in row["n0_axes"]]
    assert len(axes) == 36
    assert all([axis["coordinate"] for axis in row["n0_axes"]] == AXIS_ORDER for row in rows)
    assert sum(axis["cell_count"] for axis in axes) == 5037
    assert all(type(axis["cell_count"]) is int and axis["cell_count"] >= 2 for axis in axes)
    for row in rows:
        row_path = REPORT / row["initial_partition_row_manifest_path"]
        assert row_path.is_file()
        assert row["initial_partition_row_manifest_sha256"] == sha256(row_path)
        for axis in row["n0_axes"]:
            partition_path = REPORT / axis["partition_report_relative_path"]
            assert partition_path.is_file()
            assert axis["partition_sha256"] == sha256(partition_path)


def test_parameter_and_method_registries_are_conservatively_incomplete() -> None:
    parameters = load(PARAMETERS)
    methods = load(METHODS)
    assert parameters["parameter_count"] == len(parameters["parameters"]) == 10
    assert methods["method_count"] == len(methods["methods"]) == 9
    identity = methods["method_identity_properties"]
    assert identity["B06_structural_remedy_prepared"] is False
    assert identity["all_report_local_dependency_closures_bound"] is False
    assert identity["transitive_report_local_dependency_closure_complete"] is False
    assert identity["missing_candidate_native_method_ids"] == ["exact_fraction_expression_dag_v2"]
    scopes: set[str] = set()
    required = {
        "enumerated_code_inventory_sha256",
        "method_parameter_sha256",
        "method_parameter_source_sha256",
        "producer_code_sha256",
        "verifier_code_sha256",
    }
    for method in methods["methods"]:
        assert required <= method.keys()
        assert all(
            type(method[key]) is str
            and len(method[key]) == 64
            and set(method[key]) <= set("0123456789abcdef")
            for key in required
        )
        scopes.update(method["source_role_scope"])
    assert scopes == {
        "role8_raw_axis_enclosure",
        "role9_stationary_integral",
        "role10_killing_geometry",
    }
    assert "exact_fraction_expression_dag_v2" not in {
        method["method_id"] for method in methods["methods"]
    }


def test_policy_is_unsealed_and_current_results_are_ineligible() -> None:
    policy = load(POLICY)
    ordering = policy["ordering"]
    assert ordering["current_enclosure_sources_eligible_for_acceptance"] is False
    assert ordering["external_predecessor_commitment_present"] is False
    assert ordering["future_replay_required"] is True
    assert ordering["policy_predecessor_order_independently_sealed"] is False
    assert ordering["retroactive_acceptance_authorized"] is False
    assert ordering["roles_8_10_outputs_read_while_constructing_this_policy"] is False
    assert policy["threshold_lineage"]["post_enclosure_adaptation_allowed"] is False
    assert policy["threshold_lineage"]["threshold_loosening_detected"] is False


def test_manifest_has_48_bound_subordinates_but_no_result_roles() -> None:
    manifest = load(MANIFEST)
    subordinate = manifest["subordinate_inventory"]
    assert len(subordinate) == 48
    assert len({item["role"] for item in subordinate}) == 48
    assert len({item["path"] for item in subordinate}) == 48
    assert sum(item["role"].startswith("initial_partition_row_") for item in subordinate) == 12
    assert (
        sum(
            item["role"].startswith("initial_partition_")
            and not item["role"].startswith("initial_partition_row_")
            for item in subordinate
        )
        == 36
    )
    for item in subordinate:
        assert sha256(REPORT / item["path"]) == item["sha256"]
    role_names = {item["role"] for item in manifest["role_catalog"]}
    node_names = set(manifest["predecessor_prefix_dag"]["nodes"])
    assert not {
        "role8_raw_axis_enclosure",
        "role9_stationary_integral",
        "role10_killing_geometry",
    }.intersection(role_names | node_names)
    forbidden = manifest["forbidden_selected_roles"]
    assert forbidden
    assert all(value == [] for value in forbidden.values())
    dag = manifest["predecessor_prefix_dag"]
    assert dag["formal_selected_source_dag_complete"] is False
    assert dag["role8_to_role10_outputs_materialized"] is False


def test_review_request_is_not_authentication_or_a_seal() -> None:
    request = load(REVIEW_REQUEST)
    assert request["local_state"]["candidate_ready_for_external_predecessor_commitment"] is False
    assert request["local_state"]["external_authentication_present"] is False
    assert request["local_state"]["local_or_subagent_review_is_external_authentication"] is False
    requested = request["requested_external_record"]
    assert requested["current_request_may_authorize_roles_8_10_replay"] is False
    assert requested["must_exist_before_any_roles_8_10_replay"] is True
    assert "same_process_or_child_process_assertion" in requested["forbidden_evidence_classes"]


def test_reserved_candidate_and_receipt_basenames_are_absent() -> None:
    assert not FORBIDDEN_BASENAMES.intersection(path.name for path in PACKAGE.iterdir())
    bundle = load(BUNDLE)
    assert set(bundle["reserved_basename_absence_required"]) == FORBIDDEN_BASENAMES
    manifest = load(MANIFEST)
    selected_paths = [
        item["path"]
        for key in ("role_catalog", "supporting_evidence", "subordinate_inventory")
        for item in manifest[key]
    ]
    assert not FORBIDDEN_BASENAMES.intersection(Path(path).name for path in selected_paths)


@pytest.mark.parametrize("path", [BUILDER, VALIDATOR])
def test_builder_and_validator_use_standard_library_only(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert imports <= set(sys.stdlib_module_names) | {"__future__"}


def test_validator_does_not_import_or_execute_builder() -> None:
    source = VALIDATOR.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all("build_continuum" not in alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert "build_continuum" not in node.module
    assert "runpy.run_path" not in source
    assert "subprocess" not in {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
