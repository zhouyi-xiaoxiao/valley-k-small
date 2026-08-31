#!/usr/bin/env python3
"""Tests for the explicitly scoped current continuum-spine verifier."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))

import verify_current_continuum_spine as verifier  # noqa: E402


class CurrentContinuumSpineTests(unittest.TestCase):
    def test_frozen_round174_and_round175_receipt_are_current(self) -> None:
        verifier.validate_environment()
        verifier.validate_round175_receipt()
        verifier.validate_manifest()
        dependencies = verifier._round176_dependency_paths()
        self.assertEqual(len(dependencies), 78)
        self.assertIn(verifier.REPORT / verifier.ROUND176_MANIFEST, dependencies)
        for path in dependencies:
            self.assertTrue(verifier._stable_regular_bytes(path))
        dependencies = verifier._round177_dependency_paths()
        self.assertEqual(len(dependencies), 77)
        self.assertIn(verifier.REPORT / verifier.ROUND177_MANIFEST, dependencies)
        for path in dependencies:
            self.assertTrue(verifier._stable_regular_bytes(path))

    def test_scoped_check_names_are_unique_and_complete(self) -> None:
        names = [check.name for check in verifier.CHECKS]
        self.assertEqual(len(names), 23)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names[0], "round175-receipt-currentness-tests")
        self.assertIn("round10-free-residual-independent-validator", names)
        self.assertIn("round10-free-residual-mutations", names)
        self.assertIn("round11-sector-contour-independent-validator", names)
        self.assertIn("round11-sector-contour-mutations", names)
        self.assertIn("round172-refinement-tests", names)
        self.assertIn("round173-source-bound-tests", names)
        self.assertIn("round174-composition-tests", names)
        self.assertIn("round176-n0-same-member-preflight-builder", names)
        self.assertIn("round176-n0-same-member-preflight-validator", names)
        self.assertIn("round176-n0-same-member-preflight-tests", names)
        self.assertIn("round177-predecessor-authority-candidate-builder", names)
        self.assertIn("round177-predecessor-authority-candidate-validator", names)
        self.assertIn("round177-predecessor-authority-candidate-tests", names)
        self.assertEqual(names[-1], "theorem-first-manuscript-freshness-and-scope")
        for check in verifier.CHECKS:
            if check.name.startswith(("round176-", "round177-")):
                self.assertEqual(check.argv[1:3], ("-I", "-B"))
        self.assertEqual(
            sum(check.expected_pytest_cases or 0 for check in verifier.CHECKS),
            verifier.EXPECTED_PYTEST_CASES,
        )
        self.assertEqual(
            sum(check.expected_pytest_tests or 0 for check in verifier.CHECKS),
            verifier.EXPECTED_JUNIT_TESTS,
        )
        summaries = {
            check.name: check.expected_output
            for check in verifier.CHECKS
            if check.expected_output is not None
        }
        self.assertIn("SUMMARY 107/107 PASS", summaries.values())
        self.assertIn("SUMMARY 30/30 PASS", summaries.values())
        self.assertIn("SUMMARY 1436/1436 PASS", summaries.values())
        self.assertIn("SUMMARY 46/46 PASS", summaries.values())

    def test_every_pytest_command_disables_repository_cache_collection_side_effects(
        self,
    ) -> None:
        pytest_commands = [check.argv for check in verifier.CHECKS if "pytest" in check.argv]
        self.assertGreaterEqual(len(pytest_commands), 5)
        for command in pytest_commands:
            self.assertIn("-p", command)
            self.assertIn("no:cacheprovider", command)
            self.assertIn("--strict-config", command)
            self.assertIn("--strict-markers", command)
            self.assertIn("xfail_strict=true", command)
            self.assertTrue(
                all(
                    item.startswith(verifier.CODE_PREFIX)
                    for item in command
                    if item.endswith(".py")
                )
            )

    def test_runner_is_serial_and_stops_at_first_failure(self) -> None:
        checks = (
            verifier.Check("first", ("python", "first.py")),
            verifier.Check("second", ("python", "second.py")),
            verifier.Check("unreached", ("python", "unreached.py")),
        )
        calls: list[tuple[str, ...]] = []

        def fake_runner(argv: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
            calls.append(argv)
            return subprocess.CompletedProcess(
                argv,
                7 if len(calls) == 2 else 0,
                stdout="",
            )

        with (
            patch.object(verifier, "validate_environment"),
            patch.object(verifier, "validate_round175_receipt"),
            patch.object(verifier, "validate_manifest"),
            patch.object(verifier, "_snapshot_allowlist", return_value={}),
            self.assertRaisesRegex(verifier.CurrentSpineFailure, "second"),
        ):
            verifier.run_checks(checks, runner=fake_runner)
        self.assertEqual(calls, [checks[0].argv, checks[1].argv])

    def test_list_mode_does_not_validate_or_execute(self) -> None:
        with patch.object(
            verifier,
            "validate_round175_receipt",
            side_effect=AssertionError("list mode must not execute"),
        ):
            self.assertEqual(verifier.main(["--list"]), 0)

    def test_success_line_retains_all_negative_promotions(self) -> None:
        with patch.object(verifier, "run_checks"):
            with patch("builtins.print") as emit:
                self.assertEqual(verifier.main([]), 0)
        status = emit.call_args.args[0]
        self.assertIn("full_report=false", status)
        self.assertIn("ci_attestation=false", status)
        self.assertIn("production_complete_C1=false", status)
        self.assertIn("production_same_member_bridge=false", status)
        self.assertIn("formal_symbolic_candidate=false", status)
        self.assertIn("computable_C2=false", status)
        self.assertIn("complete_C3=false", status)
        self.assertIn("root_transfer=false", status)
        self.assertIn("release_eligible=false", status)


if __name__ == "__main__":
    unittest.main()
