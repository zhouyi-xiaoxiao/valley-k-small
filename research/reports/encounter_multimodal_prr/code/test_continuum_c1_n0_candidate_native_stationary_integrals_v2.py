"""Committed-run tests for role-9 stationary physical integrals v2."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import stat
import sys
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"
VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_stationary_integrals_v2.py"

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


producer = _load("role9_v2_producer_tests", PRODUCER_PATH)
verifier = _load("role9_v2_verifier_tests", VERIFIER_PATH)


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


def contextual_pin(path: Path, schema: str, report_root: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(report_root).as_posix(),
        "schema": schema,
        "sha256": sha256(path.read_bytes()),
    }


def clone(root: Path, relative: Path) -> Path:
    destination = root / relative
    immutable_write(destination, (REPORT / relative).read_bytes())
    return destination


def role8_runtime_closure(
    producer_path: Path,
    verifier_path: Path,
) -> dict[str, Any]:
    package_directory = Path(producer.gmpy2.__file__).resolve().parent
    library_directory = package_directory.parent / "gmpy2.libs"
    candidates = {
        "gmpy2_extension": sorted(package_directory.glob("gmpy2*.so")),
        "libgmp": sorted(library_directory.glob("libgmp.*.dylib")),
        "libmpfr": sorted(library_directory.glob("libmpfr.*.dylib")),
        "libmpc": sorted(library_directory.glob("libmpc.*.dylib")),
    }
    assert all(len(paths) == 1 for paths in candidates.values())
    native_libraries = [
        {
            **pin(candidates[role][0].resolve()),
            "role": role,
        }
        for role in producer._ROLE8_NATIVE_LIBRARY_ROLES
    ]
    return {
        "claim_boundary": dict(producer._ROLE8_RUNTIME_CLAIMS),
        "code_inputs": {
            "producer": pin(producer_path),
            "verifier": pin(verifier_path),
        },
        "native_libraries": native_libraries,
        "native_runtime": producer._runtime_versions(),
        "python_executable": pin(Path(sys.executable).resolve()),
        "python_imports": {
            role: list(imports) for role, imports in producer._ROLE8_PYTHON_IMPORTS.items()
        },
        "report_local_dependencies": [],
        "schema": producer.ROLE8_RUNTIME_CLOSURE_SCHEMA,
        "status": producer.ROLE8_RUNTIME_CLOSURE_STATUS,
    }


def _peer_entry(
    *,
    entry_id: str,
    role: int,
    authorities: dict[str, dict[str, str]],
    output_dir: Path,
    partitions: list[dict[str, Any]],
    root: Path,
    role8_runtime_closure_path: Path,
    peer_sources: dict[int, tuple[Path, Path]],
) -> dict[str, Any]:
    request_path = root / f"role{role}.request.json"
    artifact_path = output_dir / f"role{role}.artifact.json"
    receipt_path = output_dir / f"role{role}.receipt.json"
    producer_path, verifier_path = peer_sources[role]
    if role == 8:
        runtime_closure: dict[str, Any] = {
            **pin(role8_runtime_closure_path),
            "schema": producer.ROLE8_RUNTIME_CLOSURE_SCHEMA,
        }
        invocation_prefix = [sys.executable, "-I", "-B"]
        selected_authorities = {
            key: dict(value)
            for key, value in authorities.items()
            if key in producer._ROLE8_INPUT_AUTHORITY_ROLES
        }
        method_selection: Any = [dict(record) for record in producer._ROLE8_METHOD_SELECTION]
        request_schema = producer.ROLE8_REQUEST_SCHEMA
        artifact_schema = producer.ROLE8_OUTPUT_SCHEMA
        receipt_schema = producer.ROLE8_RECEIPT_SCHEMA
    else:
        runtime_closure = {
            "producer": pin(producer_path),
            "runtime_requirements": producer._runtime_versions(),
            "verifier": pin(verifier_path),
        }
        invocation_prefix = [sys.executable]
        selected_authorities = {key: dict(value) for key, value in authorities.items()}
        method_selection = dict(producer._ROLE10_METHOD_SELECTION)
        request_schema = producer.ROLE10_REQUEST_SCHEMA
        artifact_schema = producer.ROLE10_OUTPUT_SCHEMA
        receipt_schema = producer.ROLE10_RECEIPT_SCHEMA
    placeholder = {
        "entry_id": entry_id,
        "implementation_runtime_closure": runtime_closure,
        "input_authorities": selected_authorities,
        "invocations": {
            "producer": {
                "argv": [
                    *invocation_prefix,
                    str(producer_path),
                    "--request",
                    str(request_path),
                    "--output",
                    str(artifact_path),
                ],
                "cwd": str(producer_path.parent.parent),
            },
            "verifier": {
                "argv": [
                    *invocation_prefix,
                    str(verifier_path),
                    "--request",
                    str(request_path),
                    "--output",
                    str(artifact_path),
                    "--receipt",
                    str(receipt_path),
                ],
                "cwd": str(producer_path.parent.parent),
            },
        },
        "method_selection": method_selection,
        "outputs": {
            "artifact": {
                "path": str(artifact_path),
                "schema": artifact_schema,
            },
            "validation_receipt": {
                "path": str(receipt_path),
                "schema": receipt_schema,
            },
        },
        "partition_path_bindings": [dict(binding) for binding in partitions],
        "request": {
            "path": str(request_path),
            "schema": request_schema,
            "status": producer.REQUEST_STATUS,
        },
        "role": role,
    }
    placeholder["precommit_projection_sha256"] = digest(
        producer.PRECOMMIT_PROJECTION_DOMAIN, placeholder
    )
    return placeholder


def make_fixture(tmp_path: Path) -> dict[str, Any]:
    root = tmp_path / "fixture"
    root.mkdir(mode=0o700)
    output_dir = tmp_path / "output"
    output_dir.mkdir(mode=0o700)
    paths = {role: clone(root, relative) for role, relative in RELATIVE_AUTHORITIES.items()}
    member = json.loads(paths["member_spec"].read_text("ascii"))
    configuration = json.loads(paths["configuration"].read_text("ascii"))
    assert sha256(paths["member_spec"].read_bytes()) == producer.MEMBER_SHA256
    assert sha256(paths["method_parameters"].read_bytes()) == producer.PARAMETER_SHA256
    assert sha256(paths["anti_vacuity_policy"].read_bytes()) == (
        producer.ANTI_VACUITY_POLICY_SHA256
    )

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
            paths["anti_vacuity_policy"], schemas["anti_vacuity_policy"], root
        ),
        "configuration": contextual_pin(paths["configuration"], schemas["configuration"], root),
        "configuration_row_inventory_sha256": digest(
            producer.CONFIGURATION_INVENTORY_DOMAIN,
            producer._configuration_inventory(configuration),
        ),
        "factorization": contextual_pin(paths["factorization"], schemas["factorization"], root),
        "ideal_formula": contextual_pin(paths["ideal_formula"], schemas["ideal_formula"], root),
        "member_identity_sha256": producer.MEMBER_IDENTITY_SHA256,
        "member_spec": contextual_pin(paths["member_spec"], schemas["member_spec"], root),
        "method_parameter_registry": contextual_pin(
            paths["method_parameters"], schemas["method_parameters"], root
        ),
        "partition_inventory_sha256": digest(
            producer.PARTITION_INVENTORY_DOMAIN,
            producer._partition_inventory(member),
        ),
        "reference_density": contextual_pin(
            paths["reference_density"], schemas["reference_density"], root
        ),
    }
    precommit = digest(producer.PRECOMMIT_CONTEXT_DOMAIN, shared_context)
    request_path = root / "role9.request.json"
    artifact_path = output_dir / "role9.stationary.json"
    receipt_path = output_dir / "role9.stationary.receipt.json"
    peer_code_directory = root / "peer-report" / "code"
    peer_sources: dict[int, tuple[Path, Path]] = {}
    for peer_role in (8, 10):
        filenames = producer._ROLE_SOURCE_FILENAMES[peer_role]
        cloned_sources: list[Path] = []
        for filename in filenames:
            source = CODE / filename
            destination = peer_code_directory / filename
            immutable_write(destination, source.read_bytes())
            cloned_sources.append(destination)
        peer_sources[peer_role] = (cloned_sources[0], cloned_sources[1])
    role8_runtime_closure_path = root / "role8.runtime-closure.json"
    immutable_write(
        role8_runtime_closure_path,
        role8_runtime_closure(*peer_sources[8]),
    )
    authorities = {role: pin(path) for role, path in paths.items()}
    role9_entry = {
        "entry_id": producer.ROLE_NAME,
        "implementation_runtime_closure": {
            "producer": pin(PRODUCER_PATH),
            "runtime_requirements": producer._runtime_versions(),
            "verifier": pin(VERIFIER_PATH),
        },
        "input_authorities": authorities,
        "invocations": {
            "producer": {
                "argv": [
                    sys.executable,
                    str(PRODUCER_PATH),
                    "--request",
                    str(request_path),
                    "--output",
                    str(artifact_path),
                ],
                "cwd": str(REPORT),
            },
            "verifier": {
                "argv": [
                    sys.executable,
                    str(VERIFIER_PATH),
                    "--request",
                    str(request_path),
                    "--output",
                    str(artifact_path),
                    "--receipt",
                    str(receipt_path),
                ],
                "cwd": str(REPORT),
            },
        },
        "method_selection": {
            "exact_parameter_id": producer.EXACT_PARAMETER_ID,
            "primary_parameter_id": producer.PRIMARY_PARAMETER_ID,
            "sentinel_parameter_id": producer.SENTINEL_PARAMETER_ID,
        },
        "outputs": {
            "artifact": {"path": str(artifact_path), "schema": producer.OUTPUT_SCHEMA},
            "validation_receipt": {
                "path": str(receipt_path),
                "schema": producer.RECEIPT_SCHEMA,
            },
        },
        "partition_path_bindings": partitions,
        "request": {
            "path": str(request_path),
            "schema": producer.REQUEST_SCHEMA,
            "status": producer.REQUEST_STATUS,
        },
        "role": producer.ROLE_ID,
    }
    role9_entry["precommit_projection_sha256"] = digest(
        producer.PRECOMMIT_PROJECTION_DOMAIN, role9_entry
    )
    plan = {
        "claim_boundary": {
            "external_predecessor_commitment_present": False,
            "ordered_roles_8_10_replay_executed": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "entries": [
            _peer_entry(
                entry_id="role8_raw_axis_formula_primitive",
                role=8,
                authorities=authorities,
                output_dir=output_dir,
                partitions=partitions,
                root=root,
                role8_runtime_closure_path=role8_runtime_closure_path,
                peer_sources=peer_sources,
            ),
            role9_entry,
            _peer_entry(
                entry_id="role10_killing_factor_geometry",
                role=10,
                authorities=authorities,
                output_dir=output_dir,
                partitions=partitions,
                root=root,
                role8_runtime_closure_path=role8_runtime_closure_path,
                peer_sources=peer_sources,
            ),
        ],
        "schema": producer.PLAN_SCHEMA,
        "shared_context": shared_context,
        "shared_precommit_context_sha256": precommit,
        "status": producer.PLAN_STATUS,
    }
    peer_authority_path = (
        root / "peer-role10-authority" / RELATIVE_AUTHORITIES["configuration_design"]
    )
    immutable_write(
        peer_authority_path,
        paths["configuration_design"].read_bytes(),
    )
    role10_entry = plan["entries"][2]
    role10_entry["input_authorities"]["configuration_design"] = pin(peer_authority_path)
    role10_projection = {
        key: value for key, value in role10_entry.items() if key != "precommit_projection_sha256"
    }
    role10_entry["precommit_projection_sha256"] = digest(
        producer.PRECOMMIT_PROJECTION_DOMAIN,
        role10_projection,
    )
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
    commitment_message = digest(
        producer.COMMITMENT_MESSAGE_DOMAIN,
        {
            "authority": authority,
            "candidate_bundle": pin(bundle_path),
            "claim_boundary": commitment_claims,
            "ordering": ordering,
        },
    )
    commitment = {
        "authentication": {
            "authentication_class": "independently_audited_predecessor_commit_hash",
            "evidence_identifier": "synthetic-pytest-evidence-only",
            "structural_validation_only": True,
        },
        "authority": authority,
        "candidate_bundle": pin(bundle_path),
        "claim_boundary": commitment_claims,
        "commitment_message_sha256": commitment_message,
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
        "configuration": configuration,
        "member": member,
        "paths": paths,
        "plan": plan,
        "plan_path": plan_path,
        "peer_sources": peer_sources,
        "peer_authority_path": peer_authority_path,
        "receipt_path": receipt_path,
        "request": request,
        "request_path": request_path,
        "root": root,
        "role8_runtime_closure_path": role8_runtime_closure_path,
    }


@pytest.fixture
def fixture(tmp_path: Path) -> dict[str, Any]:
    return make_fixture(tmp_path)


def test_full_twelve_row_committed_replay_and_receipt(fixture: dict[str, Any]) -> None:
    assert (
        producer.main(
            [
                "--request",
                str(fixture["request_path"]),
                "--output",
                str(fixture["artifact_path"]),
            ]
        )
        == 0
    )
    artifact_path = fixture["artifact_path"]
    assert stat.S_IMODE(artifact_path.stat().st_mode) == 0o444
    assert artifact_path.stat().st_nlink == 1
    artifact = json.loads(artifact_path.read_text("ascii"))
    assert set(artifact) == {
        "axis_stream",
        "claim_boundary",
        "member_binding",
        "method_binding",
        "partition_closure",
        "replay_binding",
        "role",
        "rows",
        "runtime_binding",
        "schema",
        "source_pins",
        "status",
        "summary",
    }
    assert len(artifact["rows"]) == 12
    assert artifact["summary"]["factorized_axis_cell_count"] == 5_037
    assert artifact["summary"]["total_virtual_tensor_state_count"] == 34_787_462
    assert artifact["axis_stream"]["record_count"] == 5_229
    assert artifact["partition_closure"]["node_count"] == 50
    assert artifact["partition_closure"]["edge_count"] == 49
    assert artifact["partition_closure"]["nodes"] == sorted(
        artifact["partition_closure"]["nodes"], key=lambda node: node["id"]
    )
    assert artifact["partition_closure"]["edges"] == sorted(
        artifact["partition_closure"]["edges"],
        key=lambda edge: (edge["from"], edge["relation"], edge["to"]),
    )
    assert artifact["method_binding"]["dense_tensor_materialized"] is False
    assert all(value is False for value in artifact["claim_boundary"].values())

    assert (
        verifier.main(
            [
                "--request",
                str(fixture["request_path"]),
                "--output",
                str(artifact_path),
                "--receipt",
                str(fixture["receipt_path"]),
            ]
        )
        == 0
    )
    receipt_path = fixture["receipt_path"]
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o444
    assert receipt_path.stat().st_nlink == 1
    receipt = json.loads(receipt_path.read_text("ascii"))
    assert receipt["schema"] == verifier.RECEIPT_SCHEMA
    assert receipt["status"] == verifier.RECEIPT_STATUS
    assert receipt["artifact"]["sha256"] == sha256(artifact_path.read_bytes())
    assert receipt["stream_binding"] == artifact["axis_stream"]
    assert receipt["partition_closure"]["sha256"] == artifact["partition_closure"]["sha256"]
    assert all(value is False for value in receipt["claim_boundary"].values())


def test_stream_digest_and_partition_dag_are_independently_reproducible(
    fixture: dict[str, Any],
) -> None:
    payload = producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    artifact = json.loads(payload)
    records = verifier._axis_stream_records(artifact["rows"])
    assert verifier._stream_digest(records) == artifact["axis_stream"]["sha256"]
    assert len(records) == artifact["axis_stream"]["record_count"]
    independent_dag = verifier._partition_closure(
        fixture["member"],
        fixture["configuration"],
        verifier._partition_inventory(fixture["member"]),
    )
    assert independent_dag == artifact["partition_closure"]


def test_protocol_blindness_and_synthetic_commitment_is_not_overclaimed(
    fixture: dict[str, Any],
) -> None:
    request = fixture["request"]
    plan = fixture["plan"]
    commitment = fixture["commitment"]
    assert set(request) == producer._REQUEST_KEYS
    assert set(plan) == producer._PLAN_KEYS
    assert all(set(entry) == producer._PLAN_ENTRY_KEYS for entry in plan["entries"])
    assert commitment["authority"]["authority_identifier"] == "synthetic-test-predecessor"
    assert commitment["authentication"]["structural_validation_only"] is True
    assert all(value is False for value in commitment["claim_boundary"].values())
    producer._validate_result_blind_keys(plan, label="test plan")
    verifier._validate_result_blind_keys(plan, "test plan")
    producer._validate_result_blind_keys({"sha256": "0" * 64}, label="plain input pin")
    verifier._validate_result_blind_keys({"sha256": "0" * 64}, "plain input pin")
    role8_entry = plan["entries"][0]
    closure = json.loads(fixture["role8_runtime_closure_path"].read_text(encoding="ascii"))
    assert set(closure) == producer._ROLE8_RUNTIME_CLOSURE_KEYS
    assert closure["claim_boundary"] == producer._ROLE8_RUNTIME_CLAIMS
    assert closure["python_imports"] == producer._ROLE8_PYTHON_IMPORTS
    assert closure["report_local_dependencies"] == []
    assert [item["role"] for item in closure["native_libraries"]] == list(
        producer._ROLE8_NATIVE_LIBRARY_ROLES
    )
    assert role8_entry["invocations"]["producer"]["argv"][:3] == [
        sys.executable,
        "-I",
        "-B",
    ]
    assert role8_entry["invocations"]["verifier"]["argv"][:3] == [
        sys.executable,
        "-I",
        "-B",
    ]
    assert closure["code_inputs"]["producer"]["path"] != closure["code_inputs"]["verifier"]["path"]


def test_source_separation_and_no_v1_scientific_backend_import() -> None:
    forbidden = {
        "build_continuum_c1_n0_candidate_native_stationary_integrals_v1",
        "validate_continuum_c1_n0_candidate_native_stationary_integrals_v1",
        "build_continuum_c1_stationary_integral_source_v1",
        "validate_continuum_c1_stationary_integral_source_v1",
        "rate_defined_tensor_f0",
    }
    for path in (PRODUCER_PATH, VERIFIER_PATH):
        tree = ast.parse(path.read_text("utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert imported.isdisjoint(forbidden)
    verifier_source = VERIFIER_PATH.read_text("utf-8")
    assert f"import {PRODUCER_PATH.stem}" not in verifier_source
    assert f"from {PRODUCER_PATH.stem}" not in verifier_source
    assert "_stationary_integrals_v1" not in PRODUCER_PATH.read_text("utf-8")
    assert "_stationary_integrals_v1" not in VERIFIER_PATH.read_text("utf-8")


def test_preexisting_artifact_and_receipt_are_rejected(fixture: dict[str, Any]) -> None:
    fixture["artifact_path"].write_bytes(b"occupied\n")
    fixture["artifact_path"].chmod(0o444)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"])
    assert captured.value.code == producer.HOLD_REQUEST
    fixture["artifact_path"].unlink()
    producer._publish(
        fixture["artifact_path"],
        producer.build_from_request(fixture["request_path"], fixture["artifact_path"]),
    )
    fixture["receipt_path"].write_bytes(b"occupied\n")
    fixture["receipt_path"].chmod(0o444)
    with pytest.raises(verifier.CandidateStationaryVerificationFailure) as captured_verify:
        verifier.validate(
            fixture["request_path"],
            fixture["artifact_path"],
            fixture["receipt_path"],
        )
    assert captured_verify.value.code == verifier.HOLD_REQUEST


def test_noncanonical_numeric_json_is_rejected() -> None:
    with pytest.raises(verifier.CandidateStationaryVerificationFailure):
        verifier._check_json_tree({"float": 1.0})
