from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import continuum_c1_n0_roles_8_10_protocol_constants_v2 as protocol
import pytest
import validate_continuum_c1_n0_roles_8_10_precommit_package_v2 as validator

REPORT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = Path(validator.__file__).resolve()


@dataclass
class PrecommitFixture:
    report: Path
    operation_model: Path
    runtime_closure: Path
    plan: Path
    bundle: Path
    runtime_document: dict[str, Any]
    plan_document: dict[str, Any]
    bundle_document: dict[str, Any]
    slot_paths: dict[str, Path]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("ascii")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def pin(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256_file(path)}


def schema_pin(path: Path, schema: str) -> dict[str, str]:
    return {"path": str(path), "schema": schema, "sha256": sha256_file(path)}


def write_immutable(path: Path, value: Any, *, mode: int = 0o444) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        path.chmod(0o644)
    path.write_bytes(canonical_bytes(value))
    path.chmod(mode)


def write_source(path: Path, text: str, *, mode: int = 0o444) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def copy_immutable(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    target.chmod(0o444)


def copy_immutable_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target)
    for path in sorted(target.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(0o444)
        elif path.is_dir():
            path.chmod(0o555)
    target.chmod(0o555)


def entry_digest(entry: dict[str, Any]) -> str:
    projection = dict(entry)
    projection.pop("precommit_projection_sha256", None)
    raw = canonical_bytes(projection)
    return sha256_bytes(
        protocol.ENTRY_PROJECTION_DOMAIN.encode("ascii") + b"\0" + len(raw).to_bytes(8, "big") + raw
    )


def shared_digest(shared_context: dict[str, Any]) -> str:
    return sha256_bytes(
        protocol.SHARED_PRECOMMIT_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(shared_context)
    )


def _resolved_builtin() -> list[dict[str, Any]]:
    return [
        {
            "import_name": "builtins",
            "origin_kind": "builtin",
            "path": None,
            "sha256": None,
        }
    ]


def _role_invocations(
    role_id: int,
    python_path: Path,
    producer: Path,
    verifier_path: Path,
    slots: dict[str, Path],
) -> dict[str, Any]:
    if role_id == 8:
        return {
            "producer": {
                "argv": [
                    str(python_path),
                    "-I",
                    "-B",
                    str(producer),
                    "--request",
                    str(slots["role8_request"]),
                    "--output",
                    str(slots["role8_artifact"]),
                ],
                "invocation_id": "role8_raw_axis_formula_producer_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
            "verifier": {
                "argv": [
                    str(python_path),
                    "-I",
                    "-B",
                    str(verifier_path),
                    "--request",
                    str(slots["role8_request"]),
                    "--output",
                    str(slots["role8_artifact"]),
                    "--receipt",
                    str(slots["role8_validation_receipt"]),
                ],
                "invocation_id": "role8_raw_axis_formula_verifier_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
        }
    if role_id == 9:
        return {
            "producer": {
                "argv": [
                    str(python_path),
                    "-I",
                    "-B",
                    str(producer),
                    "--request",
                    str(slots["role9_request"]),
                    "--output",
                    str(slots["role9_artifact"]),
                ],
                "invocation_id": "role9_stationary_integrals_producer_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
            "verifier": {
                "argv": [
                    str(python_path),
                    "-I",
                    "-B",
                    str(verifier_path),
                    "--request",
                    str(slots["role9_request"]),
                    "--output",
                    str(slots["role9_artifact"]),
                    "--receipt",
                    str(slots["role9_validation_receipt"]),
                ],
                "invocation_id": "role9_stationary_integrals_verifier_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
        }
    return {
        "transaction_orchestrator": {
            "argv": [
                str(python_path),
                "-I",
                "-B",
                str(verifier_path),
                "--request",
                str(slots["role10_request"]),
                "--output",
                str(slots["role10_artifact_directory"]),
                "--semantic-receipt",
                str(slots["role10_semantic_receipt"]),
                "--receipt",
                str(slots["role10_outer_validation_receipt"]),
            ],
            "invocation_id": "role10_killing_geometry_transaction_orchestrator_v3",
            "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
        }
    }


def create_fixture(tmp_path: Path) -> PrecommitFixture:
    report = tmp_path / "report"
    operation_model = report.joinpath(
        *PurePosixPath(protocol.OPERATION_MODEL_REPORT_RELATIVE_PATH).parts
    )
    copy_immutable(REPORT / protocol.OPERATION_MODEL_REPORT_RELATIVE_PATH, operation_model)
    model = json.loads(operation_model.read_text(encoding="ascii"))

    authority_paths: dict[str, Path] = {}
    for key in (
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "killing_geometry",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
    ):
        relative = model["authority_bindings"][key]["path"]
        target = report.joinpath(*PurePosixPath(relative).parts)
        copy_immutable(REPORT / relative, target)
        authority_paths[key] = target

    mirror_relative = model["authority_bindings"]["sealed_authentication_mirror"]["path"]
    source_mirror = REPORT / mirror_relative
    target_mirror = report.joinpath(*PurePosixPath(mirror_relative).parts)
    copy_immutable_tree(source_mirror.parent, target_mirror.parent)
    authority_paths["sealed_authentication_mirror"] = target_mirror

    runtime_support = tmp_path / "runtime_support"
    python_path = runtime_support / "python3-pinned"
    write_source(python_path, "sealed-python-runtime\n", mode=0o555)
    library_paths: dict[str, Path] = {}
    for role in protocol.NATIVE_LIBRARY_ROLES:
        suffix = ".so" if role == "gmpy2_extension" else ".dylib"
        path = runtime_support / f"{role}{suffix}"
        write_source(path, f"sealed-native-{role}\n")
        library_paths[role] = path

    code_dir = report / "code"
    source_paths: dict[int, dict[str, Path]] = {}
    for role_id in protocol.ROLE_ORDER:
        source_paths[role_id] = {}
        for side in ("producer", "verifier"):
            basename = protocol.SOURCE_BASENAMES[role_id][f"{side}_basename"]
            path = code_dir / basename
            write_source(
                path,
                "import builtins\n"
                f"ROLE_ID = {role_id}\n"
                f"SIDE = {side!r}\n"
                "TOKEN = builtins.__name__\n",
            )
            source_paths[role_id][side] = path
    runner_path = code_dir / protocol.GLOBAL_RUNNER_BASENAME
    write_source(
        runner_path,
        f"import builtins\nRUNNER_ID = {protocol.GLOBAL_RUNNER_ID!r}\nTOKEN = builtins.__name__\n",
    )

    roles: list[dict[str, Any]] = []
    for role_id in protocol.ROLE_ORDER:
        roles.append(
            {
                "allowed_shared_protocol": None,
                "code_inputs": {
                    "producer": pin(source_paths[role_id]["producer"]),
                    "verifier": pin(source_paths[role_id]["verifier"]),
                },
                "native_libraries": [
                    {
                        "path": str(library_paths[library_role]),
                        "role": library_role,
                        "sha256": sha256_file(library_paths[library_role]),
                    }
                    for library_role in protocol.NATIVE_LIBRARY_ROLES
                ],
                "native_runtime": {
                    "gmp": "synthetic-gmp",
                    "gmpy2": "synthetic-gmpy2",
                    "mpc": "synthetic-mpc",
                    "mpfr": "synthetic-mpfr",
                    "python_abi": "synthetic-cpython-abi",
                    "python_version": "synthetic-python-version",
                },
                "python_executable": pin(python_path),
                "python_imports": {"producer": ["builtins"], "verifier": ["builtins"]},
                "report_local_dependencies": {"producer": [], "verifier": []},
                "resolved_python_dependencies": {
                    "producer": _resolved_builtin(),
                    "verifier": _resolved_builtin(),
                },
                "role_id": role_id,
                "role_name": protocol.ROLE_NAMES[role_id],
            }
        )

    runtime_document = {
        "claim_boundary": dict(protocol.RUNTIME_CLAIM_BOUNDARY),
        "global_runner": {
            "code_input": pin(runner_path),
            "python_executable": pin(python_path),
            "python_imports": ["builtins"],
            "python_runtime": {
                "python_abi": "synthetic-cpython-abi",
                "python_version": "synthetic-python-version",
            },
            "report_local_dependencies": [],
            "resolved_python_dependencies": _resolved_builtin(),
            "runner_contract_sha256": protocol.GLOBAL_RUNNER_CONTRACT_SHA256,
            "runner_id": protocol.GLOBAL_RUNNER_ID,
        },
        "host_runtime_trust_boundary": {
            "byte_complete": False,
            "darwin_kernel_release": "synthetic-darwin-release",
            "machine": "synthetic-machine",
            "macos_build_version": "synthetic-build",
            "scope": list(protocol.HOST_RUNTIME_SCOPE),
            "status": protocol.HOST_RUNTIME_STATUS,
        },
        "process_contract": model["process_contract"],
        "roles": roles,
        "schema": protocol.RUNTIME_CLOSURE_SCHEMA,
        "status": protocol.RUNTIME_CLOSURE_STATUS,
    }
    runtime_closure = report / "artifacts/data/continuum_c1_n0_runtime_closure_v1.json"
    write_immutable(runtime_closure, runtime_document)

    shared_context: dict[str, Any] = {
        "anti_vacuity_policy": schema_pin(
            authority_paths["anti_vacuity_policy"],
            protocol.AUTHORITY_SCHEMAS["anti_vacuity_policy"],
        ),
        "configuration": schema_pin(
            authority_paths["configuration"], protocol.AUTHORITY_SCHEMAS["configuration"]
        ),
        "configuration_row_inventory_sha256": protocol.CONFIGURATION_ROW_INVENTORY_SHA256,
        "factorization": schema_pin(
            authority_paths["factorization"], protocol.AUTHORITY_SCHEMAS["factorization"]
        ),
        "ideal_formula": schema_pin(
            authority_paths["ideal_formula"], protocol.AUTHORITY_SCHEMAS["ideal_formula"]
        ),
        "member_identity_sha256": protocol.MEMBER_IDENTITY_SHA256,
        "member_spec": schema_pin(
            authority_paths["member_spec"], protocol.AUTHORITY_SCHEMAS["member_spec"]
        ),
        "method_parameter_registry": schema_pin(
            authority_paths["method_parameter_registry"],
            protocol.AUTHORITY_SCHEMAS["method_parameter_registry"],
        ),
        "partition_inventory_sha256": protocol.PARTITION_INVENTORY_SHA256,
        "reference_density": schema_pin(
            authority_paths["reference_density"],
            protocol.AUTHORITY_SCHEMAS["reference_density"],
        ),
        "role10_operation_model": schema_pin(operation_model, protocol.OPERATION_MODEL_SCHEMA),
    }

    slot_parent = tmp_path / "future_slots"
    slot_parent.mkdir(mode=0o700)
    slot_paths: dict[str, Path] = {}
    slots: list[dict[str, Any]] = []
    for template in protocol.SLOT_TEMPLATES:
        slot_id = template["slot_id"]
        slot_path = slot_parent / slot_id
        slot_paths[slot_id] = slot_path
        slots.append({**template, "path": str(slot_path)})

    member = json.loads(authority_paths["member_spec"].read_text(encoding="ascii"))
    mirror = json.loads(target_mirror.read_text(encoding="ascii"))
    mirror_entries = {
        entry["source_report_relative_path"]: entry
        for entry in mirror["entries"]
        if entry["semantic_role"] == "member_v4_partition"
    }
    partitions: list[dict[str, Any]] = []
    for configuration_index, row in enumerate(member["n0_sequence_bindings"]):
        for axis_index, coordinate in enumerate(protocol.COORDINATE_ORDER):
            axis = row["n0_axes"][axis_index]
            relative = axis["partition_report_relative_path"]
            entry = mirror_entries[relative]
            mirror_path = target_mirror.parent.joinpath(
                *PurePosixPath(entry["mirror_relative_path"]).parts
            )
            partitions.append(
                {
                    "configuration_index": configuration_index,
                    "coordinate": coordinate,
                    "member_report_relative_path": relative,
                    "path": str(mirror_path),
                    "sha256": axis["partition_sha256"],
                }
            )

    direct_authority_pins = {
        key: schema_pin(authority_paths[key], protocol.AUTHORITY_SCHEMAS[key])
        for key in (
            "anti_vacuity_policy",
            "configuration",
            "factorization",
            "ideal_formula",
            "killing_geometry",
            "member_spec",
            "method_parameter_registry",
            "reference_density",
            "sealed_authentication_mirror",
        )
    }
    entries: list[dict[str, Any]] = []
    for role_id in protocol.ROLE_ORDER:
        entry = {
            "entry_id": protocol.ROLE_NAMES[role_id],
            "input_authorities": {
                key: direct_authority_pins[key]
                for key in protocol.NORMATIVE_INPUT_AUTHORITY_KEYS[role_id]
            },
            "invocations": _role_invocations(
                role_id,
                python_path,
                source_paths[role_id]["producer"],
                source_paths[role_id]["verifier"],
                slot_paths,
            ),
            "method_selection": list(protocol.METHOD_PARAMETER_IDS[role_id]),
            "output_slot_ids": list(protocol.OUTPUT_SLOT_IDS[role_id]),
            "partition_path_bindings": partitions,
            "precommit_projection_sha256": "0" * 64,
            "request_slot_id": protocol.REQUEST_SLOT_IDS[role_id],
            "role": role_id,
            "runtime_role_id": role_id,
        }
        entry["precommit_projection_sha256"] = entry_digest(entry)
        entries.append(entry)

    plan_document = {
        "claim_boundary": dict(protocol.PLAN_CLAIM_BOUNDARY),
        "entries": entries,
        "runtime_closure": schema_pin(runtime_closure, protocol.RUNTIME_CLOSURE_SCHEMA),
        "schema": protocol.PLAN_SCHEMA,
        "shared_context": shared_context,
        "shared_precommit_context_sha256": shared_digest(shared_context),
        "slots": slots,
        "status": protocol.PLAN_STATUS,
    }
    plan = report / "artifacts/data/continuum_c1_n0_replay_plan_v2.json"
    write_immutable(plan, plan_document)

    bundle_document = {
        "claim_boundary": dict(protocol.PLAN_CLAIM_BOUNDARY),
        "member_spec": schema_pin(
            authority_paths["member_spec"], protocol.AUTHORITY_SCHEMAS["member_spec"]
        ),
        "method_parameter_registry": schema_pin(
            authority_paths["method_parameter_registry"],
            protocol.AUTHORITY_SCHEMAS["method_parameter_registry"],
        ),
        "operation_model": schema_pin(operation_model, protocol.OPERATION_MODEL_SCHEMA),
        "replay_plan": schema_pin(plan, protocol.PLAN_SCHEMA),
        "runtime_closure": schema_pin(runtime_closure, protocol.RUNTIME_CLOSURE_SCHEMA),
        "schema": protocol.BUNDLE_SCHEMA,
        "shared_precommit_context_sha256": plan_document["shared_precommit_context_sha256"],
        "status": protocol.BUNDLE_STATUS,
    }
    bundle = report / "artifacts/data/continuum_c1_n0_precommit_bundle_v2.json"
    write_immutable(bundle, bundle_document)

    return PrecommitFixture(
        report=report,
        operation_model=operation_model,
        runtime_closure=runtime_closure,
        plan=plan,
        bundle=bundle,
        runtime_document=runtime_document,
        plan_document=plan_document,
        bundle_document=bundle_document,
        slot_paths=slot_paths,
    )


def reseal_runtime(fixture: PrecommitFixture) -> None:
    write_immutable(fixture.runtime_closure, fixture.runtime_document)
    fixture.plan_document["runtime_closure"] = schema_pin(
        fixture.runtime_closure, protocol.RUNTIME_CLOSURE_SCHEMA
    )
    fixture.bundle_document["runtime_closure"] = schema_pin(
        fixture.runtime_closure, protocol.RUNTIME_CLOSURE_SCHEMA
    )
    reseal_plan(fixture)


def reseal_plan(fixture: PrecommitFixture) -> None:
    write_immutable(fixture.plan, fixture.plan_document)
    fixture.bundle_document["replay_plan"] = schema_pin(fixture.plan, protocol.PLAN_SCHEMA)
    write_immutable(fixture.bundle, fixture.bundle_document)


def reseal_authority_and_operation_model(
    fixture: PrecommitFixture,
    monkeypatch: pytest.MonkeyPatch,
    authority_key: str,
    authority_document: dict[str, Any],
    *,
    member_identity_sha256: str | None = None,
) -> None:
    authority_path = Path(fixture.plan_document["shared_context"][authority_key]["path"])
    write_immutable(authority_path, authority_document)
    authority_sha256 = sha256_file(authority_path)
    monkeypatch.setitem(protocol.AUTHORITY_SHA256, authority_key, authority_sha256)
    monkeypatch.setitem(validator.protocol.AUTHORITY_SHA256, authority_key, authority_sha256)

    operation_model = json.loads(fixture.operation_model.read_text(encoding="ascii"))
    operation_model["authority_bindings"][authority_key]["sha256"] = authority_sha256
    if member_identity_sha256 is not None:
        operation_model["authority_model"]["member_identity_sha256"] = member_identity_sha256
        operation_model["replay_plan_contract"]["shared_context_contract"]["field_schemas"][
            "member_identity_sha256"
        ] = f"literal_{member_identity_sha256}"
        monkeypatch.setattr(protocol, "MEMBER_IDENTITY_SHA256", member_identity_sha256)
        monkeypatch.setattr(validator.protocol, "MEMBER_IDENTITY_SHA256", member_identity_sha256)
    write_immutable(fixture.operation_model, operation_model)
    monkeypatch.setattr(protocol, "OPERATION_MODEL_SHA256", sha256_file(fixture.operation_model))
    monkeypatch.setattr(
        validator.protocol,
        "OPERATION_MODEL_SHA256",
        sha256_file(fixture.operation_model),
    )

    authority_pin = schema_pin(authority_path, protocol.AUTHORITY_SCHEMAS[authority_key])
    shared_context = fixture.plan_document["shared_context"]
    shared_context[authority_key] = authority_pin
    shared_context["role10_operation_model"] = schema_pin(
        fixture.operation_model, protocol.OPERATION_MODEL_SCHEMA
    )
    if member_identity_sha256 is not None:
        shared_context["member_identity_sha256"] = member_identity_sha256
    fixture.plan_document["shared_precommit_context_sha256"] = shared_digest(shared_context)

    for entry in fixture.plan_document["entries"]:
        if authority_key in entry["input_authorities"]:
            entry["input_authorities"][authority_key] = authority_pin
        entry["precommit_projection_sha256"] = entry_digest(entry)

    if authority_key in fixture.bundle_document:
        fixture.bundle_document[authority_key] = authority_pin
    fixture.bundle_document["operation_model"] = schema_pin(
        fixture.operation_model, protocol.OPERATION_MODEL_SCHEMA
    )
    fixture.bundle_document["shared_precommit_context_sha256"] = fixture.plan_document[
        "shared_precommit_context_sha256"
    ]
    reseal_plan(fixture)


def validate(fixture: PrecommitFixture) -> dict[str, Any]:
    return validator.validate_package(
        fixture.operation_model,
        fixture.runtime_closure,
        fixture.plan,
        fixture.bundle,
    )


def test_synthetic_precommit_package_v2_passes(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    ack = validate(fixture)
    assert ack["schema"] == validator.PASS_SCHEMA
    assert ack["status"] == validator.PASS_STATUS
    assert ack["candidate_bundle_sha256"] == sha256_file(fixture.bundle)
    assert all(not path.exists() for path in fixture.slot_paths.values())


def test_synthetic_precommit_package_v2_cli_passes(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    completed = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_PATH),
            "--operation-model",
            str(fixture.operation_model),
            "--runtime-closure",
            str(fixture.runtime_closure),
            "--plan",
            str(fixture.plan),
            "--candidate-bundle",
            str(fixture.bundle),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert json.loads(completed.stdout)["status"] == validator.PASS_STATUS


def test_canonical_package_json_mode_0400_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.bundle.chmod(0o400)
    with pytest.raises(validator.ProtocolFailure, match="exact mode 0444 required"):
        validate(fixture)


def test_v3_source_mode_0555_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    producer = Path(fixture.runtime_document["roles"][0]["code_inputs"]["producer"]["path"])
    producer.chmod(0o555)
    with pytest.raises(validator.ProtocolFailure, match="exact mode 0444 required"):
        validate(fixture)


def test_pinned_python_mode_0444_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    python_executable = Path(fixture.runtime_document["roles"][0]["python_executable"]["path"])
    python_executable.chmod(0o444)
    with pytest.raises(validator.ProtocolFailure, match="exact mode 0555 required"):
        validate(fixture)


def test_plan_v1_downgrade_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.plan_document["schema"] = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v1"
    write_immutable(fixture.plan, fixture.plan_document)
    fixture.bundle_document["replay_plan"] = schema_pin(
        fixture.plan, "encounter_continuum_c1_n0_roles_8_10_replay_plan_v1"
    )
    write_immutable(fixture.bundle, fixture.bundle_document)
    with pytest.raises(validator.ProtocolFailure, match="replay plan schema/status"):
        validate(fixture)


def test_runtime_all_false_claim_map_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.runtime_document["claim_boundary"] = {
        key: False for key in protocol.RUNTIME_CLAIM_BOUNDARY
    }
    reseal_runtime(fixture)
    with pytest.raises(validator.ProtocolFailure, match="runtime closure schema/status/claim"):
        validate(fixture)


@pytest.mark.parametrize(
    ("claim", "replacement"),
    [
        ("complete_report_local_and_declared_numerical_runtime_closure", 1),
        ("complete_host_runtime_image", 0),
    ],
)
def test_runtime_boolean_claim_cannot_be_encoded_as_integer(
    tmp_path: Path, claim: str, replacement: int
) -> None:
    fixture = create_fixture(tmp_path)
    fixture.runtime_document["claim_boundary"][claim] = replacement
    reseal_runtime(fixture)
    with pytest.raises(validator.ProtocolFailure, match="runtime closure schema/status/claim"):
        validate(fixture)


def test_plan_boolean_claim_cannot_be_encoded_as_integer(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.plan_document["claim_boundary"]["external_predecessor_commitment_present"] = 0
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="claim boundary|boolean"):
        validate(fixture)


def test_bundle_boolean_claim_cannot_be_encoded_as_integer(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.bundle_document["claim_boundary"]["release_eligible"] = 0
    write_immutable(fixture.bundle, fixture.bundle_document)
    with pytest.raises(validator.ProtocolFailure, match="candidate bundle schema/status/claim"):
        validate(fixture)


def test_slot_integer_ordinal_cannot_be_encoded_as_boolean(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.plan_document["slots"][1]["ordinal"] = True
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="ordinal|template field drift"):
        validate(fixture)


def test_partition_configuration_index_cannot_be_encoded_as_boolean(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    for entry in fixture.plan_document["entries"]:
        entry["partition_path_bindings"] = json.loads(json.dumps(entry["partition_path_bindings"]))
        entry["partition_path_bindings"][0]["configuration_index"] = False
        entry["precommit_projection_sha256"] = entry_digest(entry)
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="partition bindings mismatch"):
        validate(fixture)


def test_slot_reordering_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.plan_document["slots"][0], fixture.plan_document["slots"][1] = (
        fixture.plan_document["slots"][1],
        fixture.plan_document["slots"][0],
    )
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="slot 0: template field drift"):
        validate(fixture)


def test_configuration_inventory_is_recomputed_from_authenticated_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = create_fixture(tmp_path)
    frozen_inventory_sha256 = protocol.CONFIGURATION_ROW_INVENTORY_SHA256
    configuration_path = Path(fixture.plan_document["shared_context"]["configuration"]["path"])
    configuration = json.loads(configuration_path.read_text(encoding="ascii"))
    configuration["configurations"][0]["purpose"] = "synthetic authenticated inventory drift"
    reseal_authority_and_operation_model(
        fixture,
        monkeypatch,
        "configuration",
        configuration,
    )
    assert protocol.CONFIGURATION_ROW_INVENTORY_SHA256 == frozen_inventory_sha256
    with pytest.raises(validator.ProtocolFailure, match="inventory digest replay mismatch"):
        validate(fixture)


def test_partition_inventory_is_recomputed_from_authenticated_member(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = create_fixture(tmp_path)
    frozen_inventory_sha256 = protocol.PARTITION_INVENTORY_SHA256
    member_path = Path(fixture.plan_document["shared_context"]["member_spec"]["path"])
    member = json.loads(member_path.read_text(encoding="ascii"))
    member["n0_sequence_bindings"][0]["n0_axes"][0]["alignment"] = (
        "synthetic_authenticated_inventory_drift"
    )
    member_identity_sha256 = validator._member_identity(member)
    member["member_identity_sha256"] = member_identity_sha256
    reseal_authority_and_operation_model(
        fixture,
        monkeypatch,
        "member_spec",
        member,
        member_identity_sha256=member_identity_sha256,
    )
    assert protocol.PARTITION_INVENTORY_SHA256 == frozen_inventory_sha256
    with pytest.raises(validator.ProtocolFailure, match="inventory digest replay mismatch"):
        validate(fixture)


def test_extra_sealed_mirror_sibling_file_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    operation_model = json.loads(fixture.operation_model.read_text(encoding="ascii"))
    mirror_manifest = fixture.report.joinpath(
        *PurePosixPath(
            operation_model["authority_bindings"]["sealed_authentication_mirror"]["path"]
        ).parts
    )
    mirror_root = mirror_manifest.parent
    mirror_root.chmod(0o755)
    write_source(mirror_root / "undeclared_sibling.json", "{}\n")
    mirror_root.chmod(0o555)
    with pytest.raises(validator.ProtocolFailure, match="missing or extra filesystem entries"):
        validate(fixture)


@pytest.mark.parametrize(
    "aliased_import",
    [
        "from builtins import __import__ as load",
        "from importlib import import_module as load",
    ],
)
def test_dynamic_import_alias_is_rejected_after_reseal(tmp_path: Path, aliased_import: str) -> None:
    fixture = create_fixture(tmp_path)
    role8 = fixture.runtime_document["roles"][0]
    producer = Path(role8["code_inputs"]["producer"]["path"])
    original = producer.read_text(encoding="utf-8")
    producer.chmod(0o644)
    write_source(producer, f"{aliased_import}\n{original}")
    role8["code_inputs"]["producer"] = pin(producer)
    reseal_runtime(fixture)
    with pytest.raises(
        validator.ProtocolFailure, match="from-import forbidden|dynamic execution/import"
    ):
        validate(fixture)


def test_non_null_allowed_shared_protocol_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    shared_protocol = fixture.report / "code/round180_semantics_free_protocol.py"
    write_source(shared_protocol, 'SCHEMA = "synthetic_protocol"\n')
    fixture.runtime_document["roles"][0]["allowed_shared_protocol"] = pin(shared_protocol)
    reseal_runtime(fixture)
    with pytest.raises(
        validator.ProtocolFailure, match="non-null allowed_shared_protocol is unsupported"
    ):
        validate(fixture)


def test_absent_output_descendant_of_sealed_mirror_root_is_rejected(
    tmp_path: Path,
) -> None:
    fixture = create_fixture(tmp_path)
    operation_model = json.loads(fixture.operation_model.read_text(encoding="ascii"))
    mirror_manifest = fixture.report.joinpath(
        *PurePosixPath(
            operation_model["authority_bindings"]["sealed_authentication_mirror"]["path"]
        ).parts
    )
    future_output = mirror_manifest.parent / "future_role8_artifact.json"
    assert not future_output.exists()
    fixture.slot_paths["role8_artifact"] = future_output
    for slot in fixture.plan_document["slots"]:
        if slot["slot_id"] == "role8_artifact":
            slot["path"] = str(future_output)
            break
    role8_runtime = fixture.runtime_document["roles"][0]
    role8_entry = fixture.plan_document["entries"][0]
    role8_entry["invocations"] = _role_invocations(
        8,
        Path(role8_runtime["python_executable"]["path"]),
        Path(role8_runtime["code_inputs"]["producer"]["path"]),
        Path(role8_runtime["code_inputs"]["verifier"]["path"]),
        fixture.slot_paths,
    )
    role8_entry["precommit_projection_sha256"] = entry_digest(role8_entry)
    reseal_plan(fixture)
    with pytest.raises(
        validator.ProtocolFailure,
        match="planned output has ancestor/descendant conflict with protocol input",
    ):
        validate(fixture)


def test_runner_transitive_helper_importing_gmpy2_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    runner = fixture.runtime_document["global_runner"]
    runner_code = Path(runner["code_input"]["path"])
    helper = fixture.report / "code/round180_runner_numerical_helper.py"
    write_source(helper, "import gmpy2\nTOKEN = gmpy2.__name__\n")
    original = runner_code.read_text(encoding="utf-8")
    runner_code.chmod(0o644)
    write_source(
        runner_code,
        f"import round180_runner_numerical_helper\n{original}"
        "HELPER = round180_runner_numerical_helper.__name__\n",
    )
    gmpy2_library = fixture.runtime_document["roles"][0]["native_libraries"][0]
    runner["code_input"] = pin(runner_code)
    runner["python_imports"] = [
        "builtins",
        "gmpy2",
        "round180_runner_numerical_helper",
    ]
    runner["report_local_dependencies"] = [pin(helper)]
    runner["resolved_python_dependencies"] = [
        *_resolved_builtin(),
        {
            "import_name": "gmpy2",
            "origin_kind": "numerical_native_extension",
            "path": gmpy2_library["path"],
            "sha256": gmpy2_library["sha256"],
        },
        {
            "import_name": "round180_runner_numerical_helper",
            "origin_kind": "file_report_local",
            "path": str(helper),
            "sha256": sha256_file(helper),
        },
    ]
    reseal_runtime(fixture)
    with pytest.raises(
        validator.ProtocolFailure,
        match="global replay runner transitive closure imports numerical code",
    ):
        validate(fixture)


def test_cross_role_producer_verifier_byte_overlap_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    role8_producer = Path(fixture.runtime_document["roles"][0]["code_inputs"]["producer"]["path"])
    role9_verifier = Path(fixture.runtime_document["roles"][1]["code_inputs"]["verifier"]["path"])
    role9_verifier.chmod(0o644)
    role9_verifier.write_bytes(role8_producer.read_bytes())
    role9_verifier.chmod(0o444)
    fixture.runtime_document["roles"][1]["code_inputs"]["verifier"] = pin(role9_verifier)
    reseal_runtime(fixture)
    with pytest.raises(validator.ProtocolFailure, match="source byte overlap"):
        validate(fixture)


def test_unreferenced_report_dependency_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    dependency = fixture.report / "code/unreferenced_helper.py"
    write_source(dependency, "UNREFERENCED = True\n")
    role8 = fixture.runtime_document["roles"][0]
    role8["report_local_dependencies"]["producer"] = [pin(dependency)]
    reseal_runtime(fixture)
    with pytest.raises(validator.ProtocolFailure, match="reachable report-local import closure"):
        validate(fixture)


def test_unreachable_report_local_import_cycle_is_rejected(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    dependency_a = fixture.report / "code/round180_cycle_a.py"
    dependency_b = fixture.report / "code/round180_cycle_b.py"
    write_source(dependency_a, "import round180_cycle_b\nA = round180_cycle_b.__name__\n")
    write_source(dependency_b, "import round180_cycle_a\nB = round180_cycle_a.__name__\n")
    role8 = fixture.runtime_document["roles"][0]
    role8["python_imports"]["producer"] = [
        "builtins",
        "round180_cycle_a",
        "round180_cycle_b",
    ]
    role8["report_local_dependencies"]["producer"] = sorted(
        [pin(dependency_a), pin(dependency_b)], key=lambda value: value["path"]
    )
    role8["resolved_python_dependencies"]["producer"] = [
        *_resolved_builtin(),
        {
            "import_name": "round180_cycle_a",
            "origin_kind": "file_report_local",
            "path": str(dependency_a),
            "sha256": sha256_file(dependency_a),
        },
        {
            "import_name": "round180_cycle_b",
            "origin_kind": "file_report_local",
            "path": str(dependency_b),
            "sha256": sha256_file(dependency_b),
        },
    ]
    reseal_runtime(fixture)
    with pytest.raises(validator.ProtocolFailure, match="unreachable resolved dependency"):
        validate(fixture)


def test_reachable_report_local_import_cycle_is_accepted(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    producer = Path(fixture.runtime_document["roles"][0]["code_inputs"]["producer"]["path"])
    dependency_a = fixture.report / "code/round180_reachable_cycle_a.py"
    dependency_b = fixture.report / "code/round180_reachable_cycle_b.py"
    write_source(
        dependency_a,
        "import round180_reachable_cycle_b\nA = round180_reachable_cycle_b.__name__\n",
    )
    write_source(
        dependency_b,
        "import round180_reachable_cycle_a\nB = round180_reachable_cycle_a.__name__\n",
    )
    producer.chmod(0o644)
    write_source(
        producer,
        "import builtins\n"
        "import round180_reachable_cycle_a\n"
        "ROLE_ID = 8\n"
        "SIDE = 'producer'\n"
        "TOKEN = (builtins.__name__, round180_reachable_cycle_a.__name__)\n",
    )
    role8 = fixture.runtime_document["roles"][0]
    role8["code_inputs"]["producer"] = pin(producer)
    role8["python_imports"]["producer"] = [
        "builtins",
        "round180_reachable_cycle_a",
        "round180_reachable_cycle_b",
    ]
    role8["report_local_dependencies"]["producer"] = sorted(
        [pin(dependency_a), pin(dependency_b)], key=lambda value: value["path"]
    )
    role8["resolved_python_dependencies"]["producer"] = [
        *_resolved_builtin(),
        {
            "import_name": "round180_reachable_cycle_a",
            "origin_kind": "file_report_local",
            "path": str(dependency_a),
            "sha256": sha256_file(dependency_a),
        },
        {
            "import_name": "round180_reachable_cycle_b",
            "origin_kind": "file_report_local",
            "path": str(dependency_b),
            "sha256": sha256_file(dependency_b),
        },
    ]
    reseal_runtime(fixture)
    ack = validate(fixture)
    assert ack["status"] == validator.PASS_STATUS


@pytest.mark.parametrize(
    ("location", "mutation"),
    [
        ("field", "observed_result"),
        ("value", "result_summary"),
    ],
)
def test_forbidden_result_field_or_value_is_rejected(
    tmp_path: Path, location: str, mutation: str
) -> None:
    fixture = create_fixture(tmp_path)
    entry = fixture.plan_document["entries"][0]
    if location == "field":
        entry[mutation] = None
    else:
        entry["invocations"]["producer"]["invocation_id"] = mutation
    entry["precommit_projection_sha256"] = entry_digest(entry)
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="forbidden (precommit field|result token)"):
        validate(fixture)


def test_role10_dual_public_invocation_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    role10 = fixture.plan_document["entries"][2]
    role10["invocations"]["producer"] = dict(role10["invocations"]["transaction_orchestrator"])
    role10["precommit_projection_sha256"] = entry_digest(role10)
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="role 10 invocation mismatch"):
        validate(fixture)


def test_role10_method_order_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    role10 = fixture.plan_document["entries"][2]
    role10["method_selection"][0], role10["method_selection"][1] = (
        role10["method_selection"][1],
        role10["method_selection"][0],
    )
    role10["precommit_projection_sha256"] = entry_digest(role10)
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="role 10 method selection mismatch"):
        validate(fixture)


def test_role10_entry_order_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    fixture.plan_document["entries"][1], fixture.plan_document["entries"][2] = (
        fixture.plan_document["entries"][2],
        fixture.plan_document["entries"][1],
    )
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="role 9 entry identity"):
        validate(fixture)


def test_partition_binding_mutation_is_rejected_after_reseal(tmp_path: Path) -> None:
    fixture = create_fixture(tmp_path)
    role10 = fixture.plan_document["entries"][2]
    role10["partition_path_bindings"] = json.loads(json.dumps(role10["partition_path_bindings"]))
    role10["partition_path_bindings"][0]["coordinate"] = "relative_parallel"
    role10["precommit_projection_sha256"] = entry_digest(role10)
    reseal_plan(fixture)
    with pytest.raises(validator.ProtocolFailure, match="role 10 partition bindings mismatch"):
        validate(fixture)


@pytest.mark.parametrize(
    "slot_id",
    [template["slot_id"] for template in protocol.SLOT_TEMPLATES],
)
def test_preexisting_request_or_output_is_rejected(tmp_path: Path, slot_id: str) -> None:
    fixture = create_fixture(tmp_path)
    path = fixture.slot_paths[slot_id]
    path.write_text("foreign\n", encoding="ascii")
    path.chmod(0o444)
    with pytest.raises(validator.ProtocolFailure, match="already materialized|not absent"):
        validate(fixture)
