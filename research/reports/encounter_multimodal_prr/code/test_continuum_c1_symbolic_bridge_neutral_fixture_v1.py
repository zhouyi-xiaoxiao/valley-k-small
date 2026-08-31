#!/usr/bin/env python3
"""Standalone static/two-build tests for the neutral symbolic-bridge fixture.

The test deliberately exercises the builder and independent validator through
isolated subprocesses.  Temporary artifacts live below ``REPORT/tmp`` and are
removed after the test run.  The builder's ``--check`` mode is input-only: the
sentinel output path must remain absent and stdout must say
``OUTPUT_NOT_OPENED``.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_ARTIFACT_SHA256 = "2aa8facd4f820ae4d28af9eadb4acf095e64f68d3742c4816d9f02337413ebee"

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py"
OPERATION_MODEL = REPORT / "code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json"
CANONICAL_ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json"
)
NEUTRAL_SOURCE = REPORT / "artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json"

OUTPUT_SCHEMA = "encounter_continuum_c1_symbolic_bridge_neutral_fixture_v1"
OUTPUT_STATUS = (
    "PASS_NEUTRAL_SYMBOLIC_CONTRACT_FIXTURE_ONLY_"
    "PRODUCTION_CANDIDATE_NOT_MATERIALIZED"
)
FORMAL_PRODUCTION_SCHEMA = "encounter_c1_gauge_killing_symbolic_candidate_v1"
NATIVE_DOMAIN = b"encounter-source-native-record-v1\x00"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CHECK_RE = re.compile(
    r"^PASS_INPUTS_EXPECTED_FIXTURE_SHA ([0-9a-f]{64}) OUTPUT_NOT_OPENED\n$"
)

EXPECTED_TRUE_PATHS = {
    "contract_scope.acceptance_receipt_deferred",
    "contract_scope.error_ledger.E_space_E_eval_double_count_forbidden",
    "contract_scope.external_operation_model_trust_anchor_verified",
    "contract_scope.neutral_contract_fixture_pass",
    "contract_scope.outer_manifest_is_neutral_only",
    "exact_identity_results.all_four_neutral_witnesses_exact_pass",
    "exact_identity_results.common_flux_and_tensor_conductance.forward_reverse_exactly_equal",
    "exact_identity_results.common_flux_and_tensor_conductance.neutral_witness_exact_pass",
    "exact_identity_results.global_gauge.neutral_witness_exact_pass",
    "exact_identity_results.interval_division.denominator_lower_strictly_positive",
    "exact_identity_results.interval_division.neutral_witness_exact_pass",
    "exact_identity_results.reconstruction.K_path_endpoints_exactly_equal",
    "exact_identity_results.reconstruction.neutral_witness_exact_pass",
    "member_semantics.neutral_algebra_witnesses_do_not_construct_a_model",
    "open_ledger.bootstrap_payload_sets_disjoint",
    "open_ledger.explicit_snapshot_counter_union_exact",
}


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def _walk_strict(value: Any) -> None:
    if value is None or type(value) in {bool, int}:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        return
    if type(value) is list:
        for item in value:
            _walk_strict(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise ValueError("invalid JSON object key")
            _walk_strict(item)
        return
    raise ValueError(f"forbidden JSON value type: {type(value).__name__}")


def _canonical_bytes(value: Any) -> bytes:
    _walk_strict(value)
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode("ascii")


def _load_canonical(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicates)
    if type(value) is not dict:
        raise ValueError(f"top-level object required: {path}")
    if raw != _canonical_bytes(value):
        raise ValueError(f"noncanonical JSON: {path}")
    return raw, value


def _jcs_subset(value: Any) -> bytes:
    _walk_strict(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _true_paths(value: Any, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if type(value) is dict:
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            found.update(_true_paths(item, path))
    elif type(value) is list:
        for index, item in enumerate(value):
            found.update(_true_paths(item, f"{prefix}[{index}]"))
    elif type(value) is bool and value:
        found.add(prefix)
    return found


def _run(program: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(program), *arguments],
        cwd=REPORT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


class NeutralSymbolicBridgeFixtureV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for required in (
            BUILDER,
            VALIDATOR,
            OPERATION_MODEL,
            CANONICAL_ARTIFACT,
            NEUTRAL_SOURCE,
        ):
            if not required.is_file():
                raise AssertionError(f"required fixture input is absent: {required}")
        if not SHA256_RE.fullmatch(EXPECTED_ARTIFACT_SHA256):
            raise AssertionError("EXPECTED_ARTIFACT_SHA256 must be finalized")

        cls.canonical_raw, cls.artifact = _load_canonical(CANONICAL_ARTIFACT)
        cls.canonical_sha = hashlib.sha256(cls.canonical_raw).hexdigest()
        if cls.canonical_sha != EXPECTED_ARTIFACT_SHA256:
            raise AssertionError("canonical artifact digest drifted")

        temporary_parent = REPORT / "tmp"
        temporary_parent.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="continuum-c1-neutral-fixture-test-", dir=temporary_parent
        )
        root = Path(cls.temporary.name)
        operation_sha = hashlib.sha256(OPERATION_MODEL.read_bytes()).hexdigest()
        output_basename = "continuum_c1_symbolic_bridge_neutral_fixture_v1.json"
        first_directory = root / "build-one"
        second_directory = root / "build-two"
        check_directory = root / "check"
        for directory in (first_directory, second_directory, check_directory):
            directory.mkdir()
        cls.output_one = first_directory / output_basename
        cls.output_two = second_directory / output_basename
        check_sentinel = check_directory / output_basename

        checked = _run(
            BUILDER,
            "--operation-model",
            str(OPERATION_MODEL),
            "--expected-operation-model-sha256",
            operation_sha,
            "--output",
            str(check_sentinel),
            "--check",
        )
        if checked.returncode != 0 or checked.stderr:
            raise AssertionError(f"builder --check failed: {checked.stderr}")
        match = CHECK_RE.fullmatch(checked.stdout)
        if match is None or match.group(1) != EXPECTED_ARTIFACT_SHA256:
            raise AssertionError(f"wrong input-only --check acknowledgement: {checked.stdout!r}")
        if check_sentinel.exists():
            raise AssertionError("--check materialized or touched its output target")

        for output in (cls.output_one, cls.output_two):
            built = _run(
                BUILDER,
                "--operation-model",
                str(OPERATION_MODEL),
                "--expected-operation-model-sha256",
                operation_sha,
                "--output",
                str(output),
            )
            if built.returncode != 0 or built.stderr or "OUTPUT_NOT_REOPENED" not in built.stdout:
                raise AssertionError(f"one-shot builder failed: {built.stdout!r} {built.stderr!r}")
        cls.built_one = cls.output_one.read_bytes()
        cls.built_two = cls.output_two.read_bytes()
        if cls.built_one != cls.built_two or cls.built_one != cls.canonical_raw:
            raise AssertionError("two builds and canonical artifact are not byte-identical")

        before = cls.output_one.read_bytes()
        duplicate = _run(
            BUILDER,
            "--operation-model",
            str(OPERATION_MODEL),
            "--expected-operation-model-sha256",
            operation_sha,
            "--output",
            str(cls.output_one),
        )
        if duplicate.returncode == 0 or cls.output_one.read_bytes() != before:
            raise AssertionError("builder failed to reject an existing output atomically")

        for output in (cls.output_one, cls.output_two):
            verified = _run(
                VALIDATOR,
                "--operation-model",
                str(OPERATION_MODEL),
                "--expected-operation-model-sha256",
                operation_sha,
                "--artifact",
                str(output),
            )
            if verified.returncode != 0 or verified.stderr:
                raise AssertionError(f"independent validator failed: {verified.stderr}")
            if not verified.stdout.startswith("PASS "):
                raise AssertionError(f"validator acknowledgement is not PASS: {verified.stdout!r}")
            try:
                receipt = json.loads(
                    verified.stdout[len("PASS ") :],
                    object_pairs_hook=_reject_duplicates,
                )
            except (json.JSONDecodeError, ValueError) as error:
                raise AssertionError("validator did not emit one JSON receipt") from error
            if type(receipt) is not dict:
                raise AssertionError(f"validator PASS payload is not an object: {receipt!r}")

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_schema_status_and_production_nonmaterialization(self) -> None:
        artifact = self.artifact
        self.assertEqual(artifact["schema"], OUTPUT_SCHEMA)
        self.assertEqual(artifact["status"], OUTPUT_STATUS)
        scope = artifact["contract_scope"]
        claims = artifact["claim_boundary"]
        self.assertEqual(scope["formal_production_schema_name"], FORMAL_PRODUCTION_SCHEMA)
        self.assertEqual(scope["production_payload_roles_bound"], [])
        self.assertIs(scope["acceptance_receipt_deferred"], True)
        self.assertIs(claims["formal_symbolic_candidate_materialized"], False)
        self.assertIs(claims["symbolic_acceptance_receipt_materialized"], False)
        self.assertIs(claims["symbolic_bridge_accepted"], False)
        self.assertTrue(all(type(value) is bool and value is False for value in claims.values()))

    def test_only_whitelisted_neutral_process_flags_are_true(self) -> None:
        self.assertEqual(_true_paths(self.artifact), EXPECTED_TRUE_PATHS)
        self.assertIs(self.artifact["contract_scope"]["neutral_contract_fixture_pass"], True)

    def test_four_exact_rational_results(self) -> None:
        exact = self.artifact["exact_identity_results"]
        self.assertEqual(exact["global_gauge"]["G_exact"], "1/4")
        flux = exact["common_flux_and_tensor_conductance"]
        self.assertEqual(flux["common_flux_exact"], "6/5")
        self.assertEqual(flux["tensor_conductance_exact"], "6/7")
        reconstruction = exact["reconstruction"]
        self.assertEqual(reconstruction["rho_exact"], "6/5")
        self.assertEqual(reconstruction["K_exact"], "1/3")
        self.assertEqual(reconstruction["physical_weight_identity_exact"], "1/10")
        self.assertEqual(exact["interval_division"]["rho_interval"], ["15/13", "31/25"])

    def test_native_domain_nul_digest(self) -> None:
        receipts = self.artifact["native_record_receipts"]
        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertRegex(receipt["source_native_record_sha256"], SHA256_RE)
        _raw, source = _load_canonical(NEUTRAL_SOURCE)
        records = source["native_interval_records"]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertNotIn("source_path", record)
        self.assertNotIn("source_sha256", record)
        expected = hashlib.sha256(NATIVE_DOMAIN + _jcs_subset(record)).hexdigest()
        self.assertEqual(receipt["source_native_record_sha256"], expected)

    def test_six_open_counter_union_and_disjointness(self) -> None:
        ledger = self.artifact["open_ledger"]
        bootstrap = Counter(ledger["bootstrap_explicit_snapshot_counter"])
        payload = Counter(ledger["payload_explicit_snapshot_counter"])
        complete = Counter(ledger["explicit_construction_snapshot_counter"])
        self.assertTrue(set(bootstrap).isdisjoint(payload))
        self.assertEqual(bootstrap + payload, complete)
        self.assertEqual(sum(complete.values()), 6)
        self.assertEqual(ledger["maximum_report_file_opens"], 6)
        self.assertTrue(all(type(count) is int and count == 1 for count in complete.values()))
        self.assertEqual(len(bootstrap), 5)
        self.assertEqual(len(payload), 1)
        self.assertIs(ledger["complete_process_report_file_open_closure"], False)
        self.assertIs(ledger["current_run_output_reopened_as_input"], False)
        self.assertIs(ledger["prebootstrap_runtime_or_import_opens_traced"], False)
        outer_path = self.artifact["source_bindings"]["outer_manifest_source"]["path"]
        self.assertIn(outer_path, bootstrap)
        self.assertNotIn(outer_path, payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
