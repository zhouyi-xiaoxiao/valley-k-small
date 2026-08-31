#!/usr/bin/env python3
"""Validate and publish the fail-closed terminal branch for this completion run."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
MANUSCRIPT = REPORT / "manuscript"
OUTPUT = REPORT / "output"

CONTRACT = DATA / "manuscript_completion_contract_v1.json"
SEMANTIC_RECEIPT = DATA / "rate_defined_tensor_f0_semantic_independent_v1.json"
RESOURCE_RECEIPT = (
    DATA / "rate_defined_tensor_f0_resource_independent_replay_v1.json"
)
FORMAL_RESOURCE = DATA / "rate_defined_tensor_f0_resource_v1.json"
FORMAL_SIDECAR = DATA / "rate_defined_tensor_f0_resource_v1.json.resources.json"
SCHEDULE = DATA / "rate_defined_tensor_f0_topology_schedule_v1.json"
CANDIDATE_A = DATA / "rate_defined_tensor_f0_candidate_v1_replica_a.json"
CANDIDATE_B = DATA / "rate_defined_tensor_f0_candidate_v1_replica_b.json"
COMPILE_MANIFEST = DATA / "theorem_first_submission_compile.json"
PACKAGE_MANIFEST = DATA / "theorem_first_submission_source_package.json"
MAIN_PDF = OUTPUT / "pdf" / "encounter_multimodal_prr_submission.pdf"
SUPPLEMENT_PDF = (
    OUTPUT / "pdf" / "encounter_multimodal_prr_submission_supplement.pdf"
)
SOURCE_ARCHIVE = (
    OUTPUT / "source" / "encounter_multimodal_prr_submission_source.tar.gz"
)
MAIN_TEX = MANUSCRIPT / "encounter_multimodal_prr_submission.tex"
SUPPLEMENT_TEX = MANUSCRIPT / "encounter_multimodal_prr_submission_supplement.tex"
SPINE_TEX = MANUSCRIPT / "exact_m_theorem_spine.tex"
FULL_PROOF_TEX = MANUSCRIPT / "exact_m_theorem_full_proof.tex"
REFERENCES_BIB = MANUSCRIPT / "references.bib"
OUTPUT_RECEIPT = DATA / "encounter_prr_terminal_branch_v1.json"

SCHEMA = "encounter_prr_terminal_branch_v1"
BRANCH = "HOLD_F0_METHOD_OR_RESOURCE"
FAILURE_CLASS = "METHOD_OR_RESOURCE"
FAILURE_REASONS = ("rss_cap_exceeded", "peak_footprint_cap_exceeded")
STAGE_STATUSES = {
    "f0": "HOLD_F0",
    "f1": "NOT_RUN",
    "f2": "NOT_RUN",
    "f3": "NOT_RUN",
}

EXPECTED_SHA256 = {
    "contract": "f32fee61edb48fad4e0da0ad5e747db8c417fd25c3acb18da74354c60ec68ee0",
    "semantic_receipt": "0ed41cf67c21a90c33103badef4bcad42d1f633c0b9a449a784e5f25ea7cf957",
    "resource_receipt": "8a332c7a4dd3c594709283403292cd26b77abd076f7cc137c05176cf1cf14758",
    "formal_resource": "0681015f350f9df702d32c4aaa712b89fce7aa742ebccb345a9336a5b64ad2b1",
    "formal_sidecar": "98ed3190c518614f5adf6a9d64933d847ab52bbf6cb4eb73c9635d4035a23061",
    "schedule": "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344",
    "candidate": "f3c294fbc6323845b530b986197ee43d3f0b3fb8a690aa9f5bb71e4f343889dd",
    "semantic_validator": "3d2d03f147c32540c2ee6245b38b815139f6794a3f01cb066ff07514eae2c3a1",
    "resource_validator": "60fafed54072c590bc478253c77d42cd04606b9efe3ad7a139d8b870776a0436",
    "spine": "79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e",
    "full_proof": "a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b",
}

SEMANTIC_VALIDATOR = REPORT / "code" / "rate_defined_tensor_f0_semantic_independent_v1.py"
RESOURCE_VALIDATOR = REPORT / "code" / "validate_rate_defined_tensor_f0_resource_v1.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read valid JSON object: {path}") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return payload


def _require_hash(path: Path, expected: str, *, label: str) -> str:
    observed = _sha256(path)
    if observed != expected:
        raise RuntimeError(f"{label} hash mismatch")
    return observed


def _require_false_flags(
    value: Any,
    required: tuple[str, ...],
    *,
    label: str,
) -> None:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{label} is not an object")
    for name in required:
        if value.get(name) is not False:
            raise RuntimeError(f"{label}.{name} is not fail-closed")


def _validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != "encounter_manuscript_completion_contract_v1":
        raise RuntimeError("completion contract schema mismatch")
    branches = contract.get("terminal_branches")
    if not isinstance(branches, Mapping):
        raise RuntimeError("completion contract terminal branches missing")
    selected = branches.get(BRANCH)
    if not isinstance(selected, Mapping):
        raise RuntimeError("selected terminal branch missing")
    if selected.get("required_failure_class") != FAILURE_CLASS:
        raise RuntimeError("selected branch failure class mismatch")
    if selected.get("required_statuses") != STAGE_STATUSES:
        raise RuntimeError("selected branch stage statuses mismatch")
    for key in ("f1_permitted", "f2_permitted", "f3_permitted"):
        if selected.get(key) is not False:
            raise RuntimeError(f"selected branch unexpectedly permits {key[:2]}")
    if selected.get("independent_validation_claim_permitted") is not False:
        raise RuntimeError("selected branch permits an independent validation claim")
    claim = contract.get("claim_ceiling")
    if not isinstance(claim, Mapping):
        raise RuntimeError("claim ceiling missing")
    if claim.get("theorem_claim") != (
        "accepted_exact_m_doi_theorem_at_frozen_hypotheses_and_sequential_limits"
    ):
        raise RuntimeError("theorem claim ceiling mismatch")
    if claim.get("strict_continuum_claimed") is not False:
        raise RuntimeError("strict continuum was unexpectedly elected")
    if claim.get("strict_continuum_gate") != (
        "CONDITIONAL_ONLY_IF_STRICT_NUMERICAL_CONTINUUM_CLAIMED"
    ):
        raise RuntimeError("strict continuum activation boundary mismatch")


def _validate_semantic_receipt(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema") != "rate_defined_tensor_f0_semantic_independent_receipt_v1":
        raise RuntimeError("semantic receipt schema mismatch")
    if receipt.get("status") != "PASS_F0_SEMANTIC_REPLAY_RESOURCE_HOLD_NOT_F0":
        raise RuntimeError("semantic receipt status mismatch")
    if receipt.get("terminal_branch_recommendation") != BRANCH:
        raise RuntimeError("semantic receipt recommends a different branch")
    if receipt.get("method_semantic_replay_pass") is not True:
        raise RuntimeError("semantic replay did not pass")
    _require_false_flags(
        receipt.get("authority_flags"),
        (
            "authorizes_f1",
            "authorizes_scientific_execution",
            "f0_accepted",
            "f0_pass",
            "independent_aggregation_complete",
            "production_resource_gate",
            "science_executed",
        ),
        label="semantic authority flags",
    )
    candidates = receipt.get("candidate_binding")
    if not isinstance(candidates, Mapping):
        raise RuntimeError("semantic candidate binding missing")
    if candidates.get("replicas_byte_identical") is not True:
        raise RuntimeError("semantic candidate replicas differ")
    if {
        candidates.get("replica_a_sha256"),
        candidates.get("replica_b_sha256"),
    } != {EXPECTED_SHA256["candidate"]}:
        raise RuntimeError("semantic candidate hashes mismatch")
    selector = receipt.get("selector_configuration_replay")
    if not isinstance(selector, Mapping):
        raise RuntimeError("semantic selector replay missing")
    rows = selector.get("fixed_36_row_order")
    if not isinstance(rows, list) or len(rows) != 36:
        raise RuntimeError("frozen F1 row ledger is not exactly 36 rows")
    expected_roles = ["lp_m1"] * 12 + ["lp_m2"] * 12 + ["lp_m3"] * 12
    if [row.get("control_role") for row in rows if isinstance(row, Mapping)] != (
        expected_roles
    ):
        raise RuntimeError("frozen F1 row ledger is not control-major")
    if selector.get("fixed_36_row_cross_product_sha256") != (
        "97cac6cc2202fa4fcd6737b1decdd56ea489904637c3cc3ec4bfea95ffa1fe70"
    ):
        raise RuntimeError("frozen F1 row ledger hash mismatch")


def _validate_resource_receipt(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema") != "rate_defined_tensor_f0_resource_independent_replay_v1":
        raise RuntimeError("resource replay schema mismatch")
    if receipt.get("status") != (
        "INDEPENDENTLY_CONFIRMED_HOLD_F0_METHOD_OR_RESOURCE"
    ):
        raise RuntimeError("resource replay status mismatch")
    if tuple(receipt.get("failure_reasons", ())) != FAILURE_REASONS:
        raise RuntimeError("resource replay failure reasons mismatch")
    _require_false_flags(
        receipt.get("promotion_flags"),
        (
            "authorizes_f1",
            "authorizes_scientific_execution",
            "f0_accepted",
            "f0_pass",
            "production_resource_gate",
            "resource_pass",
            "science_executed",
        ),
        label="resource replay promotion flags",
    )
    caps = receipt.get("frozen_caps")
    observed = receipt.get("observed_measurements")
    if not isinstance(caps, Mapping) or not isinstance(observed, Mapping):
        raise RuntimeError("resource caps or observations missing")
    if observed.get("peak_rss_bytes", 0) <= caps.get("maximum_rss_bytes", 0):
        raise RuntimeError("RSS resource failure is not substantiated")
    if observed.get("host_peak_footprint_bytes", 0) <= caps.get(
        "maximum_peak_footprint_bytes", 0
    ):
        raise RuntimeError("footprint resource failure is not substantiated")
    if observed.get("process_swap_delta") != 0:
        raise RuntimeError("resource replay swap observation changed")
    if float.fromhex(str(observed.get("wall_seconds_hex"))) > float(
        caps.get("maximum_wall_seconds", 0)
    ):
        raise RuntimeError("resource replay wall-time cap was unexpectedly exceeded")


def _validate_reader_artifacts(
    compile_manifest: Mapping[str, Any],
    package_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    claim = compile_manifest.get("claim_scope")
    expected_claim = {
        "finite_parameter_physical_evidence": False,
        "off_lattice_execution": False,
        "rigorous_numerical_continuum_convergence": False,
        "scientific_result": "exact_prescribed_finite_modality_doi_continuum_theorem",
    }
    if claim != expected_claim:
        raise RuntimeError("compiled claim scope exceeds the selected branch")
    if compile_manifest.get("reader_artifacts_ready") is not True:
        raise RuntimeError("reader artifacts are not compile-ready")
    outputs = compile_manifest.get("outputs")
    if not isinstance(outputs, Mapping):
        raise RuntimeError("compiled output ledger missing")
    actual = {
        "main": _sha256(MAIN_PDF),
        "supplement": _sha256(SUPPLEMENT_PDF),
    }
    for label in ("main", "supplement"):
        record = outputs.get(label)
        if not isinstance(record, Mapping) or record.get("sha256") != actual[label]:
            raise RuntimeError(f"compiled {label} PDF hash mismatch")
        if record.get("byte_identical_rebuilds") is not True:
            raise RuntimeError(f"compiled {label} PDF is not deterministic")
        if record.get("ghostscript_parse") is not True:
            raise RuntimeError(f"compiled {label} PDF failed parser audit")
        fonts = record.get("font_audit")
        if (
            not isinstance(fonts, Mapping)
            or fonts.get("all_fonts_embedded") is not True
            or fonts.get("type3_fonts") != 0
        ):
            raise RuntimeError(f"compiled {label} PDF font audit failed")
    archive = package_manifest.get("archive")
    validation = package_manifest.get("validation")
    if not isinstance(archive, Mapping) or not isinstance(validation, Mapping):
        raise RuntimeError("source package ledger missing")
    if archive.get("sha256") != _sha256(SOURCE_ARCHIVE):
        raise RuntimeError("source archive hash mismatch")
    if package_manifest.get("published_pdf_sha256") != actual:
        raise RuntimeError("source archive PDF ledger mismatch")
    expected_validation = {
        "archive_rebuilt_main_pdf_byte_identically": True,
        "archive_rebuilt_supplement_pdf_byte_identically": True,
        "deterministic_archive_rebuilds": True,
        "forbidden_reader_markers": 0,
        "safe_regular_members_only": True,
        "sha256_ledger_valid": True,
    }
    if validation != expected_validation:
        raise RuntimeError("source archive validation is incomplete")
    return {
        "main_pdf_sha256": actual["main"],
        "supplement_pdf_sha256": actual["supplement"],
        "source_archive_sha256": archive["sha256"],
        "reader_artifacts_ready": True,
        "source_archive_rebuilds_byte_identically": True,
    }


def build_receipt() -> dict[str, Any]:
    pinned_paths = {
        "contract": CONTRACT,
        "semantic_receipt": SEMANTIC_RECEIPT,
        "resource_receipt": RESOURCE_RECEIPT,
        "formal_resource": FORMAL_RESOURCE,
        "formal_sidecar": FORMAL_SIDECAR,
        "schedule": SCHEDULE,
        "semantic_validator": SEMANTIC_VALIDATOR,
        "resource_validator": RESOURCE_VALIDATOR,
        "spine": SPINE_TEX,
        "full_proof": FULL_PROOF_TEX,
    }
    pins = {
        label: _require_hash(path, EXPECTED_SHA256[label], label=label)
        for label, path in pinned_paths.items()
    }
    pins["candidate_a"] = _require_hash(
        CANDIDATE_A, EXPECTED_SHA256["candidate"], label="candidate A"
    )
    pins["candidate_b"] = _require_hash(
        CANDIDATE_B, EXPECTED_SHA256["candidate"], label="candidate B"
    )

    contract = _load_json(CONTRACT)
    semantic = _load_json(SEMANTIC_RECEIPT)
    resource = _load_json(RESOURCE_RECEIPT)
    compile_manifest = _load_json(COMPILE_MANIFEST)
    package_manifest = _load_json(PACKAGE_MANIFEST)
    _validate_contract(contract)
    _validate_semantic_receipt(semantic)
    _validate_resource_receipt(resource)
    reader = _validate_reader_artifacts(compile_manifest, package_manifest)

    observed = resource["observed_measurements"]
    caps = resource["frozen_caps"]
    return {
        "branch": BRANCH,
        "claim_ceiling": {
            "finite_parameter_physical_d2_numerical_evidence": False,
            "off_lattice_validation": False,
            "rigorous_numerical_continuum_convergence": False,
            "scientific_result": (
                "accepted_exact_m_doi_continuum_theorem_with_finite_window_scope"
            ),
            "strict_c0_c3_and_root_transfer": "CONDITIONAL_NOT_ELECTED",
        },
        "execution": {
            "failure_class": FAILURE_CLASS,
            "failure_reasons": list(FAILURE_REASONS),
            "f1_refit_attempted": False,
            "formal_f1_rows_executed": 0,
            "formal_f2_executed": False,
            "formal_f3_off_lattice_executed": False,
            "science_execution_authorized": False,
            "stage_statuses": dict(STAGE_STATUSES),
        },
        "f0": {
            "candidate_replicas_byte_identical": True,
            "method_semantic_replay_pass": True,
            "resource_caps_satisfied": False,
            "resource_measurement": {
                "host_peak_footprint_bytes": observed[
                    "host_peak_footprint_bytes"
                ],
                "maximum_peak_footprint_bytes": caps[
                    "maximum_peak_footprint_bytes"
                ],
                "peak_rss_bytes": observed["peak_rss_bytes"],
                "maximum_rss_bytes": caps["maximum_rss_bytes"],
                "process_swap_delta": observed["process_swap_delta"],
                "wall_seconds_hex": observed["wall_seconds_hex"],
                "maximum_wall_seconds": caps["maximum_wall_seconds"],
            },
            "semantic_status": semantic["status"],
            "resource_status": resource["status"],
        },
        "input_sha256": {
            **pins,
            "compile_manifest": _sha256(COMPILE_MANIFEST),
            "package_manifest": _sha256(PACKAGE_MANIFEST),
            "main_tex": _sha256(MAIN_TEX),
            "supplement_tex": _sha256(SUPPLEMENT_TEX),
            "references_bib": _sha256(REFERENCES_BIB),
        },
        "reader_outputs": reader,
        "schema": SCHEMA,
        "terminal": True,
    }


def _publish(payload: Mapping[str, Any]) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUTPUT_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=OUTPUT_RECEIPT.parent,
        prefix=f".{OUTPUT_RECEIPT.name}.",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, OUTPUT_RECEIPT)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    payload = build_receipt()
    _publish(payload)
    print(
        "Published terminal branch receipt: "
        f"{payload['branch']} {_sha256(OUTPUT_RECEIPT)}"
    )


if __name__ == "__main__":
    main()
