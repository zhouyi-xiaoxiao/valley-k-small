#!/usr/bin/env python3
"""Standalone adversarial suite for the neutral C1 symbolic-bridge fixture.

Source, outer-manifest, and operation-model mutations are exercised in a
minimal report clone below ``REPORT/tmp``.  Every lower-layer mutation is
rehash-propagated through its honest ancestors before both producer and
independent validator are invoked.  This distinguishes semantic rejection
from an accidental stale-hash rejection.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]

BUILDER_RELATIVE = Path("code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py")
VALIDATOR_RELATIVE = Path("code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py")
OPERATION_RELATIVE = Path("code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json")
DESIGN_RELATIVE = Path("notes/continuum_c1_production_gauge_killing_bridge_design_v1.md")
SOURCE_RELATIVE = Path("artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json")
MANIFEST_RELATIVE = Path(
    "artifacts/data/continuum_c1_symbolic_bridge_neutral_outer_manifest_v1.json"
)
ARTIFACT_RELATIVE = Path("artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json")

NATIVE_DOMAIN = b"encounter-source-native-record-v1\x00"
NEUTRAL_OUTPUT_BASENAME = ARTIFACT_RELATIVE.name
FORMAL_OUTPUT_BASENAMES = (
    "continuum_c1_gauge_killing_symbolic_candidate_v1.json",
    "continuum_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
)


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _compact_jcs_subset(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise AssertionError(f"top-level JSON object required: {path}")
    return value


def _write(path: Path, value: Any) -> None:
    path.write_bytes(_canonical(value))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _path(stage: Path, relative: Path) -> Path:
    return stage / relative


def _copy_minimal_stage(parent: Path, label: str) -> Path:
    stage = parent / label
    stage.mkdir()
    for relative in (
        BUILDER_RELATIVE,
        VALIDATOR_RELATIVE,
        OPERATION_RELATIVE,
        DESIGN_RELATIVE,
        SOURCE_RELATIVE,
        MANIFEST_RELATIVE,
        ARTIFACT_RELATIVE,
    ):
        source = REPORT / relative
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    (stage / "tmp").mkdir()
    return stage


def _refresh_manifest_source_hash(stage: Path) -> None:
    manifest_path = _path(stage, MANIFEST_RELATIVE)
    manifest = _load(manifest_path)
    payloads = manifest["payload_sources"]
    if type(payloads) is not list or len(payloads) != 1:
        raise AssertionError("baseline manifest must contain one payload")
    payloads[0]["sha256"] = _sha(_path(stage, SOURCE_RELATIVE))
    _write(manifest_path, manifest)


def _refresh_operation_ancestor_hashes(stage: Path) -> str:
    operation_path = _path(stage, OPERATION_RELATIVE)
    operation = _load(operation_path)
    for binding in operation["bootstrap_sources"]:
        binding["sha256"] = _sha(_path(stage, Path(binding["path"])))
    operation["outer_manifest_source"]["sha256"] = _sha(
        _path(stage, MANIFEST_RELATIVE)
    )
    _write(operation_path, operation)
    return _sha(operation_path)


def _native_record_key(source_role: str, record: dict[str, Any]) -> list[str]:
    return [
        source_role,
        record["member_spec_manifest_sha256"],
        record["partition_sha256"],
        record["refinement_family_id"],
        record["refinement_member_id"],
        record["configuration_id"],
        record["axis_or_factor_role"],
        record["cell_or_edge_id"],
        record["ideal_quantity_id"],
    ]


def _refresh_artifact_provenance(stage: Path) -> None:
    """Keep a staged artifact current enough that input semantics fail first."""

    artifact_path = _path(stage, ARTIFACT_RELATIVE)
    artifact = _load(artifact_path)
    operation = _load(_path(stage, OPERATION_RELATIVE))
    manifest = _load(_path(stage, MANIFEST_RELATIVE))
    operation_sha = _sha(_path(stage, OPERATION_RELATIVE))
    manifest_sha = _sha(_path(stage, MANIFEST_RELATIVE))
    source_sha = _sha(_path(stage, SOURCE_RELATIVE))

    bindings = artifact["source_bindings"]
    bindings["bootstrap_sources"] = copy.deepcopy(operation["bootstrap_sources"])
    bindings["operation_model_source"] = {
        "path": OPERATION_RELATIVE.as_posix(),
        "schema": operation["schema"],
        "sha256": operation_sha,
    }
    bindings["outer_manifest_source"] = {
        "path": operation["outer_manifest_source"]["path"],
        "schema": manifest["schema"],
        "sha256": manifest_sha,
    }
    bindings["payload_sources"] = copy.deepcopy(manifest["payload_sources"])

    payloads = manifest.get("payload_sources")
    source = _load(_path(stage, SOURCE_RELATIVE))
    records = source.get("native_interval_records")
    receipts = artifact.get("native_record_receipts")
    if (
        type(payloads) is list
        and len(payloads) == 1
        and type(payloads[0]) is dict
        and type(records) is list
        and records
        and type(records[0]) is dict
        and type(receipts) is list
        and receipts
        and type(receipts[0]) is dict
    ):
        record = records[0]
        role = payloads[0].get("role", "neutral_symbolic_witness_source")
        receipt = receipts[0]
        receipt["source_path"] = payloads[0].get("path", SOURCE_RELATIVE.as_posix())
        receipt["source_role"] = role
        receipt["source_sha256"] = source_sha
        if all(
            key in record
            for key in (
                "member_spec_manifest_sha256",
                "partition_sha256",
                "refinement_family_id",
                "refinement_member_id",
                "configuration_id",
                "axis_or_factor_role",
                "cell_or_edge_id",
                "ideal_quantity_id",
                "schema",
            )
        ):
            receipt["source_native_record_key"] = _native_record_key(role, record)
            receipt["source_native_record_schema"] = record["schema"]
            receipt["source_native_record_sha256"] = hashlib.sha256(
                NATIVE_DOMAIN + _compact_jcs_subset(record)
            ).hexdigest()
    _write(artifact_path, artifact)


def _refresh_stage(stage: Path) -> str:
    _refresh_manifest_source_hash(stage)
    operation_sha = _refresh_operation_ancestor_hashes(stage)
    _refresh_artifact_provenance(stage)
    return operation_sha


def _run(
    stage: Path,
    program_relative: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(_path(stage, program_relative)), *arguments],
        cwd=stage,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
        check=False,
    )


def _builder(
    stage: Path,
    expected_operation_sha256: str,
    *,
    output: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    if output is None:
        output = stage / "tmp" / NEUTRAL_OUTPUT_BASENAME
    arguments = [
        "--operation-model",
        str(_path(stage, OPERATION_RELATIVE)),
        "--expected-operation-model-sha256",
        expected_operation_sha256,
        "--output",
        str(output),
    ]
    if check:
        arguments.append("--check")
    return _run(stage, BUILDER_RELATIVE, *arguments)


def _validator(
    stage: Path,
    expected_operation_sha256: str,
    *,
    artifact: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if artifact is None:
        artifact = _path(stage, ARTIFACT_RELATIVE)
    return _run(
        stage,
        VALIDATOR_RELATIVE,
        "--operation-model",
        str(_path(stage, OPERATION_RELATIVE)),
        "--expected-operation-model-sha256",
        expected_operation_sha256,
        "--artifact",
        str(artifact),
    )


def _require_rejected(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        raise AssertionError(f"mutation unexpectedly accepted: {label}\n{result.stdout}")


def _require_both_rejected(
    stage: Path,
    label: str,
    *,
    expected_operation_sha256: str | None = None,
) -> None:
    observed = _sha(_path(stage, OPERATION_RELATIVE))
    expected = observed if expected_operation_sha256 is None else expected_operation_sha256
    producer = _builder(stage, expected)
    verifier = _validator(stage, expected)
    _require_rejected(producer, f"builder_{label}")
    _require_rejected(verifier, f"validator_{label}")


def _artifact_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        (
            "artifact_global_gauge_identity",
            lambda value: value["exact_identity_results"]["global_gauge"].__setitem__(
                "G_exact", "1/3"
            ),
        ),
        (
            "artifact_common_flux_identity",
            lambda value: value["exact_identity_results"][
                "common_flux_and_tensor_conductance"
            ].__setitem__("common_flux_exact", "7/5"),
        ),
        (
            "artifact_reconstruction_identity",
            lambda value: value["exact_identity_results"]["reconstruction"].__setitem__(
                "K_exact", "2/3"
            ),
        ),
        (
            "artifact_interval_division_identity",
            lambda value: value["exact_identity_results"]["interval_division"].__setitem__(
                "rho_interval", ["1/1", "2/1"]
            ),
        ),
        (
            "artifact_formal_candidate_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "formal_symbolic_candidate_materialized", True
            ),
        ),
        (
            "artifact_acceptance_receipt_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "symbolic_acceptance_receipt_materialized", True
            ),
        ),
        (
            "artifact_false_bool_int_alias",
            lambda value: value["claim_boundary"].__setitem__("complete_C1", 0),
        ),
        (
            "artifact_true_bool_int_alias",
            lambda value: value["contract_scope"].__setitem__(
                "neutral_contract_fixture_pass", 1
            ),
        ),
        (
            "artifact_counter_float_alias",
            lambda value: value["open_ledger"].__setitem__(
                "maximum_report_file_opens", 6.0
            ),
        ),
        (
            "artifact_explicit_counter_drift",
            lambda value: value["open_ledger"][
                "explicit_construction_snapshot_counter"
            ].__setitem__(next(iter(value["open_ledger"]["explicit_construction_snapshot_counter"])), 2),
        ),
        (
            "artifact_false_full_process_closure_promotion",
            lambda value: value["open_ledger"].__setitem__(
                "complete_process_report_file_open_closure", True
            ),
        ),
        (
            "artifact_native_record_digest",
            lambda value: value["native_record_receipts"][0].__setitem__(
                "source_native_record_sha256", "0" * 64
            ),
        ),
        (
            "artifact_native_record_key",
            lambda value: value["native_record_receipts"][0][
                "source_native_record_key"
            ].__setitem__(5, "wrong_configuration"),
        ),
        (
            "artifact_source_binding",
            lambda value: value["source_bindings"]["payload_sources"][0].__setitem__(
                "sha256", "f" * 64
            ),
        ),
    ]


def _source_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        (
            "source_wrong_gauge",
            lambda value: value["rational_sanity_witnesses"]["global_gauge"].__setitem__(
                "expected_G", "1/3"
            ),
        ),
        (
            "source_wrong_flux",
            lambda value: value["rational_sanity_witnesses"]["common_flux"].__setitem__(
                "expected_reverse_flux", "7/5"
            ),
        ),
        (
            "source_wrong_K",
            lambda value: value["rational_sanity_witnesses"]["reconstruction"].__setitem__(
                "expected_K", "2/3"
            ),
        ),
        (
            "source_wrong_interval",
            lambda value: value["rational_sanity_witnesses"]["interval_division"].__setitem__(
                "expected_rho_interval", ["1/1", "2/1"]
            ),
        ),
        (
            "source_descriptor_hash",
            lambda value: value["native_interval_records"][0].__setitem__(
                "configuration_geometry_sha256", "0" * 64
            ),
        ),
        (
            "source_duplicate_native_record",
            lambda value: value["native_interval_records"].append(
                copy.deepcopy(value["native_interval_records"][0])
            ),
        ),
        (
            "source_non_nfc",
            lambda value: value["native_interval_records"][0].__setitem__(
                "unit", "e\u0301"
            ),
        ),
        (
            "source_noncanonical_rational",
            lambda value: value["rational_sanity_witnesses"]["global_gauge"].__setitem__(
                "M_L", "2/4"
            ),
        ),
        (
            "source_float",
            lambda value: value["neutral_descriptors"]["configuration_geometry"][
                "shape"
            ].__setitem__(0, 1.0),
        ),
        (
            "source_claim_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "symbolic_bridge_accepted", True
            ),
        ),
        (
            "source_embedded_self_path",
            lambda value: value["native_interval_records"][0].__setitem__(
                "unit", SOURCE_RELATIVE.as_posix()
            ),
        ),
        (
            "source_embedded_prior_self_hash",
            lambda value: value["native_interval_records"][0].__setitem__(
                "unit", _sha(REPORT / SOURCE_RELATIVE)
            ),
        ),
    ]


def _manifest_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        (
            "manifest_self_authorize",
            lambda value: value["payload_sources"][0].__setitem__(
                "path", MANIFEST_RELATIVE.as_posix()
            ),
        ),
        (
            "manifest_control_role",
            lambda value: value["forbidden_selected_roles"]["control_value_sources"].append(
                "forbidden_control_source"
            ),
        ),
        (
            "manifest_budget_role",
            lambda value: value["forbidden_selected_roles"]["budget_value_sources"].append(
                "forbidden_budget_source"
            ),
        ),
        (
            "manifest_result_role",
            lambda value: value["forbidden_selected_roles"]["result_or_scratch_sources"].append(
                "forbidden_result_source"
            ),
        ),
        (
            "manifest_extra_payload",
            lambda value: value["payload_sources"].append(
                copy.deepcopy(value["payload_sources"][0])
            ),
        ),
        (
            "manifest_dag_edge",
            lambda value: value["source_dependency_dag"]["edges"].append(
                ["neutral_symbolic_witness_source", "neutral_symbolic_witness_source"]
            ),
        ),
        (
            "manifest_path_escape",
            lambda value: value["payload_sources"][0].__setitem__(
                "path", "../outside.json"
            ),
        ),
        (
            "manifest_payload_hash_drift",
            lambda value: value["payload_sources"][0].__setitem__("sha256", "0" * 64),
        ),
    ]


def _operation_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    def drift_bootstrap(role: str) -> Callable[[dict[str, Any]], None]:
        def mutate(value: dict[str, Any]) -> None:
            for binding in value["bootstrap_sources"]:
                if binding["role"] == role:
                    binding["sha256"] = "0" * 64
                    return
            raise AssertionError(f"missing bootstrap role: {role}")

        return mutate

    return [
        ("operation_builder_hash_drift", drift_bootstrap("builder_entry_source")),
        ("operation_verifier_hash_drift", drift_bootstrap("verifier_entry_source")),
        ("operation_design_hash_drift", drift_bootstrap("design_authority_source")),
        (
            "operation_manifest_hash_drift",
            lambda value: value["outer_manifest_source"].__setitem__("sha256", "0" * 64),
        ),
        (
            "operation_extra_dependency_closure",
            lambda value: value["verifier_dependency_closure"].append(
                "code/unexpected_helper.py"
            ),
        ),
        (
            "operation_claim_int_alias",
            lambda value: value["claim_boundary"].__setitem__(
                "symbolic_bridge_accepted", 0
            ),
        ),
        (
            "operation_cap_float_alias",
            lambda value: value["resource_caps"].__setitem__(
                "maximum_report_file_opens", 6.0
            ),
        ),
        (
            "operation_snapshot_int_alias",
            lambda value: value["two_repeat_snapshot_policy"].__setitem__(
                "snapshot_before_parse", 1
            ),
        ),
    ]


def main() -> int:
    for relative in (
        BUILDER_RELATIVE,
        VALIDATOR_RELATIVE,
        OPERATION_RELATIVE,
        DESIGN_RELATIVE,
        SOURCE_RELATIVE,
        MANIFEST_RELATIVE,
        ARTIFACT_RELATIVE,
    ):
        if not (REPORT / relative).is_file():
            raise AssertionError(f"required neutral fixture file is absent: {relative}")

    temporary_parent = REPORT / "tmp"
    temporary_parent.mkdir(exist_ok=True)
    passes = 0
    with tempfile.TemporaryDirectory(
        prefix="continuum-c1-neutral-mutations-", dir=temporary_parent
    ) as directory:
        root = Path(directory)

        for label, mutate in _artifact_mutations():
            stage = _copy_minimal_stage(root, label)
            operation_sha = _refresh_stage(stage)
            artifact_path = _path(stage, ARTIFACT_RELATIVE)
            artifact = _load(artifact_path)
            mutate(artifact)
            _write(artifact_path, artifact)
            _require_rejected(_validator(stage, operation_sha), label)
            print(f"PASS reject_{label}")
            passes += 1

        for label, mutate in _source_mutations():
            stage = _copy_minimal_stage(root, label)
            source_path = _path(stage, SOURCE_RELATIVE)
            source = _load(source_path)
            mutate(source)
            _write(source_path, source)
            _refresh_manifest_source_hash(stage)
            _refresh_operation_ancestor_hashes(stage)
            _refresh_artifact_provenance(stage)
            _require_both_rejected(stage, label)
            print(f"PASS reject_{label}_by_builder_and_validator")
            passes += 1

        label = "source_duplicate_json_key"
        stage = _copy_minimal_stage(root, label)
        source_path = _path(stage, SOURCE_RELATIVE)
        raw = source_path.read_text(encoding="utf-8")
        source_path.write_text(
            raw.replace(
                '{\n  "claim_boundary"',
                '{\n  "schema": "duplicate",\n  "claim_boundary"',
                1,
            ),
            encoding="utf-8",
        )
        _refresh_manifest_source_hash(stage)
        _refresh_operation_ancestor_hashes(stage)
        # Do not parse the deliberately duplicate-key source while refreshing
        # the artifact; the validator must reject it before artifact semantics.
        _require_both_rejected(stage, label)
        print(f"PASS reject_{label}_by_builder_and_validator")
        passes += 1

        for label, mutate in _manifest_mutations():
            stage = _copy_minimal_stage(root, label)
            manifest_path = _path(stage, MANIFEST_RELATIVE)
            manifest = _load(manifest_path)
            mutate(manifest)
            _write(manifest_path, manifest)
            _refresh_operation_ancestor_hashes(stage)
            _refresh_artifact_provenance(stage)
            _require_both_rejected(stage, label)
            print(f"PASS reject_{label}_by_builder_and_validator")
            passes += 1

        label = "operation_external_hash_mismatch"
        stage = _copy_minimal_stage(root, label)
        operation_sha = _refresh_stage(stage)
        wrong_sha = "0" * 64 if operation_sha != "0" * 64 else "f" * 64
        _require_both_rejected(
            stage,
            label,
            expected_operation_sha256=wrong_sha,
        )
        print(f"PASS reject_{label}_by_builder_and_validator")
        passes += 1

        for label, mutate in _operation_mutations():
            stage = _copy_minimal_stage(root, label)
            _refresh_stage(stage)
            operation_path = _path(stage, OPERATION_RELATIVE)
            operation = _load(operation_path)
            mutate(operation)
            _write(operation_path, operation)
            _refresh_artifact_provenance(stage)
            _require_both_rejected(stage, label)
            print(f"PASS reject_{label}_by_builder_and_validator")
            passes += 1

        for basename in FORMAL_OUTPUT_BASENAMES:
            label = f"formal_output_basename_{Path(basename).stem}"
            stage = _copy_minimal_stage(root, label)
            operation_sha = _refresh_stage(stage)
            output = stage / "tmp" / basename
            result = _builder(
                stage,
                operation_sha,
                output=output,
                check=False,
            )
            _require_rejected(result, label)
            if output.exists():
                raise AssertionError(f"formal output basename was materialized: {output}")
            print(f"PASS reject_{label}")
            passes += 1

    print(f"{passes}/{passes} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
