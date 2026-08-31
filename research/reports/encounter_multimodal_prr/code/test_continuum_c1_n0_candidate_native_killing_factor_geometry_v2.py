"""Tests for the fail-closed role-10 killing-geometry protocol shell."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import gmpy2
import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py"
VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py"
ROLE8_PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
ROLE8_VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py"
ROLE9_PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"
ROLE9_VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"

RELATIVE_AUTHORITIES = {
    "anti_vacuity_policy": Path(
        "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"
    ),
    "configuration": Path("artifacts/data/physical_configuration_family_control_free_v1.json"),
    "configuration_design": Path("notes/positive_b_fixed_control_robustness_design_v2.md"),
    "configuration_implementation": Path("code/rate_defined_tensor_f0.py"),
    "configuration_initial_geometry": Path(
        "artifacts/data/physical_initial_analytic_source_v1.json"
    ),
    "configuration_test": Path("code/test_rate_defined_tensor_f0.py"),
    "factorization": Path("artifacts/data/continuum_c1_factorization_source_v2_candidate.json"),
    "factorization_initial_partition_bundle": Path(
        "artifacts/data/physical_production_initial_stream_v1/bundle.json"
    ),
    "factorization_killing_geometry": Path(
        "artifacts/data/physical_killing_geometry_source_v1.json"
    ),
    "ideal_formula": Path("artifacts/data/continuum_c1_ideal_formula_source_v1.json"),
    "member_spec": Path("artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"),
    "method_parameters": Path(
        "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
    ),
    "reference_density": Path("artifacts/data/continuum_c1_reference_density_source_v1.json"),
}


def _load(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
verifier = _load(
    "validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v2",
    VERIFIER_PATH,
)
producer = _load(
    "build_continuum_c1_n0_candidate_native_killing_factor_geometry_v2_tests",
    PRODUCER_PATH,
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + canonical(value))


def immutable_write(path: Path, value: Any) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if type(value) is bytes else canonical(value)
    path.write_bytes(raw)
    path.chmod(0o444)
    return raw


def replace_immutable(path: Path, value: Any) -> bytes:
    path.chmod(0o600)
    raw = value if type(value) is bytes else canonical(value)
    path.write_bytes(raw)
    path.chmod(0o444)
    return raw


def pin(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256(path.read_bytes())}


def contextual_pin(path: Path, relative: Path, schema: str) -> dict[str, str]:
    return {
        "path": relative.as_posix(),
        "schema": schema,
        "sha256": sha256(path.read_bytes()),
    }


def clone(root: Path, relative: Path) -> Path:
    destination = root / relative
    immutable_write(destination, (REPORT / relative).read_bytes())
    return destination


def make_fixture(tmp_path: Path) -> dict[str, Any]:
    root = tmp_path / "fixture"
    root.mkdir(mode=0o700)
    output_parent = tmp_path / "output"
    output_parent.mkdir(mode=0o700)
    paths = {role: clone(root, relative) for role, relative in RELATIVE_AUTHORITIES.items()}
    member = json.loads(paths["member_spec"].read_text("ascii"))
    configuration = json.loads(paths["configuration"].read_text("ascii"))
    assert sha256(paths["member_spec"].read_bytes()) == producer.MEMBER_SHA256
    assert sha256(paths["method_parameters"].read_bytes()) == producer.PARAMETER_SHA256
    assert sha256(paths["factorization"].read_bytes()) == producer.FACTORIZATION_SHA256
    assert sha256(paths["anti_vacuity_policy"].read_bytes()) == producer.ANTI_VACUITY_POLICY_SHA256

    partitions: list[dict[str, Any]] = []
    for index, binding in enumerate(member["n0_sequence_bindings"]):
        for axis in binding["n0_axes"]:
            relative = Path(axis["partition_report_relative_path"])
            partition_path = clone(root, relative)
            partitions.append(
                {
                    "configuration_index": index,
                    "coordinate": axis["coordinate"],
                    "member_report_relative_path": relative.as_posix(),
                    **pin(partition_path),
                }
            )

    schemas = {
        "anti_vacuity_policy": producer.ANTI_VACUITY_POLICY_SCHEMA,
        "configuration": producer.CONFIGURATION_SCHEMA,
        "factorization": producer.FACTORIZATION_SCHEMA,
        "ideal_formula": producer.FORMULA_SCHEMA,
        "member_spec": producer.MEMBER_SCHEMA,
        "method_parameters": producer.PARAMETER_SCHEMA,
        "reference_density": producer.REFERENCE_SCHEMA,
    }
    shared_context = {
        "anti_vacuity_policy": contextual_pin(
            paths["anti_vacuity_policy"],
            RELATIVE_AUTHORITIES["anti_vacuity_policy"],
            schemas["anti_vacuity_policy"],
        ),
        "configuration": contextual_pin(
            paths["configuration"],
            RELATIVE_AUTHORITIES["configuration"],
            schemas["configuration"],
        ),
        "configuration_row_inventory_sha256": digest(
            producer.CONFIGURATION_INVENTORY_DOMAIN,
            producer._configuration_inventory(configuration),
        ),
        "factorization": contextual_pin(
            paths["factorization"],
            RELATIVE_AUTHORITIES["factorization"],
            schemas["factorization"],
        ),
        "ideal_formula": contextual_pin(
            paths["ideal_formula"],
            RELATIVE_AUTHORITIES["ideal_formula"],
            schemas["ideal_formula"],
        ),
        "member_identity_sha256": producer.MEMBER_IDENTITY_SHA256,
        "member_spec": contextual_pin(
            paths["member_spec"],
            RELATIVE_AUTHORITIES["member_spec"],
            schemas["member_spec"],
        ),
        "method_parameter_registry": contextual_pin(
            paths["method_parameters"],
            RELATIVE_AUTHORITIES["method_parameters"],
            schemas["method_parameters"],
        ),
        "partition_inventory_sha256": digest(
            producer.PARTITION_INVENTORY_DOMAIN,
            producer._partition_inventory(member),
        ),
        "reference_density": contextual_pin(
            paths["reference_density"],
            RELATIVE_AUTHORITIES["reference_density"],
            schemas["reference_density"],
        ),
    }
    assert (
        shared_context["configuration_row_inventory_sha256"]
        == producer.CONFIGURATION_INVENTORY_SHA256
    )
    assert shared_context["partition_inventory_sha256"] == producer.PARTITION_INVENTORY_SHA256
    precommit = digest(producer.PRECOMMIT_CONTEXT_DOMAIN, shared_context)

    role_sources = {
        8: {
            "producer": clone(root, ROLE8_PRODUCER_PATH.relative_to(REPORT)),
            "verifier": clone(root, ROLE8_VERIFIER_PATH.relative_to(REPORT)),
        },
        9: {
            "producer": clone(root, ROLE9_PRODUCER_PATH.relative_to(REPORT)),
            "verifier": clone(root, ROLE9_VERIFIER_PATH.relative_to(REPORT)),
        },
        10: {"producer": PRODUCER_PATH, "verifier": VERIFIER_PATH},
    }
    runtime = producer._runtime_versions()
    package_directory = Path(gmpy2.__file__).resolve().parent
    native_candidates = {
        "gmpy2_extension": sorted(package_directory.glob("gmpy2*.so")),
        "libgmp": sorted((package_directory.parent / "gmpy2.libs").glob("libgmp.*.dylib")),
        "libmpfr": sorted((package_directory.parent / "gmpy2.libs").glob("libmpfr.*.dylib")),
        "libmpc": sorted((package_directory.parent / "gmpy2.libs").glob("libmpc.*.dylib")),
    }
    assert all(len(candidates) == 1 for candidates in native_candidates.values())
    native_libraries = [
        {
            "path": str(native_candidates[role][0].resolve()),
            "role": role,
            "sha256": sha256(native_candidates[role][0].resolve().read_bytes()),
        }
        for role in verifier._NATIVE_LIBRARY_ROLES
    ]
    python_executable = Path(sys.executable).resolve()
    role8_runtime_closure = {
        "claim_boundary": dict(verifier._ROLE8_RUNTIME_CLAIMS),
        "code_inputs": {role: pin(source) for role, source in role_sources[8].items()},
        "native_libraries": native_libraries,
        "native_runtime": runtime,
        "python_executable": {
            "path": str(python_executable),
            "sha256": sha256(python_executable.read_bytes()),
        },
        "python_imports": verifier._ROLE8_PYTHON_IMPORTS,
        "report_local_dependencies": [],
        "schema": verifier.ROLE8_RUNTIME_CLOSURE_SCHEMA,
        "status": verifier.ROLE8_RUNTIME_CLOSURE_STATUS,
    }
    role8_runtime_closure_path = root / "role8.runtime-closure.json"
    immutable_write(role8_runtime_closure_path, role8_runtime_closure)

    role_slots = {
        8: {
            "request": root / "role8.request.json",
            "artifact": output_parent / "role8.raw-axis-formula.json",
            "receipt": output_parent / "role8.raw-axis-formula.receipt.json",
        },
        9: {
            "request": root / "role9.request.json",
            "artifact": output_parent / "role9.stationary-integrals.json",
            "receipt": output_parent / "role9.stationary-integrals.receipt.json",
        },
        10: {
            "request": root / "role10.request.json",
            "artifact": output_parent / "role10.killing-factor-geometry",
            "receipt": output_parent / "role10.killing-factor-geometry.receipt.json",
        },
    }
    registry = json.loads(paths["method_parameters"].read_text("ascii"))
    registry_by_id = {record["parameter_id"]: record for record in registry["parameters"]}

    def role_entry(role: int) -> dict[str, Any]:
        sources = role_sources[role]
        slots = role_slots[role]
        if role == 8:
            runtime_closure: dict[str, Any] = {
                "path": str(role8_runtime_closure_path),
                "schema": verifier.ROLE8_RUNTIME_CLOSURE_SCHEMA,
                "sha256": sha256(role8_runtime_closure_path.read_bytes()),
            }
            authority_roles = sorted(verifier._ROLE8_INPUT_AUTHORITY_ROLES)
            selected_ids = [
                "raw_flux_directed_mpfr_320_v2",
                "raw_flux_directed_mpfr_640_sentinel_v2",
                "raw_flux_binary64_decode_v2",
                "exact_fraction_expression_dag_v2",
            ]
            method_selection: Any = [
                {
                    "method_parameter_sha256": registry_by_id[identifier][
                        "method_parameter_sha256"
                    ],
                    "parameter_id": identifier,
                }
                for identifier in selected_ids
            ]
            invocation_prefix = [sys.executable, "-I", "-B"]
        else:
            runtime_closure = {
                "producer": pin(sources["producer"]),
                "runtime_requirements": runtime,
                "verifier": pin(sources["verifier"]),
            }
            authority_roles = sorted(verifier._INPUT_AUTHORITY_ROLES)
            method_selection = dict(
                verifier._ROLE9_METHOD_SELECTION if role == 9 else verifier._ROLE10_METHOD_SELECTION
            )
            invocation_prefix = [sys.executable]
        entry = {
            "entry_id": verifier._ROLE_ENTRY_NAMES[role],
            "implementation_runtime_closure": runtime_closure,
            "input_authorities": {
                authority_role: pin(paths[authority_role]) for authority_role in authority_roles
            },
            "invocations": {
                "producer": {
                    "argv": [
                        *invocation_prefix,
                        str(sources["producer"]),
                        "--request",
                        str(slots["request"]),
                        "--output",
                        str(slots["artifact"]),
                    ],
                    "cwd": str(sources["producer"].parent.parent),
                },
                "verifier": {
                    "argv": [
                        *invocation_prefix,
                        str(sources["verifier"]),
                        "--request",
                        str(slots["request"]),
                        "--output",
                        str(slots["artifact"]),
                        "--receipt",
                        str(slots["receipt"]),
                    ],
                    "cwd": str(sources["verifier"].parent.parent),
                },
            },
            "method_selection": method_selection,
            "outputs": {
                "artifact": {
                    "path": str(slots["artifact"]),
                    "schema": verifier._ROLE_OUTPUT_SCHEMAS[role],
                },
                "validation_receipt": {
                    "path": str(slots["receipt"]),
                    "schema": verifier._ROLE_RECEIPT_SCHEMAS[role],
                },
            },
            "partition_path_bindings": [dict(binding) for binding in partitions],
            "request": {
                "path": str(slots["request"]),
                "schema": verifier._ROLE_REQUEST_SCHEMAS[role],
                "status": producer.REQUEST_STATUS,
            },
            "role": role,
        }
        entry["precommit_projection_sha256"] = digest(
            producer.PRECOMMIT_PROJECTION_DOMAIN,
            entry,
        )
        return entry

    entries = [role_entry(role) for role in (8, 9, 10)]
    request_path = role_slots[10]["request"]
    artifact_path = role_slots[10]["artifact"]
    receipt_path = role_slots[10]["receipt"]
    plan = {
        "claim_boundary": {
            "external_predecessor_commitment_present": False,
            "ordered_roles_8_10_replay_executed": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "entries": entries,
        "schema": producer.PLAN_SCHEMA,
        "shared_context": shared_context,
        "shared_precommit_context_sha256": precommit,
        "status": producer.PLAN_STATUS,
    }
    plan_path = root / "replay-plan.json"
    immutable_write(plan_path, plan)
    bundle = {
        "claim_boundary": {
            "external_predecessor_commitment_present": False,
            "ordered_roles_8_10_replay_executed": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "member_spec": pin(paths["member_spec"]),
        "method_parameter_registry": pin(paths["method_parameters"]),
        "replay_plan": pin(plan_path),
        "schema": producer.BUNDLE_SCHEMA,
        "shared_precommit_context_sha256": precommit,
        "status": producer.BUNDLE_STATUS,
    }
    bundle_path = root / "candidate-bundle.json"
    immutable_write(bundle_path, bundle)
    authority = {
        "authority_identifier": "synthetic-test-predecessor",
        "trust_domain_identifier": "synthetic-pytest-only",
    }
    ordering = {
        "committed_before_roles_8_10_replay": True,
        "no_role_8_10_outputs_observed": True,
        "result_blind_plan": True,
    }
    commitment_claims = {
        "cryptographic_authenticity_verified_locally": False,
        "externality_proven_by_local_code": False,
        "roles_8_10_outputs_observed": False,
    }
    commitment = {
        "authentication": {
            "authentication_class": "independently_audited_predecessor_commit_hash",
            "evidence_identifier": "synthetic-pytest-evidence-only",
            "structural_validation_only": True,
        },
        "authority": authority,
        "candidate_bundle": pin(bundle_path),
        "claim_boundary": commitment_claims,
        "commitment_message_sha256": digest(
            producer.COMMITMENT_MESSAGE_DOMAIN,
            {
                "authority": authority,
                "candidate_bundle": pin(bundle_path),
                "claim_boundary": commitment_claims,
                "ordering": ordering,
            },
        ),
        "ordering": ordering,
        "schema": producer.COMMITMENT_SCHEMA,
        "status": producer.COMMITMENT_STATUS,
    }
    commitment_path = root / "synthetic-external-commitment.json"
    immutable_write(commitment_path, commitment)
    replay = digest(
        producer.REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": sha256(commitment_path.read_bytes()),
            "replay_plan_sha256": sha256(plan_path.read_bytes()),
            "shared_precommit_context_sha256": precommit,
        },
    )
    request = {
        "external_predecessor_commitment": pin(commitment_path),
        "plan": pin(plan_path),
        "plan_entry_id": producer.ROLE_NAME,
        "role": {"role_id": producer.ROLE_ID, "role_name": producer.ROLE_NAME},
        "schema": producer.REQUEST_SCHEMA,
        "shared_precommit_context_sha256": precommit,
        "shared_replay_context_sha256": replay,
        "status": producer.REQUEST_STATUS,
    }
    immutable_write(request_path, request)
    return {
        "artifact_path": artifact_path,
        "bundle": bundle,
        "bundle_path": bundle_path,
        "commitment": commitment,
        "commitment_path": commitment_path,
        "paths": paths,
        "plan": plan,
        "plan_path": plan_path,
        "receipt_path": receipt_path,
        "request": request,
        "request_path": request_path,
        "role8_runtime_closure": role8_runtime_closure,
        "role8_runtime_closure_path": role8_runtime_closure_path,
        "role_slots": role_slots,
        "role_sources": role_sources,
        "root": root,
    }


@pytest.fixture
def fixture(tmp_path: Path) -> dict[str, Any]:
    return make_fixture(tmp_path)


def test_producer_and_verifier_reach_only_exact_incomplete_hold(
    fixture: dict[str, Any],
) -> None:
    with pytest.raises(producer.CandidateKillingFailure) as producer_error:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert producer_error.value.code == producer.HOLD_NUMERICAL_INCOMPLETE
    assert str(producer_error.value) == (
        "HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE"
    )
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()

    with pytest.raises(verifier.CandidateKillingVerificationFailure) as verifier_error:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert verifier_error.value.code == verifier.HOLD_NUMERICAL_INCOMPLETE
    assert str(verifier_error.value) == (
        "HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE"
    )
    assert not fixture["artifact_path"].exists()
    assert not fixture["receipt_path"].exists()


def test_exact_role_protocol_method_and_authority_constants() -> None:
    assert (producer.ROLE_ID, producer.ROLE_NAME) == (10, "role10_killing_factor_geometry")
    assert producer.REQUEST_SCHEMA == (
        "encounter_continuum_c1_n0_killing_factor_geometry_request_v3"
    )
    assert producer.OUTPUT_SCHEMA == "encounter_c1_n0_killing_factor_geometry_source_v2"
    assert producer.RECEIPT_SCHEMA == (
        "encounter_c1_n0_killing_factor_geometry_validation_receipt_v1"
    )
    assert list(verifier.PARAMETER_ORDER[6:]) == [
        "killing_contact_profile_mpfr_192_v3",
        "killing_analytic_disk_area_mpfr_256_v3",
        "killing_source_independent_same_backend_verifier_v3",
        "killing_exact_contact_cell_classification_v3",
    ]
    assert len(verifier.PARAMETER_ORDER) == len(verifier.PARAMETER_DIGEST_ORDER) == 10
    assert producer.MEMBER_SHA256.startswith("b2982e4e")
    assert producer.MEMBER_IDENTITY_SHA256.startswith("68c8f9ee")
    assert producer.PARAMETER_SHA256.startswith("e403a957")
    assert producer.FACTORIZATION_SHA256.startswith("1cf32a65")
    assert producer.ANTI_VACUITY_POLICY_SHA256.startswith("599252aa")


def test_protocol_is_structural_only_and_result_blind(fixture: dict[str, Any]) -> None:
    assert set(fixture["request"]) == producer._REQUEST_KEYS
    assert set(fixture["plan"]) == producer._PLAN_KEYS
    role8_entry, role9_entry, role10_entry = fixture["plan"]["entries"]
    assert [entry["role"] for entry in (role8_entry, role9_entry, role10_entry)] == [8, 9, 10]
    assert set(role8_entry["implementation_runtime_closure"]) == {
        "path",
        "schema",
        "sha256",
    }
    assert role8_entry["implementation_runtime_closure"]["schema"] == (
        verifier.ROLE8_RUNTIME_CLOSURE_SCHEMA
    )
    assert role8_entry["method_selection"] == verifier._ROLE8_METHOD_SELECTION
    assert set(role8_entry["input_authorities"]) == verifier._ROLE8_INPUT_AUTHORITY_ROLES
    assert role8_entry["invocations"]["producer"]["argv"][1:3] == ["-I", "-B"]
    for entry, expected_method in (
        (role9_entry, verifier._ROLE9_METHOD_SELECTION),
        (role10_entry, verifier._ROLE10_METHOD_SELECTION),
    ):
        assert set(entry["implementation_runtime_closure"]) == {
            "producer",
            "runtime_requirements",
            "verifier",
        }
        assert set(entry["input_authorities"]) == verifier._INPUT_AUTHORITY_ROLES
        assert "configuration_initial_geometry" in entry["input_authorities"]
        assert entry["method_selection"] == expected_method
        assert "-I" not in entry["invocations"]["producer"]["argv"]
        assert "-B" not in entry["invocations"]["producer"]["argv"]
    encoded_partitions = [
        canonical(entry["partition_path_bindings"])
        for entry in (role8_entry, role9_entry, role10_entry)
    ]
    assert len(role8_entry["partition_path_bindings"]) == 36
    assert encoded_partitions[0] == encoded_partitions[1] == encoded_partitions[2]
    assert fixture["commitment"]["authentication"]["structural_validation_only"] is True
    assert all(value is False for value in fixture["commitment"]["claim_boundary"].values())
    producer._validate_result_blind_keys(fixture["plan"], "test plan")


def test_result_blind_scan_allows_legitimate_schema_and_status_text() -> None:
    producer._validate_result_blind_keys(
        {
            "schema": producer.PLAN_SCHEMA,
            "status": producer.PLAN_STATUS,
            "request_status": producer.REQUEST_STATUS,
            "nested": [producer.BUNDLE_STATUS, verifier.ROLE8_RUNTIME_CLOSURE_STATUS],
        },
        "legitimate schema/status fixture",
    )


def test_fresh_directory_slot_is_required(fixture: dict[str, Any]) -> None:
    fixture["artifact_path"].mkdir()
    with pytest.raises(producer.CandidateKillingFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert captured.value.code == producer.HOLD_REQUEST
    assert not fixture["receipt_path"].exists()


def test_sources_have_no_legacy_scientific_import_or_publication_path() -> None:
    forbidden_imports = {
        "build_continuum_c1_n0_candidate_native_raw_axis_formula_v2",
        "build_continuum_c1_n0_candidate_native_stationary_integrals_v2",
        "rate_defined_tensor_f0",
        "rate_defined_tensor_f0_production_killing_geometry",
    }
    forbidden_calls = {"mkdir", "makedirs", "replace", "rename", "link", "symlink"}
    for path in (PRODUCER_PATH, VERIFIER_PATH):
        tree = ast.parse(path.read_text("utf-8"))
        imports: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        assert imports.isdisjoint(forbidden_imports)
        assert calls.isdisjoint(forbidden_calls)


def test_noncanonical_numeric_json_is_rejected() -> None:
    with pytest.raises(verifier.CandidateKillingVerificationFailure) as captured:
        verifier._check_json_tree({"float": 1.0})
    assert captured.value.code == verifier.HOLD_AUTHORITY
